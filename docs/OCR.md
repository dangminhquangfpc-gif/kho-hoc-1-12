# Nhận chữ từ ảnh (OCR) — bản .18

Bản này đã gỡ trợ lý AI trả phí khỏi giao diện, API và launcher. Không cần
khóa API hay tài khoản nhà cung cấp để nhận chữ. OCR không thu phí dịch vụ
nhận dạng; chi phí vận hành máy chủ/tài khoản cửa hàng là phần riêng.

## Dùng thử OCR ngay

Trong **Cá nhân → Nhận chữ từ ảnh**, chọn ảnh PNG, JPEG hoặc WebP tĩnh.
Không cần đăng nhập để nhận chữ. Đợi kết quả, đối chiếu ảnh xem trước, sửa lại
chữ, số và công thức rồi đánh dấu **Tôi đã kiểm tra văn bản**. Có thể hủy nhận
dạng; văn bản đang có được giữ khi lỗi hoặc không đọc được chữ.

Nếu tài khoản đã lưu nhưng máy chủ mất kết nối, màn hình lỗi có nút
**Nhận chữ từ ảnh trên thiết bị**. Lối này chỉ nhận/sửa/xác nhận và sao chép
văn bản, không thay đổi tài khoản, bài làm và lịch sử đã lưu.

Trong câu trả lời ngắn, số hoặc tự luận, **Nhập từ ảnh hoặc văn bản** mở cùng
luồng kiểm tra. Chọn
**Dùng văn bản này cho câu trả lời** mới điền vào ô bài làm; thao tác này không
tự nộp hoặc tự chấm bài. Khi điền vào bài đang làm, văn bản đó trở thành câu
trả lời và chịu quy tắc lưu bản nháp/nộp bài như nội dung gõ tay.

- Giới hạn ảnh: 8 MiB, 16 triệu điểm ảnh, mỗi cạnh không quá 6.000 điểm ảnh.
  Kiểm tra định dạng và kích thước trước khi giải mã; ảnh được thu nhỏ còn tối
  đa 8 triệu điểm ảnh/cạnh 3.200 để nhận dạng. Chưa nhận PDF, SVG, GIF hoặc ảnh động.
- Màn hình giữ tối đa 6.000 ký tự để sửa; văn bản dài cần chia nhỏ ảnh.
- Chữ in phù hợp hơn chữ viết tay. Phân số, số mũ, dấu tiếng Việt và hình vẽ
  có thể sai. OCR không xác minh kiến thức hay chấm điểm bài làm.

### Web và demo Windows

Bộ nhận chữ tiếng Việt/Anh, worker và WebAssembly nằm trong gói; không tải
  từ CDN hoặc gửi ảnh lên backend/dịch vụ OCR. Ảnh được vẽ lại để bỏ
  EXIF/GPS trước khi đưa vào worker và tạo xem trước. Không ghi ảnh vào
  localStorage/IndexedDB. Ảnh và văn bản trên màn hình giữ trong bộ nhớ; không
  tự lưu thành lịch sử/bản nháp cho tới khi người dùng đưa văn bản vào bài làm.

Mỗi lần chỉ nhận một ảnh, tối đa 60 giây xử lý; hủy/lỗi/hết hạn giải phóng
worker. Độ tin cậy Tesseract không phải điểm bài làm hay xác suất đáp án đúng.

Nguồn, phiên bản, giấy phép và checksum ở `apps/mobile/web/ocr/PROVENANCE.json`,
`licenses/` và `SHA256SUMS`; cũng được đưa vào gói web/Windows. Tái kiểm tra
không cần mạng: `python scripts/prepare_ocr_assets.py --verify`. Hướng dẫn tái
tạo tài sản từ tarball đã ghim nằm trong `apps/mobile/web/ocr/README.md`.

### Ứng dụng native Android/iOS

