import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:kho_hoc_mobile/account_screen.dart';
import 'package:kho_hoc_mobile/assignments_screen.dart';
import 'package:kho_hoc_mobile/repository.dart';

Json assignment({String id = 'assigned', String status = 'not_started'}) => {
  'exam_id': id,
  'title': 'Đề luyện phân số',
  'grade': 5,
  'subject': 'toan',
  'duration_minutes': 30,
  'group_id': 'group',
  'group_name': 'Nhóm Toán',
  'member_count': 3,
  'submitted_count': 1,
  'in_progress_count': 1,
  'not_started_count': 1,
  'status': status,
  'attempts_count': 2,
  'latest_percent': null,
  'latest_submitted_at': null,
};

class AssignmentApi extends LearningApi {
  final offsets = <int>[];
  List<Json> studentRows = [assignment(status: 'submitted')];
  List<Json> cloud = [];
  Json? assigned;
  String? resumed;
  int starts = 0, groupLoads = 0, exports = 0;
  bool failStudent = false;
  final searches = <String>[];

  @override
  Future<List<Json>> accountAssignments({int offset = 0}) async {
    offsets.add(offset);
    if (failStudent) throw StateError('Máy chủ tạm thời bận.');
    return studentRows.skip(offset).take(30).toList();
  }

  @override
  Future<List<Json>> groupAssignments(String id, {int offset = 0}) async {
    groupLoads++;
    return [assignment()];
  }

  @override
  Future<Json> groupAssignmentProgress(String groupId, String examId) async => {
    ...assignment(),
    'students': [
      {
        'id': 'a',
        'username': 'an',
        'display_name': 'Bạn An',
        'grade': 5,
        'status': 'submitted',
        'attempts_count': 2,
        'latest_percent': null,
        'latest_submitted_at': '2026-10-15T05:00:00Z',
      },
      {
        'id': 'b',
        'username': 'binh',
        'display_name': 'Bạn Bình',
        'grade': 5,
        'status': 'in_progress',
        'attempts_count': 1,
        'latest_percent': null,
        'latest_submitted_at': null,
      },
      {
        'id': 'c',
        'username': 'chi',
        'display_name': 'Bạn Chi',
        'grade': 5,
        'status': 'not_started',
        'attempts_count': 0,
        'latest_percent': null,
        'latest_submitted_at': null,
      },
    ],
  };

  @override
  Future<String> groupAssignmentCsv(String groupId, String examId) async {
    exports++;
    return 'Tên học viên,Kết quả\nBạn An,\n';
  }

  @override
  Future<List<Json>> subjects(int grade) async => [
    {'id': 'toan', 'name': 'Toán'},
  ];

  @override
  Future<List<Json>> exams(int grade, String subject, String search) async {
    searches.add('$grade/$subject/$search');
    return [
      {
        'id': 'source',
        'title': 'Đề có sẵn phù hợp',
        'question_count': 20,
        'duration_minutes': 40,
      },
    ];
  }

  @override
  Future<Json> assignGroupExam(String groupId, String examId) async {
    assigned = {'group_id': groupId, 'exam_id': examId};
    return assignment();
  }

  @override
  Future<List<Json>> pendingAttempts() async => cloud;

  @override
  Future<Json> resumeAttempt(String id) async {
    resumed = id;
    return draft('assigned', id: id);
  }

  @override
  Future<Json> start(String id) async {
    starts++;
    return draft(id);
  }

  @override
  Future<List<Json>> classroomGroups() async => [
    {
      'id': 'group',
      'name': 'Nhóm Toán',
      'join_code': 'synthetic-code',
      'student_ids': <String>[],
    },
  ];

  @override
  Future<List<Json>> classroomStudents() async => [];
  @override
  Future<List<Json>> accountResults() async => [];
}

Json draft(String exam, {String id = 'draft'}) => {
  'id': id,
  'account_id': 'viewer',
  'token': '',
  'created_at': DateTime.now().toUtc().toIso8601String(),
  'exam': {'id': exam, 'title': 'Bài luyện đang làm', 'duration_minutes': 30},
  'questions': <Json>[],
  'answers': {
    'question': ['B'],
  },
  'draft_revision': 3,
};

