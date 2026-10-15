import 'dart:convert';
import 'offline_repository.dart';
import 'secure_session_store.dart';
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

typedef Json = Map<String, dynamic>;

class LearningApi {
  LearningApi({Dio? client, String? baseUrl, this.sessionStore})
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
          ) {
    _sessionScope = nativeSessionScope(this.client.options.baseUrl);
    if (hasPersistentSession) {
      this.client.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) async {
            try {
              await restoreSession();
              if (_disposed) throw StateError('Phiên kết nối đã thay đổi.');
              final scope = Uri.parse(_sessionScope!);
              final target = options.uri;
              final withinBackend =
                  target.scheme == scope.scheme &&
                  target.host.toLowerCase() == scope.host &&
                  target.port == scope.port &&
                  (scope.path.isEmpty ||
                      target.path == scope.path ||
                      target.path.startsWith('${scope.path}/'));
              final login = const {
                '/auth/login',
                '/auth/register',
              }.contains(options.path);
              final token = withinBackend && !login ? _bearerToken : null;
              options.headers.removeWhere(
                (key, _) => key.toLowerCase() == 'authorization',
              );
              if (token != null) {
                options.headers['Authorization'] = 'Bearer $token';
                _requestTokens[options] = token;
              }
              _requestGenerations[options] = _sessionGeneration;
              // Never forward a password or bearer token through a redirect.
              if (token != null ||
                  options.path.startsWith('/auth/') ||
                  options.path == '/account/delete') {
                options.followRedirects = false;
              }
              handler.next(options);
            } catch (_) {
              handler.reject(
                DioException(
                  requestOptions: options,
                  error: const SecureSessionStorageException(),
                  message: const SecureSessionStorageException().toString(),
                ),
              );
            }
          },
          onError: (error, handler) async {
            if (error.response?.statusCode == 401 &&
                !const {
                  '/auth/login',
                  '/auth/register',
                }.contains(error.requestOptions.path)) {
              final token = _requestTokens[error.requestOptions];
              try {
                if (token != null) await _clearSessionIfToken(token);
                if (!_disposed &&
                    error.requestOptions.path != '/auth/me' &&
                    _requestGenerations[error.requestOptions] ==
                        _sessionGeneration &&
                    _bearerToken == null) {
                  onSessionLost?.call();
                }
              } catch (_) {
                handler.reject(
                  DioException(
                    requestOptions: error.requestOptions,
                    error: const SecureSessionStorageException(),
                    message: const SecureSessionStorageException().toString(),
                  ),
                );
                return;
              }
            }
            handler.next(error);
          },
        ),
      );
    }
  }
  final Dio client;
  final SecureSessionStore? sessionStore;
  String? _sessionScope;
  Future<void>? _restoration;
  var _sessionGeneration = 0;
  var _disposed = false;
  final _requestTokens = Expando<String>();
  final _requestGenerations = Expando<int>();
  bool get hasPersistentSession =>
      sessionStore != null && _sessionScope != null;
  String? get _bearerToken {
    final value = client.options.headers['Authorization'];
    return value is String && value.startsWith('Bearer ')
        ? value.substring(7)
        : null;
  }

  Future<void> restoreSession() {
    if (!hasPersistentSession) return Future<void>.value();
    if (nativeSessionScope(client.options.baseUrl) != _sessionScope) {
      throw StateError('Địa chỉ máy chủ đã thay đổi. Hãy mở lại kết nối.');
    }
    if (_restoration != null) return _restoration!;
    final work = _restoreSession(_sessionGeneration);
    _restoration = work;
    work.then<void>(
      (_) {},
      onError: (Object _, StackTrace __) {
        if (identical(_restoration, work)) _restoration = null;
      },
    );
    return work;
  }

  Future<void> _restoreSession(int generation) async {
    final saved = await sessionStore!.read(_sessionScope!);
    if (_disposed || generation != _sessionGeneration) return;
    if (saved != null) {
      client.options.headers['Authorization'] = 'Bearer ${saved.token}';
      expectedAccountId = saved.accountId;
    }
  }

  Future<void> _clearSessionIfToken(String token) async {
    if (hasPersistentSession) {
      await sessionStore!.clearIfToken(_sessionScope!, token);
    }
    if (_bearerToken == token) {
      client.options.headers.remove('Authorization');
      expectedAccountId = null;
    }
  }

  void dispose() {
    _disposed = true;
    _sessionGeneration++;
    client.options.headers.remove('Authorization');
    expectedAccountId = null;
    client.close(force: true);
  }

  bool get isOffline => false;
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
    await restoreSession();
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
    if (kIsWeb || kReleaseMode || sessionStore != null) {
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
    await restoreSession();
    final generation = ++_sessionGeneration;
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
      if (hasPersistentSession) {
        if (_disposed || generation != _sessionGeneration) {
          throw StateError('Phiên kết nối đã thay đổi. Hãy đăng nhập lại.');
        }
        final saved = await sessionStore!.write(
          _sessionScope!,
          NativeSession(
            token: response['token'] as String,
            accountId: response['user']['id'] as String,
          ),
          isCurrent: () => !_disposed && generation == _sessionGeneration,
        );
        if (!saved || _disposed || generation != _sessionGeneration) {
          throw StateError('Phiên kết nối đã thay đổi. Hãy đăng nhập lại.');
        }
      }
      client.options.headers['Authorization'] = 'Bearer ${response['token']}';
      if (hasPersistentSession) {
        expectedAccountId = response['user']['id'] as String;
      }
    }
    return response['user'] as Json;
  }

  Future<void> deleteAccount(String password) async {
    await restoreSession();
    final token = _bearerToken;
    await client.post('/account/delete', data: {'password': password});
    if (token != null) await _clearSessionIfToken(token);
  }

  Future<void> signOut() async {
    await restoreSession();
    final token = _bearerToken;
    await client.post('/auth/logout');
    if (token != null) await _clearSessionIfToken(token);
  }

  Future<Json> changePassword(String current, String next) async =>
      (await client.post<Json>(
        '/auth/password',
        data: {'current_password': current, 'new_password': next},
      )).data!;
  Future<Json> sendContentReport(Json body) async =>
      (await client.post<Json>('/content-reports', data: body)).data!;
  Future<List<Json>> contentReports({
    bool review = false,
    String? status,
    int offset = 0,
  }) async => (await client.get<List<dynamic>>(
    review ? '/classroom/content-reports' : '/content-reports',
    queryParameters: {
      if (status != null) 'status': status,
      'offset': offset,
      'limit': 30,
    },
  )).data!.cast<Json>();
  Future<Json> reviewContentReport(String id, Json body) async =>
      (await client.post<Json>(
        '/classroom/content-reports/$id/review',
        data: body,
      )).data!;
  Future<List<Json>> classroomGroups() async =>
      (await client.get<List<dynamic>>('/classroom/groups')).data!.cast<Json>();
  Future<List<Json>> accountAssignments({int offset = 0}) async =>
      (await client.get<List<dynamic>>(
        '/account/assignments',
        queryParameters: {'offset': offset, 'limit': 30},
      )).data!.cast<Json>();
  Future<List<Json>> groupAssignments(String id, {int offset = 0}) async =>
      (await client.get<List<dynamic>>(
        '/classroom/groups/$id/assignments',
        queryParameters: {'offset': offset, 'limit': 30},
      )).data!.cast<Json>();
  Future<Json> assignGroupExam(String groupId, String examId) async =>
      (await client.post<Json>(
        '/classroom/groups/$groupId/assignments',
        data: {'exam_id': examId},
      )).data!;
  Future<Json> groupAssignmentProgress(String groupId, String examId) async =>
      (await client.get<Json>(
        '/classroom/groups/$groupId/assignments/$examId',
      )).data!;
  Future<String> groupAssignmentCsv(String groupId, String examId) async =>
      (await client.get<String>(
        '/classroom/groups/$groupId/assignments/$examId/results.csv',
        options: Options(responseType: ResponseType.plain),
      )).data!;
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
    requireServerAttempt(session);
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
  void requireServerAttempt(Json session) {
    if (session['local_self_practice'] == true ||
        (session['id'] as String? ?? '').startsWith('offline_') ||
        (session['backend_url'] as String? ?? '').startsWith('offline://')) {
      throw StateError(
        'Bài tự luyện ngoại tuyến chỉ được mở trong chế độ ngoại tuyến.',
      );
    }
    final source = session['backend_url'];
    if (source != null && source != baseUrl) {
      throw StateError(
        'Bài làm thuộc máy chủ khác. Hãy kết nối lại đúng máy chủ.',
      );
    }
  }

  Future<Json> submit(Json session) async {
    requireServerAttempt(session);
    return (await client.post<Json>(
      '/attempts/${session['id']}/submit',
      data: {
        'answers': session['answers'] ?? {},
        if (session['account_id'] != null)
          'draft_revision': session['draft_revision'] ?? 0,
      },
      options: Options(headers: {'X-Attempt-Token': session['token']}),
    )).data!;
  }

  /// Open a new server attempt; keep answers only for identical public questions.
  Future<Json> recover(Json previous) async {
    requireServerAttempt(previous);
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

  Future<Json> attemptResult(Json session) async {
    requireServerAttempt(session);
    return (await client.get<Json>(
      '/attempts/${session['id']}/result',
      options: Options(headers: {'X-Attempt-Token': session['token']}),
    )).data!;
  }

  Future<void> delete(Json session) async {
    requireServerAttempt(session);
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

/// Tests and existing online callers stay online unless the application startup
/// selects the bundled native default or a saved explicit choice.
final studyOfflineProvider = StateProvider<bool>((ref) => false);

bool initialStudyOffline(
  SharedPreferences preferences, {
  bool? web,
  String? configuredBackend,
}) {
  final saved = preferences.getBool('study_offline');
  if (saved != null) return saved;
  if (web ?? kIsWeb) return false;
  final address =
      preferences.getString('backend_url') ??
      configuredBackend ??
      const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://10.0.2.2:8000',
      );
  final uri = Uri.tryParse(address);
  return uri == null ||
      uri.scheme != 'https' ||
      uri.host.isEmpty ||
      uri.host.endsWith('.invalid') ||
      uri.host == 'localhost';
}

Future<bool> initializeStudyOffline(SharedPreferences preferences) async {
  final offline = initialStudyOffline(preferences);
  if (preferences.getBool('study_offline') == null &&
      !await preferences.setBool('study_offline', offline)) {
    throw StateError('Chưa lưu được chế độ học trên thiết bị.');
  }
  return offline;
}

Future<void> changeStudyMode(WidgetRef ref, bool offline) async {
  final preferences = await ref.read(preferencesProvider.future);
  if (!await preferences.setBool('study_offline', offline)) {
    throw StateError('Chưa lưu được chế độ học. Dữ liệu cũ vẫn được giữ.');
  }
  ref.read(authUserProvider.notifier).state = null;
  ref.read(studyOfflineProvider.notifier).state = offline;
  ref.invalidate(authBootstrapProvider);
}

final backendUrlProvider = StateProvider<String?>((ref) => null);
final secureSessionStoreProvider = Provider<SecureSessionStore?>(
  (ref) => nativeSecureSessionStore(),
);
final Provider<LearningApi> apiProvider = Provider<LearningApi>((ref) {
  if (ref.watch(studyOfflineProvider)) {
    final preferences = ref.read(preferencesProvider.future);
    final local = OfflineLearningApi(preferences: () => preferences);
    ref.onDispose(local.dispose);
    return local;
  }
  final api = LearningApi(
    baseUrl: ref.watch(backendUrlProvider),
    sessionStore: ref.watch(secureSessionStoreProvider),
  );
  var disposed = false;
  ref.onDispose(() {
    disposed = true;
    api.dispose();
  });
  api.onSessionLost = () {
    if (!disposed) ref.invalidate(authBootstrapProvider);
  };
  api.client.interceptors.add(
    InterceptorsWrapper(
      onError: (error, handler) {
        if (!disposed &&
            !api.hasPersistentSession &&
            error.response?.statusCode == 401 &&
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
  var discarded = false;
  ref.onDispose(() => discarded = true);
  final api = ref.watch(apiProvider);
  final prefs = await ref.watch(preferencesProvider.future);
  if (discarded) return null;
  if (api.isOffline) {
    api.expectedAccountId = null;
    ref.read(authUserProvider.notifier).state = null;
    return null;
  }
  Json? user;
  try {
    user = await api.currentUser();
  } catch (error) {
    if (discarded) return null;
    if (error is SecureSessionStorageException ||
        (error is DioException &&
            error.error is SecureSessionStorageException)) {
      rethrow;
    }
    if (prefs.getString('active_account_id') != null) rethrow;
  }
  if (discarded) return null;
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
  LocalStore(this.preferences, {bool? offline})
    : _offlineOverride = offline,
      offline = offline ?? preferences.getBool('study_offline') ?? false,
      accountId = preferences.getString('active_account_id');
  final SharedPreferences preferences;
  final bool? _offlineOverride;
  final bool offline;
  final String? accountId;
  String get _suffix => offline
      ? '.offline'
      : accountId == null
      ? ''
      : '.$accountId';
  String get _currentKey => 'current_attempt$_suffix';
  String get _historyKey => 'history$_suffix';
  String get _readSuffix {
    final local =
        _offlineOverride ?? preferences.getBool('study_offline') ?? false;
    final active = preferences.getString('active_account_id');
    return local
        ? '.offline'
        : active == null
        ? ''
        : '.$active';
  }

  void _checkScope() {
    if ((preferences.getBool('study_offline') ?? false) != offline ||
        (!offline && preferences.getString('active_account_id') != accountId)) {
      throw StateError(
        'Chế độ học hoặc tài khoản đã thay đổi. Hãy mở lại bài đang làm.',
      );
    }
  }

  void _checkSession(Json session) {
    _checkScope();
    final isLocal =
        session['local_self_practice'] == true ||
        (session['id'] as String? ?? '').startsWith('offline_') ||
        (session['backend_url'] as String? ?? '').startsWith('offline://');
    if (isLocal != offline ||
        session['account_id'] != (offline ? null : accountId)) {
      throw StateError(
        'Bài làm thuộc chế độ học hoặc tài khoản khác. Dữ liệu cũ vẫn được giữ.',
      );
    }
  }

  Json? get current {
    final value = preferences.getString('current_attempt$_readSuffix');
    return value == null ? null : jsonDecode(value) as Json;
  }

  List<Json> get history =>
      (jsonDecode(preferences.getString('history$_readSuffix') ?? '[]') as List)
          .cast<Json>();

  Future<void> save(Json session) async {
    _checkSession(session);
    if (!await preferences.setString(_currentKey, jsonEncode(session))) {
      throw StateError('Không thể lưu bài làm trên thiết bị.');
    }
  }

  Future<void> complete(Json session, Json result) async {
    _checkSession(session);
    if (result['attempt_id'] != session['id']) {
      throw StateError('Kết quả không thuộc bài đang làm.');
    }
    final records = history.where((h) => h['id'] != session['id']).toList();
    records.insert(0, {...session, 'result': result});
    if (!await preferences.setString(_historyKey, jsonEncode(records))) {
      throw StateError('Không thể lưu kết quả.');
    }
    _checkScope();
    await preferences.remove(_currentKey);
  }

  Future<void> removeHistory(String id) async {
    _checkScope();
    if (!await preferences.setString(
      _historyKey,
      jsonEncode(history.where((h) => h['id'] != id).toList()),
    )) {
      throw StateError('Chưa xóa được kết quả trên thiết bị.');
    }
  }
}