Ứng dụng chọn một ảnh từ thư viện bằng `image_picker` 1.2.2 rồi nhận chữ bằng
`google_mlkit_text_recognition` 0.15.0, bộ Latin của Google ML Kit. Phần native
dùng Text Recognition Android 16.0.1/iOS 7. Ứng dụng yêu cầu Android tối thiểu
7.0 (API 24) theo Flutter 3.35.7 và iOS tối thiểu 15.5. Model được đưa vào
ứng dụng; đây không phải luồng OCR chạy trong trình duyệt.
Chưa có nút chụp camera hay yêu cầu quyền camera trong luồng OCR này.
Ảnh HEIC/HEIF chưa được nhận trực tiếp; nếu bộ chọn ảnh không xuất thành JPEG,
cần đổi ảnh sang JPEG hoặc PNG trước khi dùng.

Ảnh được kiểm tra, giải mã và vẽ lại thành bản PNG tạm để bỏ EXIF/GPS trước
khi ML Kit xử lý ngay trên thiết bị. Ứng dụng không tải ảnh lên backend. Bản tạm thuộc ứng dụng được dọn khi xử lý kết thúc; ảnh gốc
trong thư viện không bị xóa. Nếu ứng dụng bị hệ điều hành dừng đột ngột, bản
cache riêng có thể còn tới khi hệ điều hành dọn. Văn bản không tự trở thành
lịch sử hay câu trả lời cho tới khi người dùng chọn dùng nó.

Google ML Kit không cung cấp độ tin cậy tổng thể tương đương Tesseract, nên
màn hình không tạo phần trăm giả cho native. Người dùng vẫn phải đối chiếu ảnh,
đặc biệt với dấu tiếng Việt, chữ viết tay và công thức toán. Hủy hoặc hết hạn
giữ nguyên văn bản đang sửa và bỏ kết quả đến muộn; ML Kit không có API ép
dừng ngay việc native đang chạy. Lượt tiếp theo có thể phải chờ dọn lượt cũ.

Xử lý ảnh trên thiết bị không có nghĩa SDK không kết nối mạng. Theo công bố
của Google, ML Kit có thể thu thập/gửi thông tin thiết bị, ứng dụng, mã định
danh theo lần cài đặt và thông tin chẩn đoán/hiệu năng; tùy API có thông tin
định dạng, độ phân giải hoặc kích thước dữ liệu đầu vào/đầu ra. Nội dung ảnh
không được gửi bởi luồng nhận dạng trên thiết bị này. Cần khai đúng SDK và dữ
liệu chẩn đoán trong Data Safety/App Privacy của bản phát hành thực tế:

- Android: https://developers.google.com/ml-kit/android-data-disclosure
- iOS: https://developers.google.com/ml-kit/ios-data-disclosure

Các nền tảng native khác vẫn có thể nhập hoặc dán văn bản thủ công. Quyền truy
cập thư viện ảnh do hệ điều hành quản lý; nếu từ chối, người dùng có thể chọn
lại quyền trong Cài đặt hoặc nhập văn bản. Còn cần kiểm thử chọn ảnh/quyền ảnh,
vòng đời ứng dụng và độ chính xác trên thiết bị Android/iPhone thật.

## Kiểm tra kỹ thuật

- Web: `python scripts/prepare_ocr_assets.py --verify` và `node scripts/test_browser_ocr.cjs`.
- Flutter: `flutter test --no-pub test/ocr_screen_test.dart test/offline_ocr_test.dart test/native_ocr_test.dart`.
- Android emulator: workflow `native-ocr-validation.yml` nhận chữ tiếng Việt thật
  với Wi-Fi/dữ liệu di động tắt; không thay thế kiểm thử picker trên máy thật.
- iOS: workflow `ios-engineering.yml` build unsigned với SDK26+; cần máy iPhone
  và ký hợp lệ để nghiệm thu runtime trước phát hành.

Cấu hình/khóa AI cũ trong `state` không bị xóa tự động và không được app .18
đọc/sử dụng. Không sao chép tệp riêng này vào mã nguồn hoặc gói phát hành.
