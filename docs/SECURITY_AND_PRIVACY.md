# Bảo mật và quyền riêng tư — bản thiết kế

Chế độ khách không yêu cầu tên, email, trường, vị trí hoặc tuổi chi tiết. Backend chỉ nhận câu trả lời và ID đề. Lịch sử giữ trên thiết bị; server lưu attempt để retry. Có xóa từng attempt qua token. Không có AI call, ads, chat hoặc payments trong MVP mới.

Token admin phát triển nằm ngoài checkout (/workspace/state/khohoc.env); cookie admin HttpOnly, SameSite Strict, HMAC và hạn 1h. Next server giữ token, không nhúng browser bundle. Token guest giữ cục bộ; trước production cần encrypted storage cho thiết bị. Không dùng token phát triển làm cơ chế đăng nhập production.

API chỉ bind loopback; mode production từ chối khởi động vì chưa có JWT/Supabase adapter. Cần HTTPS/gateway rate limits, consent phù hợp trẻ em, retention worker, backup, key rotation, auditing và account deletion khi thêm tài khoản. Không coi tài liệu này là Privacy Policy pháp lý đã duyệt.

Migration RLS không cho client ghi điểm/role hoặc đọc versions/snapshots; chỉ owner đọc kết quả đã nộp. Parent/teacher role chưa cấp quyền truy cập. SQL auth shim chỉ phục vụ kiểm thử local.

## Tài khoản local bản .6

Học viên tự đăng ký được gắn với người quản lý của máy chủ. Người quản lý xem kết quả học viên thuộc mình; giao diện đăng ký thông báo việc này. Mật khẩu scrypt, cookie HttpOnly 8 giờ, quyền và điểm được kiểm tra trên backend. Hướng dẫn vận hành và giới hạn: [CLASSROOM_ACCOUNTS.md](CLASSROOM_ACCOUNTS.md).
