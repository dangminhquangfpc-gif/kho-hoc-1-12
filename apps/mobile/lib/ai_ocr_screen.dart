import 'dart:async';
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'ocr_runtime.dart';
import 'repository.dart';

/// Returns edited, acknowledged text. Closing the page never changes an answer.
Future<String?> showOcrTextDialog(
  BuildContext context, {
  String initialText = '',
}) => Navigator.of(context).push<String>(
  MaterialPageRoute(
    builder: (_) => AiOcrScreen(initialText: initialText, returnTextOnly: true),
    fullscreenDialog: true,
  ),
);

class AiOcrScreen extends ConsumerStatefulWidget {
  const AiOcrScreen({
    super.key,
    this.initialText = '',
    this.returnTextOnly = false,
    this.recognizer,
    this.attemptId,
    this.questionId,
    this.initialGrade,
    this.initialSubject,
  });
  final String initialText;
  final bool returnTextOnly;
  final OcrRecognizer? recognizer;
  final String? attemptId, questionId, initialSubject;
  final int? initialGrade;
  @override
  ConsumerState<AiOcrScreen> createState() => _AiOcrState();
}

class _AiOcrState extends ConsumerState<AiOcrScreen> {
  late final TextEditingController text;
  late final OcrRecognizer recognizer;
  bool recognizing = false, acknowledged = false, aiBusy = false;
  bool statusBusy = false;
  bool useReference = true;
  int generation = 0, grade = 5;
  String? subject, ocrError, aiError, statusError;
  double? confidence;
  List<String> warnings = [];
  Uint8List? preview;
  Json? status, explanation;

  @override
  void initState() {
    super.initState();
    text = TextEditingController(text: widget.initialText);
    recognizer = widget.recognizer ?? const DeviceOcrRecognizer();
    grade =
        (widget.initialGrade ??
                ref.read(authUserProvider)?['grade'] as int? ??
                5)
            .clamp(1, 12);
    subject = widget.initialSubject;
    if (!widget.returnTextOnly && ref.read(authUserProvider) != null) {
      unawaited(loadStatus());
    }
  }

  @override
  void dispose() {
    generation++;
    if (recognizing) recognizer.cancel();
    text.dispose();
    super.dispose();
  }

  Future<void> loadStatus() async {
    setState(() {
      statusBusy = true;
      statusError = null;
      status = null;
    });
    try {
      final result = await ref.read(apiProvider).aiStatus();
      if (mounted) setState(() => status = result);
    } catch (e) {
      if (mounted) setState(() => statusError = readableError(e));
    } finally {
      if (mounted) setState(() => statusBusy = false);
    }
  }

  void cancelOcr() {
    generation++;
    recognizer.cancel();
    setState(() {
      recognizing = false;
      ocrError = 'Đã hủy nhận dạng. Văn bản đang có được giữ nguyên.';
    });
  }

  Future<void> scan() async {
    final current = ++generation;
    setState(() {
      recognizing = true;
      ocrError = null;
    });
    try {
      final result = await recognizer.recognize().timeout(
        const Duration(minutes: 3),
        onTimeout: () {
          recognizer.cancel();
          throw TimeoutException('Nhận chữ quá lâu. Hãy thử ảnh nhỏ, rõ hơn.');
        },
      );
      if (!mounted || current != generation || result == null) return;
      Uint8List? image;
      final dataUrl = result.previewDataUrl;
      if (dataUrl != null &&
          dataUrl.length < 32 * 1024 * 1024 &&
          RegExp(r'^data:image/(png|jpeg|webp);base64,').hasMatch(dataUrl)) {
        try {
          image = base64Decode(dataUrl.substring(dataUrl.indexOf(',') + 1));
        } on FormatException {
          // A missing preview must not discard recognized or edited text.
        }
      }
      setState(() {
        preview = image;
        confidence = result.confidence;
        warnings = result.warnings;
        if (result.text.trim().isNotEmpty) {
          text.text = result.text.substring(
            0,
            result.text.length.clamp(0, 6000),
          );
          acknowledged = false;
          explanation = null;
          aiError = null;
        } else {
          ocrError = 'Không đọc được chữ. Văn bản đang có được giữ nguyên.';
        }
        if (result.text.length > 6000) {
          warnings = [
            ...warnings,
            'Chỉ giữ 6.000 ký tự đầu. Hãy chia nhỏ ảnh.',
          ];
        }
      });
    } catch (e) {
      if (mounted && current == generation) {
        setState(() => ocrError = readableError(e, ocr: true));
      }
    } finally {
      if (mounted && current == generation) {
        setState(() => recognizing = false);
      }
    }
  }

