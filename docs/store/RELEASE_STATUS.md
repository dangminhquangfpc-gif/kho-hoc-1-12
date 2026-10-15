# Tự học 111 — chuẩn bị Google Play và App Store

Bản 0.2.0+11 / demo 2026.10.15.11. Chưa phát hành lên cửa hàng.
Người dùng xác nhận chưa có Play Console, Apple Developer hoặc backend HTTPS dùng chung.
Không tạo tài khoản, thanh toán hoặc đưa backend development chứa dữ liệu học viên ra Internet.

## Những phần đã chuẩn bị trong mã nguồn

- Tên hiển thị Android, web, iOS: Tự học 111; giữ application ID Android để giữ dữ liệu khi nâng cấp.
- Android compile/target API 36; cấu hình ký upload dùng android/key.properties ngoài Git, không dùng khóa debug cho release.
- Khung iOS, Podfile, privacy manifest cho UserDefaults (CA92.1), không bật tracking.
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
