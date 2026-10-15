import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'repository.dart';
import 'library_screen.dart';
import 'create_practice_screen.dart';
import 'progress_screen.dart';
import 'account_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final preferences = await SharedPreferences.getInstance();
  LicenseRegistry.addLicense(() async* {
    yield LicenseEntryWithLineBreaks([
      'Noto Sans',
    ], await rootBundle.loadString('assets/fonts/OFL.txt'));
    yield LicenseEntryWithLineBreaks([
      'Roboto',
    ], await rootBundle.loadString('assets/fonts/Roboto-OFL.txt'));
  });
  runApp(
    ProviderScope(
      overrides: [
        backendUrlProvider.overrideWith(
          (ref) => preferences.getString('backend_url'),
        ),
      ],
      child: const KhoHocApp(),
    ),
  );
}

final darkProvider = StateProvider<bool>((ref) => false);
final routerProvider = Provider<GoRouter>(
  (ref) => GoRouter(
    redirect: (_, state) {
      final user = ref.read(authUserProvider);
      if (state.uri.path == '/classroom' && user?['role'] != 'manager') {
        return '/account';
      }
      if (user?['must_change_password'] == true &&
          state.uri.path != '/account') {
        return '/account';
      }
      return null;
    },
    routes: [
      GoRoute(path: '/', builder: (_, _) => const HomeScreen()),
      GoRoute(path: '/practice', builder: (_, _) => const PracticeScreen()),
      GoRoute(
        path: '/create-practice',
        builder: (_, _) => const CreatePracticeScreen(),
      ),
      GoRoute(path: '/exams', builder: (_, _) => const HomeScreen(index: 2)),
      GoRoute(
        path: '/source-exams',
        builder: (_, state) => LibraryScreen(
          examMode: true,
          initialGrade:
              (int.tryParse(state.uri.queryParameters['grade'] ?? '') ?? 1)
                  .clamp(1, 12),
          initialSubject: state.uri.queryParameters['subject'] ?? 'toan',
        ),
      ),
      GoRoute(path: '/documents', builder: (_, _) => const LibraryScreen()),
      GoRoute(path: '/progress', builder: (_, _) => const ProgressScreen()),
      GoRoute(path: '/history', builder: (_, _) => const HistoryScreen()),
      GoRoute(path: '/settings', builder: (_, _) => const SettingsScreen()),
      GoRoute(path: '/account', builder: (_, _) => const AccountScreen()),
      GoRoute(path: '/classroom', builder: (_, _) => const ClassroomScreen()),
    ],
  ),
);

class KhoHocApp extends ConsumerWidget {
  const KhoHocApp({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authBootstrapProvider);
    if (auth.isLoading) {
      return const MaterialApp(
        home: Scaffold(body: Center(child: CircularProgressIndicator())),
      );
    }
    if (auth.hasError) {
      return MaterialApp(
        home: Scaffold(
          body: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Chưa xác thực được tài khoản. Kiểm tra máy chủ rồi thử lại.',
                ),
                FilledButton(
                  onPressed: () => ref.invalidate(authBootstrapProvider),
                  child: const Text('Thử lại'),
                ),
              ],
            ),
          ),
        ),
      );
    }
    return MaterialApp.router(
      title: 'Kho Học 1–12',
      debugShowCheckedModeBanner: false,
      locale: const Locale('vi'),
      supportedLocales: const [Locale('vi')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      theme: ThemeData(
        fontFamily: 'NotoSans',
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff2563c7)),
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        fontFamily: 'NotoSans',
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xff2563c7),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
      ),
      themeMode: ref.watch(darkProvider) ? ThemeMode.dark : ThemeMode.light,
      routerConfig: ref.watch(routerProvider),
    );
  }
}

