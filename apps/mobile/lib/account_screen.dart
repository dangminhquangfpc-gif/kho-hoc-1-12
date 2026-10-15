import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'main.dart' show Shell, Failure, ResultView;
import 'repository.dart';
import 'study_progress.dart';

final serverResultsProvider = FutureProvider.autoDispose<List<Json>>((ref) {
  final user = ref.watch(authUserProvider);
  return user == null
      ? Future.value(<Json>[])
      : ref.watch(apiProvider).accountResults();
});

final pendingAttemptsProvider = FutureProvider.autoDispose<List<Json>>((ref) {
  final user = ref.watch(authUserProvider);
  return user == null
      ? Future.value(<Json>[])
      : ref.watch(apiProvider).pendingAttempts();
});

String accountError(Object error) {
  if (error is StateError) return error.message.toString();
  if (error is DioException) {
    final detail = error.response?.data;
    if (detail is Map && detail['detail'] is String) return detail['detail'];
    if (error.response?.statusCode == 422) {
      return 'Kiểm tra tên đăng nhập (3–40 chữ không dấu, số, dấu chấm/gạch) và mật khẩu tối thiểu 10 ký tự.';
    }
    if (error.response?.statusCode == 429) {
      return 'Bạn đã thử nhiều lần. Hãy đợi rồi thử lại.';
    }
  }
  return 'Chưa kết nối được máy chủ. Hãy kiểm tra và thử lại.';
}

class AccountScreen extends ConsumerStatefulWidget {
  const AccountScreen({super.key});
  @override
  ConsumerState<AccountScreen> createState() => _AccountState();
}

