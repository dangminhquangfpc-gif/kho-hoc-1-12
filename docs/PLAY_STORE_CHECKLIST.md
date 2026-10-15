# Chuẩn bị Tự học 111 cho Google Play — bản .18

Đã tạm gỡ trợ lý AI trả phí; giữ nhận chữ OCR miễn phí. Chưa gửi xét duyệt.
Xem [trạng thái](store/RELEASE_STATUS.md) và [kết quả kiểm thử](VALIDATION.md).

## Kiểm tra kỹ thuật có thể làm ngay

```sh
# Tại gốc repository, Flutter đã có trong PATH và đã flutter pub get --enforce-lockfile:
python scripts/store_preflight.py --platform android --engineering --build --report android-engineering.json
```

Lệnh này không gọi backend và không dùng khóa ký đang có trên máy. Gói kết quả
`apps/mobile/build/app/outputs/bundle/release/app-release.aab` là AAB **không ký**,
chỉ để kiểm tra, không tải lên Play. Báo cáo gồm hash, các thư viện 64-bit/căn
bộ nhớ 16 KB và trạng thái chưa kiểm thử runtime thiết bị 16 KB. Workflow
`android-engineering.yml` lưu gói/báo cáo 14 ngày. Chữ ký debug APK dùng thử
không thay cho chữ ký upload.

## Hồ sơ để chủ ứng dụng hoàn thiện

- [Tên, mô tả cửa hàng](store/LISTING_DRAFT.md).
- [Biểu tượng và feature graphic](store/BRAND_ASSETS.md).
- [Bản nháp chính sách quyền riêng tư](store/PRIVACY_DRAFT.md).
- [Bảng đối chiếu Data Safety](store/DATA_SAFETY_WORKSHEET.md).
- [Luồng kiểm tra và tài khoản reviewer](store/REVIEWER_GUIDE.md).

Các bản nháp chưa có tên nhà phát hành/email/URL thật. Cần vận hành công khai
trang chính sách và yêu cầu xóa tài khoản ngoài app; không điền URL ví dụ để
nộp xét duyệt. App đã có tự xóa tài khoản bằng mật khẩu xác nhận.

## Trình tự đưa lên Play

1. Chủ ứng dụng tạo/xác minh Play Console, cung cấp danh tính nhà phát hành,
   email hỗ trợ và chọn phạm vi tuổi thực tế. App phục vụ lớp 1–12 nên cần
   hoàn thiện yêu cầu trẻ em/giám hộ và quyền truy cập kết quả trước khi mở rộng.
2. Hoàn thiện adapter xác thực/dữ liệu production, triển khai backend HTTPS,
   backup/khôi phục/giám sát và kênh xử lý xóa dữ liệu. Backend hiện vẫn khóa
   production. Windows localhost không phải backend chung cho Play.
3. Rà soát chuyên môn, đáp án và quyền nội dung. Không tuyên bố đã phủ đủ
   mọi SGK/môn/lớp hoặc đã sao chép đầy đủ PDF nguồn Internet.
4. Nghiệm thu Android thật: cài/nâng cấp, đăng nhập, các vai trò, luyện/nộp,
   mất mạng/khôi phục, OCR/picker/quyền ảnh, xóa tài khoản và khả năng truy cập.
   Chụp screenshot từ app native với dữ liệu giả được phép công khai.
5. Tạo/lưu riêng khóa upload, cấu hình `apps/mobile/android/key.properties`
   ngoài Git; sao lưu khóa an toàn. Không gửi khóa/mật khẩu trong chat.
6. Điền bản riêng từ `deploy/store/publisher.example.json`, chỉ xác nhận những
   mục đã hoàn tất. Chạy preflight bản phát hành với URL/config thật:

```sh
python scripts/store_preflight.py --platform android --api-base-url https://TEN-MIEN-CUA-BAN/api --publisher-config /DUONG-DAN-RIENG/publisher.json --build --report android-release.json
```

7. Xác minh gói đã ký đúng upload certificate, tăng versionCode so với bản
   trước, khai App signing/Data Safety/content rating/app access; chạy internal
   rồi closed testing theo yêu cầu Play Console của tài khoản. Sửa lỗi từ
   pre-launch report trước khi đề nghị production. Chỉ chủ app xác nhận gửi.

Không cần khóa hoặc đăng ký dịch vụ AI cho bất kỳ bước nào trên.

Nguồn chính thức (cần đối chiếu lại lúc gửi):
- Target API: https://support.google.com/googleplay/android-developer/answer/11926878
- 16 KB: https://developer.android.com/guide/practices/page-sizes
- Xóa tài khoản: https://support.google.com/googleplay/android-developer/answer/13327111
- Kiểm thử tài khoản cá nhân mới: https://support.google.com/googleplay/android-developer/answer/14151465
