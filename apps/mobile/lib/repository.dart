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
  String get baseUrl => client.options.baseUrl;
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
      (await client.post<Json>('/exams/$id/attempts')).data!;
  Future<Json> submit(Json session) async => (await client.post<Json>(
    '/attempts/${session['id']}/submit',
    data: {'answers': session['answers'] ?? {}},
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

String validateBackendUrl(String value) {
  if (kIsWeb && value.trim() == '/api') return '/api';
  final uri = Uri.tryParse(value.trim());
  if (uri == null ||
      uri.scheme != 'https' ||
      uri.host.isEmpty ||
      uri.userInfo.isNotEmpty ||
      uri.hasQuery ||
      uri.hasFragment ||
      (uri.path.isNotEmpty && uri.path != '/')) {
    throw const FormatException(
      'Nhập địa chỉ HTTPS của máy chủ, không kèm đường dẫn hoặc mật khẩu.',
    );
  }
  return uri.replace(path: '').toString();
}

final backendUrlProvider = StateProvider<String?>((ref) => null);
final apiProvider = Provider<LearningApi>(
  (ref) => LearningApi(baseUrl: ref.watch(backendUrlProvider)),
);
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

class LocalStore {
  LocalStore(this.preferences);
  final SharedPreferences preferences;
  Json? get current {
    final value = preferences.getString('current_attempt');
    return value == null ? null : jsonDecode(value) as Json;
  }

  List<Json> get history =>
      (jsonDecode(preferences.getString('history') ?? '[]') as List)
          .cast<Json>();
  Future<void> save(Json session) async {
    if (!await preferences.setString('current_attempt', jsonEncode(session))) {
      throw StateError('Không thể lưu bài làm trên thiết bị.');
    }
  }

  Future<void> complete(Json session, Json result) async {
    final records = history.where((h) => h['id'] != session['id']).toList();
    records.insert(0, {...session, 'result': result});
    if (!await preferences.setString('history', jsonEncode(records))) {
      throw StateError('Không thể lưu kết quả.');
    }
    await preferences.remove('current_attempt');
  }

  Future<void> removeHistory(String id) async {
    await preferences.setString(
      'history',
      jsonEncode(history.where((h) => h['id'] != id).toList()),
    );
  }
}
