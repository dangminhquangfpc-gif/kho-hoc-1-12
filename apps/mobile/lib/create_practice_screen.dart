import 'dart:math' as math;
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'main.dart' show Shell, Failure;
import 'repository.dart';

final practiceOptionsProvider =
    FutureProvider.family<Json, ({int grade, String subject})>(
      (ref, f) => ref.watch(apiProvider).practiceOptions(f.grade, f.subject),
    );

class CreatePracticeScreen extends ConsumerStatefulWidget {
  const CreatePracticeScreen({super.key});
  @override
  ConsumerState<CreatePracticeScreen> createState() => _CreatePracticeState();
}

class _CreatePracticeState extends ConsumerState<CreatePracticeScreen> {
  int grade = 1, desiredCount = 10;
  String subject = 'toan',
      topic = '',
      difficulty = '',
      textbook = 'ket_noi_tri_thuc';
  bool busy = false;
  String? error;

  Future<void> start(int count) async {
    setState(() {
      busy = true;
      error = null;
    });
    try {
      final p = await ref.read(preferencesProvider.future);
      if (LocalStore(p).current != null) {
        if (mounted) context.go('/practice');
        return;
      }
      final attempt = await ref.read(apiProvider).createPractice({
        'grade': grade,
        'subject': subject,
        'count': count,
        if (topic.isNotEmpty) 'topic': topic,
        if (difficulty.isNotEmpty) 'difficulty': difficulty,
        if (textbook.isNotEmpty) 'textbook': textbook,
      });
      await LocalStore(p).save({
        ...attempt,
        'backend_url': ref.read(apiProvider).baseUrl,
        'answers': <String, List<String>>{},
      });
      if (mounted) context.go('/practice');
    } on DioException catch (e) {
      if (mounted) {
        setState(
          () => error = e.response?.statusCode == 422
              ? 'Số câu hiện có không đủ với bộ lọc này. Hãy tải lại ngân hàng hoặc giảm số câu.'
              : 'Chưa tạo được đề. Kiểm tra kết nối rồi thử lại.',
        );
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => error = 'Chưa lưu được bài. Hãy kiểm tra bộ nhớ rồi thử lại.',
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final filter = (grade: grade, subject: subject);
    return Shell(
      title: 'Tạo đề luyện tập',
      index: 2,
      child: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const Text(
            'Chọn số câu, chủ đề và độ khó. Mỗi câu chỉ xuất hiện một lần trong đề.',
          ),
          const Text(
            'Đề tự tạo từ ngân hàng hiện có, chưa bảo đảm phủ đủ SGK mọi môn. Chỉ dùng câu đã xuất bản có thể chấm theo đáp án.',
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<int>(
            initialValue: grade,
            decoration: const InputDecoration(labelText: 'Lớp học'),
            items: [
              for (var n = 1; n <= 12; n++)
                DropdownMenuItem(value: n, child: Text('Lớp $n')),
            ],
            onChanged: busy
                ? null
                : (n) => setState(() {
                    grade = n!;
                    subject = 'toan';
                    topic = '';
                    error = null;
                  }),
          ),
          ref
              .watch(subjectsProvider(grade))
              .when(
                data: (rows) => DropdownButtonFormField<String>(
                  key: ValueKey(grade),
                  initialValue: subject,
                  decoration: const InputDecoration(labelText: 'Môn học'),
                  items: [
                    for (final s in rows)
                      DropdownMenuItem(
                        value: s['id'] as String,
                        child: Text(s['name']),
                      ),
                  ],
                  onChanged: busy
                      ? null
                      : (s) => setState(() {
                          subject = s!;
                          topic = '';
                          error = null;
                        }),
                ),
                loading: () => const LinearProgressIndicator(),
                error: (_, _) => Failure(
                  retry: () => ref.invalidate(subjectsProvider(grade)),
                ),
              ),
          ref
              .watch(practiceOptionsProvider(filter))
              .when(
                data: (data) {
                  final groups = (data['groups'] as List).cast<Json>();
                  final available = groups
                      .where(
                        (g) =>
                            (topic.isEmpty || g['topic'] == topic) &&
                            (difficulty.isEmpty ||
                                g['difficulty'] == difficulty) &&
                            (textbook.isEmpty || g['textbook'] == textbook),
                      )
                      .fold<int>(0, (sum, g) => sum + (g['count'] as int));
                  final count = math.min(desiredCount, math.min(50, available));
                  final counts = {
                    1,
                    5,
                    10,
                    20,
                    30,
                    50,
                    if (count > 0) count,
                  }.where((n) => n <= available).toList()..sort();
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const SizedBox(height: 12),
                      DropdownButtonFormField<String>(
                        key: ValueKey('$grade/$subject'),
                        initialValue: topic,
                        decoration: const InputDecoration(labelText: 'Chủ đề'),
                        items: [
                          const DropdownMenuItem(
                            value: '',
                            child: Text('Tất cả chủ đề'),
                          ),
                          for (final t in data['topics'] as List)
                            DropdownMenuItem(
                              value: t['id'] as String,
                              child: Text('${t['name']} (${t['count']} câu)'),
                            ),
                        ],
                        isExpanded: true,
                        onChanged: busy
                            ? null
                            : (v) => setState(() => topic = v!),
                      ),
                      DropdownButtonFormField<String>(
                        initialValue: difficulty,
                        decoration: const InputDecoration(labelText: 'Độ khó'),
                        items: const [
                          DropdownMenuItem(
                            value: '',
                            child: Text('Tất cả mức độ'),
                          ),
                          DropdownMenuItem(
                            value: 'easy',
                            child: Text('Cơ bản'),
                          ),
                          DropdownMenuItem(
                            value: 'medium',
                            child: Text('Vận dụng'),
                          ),
                          DropdownMenuItem(
                            value: 'hard',
                            child: Text('Nâng cao'),
                          ),
                        ],
                        onChanged: busy
                            ? null
                            : (v) => setState(() => difficulty = v!),
                      ),
                      DropdownButtonFormField<String>(
                        initialValue: textbook,
                        decoration: const InputDecoration(labelText: 'Bộ sách'),
                        items: const [
                          DropdownMenuItem(
                            value: '',
                            child: Text('Tất cả bộ sách'),
                          ),
                          DropdownMenuItem(
                            value: 'ket_noi_tri_thuc',
                            child: Text('Kết nối tri thức'),
                          ),
                          DropdownMenuItem(
                            value: 'independent',
                            child: Text('Không phụ thuộc bộ sách'),
                          ),
                          DropdownMenuItem(
                            value: 'chan_troi_sang_tao',
                            child: Text('Chân trời sáng tạo'),
                          ),
                          DropdownMenuItem(
                            value: 'canh_dieu',
                            child: Text('Cánh Diều'),
                          ),
                        ],
                        isExpanded: true,
                        onChanged: busy
                            ? null
                            : (v) => setState(() => textbook = v!),
                      ),
                      const SizedBox(height: 16),
                      Text('Có $available câu phù hợp với bộ lọc.'),
                      if (counts.isNotEmpty)
                        DropdownButtonFormField<int>(
                          key: ValueKey('$available/$count'),
                          initialValue: count,
                          decoration: const InputDecoration(
                            labelText: 'Số câu',
                          ),
                          items: [
                            for (final n in counts)
                              DropdownMenuItem(value: n, child: Text('$n câu')),
                          ],
                          onChanged: busy
                              ? null
                              : (n) => setState(() => desiredCount = n!),
                        ),
                      const SizedBox(height: 20),
                      FilledButton.icon(
                        onPressed: busy || count == 0
                            ? null
                            : () => start(count),
                        icon: const Icon(Icons.shuffle),
                        label: Text(
                          busy ? 'Đang tạo đề…' : 'Bắt đầu đề $count câu',
                        ),
                      ),
                      if (available == 0)
                        const Text(
                          'Chưa có câu phù hợp. Hãy đổi chủ đề, độ khó hoặc bộ sách.',
                        ),
                    ],
                  );
                },
                loading: () => const LinearProgressIndicator(),
                error: (_, _) => Failure(
                  retry: () => ref.invalidate(practiceOptionsProvider(filter)),
                ),
              ),
          if (error != null)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Text(error!),
            ),
        ],
      ),
    );
  }
}
