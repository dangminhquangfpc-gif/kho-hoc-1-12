import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:kho_hoc_mobile/create_practice_screen.dart';
import 'package:kho_hoc_mobile/main.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'practice_test.dart' show FakeApi;

class CustomApi extends FakeApi {
  Json? requested;
  @override
  Future<Json> start(String id) async {
    final value = await super.start(id);
    value['questions'] = <Json>[
      {
        ...Map<String, dynamic>.from(value['questions'][0] as Map),
        'grade': 1,
        'subject': 'toan',
        'topic': 'cong',
        'topic_name': 'Phép cộng',
      },
    ];
    return value;
  }

  @override
  Future<Json> practiceOptions(int grade, String subject) async => {
    'total': 6,
    'topics': [
      {'id': 'cong', 'name': 'Phép cộng', 'count': 6},
    ],
    'groups': [
      {
        'topic': 'cong',
        'difficulty': 'easy',
        'textbook': 'ket_noi_tri_thuc',
        'count': 6,
      },
    ],
  };
  @override
  Future<Json> createPractice(Json filter) async {
    requested = filter;
    return {...await start('exam'), 'practice_filter': filter};
  }
}

class MultiTopicApi extends CustomApi {
  @override
  Future<Json> practiceOptions(int grade, String subject) async => {
    'total': 40,
    'topics': [
      {'id': 'cong', 'name': 'Phép cộng', 'count': 20},
      {'id': 'tru', 'name': 'Phép trừ', 'count': 20},
    ],
    'groups': [
      for (final t in ['cong', 'tru'])
        {
          'topic': t,
          'difficulty': 'easy',
          'textbook': 'ket_noi_tri_thuc',
          'count': 20,
        },
    ],
  };
}

void main() {
  testWidgets('Select two topics and send both in one practice request', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final api = MultiTopicApi();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [apiProvider.overrideWithValue(api)],
        child: const KhoHocApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Luyện đề').last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Tạo đề theo chủ đề và độ khó'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Chọn chủ đề'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Phép cộng (20 câu)'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Phép trừ (20 câu)'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Áp dụng'));
    await tester.pumpAndSettle();
    expect(find.text('Chủ đề (đã chọn 2)'), findsOneWidget);
    await tester.ensureVisible(find.text('Bắt đầu đề 10 câu'));
    await tester.drag(find.byType(ListView).first, const Offset(0, -140));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Bắt đầu đề 10 câu'));
    await tester.pumpAndSettle();
    expect(api.requested!['topics'], containsAll(['cong', 'tru']));
    expect(api.requested!.containsKey('topic'), false);
    await tester.pumpWidget(const SizedBox.shrink());
  });

  testWidgets(
    'Custom practice caps requested size to the actual matching bank',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final api = CustomApi();
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(api)],
          child: const MaterialApp(home: CreatePracticeScreen()),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Có 6 câu phù hợp với bộ lọc.'), findsOneWidget);
      expect(find.text('Bắt đầu đề 6 câu'), findsOneWidget);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
  test(
    'Recovery of custom practice reuses saved question IDs rather than drawing another set',
    () async {
      final api = CustomApi();
      final previous = {
        ...await api.start('exam'),
        'practice_filter': {'grade': 1, 'subject': 'toan', 'count': 1},
        'answers': {
          'q1': ['A'],
        },
      };
      final next = await api.recover(previous);
      expect(api.requested!['question_ids'], ['q1']);
      expect(next['answers']['q1'], ['A']);
    },
  );
  testWidgets(
    'Review latest wrong answer and update topic progress after correction',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final api = CustomApi();
      final p = await SharedPreferences.getInstance();
      final old = await api.start('exam');
      old['backend_url'] = api.baseUrl;
      old['answers'] = {
        'q1': ['B'],
      };
      await LocalStore(p).complete(old, {
        'title': 'Đề kiểm thử',
        'score': 0,
        'max_score': 1,
        'details': [
          {'question_id': 'q1', 'score': 0, 'max_score': 1},
        ],
      });
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(api)],
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tiến độ').last);
      await tester.pumpAndSettle();
      expect(find.text('0% điểm · 0/1 câu đúng hoàn toàn'), findsOneWidget);
      await tester.tap(find.text('Ôn 1 câu chưa đúng'));
      await tester.pumpAndSettle();
      expect(api.requested!['question_ids'], ['q1']);
      await tester.tap(find.text('5'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Nộp bài'));
      await tester.pumpAndSettle();
      await tester.tap(
        find.descendant(
          of: find.byType(AlertDialog),
          matching: find.widgetWithText(FilledButton, 'Nộp bài'),
        ),
      );
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Về trang luyện đề'));
      await tester.tap(find.text('Về trang luyện đề'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tiến độ').last);
      await tester.pumpAndSettle();
      expect(find.text('100% điểm · 1/1 câu đúng hoàn toàn'), findsOneWidget);
      expect(find.text('Ôn 1 câu chưa đúng'), findsNothing);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

  testWidgets('Create practice button opens a real saved attempt', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final api = CustomApi();
    await tester.pumpWidget(
      ProviderScope(
        overrides: [apiProvider.overrideWithValue(api)],
        child: const KhoHocApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Luyện đề').last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Tạo đề theo chủ đề và độ khó'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Bắt đầu đề 6 câu'));
    await tester.drag(find.byType(ListView).first, const Offset(0, -160));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Bắt đầu đề 6 câu'));
    await tester.pumpAndSettle();
    expect(api.requested!['count'], 6);
    expect(find.text('3 + 2 bằng bao nhiêu?'), findsOneWidget);
    final p = await SharedPreferences.getInstance();
    expect(LocalStore(p).current!['practice_filter']['count'], 6);
    await tester.pumpWidget(const SizedBox.shrink());
  });
}
