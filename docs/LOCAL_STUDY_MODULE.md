# Tạo đề và ôn lại theo kết quả — bản thử 2026.10.15.5

Module chạy local, không dùng AI hoặc Supabase. Dữ liệu và đáp án được giữ
nguyên; không tạo thêm số lượng đề cố định để làm tăng thống kê ngân hàng.

## Người học

Trong **Luyện đề**, chọn **Tạo đề theo chủ đề và độ khó**. Có thể chọn lớp,
môn, bộ sách, chủ đề, độ khó và 1–50 câu tùy ngân hàng thực tế. Đề được lấy
ngẫu nhiên không lặp, chỉ từ câu đã xuất bản, đã xác nhận quyền và có thể
chấm bằng đáp án. Nếu không đủ câu, UI giảm số câu khả dụng; API vẫn kiểm
tra lại để xử lý trường hợp nội dung vừa bị gỡ. Chưa bảo đảm phủ đủ SGK mọi
môn/lớp; không thay đổi quy tắc SGK riêng của mục Tài liệu.

Trong **Tiến độ**, xem điểm trung bình các bài đã chấm đủ và kết quả theo
chủ đề. Chỉ lần làm mới nhất của mỗi câu góp vào thống kê chủ đề; câu đúng
một phần vẫn được đưa vào ôn. Câu chờ duyệt không được tự gán điểm 0.
Chọn **Ôn … câu chưa đúng** để mở phiên mới với những câu đó. Sau khi làm
đúng lại, câu không còn được đề xuất ôn sai. Mỗi lượt tối đa 50 câu.

Bài đang làm vẫn được giữ: nếu chưa nộp bài cũ, thao tác tạo/ôn mở lại bài
cũ thay vì ghi đè. Phiên đề tự tạo hết hạn có thể khôi phục: dùng đúng mã
câu đã lưu, không chọn ngẫu nhiên bộ câu khác. Đáp án chỉ được giữ nếu nội
dung câu không đổi. Nếu câu đã bị gỡ, báo lỗi rõ và không xóa bài cũ.

## API

- `GET /practice-options?grade=5&subject=toan`: số câu khả dụng theo chủ đề,
  độ khó và bộ sách; không có đáp án hay lời giải.
- `POST /practice-attempts`: tạo phiên có snapshot, token riêng, cùng luồng
  nộp/chấm/xóa như đề cố định. Không tạo hoặc công khai một Exam mới.

```json
{"grade":5,"subject":"toan","topic":"add_decimal","count":8,"textbook":"ket_noi_tri_thuc","difficulty":"medium"}
```

Có thể truyền `question_ids` (không trùng, đúng `count`, tối đa 50) để ôn
các câu được chọn. API không tin điểm/thống kê gửi từ thiết bị: luôn tự lấy
câu xuất bản và đáp án server rồi tạo snapshot. Nội dung link_only, bản nháp,
chưa xác nhận quyền, sai lớp/môn hoặc bị gỡ không được dùng.

Đây là thống kê luyện tập từ dữ liệu thiết bị, chưa phải mô hình đánh giá
năng lực, đồng bộ đa thiết bị hay đề thi có giám sát. Kết quả bị xóa khỏi
Lịch sử sẽ không còn góp vào thống kê. Bài lưu từ phiên bản cũ thiếu metadata
vẫn xem trong Lịch sử, không tạo số liệu chủ đề giả.
