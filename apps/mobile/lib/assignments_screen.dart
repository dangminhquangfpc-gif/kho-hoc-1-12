import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'repository.dart';
import 'report_export.dart';

String _assignmentError(Object error) {
  if (error is StateError) return error.message.toString();
  if (error is DioException) {
    final data = error.response?.data;
    if (data is Map && data['detail'] is String) return data['detail'];
  }
  return 'Chưa tải được dữ liệu. Kiểm tra kết nối rồi thử lại.';
}

bool _isTeacher(Json? user) => ['teacher', 'manager'].contains(user?['role']);

String _status(Json row) => switch (row['status']) {
  'submitted' => 'Đã nộp',
  'in_progress' => 'Đang làm',
  _ => 'Chưa nộp',
};

String _latestResult(Json row) => row['latest_percent'] is num
    ? '${(row['latest_percent'] as num).toStringAsFixed(1)}%'
    : row['status'] == 'submitted'
    ? 'Chờ xem xét'
    : 'Chưa có kết quả';

String _submittedAt(dynamic value) {
  final date = value is String ? DateTime.tryParse(value)?.toLocal() : null;
  if (date == null) return '';
  String two(int n) => '$n'.padLeft(2, '0');
  return '${two(date.day)}/${two(date.month)}/${date.year} ${two(date.hour)}:${two(date.minute)}';
}

/// The same assignment list shows a student's own state or an owner's group.
class AssignmentsScreen extends ConsumerStatefulWidget {
  const AssignmentsScreen({super.key, this.groupId, this.groupName});
  final String? groupId, groupName;

  @override
  ConsumerState<AssignmentsScreen> createState() => _AssignmentsState();
}

class _AssignmentsState extends ConsumerState<AssignmentsScreen> {
  final rows = <Json>[];
  bool loading = false, more = true, opening = false;
  String? error;