class Shell extends StatelessWidget {
  const Shell({
    super.key,
    required this.title,
    required this.child,
    this.index = 0,
  });
  final String title;
  final Widget child;
  final int index;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text(title)),
    body: SafeArea(child: child),
    bottomNavigationBar: NavigationBar(
      selectedIndex: index,
      onDestinationSelected: (n) => context.go(
        ['/', '/documents', '/exams', '/progress', '/settings'][n],
      ),
      destinations: const [
        NavigationDestination(
          icon: Icon(Icons.school_outlined),
          label: 'Trang chủ',
        ),
        NavigationDestination(
          icon: Icon(Icons.menu_book_outlined),
          label: 'Tài liệu',
        ),
        NavigationDestination(icon: Icon(Icons.edit_note), label: 'Luyện đề'),
        NavigationDestination(icon: Icon(Icons.insights), label: 'Tiến độ'),
        NavigationDestination(
          icon: Icon(Icons.person_outline),
          label: 'Cá nhân',
        ),
      ],
    ),
  );
}

class Failure extends StatelessWidget {
  const Failure({
    super.key,
    required this.retry,
    this.message = 'Không thể tải dữ liệu. Kiểm tra kết nối rồi thử lại.',
  });
  final VoidCallback retry;
  final String message;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(24),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(message),
        const SizedBox(height: 16),
        FilledButton(onPressed: retry, child: const Text('Thử lại')),
        TextButton(
          onPressed: () => context.go('/settings'),
          child: const Text('Kiểm tra địa chỉ máy chủ'),
        ),
      ],
    ),
  );
}

final coverageProvider = FutureProvider.family<List<Json>, int>(
  (ref, grade) => ref.watch(apiProvider).coverage(grade),
);

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key, this.index = 0});
  final int index;
  @override
  ConsumerState<HomeScreen> createState() => _HomeState();
}

