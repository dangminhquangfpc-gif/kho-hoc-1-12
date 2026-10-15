import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/ocr_image_validation.dart';
import 'package:kho_hoc_mobile/ocr_runtime_native.dart';

Uint8List samplePng() => base64Decode(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGP4DwQACfsD/fteaysAAAAASUVORK5CYII=',
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('preflight rejects untrusted file types, sizes and dimensions', () {
    final size = validateOcrImage(samplePng());
    expect([size.width, size.height], [1, 1]);
    for (final input in [
      Uint8List(0),
      Uint8List(maxOcrImageBytes + 1),
      Uint8List.fromList('<svg width="1"/>'.codeUnits),
      samplePng().sublist(0, 32),
    ]) {
      expect(() => validateOcrImage(input), throwsFormatException);
    }
    for (final dimensions in [
      [7000, 1],
      [5000, 4000],
      [0, 1],
    ]) {
      final bytes = samplePng();
      final data = ByteData.sublistView(bytes);
      data.setUint32(16, dimensions[0]);
      data.setUint32(20, dimensions[1]);
      expect(() => validateOcrImage(bytes), throwsFormatException);
    }
    final animated = Uint8List(42);
    animated.setRange(0, 4, 'RIFF'.codeUnits);
    animated.setRange(8, 12, 'WEBP'.codeUnits);
    animated.setRange(12, 16, 'VP8X'.codeUnits);
    final data = ByteData.sublistView(animated);
    data.setUint32(4, animated.length - 8, Endian.little);
    data.setUint32(16, 10, Endian.little);
    animated[20] = 2;
    expect(() => validateOcrImage(animated), throwsFormatException);
  });

  test('cancelled gallery selection never invokes OCR', () async {
    var invoked = false;
    final engine = NativeOcrSession(
      pickImage: () async => null,
      processImage: (_, __) async {
        invoked = true;
        return {};
      },
      cleanupPicked: (_) async => fail('No selected file should be deleted'),
    );
    expect(await engine.recognize(), isNull);
    expect(invoked, isFalse);
  });

  test(
    'cancel during picker cleans late file, without reading its contents',
    () async {
      final picked = Completer<String?>();
      final cleaned = Completer<void>();
      final engine = NativeOcrSession(
        pickImage: () => picked.future,
        processImage: (_, __) async => throw StateError('OCR must not run'),
        cleanupPicked: (path) async {
          expect(path, 'cache-copy');
          cleaned.complete();
        },
      );
      final work = engine.recognize();
      engine.cancel();
      expect(await work, isNull);
      expect(() => engine.recognize(), throwsStateError);
      picked.complete('cache-copy');
      await cleaned.future;
      await Future<void>.delayed(Duration.zero);
    },
  );

  test(
    'cancel discards late native result and blocks overlapping work',
    () async {
      final pending = Completer<Map<String, dynamic>>();
      final started = Completer<void>();
      final cleaned = Completer<void>();
      late bool Function() stopped;
      final engine = NativeOcrSession(
        pickImage: () async => 'cache-copy',
        processImage: (_, cancelled) {
          stopped = cancelled;
          started.complete();
          return pending.future;
        },
        cleanupPicked: (_) async => cleaned.complete(),
      );
      final work = engine.recognize();
      await started.future;
      expect(() => engine.recognize(), throwsStateError);
      engine.cancel();
      expect(await work, isNull);
      expect(stopped(), isTrue);
      pending.complete({'text': 'must not overwrite edited text'});
      await cleaned.future;
      await Future<void>.delayed(Duration.zero);
    },
  );

  test(
    'timeout completes promptly and eventual native failure is discarded',
    () async {
      final pending = Completer<Map<String, dynamic>>();
      final cleaned = Completer<void>();
      final engine = NativeOcrSession(
        pickImage: () async => 'cache-copy',
        processImage: (_, __) => pending.future,
        cleanupPicked: (_) async => cleaned.complete(),
        timeout: const Duration(milliseconds: 10),
      );
      await expectLater(engine.recognize(), throwsA(isA<TimeoutException>()));
      pending.completeError(StateError('private path must not leak'));
      await cleaned.future;
      await Future<void>.delayed(Duration.zero);
    },
  );

  test(
    'native plugin errors omit raw platform messages and private paths',
    () async {
      var cleaned = false;
      final engine = NativeOcrSession(
        pickImage: () async => 'private-cache-image',
        processImage: (_, __) async => throw PlatformException(
          code: 'decode',
          message: 'secret-private-path',
        ),
        cleanupPicked: (_) async => cleaned = true,
      );
      await expectLater(
        engine.recognize(),
        throwsA(
          predicate(
            (e) =>
                e is StateError &&
                !e.toString().contains('secret-private-path'),
          ),
        ),
      );
      expect(cleaned, isTrue);
    },
  );

  test(
    'cleanup protects originals and symlinks outside app-private cache',
    () async {
      final testRoot = await Directory.systemTemp.createTemp(
        'native-ocr-test-',
      );
      try {
        final cache = await Directory('${testRoot.path}/cache').create();
        final original = await File(
          '${testRoot.path}/original.png',
        ).writeAsBytes(samplePng());
        final copied = await File(
          '${cache.path}/copy.png',
        ).writeAsBytes(samplePng());
        final linked = await Link(
          '${cache.path}/link.png',
        ).create(original.path);
        final platform = NativeOcrPlatform(
          temporaryDirectory: () async => cache,
        );
        await platform.cleanupPicked(original.path);
        await platform.cleanupPicked(linked.path);
        expect(await original.exists(), isTrue);
        expect(await linked.exists(), isTrue);
        await platform.cleanupPicked(copied.path);
        expect(await copied.exists(), isFalse);
      } finally {
        await testRoot.delete(recursive: true);
      }
    },
  );

  testWidgets(
    'actual decoder re-encodes pixels and cleans temp on ML Kit failure',
    (tester) async {
      await tester.runAsync(() async {
        final testRoot = await Directory.systemTemp.createTemp(
          'native-ocr-pixels-',
        );
        final original = await File(
          '${testRoot.path}/original.png',
        ).writeAsBytes(samplePng());
        final cache = await Directory('${testRoot.path}/cache').create();
        const channel = MethodChannel('google_mlkit_text_recognizer');
        String? normalizedPath;
        var closed = false;
        TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
            .setMockMethodCallHandler(channel, (call) async {
              if (call.method == 'vision#closeTextRecognizer') {
                closed = true;
                return null;
              }
              final args = Map<String, dynamic>.from(call.arguments as Map);
              // Only the Latin model is bundled; other scripts are optional
              // compileOnly branches in the Android plugin and must not run.
              expect(args['script'], 0);
              final image = Map<String, dynamic>.from(args['imageData'] as Map);
              normalizedPath = image['path'] as String;
              expect(normalizedPath, startsWith(cache.path));
              expect(normalizedPath, isNot(original.path));
              final normalized = await File(normalizedPath!).readAsBytes();
              expect(validateOcrImage(normalized).width, 1);
              throw PlatformException(code: 'test-native-failure');
            });
        try {
          final platform = NativeOcrPlatform(
            temporaryDirectory: () async => cache,
          );
          await expectLater(
            platform.processImage(original.path, () => false),
            throwsA(isA<PlatformException>()),
          );
          expect(closed, isTrue);
          expect(await File(normalizedPath!).exists(), isFalse);
          expect(await cache.list().toList(), isEmpty);
          expect(await original.readAsBytes(), orderedEquals(samplePng()));
        } finally {
          TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger
              .setMockMethodCallHandler(channel, null);
          await testRoot.delete(recursive: true);
        }
      });
    },
  );
}
