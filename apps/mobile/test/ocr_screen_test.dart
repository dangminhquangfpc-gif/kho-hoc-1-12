import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/ocr_screen.dart';
import 'package:kho_hoc_mobile/ocr_runtime.dart';

class TestOcr implements OcrRecognizer {
  TestOcr(this.action);
  Future<OcrResult?> Function() action;
  bool cancelled = false;
  @override
  bool get available => true;
  @override
  Future<OcrResult?> recognize() => action();
  @override
  void cancel() => cancelled = true;
}

void main() {
  Widget app(Widget screen) => MaterialApp(home: screen);

  Future<void> wide(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1000, 1800));
    addTearDown(() => tester.binding.setSurfaceSize(null));
  }

  Future<void> tapText(WidgetTester tester, String label) async {
    final finder = find.text(label);
    await tester.scrollUntilVisible(
      finder,
      250,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(finder);
    await tester.pumpAndSettle();
  }

  testWidgets(
    'Cancel and failure preserve existing editable answer, retry works',
    (tester) async {
      await wide(tester);
      final pending = Completer<OcrResult?>();
      final ocr = TestOcr(() => pending.future);
      await tester.pumpWidget(
        app(OcrScreen(initialText: 'Đáp án đã viết', recognizer: ocr)),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Chọn ảnh để nhận chữ'));
      await tester.pump();
      await tester.tap(find.text('Hủy nhận dạng'));
      await tester.pumpAndSettle();
      expect(ocr.cancelled, isTrue);
      pending.complete(
        const OcrResult(text: 'Kết quả đến muộn', confidence: 99),
      );
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<TextField>(find.byKey(const Key('ocr-edited-text')))
            .controller!
            .text,
        'Đáp án đã viết',
      );
      ocr.action = () async => throw StateError('Ảnh chưa rõ');
      await tapText(tester, 'Chọn ảnh để nhận chữ');
      expect(find.textContaining('Ảnh chưa rõ'), findsOneWidget);
      expect(
        tester
            .widget<TextField>(find.byKey(const Key('ocr-edited-text')))
            .controller!
            .text,
        'Đáp án đã viết',
      );
      ocr.action = () async =>
          const OcrResult(text: 'Đọc lại thành công', confidence: 90);
      await tapText(tester, 'Chọn ảnh để nhận chữ');
      expect(
        tester
            .widget<TextField>(find.byKey(const Key('ocr-edited-text')))
            .controller!
            .text,
        'Đọc lại thành công',
      );
    },
  );

  testWidgets(
    'Native/manual fallback returns one-character answer only after checking',
    (tester) async {
      await wide(tester);
      String? returned;
      await tester.pumpWidget(
        app(
          Builder(
            builder: (context) => Scaffold(
              body: TextButton(
                onPressed: () async {
                  returned = await showOcrTextDialog(context, initialText: '5');
                },
                child: const Text('Mở nhận chữ'),
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Mở nhận chữ'));
      await tester.pumpAndSettle();
      expect(find.textContaining('Bản chạy trên thiết bị này'), findsOneWidget);
      final button = tester.widget<FilledButton>(
        find.widgetWithText(FilledButton, 'Dùng văn bản này cho câu trả lời'),
      );
      expect(button.onPressed, isNull);
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      await tapText(tester, 'Dùng văn bản này cho câu trả lời');
      expect(returned, '5');
    },
  );

  testWidgets(
    'Native OCR without a confidence score still needs edited-text confirmation',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final ocr = TestOcr(
        () async => const OcrResult(
          text: '5',
          confidence: null,
          warnings: ['Kiểm tra lại chữ nhận từ ảnh trước khi dùng.'],
        ),
      );
      await tester.pumpWidget(
        app(
          OcrScreen(
            initialText: 'Câu trả lời cũ',
            returnTextOnly: true,
            recognizer: ocr,
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.textContaining('Google ML Kit có thể gửi'), findsOneWidget);
      expect(find.textContaining('không cung cấp chỉ số'), findsNothing);
      await tapText(tester, 'Chọn ảnh để nhận chữ');
      expect(find.textContaining('không cung cấp chỉ số'), findsOneWidget);
      expect(find.textContaining('Độ tin cậy nhận chữ:'), findsNothing);
      expect(find.textContaining('độ tin cậy thấp'), findsNothing);
      expect(
        tester
            .widget<TextField>(find.byKey(const Key('ocr-edited-text')))
            .controller!
            .text,
        '5',
      );
      await tester.scrollUntilVisible(
        find.text('Dùng văn bản này cho câu trả lời'),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      expect(
        tester
            .widget<FilledButton>(
              find.widgetWithText(
                FilledButton,
                'Dùng văn bản này cho câu trả lời',
              ),
            )
            .onPressed,
        isNull,
      );
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      expect(
        tester
            .widget<FilledButton>(
              find.widgetWithText(
                FilledButton,
                'Dùng văn bản này cho câu trả lời',
              ),
            )
            .onPressed,
        isNotNull,
      );
      expect(tester.takeException(), isNull);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.android),
  );

  testWidgets('Closing the image picker preserves the existing answer', (
    tester,
  ) async {
    await wide(tester);
    final ocr = TestOcr(() async => null);
    await tester.pumpWidget(
      app(
        OcrScreen(
          initialText: 'Đáp án đã kiểm tra',
          returnTextOnly: true,
          recognizer: ocr,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tapText(tester, 'Tôi đã kiểm tra văn bản');
    await tapText(tester, 'Chọn ảnh để nhận chữ');
    expect(
      tester
          .widget<TextField>(find.byKey(const Key('ocr-edited-text')))
          .controller!
          .text,
      'Đáp án đã kiểm tra',
    );
    expect(
      tester
          .widget<FilledButton>(
            find.widgetWithText(
              FilledButton,
              'Dùng văn bản này cho câu trả lời',
            ),
          )
          .onPressed,
      isNotNull,
    );
  });

  testWidgets(
    'Standalone OCR copies checked text and edits revoke confirmation',
    (tester) async {
      await wide(tester);
      String? copied;
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        SystemChannels.platform,
        (call) async {
          if (call.method == 'Clipboard.setData') {
            copied = call.arguments['text'] as String;
          }
          return null;
        },
      );
      addTearDown(
        () => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
          SystemChannels.platform,
          null,
        ),
      );
      final recognizer = TestOcr(
        () async => const OcrResult(
          text: '3 + 2 = 6',
          confidence: 42,
          warnings: ['Kiểm tra các dấu trong ảnh.'],
        ),
      );
      // No ProviderScope, auth state or API is required to read and copy text.
      await tester.pumpWidget(app(OcrScreen(recognizer: recognizer)));
      await tester.pumpAndSettle();
      await tapText(tester, 'Chọn ảnh để nhận chữ');
      expect(find.textContaining('Ảnh có độ tin cậy thấp'), findsOneWidget);
      expect(find.text('Kiểm tra các dấu trong ảnh.'), findsOneWidget);
      final editor = find.byKey(const Key('ocr-edited-text'));
      await tester.enterText(editor, '3 + 2 = 5');
      await tester.pump();
      Finder copyButton() => find
          .ancestor(
            of: find.text('Sao chép văn bản đã kiểm tra'),
            matching: find.byWidgetPredicate(
              (widget) => widget is FilledButton,
            ),
          )
          .first;
      expect(tester.widget<FilledButton>(copyButton()).onPressed, isNull);
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      await tapText(tester, 'Sao chép văn bản đã kiểm tra');
      expect(copied, '3 + 2 = 5');
      expect(find.text('Đã sao chép văn bản.'), findsOneWidget);
      await tester.enterText(editor, 'Nội dung khác');
      await tester.pump();
      expect(tester.widget<FilledButton>(copyButton()).onPressed, isNull);
      expect(copied, '3 + 2 = 5');
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'Empty OCR preserves an answer and long text is limited explicitly',
    (tester) async {
      await wide(tester);
      final recognizer = TestOcr(
        () async => const OcrResult(text: '', confidence: 0),
      );
      await tester.pumpWidget(
        app(OcrScreen(initialText: 'Đáp án cũ', recognizer: recognizer)),
      );
      await tester.pumpAndSettle();
      await tapText(tester, 'Chọn ảnh để nhận chữ');
      final editor = find.byKey(const Key('ocr-edited-text'));
      expect(tester.widget<TextField>(editor).controller!.text, 'Đáp án cũ');
      expect(find.textContaining('Không đọc được chữ.'), findsOneWidget);
      recognizer.action = () async =>
          OcrResult(text: List.filled(6001, 'a').join(), confidence: 90);
      await tapText(tester, 'Chọn ảnh để nhận chữ');
      expect(tester.widget<TextField>(editor).controller!.text.length, 6000);
      expect(
        find.text('Chỉ giữ 6.000 ký tự đầu. Hãy chia nhỏ ảnh.'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('Leaving OCR cancels recognition and ignores a late result', (
    tester,
  ) async {
    await wide(tester);
    final pending = Completer<OcrResult?>();
    final recognizer = TestOcr(() => pending.future);
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: TextButton(
              onPressed: () => Navigator.of(context).push<void>(
                MaterialPageRoute(
                  builder: (_) => OcrScreen(recognizer: recognizer),
                ),
              ),
              child: const Text('Mở nhận chữ'),
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Mở nhận chữ'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chọn ảnh để nhận chữ'));
    await tester.pump();
    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();
    expect(recognizer.cancelled, isTrue);
    pending.complete(const OcrResult(text: 'Kết quả đến muộn', confidence: 90));
    await tester.pumpAndSettle();
    expect(find.byType(OcrScreen), findsNothing);
    expect(tester.takeException(), isNull);
  });
}