class _HomeState extends ConsumerState<HomeScreen> {
  int grade = 1;
  String subject = 'toan', search = '';
  bool starting = false;
  String? error;
  @override
  Widget build(BuildContext context) {
    final subjects = ref.watch(subjectsProvider(grade));
    final filter = (grade: grade, subject: subject, search: search);
    final exams = ref.watch(examsProvider(filter));
    final coverage = ref.watch(coverageProvider(grade));
    final prefs = ref.watch(preferencesProvider);
    return Shell(
      title: widget.index == 2 ? 'Luyện đề' : 'Kho Học 1–12',
      index: widget.index,
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            'Học từng chút, tiến bộ mỗi ngày',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          const Text('Chọn lớp và môn để luyện tập. Không cần tài khoản.'),
          const Text('Bản thử 2026.10.15.9'),
          if (widget.index == 2)
            Card(
              child: ListTile(
                leading: const Icon(Icons.public),
                title: const Text(
                  'Đề giữa kỳ, cuối kỳ và tốt nghiệp từ Internet',
                ),
                subtitle: const Text(
                  'Lọc theo lớp, môn, đợt kiểm tra và năm đề',
                ),
                onTap: () => context.go(
                  Uri(
                    path: '/source-exams',
                    queryParameters: {'grade': '$grade', 'subject': subject},
                  ).toString(),
                ),
              ),
            ),
          if (widget.index == 2)
            Card(
              child: ListTile(
                leading: const Icon(Icons.shuffle),
                title: const Text('Tạo đề theo chủ đề và độ khó'),
                subtitle: const Text(
                  'Tối đa 50 câu, chọn ngẫu nhiên từ ngân hàng hiện có',
                ),
                onTap: () => context.go('/create-practice'),
              ),
            ),
          const SizedBox(height: 20),
          prefs.when(
            data: (p) => LocalStore(p).current == null
                ? const SizedBox.shrink()
                : Card(
                    child: ListTile(
                      leading: const Icon(Icons.restore),
                      title: const Text('Tiếp tục bài đang làm'),
                      subtitle: const Text('Bài làm đã lưu trên thiết bị'),
                      onTap: () => context.go('/practice'),
                    ),
                  ),
            loading: () => const SizedBox.shrink(),
            error: (_, _) => const Text('Không đọc được bộ nhớ cục bộ.'),
          ),
          DropdownButtonFormField<int>(
            initialValue: grade,
            decoration: const InputDecoration(
              labelText: 'Lớp học',
              border: OutlineInputBorder(),
            ),
            items: [
              for (int n = 1; n <= 12; n++)
                DropdownMenuItem(value: n, child: Text('Lớp $n')),
            ],
            onChanged: starting
                ? null
                : (n) => setState(() {
                    grade = n!;
                    subject = 'toan';
                  }),
          ),
          const SizedBox(height: 16),
          subjects.when(
            data: (list) => DropdownButtonFormField<String>(
              key: ValueKey(grade),
              initialValue: subject,
              decoration: const InputDecoration(
                labelText: 'Môn học',
                border: OutlineInputBorder(),
              ),
              items: list
                  .map(
                    (s) => DropdownMenuItem(
                      value: s['id'] as String,
                      child: Text(s['name'] as String),
                    ),
                  )
                  .toList(),
              onChanged: starting ? null : (v) => setState(() => subject = v!),
            ),
            loading: () => const LinearProgressIndicator(),
            error: (_, _) =>
                Failure(retry: () => ref.invalidate(subjectsProvider(grade))),
          ),
          const SizedBox(height: 16),
          TextField(
            decoration: const InputDecoration(
              labelText: 'Tìm tên đề',
              prefixIcon: Icon(Icons.search),
              border: OutlineInputBorder(),
            ),
            onSubmitted: (v) => setState(() => search = v.trim()),
          ),
          const SizedBox(height: 24),
          Text(
            'Bộ đề luyện tập',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const Text(
            'Nội dung tự biên soạn hướng tới Kết nối tri thức. Chưa đối chiếu từng bài SGK; các môn ngoài Toán hiện là bộ ôn kiến thức nền.',
          ),
          coverage.when(
            data: (rows) {
              final selected = rows.where((row) => row['subject'] == subject);
              if (selected.isEmpty) return const SizedBox.shrink();
              final row = selected.first;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Text(
                  '${row["question_count"]} câu · ${row["exam_count"]} đề làm trực tiếp · ${row["external_paper_count"] ?? 0} đề từ nguồn Internet',
                ),
              );
            },
            loading: () => const SizedBox.shrink(),
            error: (error, stack) =>
                const Text('Chưa tải được thống kê dữ liệu.'),
          ),
          if (error != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Text(
                error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            ),
          exams.when(
            data: (list) => list.isEmpty
                ? const Padding(
                    padding: EdgeInsets.all(24),
                    child: Text('Chưa có đề được duyệt cho lớp/môn này.'),
                  )
                : Column(
                    children: list
                        .map(
                          (exam) => Card(
                            child: ListTile(
                              title: Text(exam['title']),
                              subtitle: Text(
                                "${exam['question_count']} câu · ${exam['duration_minutes']} phút luyện tập",
                              ),
                              trailing: starting
                                  ? const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : const Icon(Icons.arrow_forward),
                              onTap: starting ? null : () => start(exam['id']),
                            ),
                          ),
                        )
                        .toList(),
                  ),
            loading: () => const Padding(
              padding: EdgeInsets.all(24),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (_, _) =>
                Failure(retry: () => ref.invalidate(examsProvider(filter))),
          ),
        ],
      ),
    );
  }

  Future<void> start(String id) async {
    setState(() {
      starting = true;
      error = null;
    });
    try {
      final p = await ref.read(preferencesProvider.future);
      if (LocalStore(p).current != null) {
        if (mounted) context.go('/practice');
        return;
      }
      final attempt = await ref.read(apiProvider).start(id);
      await LocalStore(p).save({
        ...attempt,
        'backend_url': ref.read(apiProvider).baseUrl,
        'answers': <String, List<String>>{},
      });
      if (mounted) context.go('/practice');
    } catch (_) {
      if (mounted) {
        setState(
          () => error =
              'Không thể bắt đầu bài. Kiểm tra mạng và bộ nhớ thiết bị.',
        );
      }
    } finally {
      if (mounted) setState(() => starting = false);
    }
  }
}

