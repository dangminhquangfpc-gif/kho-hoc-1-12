# Vận hành PostgreSQL: sao lưu, khôi phục và giám sát

Phần này nối tiếp `SHARED_SERVER.md`, dùng cho máy chủ Linux chạy pilot HTTPS.
Công cụ và cấu hình lịch đã có trong repo; chưa cài/kích hoạt lịch trên máy chủ
Internet của người dùng. Không cần bản ZIP Windows mới cho thay đổi vận hành này.

## Chuẩn bị

Ví dụ đặt repo ở `/opt/tu-hoc-111`. Docker Compose stack shared phải được cấu hình
và chạy theo hướng dẫn trước; không dùng database development cho học viên thật.
Công cụ dùng Docker socket local, không dựa vào Docker context từ xa. Quyền truy
cập Docker tương đương quyền quản trị máy chủ; không cấp quyền này cho học viên.

```sh
cd /opt/tu-hoc-111
python3 -m venv .server-venv
.server-venv/bin/python -m pip install -r services/api/requirements.lock.txt
sudo install -d -m 0700 /etc/tu-hoc-111 /var/backups/tu-hoc-111
sudo .server-venv/bin/python scripts/backup_postgres.py keygen --key-file /etc/tu-hoc-111/postgres.backup-key
sudo .server-venv/bin/python scripts/backup_postgres.py backup --key-file /etc/tu-hoc-111/postgres.backup-key --directory /var/backups/tu-hoc-111 --retention-days 30
```

Tạo khóa một lần; lệnh từ chối ghi đè khóa cũ. Lưu thêm một bản khóa ở nơi riêng
được bảo vệ, tách khỏi nơi chứa archive. Mất khóa thì không giải mã được. Không
đưa khóa, database, tệp trạng thái hoặc archive lên GitHub/chat.

Nguồn sao lưu mặc định lấy từ `KHOHOC_DATABASE_URL` của service API trong Compose,
không gắn cứng tên `tuhoc`. Khi chuyển API sang database khôi phục, công cụ cũng
đọc lại đúng nguồn đó. `--database` chỉ dành cho trường hợp bảo trì có chủ đích;
nếu sao lưu nhiều database, dùng các thư mục riêng để trạng thái giám sát rõ ràng.
Các mật khẩu database vẫn ở secret mount hiện có, không xuất hiện trong tham số
lệnh sao lưu hoặc log công cụ.

## Archive và chính sách lưu

- `pg_dump` custom-format lấy snapshot nhất quán; giữ tài khoản, nhóm, đề, lịch sử,
  kết quả, nội dung và metadata schema. Không sao lưu PDF/file ngoài database,
  cấu hình deployment, khóa ký ứng dụng hoặc chính khóa mã hóa.
- Dump được mã hóa AES-256-GCM theo từng khối; header, SHA-256 và toàn bộ nội dung
  được xác thực. Kiểm tra giải mã/checksum trước khi công bố archive. File cuối
  được tạo nguyên tử, không ghi đè; thư mục 0700, file/khóa 0600 (khóa 0400 cũng được).
- Giới hạn dump 512 MiB, timeout từng lệnh 5 phút. Bộ nhớ không tăng theo kích thước
  archive; cần đủ đĩa tạm cho dump và bản kiểm tra. Thư mục tạm chỉ chủ tiến trình
  đọc được; phân vùng máy chủ vẫn cần được bảo vệ.
- Có khóa chống hai job chạy chồng. Thất bại không đánh dấu sao lưu thành công,
  không dọn archive cũ. Trạng thái ghi riêng tại `status.json`, không chứa học viên.
- Không có `--retention-days` thì không xóa archive. Khi đặt 30, chỉ xóa archive
  hợp lệ của cùng database/khóa và cũ hơn 30 ngày, sau một lần sao lưu thành công;
  luôn giữ ít nhất hai bản hợp lệ, nên hai bản cuối có thể vượt mốc 30 ngày.
  File lạ, symlink, archive hỏng hoặc dùng khóa khác không bị công cụ tự xóa.

Bản sao cùng máy không bảo vệ khỏi mất cả máy chủ. Cần đưa archive đã mã hóa sang
nơi lưu tách máy bằng kênh được quản trị cho phép; chưa có kho offsite hay tài
khoản nhà cung cấp được cấu hình ở đây. Khi đổi khóa, giữ khóa cũ trong thời gian
còn archive cần đọc; retention không xóa archive mà khóa hiện tại không đọc được.

## Khôi phục an toàn để kiểm tra

Chọn một tên mới bắt đầu bằng `recovery_`. Công cụ không có tùy chọn `--clean`,
không drop database và từ chối nếu tên đích đã tồn tại. Sai khóa, tệp bị sửa hoặc
định dạng không hợp lệ bị chặn trước khi tạo database. Mỗi restore chạy trong một
transaction; nếu có lỗi sau bước createdb, database mới có thể còn lại để quản
trị kiểm tra, nhưng database đang dùng không bị thay đổi.

