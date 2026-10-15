# Sao lưu dữ liệu bản local

Công cụ `scripts/backup_local.py` dành cho SQLite hiện tại; chưa phải hạ tầng
sao lưu PostgreSQL hay dịch vụ cloud tự động. Cần Python và các thư viện trong
`services/api/requirements.lock.txt` (đã có cryptography).

Tạo khóa một lần, lưu ngoài thư mục mã nguồn và ngoài nơi lưu bản sao:

```sh
python scripts/backup_local.py keygen --key-file /duong-dan-rieng/school.backup-key
python scripts/backup_local.py backup --database /duong-dan/state/khohoc.db --archive /noi-sao-luu/school-2026-10-15.tuhocbackup --key-file /duong-dan-rieng/school.backup-key
```

Thay các đường dẫn bằng đường dẫn thật. Trên Windows có thể dùng đường dẫn
`C:\...`; đặt trong dấu ngoặc kép nếu có khoảng trắng. Không gửi khóa qua chat.
Khóa bị mất thì không khôi phục được. Sao lưu khóa ở vị trí riêng có kiểm soát.

Bản sao gồm toàn bộ dữ liệu trong database: tài khoản, mật khẩu đã băm, nhóm,
phiên đăng nhập, đề, bài làm và kết quả. Không bao gồm PDF, cấu hình, tệp tài khoản
quản lý ban đầu hoặc tài nguyên giao diện. Những tệp này cần lưu riêng. Vì có
phiên đăng nhập, chỉ khôi phục bản sao trong môi trường được bảo vệ.

Sao lưu dùng SQLite backup API để lấy ảnh nhất quán, kể cả dữ liệu WAL đã commit,
kiểm tra toàn vẹn rồi mã hóa AES-256-GCM. Tệp đầu ra được tạo độc quyền, không ghi
đè; quyền 0600 trên POSIX. Windows cần giới hạn quyền thư mục bằng quyền tài khoản
Windows. Bản này xử lý trong bộ nhớ, giới hạn database 512 MiB.

Khôi phục vào đường dẫn mới, sau đó kiểm tra trước khi chuyển ứng dụng sang đó:

```sh
python scripts/backup_local.py restore --archive /noi-sao-luu/school-2026-10-15.tuhocbackup --database /noi-khoi-phuc/khohoc-restored.db --key-file /duong-dan-rieng/school.backup-key
```

Tệp sai khóa, bị sửa, sai định dạng hoặc database không toàn vẹn bị từ chối.
Không khôi phục đè lên database đang chạy. Dừng backend trước khi đổi đường dẫn
cấu hình sang bản khôi phục; giữ bản cũ để quay lại. Khởi động bằng đúng phiên bản
mã nguồn tương thích, thử đăng nhập và đối chiếu nhóm, số bài, điểm gần nhất trước
khi mở lại cho học viên. Khôi phục không tự nâng cấp schema.

Đề xuất vận hành pilot: sao lưu hàng ngày và trước nâng cấp; giữ bản hàng ngày
7 ngày, bản hàng tuần 4 tuần, một bản mã hóa ngoài máy chủ; thử khôi phục hàng
tháng. Đây là hướng dẫn, chưa có lịch tự động, cơ chế xóa theo thời hạn, kho khóa
hay bản sao ngoài máy chủ được triển khai. Cần áp dụng chính sách xóa tài khoản
cho cả vòng đời bản sao, tránh đưa dữ liệu đã xóa trở lại sau khôi phục.

Bước tiếp theo: adapter PostgreSQL và migration; HTTPS, kiểm soát origin/cookie,
giới hạn đăng nhập dùng chung; triển khai pilot; sao lưu PostgreSQL được kiểm thử;
kiểm thử quyền giữa tài khoản và thiết bị thật. Chế độ production vẫn bị khóa.