class PracticeScreen extends ConsumerStatefulWidget {
  const PracticeScreen({super.key});
  @override
  ConsumerState<PracticeScreen> createState() => _PracticeState();
}

class _PracticeState extends ConsumerState<PracticeScreen> {
  Json? session, result;
  int index = 0;
  bool busy = false;
  bool recoveryAvailable = false;
  String? error;
  Timer? timer;
  int remaining = 0;
  Future<void> pendingSave = Future.value();
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final p = await ref.read(preferencesProvider.future);
      final s = LocalStore(p).current;
      if (!mounted) return;
      setState(() {
        session = s;
        if (s != null &&
            DateTime.now()
                    .toUtc()
                    .difference(DateTime.parse(s['created_at']))
                    .inHours >=
                24) {
          recoveryAvailable = true;
          error =
              'Bài lưu đã quá 24 giờ. Khôi phục phiên làm bài để tiếp tục nộp; câu trả lời vẫn được giữ.';
        }
      });
      if (s != null) {
        void tick() {
          if (!mounted) return;
          final start = DateTime.parse(s['created_at']);
          setState(
            () => remaining =
                (start
                        .add(Duration(minutes: s['exam']['duration_minutes']))
                        .difference(DateTime.now())
                        .inSeconds)
                    .clamp(0, 10800),
          );
        }

        tick();
        timer = Timer.periodic(const Duration(seconds: 1), (_) => tick());
      }
    } catch (_) {
      if (mounted) setState(() => error = 'Không đọc được bài đã lưu.');
    }
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  void answer(Json q, List<String> values) {
    setState(() {
      session!['answers'] = <String, dynamic>{
        ...Map<String, dynamic>.from(session!['answers'] as Map),
        q['id']: values,
      };
      error = null;
    });
    saveCurrent();
  }

  void toggleFlag(String id) {
    final flags = List<String>.from(session!['flags'] as List? ?? []);
    if (flags.contains(id)) {
      flags.remove(id);
    } else {
      flags.add(id);
    }
    setState(() => session!['flags'] = flags);
    saveCurrent();
  }

  void saveCurrent() {
    final snapshot = <String, dynamic>{
      ...session!,
      'answers': <String, dynamic>{
        ...Map<String, dynamic>.from(session!['answers'] as Map),
      },
    };
    pendingSave = pendingSave
        .then((_) async {
          final p = await ref.read(preferencesProvider.future);
          await LocalStore(p).save(snapshot);
        })
        .catchError((Object e) {
          if (mounted) {
            setState(
              () => error =
                  'Chưa lưu được bài trên thiết bị. Hãy thử lại trước khi rời màn hình.',
            );
          }
        });
  }

  Future<void> recover() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Khôi phục bài đã lưu?'),
        content: const Text(
          'Tạo phiên làm bài mới và giữ câu trả lời cho những câu hỏi không thay đổi. Những câu đã sửa cần làm lại. Bạn sẽ xem lại bài trước khi nộp.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Khôi phục'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    setState(() => busy = true);
    try {
      await pendingSave;
      final next = await ref.read(apiProvider).recover(session!);
      final p = await ref.read(preferencesProvider.future);
      await LocalStore(p).save(next);
      timer?.cancel();
      if (!mounted) return;
      setState(() {
        session = next;
        index = 0;
        recoveryAvailable = false;
        error = null;
      });
      await load();
    } catch (_) {
      if (mounted) {
        setState(
          () => error =
              'Chưa khôi phục được. Kiểm tra kết nối và xem đề gốc còn có trong Luyện đề không. Bài cũ vẫn được giữ.',
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> submit() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Nộp bài?'),
        content: const Text(
          'Câu chưa trả lời được tính là bỏ trống. Sau khi nộp không thể sửa bài này.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Làm tiếp'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Nộp bài'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await pendingSave;
      final savedPreferences = await ref.read(preferencesProvider.future);
      await LocalStore(savedPreferences).save(session!);
      final r = await ref.read(apiProvider).submit(session!);
      final p = await ref.read(preferencesProvider.future);
      await LocalStore(p).complete(session!, r);
      timer?.cancel();
      if (mounted) setState(() => result = r);
    } on DioException catch (e) {
      if (e.response?.statusCode == 409) {
        try {
          final saved = await ref.read(apiProvider).attemptResult(session!);
          final prefs = await ref.read(preferencesProvider.future);
          final submitted = <String, dynamic>{
            for (final d in saved['details'] as List)
              if (d['submitted_answer'] != null)
                d['question_id'] as String: d['submitted_answer'],
          };
          await LocalStore(
            prefs,
          ).complete({...session!, 'answers': submitted}, saved);
          timer?.cancel();
          if (mounted) {
            setState(
              () => result = {
                ...saved,
                'notice':
                    'Đã khôi phục kết quả nộp trước đó. Các chỉnh sửa sau khi nộp không thay đổi điểm.',
              },
            );
          }
          return;
        } catch (_) {
          if (mounted) {
            setState(
              () => error =
                  'Chưa lấy được kết quả đã nộp. Bài vẫn được giữ; hãy kết nối lại rồi thử.',
            );
          }
          return;
        }
      }
      if (mounted) {
        setState(() {
          recoveryAvailable = [404, 410].contains(e.response?.statusCode);
          error = recoveryAvailable
              ? 'Phiên làm bài đã hết hạn hoặc không còn trên máy chủ của bản demo này. Nhấn Khôi phục bài đã lưu để giữ câu trả lời và nộp lại.'
              : e.response?.statusCode == 409
              ? 'Bài này đã nộp với câu trả lời khác. Hãy xem kết quả trong Tiến độ.'
              : 'Chưa nộp được bài. Câu trả lời vẫn được giữ; kiểm tra kết nối rồi thử lại.';
        });
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => error =
              'Chưa nộp được bài. Câu trả lời vẫn được giữ; kiểm tra kết nối rồi thử lại.',
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (result != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Kết quả luyện tập')),
        body: ResultView(result: result!),
      );
    }
    if (session == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Bài luyện tập')),
        body: Center(
          child: Failure(
            message: error ?? 'Chưa có bài đang làm.',
            retry: () => context.go('/'),
          ),
        ),
      );
    }
    final questions = (session!['questions'] as List).cast<Json>();
    final q = questions[index];
    final answers = (session!['answers'] as Map);
    final values = (answers[q['id']] as List? ?? []).cast<String>();
    final flags = List<String>.from(session!['flags'] as List? ?? []);
    return Scaffold(
      appBar: AppBar(title: Text(session!['exam']['title'])),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Câu ${index + 1}/${questions.length}'),
                Text(
                  'Ôn tập · ${remaining ~/ 60}:${(remaining % 60).toString().padLeft(2, '0')}',
                ),
              ],
            ),
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton.icon(
                onPressed: busy ? null : () => toggleFlag(q['id']),
                icon: Icon(
                  flags.contains(q['id']) ? Icons.flag : Icons.outlined_flag,
                ),
                label: Text(
                  flags.contains(q['id']) ? 'Bỏ đánh dấu' : 'Đánh dấu xem lại',
                ),
              ),
            ),
            const SizedBox(height: 10),
            LinearProgressIndicator(value: (index + 1) / questions.length),
            const SizedBox(height: 24),
            Text(q['question'], style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 20),
            if (q['type'] == 'single_choice' || q['type'] == 'multiple_choice')
              ...[
                (q['options'] as List).map((option) {
                  final o = option as Json;
                  return Card(
                    child: CheckboxListTile(
                      title: Text(o['text']),
                      value: values.contains(o['id']),
                      onChanged: busy
                          ? null
                          : (checked) {
                              final next = q['type'] == 'single_choice'
                                  ? <String>[o['id']]
                                  : [...values];
                              if (q['type'] == 'multiple_choice') {
                                checked == true
                                    ? next.add(o['id'])
                                    : next.remove(o['id']);
                              }
                              answer(q, next);
                            },
                    ),
                  );
                }),
              ].expand((v) => v),
            if (q['type'] == 'true_false')
              ...[
                (q['options'] as List).asMap().entries.map((e) {
                  final option = e.value as Json;
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(option['text']),
                          const SizedBox(height: 8),
                          SegmentedButton<String>(
                            segments: const [
                              ButtonSegment(value: 'true', label: Text('Đúng')),
                              ButtonSegment(value: 'false', label: Text('Sai')),
                            ],
                            emptySelectionAllowed: true,
                            selected:
                                values.length > e.key &&
                                    values[e.key].isNotEmpty
                                ? {values[e.key]}
                                : <String>{},
                            onSelectionChanged: busy
                                ? null
                                : (selected) {
                                    final next = List<String>.generate(
                                      (q['options'] as List).length,
                                      (n) => n < values.length ? values[n] : '',
                                    );
                                    next[e.key] = selected.isEmpty
                                        ? ''
                                        : selected.first;
                                    answer(q, next);
                                  },
                          ),
                        ],
                      ),
                    ),
                  );
                }),
              ].expand((v) => v),
            if (['numeric', 'short_answer', 'essay'].contains(q['type']))
              TextFormField(
                key: ValueKey(q['id']),
                initialValue: values.isEmpty ? '' : values.first,
                enabled: !busy,
                maxLines: q['type'] == 'essay' ? 5 : 1,
                decoration: const InputDecoration(
                  labelText: 'Câu trả lời của bạn',
                  helperText: 'Số thập phân: dùng dấu phẩy hoặc dấu chấm.',
                  border: OutlineInputBorder(),
                ),
                onChanged: (v) => answer(q, [v]),
              ),
            if (q['type'] == 'essay')
              const Text('Tự luận cần người duyệt; AI chưa được cấu hình.'),
            if (session!['recovery_notice'] != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 12),
                child: Text(session!['recovery_notice']),
              ),
            if (recoveryAvailable)
              FilledButton.icon(
                onPressed: busy ? null : recover,
                icon: const Icon(Icons.restore),
                label: const Text('Khôi phục bài đã lưu'),
              ),
            if (error != null)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16),
                child: Text(
                  error!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            const SizedBox(height: 20),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                OutlinedButton(
                  onPressed: busy || index == 0
                      ? null
                      : () => setState(() => index--),
                  child: const Text('Câu trước'),
                ),
                OutlinedButton(
                  onPressed: busy || index == questions.length - 1
                      ? null
                      : () => setState(() => index++),
                  child: const Text('Câu tiếp'),
                ),
                FilledButton(
                  onPressed: busy ? null : submit,
                  child: Text(busy ? 'Đang nộp…' : 'Nộp bài'),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Wrap(
              spacing: 6,
              children: [
                for (int i = 0; i < questions.length; i++)
                  ActionChip(
                    label: Text('${i + 1}'),
                    avatar: flags.contains(questions[i]['id'])
                        ? const Icon(Icons.flag, size: 16)
                        : answers.containsKey(questions[i]['id'])
                        ? const Icon(Icons.check, size: 16)
                        : null,
                    onPressed: busy ? null : () => setState(() => index = i),
                  ),
              ],
            ),
            const SizedBox(height: 20),
            const Text(
              'Bài luyện tập được lưu trên thiết bị. Đồng hồ mang tính tham khảo; có thể nộp khi kết nối lại trong vòng 24 giờ.',
            ),
          ],
        ),
      ),
    );
  }
}

