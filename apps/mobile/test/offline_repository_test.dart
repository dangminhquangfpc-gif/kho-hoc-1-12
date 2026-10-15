import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kho_hoc_mobile/offline_repository.dart';
import 'package:kho_hoc_mobile/repository.dart';
import 'package:shared_preferences/shared_preferences.dart';

class OfflineTestBundle extends CachingAssetBundle {
  OfflineTestBundle(this.content);
  final Json content;
  int reads = 0;
  @override
  Future<ByteData> load(String key) async {
    expect(key, 'assets/offline/content.json');
    reads++;
    return ByteData.sublistView(
      Uint8List.fromList(utf8.encode(jsonEncode(content))),
    );
  }
}

class ForbiddenAdapter implements HttpClientAdapter {
  int calls = 0;
  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<Uint8List>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    calls++;
    throw StateError('Offline repository attempted network I/O.');
  }

  @override
  void close({bool force = false}) {}
}

Json offlineFixture({String correct = '12'}) => {
  'schema_version': 1,
  'content_version': '2026.10.15.19',
  'catalog': {
    'grades': [
      {
        'id': 6,
        'subjects': [
          {'id': 'toan', 'name': 'Toán', 'requirement': 'required'},
          {'id': 'ngu_van', 'name': 'Ngữ văn', 'requirement': 'required'},
        ],
      },
    ],
  },
  'questions': [
    {
      'id': 'q1',
      'grade': 6,
      'subject': 'toan',
      'topic': 'phan_so',
      'textbook': 'ket_noi_tri_thuc',
      'type': 'numeric',
      'difficulty': 'easy',
      'question': 'Tính 6 × 2.',
      'options': [],
      'correct_answer': [correct],
      'max_score': '1',
      'explanation': '6 × 2 = 12.',
      'tolerance': '0',
      'unit': null,
      'rubric': [],
      'source_type': 'original',
    },
    {
      'id': 'essay',
      'grade': 6,
      'subject': 'ngu_van',
      'topic': 'viet',
      'textbook': 'ket_noi_tri_thuc',
      'type': 'essay',
      'difficulty': 'medium',
      'question': 'Viết đoạn văn.',
      'options': [],
      'correct_answer': [],
      'max_score': '2',
      'explanation': 'Giáo viên đọc và đánh giá.',
      'tolerance': '0',
      'unit': null,
      'rubric': [
        {'description': 'Nội dung', 'points': '2'},
      ],
      'source_type': 'original',
    },
  ],
  'question_public_metadata': {
    'q1': {'topic': 'phan_so', 'topic_name': 'Phân số'},
    'essay': {'topic': 'viet', 'topic_name': 'Viết'},
  },
  'exams': [
    {
      'id': 'exam',
      'title': 'Toán 6 · Phân số',
      'grade': 6,
      'subject': 'toan',
      'textbook': 'ket_noi_tri_thuc',
      'topic': 'phan_so',
      'question_ids': ['q1'],
      'duration_minutes': 15,
    },
    {
      'id': 'essay_exam',
      'title': 'Ngữ văn 6 · Viết',
      'grade': 6,
      'subject': 'ngu_van',
      'textbook': 'ket_noi_tri_thuc',
      'topic': 'viet',
      'question_ids': ['essay'],
      'duration_minutes': 20,
    },
  ],
  'documents': [
    {
      'id': 'lesson',
      'title': 'Bài 1. Phân số',
      'grade': 6,
      'subject': 'toan',
      'topic': 'phan_so',
      'semester': 1,
      'textbook': 'ket_noi_tri_thuc',
      'kind': 'study_notes',
      'summary': 'Cách tính và bài tập.',
      'author': 'Tự học 111',
      'source_name': 'Mục lục',
      'source_url': 'https://example.org/lesson',
      'source_type': 'original',
      'license': 'original_content',
      'lesson_order': 1,
      'curriculum_unit_id': 'unit_1',
      'assessment_period': 'review',
      'sections': [
        {'heading': 'Kiến thức và cách làm', 'text': 'Nhân một số với 2.'},
        {
          'heading': 'Ví dụ từng bước',
          'text': 'Lời giải: 6 × 2 = 12. Đáp số: 12.',
        },
      ],
    },
    {
      'id': 'source_exam',
      'title': 'Đề giữa kì 1 nguồn tham khảo',
      'grade': 6,
      'subject': 'toan',
      'topic': 'phan_so',
      'semester': 1,
      'textbook': 'ket_noi_tri_thuc',
      'kind': 'exam',
      'summary': 'Đề tham khảo.',
      'author': 'Nguồn',
      'source_name': 'Nguồn',
      'source_url': 'https://example.org/exam',
      'source_type': 'link_only',
      'license': 'link_only',
      'assessment_period': 'midterm_1',
      'exam_year': 2026,
      'resource_scope': 'single_paper',
      'sections': [],
    },
  ],
  'lesson_document_ids': ['lesson'],
  'textbook_units': {
    'books': [
      {
        'grade': 6,
        'subject': 'toan',
        'edition': 'Kết nối tri thức',
        'source_url': 'https://example.org/index',
        'units': [
          {'id': 'unit_1', 'title': 'Phân số'},
          {'id': 'unit_2', 'title': 'Chưa có bài'},
        ],
      },
    ],
  },
  'source_practice_map': {
    'papers': {
      'source_exam': {
        'exam_id': 'exam',
        'title': 'Toán 6 · Luyện giữa kì 1',
        'question_count': 1,
        'notice': 'Đề tự biên soạn theo chủ đề.',
      },
    },
  },
};

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => SharedPreferences.setMockInitialValues({}));

  test(
    'bundled subjects/exams/coverage/documents/curriculum preserve truthful content shapes',
    () async {
      final bundle = OfflineTestBundle(offlineFixture());
      final api = OfflineLearningApi(bundle: bundle);
      expect(api.isOffline, isTrue);
      expect(await api.currentUser(), isNull);
      await api.checkConnection();
      expect((await api.subjects(6)).first['name'], 'Toán');
      expect(
        (await api.exams(6, 'toan', 'phan so')).single['question_count'],
        1,
      );
      expect((await api.exams(6, 'toan', 'missing')), isEmpty);
      final coverage = (await api.coverage(6)).first;
      expect(coverage['question_count'], 1);
      expect(coverage['external_paper_count'], 1);
      final lesson = (await api.documents({
        'grade': 6,
        'subject': 'toan',
        'section': 'lessons',
        'search': 'loi giai',
      })).single;
      expect(lesson['id'], 'lesson');
      expect(lesson.containsKey('sections'), isFalse);
      final detail = await api.document('lesson');
      expect(detail['sections'], hasLength(2));
      expect(detail['can_view_pdf'], isFalse);
      expect(detail['can_download'], isFalse);
      expect(detail['file_url'], isNull);
      expect(detail['updated_at'], '2026-10-15T00:00:00Z');
      final source = (await api.documents({
        'section': 'exams',
        'assessment_period': 'midterm_1',
        'exam_year': 2026,
      })).single;
      expect(source['practice_exam_id'], 'exam');
      expect(source['practice_notice'], contains('tự biên soạn'));
      expect(source['reference_title'], contains('nguồn tham khảo'));
      final curriculum = await api.curriculum(6, 'toan');
      expect(curriculum['authored_count'], 1);
      expect(curriculum['unit_count'], 2);
      expect(curriculum['units'][0]['document_id'], 'lesson');
      expect(curriculum['units'][1]['content_status'], 'missing');
      expect(
        (await api.curriculum(6, 'ngu_van'))['status'],
        'index_not_verified',
      );
      expect(bundle.reads, 1);
    },
  );

  test(
    'every inherited server operation is rejected before the network adapter',
    () async {
      final api = OfflineLearningApi(
        bundle: OfflineTestBundle(offlineFixture()),
      );
      final adapter = ForbiddenAdapter();
      api.client.httpClientAdapter = adapter;
      final actions = <Future<dynamic> Function()>[
        () => api.authenticate('student', 'password'),
        () => api.deleteAccount('password'),
        () => api.signOut(),
        () => api.changePassword('old', 'new'),
        () => api.sendContentReport({}),
        () => api.contentReports(),
        () => api.reviewContentReport('report', {}),
        () => api.classroomGroups(),
        () => api.accountAssignments(),
        () => api.groupAssignments('group'),
        () => api.assignGroupExam('group', 'exam'),
        () => api.groupAssignmentProgress('group', 'exam'),
        () => api.groupAssignmentCsv('group', 'exam'),
        () => api.groupResultsCsv('group'),
        () => api.createGroup('name'),
        () => api.joinGroup('code'),
        () => api.addGroupMember('group', 'student'),
        () => api.removeGroupMember('group', 'user'),
        () => api.deleteGroup('group'),
        () => api.classroomStudents(),
        () => api.createStudents([]),
        () => api.studentResults('user'),
        () => api.accountResults(),
        () => api.pendingAttempts(),
        () => api.resumeAttempt('id'),
        () => api.saveDraft({'id': 'id'}),
        () => api.removeStudent('user'),
        () => api.resetStudentPassword('user'),
        () => api.createPractice({'grade': 6, 'subject': 'toan', 'count': 1}),
      ];
      for (final action in actions) {
        await expectLater(action, throwsA(anything));
      }
      expect(
        () => api.publicUrl('/documents/id/file'),
        throwsA(isA<OfflineFeatureUnavailable>()),
      );
      expect(adapter.calls, 0);
    },
  );

  test(
    'attempt answer keys stay private until submit and immutable across restart/bundle updates',
    () async {
      final api = OfflineLearningApi(
        bundle: OfflineTestBundle(offlineFixture()),
      );
      final session = await api.start('exam');
      expect(session['id'], startsWith('offline_'));
      expect(session['account_id'], isNull);
      expect(session['local_self_practice'], isTrue);
      expect(session['questions'][0].containsKey('correct_answer'), isFalse);
      expect(session['questions'][0].containsKey('explanation'), isFalse);
      expect(session['questions'][0]['topic_name'], 'Phân số');
      session['questions'][0]['question'] = 'Client mutation';
      session['exam']['title'] = 'Client mutation';
      session['answers'] = {
        'q1': ['12'],
      };
      final restarted = OfflineLearningApi(
        bundle: OfflineTestBundle(offlineFixture(correct: '999')),
      );
      final result = await restarted.submit(session);
      expect(result['score'], 1.0);
      expect(result['title'], 'Toán 6 · Phân số');
      expect(result['details'][0]['question'], 'Tính 6 × 2.');
      expect(result['details'][0]['correct_answer'], ['12']);
      expect(result['local_self_practice'], isTrue);
      result['details'][0]['score'] = 999;
      expect(
        (await restarted.attemptResult(session))['details'][0]['score'],
        1.0,
      );
      expect((await api.submit(session))['score'], 1.0);
      final changed = {
        ...session,
        'answers': {
          'q1': ['13'],
        },
      };
      await expectLater(
        api.submit(changed),
        throwsA(
          isA<DioException>().having(
            (e) => e.response?.statusCode,
            'status',
            409,
          ),
        ),
      );
      await api.delete(session);
      await expectLater(
        api.attemptResult(session),
        throwsA(
          isA<DioException>().having(
            (e) => e.response?.statusCode,
            'status',
            404,
          ),
        ),
      );
      await api.delete(session);
    },
  );

  test(
    'invalid, cross-account and remote submissions never grade or change local results',
    () async {
      final api = OfflineLearningApi(
        bundle: OfflineTestBundle(offlineFixture()),
      );
      final session = await api.start('exam');
      for (final bad in <Json>[
        {...session, 'backend_url': 'https://example.org/api'},
        {...session, 'account_id': 'student'},
        {...session, 'token': 'different'},
        {
          ...session,
          'answers': {
            'unknown': ['12'],
          },
        },
        {
          ...session,
          'answers': {
            'q1': ['12', for (var i = 0; i < 20; i++) '12'],
          },
        },
        {
          ...session,
          'answers': {
            'q1': [1],
          },
        },
      ]) {
        await expectLater(api.submit(bad), throwsA(isA<DioException>()));
      }
      await expectLater(
        api.attemptResult(session),
        throwsA(
          isA<DioException>().having(
            (e) => e.response?.statusCode,
            'status',
            409,
          ),
        ),
      );
      session['answers'] = {
        'q1': ['12'],
      };
      final results = await Future.wait([
        api.submit(session),
        api.submit(session),
      ]);
      expect(results[0], results[1]);
      expect(results[0]['score'], 1.0);
    },
  );

  test(
    'essay self-practice remains ungraded and explicit wrong-question review stays offline',
    () async {
      final api = OfflineLearningApi(
        bundle: OfflineTestBundle(offlineFixture()),
      );
      final essay = await api.start('essay_exam');
      essay['answers'] = {
        'essay': ['Một đoạn văn.'],
      };
      final result = await api.submit(essay);
      expect(result['score'], isNull);
      expect(result['graded_score'], 0);
      expect(result['status'], 'needs_manual_review');
      final filter = {
        'grade': 6,
        'subject': 'toan',
        'topic': 'phan_so',
        'count': 1,
        'question_ids': ['q1'],
      };
      final review = await api.createPractice(filter);
      review['answers'] = {
        'q1': ['12'],
      };
      review['flags'] = ['q1'];
      final recovered = await api.recover(review);
      expect(recovered['id'], isNot(review['id']));
      expect(recovered['answers'], {
        'q1': ['12'],
      });
      expect(recovered['flags'], ['q1']);
      expect((await api.submit(recovered))['score'], 1.0);
      await expectLater(
        api.createPractice({...filter, 'group_id': 'group'}),
        throwsA(isA<OfflineFeatureUnavailable>()),
      );
      await expectLater(
        api.createPractice({
          ...filter,
          'question_ids': ['essay'],
        }),
        throwsA(isA<DioException>()),
      );
    },
  );
}
