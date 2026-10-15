import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

typedef Json = Map<String, dynamic>;

class LearningApi {
  LearningApi({Dio? client, String? baseUrl})
    : client =
          client ??
          Dio(
            BaseOptions(
              baseUrl:
                  baseUrl ??
                  const String.fromEnvironment(
                    'API_BASE_URL',
                    defaultValue: 'http://10.0.2.2:8000',
                  ),
              connectTimeout: const Duration(seconds: 10),
              receiveTimeout: const Duration(seconds: 20),
            ),
          );
  final Dio client;
  String? expectedAccountId;
  void Function()? onSessionLost;
  Json checkedAttempt(Json value) {
    if (expectedAccountId != null && value['account_id'] != expectedAccountId) {
      onSessionLost?.call();
      throw StateError('Phiên đăng nhập đã hết hạn. Hãy đăng nhập lại.');
    }
    return value;
  }

  String get baseUrl => client.options.baseUrl;
  Future<Json?> currentUser() async {
    try {
      return (await client.get<Json>('/auth/me')).data;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) return null;
      rethrow;
    }
  }

  Future<Json> authenticate(
    String username,
    String password, {
    String? displayName,
    int? grade,
    String role = 'student',
  }) async {
    if (kIsWeb || kReleaseMode) {
      final target = kIsWeb
          ? Uri.base.resolve(client.options.baseUrl)
          : Uri.parse(client.options.baseUrl);
      if (target.scheme != 'https' &&
          !(kIsWeb &&
              ['localhost', '127.0.0.1', '::1'].contains(target.host))) {
        throw StateError(
          'Đăng nhập từ máy khác cần backend HTTPS. Không gửi mật khẩu qua kết nối HTTP.',
        );
      }
    }
    final response = (await client.post<Json>(
      displayName == null ? '/auth/login' : '/auth/register',
      data: {
        'username': username.trim(),
        'password': password,
        'mobile': !kIsWeb,
        if (displayName != null) 'display_name': displayName.trim(),
        if (displayName != null) 'role': role,
        if (grade != null) 'grade': grade,
      },
    )).data!;
    if (!kIsWeb) {
      client.options.headers['Authorization'] = 'Bearer ${response['token']}';
    }
    return response['user'] as Json;
  }

  Future<void> deleteAccount(String password) async {
    await client.post('/account/delete', data: {'password': password});
    client.options.headers.remove('Authorization');
  }

  Future<void> signOut() async {
    await client.post('/auth/logout');
    client.options.headers.remove('Authorization');
  }

  Future<Json> changePassword(String current, String next) async =>
      (await client.post<Json>(
        '/auth/password',
        data: {'current_password': current, 'new_password': next},
      )).data!;
  Future<List<Json>> classroomGroups() async =>
      (await client.get<List<dynamic>>('/classroom/groups')).data!.cast<Json>();
  Future<String> groupResultsCsv(String id) async => (await client.get<String>(
    '/classroom/groups/$id/results.csv',
    options: Options(responseType: ResponseType.plain),
  )).data!;
  Future<void> createGroup(String name) async {
    await client.post('/classroom/groups', data: {'name': name});
  }

  Future<void> joinGroup(String code) async {
    await client.post('/classroom/groups/join', data: {'code': code.trim()});
  }

  Future<void> addGroupMember(String id, String username) async {
    await client.post(
      '/classroom/groups/$id/members',
      data: {'username': username.trim()},
    );
  }

  Future<void> removeGroupMember(String id, String userId) async {
    await client.delete('/classroom/groups/$id/members/$userId');
  }

  Future<void> deleteGroup(String id) async {
    await client.delete('/classroom/groups/$id');
  }

  Future<List<Json>> classroomStudents() async =>
      (await client.get<List<dynamic>>(
        '/classroom/students',
      )).data!.cast<Json>();
  Future<List<Json>> createStudents(List<Json> students) async =>
      (await client.post<List<dynamic>>(
        '/classroom/students/bulk',
        data: {'students': students},
      )).data!.cast<Json>();
  Future<Json> studentResults(String id) async =>
      (await client.get<Json>('/classroom/students/$id/results')).data!;
  Future<List<Json>> accountResults() async =>
      (await client.get<List<dynamic>>('/account/results')).data!.cast<Json>();
  Future<List<Json>> pendingAttempts() async =>
      (await client.get<List<dynamic>>('/account/attempts')).data!.cast<Json>();
  Future<Json> resumeAttempt(String id) async =>
      checkedAttempt((await client.get<Json>('/account/attempts/$id')).data!);
  Future<int> saveDraft(Json session) async {
    final response = await client.post<Json>(
      '/account/attempts/${session['id']}/draft',
      data: {
        'revision': session['draft_revision'] ?? 0,
        'answers': session['answers'] ?? {},
      },
    );
    return response.data!['revision'] as int;
  }

  Future<void> removeStudent(String id) async {
    await client.delete('/classroom/students/$id');
  }

  Future<Json> resetStudentPassword(String id) async =>
      (await client.post<Json>('/classroom/students/$id/reset-password')).data!;

  Future<void> checkConnection() async {
    final response = await client.get<Json>('/health');
    if (response.data?['status'] != 'ok') {
      throw StateError('Máy chủ chưa sẵn sàng.');
    }
    await subjects(1);
  }

  Future<List<Json>> documents(Map<String, dynamic> filter) async {
    final output = <Json>[];
    for (var offset = 0; offset <= 10000; offset += 100) {
      final page = (await client.get<List<dynamic>>(
        '/documents',
        queryParameters: {...filter, 'limit': 100, 'offset': offset},
      )).data!.cast<Json>();
      output.addAll(page);
      if (page.length < 100) return output;
    }
    throw StateError('Quá nhiều tài liệu. Hãy chọn thêm bộ lọc.');
  }

  Future<Json> curriculum(int grade, String subject) async =>
      (await client.get<Json>(
        '/curriculum',
        queryParameters: {'grade': grade, 'subject': subject},
      )).data!;

  Future<Json> document(String id) async =>
      (await client.get<Json>('/documents/$id')).data!;
  Uri publicUrl(String path) {
    final base = Uri.base.resolve(
      client.options.baseUrl.endsWith('/')
          ? client.options.baseUrl
          : '${client.options.baseUrl}/',
    );
    return base.resolve(path.replaceFirst(RegExp(r'^/'), ''));
  }

  Future<List<Json>> coverage(int grade) async =>
      (await client.get<List<dynamic>>(
        '/coverage',
        queryParameters: {'grade': grade},
      )).data!.cast<Json>();

  Future<List<Json>> subjects(int grade) async =>
      (await client.get<List<dynamic>>(
        '/grades/$grade/subjects',
      )).data!.cast<Json>();
  Future<List<Json>> exams(int grade, String subject, String search) async =>
      (await client.get<List<dynamic>>(
        '/exams',
        queryParameters: {'grade': grade, 'subject': subject, 'search': search},
      )).data!.cast<Json>();
  Future<Json> start(String id) async =>
      checkedAttempt((await client.post<Json>('/exams/$id/attempts')).data!);
  Future<Json> practiceOptions(int grade, String subject) async =>
      (await client.get<Json>(
        '/practice-options',
        queryParameters: {'grade': grade, 'subject': subject},
      )).data!;
  Future<Json> createPractice(Json filter) async => checkedAttempt(
    (await client.post<Json>('/practice-attempts', data: filter)).data!,
  );
  Future<Json> submit(Json session) async => (await client.post<Json>(
    '/attempts/${session['id']}/submit',
    data: {
      'answers': session['answers'] ?? {},
      if (session['account_id'] != null)
        'draft_revision': session['draft_revision'] ?? 0,
    },
    options: Options(headers: {'X-Attempt-Token': session['token']}),
  )).data!;

  /// Open a new server attempt; keep answers only for identical public questions.
  Future<Json> recover(Json previous) async {
    final examId = previous['exam']?['id'];
    final customFilter = previous['practice_filter'];
    if (customFilter is! Map && (examId is! String || examId.isEmpty)) {
      throw StateError('Bài cũ thiếu mã đề. Hãy chọn lại đề trong Luyện đề.');
    }
    final next = customFilter is Map
        ? await createPractice({
            ...Map<String, dynamic>.from(customFilter),
            'question_ids': [
              for (final q in previous['questions'] as List) q['id'],
            ],
            'count': (previous['questions'] as List).length,
          })
        : await start(examId as String);
    final oldQuestions = {
      for (final q in (previous['questions'] as List).cast<Json>()) q['id']: q,
    };
    final answers = <String, dynamic>{};
    final unchanged = <String>{};
    for (final q in (next['questions'] as List).cast<Json>()) {
      final old = oldQuestions[q['id']];
      if (old != null && _questionSignature(old) == _questionSignature(q)) {
        unchanged.add(q['id'] as String);
        final answer = (previous['answers'] as Map? ?? {})[q['id']];
        if (answer != null) {
          answers[q['id'] as String] = List<String>.from(answer);
        }
      }
    }
    return {
      ...next,
      'backend_url': baseUrl,
      'answers': answers,
      'flags': (previous['flags'] as List? ?? [])
          .where(unchanged.contains)
          .toList(),
      'recovery_notice':
          'Đã khôi phục ${answers.length} câu trả lời. '
          'Câu đã thay đổi không được giữ đáp án cũ; hãy kiểm tra trước khi nộp.',
    };
  }

  String _questionSignature(Json q) => jsonEncode([
    q['question'],
    q['type'],
    q['max_score'],
    q['unit'],
    q['rubric'],
    [
      for (final o in (q['options'] as List? ?? [])) [o['id'], o['text']],
    ],
  ]);

  Future<Json> attemptResult(Json session) async => (await client.get<Json>(
    '/attempts/${session['id']}/result',
    options: Options(headers: {'X-Attempt-Token': session['token']}),
  )).data!;
  Future<void> delete(Json session) async {
    try {
      await client.delete(
        '/attempts/${session['id']}',
        options: Options(headers: {'X-Attempt-Token': session['token']}),
      );
    } on DioException catch (e) {
      // An already deleted/missing token-owned attempt should not lock local history.
      if (e.response?.statusCode != 404) rethrow;
    }
  }
}