class ResultView extends StatelessWidget {
  const ResultView({super.key, required this.result});
  final Json result;
  @override
  Widget build(BuildContext context) => ListView(
    padding: const EdgeInsets.all(24),
    children: [
      Text(result['title'], style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 24),
      Text(
        result['score'] == null
            ? 'Cần kiểm tra thủ công'
            : '${result['score']} / ${result['max_score']}',
        style: Theme.of(context).textTheme.displaySmall,
      ),
      const Text(
        'Điểm luyện tập theo đáp án đã duyệt, không phải điểm chính thức của giáo viên.',
      ),
      if (result['notice'] != null) Text(result['notice']),
      const SizedBox(height: 24),
      ...(result['details'] as List).map(
        (d) => Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Câu ${(result['details'] as List).indexOf(d) + 1} · ${d['score'] ?? 'Chờ duyệt'}/${d['max_score']}",
                ),
                const SizedBox(height: 8),
                if (d['question'] != null) Text(d['question']),
                if (d['submitted_answer_display'] != null)
                  Text(
                    'Bài làm: ${(d['submitted_answer_display'] as List).join(', ')}',
                  ),
                Text(
                  "Đáp án: ${((d['answer_display'] ?? d['correct_answer']) as List).join(', ')}",
                ),
                Text(d['explanation']),
              ],
            ),
          ),
        ),
      ),
      FilledButton(
        onPressed: () => context.go('/exams'),
        child: const Text('Về trang luyện đề'),
      ),
    ],
  );
}

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});
  @override
  ConsumerState<HistoryScreen> createState() => _HistoryState();
}

