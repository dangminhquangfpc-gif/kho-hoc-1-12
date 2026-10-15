# Ảnh và trợ lý học tập — bản thử .17

Bản .17 giữ OCR Tesseract cho web/demo Windows, bổ sung OCR trên Android/iOS
bằng Google ML Kit và công cụ cấu hình AI cho người vận hành. OCR trình duyệt
đã được chạy thật bằng Chromium với chữ in tiếng Việt. Luồng native đã được
tích hợp trong mã nguồn; không suy ra kết quả thiết bị thật từ kiểm thử web
hoặc kiểm thử mô phỏng.

AI vẫn mặc định tắt cho tới khi người vận hành cung cấp khóa hợp lệ và model
tương thích. Chưa có tài khoản/khóa nhà cung cấp của người dùng để gọi hoặc
đánh giá chất lượng AI thật. Kiểm thử provider dùng mô phỏng; không coi phản
hồi mô phỏng là dịch vụ AI đang hoạt động.

## Dùng thử OCR ngay

Trong **Cá nhân → Ảnh và trợ lý học tập**, chọn ảnh PNG, JPEG hoặc WebP tĩnh.
Không cần đăng nhập để nhận chữ. Đợi kết quả, đối chiếu ảnh xem trước, sửa lại
chữ, số và công thức rồi đánh dấu **Tôi đã kiểm tra văn bản**. Có thể hủy nhận
dạng; văn bản đang có được giữ khi lỗi hoặc không đọc được chữ.

Nếu tài khoản đã lưu nhưng máy chủ mất kết nối, màn hình lỗi có nút
**Nhận chữ từ ảnh trên thiết bị**. Lối này chỉ nhận/sửa/xác nhận và sao chép
văn bản, không gọi AI hoặc thay đổi tài khoản, bài làm và lịch sử đã lưu.

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
  từ CDN hoặc gửi ảnh lên backend/nhà cung cấp OCR. Ảnh được vẽ lại để bỏ
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
khi ML Kit xử lý ngay trên thiết bị. Ứng dụng không tải ảnh lên backend hoặc
nhà cung cấp AI. Bản tạm thuộc ứng dụng được dọn khi xử lý kết thúc; ảnh gốc
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

## Trợ giảng AI khi có cấu hình thật

Đăng nhập để dùng AI; nhận chữ và các bài luyện có sẵn vẫn dùng khi AI tắt.
Người dùng chọn lớp/môn, sửa văn bản và xác nhận gửi cho nhà cung cấp được nêu
trong hộp thoại. Mỗi yêu cầu cần xác nhận riêng. Nếu nhà cung cấp trên máy chủ
đã đổi, yêu cầu bị từ chối để tải lại thông tin và xác nhận lại.

Nút **Nhờ AI giải thích** trong bài đã nộp có lựa chọn dùng tham chiếu của câu
đó. Khi bật, máy chủ còn gửi đề bài gốc, lựa chọn, đáp án và lời giải đã lưu;
chỉnh ô văn bản không chỉnh những dữ liệu tham chiếu này. Hộp xác nhận nói rõ
điều đó. Tắt lựa chọn để chỉ gửi văn bản đã kiểm tra cùng lớp/môn. Máy chủ chỉ
lấy tham chiếu từ bài đã nộp thuộc tài khoản hiện tại; không lấy lời giải từ
bài chưa nộp. Bài làm gốc của học viên không được thêm ngầm vào tham chiếu.

Ảnh, tên tài khoản và cookie/token đăng nhập không được đưa vào nội dung gửi
AI. Văn bản hoặc đề tham chiếu vẫn có thể chứa thông tin cá nhân nếu người
soạn nhập vào đó: cần loại bỏ trước khi gửi, hoặc chọn chỉ gửi phần văn bản
đã sửa. Không khẳng định AI đã kiểm chứng toàn bộ SGK Kết nối tri thức.

Phản hồi chỉ là hướng dẫn tham khảo, luôn cần kiểm tra lại. Không tạo điểm AI
chính thức, không thay đổi đáp án, bản nháp, bài nộp hoặc điểm đã chấm. Văn bản
AI không được tự ghi thành tài liệu hay câu hỏi công khai.

## Cấu hình backend cho người vận hành

