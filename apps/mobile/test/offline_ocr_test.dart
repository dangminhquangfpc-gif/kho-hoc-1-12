import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/ai_ocr_screen.dart';
import 'package:kho_hoc_mobile/main.dart';
import 'package:kho_hoc_mobile/ocr_runtime.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'ai_ocr_test.dart' show TestOcr, TutorApi;

class OfflineTutorApi extends TutorApi {
  int subjectCalls = 0;

  @override
  Future<List<Json>> subjects(int grade) async {
    subjectCalls++;
    throw StateError('Backend unavailable');
  }
}

void main() {
  Finder checkedCopyButton() => find
      .ancestor(
        of: find.text('Sao chép văn bản đã kiểm tra'),
        matching: find.byWidgetPredicate((widget) => widget is FilledButton),
      )
      .first;

  Future<void> wide(WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1000, 1800));
    addTearDown(() => tester.binding.setSurfaceSize(null));
  }

  testWidgets(
    'Failed account bootstrap still allows OCR copy without changing account data',
    (tester) async {
      await wide(tester);
      const account = 'offline-student';
      SharedPreferences.setMockInitialValues({
        'active_account_id': account,
        'backend_url': 'https://offline.example.test/api',
        'current_attempt.$account': jsonEncode({
          'id': 'unfinished',
          'account_id': account,
          'answers': {
            'question': ['Câu trả lời đã lưu'],
          },
        }),
        'history.$account': jsonEncode([
          {
            'id': 'completed',
            'result': {'score': 2},
          },
        ]),
      });
      final prefs = await SharedPreferences.getInstance();
      final original = {for (final key in prefs.getKeys()) key: prefs.get(key)};
      final api = OfflineTutorApi()..expectedAccountId = account;
      final user = {'id': account, 'role': 'student', 'grade': 5};
      var bootstrapCalls = 0;
      final container = ProviderContainer(
        overrides: [
          apiProvider.overrideWithValue(api),
          authUserProvider.overrideWith((ref) => user),
          authBootstrapProvider.overrideWith((ref) async {
            bootstrapCalls++;
            throw StateError('Backend unavailable');
          }),
        ],
      );
      addTearDown(container.dispose);
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

      await tester.pumpWidget(
        UncontrolledProviderScope(
          container: container,
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      expect(bootstrapCalls, 1);
      expect(
        find.textContaining('Chưa xác thực được tài khoản'),
        findsOneWidget,
      );
      await tester.tap(find.text('Nhận chữ từ ảnh trên thiết bị'));
      await tester.pumpAndSettle();
      expect(find.text('Nhận chữ trên thiết bị'), findsOneWidget);
      final ocrContext = tester.element(find.byType(AiOcrScreen));
      expect(Localizations.localeOf(ocrContext), const Locale('vi'));
      expect(Theme.of(ocrContext).textTheme.bodyMedium!.fontFamily, 'NotoSans');
      expect(find.text('Trợ lý học tập AI'), findsNothing);
      expect(find.text('Đăng nhập để dùng AI'), findsNothing);
      expect(find.text('Kiểm tra lại trạng thái AI'), findsNothing);
      expect(find.text('Dùng văn bản này cho câu trả lời'), findsNothing);
      await tester.enterText(find.byKey(const Key('ocr-edited-text')), '5');
      await tester.pump();
      final copyButton = checkedCopyButton();
      expect(tester.widget<FilledButton>(copyButton).onPressed, isNull);
      await tester.tap(find.text('Tôi đã kiểm tra văn bản'));
      await tester.pump();
      await tester.tap(copyButton);
      await tester.pumpAndSettle();
      expect(copied, '5');
      expect(find.text('Đã sao chép văn bản.'), findsOneWidget);
      expect(api.statusCalls, 0);
      expect(api.subjectCalls, 0);
      expect(api.requests, isEmpty);
      expect(container.read(authUserProvider), user);
      expect(api.expectedAccountId, account);
      expect({
        for (final key in prefs.getKeys()) key: prefs.get(key),
      }, original);
      expect(LocalStore(prefs).current!['id'], 'unfinished');
      expect(LocalStore(prefs).history.single['id'], 'completed');
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Thử lại'));
      await tester.pumpAndSettle();
      expect(bootstrapCalls, 2);
      expect({
        for (final key in prefs.getKeys()) key: prefs.get(key),
      }, original);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'OCR-only mode recognizes and edits without loading any AI data',
    (tester) async {
      await wide(tester);
      final api = OfflineTutorApi();
      final recognizer = TestOcr(
        () async => const OcrResult(text: '12 + 5', confidence: null),
      );
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            apiProvider.overrideWithValue(api),
            authUserProvider.overrideWith(
              (ref) => {'id': 'cached-student', 'grade': 5},
            ),
          ],
          child: MaterialApp(
            home: AiOcrScreen(ocrOnly: true, recognizer: recognizer),
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Chọn ảnh để nhận chữ'));
      await tester.pumpAndSettle();
      final editor = find.byKey(const Key('ocr-edited-text'));
      expect(tester.widget<TextField>(editor).controller!.text, '12 + 5');
      await tester.tap(find.text('Tôi đã kiểm tra văn bản'));
      await tester.pump();
      await tester.enterText(editor, '12 + 5 = 17');
      await tester.pump();
      expect(
        tester.widget<FilledButton>(checkedCopyButton()).onPressed,
        isNull,
      );
      expect(api.statusCalls, 0);
      expect(api.subjectCalls, 0);
      expect(api.requests, isEmpty);
      expect(find.text('Trợ lý học tập AI'), findsNothing);
    },
  );
}
