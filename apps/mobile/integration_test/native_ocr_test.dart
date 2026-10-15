import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/painting.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:kho_hoc_mobile/ocr_runtime_native.dart';
import 'package:path_provider/path_provider.dart';

/// Exercises the production normalizer and real platform ML Kit recognizer.
/// The test supplies a synthetic page in place of the operating system picker;
/// neither the OCR engine nor the text result is mocked.
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets(
    'ML Kit reads a Vietnamese page without modifying its original image',
    (tester) async {
      expect(Platform.isAndroid || Platform.isIOS, isTrue);
      final font = FontLoader('NativeOcrQaNoto')
        ..addFont(rootBundle.load('assets/fonts/NotoSans.ttf'));
      await font.load();

      final recorder = ui.PictureRecorder();
      final canvas = ui.Canvas(recorder);
      canvas.drawColor(const ui.Color(0xffffffff), ui.BlendMode.src);
      final painter = TextPainter(
        text: const TextSpan(
          text:
              'Tự học 111\n'
              'Bài 1: Tính diện tích hình chữ nhật.\n'
              'Chiều dài 12 cm, chiều rộng 5 cm.\n'
              'Đáp số: 60 cm2.',
          style: TextStyle(
            fontFamily: 'NativeOcrQaNoto',
            fontSize: 42,
            height: 1.6,
            color: ui.Color(0xff000000),
          ),
        ),
        textDirection: ui.TextDirection.ltr,
      )..layout(maxWidth: 1130);
      painter.paint(canvas, const ui.Offset(35, 35));
      final picture = recorder.endRecording();
      final image = await picture.toImage(1200, 420);
      final data = await image.toByteData(format: ui.ImageByteFormat.png);
      expect(data, isNotNull);
      final originalBytes = data!.buffer.asUint8List(
        data.offsetInBytes,
        data.lengthInBytes,
      );
      image.dispose();
      picture.dispose();
      painter.dispose();

      final temporary = await getTemporaryDirectory();
      final fixture = await temporary.createTemp('tu-hoc-ocr-fixture-');
      addTearDown(() => fixture.delete(recursive: true));
      final original = File('${fixture.path}/vietnamese-page.png');
      await original.writeAsBytes(originalBytes, flush: true);

      final result = await recognizeNativeImageFile(original.path);
      final text = (result['text'] as String).toLowerCase();
      expect(text, contains('tự học'));
      expect(text, contains('hình chữ nhật'));
      expect(text, contains('chiều dài'));
      expect(text, contains('12'));
      expect(text, contains('5'));
      expect(text, contains('60'));
      // ML Kit does not expose a calibrated confidence for the complete page.
      expect(result['confidence'], isNull);
      expect(result['warnings'], isA<List>());
      final preview = result['preview_data_url'] as String;
      expect(preview, startsWith('data:image/png;base64,'));
      expect(base64Decode(preview.split(',').last).length, greaterThan(100));
      expect(await original.readAsBytes(), orderedEquals(originalBytes));
    },
    timeout: const Timeout(Duration(minutes: 3)),
  );
}
