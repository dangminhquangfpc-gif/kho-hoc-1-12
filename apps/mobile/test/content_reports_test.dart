import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/content_reports.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'accounts_test.dart' show SchoolApi;

class FeedbackApi extends SchoolApi {
  Json? sent, reviewed;
  Json report = {
    'id': 'report',
    'target_title': 'Bài học kiểm thử',
    'excerpt': 'Đề bài cần giải thích',
    'target_kind': 'question',
    'target_id': 'q',
    'category': 'unclear',
    'message': 'Cần giải thích rõ hơn',
    'status': 'open',
    'response': '',
    'revision': 1,
    'created_at': '2026-10-15T10:00:00Z',
  };
  @override
  Future<Json> sendContentReport(Json body) async {
    sent = body;
    return report;
  }

  @override
  Future<List<Json>> contentReports({
    bool review = false,
    String? status,
    int offset = 0,
  }) async => [report];
  @override
  Future<Json> reviewContentReport(String id, Json body) async {
    reviewed = body;
    report = {...report, ...body};
    return report;
  }
}

void main() {
  Widget app(FeedbackApi api, Widget child) => ProviderScope(
    overrides: [
      apiProvider.overrideWithValue(api),
      authUserProvider.overrideWith(
        (ref) => {'id': 'student', 'role': 'student'},
      ),
    ],
    child: MaterialApp(home: Scaffold(body: child)),
  );
  testWidgets(
    'Learner validates and sends an owned question report without changing answers',
    (tester) async {
      final api = FeedbackApi();
      await tester.pumpWidget(
        app(
          api,
          const ReportContentButton(
            kind: 'question',
            targetId: 'q',
            attemptId: 'attempt',
          ),
        ),
      );
      await tester.tap(find.text('Báo lỗi nội dung'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Gửi phản hồi'));
      await tester.pumpAndSettle();
      expect(find.text('Vui lòng mô tả ít nhất 5 ký tự.'), findsOneWidget);
      expect(api.sent, isNull);
      await tester.enterText(
        find.widgetWithText(TextField, 'Mô tả vấn đề'),
        'Bài này cần giải thích rõ hơn.',
      );
      await tester.tap(find.text('Gửi phản hồi'));
      await tester.pumpAndSettle();
      expect(api.sent!['attempt_id'], 'attempt');
      expect(api.sent!['target_id'], 'q');
      expect(api.sent!.containsKey('answers'), isFalse);
      expect(find.textContaining('Đã gửi phản hồi.'), findsOneWidget);
    },
  );
  testWidgets(
    'Teacher saves explanation with expected revision; own reports have no review action',
    (tester) async {
      final api = FeedbackApi();
      await tester.pumpWidget(
        app(api, const ContentReportsScreen(review: true)),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Xem xét và trả lời'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.widgetWithText(TextField, 'Giải thích cho học viên'),
        'Giáo viên sẽ bổ sung bước giải.',
      );
      await tester.tap(find.text('Lưu trả lời'));
      await tester.pumpAndSettle();
      expect(api.reviewed!['revision'], 1);
      expect(api.reviewed!['status'], 'in_review');
      expect(find.textContaining('Trả lời: Giáo viên'), findsOneWidget);
      await tester.pumpWidget(
        app(api, const ContentReportsScreen(key: ValueKey('mine'))),
      );
      await tester.pumpAndSettle();
      expect(find.text('Xem xét và trả lời'), findsNothing);
    },
  );
}
