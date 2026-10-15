import 'package:flutter/services.dart';

const reportExportLabel = 'Sao chép bảng điểm CSV';
const reportExportMessage =
    'Đã sao chép bảng điểm. Dán vào tệp CSV để mở bằng bảng tính. Bảng gồm kết quả mọi môn, mọi lần nộp của thành viên hiện tại.';
Future<void> exportReport(String csv) =>
    Clipboard.setData(ClipboardData(text: csv));
