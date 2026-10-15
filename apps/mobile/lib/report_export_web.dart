// Browser download stays in memory; authentication cookies/tokens never enter a URL.
// Selected only by the dart.library.html conditional export.
// ignore: deprecated_member_use, avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:convert';

const reportExportLabel = 'Tải bảng điểm CSV';
const reportExportMessage =
    'Đã tạo tệp CSV. Bảng gồm kết quả mọi môn, mọi lần nộp của thành viên hiện tại; học viên chưa nộp bài có điểm để trống.';
Future<void> exportReport(String csv) async {
  final url = html.Url.createObjectUrlFromBlob(
    html.Blob([
      utf8.encode(csv.startsWith('\ufeff') ? csv : '\ufeff$csv'),
    ], 'text/csv;charset=utf-8'),
  );
  final anchor = html.AnchorElement(href: url)
    ..download = 'tu-hoc-111-bang-diem.csv';
  anchor.click();
  Future<void>.delayed(
    const Duration(seconds: 30),
    () => html.Url.revokeObjectUrl(url),
  );
}