  Future<void> askAi(String selectedSubject) async {
    if (!acknowledged || aiBusy || text.text.trim().length < 3) return;
    final host = status?['provider_host'] as String? ?? '';
    if (status?['configured'] != true || host.isEmpty) return;
    final consent = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Gửi văn bản để nhận hướng dẫn?'),
        content: Text(
          'Văn bản bạn vừa kiểm tra sẽ được gửi qua máy chủ Tự học 111 đến dịch vụ AI tại $host. '
          '${widget.attemptId != null && useReference ? 'Máy chủ còn gửi đề bài, các lựa chọn, đáp án và lời giải tham chiếu của câu đã nộp này; sửa ô văn bản không sửa những dữ liệu tham chiếu đó. ' : ''}'
          'Ảnh không được gửi. Không đưa tên, mật khẩu hoặc thông tin riêng tư vào văn bản. Kết quả AI có thể sai và cần kiểm tra lại.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Đồng ý gửi văn bản'),
          ),
        ],
      ),
    );
    if (consent != true || !mounted) return;
    setState(() {
      aiBusy = true;
      aiError = null;
      explanation = null;
    });
    try {
      final result = await ref
          .read(apiProvider)
          .explainAi(
            grade: grade,
            subject: selectedSubject,
            text: text.text.trim(),
            consent: true,
            expectedProviderHost: host,
            attemptId: useReference ? widget.attemptId : null,
            questionId: useReference ? widget.questionId : null,
          );
      if (mounted) setState(() => explanation = result);
    } catch (e) {
      if (mounted) setState(() => aiError = readableError(e));
      if (e is DioException && e.response?.statusCode == 409 && mounted) {
        unawaited(loadStatus());
      }
    } finally {
      if (mounted) setState(() => aiBusy = false);
    }
  }

  String readableError(Object e, {bool ocr = false}) {
    if (e is TimeoutException) {
      return 'Xử lý quá lâu. Văn bản được giữ nguyên; hãy thử lại.';
    }
    if (e is DioException) {
      final detail = e.response?.data;
      if (detail is Map && detail['detail'] is String) return detail['detail'];
      if (e.response?.statusCode == 401) return 'Hãy đăng nhập lại để dùng AI.';
      if (e.response?.statusCode == 429) {
        return 'Đã tới giới hạn sử dụng AI. Hãy thử lại sau.';
      }
      return 'Chưa kết nối được dịch vụ AI. Văn bản được giữ nguyên; hãy thử lại.';
    }
    if (ocr) {
      final message = '$e';
      return message.length <= 400
          ? '$message\nVăn bản đang có được giữ nguyên.'
          : 'Chưa nhận chữ được. Hãy thử ảnh rõ hơn hoặc nhập văn bản.';
    }
    return 'Chưa tải được trạng thái AI. Hãy thử lại.';
  }

  Widget errorText(String value) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Text(
      value,
      style: TextStyle(color: Theme.of(context).colorScheme.error),
    ),
  );

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(authUserProvider);
    final locked = recognizing || aiBusy;
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.returnTextOnly
              ? 'Nhập câu trả lời từ ảnh'
              : 'Ảnh và trợ lý học tập',
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Nhận chữ ngay trên thiết bị, không tải ảnh lên máy chủ. Hỗ trợ ảnh chữ in tiếng Việt và tiếng Anh; chữ viết tay, phân số, số mũ và hình vẽ có thể đọc sai. Ảnh tối đa 8 MiB, 16 triệu điểm ảnh.',
          ),
          const SizedBox(height: 12),
          if (!recognizer.available)
            const Text(
              kIsWeb
                  ? 'Bộ nhận chữ chưa tải được. Hãy tải lại trang hoặc nhập, dán văn bản bên dưới.'
                  : 'Nhận chữ từ ảnh hiện có trên bản web và demo Windows chạy trong trình duyệt. Trên bản điện thoại này, bạn có thể nhập hoặc dán văn bản bên dưới.',
            ),
          FilledButton.icon(
            onPressed: locked || !recognizer.available ? null : scan,
            icon: const Icon(Icons.document_scanner_outlined),
            label: Text(recognizing ? 'Đang đọc ảnh…' : 'Chọn ảnh để nhận chữ'),
          ),
          if (recognizing) ...[
            const LinearProgressIndicator(),
            const Text(
              'Lần đầu có thể cần tải bộ nhận chữ. Bạn có thể hủy bất kỳ lúc nào.',
            ),
            TextButton(
              onPressed: cancelOcr,
              child: const Text('Hủy nhận dạng'),
            ),
          ],
          if (ocrError != null) errorText(ocrError!),
          if (preview != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Image.memory(
                preview!,
                height: 240,
                fit: BoxFit.contain,
                semanticLabel: 'Ảnh vừa chọn, chỉ lưu trong bộ nhớ trang',
                errorBuilder: (_, __, ___) =>
                    const Text('Không hiển thị được ảnh xem trước.'),
              ),
            ),
          if (confidence != null)
            Text(
              'Độ tin cậy nhận chữ: ${confidence!.clamp(0, 100).round()}% — đây không phải điểm bài làm.',
            ),
          if (confidence != null && confidence! < 80)
            const Text(
              'Ảnh có độ tin cậy thấp. Hãy kiểm tra kỹ từng số, dấu tiếng Việt và phép tính.',
            ),
          for (final warning in warnings) Text(warning),
          const SizedBox(height: 12),
          TextField(
            key: const Key('ocr-edited-text'),
            controller: text,
            enabled: !locked,
            minLines: 5,
            maxLines: 12,
            maxLength: 6000,
            inputFormatters: [LengthLimitingTextInputFormatter(6000)],
            decoration: const InputDecoration(
              labelText: 'Văn bản để kiểm tra và chỉnh sửa',
              border: OutlineInputBorder(),
            ),
            onChanged: (_) => setState(() {
              acknowledged = false;
              explanation = null;
              aiError = null;
            }),
          ),
          CheckboxListTile(
            value: acknowledged,
            controlAffinity: ListTileControlAffinity.leading,
            title: const Text('Tôi đã kiểm tra văn bản'),
            subtitle: const Text(
              'Sửa lại chữ, số, đơn vị và công thức trước khi sử dụng.',
            ),
            onChanged: locked || text.text.trim().isEmpty
                ? null
                : (v) => setState(() => acknowledged = v ?? false),
          ),
          if (widget.returnTextOnly) ...[
            const Text(
              'Chỉ đưa văn bản đã sửa vào ô trả lời. Bạn vẫn cần kiểm tra bài và tự bấm nộp.',
            ),
            FilledButton(
              onPressed: !locked && acknowledged && text.text.trim().isNotEmpty
                  ? () => Navigator.pop(context, text.text.trim())
                  : null,
              child: const Text('Dùng văn bản này cho câu trả lời'),
            ),
          ] else ...[
            const Divider(height: 32),
            Text(
              'Trợ lý học tập AI',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const Text(
              'AI chỉ gợi ý cách học và cách làm, có thể sai. Hãy đối chiếu SGK và giáo viên; nội dung này không thay đổi điểm bài làm.',
            ),
            if (widget.attemptId != null)
              CheckboxListTile(
                value: useReference,
                title: const Text(
                  'Dùng đáp án và lời giải đã lưu làm tham chiếu',
                ),
                subtitle: const Text(
                  'Bỏ chọn để chỉ gửi văn bản đã kiểm tra; AI sẽ hướng dẫn tổng quát.',
                ),
                controlAffinity: ListTileControlAffinity.leading,
                onChanged: locked
                    ? null
                    : (v) => setState(() {
                        useReference = v ?? false;
                        explanation = null;
                      }),
              ),
            if (user == null) ...[
              const Text(
                'Bạn có thể nhận chữ mà không đăng nhập. Đăng nhập để yêu cầu hướng dẫn AI.',
              ),
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                  context.go('/account');
                },
                child: const Text('Đăng nhập để dùng AI'),
              ),
            ] else ...[
              if (statusBusy) const LinearProgressIndicator(),
              if (statusError != null) errorText(statusError!),
              if (!statusBusy &&
                  status?['configured'] != true &&
                  statusError == null)
                const Text(
                  'AI chưa được cấu hình trên máy chủ này. Bạn vẫn có thể nhận chữ, chỉnh sửa và dùng tài liệu, bài luyện có sẵn.',
                ),
              TextButton.icon(
                onPressed: statusBusy || aiBusy ? null : loadStatus,
                icon: const Icon(Icons.refresh),
                label: const Text('Kiểm tra lại trạng thái AI'),
              ),
              DropdownButtonFormField<int>(
                initialValue: grade,
                decoration: const InputDecoration(labelText: 'Lớp'),
                items: [
                  for (var n = 1; n <= 12; n++)
                    DropdownMenuItem(value: n, child: Text('Lớp $n')),
                ],
                onChanged: locked || widget.attemptId != null
                    ? null
                    : (v) => setState(() {
                        grade = v!;
                        subject = null;
                        explanation = null;
                      }),
              ),
              ref
                  .watch(subjectsProvider(grade))
                  .when(
                    loading: () => const LinearProgressIndicator(),
                    error: (_, __) => TextButton(
                      onPressed: () => ref.invalidate(subjectsProvider(grade)),
                      child: const Text('Chưa tải được môn học. Thử lại'),
                    ),
                    data: (subjects) {
                      if (subjects.isEmpty) {
                        return const Text('Lớp này chưa có môn học.');
                      }
                      final selected = subjects.any((s) => s['id'] == subject)
                          ? subject!
                          : subjects.first['id'] as String;
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          DropdownButtonFormField<String>(
                            key: ValueKey('ai-subject-$grade-$selected'),
                            initialValue: selected,
                            decoration: const InputDecoration(
                              labelText: 'Môn học',
                            ),
                            items: [
                              for (final s in subjects)
                                DropdownMenuItem(
                                  value: s['id'] as String,
                                  child: Text(s['name'] as String),
                                ),
                            ],
                            onChanged: locked || widget.attemptId != null
                                ? null
                                : (v) => setState(() {
                                    subject = v;
                                    explanation = null;
                                  }),
                          ),
                          if (status?['configured'] == true)
                            Text(
                              'Dịch vụ: ${status!['provider_host']} · Mô hình: ${status!['model']}',
                            ),
                          if (text.text.trim().length < 3)
                            const Text(
                              'Nhập ít nhất 3 ký tự để yêu cầu AI hướng dẫn.',
                            ),
                          const SizedBox(height: 12),
                          FilledButton.icon(
                            onPressed:
                                !locked &&
                                    acknowledged &&
                                    text.text.trim().length >= 3 &&
                                    status?['configured'] == true
                                ? () => askAi(selected)
                                : null,
                            icon: const Icon(Icons.auto_awesome_outlined),
                            label: Text(
                              aiBusy
                                  ? 'Đang xin hướng dẫn…'
                                  : 'Xin hướng dẫn từ AI',
                            ),
                          ),
                        ],
                      );
                    },
                  ),
              if (aiBusy) const LinearProgressIndicator(),
              if (aiError != null) errorText(aiError!),
              if (explanation != null) ...[
                const SizedBox(height: 20),
                Text(
                  'Hướng dẫn AI cần kiểm tra lại',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Text(
                  explanation!['grounded'] == true
                      ? 'AI có tham khảo câu hỏi, đáp án và lời giải đã lưu của câu đã nộp này.'
                      : 'Hướng dẫn tổng quát; chưa đối chiếu lời giải của một câu đã nộp.',
                ),
                SelectableText('${explanation!['explanation'] ?? ''}'),
                for (final step in explanation!['steps'] as List? ?? [])
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: SelectableText('$step'),
                  ),
                for (final uncertainty
                    in explanation!['uncertainties'] as List? ?? [])
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text('Cần kiểm tra: $uncertainty'),
                  ),
                if (explanation!['needs_review'] == true)
                  const Text(
                    'AI chưa chắc chắn. Hãy nhờ giáo viên kiểm tra trước khi dùng.',
                  ),
                Text(
                  'Nguồn xử lý: ${explanation!['provider_host']} · ${explanation!['model']}',
                ),
              ],
            ],
          ],
          const SizedBox(height: 24),
          const Text(
            'Ảnh và văn bản ở màn hình này chỉ giữ trong bộ nhớ trong lúc mở trang, không tự lưu vào lịch sử hoặc bản nháp.',
          ),
        ],
      ),
    );
  }
}