  bool get teacher =>
      widget.groupId != null && _isTeacher(ref.read(authUserProvider));

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load({bool reset = false}) async {
    if (loading) return;
    if (ref.read(authUserProvider) == null ||
        (widget.groupId != null && !teacher)) {
      return;
    }
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final api = ref.read(apiProvider);
      final page = teacher
          ? await api.groupAssignments(
              widget.groupId!,
              offset: reset ? 0 : rows.length,
            )
          : await api.accountAssignments(offset: reset ? 0 : rows.length);
      if (!mounted) return;
      setState(() {
        if (reset) rows.clear();
        rows.addAll(page);
        more = page.length == 30;
      });
    } catch (e) {
      if (mounted) setState(() => error = _assignmentError(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  void openPractice() {
    final router = GoRouter.of(context);
    if (Navigator.canPop(context)) Navigator.pop(context);
    router.go('/practice');
  }

  Future<void> open(Json row) async {
    setState(() {
      opening = true;
      error = null;
    });
    try {
      final prefs = await ref.read(preferencesProvider.future);
      final store = LocalStore(prefs);
      final previous = store.current;
      if (!mounted) return;
      if (previous != null) {
        if (previous['exam']?['id'] != row['exam_id']) {
          final yes = await showDialog<bool>(
            context: context,
            builder: (c) => AlertDialog(
              title: const Text('Bạn còn bài đang làm'),
              content: const Text(
                'Câu trả lời đang lưu trên thiết bị được giữ nguyên. Hãy tiếp tục và hoàn thành bài đó trước khi mở bài được giao này.',
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(c, false),
                  child: const Text('Ở lại'),
                ),
                FilledButton(
                  onPressed: () => Navigator.pop(c, true),
                  child: const Text('Tiếp tục bài đang làm'),
                ),
              ],
            ),
          );
          if (yes != true || !mounted) return;
        }
        openPractice();
        return;
      }
      final api = ref.read(apiProvider);
      final pending = await api.pendingAttempts();
      final matches = pending.where((a) => a['exam_id'] == row['exam_id']);
      final attempt = matches.isNotEmpty
          ? await api.resumeAttempt(matches.first['id'])
          : await api.start(row['exam_id']);
      await store.save({
        ...attempt,
        'backend_url': api.baseUrl,
        'answers': attempt['answers'] ?? <String, List<String>>{},
      });
      if (mounted) openPractice();
    } catch (e) {
      if (mounted) setState(() => error = _assignmentError(e));
    } finally {
      if (mounted) setState(() => opening = false);
    }
  }

  Future<void> chooseExam() async {
    final assigned = await Navigator.push<bool>(
      context,
      MaterialPageRoute(
        builder: (_) => _AssignExamScreen(groupId: widget.groupId!),
      ),
    );
    if (assigned == true && mounted) await load(reset: true);
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authUserProvider);
    final allowed =
        user != null && (widget.groupId == null || _isTeacher(user));
    return Scaffold(
      appBar: AppBar(
        title: Text(teacher ? 'Bài giao và tiến độ' : 'Bài được giao'),
        actions: [
          if (allowed)
            IconButton(
              tooltip: 'Tải lại bài được giao',
              onPressed: loading ? null : () => load(reset: true),
              icon: const Icon(Icons.refresh),
            ),
        ],
      ),
      body: !allowed
          ? const Center(child: Text('Bạn cần đăng nhập với vai trò phù hợp.'))
          : ListView(
              padding: const EdgeInsets.all(20),
              children: [
                if (teacher) ...[
                  Text(
                    widget.groupName ?? 'Nhóm học viên',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const Text(
                    'Tiến độ tính theo thành viên hiện tại của nhóm và mọi lần nộp đề này. Kết quả hiển thị theo phần trăm ở lần nộp mới nhất, phục vụ theo dõi luyện tập. Mục “Chưa nộp” gồm học viên chưa nộp và không có phiên đang làm còn hiệu lực.',
                  ),
                  const SizedBox(height: 12),
                  FilledButton.icon(
                    onPressed: loading ? null : chooseExam,
                    icon: const Icon(Icons.add),
                    label: const Text('Giao đề có sẵn'),
                  ),
                ] else
                  const Text(
                    'Các đề giáo viên giao cho nhóm bạn đang tham gia. Kết quả luyện tập dùng lần nộp mới nhất; bạn chỉ xem được tiến độ của mình.',
                  ),
                const SizedBox(height: 12),
                if (error != null) ...[
                  Text(
                    error!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                  TextButton(
                    onPressed: loading ? null : () => load(reset: rows.isEmpty),
                    child: const Text('Thử lại'),
                  ),
                ],
                if (!loading && error == null && rows.isEmpty)
                  const Text('Chưa có bài được giao.'),
                for (final row in rows)
                  Card(
                    child: ListTile(
                      title: Text(row['title'] as String),
                      subtitle: Text(
                        teacher
                            ? 'Lớp ${row['grade']} · ${row['duration_minutes']} phút\n${row['submitted_count']} đã nộp · ${row['in_progress_count']} đang làm · ${row['not_started_count']} chưa nộp / ${row['member_count']} học viên'
                            : '${row['group_name']} · Lớp ${row['grade']} · ${row['duration_minutes']} phút\n${_status(row)} · ${row['attempts_count']} lần nộp · ${_latestResult(row)}',
                      ),
                      isThreeLine: true,
                      trailing: Icon(
                        teacher ? Icons.chevron_right : Icons.play_arrow,
                      ),
                      onTap: opening
                          ? null
                          : teacher
                          ? () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => AssignmentProgressScreen(
                                  groupId: widget.groupId!,
                                  examId: row['exam_id'],
                                ),
                              ),
                            )
                          : () => open(row),
                    ),
                  ),
                if (loading || opening) const LinearProgressIndicator(),
                if (more && !loading && rows.isNotEmpty)
                  TextButton(onPressed: load, child: const Text('Xem thêm')),
              ],
            ),
    );
  }
}

class AssignmentProgressScreen extends ConsumerStatefulWidget {
  const AssignmentProgressScreen({
    super.key,
    required this.groupId,
    required this.examId,
  });
  final String groupId, examId;

