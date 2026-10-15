import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/account_screen.dart';
import 'package:kho_hoc_mobile/content_reports.dart';
import 'package:kho_hoc_mobile/main.dart';
import 'package:kho_hoc_mobile/progress_screen.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'practice_test.dart' show FakeApi;

class LocalOnlyUiApi extends LearningApi {
  @override
  bool get isOffline => true;

  @override
  Future<List<Json>> subjects(int grade) async => [
    {'id': 'toan', 'name': 'Toán'},
  ];

  @override
  Future<List<Json>> exams(int grade, String subject, String search) async =>
      [];

  @override
  Future<List<Json>> coverage(int grade) async => [];
}

void main() {
  Future<void> wide(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(900, 1600));
    addTearDown(() => tester.binding.setSurfaceSize(null));
  }

  ProviderScope localScope(Widget child) => ProviderScope(
    overrides: [
      apiProvider.overrideWithValue(LocalOnlyUiApi()),
      authUserProvider.overrideWith(
        (ref) => throw StateError('Local study must not read a server account'),
      ),
    ],
    child: MaterialApp(home: child),
  );

  setUp(() {
    SharedPreferences.setMockInitialValues({'study_offline': true});
  });

  testWidgets('Local account screen does not expose authentication or groups', (
    tester,
  ) async {
    await wide(tester);
    await tester.pumpWidget(localScope(const AccountScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Bạn đang học trên thiết bị'), findsOneWidget);
    expect(find.text('Kết nối máy chủ lớp học'), findsOneWidget);
    expect(find.text('Nhận chữ từ ảnh'), findsOneWidget);
    expect(find.byType(TextField), findsNothing);
    expect(find.byType(GroupPanel), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Local home works without a server account and labels storage', (
    tester,
  ) async {
    await wide(tester);
    await tester.pumpWidget(localScope(const HomeScreen(index: 2)));
    await tester.pumpAndSettle();
    expect(find.text('Học trên thiết bị'), findsOneWidget);
    expect(
      find.textContaining('không tự đồng bộ vào tài khoản'),
      findsOneWidget,
    );
    expect(find.text('Tạo đề theo chủ đề và độ khó'), findsNothing);
    expect(
      find.text('Không thể tải dữ liệu. Kiểm tra kết nối rồi thử lại.'),
      findsNothing,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets('Local progress and reports do not request server account data', (
    tester,
  ) async {
    await wide(tester);
    await tester.pumpWidget(localScope(const ProgressScreen()));
    await tester.pumpAndSettle();
    expect(find.text('Đã hoàn thành 0 bài luyện tập'), findsOneWidget);
    expect(
      find.textContaining('Điểm tự luyện chỉ lưu trên thiết bị'),
      findsOneWidget,
    );
    expect(find.text('Tạo đề theo chủ đề'), findsNothing);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(
      localScope(
        const Scaffold(
          body: ReportContentButton(
            kind: 'question',
            targetId: 'local-question',
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.text('Báo lỗi nội dung'), findsNothing);
    expect(tester.takeException(), isNull);
  });

  test('Server results providers remain empty in local mode', () async {
    final container = ProviderContainer(
      overrides: [
        apiProvider.overrideWithValue(LocalOnlyUiApi()),
        authUserProvider.overrideWith(
          (ref) => throw StateError('Must not request a server account'),
        ),
      ],
    );
    addTearDown(container.dispose);
    expect(await container.read(serverResultsProvider.future), isEmpty);
    expect(await container.read(pendingAttemptsProvider.future), isEmpty);
  });

  testWidgets('An older local draft has no server expiry or recovery warning', (
    tester,
  ) async {
    await wide(tester);
    final prefs = await SharedPreferences.getInstance();
    final draft = await FakeApi().start('exam');
    draft['local_self_practice'] = true;
    draft['created_at'] = DateTime.now()
        .subtract(const Duration(days: 2))
        .toUtc()
        .toIso8601String();
    await LocalStore(prefs).save(draft);
    await tester.pumpWidget(localScope(const PracticeScreen()));
    await tester.pumpAndSettle();
    expect(find.textContaining('Bài lưu đã quá 24 giờ'), findsNothing);
    expect(find.text('Khôi phục bài đã lưu'), findsNothing);
    expect(find.textContaining('Tự luyện trên thiết bị'), findsOneWidget);
    expect(
      tester
          .widget<FilledButton>(find.widgetWithText(FilledButton, 'Nộp bài'))
          .onPressed,
      isNotNull,
    );
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox.shrink());
  });
}