Không cần cấu hình phần này để thử OCR. Chỉ bật AI sau khi có dịch vụ phù hợp,
đã xem điều khoản, chi phí, cách lưu/xử lý dữ liệu và cơ chế đồng ý phù hợp học
sinh. Không gửi khóa qua chat, đưa vào Git/ZIP, Flutter build define hoặc trình
duyệt. Ứng dụng không tự tạo tài khoản hay mua dịch vụ AI.

Backend hỗ trợ API có giao thức OpenAI Chat Completions với JSON object,
`max_tokens` và số token sử dụng. Chưa kiểm chứng tương thích với provider/model
thật nào; không có tích hợp Gemini riêng trong bản này. Khóa chỉ đọc từ một
tệp riêng, không phải giá trị biến môi trường chứa khóa.

| Biến backend | Mặc định / yêu cầu |
| --- | --- |
| `KHOHOC_AI_ENABLED` | `false`; đặt `true` khi chủ động bật |
| `KHOHOC_AI_BASE_URL` | `https://api.openai.com/v1`; URL HTTPS công khai, không thông tin đăng nhập/query/fragment, không chuyển hướng |
| `KHOHOC_AI_MODEL` | Trống; điền tên model thực sự hỗ trợ giao thức trên |
| `KHOHOC_AI_API_KEY_FILE` | Đường dẫn tệp khóa riêng có thể đọc bởi tiến trình backend |
| `KHOHOC_AI_DAILY_USER_LIMIT` | 10 lượt/tài khoản/ngày UTC; cấu hình 1–50 |
| `KHOHOC_AI_DAILY_SERVER_LIMIT` | 100 lượt/máy chủ/ngày UTC; cấu hình 1–500 |
| `KHOHOC_AI_OUTPUT_TOKENS` | 800; cấu hình 100–1.200 |

Trên POSIX, dùng tệp thường với quyền `0400` hoặc `0600`, do tài khoản chạy
backend sở hữu và đọc được; không dùng symlink, FIFO hoặc tệp cho nhóm/người
khác đọc. Trên Windows, giới hạn ACL của tệp và thư mục cho người vận hành;
kiểm tra mode POSIX không thay thế ACL Windows. Không để tệp trong thư mục
được web server phục vụ.

Với demo Windows, dừng demo rồi chạy `configure-ai.bat`. Công cụ hỏi khóa bằng
ô nhập ẩn và lưu cấu hình không bí mật tại `state/ai-config.json`, khóa tại
`state/ai-secret.api-key` với quyền truy cập riêng. Sau đó chạy lại
`start-demo.bat`. Không đưa khóa vào tham số dòng lệnh, chat hay mã Flutter.
Thư mục `state` lúc này có thể chứa khóa thật: không chia sẻ hoặc đưa vào gói
phát hành. Hướng dẫn bật/tắt, kiểm tra và bảo vệ khóa: [AI_ACTIVATION.md](AI_ACTIVATION.md).

Công cụ `--status` kiểm tra cấu hình cục bộ, không xác minh khóa có hoạt động
với nhà cung cấp hay đánh giá câu trả lời AI. Chỉ coi AI kết nối thật sau khi
đã gọi thành công một yêu cầu được người dùng xác nhận. Cấu hình AI tường minh
qua biến môi trường có ưu tiên hơn tệp local. Launcher không tự đọc `.env`;
`.env.example` là mẫu. Khi đổi cấu hình cần dừng và chạy lại.

Với pilot Docker, Compose mặc định vẫn tắt AI và chưa mount khóa. API chạy
`10001:10001`; tệp bind-mount cần thuộc UID/GID này và quyền `0400` hoặc `0600`.
Không mở quyền thành `0444/0644` để container đọc vì kiểm tra khóa sẽ từ chối.
Ví dụ override riêng tại `deploy/shared/ai.private.yaml` (đã được bỏ qua trong
Git), sau khi người vận hành chuẩn bị tệp `secrets/ai.api-key`:

```yaml
services:
  api:
    environment:
      KHOHOC_AI_ENABLED: "true"
      KHOHOC_AI_BASE_URL: https://api.openai.com/v1
      KHOHOC_AI_MODEL: THAY_BANG_MODEL_DA_KIEM_TRA
      KHOHOC_AI_API_KEY_FILE: /run/secrets/ai.api-key
      KHOHOC_AI_DAILY_USER_LIMIT: "10"
      KHOHOC_AI_DAILY_SERVER_LIMIT: "100"
      KHOHOC_AI_OUTPUT_TOKENS: "800"
    volumes:
      - ./secrets/ai.api-key:/run/secrets/ai.api-key:ro
```

