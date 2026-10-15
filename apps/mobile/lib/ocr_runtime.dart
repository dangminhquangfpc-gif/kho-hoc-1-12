import 'ocr_runtime_native.dart'
    if (dart.library.js_interop) 'ocr_runtime_web.dart'
    as platform;

/// OCR data lives in memory only. Callers decide whether to use the edited text.
class OcrResult {
  const OcrResult({
    required this.text,
    required this.confidence,
    this.warnings = const [],
    this.previewDataUrl,
  });
  final String text;
  final double confidence;
  final List<String> warnings;
  final String? previewDataUrl;
}

abstract interface class OcrRecognizer {
  bool get available;
  Future<OcrResult?> recognize();
  void cancel();
}

class DeviceOcrRecognizer implements OcrRecognizer {
  const DeviceOcrRecognizer();
  @override
  bool get available => platform.ocrAvailable;
  @override
  Future<OcrResult?> recognize() async {
    final data = await platform.pickOcr();
    if (data == null || data['cancelled'] == true) return null;
    return OcrResult(
      text: data['text'] as String? ?? '',
      confidence: (data['confidence'] as num? ?? 0).toDouble(),
      warnings: (data['warnings'] as List? ?? []).map((v) => '$v').toList(),
      previewDataUrl: data['preview_data_url'] as String?,
    );
  }

  @override
  void cancel() => platform.cancelOcr();
}
