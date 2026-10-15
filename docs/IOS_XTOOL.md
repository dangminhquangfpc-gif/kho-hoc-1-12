# Cài Tự học 111 iOS bằng xtool của bạn

Repo đã thêm: https://github.com/dangminhquangfpc-gif/xtool tại `/workspace/xtool`.
Checkout được giữ nguyên. Fork chưa có binary release riêng; helper dùng bản
CLI chính thức **xtool-org/xtool 1.22.2**, kiểm tra SHA256 do GitHub cung cấp
trước khi chạy. Không tuyên bố binary này được build từ HEAD của fork.

Đây là cách thay Sideloadly bằng xtool. `xtool install` ký và cài IPA có sẵn,
không yêu cầu chuyển app Flutter sang Swift. Chỉ cài IPA thì dùng `auth login`
và `install`, không chạy toàn bộ `xtool setup` (bước setup còn đòi Swift SDK và
Xcode.xip để build dự án Swift). Không cần tải Xcode/Swift để dùng gói này.

## Windows: chuẩn bị WSL và kết nối iPhone

1. Cài WSL2/Ubuntu theo https://learn.microsoft.com/windows/wsl/install
   (`wsl --install` trong PowerShell quản trị nếu máy chưa có; có thể cần khởi
   động lại). Đây là thao tác trên máy Windows của bạn, không phải cloud.
2. Cài usbipd-win theo https://learn.microsoft.com/windows/wsl/connect-usb.
   Nối iPhone bằng cáp, mở khóa và tin cậy máy tính của bạn. Trong PowerShell
   quản trị chạy `usbipd list`, tìm BUSID của đúng iPhone rồi chạy
   `usbipd bind --busid BUSID`. Thay BUSID bằng giá trị thật trên máy bạn.
3. Giữ Ubuntu/WSL đang chạy; trong PowerShell chạy
   `usbipd attach --wsl --busid BUSID`. Trong Ubuntu, chuẩn bị gói:

   ```bash
   sudo apt-get update
   sudo apt-get install ca-certificates curl usbmuxd libimobiledevice-utils unzip zip
   ```

   Nếu cần, khởi động dịch vụ `usbmuxd` theo cấu hình Ubuntu/WSL của bạn.
   Chạy `idevice_id -l` để kiểm tra thấy thiết bị; chấp nhận yêu cầu tin cậy
   trên iPhone. Nếu không thấy, xử lý USB trước khi đăng nhập Apple.
4. Với iOS 16+, bật Developer Mode theo
   https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device
   rồi khởi động lại/xác nhận nếu iPhone yêu cầu. App cần iOS/iPadOS 15.5+.

## Ký và cài bằng gói tải xuống

Giải nén **toàn bộ** `tu-hoc-111-xtool-wsl.zip`. Gói có IPA .20 chưa ký,
hai script và hướng dẫn; không có tài khoản, khóa ký hoặc profile riêng tư.
Mở thư mục này trong Ubuntu/WSL (ví dụ đường dẫn Windows C: ở `/mnt/c/…`):

```bash
bash install-ios.sh --check
# Chỉ sau khi thấy thiết bị USB:
bash install-ios.sh --login
```

Helper kiểm tra SHA256 IPA, cài CLI đã khóa phiên bản, kiểm tra USB rồi mới
đăng nhập. `--check` không đăng nhập/ký/cài; mã thoát 3 nghĩa là chưa thấy USB.
`--login` là yêu cầu đăng nhập lại tường minh; chọn tài khoản Apple của chính
bạn trong prompt xtool. Password mode hỗ trợ Apple ID miễn phí và dùng API
riêng của Apple theo tài liệu xtool; không phải luồng được Apple bảo đảm ổn
định. Chỉ nhập mật khẩu/2FA tại terminal riêng, không dùng tham số `--password`
hoặc gửi thông tin đó vào chat/GitHub. Không chạy với `sudo`, không bật `set -x`
hoặc ghi log toàn bộ quá trình đăng nhập.

Lần refresh sau có thể dùng `bash install-ios.sh` để dùng lại đăng nhập xtool.
Apple ID miễn phí thường cần ký lại sau khoảng 7 ngày. Giữ cùng tài khoản/
bundle ID và cài đè để giữ lịch sử; không gỡ app khi refresh. Nếu phiên Apple
hết hạn, chủ động dùng lại `--login`. Không có TestFlight/App Store trong gói.

Sau khi cài, mở app, thử làm/nộp một đề ngoại tuyến và xem lịch sử. OCR, Keychain
và cài đặt iPhone thật vẫn cần nghiệm thu trên thiết bị của bạn. Native xtool
có thể in UDID/tài khoản khi chạy; che thông tin riêng trước khi chia sẻ lỗi.

## Những gì đã kiểm tra trong cloud

Repo fork được clone và đọc hướng dẫn; CLI x86_64 1.22.2 chạy được sau khi
kiểm SHA và giải nén AppImage, không cần FUSE. Lệnh version/help/auth/install
và tìm thiết bị không chờ đã chạy. Cloud không thấy iPhone USB; chưa đăng nhập
Apple, cấp certificate, ký hoặc cài trên thiết bị. Nhánh source fork chưa được
build/test Swift đầy đủ; cài CLI prebuilt không chứng minh môi trường build
Swift SDK đã sẵn sàng. Script không tự bật WSL/USBIPD hoặc cài gói hệ thống.

Nguồn: README/AGENTS và Documentation/xtool.docc/Installation-Linux.md trong
fork; https://github.com/xtool-org/xtool/releases/tag/1.22.2.
