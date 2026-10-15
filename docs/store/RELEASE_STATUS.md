# Tự học 111 — chuẩn bị Google Play và App Store

Bản mã nguồn 0.2.0+17 / demo .17; các mốc kỹ thuật cũ được giữ bên dưới.
Chưa phát hành lên cửa hàng.
Người dùng xác nhận chưa có Play Console, Apple Developer hoặc backend HTTPS dùng chung.
Không tạo tài khoản, thanh toán hoặc đưa backend development chứa dữ liệu học viên ra Internet.

## Những phần đã chuẩn bị trong mã nguồn

- Tên hiển thị Android, web, iOS: Tự học 111; giữ application ID Android để giữ dữ liệu khi nâng cấp.
- Android compile/target API 36; cấu hình ký upload dùng android/key.properties ngoài Git, không dùng khóa debug cho release.
- Khung iOS, Podfile, privacy manifest cho UserDefaults (CA92.1), không bật tracking.
- Native OCR có chọn ảnh từ thư viện bằng image_picker 1.2.2 và Google ML Kit Latin
  qua google_mlkit_text_recognition 0.15.0; iOS tối thiểu 15.5. Chưa có camera/cắt ảnh.
  SDK xử lý ảnh trên thiết bị nhưng có dữ liệu chẩn đoán/định danh cần khai cửa hàng.
- Tài khoản tự đăng ký có thể xóa trong ứng dụng sau khi xác nhận mật khẩu.
  Xóa tài khoản giáo viên giữ tài khoản/kết quả học sinh cho quản lý hệ thống;
  các bài/kết quả đã chia sẻ thuộc học viên khác không bị xóa theo.
- scripts/store_preflight.py kiểm tra URL HTTPS, metadata nhà phát hành,
  trạng thái production của backend, thẩm định nội dung/trẻ em và cấu hình ký trước lệnh build dùng để phát hành.
- Gói AAB engineering có thể biên dịch không ký để kiểm tra kỹ thuật; không đủ điều kiện tải lên Play.
  Đăng nhập native release yêu cầu HTTPS. Backend mặc định phát triển không dùng được để xét duyệt.

## Những bước còn cần trước khi gửi xét duyệt

1. Tạo, xác minh tài khoản Play Console và Apple Developer bằng thông tin của chủ ứng dụng.
2. Chuẩn bị nhà phát hành, email hỗ trợ, tên miền/backend HTTPS production, quản trị và backup,
   vận hành/xử lý yêu cầu xóa dữ liệu; các URL chính sách và yêu cầu xóa tài khoản ngoài ứng dụng.
   Backend hiện từ chối production vì adapter xác thực/dữ liệu production chưa hoàn tất.
3. Đối chiếu SGK, đáp án, phạm vi từng đề và quyền nội dung. 991 đề gắn thẻ nguồn là đề tự biên soạn
   cùng lớp/môn, không phải bản sao nguồn và chưa đảm bảo ma trận chương/học kỳ của nguồn.
   525 thẻ chưa đủ ngân hàng vẫn là tham khảo. Không mô tả chúng như đề nguồn đã chuyển đổi.
4. Duyệt dữ liệu trẻ em, cơ chế đồng ý của phụ huynh/người giám hộ, vai trò giáo viên hiện tự khai,
   chính sách chia sẻ kết quả và liên kết ngoài. Chưa khẳng định đáp ứng Families/Children's Privacy.
5. Logo riêng, ảnh chụp điện thoại Android/iPhone/iPad thật, khả năng truy cập và kiểm thử thiết bị.
   Tài sản icon trong khung iOS vẫn là template; chưa coi bộ hình ảnh cửa hàng là hoàn chỉnh.
6. Khóa Android upload signing và Apple team/certificate/profile ở kho bí mật riêng, ngoài Git.
   Tăng version/build, kiểm tra AAB/IPA đã ký; kiểm thử nội bộ/kín/TestFlight theo loại tài khoản.
7. Khai Data Safety/App Privacy, độ tuổi, content rating, SDK, quyền nội dung, tài khoản demo cho reviewer;
   đối chiếu dữ liệu chẩn đoán/định danh ML Kit và dữ liệu văn bản gửi nhà cung cấp AI thực tế;
   kiểm tra lần cuối trước khi gửi bản cụ thể xét duyệt. Chưa gửi submission hay thanh toán phí.

