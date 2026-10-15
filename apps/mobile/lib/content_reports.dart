import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'repository.dart';
import 'account_screen.dart' show accountError;

const reportStatuses = {
  'open': 'Chờ xử lý',
  'in_review': 'Đang xem xét',
  'resolved': 'Đã xử lý',
  'dismissed': 'Không cần sửa',
};
const reportCategories = {
  'wrong_answer': 'Đáp án hoặc lời giải chưa đúng',
  'unclear': 'Thiếu dữ kiện hoặc khó hiểu',
  'typo': 'Lỗi chính tả, trình bày',
  'other': 'Vấn đề khác',
};

class ReportContentButton extends ConsumerWidget {
  const ReportContentButton({
    super.key,
    required this.kind,
    required this.targetId,
    this.attemptId,
  });
  final String kind, targetId;
  final String? attemptId;
  @override
  Widget build(BuildContext context, WidgetRef ref) => TextButton.icon(
    icon: const Icon(Icons.flag_outlined),
    label: const Text('Báo lỗi nội dung'),
    onPressed: () async {
      if (ref.read(authUserProvider) == null) {
        context.go('/account');
        return;
      }
      final sent = await showDialog<bool>(
        context: context,
        builder: (_) =>
            _ReportDialog(kind: kind, targetId: targetId, attemptId: attemptId),
      );
      if (sent == true && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Đã gửi phản hồi. Theo dõi trả lời tại Cá nhân → Phản hồi của tôi.',
            ),
          ),
        );
      }
    },
  );
}

class _ReportDialog extends ConsumerStatefulWidget {
  const _ReportDialog({
    required this.kind,
    required this.targetId,
    this.attemptId,
  });
  final String kind, targetId;
  final String? attemptId;
  @override
  ConsumerState<_ReportDialog> createState() => _ReportDialogState();
}

class _ReportDialogState extends ConsumerState<_ReportDialog> {
  final message = TextEditingController();
  String category = 'unclear';
  String? error;
  bool busy = false;
  @override
  void dispose() {
    message.dispose();
    super.dispose();
  }

  Future<void> send() async {
    if (message.text.trim().length < 5) {
      setState(() => error = 'Vui lòng mô tả ít nhất 5 ký tự.');
      return;
    }
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await ref.read(apiProvider).sendContentReport({
        'target_kind': widget.kind,
        'target_id': widget.targetId,
        if (widget.attemptId != null) 'attempt_id': widget.attemptId,
        'category': category,
        'message': message.text.trim(),
      });
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() {
          error = accountError(e);
          busy = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
    title: const Text('Báo lỗi nội dung'),
    content: SizedBox(
      width: 520,
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Nêu rõ chỗ chưa đúng và cách sửa bạn đề xuất. Không gửi mật khẩu hoặc thông tin riêng tư. Phản hồi không tự thay đổi điểm đã nộp.',
            ),
            DropdownButtonFormField<String>(
              initialValue: category,
              isExpanded: true,
              decoration: const InputDecoration(labelText: 'Loại vấn đề'),
              items: [
                for (final e in reportCategories.entries)
                  DropdownMenuItem(value: e.key, child: Text(e.value)),
              ],
              onChanged: busy ? null : (v) => setState(() => category = v!),
            ),
            TextField(
              controller: message,
              minLines: 3,
              maxLines: 7,
              maxLength: 1500,
              enabled: !busy,
              decoration: const InputDecoration(labelText: 'Mô tả vấn đề'),
            ),
            if (error != null)
              Text(
                error!,
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
          ],
        ),
      ),
    ),
    actions: [
      TextButton(
        onPressed: busy ? null : () => Navigator.pop(context),
        child: const Text('Hủy'),
      ),
      FilledButton(
        onPressed: busy ? null : send,
        child: Text(busy ? 'Đang gửi…' : 'Gửi phản hồi'),
      ),
    ],
  );
}

class ContentReportsScreen extends ConsumerStatefulWidget {
  const ContentReportsScreen({super.key, this.review = false});
  final bool review;
  @override
  ConsumerState<ContentReportsScreen> createState() =>
      _ContentReportsScreenState();
}

class _ContentReportsScreenState extends ConsumerState<ContentReportsScreen> {
  late Future<List<Json>> rows;
  String status = 'all';
  int offset = 0;
  @override
  void initState() {
    super.initState();
    load();
  }

  void load() {
    rows = ref
        .read(apiProvider)
        .contentReports(
          review: widget.review,
          status: status == 'all' ? null : status,
          offset: offset,
        );
  }

