# Phiên đăng nhập native được lưu an toàn

Android/iOS giữ token phiên opaque của máy chủ trong nơi lưu an toàn của hệ điều
hành để có thể mở lại ứng dụng hoặc chuyển từ học ngoại tuyến về đúng máy chủ mà
không mất phiên còn hạn. Không lưu mật khẩu, token trong SharedPreferences, URL,
log, mã nguồn hay gói tài liệu ngoại tuyến. Web tiếp tục dùng cookie HttpOnly của
máy chủ; không chuyển token vào localStorage hoặc gọi plugin secure storage web.

## Giới hạn và vòng đời

Mỗi phiên gắn với địa chỉ HTTPS đã chuẩn hóa, gồm host, cổng và đường dẫn API.
`https://truong.vn/api` khác `https://truong.vn`, host khác hoặc cổng khác. Chỉ
chữ hoa/thường của host, cổng HTTPS mặc định và dấu `/` cuối được chuẩn hóa;
không nhận địa chỉ có mật khẩu, query hoặc fragment làm scope. Không gửi bearer
ra ngoài host/đường dẫn đó; yêu cầu chứa mật khẩu hoặc bearer không đi theo redirect.

Token được đọc trước yêu cầu xác thực đầu tiên. Máy chủ vẫn quyết định phiên
còn hạn hay không (hiện là 8 giờ), không kéo dài thời hạn khi mở app. Mất mạng,
lỗi máy chủ tạm thời hoặc chuyển sang ngoại tuyến giữ token và bản nháp. Khi nhận
401 cho token đang dùng, đăng xuất hoặc xóa tài khoản thành công, app xóa đúng
token của đúng backend. Đăng xuất thất bại vì mất mạng không được báo là đã thu
hồi phiên. Phản hồi muộn từ client cũ không được xóa hay ghi đè một lần đăng nhập
mới. Mỗi scope chỉ giữ tài khoản đăng nhập gần nhất trên thiết bị đó.

Đổi mật khẩu theo chính sách backend hiện có vẫn giữ phiên đang thực hiện đổi,
thu hồi các phiên khác. Thiết bị khác xóa token cục bộ khi máy chủ trả 401. Không
có refresh token, đăng nhập vĩnh viễn hay công cụ xóa token trên thiết bị từ xa.
Lưu phiên không tự chuyển điểm tự luyện ngoại tuyến thành kết quả máy chủ.

## Cấu hình nền tảng

`flutter_secure_storage` được khóa ở **9.2.4** trong pubspec và lockfile. Bản này
dùng AGP 8.5.1, tương thích toolchain AGP 8.9.1/Gradle 8.12/JDK 21 đang khóa của
app. Các bản 10.x dùng AGP 8.13.x nên chưa nâng trong đợt này. Android vẫn cần
API 24 trở lên; iOS vẫn giữ mức tối thiểu 15.5 do OCR.

- Android chọn rõ RSA-OAEP để bọc khóa và AES-GCM để mã hóa dữ liệu, thay cho các
  thuật toán mặc định cũ của plugin. Khóa bọc nằm trong Android KeyStore; dữ liệu
  phiên được plugin mã hóa trong tệp riêng. `resetOnError: false` để lỗi tạm thời
  không tự xóa mọi dữ liệu an toàn. Khi không truy cập được nơi lưu, app báo lỗi
  chung và cho phép thử lại sau khi mở khóa thiết bị, không in ngoại lệ native.
- Android tắt OS Auto Backup và thêm quy tắc từ chối cloud backup/device transfer
  cho dữ liệu ứng dụng, bao gồm token mã hóa và dữ liệu học viên. Cài đè giữ dữ
  liệu hiện có; gỡ app/xóa dữ liệu không phải cách nâng cấp. Khi chuyển điện thoại,
  đăng nhập lại để nhận dữ liệu đã đồng bộ từ máy chủ; tự luyện chỉ lưu trên máy
  không tự xuất hiện ở điện thoại mới.
- iOS dùng Keychain `unlocked_this_device`, `synchronizable: false`, service riêng
  và nhóm mặc định của app. Token chỉ đọc được khi máy đã mở khóa, không di chuyển
  qua iCloud Keychain hoặc sang thiết bị mới. Entitlements được gắn cho cả Debug,
  Profile và Release; không có nhóm chia sẻ với app khác. Keychain có thể giữ mục
  qua lần gỡ/cài lại trên cùng thiết bị; máy chủ vẫn kiểm tra hạn/thu hồi, và app
  vẫn cho đăng xuất. Chưa khẳng định có thử nghiệm thiết bị iOS thật.

Plugin này chỉ được dùng cho phiên trên Android/iOS. Không bật dịch vụ AI có phí
và không thêm quyền camera, microphone hay sinh trắc học cho việc lưu phiên.

## Kiểm tra

Từ `apps/mobile`, chạy `flutter test test/secure_session_test.dart` cùng các bộ
`accounts_test.dart`, `study_mode_test.dart`, `backend_test.dart`. Adapter mạng và
store giả dùng token tổng hợp để kiểm tra khôi phục phiên, tách backend/tài khoản,
401, mất mạng, đăng xuất/xóa thất bại, đổi mật khẩu và phản hồi muộn. Các kiểm thử
này không liên hệ tài khoản/máy chủ thật.

`integration_test/native_secure_session_test.dart` ghi/đọc bằng plugin nền tảng
thật, tạo lại API client rồi kiểm tra token được khôi phục, và chỉ dọn scope QA
riêng. Transport trong bài test này là tổng hợp; nó kiểm tra Android KeyStore/iOS
Keychain, không chứng minh backend HTTPS công khai đã được triển khai. Chạy nó
trên emulator/simulator trước khi ghi nhận kiểm tra native thành công.