class _AccountState extends ConsumerState<AccountScreen> {
  final username = TextEditingController(),
      password = TextEditingController(),
      name = TextEditingController();
  final current = TextEditingController(),
      next = TextEditingController(),
      confirm = TextEditingController();
  bool register = false, busy = false;
  int grade = 5;
  String role = 'student';
  String? error;
  @override
  void dispose() {
    for (final c in [username, password, name, current, next, confirm]) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> act(Future<void> Function() action) async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await action();
    } catch (e) {
      if (mounted) setState(() => error = accountError(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> login() => act(() async {
    final container = ProviderScope.containerOf(context, listen: false);
    final p = await ref.read(preferencesProvider.future);
    if (LocalStore(p).current != null) {
      setState(
        () => error = 'Hãy hoàn thành bài đang làm trước khi đổi tài khoản.',
      );
      return;
    }
    if (password.text.length < 10 || (register && name.text.trim().isEmpty)) {
      setState(
        () => error = 'Nhập đủ thông tin; mật khẩu cần ít nhất 10 ký tự.',
      );
      return;
    }
    await ref
        .read(apiProvider)
        .authenticate(
          username.text,
          password.text,
          displayName: register ? name.text : null,
          grade: register ? grade : null,
          role: role,
        );
    container.invalidate(authBootstrapProvider);
  });
  Future<void> change() => act(() async {
    final container = ProviderScope.containerOf(context, listen: false);
    if (next.text != confirm.text || next.text.length < 10) {
      setState(
        () => error =
            'Mật khẩu mới cần ít nhất 10 ký tự và hai lần nhập phải giống nhau.',
      );
      return;
    }
    await ref.read(apiProvider).changePassword(current.text, next.text);
    container.invalidate(authBootstrapProvider);
  });
  Future<void> logout() => act(() async {
    final container = ProviderScope.containerOf(context, listen: false);
    final p = await ref.read(preferencesProvider.future);
    if (LocalStore(p).current != null) {
      setState(
        () => error = 'Hãy hoàn thành bài đang làm trước khi đăng xuất.',
      );
      return;
    }
    final accountId = p.getString('active_account_id');
    await ref.read(apiProvider).signOut();
    if (accountId != null) await p.remove('history.$accountId');
    container.invalidate(authBootstrapProvider);
  });
  Future<void> deleteAccount() async {
    final text = TextEditingController();
    final password = await showDialog<String>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Xóa tài khoản và kết quả học tập?'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Thao tác không thể hoàn tác. Tài khoản và kết quả của bạn trên máy chủ sẽ bị xóa. Nếu bạn là giáo viên, tài khoản học sinh được giữ lại cho người quản lý hệ thống.',
            ),
            TextField(
              controller: text,
              obscureText: true,
              decoration: const InputDecoration(labelText: 'Mật khẩu xác nhận'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, text.text),
            child: const Text('Xóa vĩnh viễn'),
          ),
        ],
      ),
    );
    Future<void>.delayed(const Duration(seconds: 1), text.dispose);
    if (password == null || !mounted) return;
    await act(() async {
      final container = ProviderScope.containerOf(context, listen: false);
      final prefs = await ref.read(preferencesProvider.future);
      final id = prefs.getString('active_account_id');
      await ref.read(apiProvider).deleteAccount(password);
      if (id != null) {
        for (final key in ['history.$id', 'current_attempt.$id']) {
          await prefs.remove(key);
        }
      }
      container.invalidate(authBootstrapProvider);
    });
  }

  Widget field(
    TextEditingController controller,
    String label, {
    bool secret = false,
  }) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: TextField(
      controller: controller,
      enabled: !busy,
      obscureText: secret,
      autocorrect: !secret,
      decoration: InputDecoration(
        labelText: label,
        border: const OutlineInputBorder(),
      ),
    ),
  );
  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authUserProvider);
    return Shell(
      title: 'Tài khoản',
      index: 4,
      child: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          if (user == null) ...[
            Text(
              register ? 'Đăng ký tài khoản' : 'Đăng nhập',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const Text(
              'Học viên tự đăng ký sẽ xuất hiện trong danh sách của người quản lý hệ thống. Không cần email hoặc số điện thoại.',
            ),
            field(username, 'Tên đăng nhập'),
            field(password, 'Mật khẩu', secret: true),
            if (register) ...[
              field(name, 'Tên hiển thị'),
              DropdownButtonFormField<String>(
                isExpanded: true,
                initialValue: role,
                decoration: const InputDecoration(labelText: 'Vai trò'),
                items: const [
                  DropdownMenuItem(
                    value: 'student',
                    child: Text('Học sinh — làm đề có sẵn'),
                  ),
                  DropdownMenuItem(
                    value: 'teacher',
                    child: Text('Giáo viên — tạo đề và quản lý nhóm'),
                  ),
                ],
                onChanged: busy ? null : (v) => setState(() => role = v!),
              ),
              DropdownButtonFormField<int>(
                initialValue: grade,
                decoration: const InputDecoration(labelText: 'Lớp học'),
                items: [
                  for (var n = 1; n <= 12; n++)
                    DropdownMenuItem(value: n, child: Text('Lớp $n')),
                ],
                onChanged: busy ? null : (v) => setState(() => grade = v!),
              ),
            ],
            const SizedBox(height: 16),
            FilledButton(
              onPressed: busy ? null : login,
              child: Text(
                busy
                    ? 'Đang xử lý…'
                    : register
                    ? 'Đăng ký'
                    : 'Đăng nhập',
              ),
            ),
            TextButton(
              onPressed: busy
                  ? null
                  : () => setState(() {
                      register = !register;
                      error = null;
                    }),
              child: Text(
                register
                    ? 'Đã có tài khoản? Đăng nhập'
                    : 'Chưa có tài khoản? Đăng ký',
              ),
            ),
            const Text(
              'Người quản lý bản local: mở tệp state/TAI-KHOAN-QUAN-LY.txt trong thư mục đang chạy demo để lấy tài khoản ban đầu. Không gửi mật khẩu qua chat.',
            ),
          ] else ...[
            Text(
              user['display_name'],
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            Text(
              '${user['username']} · ${user['role'] == 'manager'
                  ? 'Người quản lý'
                  : user['role'] == 'teacher'
                  ? 'Giáo viên'
                  : 'Học sinh'}',
            ),
            if (user['must_change_password'] == true) ...[
              const Text(
                'Bạn cần đổi mật khẩu tạm trước khi làm bài hoặc quản lý lớp.',
              ),
              field(current, 'Mật khẩu hiện tại', secret: true),
              field(next, 'Mật khẩu mới', secret: true),
              field(confirm, 'Nhập lại mật khẩu mới', secret: true),
              FilledButton(
                onPressed: busy ? null : change,
                child: const Text('Đổi mật khẩu'),
              ),
            ] else ...[
              if (['manager', 'teacher'].contains(user['role']))
                FilledButton.icon(
                  onPressed: () => context.go('/classroom'),
                  icon: const Icon(Icons.groups),
                  label: const Text('Quản lý học viên và kết quả'),
                ),
              if (user['role'] == 'student') const GroupPanel(student: true),
              Row(
                children: [
                  const Expanded(child: Text('Bài đang làm trên các thiết bị')),
                  IconButton(
                    tooltip: 'Đồng bộ lại',
                    icon: const Icon(Icons.sync),
                    onPressed: () {
                      ref.invalidate(pendingAttemptsProvider);
                      ref.invalidate(serverResultsProvider);
                    },
                  ),
                ],
              ),
              ref
                  .watch(pendingAttemptsProvider)
                  .when(
                    data: (rows) => Column(
                      children: [
                        if (rows.isEmpty)
                          const Text('Chưa có bài đang làm trên máy chủ.'),
                        for (final row in rows)
                          ListTile(
                            leading: const Icon(Icons.cloud_sync),
                            title: Text(row['title']),
                            trailing: const Icon(Icons.play_arrow),
                            onTap: busy
                                ? null
                                : () => act(() async {
                                    final prefs = await ref.read(
                                      preferencesProvider.future,
                                    );
                                    final previous = LocalStore(prefs).current;
                                    if (!context.mounted) return;
                                    if (previous != null) {
                                      final confirmed = await showDialog<bool>(
                                        context: context,
                                        builder: (c) => AlertDialog(
                                          title: const Text(
                                            'Mở bản lưu trên máy chủ?',
                                          ),
                                          content: const Text(
                                            'Bản đang lưu trên thiết bị sẽ được thay bằng bản máy chủ. Hãy đồng bộ những thay đổi chưa lưu trước khi tiếp tục.',
                                          ),
                                          actions: [
                                            TextButton(
                                              onPressed: () =>
                                                  Navigator.pop(c, false),
                                              child: const Text('Hủy'),
                                            ),
                                            FilledButton(
                                              onPressed: () =>
                                                  Navigator.pop(c, true),
                                              child: const Text(
                                                'Mở bản máy chủ',
                                              ),
                                            ),
                                          ],
                                        ),
                                      );
                                      if (confirmed != true) return;
                                    }
                                    final attempt = await ref
                                        .read(apiProvider)
                                        .resumeAttempt(row['id']);
                                    await LocalStore(prefs).save({
                                      ...attempt,
                                      'backend_url': ref
                                          .read(apiProvider)
                                          .baseUrl,
                                    });
                                    if (context.mounted) {
                                      context.go('/practice');
                                    }
                                  }),
                          ),
                      ],
                    ),
                    loading: () => const LinearProgressIndicator(),
                    error: (e, _) => Text(accountError(e)),
                  ),
              ...[
                const Text(
                  'Kết quả được lưu theo tài khoản trên máy chủ (hiển thị tối đa 500 bài gần nhất). Người quản lý có thể theo dõi bài đã nộp và chủ đề cần ôn.',
                ),
                ref
                    .watch(serverResultsProvider)
                    .when(
                      data: (records) => Column(
                        children: [
                          for (final row in records)
                            Card(
                              child: ListTile(
                                title: Text(row['result']['title']),
                                subtitle: Text(
                                  '${row['result']['score'] ?? 'Chờ duyệt'} / ${row['result']['max_score']}',
                                ),
                                onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => Scaffold(
                                      appBar: AppBar(
                                        title: const Text('Kết quả đã lưu'),
                                      ),
                                      body: ResultView(result: row['result']),
                                    ),
                                  ),
                                ),
                              ),
                            ),
                        ],
                      ),
                      loading: () => const LinearProgressIndicator(),
                      error: (_, _) => Failure(
                        retry: () => ref.invalidate(serverResultsProvider),
                      ),
                    ),
              ],
              ExpansionTile(
                title: const Text('Đổi mật khẩu'),
                children: [
                  field(current, 'Mật khẩu hiện tại', secret: true),
                  field(next, 'Mật khẩu mới', secret: true),
                  field(confirm, 'Nhập lại mật khẩu mới', secret: true),
                  FilledButton(
                    onPressed: busy ? null : change,
                    child: const Text('Lưu mật khẩu mới'),
                  ),
                ],
              ),
            ],
            if (user['role'] != 'manager')
              TextButton.icon(
                onPressed: busy ? null : deleteAccount,
                icon: const Icon(Icons.delete_forever),
                label: const Text('Xóa tài khoản và dữ liệu học tập'),
              ),
            TextButton(
              onPressed: busy ? null : logout,
              child: const Text('Đăng xuất'),
            ),
          ],
          if (error != null)
            Padding(padding: const EdgeInsets.all(12), child: Text(error!)),
        ],
      ),
    );
  }
}

