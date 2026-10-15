# Thư viện Internet — 15/10/2026

Bổ sung 1.934 mục liên kết đã kiểm tra, bên cạnh 199 ghi chú/tài liệu tự biên soạn: tổng 2.133 mục tài liệu. Không tăng số câu chấm trực tiếp: app vẫn có 1.566 câu và 219 đề tự biên soạn.

## Nguồn và phạm vi

- 1.830 mục ghi rõ Kết nối tri thức / KNTT / Global Success trong tiêu đề trang hoặc thẻ title HTML của chính trang. Tiếng Anh giữ tên Global Success theo nguồn.
- 1.444 trang đề giữa/cuối kì: 340 giữa kì 1, 452 cuối kì 1, 295 giữa kì 2, 357 cuối kì 2.
- 330 mục ôn tập/củng cố và 56 kho đề nhiều đợt. Nhiều mục là một bộ tài liệu hoặc bộ đề, không được đếm thành số đề thành viên.
- 104 mục đề/tài liệu tốt nghiệp dùng chung cho các bộ sách. Nguồn ghi các năm 2022, 2024, 2025, 2026; 6 kho tổng hợp không gán một năm cố định. Có đề thi thử, đề tham khảo và bản đăng lại được trang nguồn gọi là đề chính thức; chưa xác nhận độc lập toàn bộ bản đăng lại với bản của Bộ GDĐT.
- Có nguồn KNTT cho 122/135 tổ hợp lớp–môn. Danh sách 13 tổ hợp chưa có nguồn phù hợp ở `data/library/external_coverage.json`; chủ yếu Giáo dục thể chất. Không coi một kho nguồn là đủ toàn bộ chương trình hoặc tất cả tài liệu trên Internet.

Nguồn hiện được kiểm tra từ loigiaihay.com và vietjack.com. Cổng moet.gov.vn trả HTTP 503 khi kiểm tra, nên chưa lấy tài liệu từ cổng này. Các URL thử tìm thêm kho lịch sử trả lỗi không được nhập thành tài liệu.

## Điều kiện sử dụng

Mọi mục Internet có `source_type=link_only`, `license=link_only`: chỉ metadata nhận diện và liên kết HTTPS; không lưu bài đọc, câu hỏi, đáp án, ảnh đề hoặc PDF của bên thứ ba vào gói phát hành. Quyền phân phối/tải PDF trong app đều false. Trạng thái duyệt mẫu của demo chỉ duyệt việc liên kết, không phải quyền sao chép toàn văn.

Trang nguồn có thể chứa quảng cáo, yêu cầu đăng nhập hoặc phí. Chưa xác nhận miễn phí toàn bộ. App nêu điều này ở trang tài liệu. Mở nguồn cần mạng; các ghi chú và đề tự biên soạn vẫn dùng backend local.

Đề tốt nghiệp quốc gia được gắn `national_common`, không gắn KNTT. Các nguồn trước 2025 chỉ dùng tham khảo và cần đối chiếu cấu trúc kỳ thi GDPT 2018 hiện hành. `exam_year` lấy từ tiêu đề nội dung đã kiểm tra, không lấy trực tiếp từ URL vì một số URL được nhà cung cấp tái sử dụng cho năm khác.

## Kiểm tra chất lượng

`data/library/source_checks.json` giữ URL, tiêu đề, dấu hiệu bộ sách, trang cha, HTTP 200, ngày kiểm tra và SHA-256 HTML đã nhận. Không chứa nội dung đầy đủ của trang. Trùng tiêu đề cùng lớp/môn bị loại theo quy tắc của backend; URL trùng cũng bị loại. Chữ số học kì không được dùng nhầm làm số lớp.

`data/pipelines/import_web_catalog.py` dựng dữ liệu từ bằng chứng đã kiểm tra. Khi nhập lại, giữ payload đã phát hành; báo cáo kiểm tra được cập nhật riêng. Thay đổi payload đã lưu cần đi qua quản trị và duyệt lại, thay vì tự động ghi đè vào fixture.

Có thể kiểm tra lại link bằng:

```bash
/workspace/venvs/khohoc/bin/python data/pipelines/check_source_links.py --report /tmp/source-link-report.json
```

Trình kiểm tra giới hạn host, HTTPS, redirect, kích thước và thời gian; không tải PDF, không vượt đăng nhập/paywall, không sửa các bản ghi đã phát hành.

## Trong app

Mở Tài liệu, chọn lớp/môn, bộ sách, đợt kiểm tra và năm đề thi. Các mục nguồn ngoài mở bằng nút Mở nguồn gốc tài liệu; các bộ nhiều đề có nhãn riêng. Thư viện lấy đủ các trang kết quả thay vì dừng ở 50 mục. Thống kê phân biệt nguồn Internet với đề làm trực tiếp trong app.
