import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'main.dart' show Shell, Failure;
import 'repository.dart';
import 'study_progress.dart';
import 'account_screen.dart' show serverResultsProvider;

class ProgressScreen extends ConsumerStatefulWidget {
  const ProgressScreen({super.key});
  @override
  ConsumerState<ProgressScreen> createState() => _ProgressState();
}

class _ProgressState extends ConsumerState<ProgressScreen> {
  bool busy = false;
  String? error;
  Future<void> review(TopicProgress topic) async {
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
      final ids = topic.wrongQuestionIds.take(50).toList();
      final attempt = await ref.read(apiProvider).createPractice({
        'grade': topic.grade,
        'subject': topic.subject,
        'topic': topic.topic,
        'count': ids.length,
        'question_ids': ids,
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
          () => error = e.response?.statusCode == 409
              ? 'Một số câu đã được sửa hoặc gỡ khỏi ngân hàng. Hãy tạo đề mới theo chủ đề này.'
              : 'Chưa mở được bài ôn. Kiểm tra kết nối rồi thử lại.',
        );
      }
    } catch (_) {
      if (mounted) {
        setState(
          () => error = 'Chưa lưu được bài ôn trên thiết bị. Hãy thử lại.',
        );
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Shell(
    title: 'Tiến độ học tập',
    index: 3,
    child: ref
        .watch(preferencesProvider)
        .when(
          data: (p) {
            final offline = ref.watch(apiProvider).isOffline;
            final account = offline ? null : ref.watch(authUserProvider);
            final server = account == null
                ? null
                : ref.watch(serverResultsProvider);
            if (server?.isLoading == true) {
              return const Center(child: CircularProgressIndicator());
            }
            if (server?.hasError == true) {
              return Failure(
                retry: () => ref.invalidate(serverResultsProvider),
              );
            }
            final history = account == null
                ? LocalStore(p).history
                : server!.value!;
            final progress = StudyProgress.fromHistory(history);
            return ListView(
              padding: const EdgeInsets.all(24),
              children: [
                Text(
                  'Đã hoàn thành ${progress.completed} bài luyện tập',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                if (progress.averagePercent != null)
                  Text(
                    'Điểm trung bình: ${progress.averagePercent!.round()}% · ${progress.graded} bài đã chấm đủ',
                  ),
                const SizedBox(height: 12),
                Text(
                  offline
                      ? 'Điểm tự luyện chỉ lưu trên thiết bị, không tự đồng bộ hoặc gửi cho giáo viên. Mỗi câu tính lần làm mới nhất; câu cần kiểm tra thủ công chưa được tính điểm.'
                      : account == null
                      ? 'Thống kê trên thiết bị. Mỗi câu tính lần làm mới nhất; câu chờ duyệt chưa được tính điểm.'
                      : 'Thống kê từ tối đa 500 bài gần nhất trên tài khoản. Mỗi câu tính lần làm mới nhất; đây không phải đánh giá năng lực chính thức.',
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: () =>
                      context.go(account == null ? '/history' : '/account'),
                  icon: const Icon(Icons.history),
                  label: Text(
                    account == null
                        ? 'Lịch sử bài làm'
                        : 'Kết quả trên tài khoản',
                  ),
                ),
                if (!offline &&
                    ['manager', 'teacher'].contains(account?['role']))
                  OutlinedButton.icon(
                    onPressed: () => context.go('/create-practice'),
                    icon: const Icon(Icons.shuffle),
                    label: const Text('Tạo đề theo chủ đề'),
                  ),
                if (error != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    child: Text(error!),
                  ),
                const SizedBox(height: 20),
                Text(
                  'Chủ đề cần ôn và kết quả gần nhất',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                if (progress.topics.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'Chưa có đủ dữ liệu theo chủ đề. Hãy hoàn thành một đề để bắt đầu.',
                    ),
                  ),
                for (final topic in progress.topics)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Lớp ${topic.grade} · ${subjectNames[topic.subject] ?? topic.subject} · ${topic.name}',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          LinearProgressIndicator(value: topic.percent / 100),
                          const SizedBox(height: 8),
                          Text(
                            '${topic.percent.round()}% điểm · ${topic.correct}/${topic.attempted} câu đúng hoàn toàn',
                          ),
                          if (topic.wrongQuestionIds.isNotEmpty)
                            OutlinedButton.icon(
                              onPressed: busy ? null : () => review(topic),
                              icon: const Icon(Icons.refresh),
                              label: Text(
                                'Ôn ${topic.wrongQuestionIds.take(50).length} câu chưa đúng',
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                if (history.isNotEmpty && account == null)
                  const Padding(
                    padding: EdgeInsets.only(top: 16),
                    child: Text(
                      'Xóa một kết quả trong Lịch sử sẽ cập nhật lại thống kê. Các bài cũ thiếu thông tin lớp/chủ đề vẫn nằm trong Lịch sử.',
                    ),
                  ),
              ],
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, _) =>
              Failure(retry: () => ref.invalidate(preferencesProvider)),
        ),
  );
}
