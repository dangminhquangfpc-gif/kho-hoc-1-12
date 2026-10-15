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


## Trạng thái hiện hành — bản thử 2026.10.15.6

- Ngân hàng: 2.640 câu đang dùng, 306 đề cố định; 75 bài Toán 5 đã gắn mục lục nguồn
  thứ cấp; 1.934 liên kết nguồn Internet. Chưa phủ đủ SGK mọi môn/lớp và
  chưa thẩm định chuyên môn độc lập.
- Hoàn tất module local mới: tạo đề 1–50 câu theo lớp/môn/chủ đề/bộ sách/độ
  khó; snapshot và chấm theo đáp án server; phân tích chủ đề từ lần làm mới
  nhất; ôn lại câu chưa đúng, tính lại thống kê sau khi sửa/xóa kết quả.
- Đã sửa khôi phục phiên cũ và cache giao diện ở bản .4. Đề kiểm tra ở Luyện
  đề; Tài liệu giữ điều kiện gắn đúng bài SGK và đủ phần hướng dẫn/luyện tập.
- Giai đoạn 1 còn: kiểm thử thiết bị Android thật, hoàn thiện quản trị bộ đề,
  báo lỗi nội dung/xem xét lại bài, kiểm duyệt sư phạm, chính sách cuối cùng.
- Giai đoạn 2 chưa hoàn tất: chưa có AI provider, nhận dạng ảnh/OCR, quota,
  consent và chấm tự luận được tích hợp. Không tự sinh điểm AI giả.
- Chức năng tạo đề/phân tích local là một phần nền tảng cho giai đoạn 3;
  đã có đăng ký học viên, tạo hàng loạt và báo cáo quản lý qua backend local.
  Chưa triển khai backend HTTPS dùng chung hoặc liên kết phụ huynh.
- Production còn: Supabase Auth/Storage, adapter dữ liệu, JWT/server roles,
  hạ tầng backup/retention, kiểm thử tải, domain/backend thật, ký AAB và các
  bước Google Play. Không yêu cầu secret trong chat hoặc tự mua dịch vụ.

Chi tiết module: [LOCAL_STUDY_MODULE.md](LOCAL_STUDY_MODULE.md).

Chi tiết tài khoản bản .6: [CLASSROOM_ACCOUNTS.md](CLASSROOM_ACCOUNTS.md).