String vietnameseSearchKey(String value) {
  var text = value.toLowerCase().replaceAll('đ', 'd');
  const groups = {
    'a': 'àáạảãâầấậẩẫăằắặẳẵ',
    'e': 'èéẹẻẽêềếệểễ',
    'i': 'ìíịỉĩ',
    'o': 'òóọỏõôồốộổỗơờớợởỡ',
    'u': 'ùúụủũưừứựửữ',
    'y': 'ỳýỵỷỹ',
  };
  groups.forEach(
    (key, chars) => text = text.replaceAll(RegExp('[$chars]'), key),
  );
  return text;
}

String validateBackendUrl(String value) {
  if (kIsWeb && value.trim() == '/api') return '/api';
  final uri = Uri.tryParse(value.trim());
  if (uri == null ||
      uri.scheme != 'https' ||
      uri.host.isEmpty ||
      uri.userInfo.isNotEmpty ||
      uri.hasQuery ||
      uri.hasFragment ||
      !['', '/', '/api', '/api/'].contains(uri.path)) {
    throw const FormatException(
      'Nhập địa chỉ HTTPS của máy chủ (có thể kết thúc bằng /api), không kèm mật khẩu.',
    );
  }
  return uri
      .replace(path: uri.path.startsWith('/api') ? '/api' : '')
      .toString();
}

