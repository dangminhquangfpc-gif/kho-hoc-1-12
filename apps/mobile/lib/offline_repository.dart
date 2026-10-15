import 'dart:convert';
import 'dart:math';

import 'package:dio/dio.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'offline_grading.dart';
import 'repository.dart' show Json, LearningApi, vietnameseSearchKey;

/// Bundled, deterministic self-practice. No account or server credentials are
/// read here, and all inherited remote operations are blocked before I/O.
class OfflineLearningApi extends LearningApi {
  OfflineLearningApi({
    AssetBundle? bundle,
    Future<SharedPreferences> Function()? preferences,
  }) : _bundle = bundle ?? rootBundle,
       _preferences = preferences ?? SharedPreferences.getInstance,
       super(baseUrl: offlineBaseUrl) {
    client.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) => handler.reject(
          DioException(
            requestOptions: options,
            type: DioExceptionType.cancel,
            error: const OfflineFeatureUnavailable(),
            message: const OfflineFeatureUnavailable().toString(),
          ),
        ),
      ),
    );
  }

  static const offlineBaseUrl = 'offline://tu-hoc-111/v1';
  static const _prefix = 'offline_api_v1.attempt.';
  final AssetBundle _bundle;
  final Future<SharedPreferences> Function() _preferences;
  Future<Json>? _loaded;
  // Serialize local writes even across multiple API instances during provider
  // recreation. Persist before returning so an interrupted submit can retry.
  static Future<void> _writeTail = Future<void>.value();

  @override
  bool get isOffline => true;

  @override
  String get baseUrl => offlineBaseUrl;

  Future<Json> _content() => _loaded ??= _readContent();

  Future<Json> _readContent() async {
    final value = await compute(
      _decodeOfflineContent,
      await _bundle.loadString('assets/offline/content.json'),
    );
    if (value['schema_version'] != 1 ||
        value['questions'] is! List ||
        value['exams'] is! List ||
        value['documents'] is! List ||
        value['catalog'] is! Json) {
      throw const FormatException('Dữ liệu học ngoại tuyến không hợp lệ.');
    }
    return value;
  }

  Json _clone(Json value) => jsonDecode(jsonEncode(value)) as Json;
  List<Json> _rows(dynamic value) => (value as List? ?? []).cast<Json>();

  Future<T> _write<T>(Future<T> Function() operation) {
    final next = _writeTail.then((_) => operation());
    _writeTail = next.then<void>((_) {}, onError: (Object _, StackTrace __) {});
    return next;
  }

  DioException _error(int status, String message) {
    final request = RequestOptions(path: '/offline', baseUrl: offlineBaseUrl);
    return DioException(
      requestOptions: request,
      response: Response(
        requestOptions: request,
        statusCode: status,
        data: {'detail': message},
      ),
      type: DioExceptionType.badResponse,
      message: message,
    );
  }

  @override
  Future<Json?> currentUser() async => null;

  @override
  Future<void> checkConnection() async {
    await _content();
  }

  @override
  Future<Json> authenticate(
    String username,
    String password, {
    String? displayName,
    int? grade,
    String role = 'student',
  }) async => throw const OfflineFeatureUnavailable();

  @override
  Uri publicUrl(String path) => throw const OfflineFeatureUnavailable();

  @override
  Future<List<Json>> subjects(int grade) async {
    final content = await _content();
    final row = _rows(
      content['catalog']['grades'],
    ).where((value) => value['id'] == grade);
    if (row.isEmpty) throw _error(404, 'Không tìm thấy lớp học.');
    return _rows(row.single['subjects']).map(_clone).toList();
  }

  @override
  Future<List<Json>> exams(int grade, String subject, String search) async {
    final content = await _content();
    final needle = _search(search);
    return [
      for (final exam in _rows(content['exams']))
        if (exam['grade'] == grade &&
            exam['subject'] == subject &&
            _search(exam['title']).contains(needle))
          {
            for (final entry in exam.entries)
              if (entry.key != 'question_ids') entry.key: entry.value,
            'question_count': (exam['question_ids'] as List).length,
          },
    ].map(_clone).toList();
  }

  @override
  Future<List<Json>> coverage(int grade) async {
    final content = await _content();
    final questions = _rows(
      content['questions'],
    ).where((q) => q['grade'] == grade);
    final allExams = _rows(content['exams']).where((q) => q['grade'] == grade);
    final docs = _rows(content['documents']).where((q) => q['grade'] == grade);
    return [
      for (final subject in await subjects(grade))
        {
          'subject': subject['id'],
          'name': subject['name'],
          'question_count': questions
              .where((q) => q['subject'] == subject['id'])
              .length,
          'exam_count': allExams
              .where((q) => q['subject'] == subject['id'])
              .length,
          'document_count': docs
              .where((d) => d['subject'] == subject['id'])
              .length,
          'external_document_count': docs
              .where(
                (d) =>
                    d['subject'] == subject['id'] &&
                    d['source_type'] == 'link_only',
              )
              .length,
          'external_paper_count': docs
              .where(
                (d) =>
                    d['subject'] == subject['id'] &&
                    d['source_type'] == 'link_only' &&
                    d['resource_scope'] == 'single_paper',
              )
              .length,
          'topic_count': questions
              .where((q) => q['subject'] == subject['id'])
              .map((q) => q['topic'])
              .toSet()
              .length,
          'local_self_practice': true,
        },
    ];
  }

  @override
  Future<Json> curriculum(int grade, String subject) async {
    final content = await _content();
    final books = _rows(content['textbook_units']?['books']);
    final matches = books.where(
      (b) => b['grade'] == grade && b['subject'] == subject,
    );
    if (matches.isEmpty || _rows(matches.single['units']).isEmpty) {
      return {
        'status': 'index_not_verified',
        'units': [],
        'unit_count': null,
        'authored_count': 0,
      };
    }
    final book = matches.single;
    final lessonIds = Set<String>.from(
      content['lesson_document_ids'] as List? ?? [],
    );
    final authored = <String, String>{
      for (final doc in _rows(content['documents']))
        if (doc['grade'] == grade &&
            doc['subject'] == subject &&
            lessonIds.contains(doc['id']) &&
            doc['curriculum_unit_id'] is String)
          doc['curriculum_unit_id'] as String: doc['id'] as String,
    };
    final units = [
      for (final unit in _rows(book['units']))
        {
          ..._clone(unit),
          'document_id': authored[unit['id']],
          'content_status': authored.containsKey(unit['id'])
              ? 'authored_pending_review'
              : 'missing',
        },
    ];
    return {
      'status': 'secondary_index_pending_publisher_review',
      'source_url': book['source_url'],
      'edition': book['edition'],
      'unit_count': units.length,
      'authored_count': units
          .where((unit) => unit['document_id'] != null)
          .length,
      'units': units,
    };
  }

  String _search(dynamic value) => vietnameseSearchKey(value?.toString() ?? '')
      .replaceAll(RegExp(r'[\u0300-\u036f]'), '')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  Json _documentView(Json doc, Json content, {bool detail = false}) {
    const keys = [
      'id',
      'title',
      'grade',
      'subject',
      'semester',
      'topic',
      'textbook',
      'kind',
      'summary',
      'author',
      'source_name',
      'source_url',
      'source_type',
      'license',
      'assessment_period',
      'chapter',
      'lesson_order',
      'curriculum_unit_id',
      'exam_year',
      'source_verified_on',
      'resource_scope',
      'access_notice',
    ];
    final output = <String, dynamic>{
      for (final key in keys) key: doc[key],
      'state': 'published', 'version': 1,
      'updated_at':
          '${content['content_version'].toString().split('.').take(3).join('-')}T00:00:00Z',
      // Only the document text is bundled; PDF references remain online links.
      'can_view_pdf': false, 'can_download': false, 'file_url': null,
      'can_open_source':
          doc['source_url'] is String &&
          Uri.tryParse(doc['source_url'])?.scheme == 'https',
      if (detail) 'sections': doc['sections'] ?? [],
      'local_self_practice': true,
    };
    final pair = content['source_practice_map']?['papers']?[doc['id']];
    if (pair is Map) {
      output.addAll({
        'reference_title': output['title'],
        'title': pair['title'],
        'practice_exam_id': pair['exam_id'],
        'practice_notice': pair['notice'],
        'summary':
            "${pair['question_count']} câu · Làm và chấm trong app. ${pair['notice']} Nguồn tham khảo: ${doc['title']}",
      });
    }
    return _clone(output);
  }

  @override
  Future<List<Json>> documents(Map<String, dynamic> filter) async {
    final content = await _content();
    final lessonIds = Set<String>.from(
      content['lesson_document_ids'] as List? ?? [],
    );
    final found = <Json>[];
    final terms = _search(
      filter['search'],
    ).split(' ').where((s) => s.isNotEmpty).toList();
    for (final doc in _rows(content['documents'])) {
      final isExam =
          doc['kind'] == 'exam' ||
          const [
            'midterm_1',
            'final_1',
            'midterm_2',
            'final_2',
            'graduation',
          ].contains(doc['assessment_period']);
      final isLesson = lessonIds.contains(doc['id']);
      final section = filter['section'];
      if ((section == 'lessons' && !isLesson) ||
          (section == 'exams' && !isExam) ||
          (section == 'references' && (isLesson || isExam))) {
        continue;
      }
      if (const [
        'grade',
        'subject',
        'semester',
        'textbook',
        'kind',
        'assessment_period',
        'exam_year',
      ].any((key) => filter[key] != null && doc[key] != filter[key])) {
        continue;
      }
      if (!_search(doc['topic']).contains(_search(filter['topic']))) continue;
      final haystack = _search(
        [
          doc['title'],
          doc['topic'],
          doc['summary'],
          doc['author'],
          for (final section in _rows(doc['sections']))
            '${section['heading']} ${section['text']}',
        ].join(' '),
      );
      if (!terms.every(haystack.contains)) continue;
      found.add(_documentView(doc, content));
    }
    int rank(Json item) {
      if (terms.isEmpty || terms.every(_search(item['title']).contains)) {
        return 0;
      }
      final metadata = _search(
        '${item['title']} ${item['topic']} ${item['summary']}',
      );
      return terms.every(metadata.contains) ? 1 : 2;
    }

    if (filter['section'] == 'lessons') {
      found.sort((a, b) {
        final ranked = rank(a).compareTo(rank(b));
        if (ranked != 0) return ranked;
        final order = (a['lesson_order'] as int? ?? 100000).compareTo(
          b['lesson_order'] as int? ?? 100000,
        );
        return order != 0
            ? order
            : a['title'].toString().compareTo(b['title'].toString());
      });
    } else if (terms.isNotEmpty) {
      found.sort((a, b) => rank(a).compareTo(rank(b)));
    }
    return found;
  }

  @override
  Future<Json> document(String id) async {
    final content = await _content();
    final matches = _rows(content['documents']).where((d) => d['id'] == id);
    if (matches.isEmpty) {
      throw _error(404, 'Không tìm thấy tài liệu trên thiết bị.');
    }
    return _documentView(matches.single, content, detail: true);
  }

  Json _publicQuestion(Json q, Json content) => {
    for (final key in const [
      'id',
      'grade',
      'subject',
      'type',
      'question',
      'options',
      'max_score',
    ])
      key: q[key],
    'topic':
        content['question_public_metadata']?[q['id']]?['topic'] ?? q['topic'],
    'topic_name':
        content['question_public_metadata']?[q['id']]?['topic_name'] ??
        q['topic'],
  };

  @override
  Future<Json> practiceOptions(int grade, String subject) async {
    final content = await _content();
    final topics = <String, Json>{}, groups = <String, Json>{};
    var total = 0;
    for (final q in _rows(content['questions'])) {
      if (q['grade'] != grade ||
          q['subject'] != subject ||
          q['type'] == 'essay' ||
          q['source_type'] == 'link_only') {
        continue;
      }
      total++;
      final public = _publicQuestion(q, content);
      final topic = public['topic'] as String;
      final item = topics.putIfAbsent(
        topic,
        () => {'id': topic, 'name': public['topic_name'], 'count': 0},
      );
      item['count'] = (item['count'] as int) + 1;
      final key = '$topic/${q['difficulty']}/${q['textbook']}';
      final group = groups.putIfAbsent(
        key,
        () => {
          'topic': topic,
          'difficulty': q['difficulty'],
          'textbook': q['textbook'],
          'count': 0,
        },
      );
      group['count'] = (group['count'] as int) + 1;
    }
    final topicRows = topics.values.toList()
      ..sort((a, b) => _search(a['name']).compareTo(_search(b['name'])));
    return {
      'grade': grade,
      'subject': subject,
      'total': total,
      'topics': topicRows,
      'groups': groups.values.toList(),
    };
  }

  @override
  Future<Json> createPractice(Json filter) async {
    final ids = filter['question_ids'];
    if (filter['group_id'] != null ||
        ids is! List ||
        ids.isEmpty ||
        ids.length > 50 ||
        ids.any((id) => id is! String) ||
        ids.toSet().length != ids.length ||
        filter['count'] != ids.length) {
      throw const OfflineFeatureUnavailable();
    }
    final content = await _content();
    final byId = {for (final q in _rows(content['questions'])) q['id']: q};
    final questions = <Json>[];
    for (final id in ids) {
      final q = byId[id];
      if (q == null ||
          q['grade'] != filter['grade'] ||
          q['subject'] != filter['subject'] ||
          q['type'] == 'essay') {
        throw _error(
          409,
          'Một số câu hỏi không có trong ngân hàng tự luyện trên thiết bị.',
        );
      }
      final public = _publicQuestion(q, content);
      if (filter['topic'] != null && public['topic'] != filter['topic']) {
        throw _error(409, 'Câu hỏi không thuộc chủ đề cần ôn.');
      }
      questions.add(q);
    }
    final title = (await subjects(
      filter['grade'] as int,
    )).firstWhere((s) => s['id'] == filter['subject'])['name'];
    final exam = <String, dynamic>{
      'id': 'offline_review_${filter['grade']}_${filter['subject']}',
      'grade': filter['grade'],
      'subject': filter['subject'],
      'title': '$title ${filter['grade']} · Ôn câu chưa đúng',
      'textbook': 'independent',
      'topic': filter['topic'] ?? 'tong_hop',
      'duration_minutes': 30,
    };
    return _createAttempt(
      exam,
      questions,
      content,
      practiceFilter: _clone(filter),
    );
  }

  @override
  Future<Json> start(String id) async {
    final content = await _content();
    final matches = _rows(content['exams']).where((exam) => exam['id'] == id);
    if (matches.isEmpty) {
      throw _error(404, 'Không tìm thấy đề luyện trên thiết bị.');
    }
    final exam = matches.single;
    final byId = {for (final q in _rows(content['questions'])) q['id']: q};
    final questions = <Json>[];
    for (final qid in exam['question_ids'] as List) {
      final q = byId[qid];
      if (q == null ||
          q['grade'] != exam['grade'] ||
          q['subject'] != exam['subject']) {
        throw const FormatException('Đề luyện thiếu câu hỏi hợp lệ.');
      }
      questions.add(q);
    }
    return _createAttempt(exam, questions, content);
  }

  Future<Json> _createAttempt(
    Json exam,
    List<Json> questions,
    Json content, {
    Json? practiceFilter,
  }) async {
    final random = Random.secure();
    final token = List.generate(24, (_) => random.nextInt(256));
    final attemptId =
        'offline_${DateTime.now().microsecondsSinceEpoch}_${base64UrlEncode(token.take(9).toList()).replaceAll('=', '')}';
    final session = <String, dynamic>{
      'id': attemptId,
      'token': base64UrlEncode(token),
      'exam': {
        for (final entry in exam.entries)
          if (entry.key != 'question_ids') entry.key: entry.value,
      },
      'questions': [for (final q in questions) _publicQuestion(q, content)],
      'created_at': DateTime.now().toUtc().toIso8601String(),
      'backend_url': offlineBaseUrl,
      'local_self_practice': true,
      'answers': <String, dynamic>{},
      'flags': <String>[],
      'content_version': content['content_version'],
      if (practiceFilter != null) 'practice_filter': practiceFilter,
    };
    await _write(() async {
      final prefs = await _preferences();
      if (!await prefs.setString(
        '$_prefix$attemptId',
        jsonEncode({
          'session': session,
          'questions': questions,
          'result': null,
        }),
      )) {
        throw StateError('Không thể lưu đề luyện trên thiết bị.');
      }
    });
    return _clone(session);
  }

  Future<(SharedPreferences, Json)> _owned(Json session) async {
    if (session['backend_url'] != offlineBaseUrl ||
        session['local_self_practice'] != true ||
        session['account_id'] != null ||
        session['id'] is! String ||
        !session['id'].toString().startsWith('offline_')) {
      throw _error(
        404,
        'Bài này thuộc máy chủ khác, không thể nộp bằng chế độ tự luyện.',
      );
    }
    final prefs = await _preferences();
    await prefs.reload();
    final encoded = prefs.getString('$_prefix${session['id']}');
    if (encoded == null) {
      throw _error(404, 'Phiên tự luyện không còn trên thiết bị.');
    }
    final record = jsonDecode(encoded) as Json;
    if (record['session']?['token'] != session['token']) {
      throw _error(404, 'Không tìm thấy phiên tự luyện.');
    }
    return (prefs, record);
  }

  Map<String, dynamic> _answers(Json session, List<Json> questions) {
    final value = session['answers'] ?? <String, dynamic>{};
    if (value is! Map || value.length > 100) {
      throw _error(422, 'Câu trả lời không hợp lệ.');
    }
    final ids = questions.map((q) => q['id']).toSet();
    final output = <String, dynamic>{};
    for (final entry in value.entries) {
      final answer = entry.value;
      if (entry.key is! String ||
          !ids.contains(entry.key) ||
          answer is! List ||
          answer.length > 20 ||
          answer.any((a) => a is! String || a.length > 10000)) {
        throw _error(422, 'Câu trả lời không hợp lệ.');
      }
      output[entry.key as String] = List<String>.from(answer);
    }
    return output;
  }

  bool _sameAnswers(Map old, Map next) =>
      old.length == next.length &&
      old.entries.every(
        (entry) =>
            next.containsKey(entry.key) &&
            jsonEncode(entry.value) == jsonEncode(next[entry.key]),
      );

  @override
  Future<Json> submit(Json session) => _write(() async {
    final (prefs, record) = await _owned(session);
    final questions = _rows(record['questions']);
    final answers = _answers(session, questions);
    if (record['result'] != null) {
      if (!_sameAnswers(record['answers'] as Map, answers)) {
        throw _error(409, 'Bài đã nộp với câu trả lời khác.');
      }
      return _clone(record['result'] as Json);
    }
    final saved = record['session'] as Json;
    final result = gradeOfflineAttempt(
      id: saved['id'],
      exam: saved['exam'] as Json,
      questions: questions,
      answers: answers,
    );
    record['result'] = result;
    record['answers'] = answers;
    if (!await prefs.setString('$_prefix${saved['id']}', jsonEncode(record))) {
      throw StateError('Không thể lưu kết quả tự luyện.');
    }
    return _clone(result);
  });

  @override
  Future<Json> attemptResult(Json session) async {
    final (_, record) = await _owned(session);
    if (record['result'] == null) throw _error(409, 'Bài tự luyện chưa nộp.');
    return _clone(record['result'] as Json);
  }

  @override
  Future<void> delete(Json session) => _write(() async {
    try {
      final (prefs, _) = await _owned(session);
      if (!await prefs.remove('$_prefix${session['id']}')) {
        throw StateError('Không thể xóa bài tự luyện.');
      }
    } on DioException catch (error) {
      if (error.response?.statusCode != 404) rethrow;
    }
  });

  @override
  Future<Json> recover(Json previous) async {
    if (previous['backend_url'] != offlineBaseUrl ||
        previous['local_self_practice'] != true ||
        previous['account_id'] != null) {
      throw _error(
        404,
        'Bài cũ thuộc máy chủ khác. Hãy kết nối lại đúng máy chủ.',
      );
    }
    final next = previous['practice_filter'] is Map
        ? await createPractice(
            Map<String, dynamic>.from(previous['practice_filter'] as Map),
          )
        : await start(previous['exam']?['id'] as String? ?? '');
    final oldQuestions = {
      for (final q in _rows(previous['questions'])) q['id']: q,
    };
    final unchanged = <String>{};
    final answers = <String, dynamic>{};
    for (final q in _rows(next['questions'])) {
      final old = oldQuestions[q['id']];
      if (old == null || jsonEncode(old) != jsonEncode(q)) continue;
      unchanged.add(q['id'] as String);
      final answer = (previous['answers'] as Map? ?? {})[q['id']];
      if (answer is List && answer.every((a) => a is String)) {
        answers[q['id'] as String] = List<String>.from(answer);
      }
    }
    return {
      ...next,
      'answers': answers,
      'flags': (previous['flags'] as List? ?? [])
          .where(unchanged.contains)
          .toList(),
      'recovery_notice':
          'Đã khôi phục ${answers.length} câu trả lời tự luyện trên thiết bị. Hãy xem lại trước khi nộp.',
    };
  }
}

class OfflineFeatureUnavailable implements Exception {
  const OfflineFeatureUnavailable();
  @override
  String toString() =>
      'Tính năng tài khoản, lớp học và tạo đề cần kết nối máy chủ HTTPS. Bạn vẫn có thể đọc tài liệu và làm đề có sẵn trên thiết bị.';
}

Json _decodeOfflineContent(String encoded) => jsonDecode(encoded) as Json;