class ClassroomScreen extends ConsumerStatefulWidget {
  const ClassroomScreen({super.key});
  @override
  ConsumerState<ClassroomScreen> createState() => _ClassroomState();
}

class _ClassroomState extends ConsumerState<ClassroomScreen> {
  late Future<List<Json>> students;
  String? error;
  String search = '';
  bool busy = false;
  @override
  void initState() {
    super.initState();
    students = ref.read(apiProvider).classroomStudents();
  }

  void refresh() => setState(() {
    students = ref.read(apiProvider).classroomStudents();
  });
  Future<void> credentials(List<Json> records) async {
    if (!mounted) return;
    final text = records
        .map((r) => '${r['username']} ; ${r['temporary_password']}')
        .join('\n');
    await showDialog<void>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Tài khoản vừa cấp'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Mật khẩu tạm chỉ hiển thị tại đây. Lưu lại để cấp cho học viên; học viên phải đổi ở lần đăng nhập đầu.',
              ),
              SelectableText(text),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () async {
              await Clipboard.setData(ClipboardData(text: text));
            },
            child: const Text('Sao chép'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c),
            child: const Text('Đã lưu'),
          ),
        ],
      ),
    );
  }

  Future<void> create() async {
    String draft = '';
    final value = await showDialog<String>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Tạo hàng loạt tài khoản'),
        content: SizedBox(
          width: 560,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Mỗi dòng: tên_đăng_nhập ; tên hiển thị ; lớp\nVí dụ: hv001 ; Nguyễn An ; 5\nTối đa 50 tài khoản mỗi lượt. Mật khẩu tạm được tạo riêng cho từng bạn.',
              ),
              TextField(
                onChanged: (value) => draft = value,
                maxLines: 8,
                decoration: const InputDecoration(
                  labelText: 'Danh sách học viên',
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, draft),
            child: const Text('Tạo tài khoản'),
          ),
        ],
      ),
    );
    if (value == null) return;
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final rows = <Json>[];
      for (final line in value.split('\n').where((s) => s.trim().isNotEmpty)) {
        final fields = line.split(';').map((s) => s.trim()).toList();
        if (fields.length < 2 ||
            fields.length > 3 ||
            fields[0].isEmpty ||
            fields[1].isEmpty) {
          throw const FormatException('Kiểm tra định dạng từng dòng.');
        }
        final grade = fields.length == 3 ? int.tryParse(fields[2]) : null;
        if (fields.length == 3 && (grade == null || grade < 1 || grade > 12)) {
          throw const FormatException('Lớp phải là số từ 1 đến 12.');
        }
        rows.add({
          'username': fields[0],
          'display_name': fields[1],
          if (grade != null) 'grade': grade,
        });
      }
      if (rows.isEmpty || rows.length > 50) {
        throw const FormatException('Nhập từ 1 đến 50 học viên.');
      }
      final created = await ref.read(apiProvider).createStudents(rows);
      refresh();
      await credentials(created);
    } catch (e) {
      if (mounted) {
        setState(
          () => error = e is FormatException ? e.message : accountError(e),
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> reset(Json student) async {
    final yes = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Cấp lại mật khẩu?'),
        content: Text(
          'Các phiên đăng nhập của ${student['display_name']} sẽ kết thúc. Bạn cần cấp mật khẩu mới cho học viên.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Cấp lại'),
          ),
        ],
      ),
    );
    if (yes != true) return;
    try {
      await credentials([
        await ref.read(apiProvider).resetStudentPassword(student['id']),
      ]);
    } catch (e) {
      if (mounted) setState(() => error = accountError(e));
    }
  }

  Future<void> remove(Json student) async {
    final yes = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Xóa học viên và kết quả?'),
        content: Text(
          'Tài khoản ${student['username']} và toàn bộ kết quả trên máy chủ sẽ bị xóa. Thao tác này không thể hoàn tác.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Xóa toàn bộ'),
          ),
        ],
      ),
    );
    if (yes != true) return;
    try {
      await ref.read(apiProvider).removeStudent(student['id']);
      if (mounted) refresh();
    } catch (e) {
      if (mounted) setState(() => error = accountError(e));
    }
  }

  @override
  Widget build(BuildContext context) => Shell(
    title: 'Quản lý học viên',
    index: 4,
    child: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        const Text(
          'Học viên tự đăng ký và tài khoản bạn cấp đều xuất hiện tại đây. Kết quả lấy từ máy chủ chấm bài, không nhận điểm do thiết bị tự gửi.',
        ),
        const GroupPanel(),
        Wrap(
          spacing: 8,
          children: [
            FilledButton.icon(
              onPressed: busy ? null : create,
              icon: const Icon(Icons.person_add),
              label: const Text('Tạo hàng loạt tài khoản'),
            ),
            OutlinedButton(onPressed: refresh, child: const Text('Làm mới')),
          ],
        ),
        TextField(
          decoration: const InputDecoration(labelText: 'Tìm học viên'),
          onChanged: (s) => setState(() => search = vietnameseSearchKey(s)),
        ),
        if (error != null) Text(error!),
        FutureBuilder<List<Json>>(
          future: students,
          builder: (c, s) {
            if (s.hasError) {
              return Failure(message: accountError(s.error!), retry: refresh);
            }
            if (!s.hasData) return const LinearProgressIndicator();
            final rows = s.data!
                .where(
                  (r) => vietnameseSearchKey(
                    '${r['username']} ${r['display_name']}',
                  ).contains(search),
                )
                .toList();
            return Column(
              children: [
                Text('${s.data!.length} học viên'),
                for (final row in rows)
                  Card(
                    child: ListTile(
                      title: Text(
                        '${row['display_name']} (${row['username']})',
                      ),
                      subtitle: Text(
                        '${row['grade'] == null ? 'Chưa chọn lớp' : 'Lớp ${row['grade']}'} · ${row['completed']} bài · Điểm trung bình ${row['average_percent'] == null ? 'chưa có' : '${(row['average_percent'] as num).round()}%'}',
                      ),
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => StudentReportScreen(id: row['id']),
                        ),
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            tooltip: 'Cấp lại mật khẩu',
                            icon: const Icon(Icons.key),
                            onPressed: () => reset(row),
                          ),
                          IconButton(
                            tooltip: 'Xóa học viên',
                            icon: const Icon(Icons.delete_outline),
                            onPressed: () => remove(row),
                          ),
                        ],
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ],
    ),
  );
}