final backendUrlProvider = StateProvider<String?>((ref) => null);
final Provider<LearningApi> apiProvider = Provider<LearningApi>((ref) {
  final api = LearningApi(baseUrl: ref.watch(backendUrlProvider));
  api.onSessionLost = () => ref.invalidate(authBootstrapProvider);
  api.client.interceptors.add(
    InterceptorsWrapper(
      onError: (error, handler) {
        if (error.response?.statusCode == 401 &&
            !['/auth/me', '/auth/login'].contains(error.requestOptions.path)) {
          ref.invalidate(authBootstrapProvider);
        }
        handler.next(error);
      },
    ),
  );
  return api;
});
final preferencesProvider = FutureProvider<SharedPreferences>(
  (ref) => SharedPreferences.getInstance(),
);
final subjectsProvider = FutureProvider.family<List<Json>, int>(
  (ref, grade) => ref.watch(apiProvider).subjects(grade),
);
final examsProvider =
    FutureProvider.family<
      List<Json>,
      ({int grade, String subject, String search})
    >(
      (ref, filter) => ref
          .watch(apiProvider)
          .exams(filter.grade, filter.subject, filter.search),
    );

final authUserProvider = StateProvider<Json?>((ref) => null);
final FutureProvider<Json?> authBootstrapProvider = FutureProvider<Json?>((
  ref,
) async {
  final api = ref.watch(apiProvider);
  final prefs = await ref.watch(preferencesProvider.future);
  Json? user;
  try {
    user = await api.currentUser();
  } catch (_) {
    if (prefs.getString('active_account_id') != null) rethrow;
  }
  if (user == null) {
    await prefs.remove('active_account_id');
  } else {
    await prefs.setString('active_account_id', user['id']);
  }
  api.expectedAccountId = user?['id'] as String?;
  ref.read(authUserProvider.notifier).state = user;
  return user;
});

class LocalStore {
  LocalStore(this.preferences);
  final SharedPreferences preferences;
  String get _suffix => preferences.getString('active_account_id') == null
      ? ''
      : '.${preferences.getString('active_account_id')}';
  String get _currentKey => 'current_attempt$_suffix';
  String get _historyKey => 'history$_suffix';
  Json? get current {
    final value = preferences.getString(_currentKey);
    return value == null ? null : jsonDecode(value) as Json;
  }

  List<Json> get history =>
      (jsonDecode(preferences.getString(_historyKey) ?? '[]') as List)
          .cast<Json>();
  Future<void> save(Json session) async {
    if (session['account_id'] != preferences.getString('active_account_id')) {
      throw StateError(
        'Tài khoản đã thay đổi. Hãy đăng nhập lại trước khi làm bài.',
      );
    }
    if (!await preferences.setString(_currentKey, jsonEncode(session))) {
      throw StateError('Không thể lưu bài làm trên thiết bị.');
    }
  }

  Future<void> complete(Json session, Json result) async {
    final records = history.where((h) => h['id'] != session['id']).toList();
    records.insert(0, {...session, 'result': result});
    if (!await preferences.setString(_historyKey, jsonEncode(records))) {
      throw StateError('Không thể lưu kết quả.');
    }
    await preferences.remove(_currentKey);
  }

  Future<void> removeHistory(String id) async {
    await preferences.setString(
      _historyKey,
      jsonEncode(history.where((h) => h['id'] != id).toList()),
    );
  }
}
