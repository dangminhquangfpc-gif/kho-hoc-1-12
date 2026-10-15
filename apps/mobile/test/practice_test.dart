import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:kho_hoc_mobile/main.dart';
import 'package:kho_hoc_mobile/repository.dart';

class FakeApi extends LearningApi {
  @override
  Future<Json?> currentUser() async => null;
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
    'exam': {'id': 'exam', 'title': 'Đề kiểm thử', 'duration_minutes': 30},
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
      'attempt_id': session['id'] ?? 'attempt',
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

class MissingAttemptApi extends FakeApi {
  @override
  Future<Json> start(String id) async => {
    ...await super.start(id),
    'id': 'recovered',
  };

  @override
  Future<Json> submit(Json session) async {
    if (session['id'] == 'missing') {
      throw DioException(
        requestOptions: RequestOptions(path: '/attempts/missing/submit'),
        response: Response(
          statusCode: 404,
          requestOptions: RequestOptions(path: '/attempts/missing/submit'),
        ),
        type: DioExceptionType.badResponse,
      );
    }
    return super.submit(session);
  }
}

class SubmittedApi extends FakeApi {
  @override
  Future<Json> submit(Json session) async => throw DioException(
    requestOptions: RequestOptions(path: '/submit'),
    response: Response(
      statusCode: 409,
      requestOptions: RequestOptions(path: '/submit'),
    ),
    type: DioExceptionType.badResponse,
  );
  @override
  Future<Json> attemptResult(Json session) async {
    final result = await super.submit({
      'answers': {
        'q1': ['A'],
      },
    });
    result['details'][0]['submitted_answer'] = ['A'];
    return result;
  }
}

class LoginRequiredApi extends FakeApi {
  @override
  Future<Json> start(String id) async => throw DioException(
    requestOptions: RequestOptions(path: '/exams/$id/attempts'),
    response: Response(
      statusCode: 401,
      requestOptions: RequestOptions(path: '/exams/$id/attempts'),
    ),
  );
}

void main() {
  testWidgets(
    'Previously submitted result clears stale draft without changing server score',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final p = await SharedPreferences.getInstance();
      final old = await FakeApi().start('exam');
      old['answers'] = {
        'q1': ['B'],
      };
      await LocalStore(p).save(old);
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(SubmittedApi())],
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tiếp tục bài đang làm'));
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
      expect(find.text('1 / 1'), findsOneWidget);
      expect(LocalStore(p).current, isNull);
      expect(LocalStore(p).history.single['answers']['q1'], ['A']);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

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
      await tester.scrollUntilVisible(
        find.text('Đề kiểm thử'),
        180,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.drag(find.byType(ListView).first, const Offset(0, -120));
      await tester.pumpAndSettle();
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

  testWidgets('Missing saved attempt recovers answers and can be submitted', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    final old = {
      ...await FakeApi().start('exam'),
      'id': 'missing',
      'answers': {
        'q1': ['A'],
      },
    };
    await LocalStore(prefs).save(old);
    await tester.pumpWidget(
      ProviderScope(
        overrides: [apiProvider.overrideWithValue(MissingAttemptApi())],
        child: const KhoHocApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Tiếp tục bài đang làm'));
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
    expect(LocalStore(prefs).current!['answers']['q1'], ['A']);
    await tester.tap(find.text('Khôi phục bài đã lưu'));
    await tester.pumpAndSettle();
    await tester.tap(find.widgetWithText(FilledButton, 'Khôi phục'));
    await tester.pumpAndSettle();
    expect(LocalStore(prefs).current!['id'], 'recovered');
    expect(LocalStore(prefs).current!['answers']['q1'], ['A']);
    expect(find.textContaining('Đã khôi phục 1 câu trả lời'), findsOneWidget);
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
    expect(LocalStore(prefs).current, isNull);
    await tester.pumpWidget(const SizedBox.shrink());
  });

  test(
    'Recovery discards answers for changed questions despite matching ID',
    () async {
      final api = FakeApi();
      final previous = await api.start('exam');
      previous['answers'] = {
        'q1': ['A'],
      };
      (previous['questions'][0] as Json)['question'] =
          'Câu hỏi của phiên bản cũ';
      final restored = await api.recover(previous);
      expect(restored['answers'], isEmpty);
      expect(previous['answers']['q1'], ['A']);
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
  testWidgets('Shared server requiring login opens the account screen', (
    tester,
  ) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(
      ProviderScope(
        overrides: [apiProvider.overrideWithValue(LoginRequiredApi())],
        child: const KhoHocApp(),
      ),
    );
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('Đề kiểm thử'),
      180,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.drag(find.byType(ListView).first, const Offset(0, -120));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Đề kiểm thử'));
    await tester.pumpAndSettle();
    expect(find.widgetWithText(TextField, 'Tên đăng nhập'), findsOneWidget);
    expect(
      find.text('Không thể bắt đầu bài. Kiểm tra mạng và bộ nhớ thiết bị.'),
      findsNothing,
    );
    await tester.pumpWidget(const SizedBox.shrink());
  });
}
