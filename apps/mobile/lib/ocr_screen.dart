import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'ocr_runtime.dart';

/// Returns edited, acknowledged text. Closing the page never changes an answer.
Future<String?> showOcrTextDialog(
  BuildContext context, {
  String initialText = '',
}) => Navigator.of(context).push<String>(
  MaterialPageRoute(
    builder: (_) => OcrScreen(initialText: initialText, returnTextOnly: true),
    fullscreenDialog: true,
  ),
);

class OcrScreen extends StatefulWidget {
  const OcrScreen({
    super.key,
    this.initialText = '',
    this.returnTextOnly = false,
    this.recognizer,
  });
  final String initialText;
  final bool returnTextOnly;

  final OcrRecognizer? recognizer;
  @override
  State<OcrScreen> createState() => _OcrState();
}

class _OcrState extends State<OcrScreen> {
  late final TextEditingController text;
  late final OcrRecognizer recognizer;
  bool recognizing = false, acknowledged = false, copying = false;
  bool hasOcrResult = false;
  int generation = 0;
  String? ocrError;
  double? confidence;
  List<String> warnings = [];
  Uint8List? preview;

  @override
  void initState() {
    super.initState();
    text = TextEditingController(text: widget.initialText);
    recognizer = widget.recognizer ?? const DeviceOcrRecognizer();
  }

  @override
  void dispose() {
    generation++;
    if (recognizing) recognizer.cancel();
    text.dispose();
    super.dispose();
  }

  void cancelOcr() {
    generation++;
    recognizer.cancel();
    setState(() {
      recognizing = false;
      ocrError = 'Đã hủy nhận dạng. Văn bản đang có được giữ nguyên.';
    });
  }

  Future<void> copyCheckedText() async {
    if (!acknowledged || copying || text.text.trim().isEmpty) return;
    setState(() => copying = true);
    try {
      await Clipboard.setData(ClipboardData(text: text.text.trim()));
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Đã sao chép văn bản.')));
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          ocrError = 'Chưa sao chép được. Văn bản đang có được giữ nguyên.';
        });
      }
    } finally {
      if (mounted) setState(() => copying = false);
    }
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
        hasOcrResult = true;
        preview = image;
        confidence = result.confidence;
        warnings = result.warnings;
        if (result.text.trim().isNotEmpty) {
          text.text = result.text.substring(
            0,
            result.text.length.clamp(0, 6000),
          );
          acknowledged = false;
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
        setState(() => ocrError = readableError(e));
      }
    } finally {
      if (mounted && current == generation) {
        setState(() => recognizing = false);
      }
    }
  }

  String readableError(Object error) {
    if (error is TimeoutException) {
      return 'Xử lý quá lâu. Văn bản được giữ nguyên; hãy thử lại.';
    }
    final message = '$error';
    return message.length <= 400
        ? '$message\nVăn bản đang có được giữ nguyên.'
        : 'Chưa nhận chữ được. Hãy thử ảnh rõ hơn hoặc nhập văn bản.';
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
    final locked = recognizing || copying;
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.returnTextOnly
              ? 'Nhập câu trả lời từ ảnh'
              : 'Nhận chữ trên thiết bị',
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
                  : 'Bản chạy trên thiết bị này chưa hỗ trợ nhận chữ từ ảnh. Bạn có thể nhập, dán văn bản bên dưới hoặc dùng bản web.',
            ),
          if (!kIsWeb &&
              recognizer.available &&
              (defaultTargetPlatform == TargetPlatform.android ||
                  defaultTargetPlatform == TargetPlatform.iOS))
            const Text(
              'Google ML Kit có thể gửi thông tin thiết bị, ứng dụng và hiệu năng cho Google để chẩn đoán và thống kê sử dụng.',
            ),
          FilledButton.icon(
            onPressed: locked || !recognizer.available ? null : scan,
            icon: const Icon(Icons.document_scanner_outlined),
            label: Text(recognizing ? 'Đang đọc ảnh…' : 'Chọn ảnh để nhận chữ'),
          ),
          if (recognizing) ...[
            const LinearProgressIndicator(),
            const Text(
              kIsWeb
                  ? 'Lần đầu có thể cần tải bộ nhận chữ. Bạn có thể hủy bất kỳ lúc nào.'
                  : 'Đang nhận chữ trên thiết bị. Bạn có thể hủy bất kỳ lúc nào.',
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
                semanticLabel: 'Ảnh vừa chọn để nhận chữ',
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
          if (hasOcrResult && confidence == null)
            const Text(
              'Bộ nhận chữ không cung cấp chỉ số độ tin cậy. Hãy kiểm tra kỹ từng số, dấu tiếng Việt và phép tính.',
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
            const Text(
              'Bạn có thể nhận chữ, chỉnh sửa và sao chép mà không cần tài khoản hay kết nối máy chủ. Văn bản chỉ được chép vào bộ nhớ tạm khi bạn chọn sao chép.',
            ),
            FilledButton.icon(
              onPressed: !locked && acknowledged && text.text.trim().isNotEmpty
                  ? copyCheckedText
                  : null,
              icon: const Icon(Icons.copy_outlined),
              label: const Text('Sao chép văn bản đã kiểm tra'),
            ),
          ],
          const SizedBox(height: 24),
          const Text(
            'Ứng dụng chỉ dùng ảnh và văn bản ở màn hình này để xử lý yêu cầu hiện tại, không tự thêm vào lịch sử hoặc bản nháp.',
          ),
        ],
      ),
    );
  }
}