  @override
  ConsumerState<AssignmentProgressScreen> createState() =>
      _AssignmentProgressState();
}

class _AssignmentProgressState extends ConsumerState<AssignmentProgressScreen> {
  Json? progress;
  String? error;
  bool loading = false, exporting = false;
  String status = '';

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    if (!_isTeacher(ref.read(authUserProvider))) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final value = await ref
          .read(apiProvider)
          .groupAssignmentProgress(widget.groupId, widget.examId);
      if (mounted) setState(() => progress = value);
    } catch (e) {
      if (mounted) setState(() => error = _assignmentError(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> export() async {
    setState(() {
      exporting = true;
      error = null;
    });
    try {
      final csv = await ref
          .read(apiProvider)
          .groupAssignmentCsv(widget.groupId, widget.examId);
      if (!mounted) return;
      await exportReport(csv, filename: 'tu-hoc-111-ket-qua-de-giao.csv');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Đã xuất tiến độ và kết quả lần nộp mới nhất của thành viên hiện tại. Học viên chưa có kết quả được để trống điểm.',
          ),
        ),
      );
    } catch (e) {
      if (mounted) setState(() => error = _assignmentError(e));
    } finally {
      if (mounted) setState(() => exporting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final allowed = _isTeacher(ref.watch(authUserProvider));
    final students = (progress?['students'] as List? ?? []).cast<Json>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tiến độ bài được giao'),
        actions: [
          if (allowed)
            IconButton(
              tooltip: 'Tải lại tiến độ',
              onPressed: loading ? null : load,
              icon: const Icon(Icons.refresh),
            ),
        ],
      ),
      body: !allowed
          ? const Center(
              child: Text('Chỉ giáo viên của nhóm được xem tiến độ.'),
            )
          : ListView(
              padding: const EdgeInsets.all(20),
              children: [
                if (loading || exporting) const LinearProgressIndicator(),
                if (error != null) ...[
                  Text(error!),
                  TextButton(
                    onPressed: loading ? null : load,
                    child: const Text('Thử lại'),
                  ),
                ],
                if (progress != null) ...[
                  Text(
                    progress!['title'],
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  Text(
                    '${progress!['group_name']} · ${progress!['member_count']} thành viên hiện tại',
                  ),
                  const Text(
                    'Thống kê mọi lần nộp đề này. Phần trăm là kết quả luyện tập ở lần nộp mới nhất; bài chờ xem xét chưa có điểm. Mục “Chưa nộp” gồm học viên chưa nộp và không có phiên đang làm còn hiệu lực.',
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ChoiceChip(
                        label: const Text('Tất cả'),
                        selected: status.isEmpty,
                        onSelected: (_) => setState(() => status = ''),
                      ),
                      for (final (value, label, field) in [
                        ('submitted', 'Đã nộp', 'submitted_count'),
                        ('in_progress', 'Đang làm', 'in_progress_count'),
                        ('not_started', 'Chưa nộp', 'not_started_count'),
                      ])
                        ChoiceChip(
                          label: Text('$label (${progress![field]})'),
                          selected: status == value,
                          onSelected: (_) => setState(() => status = value),
                        ),
                    ],
                  ),
                  TextButton.icon(
                    onPressed: exporting ? null : export,
                    icon: const Icon(Icons.table_view),
                    label: Text(reportExportLabel),
                  ),
                  if (students.isEmpty) const Text('Nhóm chưa có học viên.'),
                  for (final student in students.where(
                    (s) => status.isEmpty || s['status'] == status,
                  ))
                    Card(
                      child: ListTile(
                        title: Text(
                          '${student['display_name']} (${student['username']})',
                        ),
                        subtitle: Text(
                          '${_status(student)} · ${student['attempts_count']} lần nộp\n${_latestResult(student)}${student['latest_submitted_at'] == null ? '' : ' · ${_submittedAt(student['latest_submitted_at'])}'}',
                        ),
                        isThreeLine: true,
                      ),
                    ),
                  if (students.isNotEmpty &&
                      students.every(
                        (s) => status.isNotEmpty && s['status'] != status,
                      ))
                    const Text('Chưa có học viên ở trạng thái này.'),
                ],
              ],
            ),
    );
  }
}

class _AssignExamScreen extends ConsumerStatefulWidget {
  const _AssignExamScreen({required this.groupId});
  final String groupId;
  @override
  ConsumerState<_AssignExamScreen> createState() => _AssignExamState();
}