Chủ máy chủ thiết lập chủ sở hữu/quyền trên tệp thật rồi khởi động Compose với
cả hai tệp `-f deploy/shared/compose.yaml -f deploy/shared/ai.private.yaml`.
Đây là cấu hình để người vận hành xem xét, chưa được kích hoạt hay triển khai.
Không dùng khóa thật trong kiểm thử tự động. Giữ proxy/CA hợp lệ của môi trường;
không tắt xác minh TLS để khắc phục lỗi kết nối.

## Giới hạn và xử lý lỗi

Backend xác thực tài khoản, lớp/môn và xác nhận đồng ý, giới hạn 6.000 ký tự
nhập và 32 KiB UTF-8 cho toàn bộ nội dung người dùng kèm tham chiếu. Nội dung
tham chiếu quá dài bị từ chối, không cắt mất một phần đáp án để gửi ngầm.
Yêu cầu chỉ tới URL operator cấu hình, không nhận URL hoặc khóa từ client.

Quota lưu trong database, cập nhật nguyên tử giữa các worker: tối đa 3 lượt
mỗi tài khoản/phút, cộng hạn mức ngày của tài khoản và toàn máy chủ. Cửa sổ
phút/ngày cố định; ngày đổi lúc 00:00 UTC. Lượt đã đặt quota để gọi provider
vẫn tính nếu dịch vụ lỗi hoặc quá hạn. Sai đăng nhập/consent/host/tham chiếu,
AI chưa cấu hình hoặc nội dung quá dài bị chặn trước khi đặt quota.

Mỗi lần gọi có hạn tổng 20 giây, phản hồi tối đa 128 KiB, không tự retry hoặc
đi theo chuyển hướng. Backend kiểm tra JSON, độ dài, số token và chỉ trả văn
bản thuần; không chạy công cụ, mã hay HTML do mô hình trả về. Lỗi provider trả
thông báo chung, không lộ khóa/nội dung gửi trong lỗi. Mất kết nối không thay
đổi điểm bài làm; có thể thử lại thủ công nhưng lần gửi mới có thể tính thêm quota.

Nhật ký backend giữ ID tài khoản, thời điểm, model, trạng thái, số ký tự và
số token của lượt thành công; không giữ ảnh, văn bản yêu cầu hoặc nội dung
phản hồi AI trong nhật ký này. Quota không phải hạn mức tiền cứng của provider;
cần đặt thêm hạn mức thanh toán ở dịch vụ thật. Chưa có bảng điều khiển chi phí
hoặc lịch tự xóa/ẩn danh nhật ký AI. Điều khoản lưu giữ/huấn luyện của nhà cung
cấp cần được kiểm tra riêng; không suy ra từ việc app không lưu văn bản.

## Đã kiểm tra và phần còn lại

Đã kiểm tra nhận dạng tiếng Việt thật bằng Chromium, lựa chọn PNG/JPEG/WebP,
giới hạn tệp/kích thước, hủy/hết hạn và không truy cập URL ngoài trong kiểm thử
OCR. Backend có kiểm thử provider mô phỏng cho quyền truy cập, tham chiếu bài
đã nộp, quota nguyên tử, host/consent, dữ liệu quá dài, lỗi JSON/redirect/timeout
và việc giữ nguyên điểm. Các kiểm tra này không đánh giá chất lượng AI thật.

Còn: kiểm thử native trên thiết bị thật; chụp camera/cắt ảnh trong app; chữ viết
tay và công thức toán; nhập
đề OCR có người duyệt; chấm tự luận theo rubric; lưu/yêu cầu xem xét/báo lỗi
phản hồi AI; đánh giá model thật và tập dữ liệu sư phạm; bảng chi phí; quy trình
trẻ em/nhà cung cấp, retention và kiểm thử thiết bị thật. Backend Internet và
ký/phát hành cửa hàng vẫn chưa hoàn tất. Không coi .17 là hoàn thành toàn bộ
giai đoạn AI/OCR hoặc đủ điều kiện phát hành.
