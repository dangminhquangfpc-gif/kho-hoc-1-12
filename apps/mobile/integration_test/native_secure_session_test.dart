import 'dart:convert';
import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'package:kho_hoc_mobile/secure_session_store.dart';

// Transport responses are synthetic; the platform KeyStore/Keychain is real.
// This does not prove reachability or authentication of a public HTTPS server.
class LocalSessionTransport implements HttpClientAdapter {
  String? bearer;
  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    bearer = options.headers['Authorization'] as String?;
    return ResponseBody.fromString(
      jsonEncode({
        'id': 'native-session-qa',
        'username': 'native-session-qa',
        'role': 'student',
      }),
      200,
      headers: {
        Headers.contentTypeHeader: [Headers.jsonContentType],
      },
    );
  }

  @override
  void close({bool force = false}) {}
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'Device secure storage survives client recreation and clears exact token',
    (tester) async {
      const scope = 'https://native-session-qa.invalid/api';
      const token = 'khs_native_synthetic_session_123456789';
      final store = SecureSessionStore(const PlatformSessionSecretStorage());
      // Only this disposable QA scope is touched, never deleteAll or user data.
      final previous = await store.read(scope);
      if (previous != null) await store.clearIfToken(scope, previous.token);
      LearningApi? first;
      LearningApi? reopened;
      try {
        await store.write(
          scope,
          const NativeSession(token: token, accountId: 'native-session-qa'),
        );
        first = LearningApi(baseUrl: scope, sessionStore: store);
        await first.restoreSession();
        expect(first.expectedAccountId, 'native-session-qa');
        first.dispose();
        first = null;

        final transport = LocalSessionTransport();
        reopened = LearningApi(
          client: Dio(BaseOptions(baseUrl: scope))
            ..httpClientAdapter = transport,
          sessionStore: store,
        );
        expect((await reopened.currentUser())?['id'], 'native-session-qa');
        expect(transport.bearer, 'Bearer $token');
        expect(
          await store.clearIfToken(
            scope,
            'khs_other_synthetic_session_123456789',
          ),
          isFalse,
        );
        expect((await store.read(scope))?.accountId, 'native-session-qa');
        expect(await store.clearIfToken(scope, token), isTrue);
        expect(await store.read(scope), isNull);
      } finally {
        first?.dispose();
        reopened?.dispose();
        await store.clearIfToken(scope, token);
      }
    },
  );
}