class _AssignExamState extends ConsumerState<_AssignExamScreen> {
  final search = TextEditingController();
  int grade = 5, requestId = 0;
  String subject = 'toan';
  List<Json> subjects = [], exams = [];
  bool loading = false, assigning = false;
  String? error;

  @override
  void initState() {
    super.initState();
    load(changeGrade: true);
  }

  @override
  void dispose() {
    search.dispose();
    super.dispose();
  }

  Future<void> load({bool changeGrade = false}) async {
    final current = ++requestId;
    final api = ref.read(apiProvider);
    setState(() {
      loading = true;
      error = null;
    });
    try {
      if (changeGrade) {
        final values = await api.subjects(grade);
        if (!mounted || current != requestId) return;
        subjects = values;
        if (!subjects.any((s) => s['id'] == subject)) {
          subject = subjects.isEmpty ? '' : subjects.first['id'];
        }
      }
      final values = subject.isEmpty
          ? <Json>[]
          : await api.exams(grade, subject, search.text.trim());
      if (mounted && current == requestId) setState(() => exams = values);
    } catch (e) {
      if (mounted && current == requestId) {
        setState(() => error = _assignmentError(e));
      }
    } finally {
      if (mounted && current == requestId) setState(() => loading = false);
    }
  }

  Future<void> assign(Json exam) async {
    final yes = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Giao đề cho nhóm?'),
        content: Text(
          'Giao “${exam['title']}” cho các thành viên của nhóm. App lưu một bản đề riêng cho nhóm để theo dõi tiến độ.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Giao đề'),
          ),
        ],
      ),
    );
    if (yes != true || !mounted) return;
    setState(() {
      assigning = true;
      error = null;
    });
    try {
      await ref.read(apiProvider).assignGroupExam(widget.groupId, exam['id']);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) setState(() => error = _assignmentError(e));
    } finally {
      if (mounted) setState(() => assigning = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Giao đề có sẵn')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text(
          'Chọn lớp, môn và tìm tên đề. Đề được giao sẽ xuất hiện trong Bài được giao của các học viên trong nhóm.',
        ),
        DropdownButtonFormField<int>(
          initialValue: grade,
          isExpanded: true,
          decoration: const InputDecoration(labelText: 'Lớp học'),
          items: [
            for (var n = 1; n <= 12; n++)
              DropdownMenuItem(value: n, child: Text('Lớp $n')),
          ],
          onChanged: assigning || loading
              ? null
              : (value) {
                  setState(() => grade = value!);
                  load(changeGrade: true);
                },
        ),
        if (subjects.isNotEmpty)
          DropdownButtonFormField<String>(
            key: ValueKey('subject-$grade-$subject'),
            initialValue: subject,
            isExpanded: true,
            decoration: const InputDecoration(labelText: 'Môn học'),
            items: [
              for (final s in subjects)
                DropdownMenuItem(
                  value: s['id'] as String,
                  child: Text(s['name']),
                ),
            ],
            onChanged: assigning || loading
                ? null
                : (value) {
                    setState(() => subject = value!);
                    load();
                  },
          ),
        const SizedBox(height: 12),
        TextField(
          controller: search,
          enabled: !assigning && !loading,
          decoration: InputDecoration(
            labelText: 'Tìm tên đề',
            suffixIcon: IconButton(
              tooltip: 'Tìm đề',
              onPressed: loading || assigning ? null : load,
              icon: const Icon(Icons.search),
            ),
          ),
          onSubmitted: (_) => load(),
        ),
        if (error != null) ...[
          Text(error!),
          TextButton(
            onPressed: loading || assigning
                ? null
                : () => load(changeGrade: subjects.isEmpty),
            child: const Text('Thử lại'),
          ),
        ],
        if (loading || assigning) const LinearProgressIndicator(),
        if (!loading && exams.isEmpty)
          const Text('Chưa có đề phù hợp. Hãy đổi bộ lọc hoặc từ khóa.'),
        if (!loading)
          for (final exam in exams)
            Card(
              child: ListTile(
                title: Text(exam['title']),
                subtitle: Text(
                  '${exam['question_count']} câu · ${exam['duration_minutes']} phút',
                ),
                trailing: const Icon(Icons.add_task),
                onTap: assigning ? null : () => assign(exam),
              ),
            ),
      ],
    ),
  );
}
