# Thử Tự học 111 trên điện thoại Android

Bản .19 có **Học trên thiết bị**, dùng được khi chưa có backend. Lỗi Trang
chủ không tải được dữ liệu trong APK .18 xuất phát từ việc chưa có máy chủ
HTTPS dùng chung; chờ lâu hoặc bấm Thử lại không tạo ra máy chủ đó.

## Cài hoặc cập nhật

Tải APK/ZIP APK từ [Releases của dự án](https://github.com/dangminhquangfpc-gif/kho-hoc-1-12/releases).
Nếu chọn ZIP, giải nén rồi mở APK bên trong. Chọn đúng release .19 khi tệp
đã được công bố. Bản Android thử hiện dành cho ARM64, Android 7.0/API 24 trở
lên; iPhone không cài được APK.

APK .19 giữ mã ứng dụng và chứng thư debug của .18 để **cài đè**, không cần
gỡ bản cũ hay xóa dữ liệu. Nếu Android báo chữ ký không tương thích, giữ
nguyên bản đang cài và kiểm tra đúng nguồn/phiên bản trước, không gỡ ngay.
Chữ ký hợp lệ không thay thế việc kiểm tra bảo mật hoặc Google Play duyệt.

Samsung Auto Blocker và Play Protect có thể chặn APK cài ngoài cửa hàng.
Cảnh báo “chưa từng thấy ứng dụng nào của nhà phát triển này” thể hiện
nguồn phát hành chưa được Google biết đến; không thể bảo đảm cảnh báo biến
mất chỉ bằng build lại. Không tắt Play Protect toàn cục. Nếu máy báo ứng
dụng có hại, dừng cài và gửi nguyên văn/ảnh cảnh báo để kiểm tra.

## Thử khi chưa có máy chủ

1. Mở app, kiểm tra Trang chủ có thẻ **Học trên thiết bị**. Nếu thấy **Học
   với máy chủ**, chọn **Chuyển sang học trên thiết bị**.
2. Chọn vài lớp từ 1–12 và môn có đề, mở đề và trả lời vài câu.
3. Đóng/mở app, tiếp tục bài đã lưu, nộp và xem lời giải. Câu tự luận có
   trạng thái cần đánh giá thủ công, không được tự chấm điểm.
4. Vào Tài liệu, mở hướng dẫn Toán ở lớp đã chọn. Liên kết trang ngoài cần
   mạng; các PDF bên ngoài không nằm sẵn trong gói ngoại tuyến.
5. Tắt Wi-Fi/dữ liệu di động rồi thử mở đề, nộp và xem lại lịch sử. Bài
   ngoại tuyến và điểm chỉ lưu trên thiết bị, không xuất hiện ở lớp học.

Xem [phạm vi dữ liệu và lưu trữ](OFFLINE_STUDY.md). Không có trợ lý AI trả
phí hoặc yêu cầu nhập khóa. OCR nhận chữ miễn phí còn hoạt động độc lập.

## Thử tài khoản, nhóm và đồng bộ

Các chức năng này cần backend HTTPS thật do người quản lý cung cấp. Vào
**Cá nhân → Kết nối máy chủ → Kiểm tra và lưu**. Chỉ nhận URL HTTPS gốc,
có thể kết thúc bằng `/api`; kiểm tra `/health` và danh mục trước khi lưu.
Không nhập `localhost` của máy cloud, IP nội bộ khác mạng hoặc địa chỉ
`.invalid` như máy chủ hoạt động.

Sau khi kết nối, đăng ký/đăng nhập, tham gia nhóm, làm đề rồi kiểm tra kết
quả trên thiết bị thứ hai. Chế độ máy chủ chấm qua API, kể cả bài khách;
điểm tự luyện ngoại tuyến không tự nhập vào kết quả giáo viên theo dõi.
Bài/lịch sử của hai chế độ được giữ riêng khi chuyển chế độ.

Hiện chưa có backend production công khai của dự án. `render.yaml` và
`deploy/phone-preview.Dockerfile` chỉ là cấu hình bản xem thử. SQLite tạm
trên hosting miễn phí có thể mất khi dịch vụ tái tạo; không dùng làm hồ sơ
lớp học thật. Cấu hình dùng chung PostgreSQL/HTTPS vẫn cần triển khai và
hoàn tất các điều kiện trong [SHARED_SERVER.md](SHARED_SERVER.md).

## Nhận chữ và ghi nhận lỗi

Vào **Cá nhân → Nhận chữ từ ảnh** hoặc nút **Nhập từ ảnh hoặc văn bản**
ở câu có ô nhập. Chọn ảnh PNG/JPEG/WebP, sửa chữ nhận được, xác nhận đã kiểm
tra rồi dùng văn bản. Nhập từ ảnh không tự nộp bài. Kiểm tra hủy chọn ảnh,
quay lại app và chữ tiếng Việt trên máy thật.

Khi báo lỗi, gửi ảnh màn hình, phiên bản app, mẫu máy/Android và đang ở chế
độ nào; không gửi mật khẩu hay dữ liệu học sinh thật. Các bài kiểm thử tự
động/native không thay toàn bộ nghiệm thu trên thiết bị người dùng.
