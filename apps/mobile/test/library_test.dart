import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:kho_hoc_mobile/main.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'practice_test.dart' show FakeApi;

class LibraryApi extends FakeApi {
  @override
  Future<List<Json>> documents(Map<String, dynamic> filter) async => [
    {
      'id': 'notes',
      'title': 'Ghi chú cộng số',
      'summary': 'Nội dung tự biên soạn',
    },
  ];
  @override
  Future<Json> document(String id) async => {
    'id': id,
    'title': 'Ghi chú cộng số',
    'grade': 1,
    'subject': 'toan',
    'topic': 'Cộng',
    'author': 'Kho Học',
    'source_name': 'Tự biên soạn',
    'license': 'CC0',
    'updated_at': '2026-10-14',
    'sections': [
      {'heading': 'Ví dụ', 'text': '3 + 2 = 5.'},
    ],
    'can_view_pdf': false,
    'can_download': false,
  };
}

class PracticeLessonApi extends LibraryApi {
  @override
  Future<Json> curriculum(int grade, String subject) async => {
    'unit_count': 1,
    'authored_count': 1,
    'units': [],
  };
  @override
  Future<Json> document(String id) async => {
    ...await super.document(id),
    'sections': [
      {'heading': 'Bài tập tự luyện', 'text': 'Tính 4 + 3.'},
      {'heading': 'Lời giải bài tập', 'text': '4 + 3 = 7.'},
    ],
  };
}

void main() {
  testWidgets('Practice solution is concealed until the learner expands it', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(
      ProviderScope(
        overrides: [apiProvider.overrideWithValue(PracticeLessonApi())],
        child: const KhoHocApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Tài liệu'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('Ghi chú cộng số'),
      150,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.drag(find.byType(Scrollable).first, const Offset(0, -150));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Ghi chú cộng số'));
    await tester.pumpAndSettle();
    expect(find.text('Tính 4 + 3.'), findsOneWidget);
    expect(find.text('4 + 3 = 7.'), findsNothing);
    await tester.tap(find.text('Lời giải bài tập'));
    await tester.pumpAndSettle();
    expect(find.text('4 + 3 = 7.'), findsOneWidget);
    await tester.pumpWidget(const SizedBox.shrink());
  });

  testWidgets(
    'Library opens notes and retains favorites/recent after returning',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(LibraryApi())],
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tài liệu'));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.byTooltip('Lưu tài liệu yêu thích'),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Lưu tài liệu yêu thích'));
      await tester.pumpAndSettle();
      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getStringList('favorite_documents'), ['notes']);
      await tester.tap(find.text('Ghi chú cộng số'));
      await tester.pumpAndSettle();
      expect(find.text('3 + 2 = 5.'), findsOneWidget);
      expect(prefs.getStringList('recent_documents'), ['notes']);
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      expect(find.byTooltip('Bỏ yêu thích'), findsOneWidget);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
}
