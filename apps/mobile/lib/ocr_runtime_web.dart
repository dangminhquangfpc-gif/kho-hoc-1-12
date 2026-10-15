import 'dart:js_interop';

@JS('tuHocOcr')
external JSAny? get _engine;
@JS('tuHocOcr.pickAndRecognize')
external JSPromise<JSAny?> _recognize();
@JS('tuHocOcr.cancel')
external void _cancel();

bool get ocrAvailable => _engine != null;
Future<Map<String, dynamic>?> pickOcr() async {
  if (!ocrAvailable) {
    throw StateError(
      'Bộ nhận chữ chưa tải được. Hãy tải lại trang hoặc nhập văn bản.',
    );
  }
  final result = (await _recognize().toDart)?.dartify();
  if (result == null) return null;
  return Map<String, dynamic>.from(result as Map);
}

void cancelOcr() {
  if (ocrAvailable) _cancel();
}
