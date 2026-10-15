# Hướng dẫn Toán 6–12 — bản thử 2026.10.15.9

Bổ sung 391 mục hướng dẫn, gồm 230 bài đánh số và các mục luyện tập, ôn chương/cuối năm, hoạt động được ghi nhận trong mục lục nguồn Kết nối tri thức. Số mục theo lớp: 6: 74; 7: 69; 8: 75; 9: 62; 10: 39; 11: 43; 12: 29. Số bài đánh số tương ứng: 43, 37, 39, 32, 27, 33, 19; các dãy số bài không có khoảng trống theo nguồn.

Có 610 ví dụ và 1.220 bài luyện kèm Lời giải và Đáp số. Các bài ôn tập dùng lại kỹ năng/ví dụ từ phần học, không coi mọi lần xuất hiện là một câu hỏi độc lập mới. Các bài này nằm trong Tài liệu, chưa đưa 1.220 câu mới vào ngân hàng chấm tự động của Luyện đề. Tổng hướng dẫn Toán 1–12 theo các mục đã ghi nhận là 733.

## Mục lục

Trang Toán 6–12 dùng hộp `event_1_columns` và đường dẫn bài `-e...html`; bộ đọc cũ chỉ xử lí danh sách `event-articles-wrap` nên trước đây không ghi nhận được các bài này. Bộ đọc mới giới hạn trong hộp nội dung chính, bỏ liên kết sách, tiêu đề chương, sidebar/quảng cáo; giữ chương, học kì, thứ tự và URL của từng bài. ID bài được tạo từ URL. Bài hoạt động có thể có số riêng (như tài chính lớp 10), không trộn với dãy bài học chính.

Đã lưu hash HTML nguồn trong metadata từng sách và kiểm tra đủ các dãy bài đánh số. Đây là đối chiếu nguồn thứ cấp Loigiaihay ngày 15/10/2026, **không phải xác nhận của nhà xuất bản cho mọi trang hoặc mọi ấn bản**. Không tự suy thêm bài khi nguồn chưa có. Các mục khác/lớp khác được giữ nguyên.

## Nội dung và giới hạn

- Kiến thức có điều kiện mẫu, căn, log, dấu và đơn vị; phương pháp từng bước, ví dụ và hai bài luyện cho mỗi phần kỹ năng; lời giải và đáp số riêng.
- Ánh xạ từng bài học được khai báo rõ, các bài ôn chương chỉ dùng chủ đề đã học trong chương; hoạt động được gắn theo đề tài cụ thể. Bài ôn cuối năm chọn nội dung cơ bản theo phạm vi.
- Kết quả điển hình gồm phân số/số nguyên, đa thức, phương trình/bất phương trình, hình học phẳng/không gian, vectơ/tọa độ, thống kê/xác suất, lượng giác, dãy/giới hạn, đạo hàm và tích phân/Bayes.
- Quy ước sai số tương đối của số gần đúng a dùng mẫu |a|, đã đối chiếu riêng nguồn lý thuyết KNTT: https://loigiaihay.com/li-thuyet-so-gan-dung-va-sai-so-a109798.html . Các ví dụ tự soạn, không chép bài nguồn.
- Bài thực hành dùng phần mềm có chỉ dẫn thao tác và kết quả toán học để đối chiếu trên giấy; chưa kiểm thử mọi phiên bản GeoGebra/Excel. Bài khí hậu/dân số/mạng xã hội ghi rõ dữ liệu giả định, không gán thành số liệu quốc gia thực tế.
- Đây là hướng dẫn cơ bản tự biên soạn, **chưa thẩm định sư phạm độc lập, chưa đủ mọi dạng bài và lời giải của mọi trang SGK**. Không phân phối PDF hay sao chép nguyên bài giải nguồn. Các môn ngoài Toán chưa được hoàn thiện trong đợt này.

## Tái tạo

1. Tải các trang mục lục theo `source_url` của 7 sách Toán vào `math6.html` … `math12.html`, giữ proxy/CA và kiểm tra nguồn công khai, không bỏ qua TLS.
2. Chạy `python data/pipelines/refresh_secondary_math_index.py <thư_mục_HTML>` để cập nhật đúng 7 sách; dừng nếu thiếu/sai dãy bài đánh số.
3. Chạy `python data/pipelines/build_secondary_math_lessons.py`. Nội dung và ánh xạ tại `secondary_math_content.py`, tệp kết quả riêng `data/library/secondary_math_documents.json`.

Backend, seed thư viện và gói Windows nạp tệp mới. Khi nâng cấp, dừng bản cũ, sao lưu rồi chép toàn bộ state trước lần chạy đầu tiên để giữ tài khoản/kết quả. Các bài Toán 1–5 không bị biên soạn lại trong đợt này.