class _HistoryState extends ConsumerState<HistoryScreen> {
  @override
  Widget build(BuildContext context) => Shell(
    title: 'Lịch sử bài làm',
    index: 3,
    child: ref
        .watch(preferencesProvider)
        .when(
          data: (p) {
            final store = LocalStore(p);
            final records = store.history;
            return records.isEmpty
                ? const Center(
                    child: Text(
                      'Chưa có kết quả. Hãy làm bài luyện tập đầu tiên.',
                    ),
                  )
                : ListView(
                    children: records
                        .map(
                          (r) => ListTile(
                            title: Text(r['result']['title']),
                            subtitle: Text(
                              "${r['result']['score'] ?? 'Chờ duyệt'} / ${r['result']['max_score']}",
                            ),
                            onTap: () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => Scaffold(
                                  appBar: AppBar(
                                    title: const Text('Kết quả đã lưu'),
                                  ),
                                  body: ResultView(result: r['result']),
                                ),
                              ),
                            ),
                            trailing: IconButton(
                              tooltip: 'Xóa bài và kết quả',
                              icon: const Icon(Icons.delete_outline),
                              onPressed: () async {
                                final ok = await showDialog<bool>(
                                  context: context,
                                  builder: (c) => AlertDialog(
                                    title: const Text('Xóa kết quả?'),
                                    content: const Text(
                                      'Xóa cả bản lưu trên thiết bị và attempt trên server.',
                                    ),
                                    actions: [
                                      TextButton(
                                        onPressed: () =>
                                            Navigator.pop(c, false),
                                        child: const Text('Hủy'),
                                      ),
                                      FilledButton(
                                        onPressed: () => Navigator.pop(c, true),
                                        child: const Text('Xóa'),
                                      ),
                                    ],
                                  ),
                                );
                                if (ok != true) return;
                                try {
                                  await ref.read(apiProvider).delete(r);
                                  await store.removeHistory(r['id']);
                                  if (mounted) setState(() {});
                                } catch (_) {
                                  if (context.mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text(
                                          'Chưa xóa được trên server. Hãy kết nối mạng rồi thử lại.',
                                        ),
                                      ),
                                    );
                                  }
                                }
                              },
                            ),
                          ),
                        )
                        .toList(),
                  );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, _) =>
              Failure(retry: () => ref.invalidate(preferencesProvider)),
        ),
  );
}

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context, WidgetRef ref) => Shell(
    title: 'Cá nhân & quyền riêng tư',
    index: 4,
    child: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        Card(
          child: ListTile(
            leading: const Icon(Icons.account_circle),
            title: Text(
              ref.watch(authUserProvider) == null
                  ? 'Đăng nhập hoặc đăng ký'
                  : 'Tài khoản: ${ref.watch(authUserProvider)!["display_name"]}',
            ),
            subtitle: const Text('Tài khoản học viên và quản lý kết quả'),
            onTap: () => context.go('/account'),
          ),
        ),
        SwitchListTile(
          title: const Text('Giao diện tối'),
          value: ref.watch(darkProvider),
          onChanged: (v) => ref.read(darkProvider.notifier).state = v,
        ),
        const Divider(),
        const BackendSettings(),
        const Divider(),
        const Text(
          'Chế độ khách lưu lịch sử trên thiết bị. Khi đăng nhập, kết quả được máy chủ lưu theo tài khoản và người quản lý của bạn có thể xem. Xóa lịch sử trên thiết bị không xóa hồ sơ kết quả của lớp. AI và OCR chưa hoạt động; không gửi bài đến nhà cung cấp AI.',
        ),
        const SizedBox(height: 16),
        const Text(
          'Có thể xóa từng kết quả ở trang Lịch sử. Chính sách quyền riêng tư và điều khoản phát hành cần được hoàn thiện trước khi dùng với học sinh thật.',
        ),
      ],
    ),
  );
}

