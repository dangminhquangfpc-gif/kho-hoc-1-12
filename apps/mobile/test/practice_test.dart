import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:kho_hoc_mobile/main.dart';
import 'package:kho_hoc_mobile/repository.dart';

class FakeApi extends LearningApi {
  @override
  Future<List<Json>> subjects(int grade) async => [
    {'id': 'toan', 'name': 'Toán'},
  ];
  @override
  Future<List<Json>> exams(int grade, String subject, String search) async => [
    {
      'id': 'exam',
      'title': 'Đề kiểm thử',
      'question_count': 1,
      'duration_minutes': 30,
    },
  ];
  @override
  Future<Json> start(String id) async => {
    'id': 'attempt',
    'token': 'test-capability',
    'created_at': DateTime.now().toUtc().toIso8601String(),
    'exam': {'title': 'Đề kiểm thử', 'duration_minutes': 30},
    'questions': [
      {
        'id': 'q1',
        'question': '3 + 2 bằng bao nhiêu?',
        'type': 'single_choice',
        'options': [
          {'id': 'A', 'text': '5'},
          {'id': 'B', 'text': '6'},
        ],
      },
    ],
    'answers': <String, List<String>>{},
  };
  @override
  Future<Json> submit(Json session) async {
    if ((session['answers']['q1'] as List).single != 'A') {
      throw StateError('Wrong submitted payload');
    }
    return {
      'attempt_id': 'attempt',
      'title': 'Đề kiểm thử',
      'score': 1,
      'max_score': 1,
      'details': [
        {
          'question_id': 'q1',
          'score': 1,
          'max_score': 1,
          'correct_answer': ['A'],
          'explanation': '3 + 2 = 5.',
        },
      ],
    };
  }
}

void main() {
  testWidgets(
    'Choose grade/subject/exam, answer, submit, view stored history',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(FakeApi())],
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Lớp học'), findsOneWidget);
      expect(find.text('Môn học'), findsOneWidget);
      await tester.tap(find.text('Đề kiểm thử'));
      await tester.pumpAndSettle();
      expect(find.text('3 + 2 bằng bao nhiêu?'), findsOneWidget);
      expect(find.textContaining('Đáp án:'), findsNothing);
      await tester.tap(find.text('5'));
      await tester.pumpAndSettle();
      final prefs = await SharedPreferences.getInstance();
      expect(LocalStore(prefs).current!['answers']['q1'], ['A']);
      await tester.tap(find.text('Nộp bài'));
      await tester.pumpAndSettle();
      await tester.tap(
        find.descendant(
          of: find.byType(AlertDialog),
          matching: find.widgetWithText(FilledButton, 'Nộp bài'),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('1 / 1'), findsOneWidget);
      expect(find.text('3 + 2 = 5.'), findsOneWidget);
      expect(LocalStore(prefs).history.length, 1);
      expect(LocalStore(prefs).current, isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

  test(
    'LocalStore restores answers after reopening and completes idempotently',
    () async {
      SharedPreferences.setMockInitialValues({});
      final prefs = await SharedPreferences.getInstance();
      final session = await FakeApi().start('exam');
      session['answers'] = {
        'q1': ['A'],
      };
      await LocalStore(prefs).save(session);
      expect(LocalStore(prefs).current!['answers'], {
        'q1': ['A'],
      });
      final result = await FakeApi().submit(session);
      await LocalStore(prefs).complete(session, result);
      await LocalStore(prefs).complete(session, result);
      expect(LocalStore(prefs).history.length, 1);
    },
  );
}
