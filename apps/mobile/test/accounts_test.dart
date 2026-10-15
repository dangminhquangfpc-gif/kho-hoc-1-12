import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:kho_hoc_mobile/main.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'practice_test.dart' show FakeApi;

class SchoolApi extends FakeApi {
  Json? user;
  List<Json>? created;
  @override
  Future<Json?> currentUser() async => user;
  @override
  Future<Json> authenticate(
    String username,
    String password, {
    String? displayName,
    int? grade,
    String role = 'student',
  }) async {
    user = {
      'id': 'student-id',
      'username': username,
      'display_name': displayName ?? 'Học viên',
      'role': role,
      'must_change_password': false,
    };
    return user!;
  }

  @override
  Future<List<Json>> pendingAttempts() async => [];
  @override
  Future<List<Json>> accountResults() async => [];
  @override
  Future<List<Json>> classroomStudents() async => [];
  @override
  Future<List<Json>> classroomGroups() async => [];
  @override
  Future<List<Json>> createStudents(List<Json> students) async {
    created = students;
    return [
      for (final s in students)
        {...s, 'temporary_password': 'Synthetic-test-password'},
    ];
  }
}

class CloudSchoolApi extends SchoolApi {
  CloudSchoolApi() {
    user = {
      'id': 'cloud-student',
      'username': 'learner',
      'display_name': 'Học viên đồng bộ',
      'role': 'student',
      'must_change_password': false,
    };
  }
  bool conflict = false;
  Json? saved;
  @override
  Future<List<Json>> pendingAttempts() async => [
    {'id': 'remote', 'title': 'Bài trên thiết bị khác'},
  ];
  @override
  Future<Json> resumeAttempt(String id) async => {
    ...await super.start('exam'),
    'id': id,
    'account_id': 'cloud-student',
    'answers': {
      'q1': ['B'],
    },
    'draft_revision': 4,
  };
  @override
  Future<int> saveDraft(Json session) async {
    if (conflict) {
      throw DioException(
        requestOptions: RequestOptions(path: '/draft'),
        response: Response(
          statusCode: 409,
          requestOptions: RequestOptions(path: '/draft'),
        ),
      );
    }
    saved = session;
    return (session['draft_revision'] as int) + 1;
  }
}

void main() {
  test(
    'Device history and drafts are isolated between guest and accounts',
    () async {
      SharedPreferences.setMockInitialValues({});
      final p = await SharedPreferences.getInstance();
      final store = LocalStore(p);
      await store.save({'id': 'guest', 'answers': {}});
      await p.setString('active_account_id', 'alice');
      expect(store.current, isNull);
      await store.save({'id': 'a', 'account_id': 'alice', 'answers': {}});
      await store.complete({'id': 'a', 'account_id': 'alice'}, {'score': 1});
      await p.setString('active_account_id', 'bob');
      expect(store.history, isEmpty);
      expect(store.current, isNull);
      await expectLater(
        store.save({'id': 'wrong', 'account_id': 'alice'}),
        throwsStateError,
      );
      await p.remove('active_account_id');
      expect(store.current!['id'], 'guest');
      await p.setString('active_account_id', 'alice');
      expect(store.history.single['id'], 'a');
    },
  );
  testWidgets(
    'Student registration sets account namespace without exposing manager controls',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final api = SchoolApi();
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(api)],
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Cá nhân').last);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Đăng nhập hoặc đăng ký'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Chưa có tài khoản? Đăng ký'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.widgetWithText(TextField, 'Tên đăng nhập'),
        'learner01',
      );
      await tester.enterText(
        find.widgetWithText(TextField, 'Mật khẩu'),
        'Student-password-123',
      );
      await tester.enterText(
        find.widgetWithText(TextField, 'Tên hiển thị'),
        'Học viên thử',
      );
      await tester.ensureVisible(find.widgetWithText(FilledButton, 'Đăng ký'));
      await tester.drag(find.byType(ListView).first, const Offset(0, -140));
      await tester.pumpAndSettle();
      await tester.tap(find.widgetWithText(FilledButton, 'Đăng ký'));
      await tester.pumpAndSettle();
      expect(find.text('Học viên thử'), findsOneWidget);
      expect(find.text('Quản lý học viên và kết quả'), findsNothing);
      final p = await SharedPreferences.getInstance();
      expect(p.getString('active_account_id'), 'student-id');
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
  testWidgets(
    'Manager can create a batch and receive individual temporary passwords',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final api = SchoolApi()
        ..user = {
          'id': 'manager-id',
          'username': 'quanly',
          'display_name': 'Quản lý',
          'role': 'manager',
          'must_change_password': false,
        };
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(api)],
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Cá nhân').last);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tài khoản: Quản lý'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Quản lý học viên và kết quả'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tạo hàng loạt tài khoản'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.widgetWithText(TextField, 'Danh sách học viên'),
        'hv001 ; Bạn Một ; 5\nhv002 ; Bạn Hai ; 6',
      );
      await tester.tap(find.widgetWithText(FilledButton, 'Tạo tài khoản'));
      await tester.pumpAndSettle();
      expect(api.created!.length, 2);
      expect(api.created![1]['grade'], 6);
      expect(find.text('Tài khoản vừa cấp'), findsOneWidget);
      await tester.tap(find.text('Đã lưu'));
      await tester.pumpAndSettle();
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
  testWidgets(
    'Resume cloud draft, sync answer, and preserve local answer on conflict',
    (tester) async {
      SharedPreferences.setMockInitialValues({});
      final api = CloudSchoolApi();
      await tester.pumpWidget(
        ProviderScope(
          overrides: [apiProvider.overrideWithValue(api)],
          child: const KhoHocApp(),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Cá nhân').last);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Tài khoản: Học viên đồng bộ'));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Bài trên thiết bị khác'));
      await tester.tap(find.text('Bài trên thiết bị khác'));
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<CheckboxListTile>(
              find.widgetWithText(CheckboxListTile, '6'),
            )
            .value,
        isTrue,
      );
      await tester.tap(find.widgetWithText(CheckboxListTile, '5'));
      await tester.pumpAndSettle();
      await tester.pump(const Duration(seconds: 1));
      await tester.pumpAndSettle();
      expect(api.saved!['answers']['q1'], ['A']);
      final prefs = await SharedPreferences.getInstance();
      expect(LocalStore(prefs).current!['draft_revision'], 5);
      expect(find.text('Đã đồng bộ bài làm lên máy chủ.'), findsOneWidget);
      api.conflict = true;
      await tester.tap(find.widgetWithText(CheckboxListTile, '6'));
      await tester.pumpAndSettle();
      await tester.pump(const Duration(seconds: 1));
      await tester.pumpAndSettle();
      expect(
        find.textContaining('Bài đã thay đổi hoặc đã nộp trên thiết bị khác'),
        findsOneWidget,
      );
      expect(LocalStore(prefs).current!['answers']['q1'], ['B']);
      expect(api.saved!['answers']['q1'], ['A']);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
}
