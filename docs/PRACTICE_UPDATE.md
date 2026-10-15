# Bản thử 2026.10.15.4

## Nộp bài đã lưu

Phiên trên máy chủ hết hạn sau 24 giờ. Khi đổi thư mục ZIP, cơ sở dữ liệu
máy chủ mới cũng có thể không chứa phiên vẫn còn lưu trong trình duyệt.
Trước đây cả HTTP 404/410 đều chỉ hiện lỗi kết nối và không có đường sửa.

Bản mới phân biệt lỗi này và có nút **Khôi phục bài đã lưu**. Người học xác
nhận mở phiên mới của cùng đề. Chỉ câu hỏi có cùng mã, nội dung, phương án,
loại, điểm và đơn vị mới giữ đáp án/đánh dấu cũ. Câu thay đổi phải làm lại.
Không tự nộp; người học xem lại rồi nộp. Nếu máy chủ không còn đề, bài cũ
vẫn được giữ và việc khôi phục báo lỗi. Lỗi mạng không tự tạo phiên mới.

## Cập nhật giao diện

Bản web mới không đăng ký Flutter service worker. Gateway phục vụ worker
ngừng sử dụng cho các bản cũ, xóa đúng ba cache tài nguyên Flutter và tải
lại trang. localStorage, lịch sử, câu trả lời và IndexedDB không bị xóa.
Các tài nguyên gateway có Cache-Control: no-store. Nhãn phiên bản trên
Trang chủ/Luyện đề là `Bản thử 2026.10.15.4`.

## Dữ liệu và phân loại

- Tài liệu chỉ chứa bài Kết nối tri thức gắn đúng mục lục lớp/môn, đủ cách
  làm, ví dụ, luyện tập và lời giải. Mới có 75 bài Toán 5; các lớp/môn khác
  chưa được phủ đủ SGK. Ghi chú nền tảng cũ giữ ở dữ liệu tham khảo.
- Đề nguồn Internet nằm trong Luyện đề > Đề giữa kỳ, cuối kỳ và tốt nghiệp
  từ Internet. Chọn lớp/môn rồi mở mục này sẽ giữ lớp/môn đã chọn.
- Thêm 344 câu số học tự biên soạn: 43 nhóm kỹ năng × 8 biến thể. Thêm 75
  bộ luyện theo bài và 12 bộ ôn tổng hợp Toán 5. Các bộ ôn dùng lại câu hỏi;
  không phải 87 đề trường học độc lập hoặc được giáo viên thẩm định.
- Tổng ngân hàng: 1 910 câu, 306 đề làm trực tiếp; Toán 5 có 419 câu và
  95 đề. 1 934 liên kết nguồn ngoài được giữ. Không tính liên kết PDF là
  đề đã chuyển thành câu hỏi chấm điểm trong app.

## Tách PDF thành bản nháp

`data/pipelines/pdf_exam_draft.py` chạy trên môi trường biên soạn có Poppler
(`pdftotext`), không phải chức năng OCR trong gói Windows. Chỉ dùng cho PDF
có giấy phép phù hợp hoặc cho phép bằng văn bản. Công cụ không tải nguồn,
không tự suy đoán đáp án, không gọi API và không tự phát hành.

Ví dụ:

```sh
python data/pipelines/pdf_exam_draft.py de.pdf \
  --answers dap-an.json --rights-evidence quyen-su-dung.txt \
  --book-evidence doi-chieu-kntt.txt --license written_permission \
  --grade 5 --subject toan --title 'Đề giữa kỳ Toán 5 KNTT' \
  --source-url https://nguon-hop-le.example/de.pdf --output /tmp/de-nhap
```

`dap-an.json` là dạng `{"1":"B","2":"A"}`. Đầu ra gồm văn bản đã tách,
câu hỏi JSON, đề JSON và báo cáo thiếu sót. PDF ảnh quét, hình, phân số nhiều
dòng, đúng/sai, tự luận hoặc số câu lặp cần người biên soạn xử lý. Phải bổ
sung lời giải, điểm, kiểm tra đủ mọi câu và quyền sử dụng trước khi nhập
qua luồng quản trị hiện có. Không đưa bản nháp chứa nội dung nguồn chưa
có quyền vào fixtures hoặc gói phát hành công khai.

Ngày 15/10/2026 kiểm tra ba nguồn Loigiaihay Toán 5 giữa kỳ 1: trang và
liên kết PDF công khai có tồn tại nhưng không tìm thấy liên kết giấy phép
Creative Commons. Đây không phải bằng chứng có quyền tái phân phối. Chưa
sao chép nguyên các PDF đó vào bản phát hành.