## Yêu cầu chính thức đã truy cập ngày 15/10/2026

- Google target API: https://support.google.com/googleplay/android-developer/answer/11926878
  Nội dung hiện hành nêu từ 31/08/2026 app mới/cập nhật phải target Android 16/API 36, trừ nhóm thiết bị ngoại lệ.
- Google xóa tài khoản: https://support.google.com/googleplay/android-developer/answer/13327111
  Chuẩn bị luồng trong app và URL yêu cầu xóa ngoài app, không chỉ nút đăng xuất.
- Apple SDK: https://developer.apple.com/news/upcoming-requirements/
  Nội dung hiện hành nêu từ 28/04/2026 tải lên App Store Connect cần Xcode 26+ và SDK iOS 26+ tương ứng.
- Apple xóa tài khoản: https://developer.apple.com/support/offering-account-deletion-in-your-app/
  Cho phép xác nhận mật khẩu trước khi xóa, phải có luồng xóa khi app hỗ trợ tạo tài khoản.

Khung Flutter/iOS được chuẩn bị trên Linux; chỉ kiểm tra tĩnh ở đây, không khẳng định đã archive bằng Xcode.
Workflow iOS engineering trên macOS kiểm tra SDK 26 trước khi build không ký; build đó cũng không phải IPA xét duyệt.

## Lệnh chuẩn bị bản phát hành có cấu hình thật

Sao chép deploy/store/publisher.example.json ra tệp cấu hình riêng và điền thông tin đã xác minh.
Không đặt mật khẩu/khóa ký trong tệp metadata đó hoặc trong chat.

```sh
python scripts/store_preflight.py --platform android --api-base-url https://TEN-MIEN-THAT/api --publisher-config /duong-dan-rieng/publisher.json --build
# macOS có Xcode 26+, Apple team/signing đã cấu hình:
python scripts/store_preflight.py --platform ios --api-base-url https://TEN-MIEN-THAT/api --publisher-config /duong-dan-rieng/publisher.json --build
```

Các địa chỉ và đường dẫn minh họa trong lệnh không phải endpoint được triển khai.

## Cập nhật mã nguồn 0.2.0+12

Có nền tảng PostgreSQL và pilot HTTPS dùng chung; đồng bộ bản nháp/kết quả giữa
thiết bị và chống ghi đè bằng revision. Xem `docs/SHARED_SERVER.md`. Chưa triển
khai endpoint Internet, backup PostgreSQL định kỳ hoặc hoàn tất điều kiện cửa
hàng. Health của pilot trả `mode=shared`; preflight vẫn yêu cầu production để
ngăn nhầm bản pilot thành bản phát hành.

## Bổ sung vận hành sau .12

Đã có công cụ backup PostgreSQL mã hóa, restore cách ly và monitor HTTPS/readiness,
unit lịch chạy kèm runbook. Chưa kích hoạt lịch/giám sát trên máy chủ Internet,
chưa có offsite hoặc đối soát dữ liệu đã xóa sau phục hồi; không coi đây là hoàn
tất vận hành production. Xem docs/POSTGRES_OPERATIONS.md.

## Bản thử .13

Thêm xuất CSV kết quả nhóm có phân quyền chủ nhóm, xử lý tiếng Việt và phòng
công thức bảng tính. Web tải tệp; native sao chép CSV, chưa lưu tệp trực tiếp.
Đây là báo cáo toàn bộ lịch sử học của thành viên hiện tại. Không thay đổi
trạng thái pilot/production hoặc điều kiện ký, thử nghiệm thiết bị và cửa hàng.

## Bản thử .14

Có luồng báo lỗi nội dung và người quản lý/giáo viên trả lời theo quyền học viên.
Không phải kiểm duyệt sư phạm độc lập, không phải chấm lại bài hoặc xác minh
vai trò giáo viên. Chưa tích hợp thông báo đẩy/email, AI/OCR hoặc triển khai
backend Internet; điều kiện phát hành cửa hàng vẫn chưa hoàn tất.

## Bản thử .15

Có giao bài theo nhóm, theo dõi tiến độ riêng từng đề và xuất CSV; học sinh chỉ
xem dữ liệu của mình. Không thêm SDK, quyền thiết bị, AI hoặc endpoint Internet.
Chưa có hạn giao bài/thông báo đẩy; trạng thái pilot và điều kiện cửa hàng
không đổi. Xem GROUP_ASSIGNMENTS.md.

