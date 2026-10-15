# Thử trên điện thoại Android

Bản APK mới cho phép nhập URL tại **Cá nhân → Kết nối máy chủ → Kiểm tra và lưu**. Chỉ nhận URL HTTPS gốc; kiểm tra `/health` và danh mục trước khi lưu. Địa chỉ được nhớ khi mở lại app. Không đổi máy chủ khi còn bài đang làm hoặc lịch sử vì token kết quả thuộc máy chủ cũ.

## Backend dành riêng cho bản thử

`khohoc.phone_preview:create_preview` nạp 108 câu tự biên soạn, 12 đề Toán/Tiếng Việt/Ngữ văn/Tiếng Anh và 4 tài liệu Toán kèm PDF gốc. Tiếng Anh thí điểm lớp 3, 5, 9, 12; các môn còn lại lớp 1, 5, 9, 12. Chỉ mở đường dẫn luyện đề và tài liệu; chặn admin, Swagger và OpenAPI. Token quản trị dùng lúc nạp dữ liệu được hủy trước khi nhận kết nối. Giới hạn toàn bộ máy chủ 120 yêu cầu/phút (1 worker); bài làm vẫn yêu cầu token riêng. Log truy cập tắt.

Có `render.yaml` và `deploy/phone-preview.Dockerfile` để triển khai một dịch vụ Docker thử trên Render. Đây là cấu hình chuẩn bị, **chưa có dịch vụ hoặc URL thực tế được tạo**. Cần tài khoản hosting được người dùng kết nối và mã nguồn sẵn có trên hosting trước khi triển khai. TLS do hosting cấp. Không cần đưa token quản trị vào hosting.

Free tier dùng SQLite tạm: có thể ngủ khi không hoạt động, khởi động đầu chậm, dữ liệu bài làm mất khi dịch vụ tái tạo. Nếu lịch sử trên điện thoại trỏ tới dữ liệu đã mất, xóa bản ghi cục bộ và làm đề mới. Chỉ dùng cá nhân để thử bộ đề mẫu; không dùng cho lớp học thật hoặc dữ liệu cần lưu lâu dài. Không phải backend production/Supabase.

Sau khi triển khai, phải kiểm tra URL HTTPS `/health`, tải đề, nộp bài, lấy/xóa kết quả và xác nhận `/admin/questions` trả 404 từ ngoài hosting. Chưa hoàn tất các kiểm tra này khi chưa có URL.

## Trình tự kiểm tra trên máy thật

1. Cài APK debug, nhập URL được cung cấp và kiểm tra kết nối.
2. Chọn lớp 1/5/9/12, môn Toán, mở đề và trả lời vài câu.
3. Thoát/mở lại app, tiếp tục bài, nộp và xem giải thích.
4. Xem lịch sử, xóa kết quả, thử mất mạng rồi kết nối lại.
5. Ghi lại lỗi kèm mẫu điện thoại/Android; không cần gửi thông tin cá nhân.

APK hiện là bản phát triển, chưa ký phát hành và chưa kiểm tra trên điện thoại thật. iPhone không cài được APK.

Demo web tại localhost:8080 trong môi trường chạy dùng API cùng cổng qua `/api`. Dùng gateway `bash scripts/dev_demo.sh`; địa chỉ này không phải URL backend công khai cho điện thoại.
