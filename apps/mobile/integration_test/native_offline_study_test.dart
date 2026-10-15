import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:kho_hoc_mobile/main.dart' as app;
import 'package:shared_preferences/shared_preferences.dart';

/// Run only on a fresh, disposable Android/iOS test installation. This uses the
/// real entry point, bundled assets and platform SharedPreferences implementation;
/// no API/provider/storage replacement is installed. It does not erase existing
/// learner data and intentionally fails if the test device is not clean.
///
/// The HTTP guard proves this study flow does not create a Dart HTTP client. CI
/// also disables emulator Wi-Fi/mobile data. It does not observe platform SDK
/// diagnostic traffic or claim that every native library has zero network use.
class _RejectDartHttp extends HttpOverrides {
  int clientsCreated = 0;

  @override
  HttpClient createHttpClient(SecurityContext? context) {
    clientsCreated++;
    throw StateError('Native offline study attempted Dart networking');
  }
}

Future<void> _until(
  WidgetTester tester,
  bool Function() ready, {
  String reason = 'The expected UI or persisted value did not become ready',
  Duration timeout = const Duration(seconds: 45),
}) async {
  final watch = Stopwatch()..start();
  while (!ready() && watch.elapsed < timeout) {
    await tester.pump(const Duration(milliseconds: 100));
    // Asset decoding uses a real isolate and storage uses platform messages.
    // Give these operations wall-clock time instead of only advancing frames.
    await tester.runAsync(
      () => Future<void>.delayed(const Duration(milliseconds: 40)),
    );
  }
  expect(ready(), isTrue, reason: reason);
}

Future<void> _show(
  WidgetTester tester,
  Finder target, {
  double scroll = 300,
}) async {
  if (target.evaluate().isEmpty) {
    await tester.scrollUntilVisible(
      target,
      scroll,
      scrollable: find.byType(Scrollable).first,
      maxScrolls: 60,
      duration: const Duration(milliseconds: 80),
    );
  }
  await tester.ensureVisible(target);
  await tester.pump(const Duration(milliseconds: 180));
}

Future<void> _tap(
  WidgetTester tester,
  Finder target, {
  double scroll = 300,
}) async {
  await _show(tester, target, scroll: scroll);
  await tester.tap(target);
  await tester.pump(const Duration(milliseconds: 250));
}

Future<void> _chooseGrade(WidgetTester tester, int grade) async {
  final field = find.byType(DropdownButtonFormField<int>).first;
  await _tap(tester, field, scroll: -300);
  final previous = tester.state<FormFieldState<int>>(field).value ?? 1;
  final choice = find.text('Lớp $grade').last;
  await tester.scrollUntilVisible(
    choice,
    grade >= previous ? 250 : -250,
    scrollable: find.byType(Scrollable).last,
    maxScrolls: 20,
  );
  await tester.ensureVisible(choice);
  await tester.tap(choice);
  await tester.pump(const Duration(milliseconds: 300));
}

Finder _field(String label) => find.byWidgetPredicate(
  (widget) => widget is TextField && widget.decoration?.labelText == label,
);

