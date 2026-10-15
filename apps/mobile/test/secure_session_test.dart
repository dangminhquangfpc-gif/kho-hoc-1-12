import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:kho_hoc_mobile/repository.dart';
import 'package:kho_hoc_mobile/secure_session_store.dart';

const firstBackend = 'https://school.example/api';
const secondBackend = 'https://other-school.example/api';
const firstToken = 'khs_synthetic_first_token_1234567890';
const secondToken = 'khs_synthetic_second_token_123456789';
const firstSession = NativeSession(token: firstToken, accountId: 'alice');
const secondSession = NativeSession(token: secondToken, accountId: 'bob');

class FakeSecretStorage implements SessionSecretStorage {
  final values = <String, String>{};
  bool failRead = false;
  bool failWrite = false;
  @override
  Future<String?> read(String key) async {
    if (failRead) throw StateError('Synthetic keychain unavailable');
    return values[key];
  }

  @override
  Future<void> write(String key, String value) async {
    if (failWrite) throw StateError('Synthetic keychain unavailable');
    values[key] = value;
  }

  @override
  Future<void> delete(String key) async => values.remove(key);
}

class SessionAdapter implements HttpClientAdapter {
  SessionAdapter(this.respond);
  final FutureOr<ResponseBody> Function(RequestOptions) respond;
  final requests = <RequestOptions>[];
  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    requests.add(options);
    return respond(options);
  }

  @override
  void close({bool force = false}) {}
}

ResponseBody reply(int status, [Object? value]) => ResponseBody.fromString(
  jsonEncode(value),
  status,
  headers: {
    Headers.contentTypeHeader: [Headers.jsonContentType],
  },
);

Json user(String account) => {
  'id': account,
  'username': account,
  'display_name': account,
  'role': 'student',
  'must_change_password': false,
};

