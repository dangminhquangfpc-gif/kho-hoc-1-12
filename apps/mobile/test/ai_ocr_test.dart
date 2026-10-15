import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/ai_ocr_screen.dart';
import 'package:kho_hoc_mobile/ocr_runtime.dart';
import 'package:kho_hoc_mobile/repository.dart';

import 'practice_test.dart' show FakeApi;

class TutorApi extends FakeApi {
  bool configured = true, statusFails = false;
  bool changeProvider = false;
  String providerHost = 'ai.example.test';
  int statusCalls = 0;
  final List<Json> requests = [];
  @override
  Future<Json> aiStatus() async {
    statusCalls++;
    if (statusFails) throw StateError('offline');
    return {
      'configured': configured,
      'provider_host': configured ? providerHost : null,
      'model': configured ? 'test-model' : null,
      'daily_user_limit': 20,
      'daily_server_limit': 200,
    };
  }

  @override
  Future<Json> explainAi({
    required int grade,
    required String subject,
    required String text,
    required bool consent,
    required String expectedProviderHost,
    String? attemptId,
    String? questionId,
  }) async {
    requests.add({
      'grade': grade,
      'subject': subject,
      'text': text,
      'consent': consent,
      'expected_provider_host': expectedProviderHost,
      if (attemptId != null) 'attempt_id': attemptId,
      if (questionId != null) 'question_id': questionId,
    });
    if (changeProvider) {
      changeProvider = false;
      providerHost = 'new-ai.example.test';
      throw DioException(
        requestOptions: RequestOptions(path: '/ai/explain'),
        response: Response(
          requestOptions: RequestOptions(path: '/ai/explain'),
          statusCode: 409,
          data: {'detail': 'Dịch vụ AI đã thay đổi. Hãy xác nhận lại.'},
        ),
      );
    }
    return {
      'explanation': 'Hãy tính tổng theo từng hàng.',
      'steps': ['Đặt các hàng thẳng cột.'],
      'uncertainties': ['Kiểm tra lại dữ kiện đã nhận chữ.'],
      'needs_review': true,
      'grounded': attemptId != null,
      'provider_host': 'ai.example.test',
      'model': 'test-model',
    };
  }
}

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
  Widget app(TutorApi api, Widget screen, {bool signedIn = true}) =>
      ProviderScope(
        overrides: [
          apiProvider.overrideWithValue(api),
          authUserProvider.overrideWith(
            (ref) => signedIn
                ? {'id': 'student', 'role': 'student', 'grade': 5}
                : null,
          ),
        ],
        child: MaterialApp(home: screen),
      );

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
    'OCR text requires checking and fresh consent before text-only AI request',
    (tester) async {
      await wide(tester);
      final api = TutorApi();
      final ocr = TestOcr(
        () async => const OcrResult(
          text: '3 + 2 = 6',
          confidence: 42,
          warnings: ['Kiểm tra các dấu trong ảnh.'],
        ),
      );
      await tester.pumpWidget(app(api, AiOcrScreen(recognizer: ocr)));
      await tester.pumpAndSettle();
      await tapText(tester, 'Chọn ảnh để nhận chữ');
      expect(find.textContaining('Ảnh có độ tin cậy thấp'), findsOneWidget);
      expect(api.requests, isEmpty);
      await tester.enterText(
        find.byKey(const Key('ocr-edited-text')),
        '3 + 2 bằng bao nhiêu?',
      );
      await tester.pump();
      await tester.scrollUntilVisible(
        find.text('Xin hướng dẫn từ AI'),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      var button = tester.widget<FilledButton>(
        find
            .ancestor(
              of: find.text('Xin hướng dẫn từ AI'),
              matching: find.byWidgetPredicate((w) => w is FilledButton),
            )
            .first,
      );
      expect(button.onPressed, isNull);
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      await tapText(tester, 'Xin hướng dẫn từ AI');
      expect(find.textContaining('ai.example.test'), findsWidgets);
      expect(api.requests, isEmpty);
      await tester.tap(find.widgetWithText(TextButton, 'Hủy'));
      await tester.pumpAndSettle();
      expect(api.requests, isEmpty);
      await tapText(tester, 'Xin hướng dẫn từ AI');
      await tester.tap(find.text('Đồng ý gửi văn bản'));
      await tester.pumpAndSettle();
      expect(api.requests.single, {
        'grade': 5,
        'subject': 'toan',
        'text': '3 + 2 bằng bao nhiêu?',
        'consent': true,
        'expected_provider_host': 'ai.example.test',
      });
      await tester.scrollUntilVisible(
        find.text('Hướng dẫn AI cần kiểm tra lại'),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      expect(find.text('Hướng dẫn AI cần kiểm tra lại'), findsOneWidget);
      await tester.scrollUntilVisible(
        find.byKey(const Key('ocr-edited-text')),
        -400,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.enterText(
        find.byKey(const Key('ocr-edited-text')),
        'Nội dung khác',
      );
      await tester.pump();
      await tester.scrollUntilVisible(
        find.text('Xin hướng dẫn từ AI'),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      button = tester.widget<FilledButton>(
        find
            .ancestor(
              of: find.text('Xin hướng dẫn từ AI'),
              matching: find.byWidgetPredicate((w) => w is FilledButton),
            )
            .first,
      );
      expect(button.onPressed, isNull);
      expect(api.requests, hasLength(1));
    },
  );

  testWidgets(
    'Cancel and failure preserve existing editable answer, retry works',
    (tester) async {
      await wide(tester);
      final api = TutorApi();
      final pending = Completer<OcrResult?>();
      final ocr = TestOcr(() => pending.future);
      await tester.pumpWidget(
        app(api, AiOcrScreen(initialText: 'Đáp án đã viết', recognizer: ocr)),
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
      expect(api.requests, isEmpty);
    },
  );

  testWidgets(
    'Native/manual fallback returns one-character answer only after checking',
    (tester) async {
      await wide(tester);
      final api = TutorApi();
      String? returned;
      await tester.pumpWidget(
        app(
          api,
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
          signedIn: false,
        ),
      );
      await tester.tap(find.text('Mở nhận chữ'));
      await tester.pumpAndSettle();
      expect(find.textContaining('Bản chạy trên thiết bị này'), findsOneWidget);
      expect(find.text('Trợ lý học tập AI'), findsNothing);
      expect(api.statusCalls, 0);
      final button = tester.widget<FilledButton>(
        find.widgetWithText(FilledButton, 'Dùng văn bản này cho câu trả lời'),
      );
      expect(button.onPressed, isNull);
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      await tapText(tester, 'Dùng văn bản này cho câu trả lời');
      expect(returned, '5');
      expect(api.requests, isEmpty);
    },
  );

  testWidgets(
    'Native OCR without a confidence score still needs edited-text confirmation',
    (tester) async {
      await tester.binding.setSurfaceSize(const Size(390, 844));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      final api = TutorApi();
      final ocr = TestOcr(
        () async => const OcrResult(
          text: '5',
          confidence: null,
          warnings: ['Kiểm tra lại chữ nhận từ ảnh trước khi dùng.'],
        ),
      );
      await tester.pumpWidget(
        app(
          api,
          AiOcrScreen(
            initialText: 'Câu trả lời cũ',
            returnTextOnly: true,
            recognizer: ocr,
          ),
          signedIn: false,
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
      expect(api.requests, isEmpty);
      expect(api.statusCalls, 0);
      expect(tester.takeException(), isNull);
    },
    variant: TargetPlatformVariant.only(TargetPlatform.android),
  );

  testWidgets('Closing the image picker preserves the existing answer', (
    tester,
  ) async {
    await wide(tester);
    final api = TutorApi();
    final ocr = TestOcr(() async => null);
    await tester.pumpWidget(
      app(
        api,
        AiOcrScreen(
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
    expect(api.requests, isEmpty);
  });

  testWidgets(
    'Unconfigured AI remains honest and status can be retried after failure',
    (tester) async {
      await wide(tester);
      final api = TutorApi()..configured = false;
      await tester.pumpWidget(
        app(api, const AiOcrScreen(initialText: 'Giải thích phép cộng')),
      );
      await tester.pumpAndSettle();
      expect(find.textContaining('AI chưa được cấu hình'), findsOneWidget);
      expect(find.textContaining('liên hệ người quản lý'), findsOneWidget);
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      await tester.scrollUntilVisible(
        find.text('Xin hướng dẫn từ AI'),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      expect(
        tester
            .widget<FilledButton>(
              find
                  .ancestor(
                    of: find.text('Xin hướng dẫn từ AI'),
                    matching: find.byWidgetPredicate((w) => w is FilledButton),
                  )
                  .first,
            )
            .onPressed,
        isNull,
      );
      api.statusFails = true;
      await tapText(tester, 'Kiểm tra lại trạng thái AI');
      expect(
        find.text('Chưa tải được trạng thái AI. Hãy thử lại.'),
        findsOneWidget,
      );
      api.statusFails = false;
      api.configured = true;
      await tapText(tester, 'Kiểm tra lại trạng thái AI');
      await tester.scrollUntilVisible(
        find.text('Xin hướng dẫn từ AI'),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      expect(
        tester
            .widget<FilledButton>(
              find
                  .ancestor(
                    of: find.text('Xin hướng dẫn từ AI'),
                    matching: find.byWidgetPredicate((w) => w is FilledButton),
                  )
                  .first,
            )
            .onPressed,
        isNotNull,
      );
      expect(api.requests, isEmpty);
    },
  );

  testWidgets(
    'Stored reference is disclosed and can be omitted from a grounded request',
    (tester) async {
      await wide(tester);
      final api = TutorApi();
      await tester.pumpWidget(
        app(
          api,
          const AiOcrScreen(
            initialText: 'Bài này cần giải thích.',
            initialGrade: 5,
            initialSubject: 'toan',
            attemptId: 'owned-submitted',
            questionId: 'question',
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      await tapText(tester, 'Xin hướng dẫn từ AI');
      expect(find.textContaining('Máy chủ còn gửi đề bài'), findsOneWidget);
      await tester.tap(find.text('Đồng ý gửi văn bản'));
      await tester.pumpAndSettle();
      expect(api.requests.single['attempt_id'], 'owned-submitted');
      await tester.scrollUntilVisible(
        find.text('Dùng đáp án và lời giải đã lưu làm tham chiếu'),
        -300,
        scrollable: find.byType(Scrollable).first,
      );
      await tapText(tester, 'Dùng đáp án và lời giải đã lưu làm tham chiếu');
      await tapText(tester, 'Xin hướng dẫn từ AI');
      expect(find.textContaining('Máy chủ còn gửi đề bài'), findsNothing);
      await tester.tap(find.text('Đồng ý gửi văn bản'));
      await tester.pumpAndSettle();
      expect(api.requests.last.containsKey('attempt_id'), isFalse);
      expect(api.requests.last.containsKey('question_id'), isFalse);
    },
  );

  testWidgets(
    'Changed provider requires refreshed destination and new consent',
    (tester) async {
      await wide(tester);
      final api = TutorApi()..changeProvider = true;
      await tester.pumpWidget(
        app(api, const AiOcrScreen(initialText: 'Giải thích phép cộng')),
      );
      await tester.pumpAndSettle();
      await tapText(tester, 'Tôi đã kiểm tra văn bản');
      await tapText(tester, 'Xin hướng dẫn từ AI');
      expect(
        find.textContaining('đến dịch vụ AI tại ai.example.test'),
        findsOneWidget,
      );
      await tester.tap(find.text('Đồng ý gửi văn bản'));
      await tester.pumpAndSettle();
      expect(api.statusCalls, 2);
      expect(api.requests.single['expected_provider_host'], 'ai.example.test');
      await tapText(tester, 'Xin hướng dẫn từ AI');
      expect(
        find.textContaining('đến dịch vụ AI tại new-ai.example.test'),
        findsOneWidget,
      );
      expect(api.requests, hasLength(1));
      await tester.tap(find.text('Đồng ý gửi văn bản'));
      await tester.pumpAndSettle();
      expect(
        api.requests.last['expected_provider_host'],
        'new-ai.example.test',
      );
    },
  );
}
