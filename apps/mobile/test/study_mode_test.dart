import 'dart:convert';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:kho_hoc_mobile/repository.dart';

class OfflineAuthMustNotRun extends LearningApi {
  @override
  bool get isOffline => true;
  @override
  Future<Json?> currentUser() => throw StateError('Must not query account');
}

class DelayedAuth extends LearningApi {
  final response = Completer<Json?>();
  @override
  Future<Json?> currentUser() => response.future;
}

Json localSession() => {
  'id': 'offline_saved',
  'token': 'local-test',
  'account_id': null,
  'local_self_practice': true,
  'backend_url': 'offline://tu-hoc-111/v1',
  'answers': <String, dynamic>{},
};

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  test(
    'Native placeholder defaults offline, configured server and web online',
    () async {
      SharedPreferences.setMockInitialValues({});
      final p = await SharedPreferences.getInstance();
      expect(
        initialStudyOffline(
          p,
          web: false,
          configuredBackend: 'https://backend.invalid/api',
        ),
        isTrue,
      );
      expect(
        initialStudyOffline(
          p,
          web: false,
          configuredBackend: 'https://school.edu.vn/api',
        ),
        isFalse,
      );
      expect(
        initialStudyOffline(p, web: true, configuredBackend: '/api'),
        isFalse,
      );
      expect(p.getBool('study_offline'), isNull);
      await p.setBool('study_offline', false);
      expect(
        initialStudyOffline(
          p,
          web: false,
          configuredBackend: 'https://backend.invalid/api',
        ),
        isFalse,
      );
      await p.setBool('study_offline', true);
      expect(
        initialStudyOffline(p, web: true, configuredBackend: '/api'),
        isTrue,
      );
    },
  );

  test(
    'Startup persists default used by local storage before opening a new quiz',
    () async {
      SharedPreferences.setMockInitialValues({});
      final p = await SharedPreferences.getInstance();
      // Flutter widget test is native; no usable default HTTPS backend is supplied.
      expect(await initializeStudyOffline(p), isTrue);
      expect(p.getBool('study_offline'), isTrue);
      final store = LocalStore(p);
      expect(store.offline, isTrue);
      await store.save(localSession());
      expect(store.current?['id'], 'offline_saved');
    },
  );

  test(
    'Offline bootstrap preserves online account and never calls auth',
    () async {
      final history = jsonEncode([
        {'id': 'server_result'},
      ]);
      SharedPreferences.setMockInitialValues({
        'study_offline': true,
        'active_account_id': 'student_1',
        'history.student_1': history,
      });
      final p = await SharedPreferences.getInstance();
      final container = ProviderContainer(
        overrides: [
          apiProvider.overrideWithValue(OfflineAuthMustNotRun()),
          preferencesProvider.overrideWith((ref) async => p),
        ],
      );
      addTearDown(container.dispose);
      expect(await container.read(authBootstrapProvider.future), isNull);
      expect(p.getString('active_account_id'), 'student_1');
      expect(p.getString('history.student_1'), history);
    },
  );

  test(
    'A late server auth response cannot erase an account after going offline',
    () async {
      SharedPreferences.setMockInitialValues({
        'active_account_id': 'student_1',
      });
      final p = await SharedPreferences.getInstance();
      final delayed = DelayedAuth();
      final container = ProviderContainer(
        overrides: [
          apiProvider.overrideWith(
            (ref) => ref.watch(studyOfflineProvider)
                ? OfflineAuthMustNotRun()
                : delayed,
          ),
          preferencesProvider.overrideWith((ref) async => p),
        ],
      );
      addTearDown(container.dispose);
      final old = container.read(authBootstrapProvider.future);
      await Future<void>.delayed(Duration.zero);
      await p.setBool('study_offline', true);
      container.read(studyOfflineProvider.notifier).state = true;
      expect(await container.read(authBootstrapProvider.future), isNull);
      delayed.response.complete(null);
      await old;
      expect(p.getString('active_account_id'), 'student_1');
      expect(container.read(authUserProvider), isNull);
    },
  );

  test(
    'Offline completion and deletion leave all server history and drafts intact',
    () async {
      final serverDraft = jsonEncode({
        'id': 'server_attempt',
        'account_id': 'student_1',
      });
      final serverHistory = jsonEncode([
        {'id': 'server_result'},
      ]);
      SharedPreferences.setMockInitialValues({
        'study_offline': true,
        'active_account_id': 'student_1',
        'current_attempt.student_1': serverDraft,
        'history.student_1': serverHistory,
        'history': jsonEncode([
          {'id': 'guest_result'},
        ]),
      });
      final p = await SharedPreferences.getInstance();
      final store = LocalStore(p);
      final session = localSession();
      await store.save(session);
      await store.complete(session, {'attempt_id': session['id'], 'score': 1});
      expect(store.current, isNull);
      expect(store.history.single['id'], session['id']);
      await store.removeHistory(session['id']);
      expect(store.history, isEmpty);
      expect(p.getString('current_attempt.student_1'), serverDraft);
      expect(p.getString('history.student_1'), serverHistory);
      expect(LocalStore(p, offline: false).current?['id'], 'server_attempt');
      expect(p.getString('active_account_id'), 'student_1');
      expect(jsonDecode(p.getString('history')!).single['id'], 'guest_result');
    },
  );

  test(
    'Delayed writes cannot cross a mode switch or change the result identity',
    () async {
      SharedPreferences.setMockInitialValues({'study_offline': true});
      final p = await SharedPreferences.getInstance();
      final store = LocalStore(p);
      await store.save(localSession());
      await expectLater(
        store.complete(localSession(), {'attempt_id': 'another'}),
        throwsStateError,
      );
      await p.setBool('study_offline', false);
      await expectLater(store.save(localSession()), throwsStateError);
      await expectLater(store.removeHistory('offline_saved'), throwsStateError);
      expect(p.getString('current_attempt.offline'), isNotNull);
      expect(p.getString('current_attempt'), isNull);
      final online = LocalStore(p);
      await expectLater(online.save(localSession()), throwsStateError);
    },
  );

  test(
    'Server API refuses offline attempts before any transport call',
    () async {
      final api = LearningApi(baseUrl: 'https://school.edu.vn/api');
      var requests = 0;
      api.client.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            requests++;
            handler.reject(DioException(requestOptions: options));
          },
        ),
      );
      final s = localSession();
      for (final work in <Future<dynamic> Function()>[
        () => api.submit(s),
        () => api.attemptResult(s),
        () => api.delete(s),
        () => api.saveDraft(s),
        () => api.recover(s),
      ]) {
        await expectLater(work(), throwsStateError);
      }
      expect(requests, 0);
    },
  );
}