class BackendSettings extends ConsumerStatefulWidget {
  const BackendSettings({super.key});
  @override
  ConsumerState<BackendSettings> createState() => _BackendSettingsState();
}

class _BackendSettingsState extends ConsumerState<BackendSettings> {
  final controller = TextEditingController();
  bool busy = false;
  String? message;
  @override
  void initState() {
    super.initState();
    controller.text = ref.read(apiProvider).baseUrl;
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> connect() async {
    setState(() {
      busy = true;
      message = null;
    });
    try {
      final url = validateBackendUrl(controller.text);
      final prefs = await SharedPreferences.getInstance();
      final store = LocalStore(prefs);
      if (ref.read(authUserProvider) != null &&
          url != ref.read(apiProvider).baseUrl) {
        throw StateError('Hãy đăng xuất trước khi đổi máy chủ.');
      }
      if (url != ref.read(apiProvider).baseUrl &&
          (store.current != null || store.history.isNotEmpty)) {
        throw StateError(
          'Hãy hoàn thành bài đang làm và xóa lịch sử trước khi đổi máy chủ.',
        );
      }
      await LearningApi(baseUrl: url).checkConnection();
      if (!await prefs.setString('backend_url', url)) {
        throw StateError('Không thể lưu địa chỉ máy chủ.');
      }
      ref.read(backendUrlProvider.notifier).state = url;
      if (mounted) {
        setState(() => message = 'Kết nối thành công. Đã lưu địa chỉ máy chủ.');
      }
    } on FormatException catch (e) {
      if (mounted) setState(() => message = e.message);
    } on StateError catch (e) {
      if (mounted) setState(() => message = e.message.toString());
    } catch (_) {
      if (mounted) {
        setState(
          () => message =
              'Không kết nối được. Kiểm tra địa chỉ HTTPS và mạng rồi thử lại.',
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text('Kết nối máy chủ', style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 8),
      const Text(
        'Nhập địa chỉ được cung cấp cho bản thử. Bài làm sẽ được gửi đến máy chủ này.',
      ),
      const SizedBox(height: 12),
      TextField(
        controller: controller,
        enabled: !busy,
        keyboardType: TextInputType.url,
        autocorrect: false,
        decoration: const InputDecoration(
          labelText: 'Địa chỉ backend HTTPS',
          hintText: 'https://...',
          border: OutlineInputBorder(),
        ),
      ),
      const SizedBox(height: 12),
      FilledButton(
        onPressed: busy ? null : connect,
        child: Text(busy ? 'Đang kiểm tra…' : 'Kiểm tra và lưu'),
      ),
      if (message != null)
        Padding(padding: const EdgeInsets.only(top: 12), child: Text(message!)),
      const SizedBox(height: 12),
    ],
  );
}
