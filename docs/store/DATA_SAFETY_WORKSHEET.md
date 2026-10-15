# Đối chiếu Data Safety — Tự học 111

Phạm vi nguồn: 0.2.0+18, Android/iOS và demo web, ngày 15/10/2026.
Đây là bảng làm việc cho đơn vị phát hành; **chưa phải câu trả lời Data Safety
đã nộp hoặc được Google duyệt**. Khai theo bản AAB, backend và tất cả SDK thật
được phát hành. Tên loại dữ liệu trong Play Console có thể thay đổi.

## Luồng dữ liệu cần khai

| Dữ liệu/nguồn | Có rời thiết bị? | Mục đích và nơi xử lý | Nhóm khai báo cần đối chiếu |
| --- | --- | --- | --- |
| Tên hiển thị, tên đăng nhập, mã tài khoản, vai trò, lớp | Có khi dùng tài khoản | Backend: quản lý tài khoản và phạm vi nhóm | Personal info: Name, User IDs; đánh giá Other info cho lớp/vai trò |
| Mật khẩu và mã phiên | Có khi đăng nhập/xác thực | Backend băm mật khẩu scrypt; lưu băm token, phiên 8 giờ | Dữ liệu xác thực cần mô tả trong policy; đối chiếu hướng dẫn Personal info/User IDs, không coi là dữ liệu thanh toán |
| Câu trả lời, bản nháp, bài nộp, điểm, thời gian, mã đề/chủ đề | Có; cả bài khách khi tạo/chấm bài | Backend: luyện tập, đồng bộ, hiển thị tiến độ; giáo viên xem theo quyền | App activity: Other user-generated content/Other actions; dữ liệu gắn tài khoản nếu đăng nhập |
| Nhóm, mã tham gia, quan hệ giáo viên/học viên, bài giao | Có | Backend: quản lý nhóm và quyền xem kết quả | User IDs và App activity tương ứng |
| Phiếu báo lỗi, mô tả, trích đoạn, phản hồi xử lý | Có khi người dùng gửi | Backend: xử lý phản hồi; người quản lý xem theo quyền | App activity: Other user-generated content; Personal info nếu người dùng tự nhập vào nội dung |
| Ảnh OCR và ảnh xem trước | App không tải lên backend/dịch vụ OCR từ xa | Bộ nhớ/cache ứng dụng, Google ML Kit xử lý trên thiết bị | Không tự khai ảnh được thu thập từ xa chỉ vì app cho chọn ảnh; phải kiểm chứng hành vi SDK của bản gửi |
| Văn bản OCR ở màn hình độc lập | Không tự gửi | Bộ nhớ; clipboard chỉ khi chọn sao chép | Khi chèn làm câu trả lời và lưu/nộp, áp dụng luồng câu trả lời ở trên |
| Thông tin ML Kit: thiết bị/ứng dụng, mã theo lần cài đặt, API, chẩn đoán/hiệu năng | Có thể gửi Google theo công bố SDK | Chẩn đoán, hiệu năng và vận hành SDK | Device or other IDs; App info and performance; đối chiếu chính xác các loại dữ liệu SDK công bố |
| Nhật ký ứng dụng/hạ tầng, thông tin kết nối, bộ đếm chống lạm dụng | Backend/hạ tầng xử lý khi gọi API | Bảo mật, hạn chế lạm dụng; bộ đếm dùng khóa băm có thời hạn | Đối chiếu User IDs, Device or other IDs và App activity theo nội dung log thật; không tự suy ra app thu vị trí |
| CSV bảng điểm | Khi người dùng chọn tải/sao chép và tự chia sẻ | Trình duyệt/clipboard, rồi tùy nơi giáo viên dán/gửi | Luồng xuất do người dùng chủ động; đánh giá quy tắc sharing riêng, không khẳng định có thể thu hồi bản đã xuất |
| Website nguồn tham khảo ngoài | Trình duyệt kết nối website khi mở liên kết | Bên thứ ba theo chính sách riêng | Rà danh sách/luồng mở web và đối tượng tuổi; không gán chính sách website bên ngoài cho app |

“Có rời thiết bị” không tự quyết định toàn bộ câu trả lời “sharing”. Cần phân
biệt đơn vị vận hành, nhà cung cấp dịch vụ, giáo viên được người dùng cho phép
xem và SDK có mục đích riêng theo định nghĩa hiện hành của Google. Không chọn
ngoại lệ service provider hoặc user-initiated sharing khi chưa có căn cứ.

Không có quảng cáo, SDK thanh toán hay yêu cầu tới nhà cung cấp AI trong bản
.18. Luồng đăng ký không yêu cầu email, số điện thoại, ngày sinh, vị trí,
danh bạ, dữ liệu sức khỏe/tài chính. Việc này không có nghĩa ứng dụng “không
thu thập dữ liệu”. Nội dung tự do của câu trả lời/phiếu báo lỗi vẫn có thể
chứa thông tin người dùng tự nhập.

## SDK đang dùng