LearningApi apiFor(
  SecureSessionStore store,
  SessionAdapter adapter, {
  String backend = firstBackend,
}) => LearningApi(
  client: Dio(BaseOptions(baseUrl: backend))..httpClientAdapter = adapter,
  sessionStore: store,
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test(
    'HTTPS scope canonicalizes host, port and trailing slash, preserves path',
    () {
      expect(
        nativeSessionScope(' HTTPS://SCHOOL.EXAMPLE:443/api/ '),
        firstBackend,
      );
      expect(
        nativeSessionScope('https://school.example/'),
        'https://school.example',
      );
      expect(
        nativeSessionScope('https://school.example/api/v2/'),
        'https://school.example/api/v2',
      );
      expect(
        nativeSessionScope('https://school.example:8443/api'),
        'https://school.example:8443/api',
      );
      for (final backend in [
        'http://school.example/api',
        '/api',
        'https://name:password@school.example/api',
        'https://school.example/api?token=synthetic',
        'https://school.example/api#fragment',
      ]) {
        expect(nativeSessionScope(backend), isNull);
      }
    },
  );

  test(
    'Login persists only opaque session and restores before a fresh API request',
    () async {
      SharedPreferences.setMockInitialValues({});
      final secrets = FakeSecretStorage();
      final store = SecureSessionStore(secrets);
      final loginTransport = SessionAdapter((request) {
        expect(request.path, '/auth/login');
        expect(request.headers['Authorization'], isNull);
        expect(request.followRedirects, isFalse);
        return reply(200, {'user': user('alice'), 'token': firstToken});
      });
      final original = apiFor(store, loginTransport);
      await original.authenticate('alice', 'Synthetic-password-123');
      expect((await store.read(firstBackend))?.accountId, 'alice');
      final encoded = secrets.values.values.single;
      expect(encoded.contains('Synthetic-password-123'), isFalse);
      expect((await SharedPreferences.getInstance()).getKeys(), isEmpty);
      original.dispose();

      final resumedTransport = SessionAdapter((request) {
        expect(request.path, '/auth/me');
        expect(request.headers['Authorization'], 'Bearer $firstToken');
        expect(request.followRedirects, isFalse);
        return reply(200, user('alice'));
      });
      final resumed = apiFor(store, resumedTransport);
      addTearDown(resumed.dispose);
      expect((await resumed.currentUser())?['id'], 'alice');
      expect(resumed.expectedAccountId, 'alice');
      expect(resumedTransport.requests.length, 1);
    },
  );

  test(
    'Different backend paths, hosts and accounts cannot borrow each other sessions',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      await store.write(secondBackend, secondSession);
      await store.write('https://school.example', secondSession);
      expect((await store.read(firstBackend))?.accountId, 'alice');
      expect((await store.read(secondBackend))?.accountId, 'bob');
      expect((await store.read('https://school.example'))?.accountId, 'bob');
      expect(await store.read('https://school.example/api/v2'), isNull);
      await store.write(firstBackend, secondSession);
      expect((await store.read(firstBackend))?.accountId, 'bob');
      expect(await store.clearIfToken(firstBackend, firstToken), isFalse);
      expect((await store.read(firstBackend))?.token, secondToken);
    },
  );

  test(
    'Backend bootstrap restores a secure token while preserving offline history',
    () async {
      SharedPreferences.setMockInitialValues({
        'study_offline': false,
        'active_account_id': 'alice',
        'history.offline': '[{"id":"offline_preserved"}]',
        'current_attempt.alice': '{"id":"server_preserved"}',
      });
      final preferences = await SharedPreferences.getInstance();
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final transport = SessionAdapter((request) {
        expect(request.headers['Authorization'], 'Bearer $firstToken');
        return reply(200, user('alice'));
      });
      final api = apiFor(store, transport);
      final container = ProviderContainer(
        overrides: [
          apiProvider.overrideWithValue(api),
          preferencesProvider.overrideWith((ref) async => preferences),
        ],
      );
      addTearDown(container.dispose);
      addTearDown(api.dispose);
      expect(
        (await container.read(authBootstrapProvider.future))?['id'],
        'alice',
      );
      expect(preferences.getString('active_account_id'), 'alice');
      expect(
        preferences.getString('history.offline'),
        '[{"id":"offline_preserved"}]',
      );
      expect(
        preferences.getString('current_attempt.alice'),
        '{"id":"server_preserved"}',
      );
    },
  );

  test(
    'Expired session clears only that HTTPS backend, keeps learner drafts',
    () async {
      SharedPreferences.setMockInitialValues({
        'active_account_id': 'alice',
        'current_attempt.alice': '{"id":"saved"}',
      });
      final preferences = await SharedPreferences.getInstance();
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      await store.write(secondBackend, secondSession);
      final api = apiFor(store, SessionAdapter((_) => reply(401)));
      var recursiveBootstrap = 0;
      api.onSessionLost = () => recursiveBootstrap++;
      final container = ProviderContainer(
        overrides: [
          apiProvider.overrideWithValue(api),
          preferencesProvider.overrideWith((ref) async => preferences),
        ],
      );
      addTearDown(container.dispose);
      addTearDown(api.dispose);
      expect(await container.read(authBootstrapProvider.future), isNull);
      expect(recursiveBootstrap, 0);
      expect(await store.read(firstBackend), isNull);
      expect((await store.read(secondBackend))?.accountId, 'bob');
      expect(preferences.getString('active_account_id'), isNull);
      expect(preferences.getString('current_attempt.alice'), '{"id":"saved"}');
    },
  );

  test(
    'Network failure preserves login and account namespace for retry',
    () async {
      SharedPreferences.setMockInitialValues({'active_account_id': 'alice'});
      final preferences = await SharedPreferences.getInstance();
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      var status = 503;
      final api = apiFor(
        store,
        SessionAdapter((_) => reply(status, user('alice'))),
      );
      final container = ProviderContainer(
        overrides: [
          apiProvider.overrideWithValue(api),
          preferencesProvider.overrideWith((ref) async => preferences),
        ],
      );
      addTearDown(container.dispose);
      addTearDown(api.dispose);
      await expectLater(
        container.read(authBootstrapProvider.future),
        throwsA(isA<DioException>()),
      );
      expect((await store.read(firstBackend))?.token, firstToken);
      expect(preferences.getString('active_account_id'), 'alice');
      status = 200;
      container.invalidate(authBootstrapProvider);
      expect(
        (await container.read(authBootstrapProvider.future))?['id'],
        'alice',
      );
    },
  );

  test(
    'Protected 401 invalidates auth once; anonymous bootstrap never loops',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final api = apiFor(store, SessionAdapter((_) => reply(401)));
      addTearDown(api.dispose);
      var refresh = 0;
      api.onSessionLost = () => refresh++;
      await expectLater(api.accountResults(), throwsA(isA<DioException>()));
      expect(refresh, 1);
      expect(await store.read(firstBackend), isNull);
      expect(await api.currentUser(), isNull);
      expect(refresh, 1);
    },
  );

  test(
    'Failed logout retains session; successful logout clears only its backend',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      await store.write(secondBackend, secondSession);
      var status = 503;
      final api = apiFor(store, SessionAdapter((_) => reply(status)));
      addTearDown(api.dispose);
      await expectLater(api.signOut(), throwsA(isA<DioException>()));
      expect((await store.read(firstBackend))?.token, firstToken);
      status = 204;
      await api.signOut();
      expect(await store.read(firstBackend), isNull);
      expect(api.client.options.headers['Authorization'], isNull);
      expect((await store.read(secondBackend))?.token, secondToken);
    },
  );

  test(
    'Wrong password during login cannot erase the existing secure session',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final api = apiFor(
        store,
        SessionAdapter((request) {
          expect(request.path, '/auth/login');
          expect(request.headers['Authorization'], isNull);
          return reply(401);
        }),
      );
      addTearDown(api.dispose);
      await expectLater(
        api.authenticate('bob', 'Synthetic-wrong-password'),
        throwsA(isA<DioException>()),
      );
      expect((await store.read(firstBackend))?.accountId, 'alice');
      expect(api.client.options.headers['Authorization'], 'Bearer $firstToken');
    },
  );

  test(
    'A delayed logout cannot remove a login saved by the next client',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final requested = Completer<void>();
      final delayed = Completer<ResponseBody>();
      final old = apiFor(
        store,
        SessionAdapter((_) {
          requested.complete();
          return delayed.future;
        }),
      );
      addTearDown(old.dispose);
      final pending = old.signOut();
      await requested.future;
      final newer = apiFor(
        store,
        SessionAdapter(
          (_) => reply(200, {'user': user('bob'), 'token': secondToken}),
        ),
      );
      addTearDown(newer.dispose);
      await newer.authenticate('bob', 'Synthetic-password-123');
      delayed.complete(reply(204));
      await pending;
      expect((await store.read(firstBackend))?.accountId, 'bob');
      expect(newer.expectedAccountId, 'bob');
    },
  );

  test(
    'Failed account deletion keeps session; confirmed deletion removes it',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      var status = 400;
      final api = apiFor(store, SessionAdapter((_) => reply(status)));
      addTearDown(api.dispose);
      await expectLater(
        api.deleteAccount('Synthetic-wrong-password'),
        throwsA(isA<DioException>()),
      );
      expect((await store.read(firstBackend))?.token, firstToken);
      status = 204;
      await api.deleteAccount('Synthetic-confirmed-password');
      expect(await store.read(firstBackend), isNull);
    },
  );

  test(
    'Password change keeps current session, matching server rotation policy',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final api = apiFor(
        store,
        SessionAdapter((request) {
          expect(request.headers['Authorization'], 'Bearer $firstToken');
          return reply(200, user('alice'));
        }),
      );
      addTearDown(api.dispose);
      await api.changePassword(
        'Synthetic-old-password',
        'Synthetic-new-password',
      );
      expect((await store.read(firstBackend))?.token, firstToken);
      expect((await api.currentUser())?['id'], 'alice');
    },
  );

  test(
    'An old 401 cannot erase a newer login, even before old client disposal',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final requested = Completer<void>();
      final oldReply = Completer<ResponseBody>();
      final old = apiFor(
        store,
        SessionAdapter((_) {
          requested.complete();
          return oldReply.future;
        }),
      );
      final pending = old.currentUser();
      await requested.future;
      final newer = apiFor(
        store,
        SessionAdapter(
          (_) => reply(200, {'user': user('bob'), 'token': secondToken}),
        ),
      );
      addTearDown(old.dispose);
      addTearDown(newer.dispose);
      await newer.authenticate('bob', 'Synthetic-password-123');
      oldReply.complete(reply(401));
      expect(await pending, isNull);
      expect((await store.read(firstBackend))?.accountId, 'bob');
      expect(
        newer.client.options.headers['Authorization'],
        'Bearer $secondToken',
      );
    },
  );

  test(
    'A delayed 401 on the same API cannot clear a new in-memory login',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final requested = Completer<void>();
      final oldReply = Completer<ResponseBody>();
      final api = apiFor(
        store,
        SessionAdapter((request) {
          if (request.path == '/auth/login') {
            return reply(200, {'user': user('bob'), 'token': secondToken});
          }
          requested.complete();
          return oldReply.future;
        }),
      );
      addTearDown(api.dispose);
      var lost = 0;
      api.onSessionLost = () => lost++;
      final pending = api.currentUser();
      await requested.future;
      await api.authenticate('bob', 'Synthetic-password-123');
      oldReply.complete(reply(401));
      expect(await pending, isNull);
      expect(lost, 0);
      expect(
        api.client.options.headers['Authorization'],
        'Bearer $secondToken',
      );
      expect((await store.read(firstBackend))?.accountId, 'bob');
    },
  );

  test(
    'A discarded client cannot persist a late login over the next client',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      final requested = Completer<void>();
      final oldReply = Completer<ResponseBody>();
      final old = apiFor(
        store,
        SessionAdapter((_) {
          requested.complete();
          return oldReply.future;
        }),
      );
      final pending = old.authenticate('alice', 'Synthetic-password-123');
      // Install an error handler before completing the delayed response.
      final rejected = expectLater(pending, throwsA(anything));
      await requested.future;
      old.dispose();
      final newer = apiFor(
        store,
        SessionAdapter(
          (_) => reply(200, {'user': user('bob'), 'token': secondToken}),
        ),
      );
      addTearDown(newer.dispose);
      await newer.authenticate('bob', 'Synthetic-password-123');
      oldReply.complete(
        reply(200, {'user': user('alice'), 'token': firstToken}),
      );
      await rejected;
      expect((await store.read(firstBackend))?.accountId, 'bob');
    },
  );

  test(
    'No bearer is sent outside its backend scope, authenticated redirects disabled',
    () async {
      final store = SecureSessionStore(FakeSecretStorage());
      await store.write(firstBackend, firstSession);
      final transport = SessionAdapter((request) => reply(200, user('alice')));
      final api = apiFor(store, transport);
      addTearDown(api.dispose);
      await api.currentUser();
      await api.client.get('https://other-school.example/api/auth/me');
      await api.client.get('https://school.example/outside/auth/me');
      await api.client.get('http://school.example/api/auth/me');
      expect(
        transport.requests.first.headers['Authorization'],
        'Bearer $firstToken',
      );
      expect(transport.requests.first.followRedirects, isFalse);
      for (final request in transport.requests.skip(1)) {
        expect(request.headers['Authorization'], isNull);
      }
    },
  );

  test(
    'Locked secure storage does not erase data and can retry after unlock',
    () async {
      final secrets = FakeSecretStorage();
      final store = SecureSessionStore(secrets);
      await store.write(firstBackend, firstSession);
      secrets.failRead = true;
      final transport = SessionAdapter((_) => reply(200, user('alice')));
      final api = apiFor(store, transport);
      addTearDown(api.dispose);
      await expectLater(
        api.currentUser(),
        throwsA(isA<SecureSessionStorageException>()),
      );
      expect(transport.requests, isEmpty);
      expect(secrets.values.length, 1);
      secrets.failRead = false;
      expect((await api.currentUser())?['id'], 'alice');
      expect((await store.read(firstBackend))?.token, firstToken);
    },
  );

  test(
    'Storage failure during login never silently reports durable login',
    () async {
      final secrets = FakeSecretStorage()..failWrite = true;
      final store = SecureSessionStore(secrets);
      final api = apiFor(
        store,
        SessionAdapter(
          (_) => reply(200, {'user': user('alice'), 'token': firstToken}),
        ),
      );
      addTearDown(api.dispose);
      await expectLater(
        api.authenticate('alice', 'Synthetic-password-123'),
        throwsA(isA<SecureSessionStorageException>()),
      );
      expect(secrets.values, isEmpty);
      expect(api.client.options.headers['Authorization'], isNull);
    },
  );
}
