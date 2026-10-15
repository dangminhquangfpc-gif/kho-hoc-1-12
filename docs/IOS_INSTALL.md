# Cài thử Tự học 111 trên iPhone/iPad từ Windows

Tệp `tu-hoc-111-ios-unsigned.ipa` là bản iOS .20 dành cho thiết bị thật,
**chưa ký**. Không mở trực tiếp tệp này trên iPhone để cài như APK Android.
Bạn cần ký bằng tài khoản Apple của mình qua công cụ trên máy tính, hoặc có
Apple Developer để phân phối TestFlight. Chưa có bản TestFlight/App Store.

## Cài thử với Apple ID miễn phí

Cần Windows, cáp kết nối iPhone/iPad, Apple ID và thiết bị chạy **iOS/iPadOS
15.5 trở lên**. Sideloadly là công cụ bên thứ ba, không phải phần mềm của
Apple hoặc của Tự học 111. Theo trang chính thức, công cụ hỗ trợ ký/cài IPA
từ Windows với Apple ID miễn phí. Tự học 111 không nhận mật khẩu Apple ID,
mã 2FA, certificate hoặc provisioning profile của bạn.

1. Tải `tu-hoc-111-ios-unsigned.ipa` từ bản phát hành iOS .20 của repository.
2. Vào **https://sideloadly.io/** để tải bản Windows chính thức. Làm theo yêu
   cầu iTunes/iCloud và driver của trang đó; không tải từ trang đóng gói lại.
3. Kết nối iPhone với Windows bằng cáp, mở khóa và chọn **Tin cậy** máy tính
   của bạn khi iPhone hỏi. Mở Sideloadly, chọn đúng thiết bị.
4. Kéo tệp IPA vào Sideloadly. Dùng chế độ ký/cài bằng **Apple ID**, nhập tài
   khoản của bạn và bấm **Start**. Nhập mật khẩu/xác thực riêng khi công cụ
   hoặc Apple yêu cầu; không gửi chúng vào chat, ảnh chụp hoặc GitHub.
5. Nếu iPhone yêu cầu, vào **Cài đặt → Cài đặt chung → VPN & Quản lý thiết
   bị**, chọn tài khoản phát triển của chính bạn để tin cậy. Trên iOS 16 trở
   lên, bật **Chế độ nhà phát triển** theo hướng dẫn của Apple, khởi động lại
   và xác nhận trên thiết bị nếu được yêu cầu. Không cài profile lạ.
6. Mở **Tự học 111**. Khi chưa có máy chủ, app mặc định học trên thiết bị:
   chọn lớp/môn, làm/nộp đề và xem Tiến độ → Lịch sử. Đăng nhập/nhóm/đồng bộ
   cần URL HTTPS thật trong Cá nhân → Kết nối máy chủ, xem FREE_HOSTING.md.
7. Thử chọn ảnh để OCR và kiểm tra văn bản trước khi chèn vào câu trả lời.
   Với máy chủ thật, kiểm tra đóng/mở app còn phiên và đăng xuất được.

Apple ID miễn phí có giới hạn số ứng dụng và chữ ký thường hết hạn sau
**7 ngày**. Ký/cài lại cùng tài khoản và giữ cùng bundle ID để duy trì dữ liệu;
Sideloadly có tính năng refresh, cần cấu hình riêng trên máy của bạn. Giữ
app hiện có khi refresh; xóa app sẽ xóa dữ liệu học ngoại tuyến của app.
Không hứa tự refresh khi máy tính tắt hoặc thiết bị không kết nối.

Gói được build bằng Xcode/iOS SDK 26+ trên macOS, chứa dữ liệu học ngoại tuyến
và OCR native miễn phí; không bật AI trả phí. IPA có cấu trúc Payload và
quyền thực thi được kiểm tra trước khi cung cấp, kèm SHA256 và báo cáo.
Build/đóng gói không chứng minh đã ký thành công bằng Apple ID của bạn, đã
cài trên iPhone thật hoặc đã được Apple xét duyệt. Chưa nghiệm thu OCR,
Keychain và vòng đời trên iPhone vật lý.

Nếu cài lỗi, cung cấp nguyên văn thông báo và phiên bản iOS; che email Apple,
UDID, mật khẩu, mã xác thực và nội dung tài khoản trước khi gửi ảnh/log.

## Phân phối cho học viên sau này

TestFlight/App Store cần tài khoản Apple Developer của chủ app, ký/phân phối
đúng loại và hoàn tất các điều kiện ở store/RELEASE_STATUS.md. Gói IPA chưa
ký này không thay thế TestFlight hoặc bản gửi App Store.

Nguồn kiểm tra ngày 15/10/2026:

- Sideloadly chính thức, Windows/Apple ID miễn phí và refresh: https://sideloadly.io/
- FAQ và giới hạn: https://sideloadly.io/faq
- Các loại tài khoản Apple: https://developer.apple.com/support/compare-memberships/
- Developer Mode: https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device
