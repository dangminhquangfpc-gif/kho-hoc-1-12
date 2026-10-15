# Tiến độ

## Giai đoạn 1
- Đã có: kiến trúc, schema, 108 câu hỏi gốc/12 đề, catalog lớp/môn, FastAPI chấm điểm xác định, quyền admin cục bộ, capability cho guest, snapshot bài, nhập/duyệt/xuất bản, Flutter luyện đề/lưu bài/lịch sử, Next.js admin; thư viện 4 ghi chú/PDF gốc, tìm kiếm tiếng Việt không dấu, yêu thích/đọc gần đây; đánh dấu câu và tiến độ thiết bị; sửa câu hỏi/rollback revision, duyệt lại và giữ nguyên snapshot bài đang làm.
- Cần hoàn thành trước nghiệm thu MVP toàn bộ: Supabase Auth/Storage và adapter schema production; rate limiting phân tán; kiểm thử Android thiết bị và AAB (APK debug đã build được); kiểm duyệt chuyên môn; policy/privacy cuối cùng.
- Database SQL có RLS được kiểm tra trên PostgreSQL local với shim auth.uid; không khẳng định đã triển khai Supabase hosted.

## Giai đoạn 2
AI interface đã có; không có provider hoạt động. Tiếp theo: rubric validation, OCR có bước sửa, confidence threshold, log chi phí, consent, quota và dataset đánh giá.

## Giai đoạn 3
Giáo viên/phụ huynh và liên kết có xác nhận; đồng bộ đa thiết bị; phân tích năng lực; mở rộng môn/lớp; cache nâng cao.

## Giai đoạn 4
JWT/server auth production, backup/retention, kiểm thử tải, Google Play policy mới nhất, signing bảo mật và kiểm thử kín. Chưa deploy hoặc xuất bản.


## Dữ liệu mở rộng 15/10/2026

Bản thử hiện có 1.566 câu, 219 đề và 199 tài liệu; có dữ liệu cho mọi tổ hợp lớp–môn trong danh mục. Đây là dữ liệu tự biên soạn hướng tới Kết nối tri thức, chưa đối chiếu toàn bộ SGK hiện hành. Xem `docs/CURRICULUM_EXPANSION.md` để phân biệt biến thể Toán, bộ ôn nền và phần còn thiếu.


### Thư viện Internet 15/10/2026

Bổ sung 1.934 mục nguồn Internet, tổng 2.133 tài liệu/liên kết; gồm 1.444 trang đề giữa/cuối kỳ KNTT và 104 mục tốt nghiệp dùng chung. Đây là liên kết nguồn, không phải PDF/câu hỏi của bên thứ ba được sao chép vào app. Chi tiết, quyền sử dụng và phần còn thiếu: `docs/INTERNET_LIBRARY.md`.