| Thành phần | Phiên bản/khóa nguồn | Vai trò |
| --- | --- | --- |
| `google_mlkit_text_recognition` | 0.15.0 | Cầu Flutter tới OCR native |
| `google_mlkit_commons` | 0.11.0 | Cầu dữ liệu native |
| Android `com.google.mlkit:text-recognition` | 16.0.1, khai báo implementation của plugin | Mô hình Latin được đóng gói để nhận chữ trên thiết bị |
| Android `com.google.mlkit:vision-common` | 17.3.0, khai báo implementation của plugin | Thành phần dùng chung ML Kit |
| iOS `GoogleMLKit/TextRecognition` | Plugin khai báo ~> 7.0.0; cần lưu Podfile.lock của build iOS gửi xét duyệt để xác nhận phiên bản giải quyết thực tế | Không lấy số phiên bản Flutter làm số phiên bản SDK iOS |
| `image_picker` / `image_picker_android` | 1.2.2 / 0.8.13 | Chọn một ảnh từ hệ điều hành; không có luồng camera |
| `flutter_plugin_android_lifecycle` | 2.0.28 | Vòng đời plugin Android |
| `path_provider` | 2.1.5 | Cache ảnh tạm riêng của ứng dụng |
| `shared_preferences` | 2.5.3 | Tùy chọn, bài làm/lịch sử cục bộ |
| `dio` | 5.8.0+1 | Gọi backend; không phải SDK phân tích |
| `url_launcher` | 6.3.2 | Mở nguồn tham khảo trong trình duyệt |
| Web Tesseract | tesseract.js 6.0.1, core 6.1.2, dữ liệu vie/eng 1.0.0 | OCR cục bộ web; không nằm trong luồng ML Kit native |

Nguồn kiểm tra: `apps/mobile/pubspec.lock`, build.gradle/podspec của plugin
đã khóa, metadata của `apps/mobile/web/ocr` và cây phụ thuộc Gradle/Pods của
build phát hành. Manifest gộp của AAB là bằng chứng cuối cho quyền Android;
manifest nguồn chỉ khai INTERNET, SDK có thể thêm quyền cần đối chiếu.
Không yêu cầu quyền CAMERA hay quyền đọc toàn bộ thư viện chỉ để chọn một ảnh.

Tài liệu SDK cần đọc lại trước submission:

- https://developers.google.com/ml-kit/android-data-disclosure
- https://developers.google.com/ml-kit/ios-data-disclosure
- https://support.google.com/googleplay/android-developer/answer/10787469
- https://support.google.com/googleplay/android-developer/answer/13327111

## Các câu trả lời cần bằng chứng vận hành

| Câu hỏi | Kết luận hiện tại / bằng chứng còn thiếu |
| --- | --- |
| Có thu thập dữ liệu không? | Có ở luồng tài khoản/bài làm và có SDK cần đối chiếu; không chọn No |
| Mã hóa khi truyền? | App release buộc HTTPS khi đăng nhập; phải kiểm tra HTTPS toàn bộ API/SDK/log trên backend thật trước khi xác nhận |
| Có thể tạo tài khoản? | Có: học sinh và giáo viên; tài khoản giáo viên tự khai chưa được xác minh |
| Có thể yêu cầu xóa? | Có luồng tự xóa trong app; URL yêu cầu xóa công khai và xử lý backup/log chưa hoàn thiện |
| Thu thập bắt buộc hay tùy chọn? | Tài khoản tùy chọn cho một số chức năng; khi đăng nhập phải có dữ liệu xác thực; ảnh/phản hồi do người dùng chủ động chọn; dữ liệu chẩn đoán SDK cần kiểm tra khả năng tắt thật |
| Chỉ xử lý tạm thời? | Không chọn cho hồ sơ tài khoản, bài làm/kết quả hoặc phiếu lưu DB; ảnh OCR xử lý cục bộ khác với các trường lưu máy chủ |
| Dùng để quảng cáo/theo dõi? | Mã app không tích hợp quảng cáo; cần xác nhận mục đích SDK và hợp đồng thật, không suy ra tất cả dữ liệu đều not shared |
| Dữ liệu trẻ em? | Người dùng dự kiến lớp 1–12; chưa có quy trình người giám hộ/xác minh giáo viên, phải hoàn thiện đối tượng tuổi và khai Families phù hợp |
| Dữ liệu còn trong backup/log sau xóa? | Chưa có thời hạn và quy trình được công bố; không hứa xóa tức thì mọi bản sao |

## Hồ sơ cần giữ cùng bản phát hành

1. AAB và SHA-256, versionCode, applicationId, chứng thư upload; không kèm khóa riêng.
2. Manifest gộp, cây phụ thuộc release, pubspec.lock, iOS lock nếu phát hành iOS.
3. Bản chụp các trang khai báo SDK, ngày đối chiếu và các mục Data Safety đã chọn.
4. Kiểm tra mạng khi mở app, đăng nhập, làm bài khách, nộp bài, nhận chữ,
   sao chép CSV và mở nguồn ngoài; không ghi mật khẩu/token/ảnh học sinh thật vào hồ sơ.
5. Bằng chứng xóa tài khoản, thu hồi phiên, kiểm tra kết quả trên thiết bị khác;
   thời hạn log/backup và kênh yêu cầu xóa bên ngoài.
6. Chính sách đã công bố, email hỗ trợ hoạt động, thông tin đơn vị xử lý dữ
   liệu, quyết định nhóm tuổi và quy trình người giám hộ phù hợp.
