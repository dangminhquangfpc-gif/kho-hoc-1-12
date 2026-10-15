# Hướng dẫn Toán lớp 1–4 — bản thử 2026.10.15.8

Bổ sung 267 tài liệu có nội dung trong app: lớp 1 có 41, lớp 2 có 74, lớp 3 có 79, lớp 4 có 73. Mỗi tài liệu gắn đúng ID bài, tiêu đề và URL trong mục lục nguồn thứ cấp đã ghi nhận. Các bài ôn tập chọn rõ các kỹ năng có liên quan, không dùng một đoạn hướng dẫn chung cho tất cả các bài.

Có 476 ví dụ và 952 bài tự luyện kèm lời giải từng bước, đáp số. Đây là bài luyện đọc trong tài liệu, chưa phải 952 câu mới được chấm tự động trong Luyện đề. Các phần ôn tập có thể dùng lại ví dụ/kỹ năng; không tính là câu hỏi mới độc lập trong ngân hàng luyện đề.

## Phạm vi nội dung

- Lớp 1: đếm, so sánh, tách số, cộng/trừ trong 10 và không nhớ trong 100; hình phẳng, khối, vị trí; đo cm, giờ đúng, ngày trong tuần.
- Lớp 2: số đến 1 000, cộng/trừ có nhớ, bảng nhân/chia 2 và 5, thành phần phép tính; đo lường, tiền, lịch, đồng hồ; hình, biểu đồ tranh và khả năng xảy ra.
- Lớp 3: bảng nhân/chia 3–9, thành phần chưa biết, một phần mấy; trung điểm, tâm/bán kính/đường kính, góc vuông, hình/khối; tính số nhiều chữ số, chia có dư, bài hai bước; số La Mã, làm tròn; diện tích/chu vi, đơn vị, thời gian/tiền, số liệu và sự kiện.
- Lớp 4: số nhiều chữ số/lớp triệu, chẵn/lẻ, biểu thức chứa chữ, bài ba bước; góc, vuông góc/song song, bình hành/thoi; phép tính và tính chất, tổng–hiệu, trung bình cộng/rút về đơn vị; phân số, thống kê và đo lường.

Bài hình tròn lớp 3 chỉ học tâm, bán kính, đường kính; không dùng công thức diện tích/chu vi lớp 5. Lớp 1 không dùng bài cộng có nhớ hoặc phép nhân. Các bài phép tính theo số chữ số được kiểm tra miền giá trị.

## Giới hạn kiểm chứng

267 là số **mục đã có trong dữ liệu mục lục**, không chứng nhận toàn bộ SGK. Mục lục Toán 2 hiện thiếu số bài 57; Toán 3 hiện thiếu số bài 20 và 75. Không tự đặt tên hoặc gắn hướng dẫn vào các bài chưa có nguồn. Cần tiếp tục đối chiếu nguồn để bổ sung. Các môn khác và lớp 6–12 vẫn còn nhiều phần thiếu; không đổi trạng thái của chúng thành có bài.

Nội dung tự biên soạn theo nội dung bài được nhận diện, chưa đối chiếu nguyên mẫu từng trang/ấn bản SGK, chưa thẩm định sư phạm độc lập và chưa đảm bảo đủ mọi dạng bài. Không sao chép nguyên lời giải hoặc PDF từ Internet.

## Tái tạo và kiểm tra

Chạy `python data/pipelines/build_primary_math_lessons.py`. Ánh xạ từng số bài được khai báo rõ trong `primary_math_content.py`; thiếu ánh xạ thì dừng, không tự dùng một chủ đề mặc định. Dữ liệu ghi riêng ở `data/library/primary_math_documents.json`; không sửa tài liệu Toán 5 đã phát hành.

Backend, script seed thư viện và gói Windows đều nạp tệp mới. Khi nâng cấp, sao lưu và chép toàn bộ state từ bản cũ; bản mới nhập thêm ID bài và không đặt lại tài khoản hay kết quả.
