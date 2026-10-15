# Nhận diện Tự học 111

Bộ nhận diện gốc gồm ba số một và cuốn sách mở, dùng màu chàm `#263677`, màu ngọc `#51d9ca` và trắng. Không dùng logo Flutter, logo nhà xuất bản hay hình ảnh của bên thứ ba. Hình thức này không thể hiện quan hệ hợp tác hoặc xác nhận từ nhà xuất bản sách giáo khoa.

Nguồn vector có thể chỉnh sửa:

- `assets/brand/tu-hoc-111-icon.svg`: biểu tượng nền vuông, không tự bo góc.
- `assets/brand/tu-hoc-111-feature.svg`: đồ họa giới thiệu với tên app và dòng “Học theo chủ đề. Luyện tập mỗi ngày.”

Các tệp tải lên Google Play đã chuẩn bị:

- `docs/store/assets/icon-512.png`: 512 × 512 pixel, PNG RGB 8 bit, nền kín.
- `docs/store/assets/feature-1024x500.png`: 1024 × 500 pixel, PNG RGB 8 bit, nền kín.

Đây là đồ họa giới thiệu, không phải ảnh chụp màn hình. Cần bổ sung ảnh chụp màn hình từ bản phát hành thực tế trước khi gửi duyệt. Không ghi rằng ứng dụng có AI trả phí hay đã bao phủ toàn bộ sách giáo khoa.

Android có biểu tượng PNG cho API 24–25, adaptive icon từ API 26 và lớp monochrome cho giao diện theo màu hệ thống từ API 33. Hình sách và số nằm trong vùng an toàn của adaptive icon. iOS có đủ kích thước theo `Contents.json`, bao gồm biểu tượng 1024 × 1024, không có kênh alpha. Web có favicon, biểu tượng thường và maskable với cùng màu nền. Hệ điều hành tự áp dụng mặt nạ hoặc bo góc.

Tạo lại bằng Inkscape 1.4, ImageMagick 7.1 và font Noto Sans đã cài trên máy:

```bash
python3 scripts/build_brand_assets.py
python3 scripts/build_brand_assets.py --check
```

Script chạy ngoại tuyến, xóa thông tin thời gian khỏi PNG và kiểm tra kích thước, định dạng RGB nền kín. `--check` tạo tệp vào thư mục tạm rồi so sánh byte với tài nguyên đã lưu. Khác phiên bản trình kết xuất hoặc font có thể tạo PNG khác; khi cập nhật công cụ, xem lại hình ảnh trước khi chấp nhận kết quả. Font Noto Sans được dùng trong đồ họa giới thiệu; xem giấy phép OFL của font trong `apps/mobile/assets/fonts/OFL.txt`.

`docs/store/assets/brand-assets.sha256.json` ghi mã SHA-256 của toàn bộ tài nguyên được tạo. Thiết kế và nguồn vector này được tạo cho dự án Tự học 111; không sao chép hình minh họa hay logo ngoài dự án.
