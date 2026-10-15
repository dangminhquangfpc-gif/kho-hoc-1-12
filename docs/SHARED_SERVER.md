# PostgreSQL, HTTPS và đồng bộ tài khoản

Đây là cấu hình pilot có kiểm soát, `KHOHOC_MODE=shared`; không tự triển khai
lên Internet và không mở khóa bản phát hành cửa hàng `production`. Cần máy chủ
Linux chạy Docker Compose, tên miền trỏ về máy chủ và cổng 80/443 truy cập được.
Không mở cổng PostgreSQL hoặc API ra Internet.

## Những phần đã có

- PostgreSQL 17 qua psycopg, connection pool kiểm tra kết nối; migration offline
  có khóa PostgreSQL và phiên bản schema. Backend shared chỉ kiểm tra schema,
  không tự tạo bảng khi khởi động. Phiên bản hiện tại là schema 2, có migration
  bổ sung từ baseline 1 cho phản hồi nội dung; chưa có công cụ nâng/hạ cấp mọi
  schema tương lai. Xem CONTENT_REPORTS.md trước khi nâng bản đang có dữ liệu.
- Tài khoản database riêng cho API: DML và sequence; không có quyền tạo bảng,
  đổi schema hoặc quản trị role. Tài khoản owner chỉ dùng bảo trì.
- HTTPS bắt buộc, kiểm tra Host, Origin và Sec-Fetch-Site; cookie HttpOnly,
  Secure, SameSite Strict; HSTS; ẩn docs và toàn bộ API admin cục bộ.
- Giới hạn dùng chung giữa các worker: 300 yêu cầu/phút/IP, 60 lần đăng nhập/đăng
  ký/15 phút/IP và 10 lần/15 phút/tên tài khoản. Đây là cửa sổ cố định, tính cả
  lần thành công; máy chung NAT cần theo dõi điều chỉnh. Khóa bộ đếm được băm,
  không lưu mật khẩu. Cơ chế cũ trong bộ nhớ vẫn là lớp giới hạn bổ sung.
- Session opaque lưu băm trong PostgreSQL, hết hạn 8 giờ; đăng nhập trên nhiều
  thiết bị. Đổi/đặt lại mật khẩu và xóa tài khoản thu hồi phiên theo quy tắc hiện có.
- Kết quả, nhóm, đề giáo viên và bản nháp dùng chung qua cùng backend. Tài khoản
  chỉ mở được bài thuộc mình; học sinh vẫn không được tạo đề.

## Chuẩn bị trên máy chủ

Từ thư mục repo; thay tên miền/email bằng thông tin thật, không dùng ví dụ để
xin chứng chỉ. Cấu hình mạng Docker mặc định `172.29.111.0/24`; nếu mạng này đã
được dùng, đổi cả subnet, IP gateway/API và `--forwarded-allow-ips` trong Dockerfile.
Chỉ gateway có IP được tin mới được chuyển tiếp HTTPS/IP người dùng; không dùng `*`.

```sh
python scripts/prepare_shared.py --domain ten-mien-cua-ban --email email-cua-ban
```

Lệnh sinh hai mật khẩu ngẫu nhiên tại `deploy/shared/secrets/`, không in ra màn
hình; không ghi đè cấu hình cũ. Thư mục secrets 0700 bảo vệ trên host; tệp 0444 để
API không chạy root đọc được qua secret mount. Không commit/copy secret vào image.
`.env`, secrets và staging private đều đã được gitignore.

Build web và image:

```sh
cd apps/mobile
flutter pub get --enforce-lockfile
flutter build web --pwa-strategy=none --no-web-resources-cdn --no-wasm-dry-run --dart-define=API_BASE_URL=/api
cd ../..
docker compose -f deploy/shared/compose.yaml build api
docker compose -f deploy/shared/compose.yaml up -d --wait db
docker compose -f deploy/shared/compose.yaml run --rm maintenance python -m khohoc.server_admin migrate
```

Trong cloud có proxy CA, build bằng `docker build --secret
id=proxy_ca,src=/etc/ssl/certs/ca-certificates.crt -f deploy/shared/api.Dockerfile
-t tu-hoc-111-api:shared .`; CA chỉ được mount lúc cài thư viện, không lưu vào image.

## Chuyển dữ liệu hiện có hoặc tạo hệ thống mới

Chọn một trong hai: database đích phải trống trước khi import. Không bootstrap
manager trước import, không gộp tùy tiện nhiều database Windows khác nhau.

Để chuyển bản local: sao lưu trước bằng `docs/BACKUP_RECOVERY.md`, chép database
qua kênh bảo mật vào `deploy/shared/private/import.db` và cho tài khoản chạy
maintenance đọc được. Dùng bản SQLite đã kiểm tra; giữ PDF/tài nguyên gốc riêng.

```sh
docker compose -f deploy/shared/compose.yaml run --rm --user "$(id -u):$(id -g)" maintenance python -m khohoc.server_admin import-sqlite --source /maintenance/import.db
```

Import lấy snapshot SQLite nhất quán, chép dữ liệu trong một transaction, từ
chối nếu đích có dữ liệu; giữ tài khoản, nhóm, đề, bài làm, điểm và revision nội dung.
Không chuyển session/bộ đếm đăng nhập: mọi thiết bị phải đăng nhập lại. Sau khi
đối chiếu dữ liệu, xóa tệp staging theo chính sách bảo vệ dữ liệu của bạn.