  void refresh() => setState(load);
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: Text(
        widget.review ? 'Xử lý phản hồi nội dung' : 'Phản hồi của tôi',
      ),
      actions: [
        IconButton(
          onPressed: refresh,
          tooltip: 'Tải lại phản hồi',
          icon: const Icon(Icons.refresh),
        ),
      ],
    ),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          widget.review
              ? 'Phản hồi của học viên bạn đang quản lý. Trả lời không sửa đáp án gốc hoặc điểm đã lưu; nội dung cần sửa phải được biên tập và duyệt lại.'
              : 'Theo dõi câu hỏi, tài liệu bạn đã báo lỗi. Giáo viên đang quản lý bạn và người quản lý hệ thống có thể xem phản hồi.',
        ),
        DropdownButtonFormField<String>(
          initialValue: status,
          decoration: const InputDecoration(labelText: 'Trạng thái phản hồi'),
          items: [
            const DropdownMenuItem(
              value: 'all',
              child: Text('Tất cả trạng thái'),
            ),
            for (final e in reportStatuses.entries)
              DropdownMenuItem(value: e.key, child: Text(e.value)),
          ],
          onChanged: (v) => setState(() {
            status = v!;
            offset = 0;
            load();
          }),
        ),
        FutureBuilder<List<Json>>(
          future: rows,
          builder: (context, snapshot) {
            if (snapshot.hasError) return Text(accountError(snapshot.error!));
            if (!snapshot.hasData) return const LinearProgressIndicator();
            final data = snapshot.data!;
            return Column(
              children: [
                if (data.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(20),
                    child: Text('Chưa có phản hồi trong mục này.'),
                  ),
                for (final row in data)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            row['target_title'],
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          Text(
                            '${reportStatuses[row['status']]} · ${reportCategories[row['category']]}',
                          ),
                          if (row['reporter'] != null)
                            Text(
                              'Người gửi: ${row['reporter']['display_name']} (${row['reporter']['username']})',
                            ),
                          Text(
                            'Gửi lúc: ${DateTime.parse(row['created_at']).toLocal()}',
                          ),
                          if ((row['excerpt'] as String).isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.symmetric(vertical: 8),
                              child: SelectableText(row['excerpt']),
                            ),
                          SelectableText('Phản hồi: ${row['message']}'),
                          if ((row['response'] as String).isNotEmpty)
                            Padding(
                              padding: const EdgeInsets.only(top: 12),
                              child: SelectableText(
                                'Trả lời: ${row['response']}',
                              ),
                            ),
                          if (widget.review &&
                              ['open', 'in_review'].contains(row['status']))
                            TextButton.icon(
                              icon: const Icon(Icons.reply),
                              label: const Text('Xem xét và trả lời'),
                              onPressed: () async {
                                final saved = await showDialog<bool>(
                                  context: context,
                                  builder: (_) => _ReviewDialog(report: row),
                                );
                                if (saved == true && mounted) refresh();
                              },
                            ),
                        ],
                      ),
                    ),
                  ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    TextButton(
                      onPressed: offset == 0
                          ? null
                          : () => setState(() {
                              offset -= 30;
                              load();
                            }),
                      child: const Text('Trang trước'),
                    ),
                    Text('Trang ${offset ~/ 30 + 1}'),
                    TextButton(
                      onPressed: data.length < 30
                          ? null
                          : () => setState(() {
                              offset += 30;
                              load();
                            }),
                      child: const Text('Trang sau'),
                    ),
                  ],
                ),
              ],
            );
          },
        ),
      ],
    ),
  );
}

class _ReviewDialog extends ConsumerStatefulWidget {
  const _ReviewDialog({required this.report});
  final Json report;
  @override
  ConsumerState<_ReviewDialog> createState() => _ReviewDialogState();
}

class _ReviewDialogState extends ConsumerState<_ReviewDialog> {
  late final response = TextEditingController(text: widget.report['response']);
  String status = 'in_review';
  String? error;
  bool busy = false;
  @override
  void dispose() {
    response.dispose();
    super.dispose();
  }

  Future<void> save() async {
    if (response.text.trim().length < 5) {
      setState(() => error = 'Cần giải thích ít nhất 5 ký tự.');
      return;
    }
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await ref.read(apiProvider).reviewContentReport(widget.report['id'], {
        'revision': widget.report['revision'],
        'status': status,
        'response': response.text.trim(),
      });
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() {
          error = accountError(e);
          busy = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
    title: const Text('Xem xét phản hồi'),
    content: SizedBox(
      width: 520,
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Đã xử lý/Không cần sửa sẽ đóng phản hồi. Việc này không sửa câu hỏi, tài liệu hoặc điểm bài làm.',
            ),
            DropdownButtonFormField<String>(
              initialValue: status,
              decoration: const InputDecoration(labelText: 'Kết quả xem xét'),
              items: [
                for (final key in ['in_review', 'resolved', 'dismissed'])
                  DropdownMenuItem(
                    value: key,
                    child: Text(reportStatuses[key]!),
                  ),
              ],
              onChanged: busy ? null : (v) => setState(() => status = v!),
            ),
            TextField(
              controller: response,
              minLines: 3,
              maxLines: 7,
              maxLength: 2000,
              enabled: !busy,
              decoration: const InputDecoration(
                labelText: 'Giải thích cho học viên',
              ),
            ),
            if (error != null) Text(error!),
          ],
        ),
      ),
    ),
    actions: [
      TextButton(
        onPressed: busy ? null : () => Navigator.pop(context),
        child: const Text('Hủy'),
      ),
      FilledButton(
        onPressed: busy ? null : save,
        child: Text(busy ? 'Đang lưu…' : 'Lưu trả lời'),
      ),
    ],
  );
}