```sh
sudo .server-venv/bin/python scripts/backup_postgres.py restore --key-file /etc/tu-hoc-111/postgres.backup-key --archive /var/backups/tu-hoc-111/TEN-ARCHIVE.tuhocpg --database recovery_20261015
```

Sau khôi phục thành công, công cụ kiểm tra schema và xóa toàn bộ session đăng
nhập/bộ đếm rate limit trong database mới. Người dùng phải đăng nhập lại. Trước
khi đổi API, đối chiếu nhóm, học viên và điểm gần nhất, kiểm tra yêu cầu xóa tài
khoản xảy ra sau thời điểm snapshot. Chưa tự đối soát nhật ký xóa ngoài bản sao;
không mở ngay một snapshot cũ cho học viên vì có thể đưa dữ liệu đã xóa trở lại.

Nếu quyết định chuyển pilot sang bản đã kiểm tra, cấp quyền role API cho database
mới bằng lệnh bảo trì (ví dụ):

```sh
docker compose -f deploy/shared/compose.yaml run --rm -e KHOHOC_DATABASE_URL=postgresql+psycopg://tuhoc_owner@db:5432/recovery_20261015 maintenance python -m khohoc.server_admin grant-runtime --role tuhoc_app
```

Đổi đường dẫn database trong URL của service API trong Compose sang tên mới;
không đổi mật khẩu/role thành owner. Chạy lại `docker compose ... up -d api`, thử
đăng nhập và đọc kết quả trên hai thiết bị. Job sao lưu mặc định đọc cấu hình API
mới. Giữ database cũ để quay lại; không chạy `down -v` hoặc tự xóa database cũ.
Thử khôi phục vào database cách ly hàng tháng và trước nâng cấp lớn.

## Kích hoạt lịch trên máy chủ của bạn

Chỉ thực hiện sau khi các đường dẫn, backup thủ công, HTTPS và khôi phục đã được
kiểm tra trên máy chủ đó. Các lệnh dưới đây không được tự chạy trong cloud phát
triển. Thay đường dẫn unit nếu repo/venv/thư mục dữ liệu khác ví dụ.

```sh
sudo install -m 0644 deploy/shared/systemd/tuhoc-backup.service deploy/shared/systemd/tuhoc-backup.timer deploy/shared/systemd/tuhoc-monitor.service deploy/shared/systemd/tuhoc-monitor.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start tuhoc-backup.service
sudo systemctl enable --now tuhoc-backup.timer tuhoc-monitor.timer
systemctl list-timers tuhoc-backup.timer tuhoc-monitor.timer
```

Backup hàng ngày lúc 02:00 UTC (09:00 Việt Nam), trễ ngẫu nhiên tối đa 15 phút;
chạy bù khi máy bật lại. Monitor chạy khoảng mỗi 5 phút. Đây là unit oneshot;
chúng không tạo endpoint Internet hoặc thay thế giám sát của nhà cung cấp.

## Đọc trạng thái và phát hiện sự cố

`/api/health` kiểm tra kết nối DB; `/api/ready` kiểm tra thêm phiên bản schema.
Schema sai hoặc DB mất kết nối trả 503 với nội dung tối giản, không đưa chi tiết
kết nối ra ngoài. API giới hạn thời gian kết nối/câu lệnh PostgreSQL và pool;
probe vẫn đọc được trạng thái khi nơi lưu bộ đếm rate limit không hoạt động.
HTTPS và kiểm tra Host vẫn áp dụng, không cho giả header từ client để bỏ TLS.

```sh
sudo .server-venv/bin/python scripts/backup_postgres.py status --directory /var/backups/tu-hoc-111
sudo .server-venv/bin/python scripts/monitor_shared.py --url https://TEN-MIEN-THAT/api/ready --backup-directory /var/backups/tu-hoc-111
journalctl -u tuhoc-backup.service -u tuhoc-monitor.service --since today
```

Mã thoát 0 chỉ khi kiểm tra thành công. Monitor yêu cầu HTTPS/chứng chỉ hợp lệ,
không theo redirect, không coi backend development là sẵn sàng. Backup thiếu,
bị sửa, lần chạy cuối thất bại hoặc quá 26 giờ đều trả `attention`/mã 1. JSON log
chỉ có trạng thái; chưa có email/SMS/chat cảnh báo được kết nối. Có thể bổ sung
cảnh báo qua hệ thống giám sát của chủ máy chủ sau khi được cấu hình.

Đây vẫn là pilot: còn offsite backup, đối soát dữ liệu đã xóa khi phục hồi, quy
trình xác minh giáo viên, quyền riêng tư trẻ em/thẩm định nội dung, kiểm thử thiết
bị và tài khoản/ký cửa hàng. `production` và store preflight vẫn chưa mở khóa.