Finder _answer() => find.byType(TextFormField);

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets(
    'fresh native app studies, restores and grades from bundled content without a server',
    (tester) async {
      expect(Platform.isAndroid || Platform.isIOS, isTrue);
      const configured = String.fromEnvironment('API_BASE_URL');
      expect(
        configured.isEmpty ||
            (Uri.tryParse(configured)?.host.endsWith('.invalid') ?? false),
        isTrue,
        reason:
            'Run with API_BASE_URL=https://backend.invalid/api or no backend',
      );
      final preferences = await SharedPreferences.getInstance();
      final initialKeys = preferences.getKeys();
      expect(
        initialKeys,
        isEmpty,
        reason: 'Use a fresh emulator installation; do not clear learner data',
      );
      final guard = _RejectDartHttp();
      final previousOverride = HttpOverrides.current;
      HttpOverrides.global = guard;
      addTearDown(() async {
        await tester.pumpWidget(const SizedBox.shrink());
        HttpOverrides.global = previousOverride;
      });

      await app.main();
      await _until(
        tester,
        () => find.text('Học trên thiết bị').evaluate().isNotEmpty,
      );
      await _until(tester, () => _field('Tìm tên đề').evaluate().isNotEmpty);
      expect(
        find.text('Không thể tải dữ liệu. Kiểm tra kết nối rồi thử lại.'),
        findsNothing,
      );
      expect(find.text('Bản thử 2026.10.15.19'), findsOneWidget);

      // Exercise the real catalog selection for both ends of grades 1–12.
      await _chooseGrade(tester, 12);
      await _until(
        tester,
        () =>
            find.byType(DropdownButtonFormField<String>).evaluate().isNotEmpty,
      );
      await _tap(tester, find.byType(DropdownButtonFormField<String>).first);
      final physics = find.text('Vật lí').last;
      await tester.scrollUntilVisible(
        physics,
        220,
        scrollable: find.byType(Scrollable).last,
        maxScrolls: 20,
      );
      await tester.tap(physics);
      await tester.pump(const Duration(milliseconds: 250));
      await _until(
        tester,
        () => find.textContaining('câu ·').evaluate().isNotEmpty,
      );
      expect(find.text('Vật lí'), findsOneWidget);
      debugPrint(
        'Offline QA: native default and grade 12 subject catalog passed',
      );

      await _chooseGrade(tester, 1);
      await _show(tester, _field('Tìm tên đề'));
      await tester.enterText(_field('Tìm tên đề'), 'bài luyện tập gốc');
      await tester.testTextInput.receiveAction(TextInputAction.done);
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pump(const Duration(milliseconds: 300));
      const examTitle = 'Toán lớp 1 — bài luyện tập gốc';
      await _tap(tester, find.text(examTitle));
      await _until(tester, () => find.text('Câu 1/13').evaluate().isNotEmpty);
      await _tap(tester, find.widgetWithText(CheckboxListTile, '5'));
      await _tap(tester, find.widgetWithText(ActionChip, '3'));
      await _show(tester, _answer(), scroll: -300);
      expect(find.text('Số liền sau 7 là số nào?'), findsOneWidget);
      // Intentionally wrong: the real bundled question expects 8. This checks
      // both draft persistence and the displayed correction, without changing data.
      await tester.enterText(_answer(), '5');
      FocusManager.instance.primaryFocus?.unfocus();
      await _until(
        tester,
        () {
          final saved = preferences.getString('current_attempt.offline');
          if (saved == null) return false;
          return (jsonDecode(saved)['answers']['toan1_003'] as List?)?.single ==
              '5';
        },
        reason:
            'The actual platform preferences must persist the entered draft',
      );

      // Dispose the complete router/provider tree, reload platform storage, then
      // call the production entry point again. This is a widget-tree cold start,
      // not an assertion that the operating system process was force-stopped.
      await tester.pumpWidget(const SizedBox.shrink());
      await tester.pump(const Duration(milliseconds: 100));
      await preferences.reload();
      await app.main();
      await _until(
        tester,
        () => find.text('Tiếp tục bài đang làm').evaluate().isNotEmpty,
      );
      await _tap(tester, find.text('Tiếp tục bài đang làm'));
      await _until(tester, () => find.text('Câu 1/13').evaluate().isNotEmpty);
      await _tap(tester, find.widgetWithText(ActionChip, '3'));
      await _show(tester, _answer(), scroll: -300);
      final editable = tester.widget<EditableText>(
        find.descendant(of: _answer(), matching: find.byType(EditableText)),
      );
      expect(editable.controller.text, '5');
      debugPrint('Offline QA: real platform draft survived a fresh app tree');

      await _tap(tester, find.widgetWithText(FilledButton, 'Nộp bài'));
      await _until(tester, () => find.text('Nộp bài?').evaluate().isNotEmpty);
      await tester.tap(find.widgetWithText(FilledButton, 'Nộp bài').last);
      await _until(
        tester,
        () => find.text('Kết quả luyện tập').evaluate().isNotEmpty,
      );
      await preferences.reload();
      expect(preferences.getString('current_attempt.offline'), isNull);
      final history =
          jsonDecode(preferences.getString('history.offline')!) as List;
      expect(history, hasLength(1));
      final result = history.single['result'] as Map;
      expect(num.parse('${result['score']}'), 1);
      expect(num.parse('${result['max_score']}'), 13);
      final correction = (result['details'] as List).singleWhere(
        (row) => row['question_id'] == 'toan1_003',
      );
      expect(correction['submitted_answer'], ['5']);
      expect(num.parse('${correction['score']}'), 0);
      expect(correction['correct_answer'], ['8']);
      await _show(tester, find.text('Đếm tăng một đơn vị từ 7 được 8.'));
      expect(find.text('Bài làm: 5'), findsWidgets);
      expect(find.text('Đáp án: 8'), findsWidgets);
      debugPrint('Offline QA: explicit local submission and correction passed');

      await _tap(tester, find.text('Về trang luyện đề'), scroll: 550);
      await _tap(tester, find.widgetWithText(NavigationDestination, 'Tiến độ'));
      await _until(
        tester,
        () => find.text('Đã hoàn thành 1 bài luyện tập').evaluate().isNotEmpty,
      );
      // FilledButton.icon has a private runtime subclass; an exact byType
      // FilledButton finder would miss this real history button on every device.
      await _tap(tester, find.text('Lịch sử bài làm'));
      await _until(
        tester,
        () => find.byType(app.HistoryScreen).evaluate().isNotEmpty,
      );
      await _tap(tester, find.text(examTitle));
      await _until(
        tester,
        () => find.text('Kết quả đã lưu').evaluate().isNotEmpty,
      );
      debugPrint(
        'Offline QA: saved result opened from the real history screen',
      );
      // WidgetTester.pageBack() searches for the English tooltip "Back";
      // the real Vietnamese app uses a localized AppBar BackButton instead.
      await _tap(tester, find.byType(BackButton));
      final documentsTab = find.widgetWithText(
        NavigationDestination,
        'Tài liệu',
      );
      await _until(
        tester,
        () =>
            find.byType(app.HistoryScreen).evaluate().isNotEmpty &&
            documentsTab.hitTestable().evaluate().isNotEmpty,
        reason:
            'Wait for the saved-result route to pop before using navigation',
      );
      await _tap(tester, documentsTab);
      await _until(tester, () => _field('Tìm tài liệu').evaluate().isNotEmpty);
      await _chooseGrade(tester, 5);
      await _show(tester, _field('Tìm tài liệu'));
      await tester.enterText(_field('Tìm tài liệu'), 'Bài 27. Đường tròn');
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pump(const Duration(milliseconds: 300));
      const guideTitle = 'Bài 27. Đường tròn. Chu vi và diện tích hình tròn';
      await _tap(tester, find.text(guideTitle));
      await _until(
        tester,
        () => find.text('Tài liệu học tập').evaluate().isNotEmpty,
      );
      await _show(tester, find.text('Kiến thức và cách làm'));
      await _show(tester, find.text('Ví dụ từng bước'));
      await _tap(tester, find.text('Lời giải bài tập'));
      final fullSolution = find.byWidgetPredicate(
        (widget) =>
            widget is SelectableText &&
            (widget.data?.contains('Đáp số: 31,4 cm.') ?? false) &&
            (widget.data?.contains('4 : 2 = 2 (cm)') ?? false),
      );
      await _show(tester, fullSolution);
      expect(fullSolution, findsOneWidget);
      debugPrint(
        'Offline QA: bundled grade 5 guide and full worked solution passed',
      );
      expect(
        guard.clientsCreated,
        0,
        reason: 'No Dart HTTP transport is used by local study',
      );
    },
    timeout: const Timeout(Duration(minutes: 6)),
  );
}
