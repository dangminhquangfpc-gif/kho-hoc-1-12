import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math' as math;
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/services.dart' show PlatformException;
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';

import 'ocr_image_validation.dart';

bool get ocrAvailable => Platform.isAndroid || Platform.isIOS;
final _native = NativeOcrPlatform();
final _session = NativeOcrSession(
  pickImage: _native.pickImage,
  processImage: _native.processImage,
  cleanupPicked: _native.cleanupPicked,
);

Future<Map<String, dynamic>?> pickOcr() {
  if (!ocrAvailable) {
    throw UnsupportedError(
      'Nhận chữ trên thiết bị hiện hỗ trợ Android và iOS. Bạn vẫn có thể nhập hoặc dán văn bản bên dưới.',
    );
  }
  return _session.recognize();
}

void cancelOcr() => _session.cancel();

/// Same production preprocessing and ML Kit call, with an explicit selected file.
/// Used by native device integration tests without automating the OS photo UI.
/// The caller owns the original file; only our normalized cache copy is deleted.
Future<Map<String, dynamic>> recognizeNativeImageFile(String path) =>
    NativeOcrPlatform().processImage(path, () => false);

/// Native ML Kit has no force-stop API. Cancellation returns immediately and
/// discards late replies; native resources are released when that call finishes.
/// A second call waits for cleanup by being rejected while the first is active.
class NativeOcrSession {
  NativeOcrSession({
    required this.pickImage,
    required this.processImage,
    required this.cleanupPicked,
    this.timeout = const Duration(seconds: 60),
  });
  final Future<String?> Function() pickImage;
  final Future<Map<String, dynamic>> Function(String, bool Function())
  processImage;
  final Future<void> Function(String) cleanupPicked;
  final Duration timeout;
  _OcrOperation? _active;

  Future<Map<String, dynamic>?> recognize() {
    if (_active != null) {
      throw StateError(
        'Bộ nhận chữ đang hoàn tất lượt trước. Hãy đợi một lát rồi chọn lại ảnh.',
      );
    }
    final operation = _OcrOperation();
    _active = operation;
    return Future.any([_run(operation), operation.cancelled.future]);
  }

  Future<Map<String, dynamic>?> _run(_OcrOperation operation) async {
    String? picked;
    try {
      picked = await pickImage();
      if (picked == null || operation.stopped) return null;
      operation.timer = Timer(timeout, () {
        operation.stopped = true;
        if (!operation.cancelled.isCompleted) {
          operation.cancelled.completeError(
            TimeoutException(
              'Nhận dạng mất quá 60 giây. Hãy cắt riêng bài cần đọc hoặc nhập văn bản.',
            ),
          );
        }
      });
      final result = await processImage(picked, () => operation.stopped);
      return operation.stopped ? null : result;
    } on PlatformException catch (error) {
      if (operation.stopped) return null;
      if (const {
        'photo_access_denied',
        'photo_access_restricted',
        'permission_denied',
      }.contains(error.code)) {
        throw StateError(
          'Chưa có quyền chọn ảnh. Hãy cho phép truy cập ảnh trong Cài đặt của thiết bị, hoặc nhập văn bản.',
        );
      }
      throw StateError(
        'Không đọc được ảnh trên thiết bị. Hãy dùng ảnh rõ hơn hoặc nhập văn bản.',
      );
    } on FormatException {
      if (operation.stopped) return null;
      rethrow;
    } on StateError {
      if (operation.stopped) return null;
      rethrow;
    } catch (_) {
      if (operation.stopped) return null;
      throw StateError(
        'Không đọc được ảnh trên thiết bị. Hãy lưu ảnh thành JPEG hoặc PNG rồi thử lại.',
      );
    } finally {
      operation.timer?.cancel();
      if (picked != null) {
        try {
          await cleanupPicked(picked);
        } catch (_) {
          // Never log a private image path; the OS can purge its private cache.
        }
      }
      if (identical(_active, operation)) _active = null;
    }
  }

  void cancel() {
    final operation = _active;
    if (operation == null) return;
    operation.stopped = true;
    operation.timer?.cancel();
    if (!operation.cancelled.isCompleted) operation.cancelled.complete(null);
  }
}

class _OcrOperation {
  final cancelled = Completer<Map<String, dynamic>?>();
  bool stopped = false;
  Timer? timer;
}

class NativeOcrPlatform {
  NativeOcrPlatform({Future<Directory> Function()? temporaryDirectory})
    : temporaryDirectory = temporaryDirectory ?? getTemporaryDirectory;

  final Future<Directory> Function() temporaryDirectory;
  final _picker = ImagePicker();
  bool _recovered = false;

  Future<String?> pickImage() async {
    _recovered = false;
    // Recover Android's lost picker result only after an explicit OCR action,
    // never process a photo in the background after an Activity recreation.
    if (Platform.isAndroid) {
      final lost = await _picker.retrieveLostData();
      if (lost.files?.isNotEmpty == true) {
        _recovered = true;
        return lost.files!.first.path;
      }
      if (lost.exception != null) throw lost.exception!;
    }
    final picked = await _picker.pickImage(
      source: ImageSource.gallery,
      requestFullMetadata: false,
    );
    return picked?.path;
  }

