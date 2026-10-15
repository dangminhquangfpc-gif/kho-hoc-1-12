import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/repository.dart';

class StatusAdapter implements HttpClientAdapter {
  StatusAdapter(this.status);
  final int status;
  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async => ResponseBody.fromString(
    '{"detail":"Unavailable"}',
    status,
    headers: {
      Headers.contentTypeHeader: [Headers.jsonContentType],
    },
  );
  @override
  void close({bool force = false}) {}
}

void main() {
  test('HTTPS endpoint normalization and credential rejection', () {
    expect(validateBackendUrl(' https://example.org/ '), 'https://example.org');
    for (final value in [
      'http://example.org',
      'https://user:pass@example.org',
      'https://example.org/api',
      'https://example.org/?token=secret',
      'invalid',
    ]) {
      expect(() => validateBackendUrl(value), throwsFormatException);
    }
  });
  test('Deleting a missing attempt permits local history cleanup', () async {
    final dio = Dio(BaseOptions(baseUrl: 'https://example.test'))
      ..httpClientAdapter = StatusAdapter(404);
    await LearningApi(
      client: dio,
    ).delete({'id': 'removed', 'token': 'local-token'});
  });
  test(
    'Deleting during server failure keeps error available for retry',
    () async {
      final dio = Dio(BaseOptions(baseUrl: 'https://example.test'))
        ..httpClientAdapter = StatusAdapter(503);
      await expectLater(
        LearningApi(
          client: dio,
        ).delete({'id': 'retained', 'token': 'local-token'}),
        throwsA(isA<DioException>()),
      );
    },
  );
}