class StudentReportScreen extends ConsumerStatefulWidget {
  const StudentReportScreen({super.key, required this.id});
  final String id;
  @override
  ConsumerState<StudentReportScreen> createState() => _StudentReportState();
}

class _StudentReportState extends ConsumerState<StudentReportScreen> {
  late Future<Json> report;
  @override
  void initState() {
    super.initState();
    report = ref.read(apiProvider).studentResults(widget.id);
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Kết quả học viên')),
    body: FutureBuilder<Json>(
      future: report,
      builder: (c, s) {
        if (s.hasError) {
          return Failure(
            message: accountError(s.error!),
            retry: () => setState(() {
              report = ref.read(apiProvider).studentResults(widget.id);
            }),
          );
        }
        if (!s.hasData) return const Center(child: CircularProgressIndicator());
        final rows = (s.data!['records'] as List).cast<Json>();
        final progress = StudyProgress.fromHistory(rows);
        return ListView(
          padding: const EdgeInsets.all(24),
          children: [
            Text(
              s.data!['student']['display_name'],
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            Text(
              '${progress.completed} bài đã nộp · Điểm trung bình ${progress.averagePercent == null ? 'chưa có' : '${progress.averagePercent!.round()}%'}',
            ),
            const Text(
              'Hiển thị tối đa 500 bài gần nhất. Chủ đề tính lần làm mới nhất của từng câu; không phải đánh giá năng lực chính thức.',
            ),
            for (final topic in progress.topics)
              ListTile(
                title: Text(topic.name),
                subtitle: Text(
                  '${topic.percent.round()}% điểm · ${topic.wrongQuestionIds.length} câu cần ôn',
                ),
              ),
            for (final row in rows)
              Card(
                child: ListTile(
                  title: Text(row['result']['title']),
                  subtitle: Text(
                    '${row['result']['score'] ?? 'Chờ duyệt'} / ${row['result']['max_score']} · ${row['submitted_at']}',
                  ),
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => Scaffold(
                        appBar: AppBar(title: const Text('Chi tiết bài làm')),
                        body: ResultView(result: row['result']),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        );
      },
    ),
  );
}

class GroupPanel extends ConsumerStatefulWidget {
  const GroupPanel({super.key, this.student = false});
  final bool student;
  @override
  ConsumerState<GroupPanel> createState() => _GroupPanelState();
}

class _GroupPanelState extends ConsumerState<GroupPanel> {
  late Future<List<Json>> groups;
  String? error;
  bool busy = false;
  @override
  void initState() {
    super.initState();
    groups = ref.read(apiProvider).classroomGroups();
  }

  Future<String?> ask(String title, String label) async {
    final text = TextEditingController();
    final result = await showDialog<String>(
      context: context,
      builder: (c) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: text,
          decoration: InputDecoration(labelText: label),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, text.text.trim()),
            child: const Text('Lưu'),
          ),
        ],
      ),
    );
    // Keep the controller alive until the closing dialog animation completes.
    Future<void>.delayed(const Duration(seconds: 1), text.dispose);
    return result;
  }

  Future<void> act(Future<void> Function() action) async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await action();
      if (mounted) {
        setState(() => groups = ref.read(apiProvider).classroomGroups());
      }
    } catch (e) {
      if (mounted) setState(() => error = accountError(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            widget.student ? 'Nhóm học của tôi' : 'Nhóm học viên',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          Text(
            widget.student
                ? 'Nhập mã giáo viên cấp để tham gia. Giáo viên của nhóm sẽ xem được kết quả học tập của bạn.'
                : 'Tạo nhóm, cấp mã cho học sinh tự tham gia hoặc thêm tài khoản bạn đã cấp. Mở nhóm để xem kết quả từng học viên.',
          ),
          FilledButton(
            onPressed: busy
                ? null
                : () async {
                    final value = await ask(
                      widget.student ? 'Tham gia nhóm' : 'Tạo nhóm',
                      widget.student ? 'Mã nhóm' : 'Tên nhóm',
                    );
                    if (value == null || value.isEmpty) return;
                    await act(
                      () => widget.student
                          ? ref.read(apiProvider).joinGroup(value)
                          : ref.read(apiProvider).createGroup(value),
                    );
                  },
            child: Text(widget.student ? 'Nhập mã nhóm' : 'Tạo nhóm mới'),
          ),
          if (error != null) Text(error!),
          FutureBuilder<List<Json>>(
            future: groups,
            builder: (context, s) {
              if (s.hasError) return Text(accountError(s.error!));
              if (!s.hasData) return const LinearProgressIndicator();
              return Column(
                children: [
                  for (final group in s.data!)
                    ExpansionTile(
                      title: Text(group['name']),
                      subtitle: widget.student
                          ? null
                          : SelectableText(
                              'Mã tham gia: ${group['join_code']}',
                            ),
                      children: widget.student
                          ? const []
                          : [
                              TextButton(
                                onPressed: busy
                                    ? null
                                    : () async {
                                        final value = await ask(
                                          'Thêm học viên vào nhóm',
                                          'Tên đăng nhập tài khoản bạn đã cấp',
                                        );
                                        if (value != null && value.isNotEmpty) {
                                          await act(
                                            () => ref
                                                .read(apiProvider)
                                                .addGroupMember(
                                                  group['id'],
                                                  value,
                                                ),
                                          );
                                        }
                                      },
                                child: const Text('Thêm tài khoản học sinh'),
                              ),
                              FutureBuilder<List<Json>>(
                                future: ref
                                    .read(apiProvider)
                                    .classroomStudents(),
                                builder: (context, snapshot) {
                                  if (!snapshot.hasData) {
                                    return const SizedBox.shrink();
                                  }
                                  final ids = (group['student_ids'] as List)
                                      .cast<String>();
                                  return Column(
                                    children: [
                                      for (final student
                                          in snapshot.data!.where(
                                            (s) => ids.contains(s['id']),
                                          ))
                                        ListTile(
                                          title: Text(
                                            '${student['display_name']} (${student['username']})',
                                          ),
                                          subtitle: Text(
                                            '${student['completed']} bài · ${student['average_percent'] == null ? 'Chưa có điểm' : '${(student['average_percent'] as num).round()}%'}',
                                          ),
                                          onTap: () => Navigator.push(
                                            context,
                                            MaterialPageRoute(
                                              builder: (_) =>
                                                  StudentReportScreen(
                                                    id: student['id'],
                                                  ),
                                            ),
                                          ),
                                          trailing: IconButton(
                                            tooltip: 'Bỏ khỏi nhóm',
                                            icon: const Icon(
                                              Icons.person_remove,
                                            ),
                                            onPressed: busy
                                                ? null
                                                : () => act(
                                                    () => ref
                                                        .read(apiProvider)
                                                        .removeGroupMember(
                                                          group['id'],
                                                          student['id'],
                                                        ),
                                                  ),
                                          ),
                                        ),
                                    ],
                                  );
                                },
                              ),
                              TextButton(
                                onPressed: busy
                                    ? null
                                    : () async {
                                        final yes = await showDialog<bool>(
                                          context: context,
                                          builder: (c) => AlertDialog(
                                            title: const Text('Xóa nhóm?'),
                                            content: const Text(
                                              'Tài khoản và kết quả học viên vẫn được giữ lại.',
                                            ),
                                            actions: [
                                              TextButton(
                                                onPressed: () =>
                                                    Navigator.pop(c, false),
                                                child: const Text('Hủy'),
                                              ),
                                              FilledButton(
                                                onPressed: () =>
                                                    Navigator.pop(c, true),
                                                child: const Text('Xóa nhóm'),
                                              ),
                                            ],
                                          ),
                                        );
                                        if (yes == true) {
                                          await act(
                                            () => ref
                                                .read(apiProvider)
                                                .deleteGroup(group['id']),
                                          );
                                        }
                                      },
                                child: const Text('Xóa nhóm'),
                              ),
                            ],
                    ),
                ],
              );
            },
          ),
        ],
      ),
    ),
  );
}
