# Bật trợ lý AI bằng dịch vụ thật

AI cần khóa API và hạn mức sử dụng của nhà cung cấp. Mã ứng dụng không tạo khóa,
mua dịch vụ hoặc có sẵn khóa chung. Việc lưu cấu hình chỉ chuẩn bị kết nối;
một yêu cầu thành công tới dịch vụ thật mới xác nhận khóa/model/hạn mức hợp lệ.
OCR không cần khóa AI.

## Demo Windows

1. Dừng demo đang chạy và sao lưu thư mục `state` ở nơi riêng tư.
2. Mở `configure-ai.bat` trong gói .17. Công cụ dùng Python đã kèm trong ZIP,
   không yêu cầu cài phần mềm hoặc tải thư viện để nhập cấu hình.
3. Nhập khóa API khi công cụ hỏi. Phần nhập khóa được ẩn; không đưa khóa vào
   chat, ảnh chụp màn hình, tham số dòng lệnh hoặc tệp web.
4. Mặc định dùng OpenAI `gpt-4.1-mini` qua Chat Completions. Tạo khóa và thiết
   lập hạn mức thanh toán tại [OpenAI API](https://platform.openai.com/api-keys).
   Tài khoản ChatGPT hoặc gói ChatGPT trả phí không tự cấp hạn mức API.
5. Chạy `start-demo.bat` lại. Đăng nhập trong app, vào **Ảnh và trợ lý học tập**,
   nhập một câu ngắn không có thông tin cá nhân, kiểm tra văn bản và xác nhận
   dịch vụ đích trước khi gửi. Chỉ coi kết nối hoạt động khi nhận được phản hồi
   thật. Nếu khóa, thanh toán hoặc model chưa dùng được, app báo lỗi thay vì
   dựng lời giải giả.

Cấu hình không chứa khóa được lưu ở `state/ai-config.json`; khóa nằm riêng ở
`state/ai-secret.api-key`. Công cụ giới hạn quyền tệp trước khi ghi: `0600`
trên POSIX, ACL tài khoản Windows hiện tại trên Windows. Không chia sẻ thư mục
`state`, vì thư mục còn có tài khoản, kết quả học tập và khóa AI khi đã cấu hình.

Có thể mở CMD trong thư mục gói để xem trạng thái cấu hình hoặc tắt AI:

```bat
configure-ai.bat --status
configure-ai.bat --disable
```

`--status` không gọi dịch vụ và không in khóa. `--disable` tắt cấu hình local,
không thu hồi khóa tại nhà cung cấp. Cần dừng/chạy lại demo sau khi thay đổi.
Nếu nghi lộ khóa, thu hồi khóa ở nhà cung cấp rồi thay bằng khóa mới.

Công cụ `scripts/configure_ai.py` chỉ dùng thư viện chuẩn; trên máy đã có
Python 3.12 có thể chạy:

```bash
python scripts/configure_ai.py --state state
```

Nhà cung cấp tương thích OpenAI khác có thể được chọn bằng `--base-url` và
`--model` (đều là thông tin không bí mật). Không tự coi các dịch vụ tương thích
hoàn toàn: cần kiểm tra JSON object, `max_tokens`, metadata token và phản hồi
thật. Ví dụ Gemini có endpoint tương thích OpenAI; không có khóa Gemini chung
hoặc dịch vụ Gemini riêng được bật sẵn trong ứng dụng này.

## Cloud development

Đã chuẩn bị yêu cầu cấu hình bảo mật trong cài đặt môi trường:

- Bí mật `KHOHOC_AI_API_KEY`, chỉ dùng tới `api.openai.com` qua proxy HTTPS.
- `KHOHOC_AI_ENABLED=true`, `KHOHOC_AI_BASE_URL=https://api.openai.com/v1`,
  `KHOHOC_AI_MODEL=gpt-4.1-mini`.
- Hạn mức mặc định: 10 lượt/tài khoản/ngày, 100 lượt/máy chủ/ngày và 800 token
  phản hồi; vẫn có giới hạn 3 lượt/phút/tài khoản.

Người vận hành nhập khóa trong mục bí mật của cài đặt môi trường, lưu và xuất
bản môi trường để áp dụng. Lưu bản nháp không cung cấp khóa và không thay đổi
tiến trình đang chạy. Sau khi áp dụng cần khởi động lại backend, kiểm tra lại
trạng thái binding và thực hiện một yêu cầu AI thật với nội dung thử không có
thông tin cá nhân. Không chép placeholder của proxy thành tệp khóa.

Backend chấp nhận một trong hai nguồn: `KHOHOC_AI_API_KEY` từ môi trường bảo mật
hoặc `KHOHOC_AI_API_KEY_FILE` trỏ tới tệp riêng. Có cả hai nguồn thì từ chối
cấu hình để tránh gửi nhầm khóa. Không lưu khóa trong Flutter hoặc APK/IPA.

Launcher chọn toàn bộ biến AI được truyền trực tiếp nếu có bất kỳ biến AI nào;
nếu không có, mới đọc cấu hình local. Không ghép khóa trong file với host/model
từ môi trường. Vì thế, khi dùng `configure-ai.bat`, hãy bỏ cấu hình AI cũ đã
export trong cửa sổ khởi động. Riêng `KHOHOC_AI_ENABLED=false` trong môi trường
có thể tắt AI và bỏ qua cấu hình local bị hỏng.

## Máy chủ dùng chung và điện thoại

Khóa chỉ nằm trên backend. Chạy native trên điện thoại không làm localhost
của máy Windows/cloud trở thành máy chủ truy cập được từ điện thoại. Cần một
backend HTTPS dùng chung và cấu hình địa chỉ trong **Cá nhân → Địa chỉ máy chủ**
để đăng nhập, học/đồng bộ và gọi AI trên thiết bị khác.

Pilot Docker mặc định chưa bật AI. Cách bind tệp riêng cho UID `10001` và
biến cấu hình được ghi ở [AI_OCR.md](AI_OCR.md). Không đặt khóa trực tiếp trong
Compose hoặc đổi tệp khóa thành world-readable để container đọc được.

## Khi có lỗi

Không đưa khóa hoặc toàn bộ log lên chat. Thông báo `chưa cấu hình` thường do
thiếu cấu hình/khóa, sai quyền tệp hoặc hai nguồn khóa đồng thời. Lỗi dịch vụ
có thể do khóa không hợp lệ, hết hạn mức, billing/model, JSON không đúng hoặc
hết thời gian. Hệ thống không công khai nội dung lỗi thô từ provider.

Lượt đã dành quota vẫn tính khi provider lỗi; không tự gửi lại. Quota ứng dụng
không thay thế giới hạn tiền tại nhà cung cấp. Hướng dẫn AI luôn là tham khảo,
cần đối chiếu giáo viên/SGK và không tự thay đổi điểm.