Với hệ thống mới hoàn toàn, tạo manager offline thay cho bước import:

```sh
docker compose -f deploy/shared/compose.yaml run --rm --user "$(id -u):$(id -g)" maintenance python -m khohoc.server_admin bootstrap-manager --credentials-file /maintenance/TAI-KHOAN-QUAN-LY.txt
```

Không có seeding tự động hoặc tự duyệt câu hỏi trên shared. Hệ thống mới cần
nhập nội dung đã thẩm định qua quy trình bảo trì trước khi cấp cho học viên.
Cấp quyền API rồi khởi động:

```sh
docker compose -f deploy/shared/compose.yaml run --rm maintenance python -m khohoc.server_admin grant-runtime --role tuhoc_app
docker compose -f deploy/shared/compose.yaml up -d api gateway
```

Caddy xin/gia hạn chứng chỉ HTTPS và lưu PostgreSQL/chứng chỉ trong volume riêng.
API có filesystem chỉ đọc, bỏ Linux capabilities và chạy UID 10001. Chỉ DB
và API chung mạng database nội bộ. Không chạy `docker compose down -v` khi có dữ liệu.

## Dùng trên nhiều thiết bị

Web mở cùng tên miền, API dưới `/api`. Điện thoại đặt backend
`https://ten-mien-cua-ban/api`; bản native phát hành không gửi mật khẩu qua HTTP.
Mỗi học viên đăng nhập cùng tài khoản trên các thiết bị của mình.

Bài trả lời được giữ trên thiết bị ngay và tự gửi bản nháp sau khoảng 0,9 giây
khi ngừng sửa. Có nút **Đồng bộ** và trạng thái rõ ràng; mất mạng vẫn giữ bản local.
Trước khi đổi thiết bị, đợi thông báo đã đồng bộ. Ở thiết bị kia: **Cá nhân → Tài
khoản → Bài đang làm trên các thiết bị → Đồng bộ lại → chọn bài**.

Máy chủ kiểm tra revision khi lưu và khi nộp bằng client mới: hai thiết bị cùng
sửa thì bản cũ nhận 409. App giữ bản local, yêu cầu mở lại bản máy chủ hoặc xem
kết quả đã nộp; không tự gộp/ghi đè câu trả lời. Mở bản máy chủ có xác nhận trước
khi thay bản local. Tài khoản hiển thị 100 bài gần nhất chưa nộp/còn hạn và 500 kết
quả gần nhất. Bài đang làm tuân theo thời hạn nộp hiện có (24 giờ từ khi tạo bài, đồng nhất với lúc nộp).
Đánh dấu câu, yêu thích tài liệu và tùy chọn thiết bị chưa đồng bộ.

## Kiểm tra và vận hành

```sh
PYTHONPATH=services/api pytest -q services/api/tests
python scripts/test_shared_postgres.py
```

Script PostgreSQL tạo container tạm có mật khẩu ngẫu nhiên, chỉ publish loopback,
chạy các kiểm thử shared thật rồi xóa container. Không dùng database học viên.
CI cũng chạy script này. Kiểm tra `/api/health`, đăng nhập hai thiết bị, bài đang
làm, điểm, phân quyền và khả năng giữ dữ liệu sau restart trước khi mở pilot.

Volume không phải bản sao lưu. Công cụ mã hóa SQLite không sao lưu PostgreSQL.
Đã có công cụ `pg_dump` mã hóa, khôi phục cách ly, kiểm tra readiness và unit
lịch backup/monitor; xem [vận hành PostgreSQL](POSTGRES_OPERATIONS.md). Chưa cài
lịch trên máy chủ Internet, cấu hình nơi lưu tách máy hoặc đối soát xóa sau phục hồi. Quyền theo học viên hiện do ứng dụng kiểm tra,
không khẳng định database có RLS cho các bảng SQLAlchemy này. Còn cần kiểm duyệt
nội dung, quy trình xác minh giáo viên, quyền riêng tư trẻ em và thử thiết bị thật
trước phát hành rộng rãi/CH Play/App Store.

Có thể kiểm thử nguyên stack trên máy phát triển, sau khi build web/image:

```sh
PYTHONPATH=services/api python scripts/smoke_shared_stack.py
```

Script tạo Compose project/secret/database tạm, chứng chỉ CA local riêng, chỉ
publish HTTPS lên loopback, xác minh CA bằng curl (không bỏ kiểm tra TLS), rồi
xóa đúng project/volume tạm của nó. Không cấu hình DNS hoặc xin chứng chỉ thật.
Trên cloud đặt `BUILDX_CONFIG` vào thư mục cache ghi được nếu thư mục Docker mặc
định chỉ đọc; giữ nguyên Docker config/proxy/credentials của môi trường.

Với PostgreSQL của nhà cung cấp nằm ngoài mạng Docker riêng, cấu hình URL kết
nối có `sslmode=verify-full` và CA tương ứng theo nhà cung cấp. Compose hiện tại
để DB trong mạng nội bộ không publish port; không dùng cấu hình đó để kết nối
PostgreSQL công khai qua đường truyền không mã hóa.