Future<void> showAssignments(
  WidgetTester tester,
  AssignmentApi api, {
  bool teacher = false,
  Widget? screen,
  bool group = false,
}) async {
  final user = {
    'id': 'viewer',
    'role': teacher ? 'teacher' : 'student',
    'display_name': 'Người thử',
    'username': 'viewer',
    'must_change_password': false,
  };
  final router = GoRouter(
    routes: [
      GoRoute(
        path: '/',
        builder: (_, _) =>
            screen ??
            AssignmentsScreen(
              groupId: group ? 'group' : null,
              groupName: 'Nhóm Toán',
            ),
      ),
      GoRoute(
        path: '/practice',
        builder: (_, _) => const Scaffold(body: Text('Màn hình bài đang làm')),
      ),
    ],
  );
  addTearDown(router.dispose);
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        apiProvider.overrideWithValue(api),
        authUserProvider.overrideWith((ref) => user),
      ],
      child: MaterialApp.router(routerConfig: router),
    ),
  );
  await tester.pumpAndSettle();
}

void main() {
  setUp(
    () =>
        SharedPreferences.setMockInitialValues({'active_account_id': 'viewer'}),
  );

  testWidgets(
    'Student sees only own assignments and pending manual result without teacher controls',
    (tester) async {
      final api = AssignmentApi();
      await showAssignments(tester, api);
      expect(
        find.textContaining('Đã nộp · 2 lần nộp · Chờ xem xét'),
        findsOneWidget,
      );
      expect(find.text('Giao đề có sẵn'), findsNothing);
      expect(find.text('Sao chép bảng điểm CSV'), findsNothing);
      expect(api.groupLoads, 0);
      expect(api.offsets, [0]);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

  testWidgets('Student direct access to group progress does not fetch peers', (
    tester,
  ) async {
    final api = AssignmentApi();
    await showAssignments(tester, api, group: true);
    expect(find.text('Bạn cần đăng nhập với vai trò phù hợp.'), findsOneWidget);
    expect(find.text('Giao đề có sẵn'), findsNothing);
    expect(api.groupLoads, 0);
    expect(api.offsets, isEmpty);
    await tester.pumpWidget(const SizedBox.shrink());
  });

  testWidgets(
    'Teacher filters progress and exports actual CSV without guessing a zero score',
    (tester) async {
      final api = AssignmentApi();
      String? copied;
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        SystemChannels.platform,
        (call) async {
          if (call.method == 'Clipboard.setData') {
            copied = call.arguments['text'];
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
      await showAssignments(tester, api, teacher: true, group: true);
      await tester.tap(find.text('Đề luyện phân số'));
      await tester.pumpAndSettle();
      expect(find.text('Tiến độ bài được giao'), findsOneWidget);
      expect(find.textContaining('Chờ xem xét ·'), findsOneWidget);
      await tester.tap(find.text('Đã nộp (1)'));
      await tester.pumpAndSettle();
      expect(find.text('Bạn An (an)'), findsOneWidget);
      expect(find.text('Bạn Bình (binh)'), findsNothing);
      await tester.tap(find.text('Sao chép bảng điểm CSV'));
      await tester.pumpAndSettle();
      expect(api.exports, 1);
      expect(copied, 'Tên học viên,Kết quả\nBạn An,\n');
      expect(find.textContaining('Đã xuất tiến độ'), findsOneWidget);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

  testWidgets(
    'Teacher searches and assigns an existing exam then list reloads',
    (tester) async {
      final api = AssignmentApi();
      await showAssignments(tester, api, teacher: true, group: true);
      await tester.tap(find.text('Giao đề có sẵn'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.widgetWithText(TextField, 'Tìm tên đề'),
        'phân số',
      );
      await tester.tap(find.byTooltip('Tìm đề'));
      await tester.pumpAndSettle();
      expect(api.searches.last, '5/toan/phân số');
      await tester.tap(find.text('Đề có sẵn phù hợp'));
      await tester.pumpAndSettle();
      await tester.tap(find.widgetWithText(FilledButton, 'Giao đề'));
      await tester.pumpAndSettle();
      expect(api.assigned, {'group_id': 'group', 'exam_id': 'source'});
      expect(api.groupLoads, 2);
      expect(find.text('Bài giao và tiến độ'), findsOneWidget);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

  testWidgets('Student resumes matching cloud draft with saved answers', (
    tester,
  ) async {
    final api = AssignmentApi()
      ..cloud = [
        {'id': 'remote', 'exam_id': 'assigned'},
      ];
    await showAssignments(tester, api);
    await tester.tap(find.text('Đề luyện phân số'));
    await tester.pumpAndSettle();
    expect(api.resumed, 'remote');
    expect(api.starts, 0);
    expect(find.text('Màn hình bài đang làm'), findsOneWidget);
    final prefs = await SharedPreferences.getInstance();
    expect(LocalStore(prefs).current!['answers'], {
      'question': ['B'],
    });
    await tester.pumpWidget(const SizedBox.shrink());
  });

  testWidgets(
    'Opening another assignment preserves unsynced local draft and asks to continue it',
    (tester) async {
      final api = AssignmentApi();
      final prefs = await SharedPreferences.getInstance();
      await LocalStore(prefs).save(draft('different'));
      await showAssignments(tester, api);
      await tester.tap(find.text('Đề luyện phân số'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 400));
      expect(find.text('Bạn còn bài đang làm'), findsOneWidget);
      await tester.tap(find.text('Ở lại'));
      await tester.pumpAndSettle();
      expect(LocalStore(prefs).current!['exam']['id'], 'different');
      await tester.tap(find.text('Đề luyện phân số'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 400));
      await tester.tap(find.text('Tiếp tục bài đang làm'));
      await tester.pumpAndSettle();
      expect(find.text('Màn hình bài đang làm'), findsOneWidget);
      expect(LocalStore(prefs).current!['answers'], {
        'question': ['B'],
      });
      expect(api.starts, 0);
      expect(api.resumed, isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

  testWidgets('Assignment list retries a failed request and paginates by 30', (
    tester,
  ) async {
    final api = AssignmentApi()
      ..failStudent = true
      ..studentRows = [
        for (var n = 0; n < 31; n++)
          {...assignment(id: 'a$n'), 'title': 'Bài giao $n'},
      ];
    await showAssignments(tester, api);
    expect(find.text('Máy chủ tạm thời bận.'), findsOneWidget);
    api.failStudent = false;
    await tester.tap(find.text('Thử lại'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(find.text('Xem thêm'), 400);
    await tester.tap(find.text('Xem thêm'));
    await tester.pumpAndSettle();
    expect(api.offsets, [0, 0, 30]);
    await tester.scrollUntilVisible(find.text('Bài giao 30'), 300);
    expect(find.text('Bài giao 30'), findsOneWidget);
    expect(find.text('Xem thêm'), findsNothing);
    await tester.pumpWidget(const SizedBox.shrink());
  });

  testWidgets(
    'Student account and teacher group expose assignment entry points',
    (tester) async {
      final api = AssignmentApi();
      await showAssignments(tester, api, screen: const AccountScreen());
      expect(find.text('Bài được giao'), findsOneWidget);
      expect(find.text('Bài giao và tiến độ'), findsNothing);
      await tester.tap(find.text('Bài được giao'));
      await tester.pumpAndSettle();
      expect(find.text('Đề luyện phân số'), findsOneWidget);
      await tester.pumpWidget(const SizedBox.shrink());
      await showAssignments(
        tester,
        api,
        teacher: true,
        screen: const Scaffold(body: GroupPanel()),
      );
      await tester.tap(find.text('Nhóm Toán'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Bài giao và tiến độ'));
      await tester.pumpAndSettle();
      expect(find.text('Giao đề có sẵn'), findsOneWidget);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );

  test(
    'Assignment transport uses bounded pages, authenticated CSV request and explicit exam ID',
    () async {
      final requests = <RequestOptions>[];
      final dio = Dio(
        BaseOptions(
          baseUrl: 'https://school.example/api',
          headers: {'Authorization': 'Bearer synthetic'},
        ),
      );
      dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            requests.add(options);
            final Object body = options.path.endsWith('.csv')
                ? 'Tên,Điểm\n'
                : options.method == 'POST' || options.path.endsWith('/exam')
                ? assignment()
                : <Json>[];
            handler.resolve(
              Response(requestOptions: options, data: body, statusCode: 200),
            );
          },
        ),
      );
      final api = LearningApi(client: dio);
      await api.accountAssignments(offset: 30);
      await api.groupAssignments('group', offset: 60);
      await api.assignGroupExam('group', 'source');
      await api.groupAssignmentCsv('group', 'exam');
      expect(requests[0].queryParameters, {'offset': 30, 'limit': 30});
      expect(requests[1].queryParameters, {'offset': 60, 'limit': 30});
      expect(requests[2].data, {'exam_id': 'source'});
      expect(
        requests[3].path,
        '/classroom/groups/group/assignments/exam/results.csv',
      );
      expect(requests[3].queryParameters, isEmpty);
      expect(requests[3].headers['Authorization'], 'Bearer synthetic');
      expect(requests[3].responseType, ResponseType.plain);
    },
  );
}