  Future<Map<String, dynamic>> processImage(
    String path,
    bool Function() stopped,
  ) async {
    void check() {
      if (stopped()) throw StateError('Đã hủy nhận chữ.');
    }

    final input = File(path);
    final size = await input.length();
    check();
    if (size < 1 || size > maxOcrImageBytes) {
      throw const FormatException(
        'Chọn ảnh có dung lượng từ 1 byte đến 8 MiB.',
      );
    }
    // Bound the stream as well as stat(): a changed picker file must never
    // allocate beyond the input limit between the size check and the read.
    final collected = await input
        .openRead(0, maxOcrImageBytes + 1)
        .fold(
          BytesBuilder(copy: false),
          (builder, chunk) => builder..add(chunk),
        );
    final bytes = collected.takeBytes();
    check();
    final header = validateOcrImage(bytes);
    final temporary = await temporaryDirectory();
    check();
    final directory = await temporary.createTemp('tu-hoc-111-ocr-');
    TextRecognizer? recognizer;
    ui.ImmutableBuffer? buffer;
    ui.ImageDescriptor? descriptor;
    ui.Codec? codec;
    ui.Image? image;
    try {
      check();
      buffer = await ui.ImmutableBuffer.fromUint8List(bytes);
      check();
      descriptor = await ui.ImageDescriptor.encoded(buffer);
      check();
      if (!((descriptor.width == header.width &&
              descriptor.height == header.height) ||
          (descriptor.width == header.height &&
              descriptor.height == header.width))) {
        throw const FormatException(
          'Kích thước ảnh không khớp. Hãy lưu lại ảnh rồi thử lại.',
        );
      }
      final scale = math.min(
        1.0,
        math.min(
          3200 / math.max(descriptor.width, descriptor.height),
          math.sqrt(8000000 / (descriptor.width * descriptor.height)),
        ),
      );
      codec = await descriptor.instantiateCodec(
        targetWidth: math.max(1, (descriptor.width * scale).round()),
        targetHeight: math.max(1, (descriptor.height * scale).round()),
      );
      check();
      final frame = await codec.getNextFrame();
      image = frame.image;
      check();
      // Re-encoding drops EXIF, GPS, filenames and all other source metadata.
      final png = await image.toByteData(format: ui.ImageByteFormat.png);
      check();
      if (png == null || png.lengthInBytes > 32 * 1024 * 1024) {
        throw const FormatException(
          'Không thể xử lý ảnh. Hãy cắt ảnh nhỏ hơn.',
        );
      }
      final normalized = File('${directory.path}/input.png');
      await normalized.writeAsBytes(
        png.buffer.asUint8List(png.offsetInBytes, png.lengthInBytes),
        flush: true,
      );
      check();
      final preview = await _previewPng(image);
      check();
      recognizer = TextRecognizer(script: TextRecognitionScript.latin);
      final recognized = await recognizer.processImage(
        InputImage.fromFilePath(normalized.path),
      );
      check();
      final text = recognized.text.trim();
      return {
        'text': text.length > 20000 ? text.substring(0, 20000) : text,
        // ML Kit has no calibrated overall recognition confidence.
        'confidence': null,
        'warnings': <String>[
          'Dấu tiếng Việt, chữ viết tay, phân số, số mũ và hình vẽ có thể nhận sai. Hãy đối chiếu ảnh và sửa trước khi dùng.',
          if (text.isEmpty)
            'Chưa tìm thấy chữ rõ trong ảnh. Hãy dùng ảnh đủ sáng và chụp gần hơn.',
          if (scale < 1)
            'Ảnh lớn đã được thu nhỏ để xử lý. Hãy cắt riêng từng bài nếu chữ quá nhỏ.',
          if (_recovered)
            'Đã khôi phục ảnh bạn chọn trước khi Android khởi động lại ứng dụng. Hãy kiểm tra lại ảnh và văn bản.',
          if (text.length > 20000)
            'Văn bản dài được giới hạn 20.000 ký tự. Hãy nhận dạng từng phần nhỏ.',
        ],
        'preview_data_url': 'data:image/png;base64,${base64Encode(preview)}',
      };
    } finally {
      try {
        await recognizer?.close();
      } finally {
        image?.dispose();
        codec?.dispose();
        descriptor?.dispose();
        buffer?.dispose();
        await directory.delete(recursive: true);
      }
    }
  }

  Future<void> cleanupPicked(String path) async {
    // Delete only a cache copy owned by this app, never an original gallery file.
    final root = await (await temporaryDirectory()).resolveSymbolicLinks();
    final file = File(path);
    if (!await file.exists()) return;
    final resolved = await file.resolveSymbolicLinks();
    if (resolved.startsWith('$root${Platform.pathSeparator}')) {
      await file.delete();
    }
  }
}

Future<Uint8List> _previewPng(ui.Image image) async {
  final scale = math.min(1.0, 600 / math.max(image.width, image.height));
  final width = math.max(1, (image.width * scale).round());
  final height = math.max(1, (image.height * scale).round());
  final recorder = ui.PictureRecorder();
  final canvas = ui.Canvas(recorder);
  canvas.drawRect(
    ui.Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble()),
    ui.Paint()..color = const ui.Color(0xffffffff),
  );
  canvas.drawImageRect(
    image,
    ui.Rect.fromLTWH(0, 0, image.width.toDouble(), image.height.toDouble()),
    ui.Rect.fromLTWH(0, 0, width.toDouble(), height.toDouble()),
    ui.Paint()..filterQuality = ui.FilterQuality.medium,
  );
  final picture = recorder.endRecording();
  ui.Image? preview;
  try {
    preview = await picture.toImage(width, height);
    final data = await preview.toByteData(format: ui.ImageByteFormat.png);
    if (data == null || data.lengthInBytes > 2 * 1024 * 1024) {
      throw const FormatException(
        'Không tạo được ảnh xem trước. Hãy thử ảnh khác.',
      );
    }
    return data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);
  } finally {
    preview?.dispose();
    picture.dispose();
  }
}