## Bản thử .16 — OCR và trợ giảng tùy chọn

Có OCR chữ in tiếng Việt/Anh chạy thật trong Chromium ở bản web/demo Windows,
không gửi ảnh lên máy chủ. Tài sản Tesseract có giấy phép, nguồn, phiên bản và
checksum trong gói. Có xem trước/sửa/xác nhận văn bản; native Android/iOS vẫn
nhập tay hoặc dán, chưa có OCR/camera hoặc cắt ảnh trong app.

Backend trợ giảng AI mặc định tắt; khóa chỉ đọc từ tệp riêng của operator,
không có trong ứng dụng. Mỗi yêu cầu cần đăng nhập và xác nhận host/dữ liệu.
Tham chiếu câu đã nộp là tùy chọn và được công bố rõ. Có quota, hạn kích thước,
timeout và nhật ký metadata/số token; phản hồi không trở thành điểm chính thức.
Chưa gọi hoặc đánh giá provider/model thật, chưa có chấm tự luận theo rubric
hay luồng riêng báo lỗi/xem xét phản hồi AI. Xem [AI_OCR.md](../AI_OCR.md).

Trước khi bật AI cho học sinh thật hoặc nộp cửa hàng, còn phải đánh giá nhà
cung cấp/model, cơ sở xử lý và đồng ý của người giám hộ, lưu giữ/huấn luyện dữ
liệu phía provider, kiểm soát nội dung, báo lỗi AI và retention nhật ký. Cần
khai đúng tài sản/SDK và luồng dữ liệu của bản cụ thể trong Data Safety/App
Privacy; không dùng trạng thái mặc định tắt để tuyên bố mọi cấu hình không gửi
dữ liệu ra ngoài. Chưa triển khai Internet, kiểm thử/ký bản .16 trên thiết bị
thật hoặc mở khóa chế độ production; điều kiện phát hành vẫn chưa hoàn tất.

## Bản thử .17 — OCR native và cấu hình AI

Đã tích hợp luồng chọn ảnh thư viện trên Android/iOS, xử lý OCR Latin bằng
Google ML Kit trên thiết bị, xem ảnh và sửa/xác nhận văn bản trước khi dùng.
Không thêm camera vào luồng này. Ảnh được chuẩn hóa bỏ EXIF/GPS; bản tạm riêng
được dọn sau xử lý. Native không có chỉ số độ tin cậy tổng thể nên không hiển
thị phần trăm giả. Hủy bỏ kết quả đến muộn, không bảo đảm ML Kit dừng xử lý
ngay. Bản web/demo Windows tiếp tục dùng Tesseract đóng gói local.

Thêm công cụ cấu hình AI bằng khóa nhập ẩn, tệp cấu hình riêng và tệp khóa
ngoài mã nguồn/gói phát hành. AI chỉ hoạt động khi người vận hành cung cấp
dịch vụ, model và khóa hợp lệ; kiểm tra cấu hình không thay thế một yêu cầu
AI thật thành công. Chưa có khóa của người dùng để kích hoạt hoặc đánh giá
model thật trong môi trường này. Xem [AI_ACTIVATION.md](../AI_ACTIVATION.md).

ML Kit có thể gửi thông tin thiết bị/ứng dụng, mã định danh theo lần cài đặt
và thông tin hiệu năng, chẩn đoán cho Google. Nhận dạng ảnh trên thiết bị không
đồng nghĩa không có dữ liệu gửi ra ngoài. Trước xét duyệt cần đối chiếu bản
SDK và khai Data Safety/App Privacy, nhất là khi phục vụ trẻ em:

- https://developers.google.com/ml-kit/android-data-disclosure
- https://developers.google.com/ml-kit/ios-data-disclosure

Tích hợp mã nguồn/kiểm thử mô phỏng chưa chứng minh chất lượng nhận chữ trên
thiết bị thật. Còn kiểm thử quyền thư viện, vòng đời/picker, dấu tiếng Việt,
hiệu năng và độ chính xác trên Android/iPhone thật; build iOS bằng Xcode,
ký/AAB/IPA và thử nghiệm cửa hàng vẫn phụ thuộc tài khoản/hạ tầng của chủ app.
Bản .17 không thay đổi trạng thái production hoặc hoàn tất điều kiện phát hành.
