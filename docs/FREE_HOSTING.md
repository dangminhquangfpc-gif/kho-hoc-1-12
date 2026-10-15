# Máy chủ dùng chung thử miễn phí: Render và Neon

Cấu hình này phục vụ thử nghiệm có kiểm soát của **Tự học 111**, không phải xác
nhận đã triển khai hoặc đủ điều kiện phát hành rộng rãi. Người sở hữu app cần
tự tạo tài khoản Render và Neon; không gửi mật khẩu, chuỗi kết nối hoặc khóa
dịch vụ vào chat. Mã nguồn không tự đăng ký, nâng cấp gói hoặc thêm thẻ thanh toán.

## Cách hoạt động

- **Render Free Web Service** chạy API, cấp HTTPS và tên
  `https://<tên-thực-tế>.onrender.com`. Không cần mua tên miền.
- **Neon Free PostgreSQL 17**, vùng AWS Singapore (`aws-ap-southeast-1`), giữ
  tài khoản, nhóm, đề, bản nháp và kết quả giữa các lần Render khởi động lại.
- API dưới `/api`, ví dụ `https://<tên-thực-tế>.onrender.com/api`. Đây là địa chỉ
  điền trong **Cá nhân → Địa chỉ máy chủ** của app sau khi kiểm tra readiness.
- Bài đã làm ở chế độ **Học trên thiết bị** vẫn thuộc lịch sử ngoại tuyến; không
  tự nhập điểm đó thành kết quả học viên trên máy chủ. Đăng nhập máy chủ rồi làm
  bài mới để thử giám sát và đồng bộ giữa hai thiết bị.
- Trợ lý AI trả phí tiếp tục được tắt. Không cần khóa AI cho cấu hình này.

## Chuẩn bị tài khoản miễn phí

1. Đăng ký [Neon](https://neon.com/signup), giữ gói **Free**, tạo project
   PostgreSQL 17 tại **AWS Singapore**. Không chọn vùng Azure cũ hoặc tùy chọn
   nâng cấp trả phí. Chọn database dành riêng cho đợt thử app.
2. Đăng ký [Render](https://dashboard.render.com/register), giữ workspace/gói
   miễn phí. Khi liên kết GitHub, chỉ cấp quyền repository
   `dangminhquangfpc-gif/kho-hoc-1-12` cần dùng.
3. Chuẩn bị database bằng công cụ bảo trì bên dưới **trước khi** tạo web service.
   Không dùng Neon SQL Editor để nhập dữ liệu cá nhân có sẵn hoặc cấp owner URL
   cho Render API.

Neon công bố Free không phải trial và không cần thẻ. Render có thể yêu cầu bước
xác minh tài khoản theo chính sách riêng; nếu giao diện yêu cầu thanh toán hoặc
đổi sang gói trả phí thì dừng ở bước đó, không xác nhận khoản phí. Chỉ chọn
**Free** cho web service và database.

## Chuẩn bị schema, nội dung và tài khoản quản lý

Công cụ [prepare_free_server.py](../scripts/prepare_free_server.py) chạy trên máy
tính của chủ app. Trên Windows:

1. Tải [bộ chuẩn bị máy chủ .20](https://github.com/dangminhquangfpc-gif/kho-hoc-1-12/releases/download/demo-tu-hoc-111-2026-10-15-v20/tu-hoc-111-server-setup.zip),
   **giải nén toàn bộ** ra một thư mục, rồi mở `DOC-TRUOC.txt`. Không chạy trực
   tiếp tệp `.bat` trong cửa sổ xem ZIP.
2. Cài [Python 3.12](https://www.python.org/downloads/) và chọn **Add Python to
   PATH**. Các launcher cài thư viện đã khóa phiên bản vào môi trường riêng.
3. Tại Neon, mở **Connect**, chọn database mới và role owner mặc định
   `neondb_owner` (hoặc role owner đúng database bạn đã đặt tên), **tắt Connection
   pooling**, sao chép chuỗi PostgreSQL direct. Không sao chép lệnh `psql` bao
   bên ngoài chuỗi URL.
4. Mở **`1-KIEM-TRA.bat`**, dán URL khi công cụ hỏi nhập ẩn và nhấn Enter. Bước này
   chỉ đọc: kiểm tra kết nối, quyền owner, database trống và gói nội dung; không
   tạo bảng, role, manager hoặc sửa dữ liệu PostgreSQL. Cửa sổ dừng lại để bạn đọc
   kết quả. URL có `sslmode=require` thông thường từ Neon sẽ được công cụ đổi
   thành `verify-full` với CA tin cậy khi kết nối.
5. Chỉ sau khi bước kiểm tra đạt, mở **`2-KHOI-TAO.bat`**, nhập lại URL riêng tư
   để **khởi tạo database mới**. Đây là bước ghi schema, nội dung, manager và
   runtime role. Công cụ từ chối đích không trống, role `tuhoc_app` đã có hoặc
   thư mục cấu hình cũ; không đặt lại mật khẩu hay ghi đè hệ thống đang dùng.
6. Sau khi thành công, giữ riêng hai tệp trong thư mục đã giải nén:
   `state/free-server-private/manager-credentials.txt` là tài khoản quản lý để
   đăng nhập app; `state/free-server-private/render-private.env` chứa URL runtime
   để cấu hình Render. Đổi mật khẩu quản lý ở lần đăng nhập đầu. Không gửi thư
   mục `state`, hai tệp này hoặc URL owner lên Git, chat, APK hay cho học viên.

Gói .20 chứa mã công cụ và nội dung công khai của app: 7.886 câu, 1.461 đề,
2.866 mục tài liệu/nguồn. Gói không có tài khoản, session, bài làm, kết quả học
viên hoặc khóa ký. Nó không thay cho việc thẩm định chuyên môn toàn bộ nội dung.

Không đưa chuỗi owner vào biến môi trường của web service. Owner chỉ dùng ở
công cụ bảo trì trên máy của bạn; runtime URL bên dưới là role hạn chế quyền.

Quy trình bảo trì cần thực hiện theo thứ tự:

1. Kết nối **direct**, không bật Connection pooling, bằng owner của database mới.
2. Chạy migration rõ ràng. Chỉ nhập nội dung app đã được duyệt và kiểm tra; không
   tự duyệt toàn bộ PDF trên Internet hoặc chuyển database học viên tùy ý.
3. Tạo tài khoản quản lý, lưu thông tin đăng nhập vào tệp riêng trên máy chủ app.
4. Tạo role đăng nhập **`tuhoc_app` bằng SQL**, thu hồi quyền tạo schema/bảng mặc
   định của `PUBLIC`, rồi cấp quyền DML cần thiết. Xác minh runtime không thể
   tạo bảng hoặc đổi role.
5. Lưu chuỗi kết nối runtime để nhập riêng vào Render. Không cấp owner URL cho
   runtime. Không tạo runtime role bằng nút Add role của Neon Console/API/CLI:
   các đường đó tự cấp quyền quản trị `neon_superuser`.

API shared chỉ xác minh schema đã có khi khởi động. Nó không tự migrate, tạo
manager hoặc nạp fixture khi deploy/restart. Render Free không có shell/SSH,
one-off job hay pre-deploy command nên các bước owner này phải chạy từ máy tính
bảo trì riêng.

Chuỗi kết nối runtime có dạng sau; giá trị trong ngoặc phải thay tại giao diện
cấu hình riêng, không dùng ví dụ làm thông tin thật:

```text
postgresql+psycopg://tuhoc_app:<mật-khẩu>@<endpoint-direct>.ap-southeast-1.aws.neon.tech/<database>?sslmode=verify-full
```

Các ký tự đặc biệt trong username/password phải được mã hóa đúng trong URL.
Công cụ chuẩn bị chịu trách nhiệm tạo URL hợp lệ, không ghép mật khẩu bằng tay.
Kết nối qua Internet bắt buộc xác minh tên máy chủ và CA; không đổi sang
`sslmode=require`, không bỏ kiểm tra TLS. Blueprint dùng system CA tại
`/etc/ssl/certs/ca-certificates.crt`. Pilot hiện dùng **direct endpoint**, không
có `-pooler` trong hostname: code có thiết lập timeout theo phiên; PgBouncer
transaction mode cần kiểm thử tương thích riêng trước khi đổi sang pooled URL.

## Tạo Render Web Service

Blueprint [render.yaml](../render.yaml) trỏ nhánh
**`feature/shared-server-launch-20261015`**, không trỏ `main` cũ. Tên service gợi ý
`tu-hoc-111-api`; Render sẽ cấp hostname thực tế có thể khác hoặc thêm hậu tố.

Từ Render Dashboard, tạo **Blueprint** từ repository trên và chọn đúng nhánh.
Nếu dùng New → Web Service để nhập thủ công, dùng đúng các giá trị sau:

| Trường | Giá trị |
|---|---|
| Branch | `feature/shared-server-launch-20261015` |
| Runtime | Docker |
| Dockerfile | `./deploy/shared/api.Dockerfile` |
| Docker build context | `.` (gốc repository) |
| Docker command | `python -m khohoc.render_server` |
| Region | Singapore |
| Compute plan | Free |
| Health check | `/api/ready` |
| Auto deploy | Off |

Các biến môi trường:

| Tên | Giá trị |
|---|---|
| `KHOHOC_MODE` | `shared` |
| `KHOHOC_DATABASE_URL` | Chuỗi runtime `tuhoc_app` do công cụ bảo trì tạo, nhập riêng tại Render |
| `PGSSLROOTCERT` | `/etc/ssl/certs/ca-certificates.crt` |

Blueprint dùng `sync: false` để Render hỏi chuỗi kết nối trong giao diện ban đầu;
nó không chứa credential trong mã nguồn. Những lần chỉnh Blueprint sau không tự
cập nhật giá trị secret này: phải sửa riêng Environment của service khi xoay mật
khẩu. Không thêm `KHOHOC_ADMIN_TOKEN`, owner URL hoặc tệp tài khoản manager.

Để nhập đúng giá trị: mở riêng `state/free-server-private/render-private.env`
trên máy Windows. Trong Render **Environment**, đặt Key là
**`KHOHOC_DATABASE_URL`**, còn Value là **chỉ phần sau dấu `=`** của dòng
`KHOHOC_DATABASE_URL=...`. Không dán cả tên biến, dấu `=` đầu dòng, dấu ngoặc kép
hoặc URL owner vào Value. Chuỗi này là mật khẩu database runtime; không gửi ảnh
chụp màn hình chứa Value.

Render tự cấp `RENDER_EXTERNAL_URL`, `RENDER_EXTERNAL_HOSTNAME`, `RENDER_SERVICE_ID`,
`RENDER_SERVICE_TYPE` và `PORT`. Entry point tự dùng HTTPS origin này cho Host và
CORS; không nhập tên miền ví dụ vào public origin. Mọi đường ngoài `/api/` trả
404; không có web demo, Swagger hoặc admin công khai trong service này.

Chờ deploy và health check đạt, mở
`https://<hostname-thật>.onrender.com/api/ready`: chỉ tiếp tục khi nhận HTTP 200
và `{"status":"ok","mode":"shared"}`. Lưu URL API dưới `/api` vào app; không
điền thêm `/ready`. Khi service đang ngủ, lần gọi đầu có thể chưa trả JSON ngay;
chờ khoảng một phút rồi thử lại, không tự tạo thêm tài khoản hoặc nộp trùng bài.

## Kiểm tra trên hai thiết bị

1. Trên điện thoại A, chọn **Học với máy chủ**, nhập URL HTTPS và đăng nhập tài
   khoản quản lý từ tệp bảo trì riêng. Tạo nhóm học viên.
2. Học viên đăng ký role học sinh hoặc nhận tài khoản do giáo viên/quản lý cấp.
   Học sinh không có quyền tạo đề. Giáo viên dùng nhóm và mã tham gia để quản lý
   đúng học viên; không mặc nhiên đọc kết quả mọi người đã đăng ký hệ thống.
3. Với cùng tài khoản học sinh trên A và thiết bị B, bắt đầu một đề, trả lời vài
   câu, đợi trạng thái đã đồng bộ, rồi mở **Bài đang làm trên các thiết bị** ở B.
4. Nộp bài tại B; đối chiếu điểm/lịch sử tại A và kết quả học viên trong nhóm của
   giáo viên/quản lý. Tài khoản khác không được đọc bài làm không thuộc mình.
5. Thực hiện Manual deploy/restart trên Render; đăng nhập lại khi cần và kiểm
   tra nhóm, bài và kết quả còn trong PostgreSQL. Thử tắt mạng để xác nhận app
   giữ bản nháp và thông báo rõ trạng thái đồng bộ.

Chưa mời lớp học thật trước khi thử luồng này, kiểm tra backup/khôi phục và bổ
sung chính sách quyền riêng tư liên quan trẻ em. Bản pilot không tự xác minh
tư cách giáo viên và không thay cho chấm tự luận của giáo viên.

## Giới hạn miễn phí và dữ liệu

Theo tài liệu chính thức kiểm tra ngày **15/10/2026**:

- Render Free Web Service có **750 giờ chạy/workspace/tháng**, **0,1 CPU/512 MB
  RAM**; nghỉ sau **15 phút** không nhận traffic. Cold start thường khoảng một
  phút. Filesystem bị mất khi restart/redeploy/ngủ; tuyệt đối không dùng SQLite,
  tệp tài khoản, file upload hoặc backup local làm dữ liệu lâu dài.
- Hết giờ miễn phí bị đình chỉ đến tháng kế tiếp. Băng thông/build có hạn mức
  workspace; nếu không có phương thức thanh toán, quá hạn mức có thể đình chỉ
  service hoặc build. Nếu thêm phương thức thanh toán, phần dùng vượt có thể
  phát sinh phí. Render cũng có thể đình chỉ lưu lượng outbound bất thường,
  kể cả truy cập database bên ngoài. Không dùng dịch vụ ping liên tục để giữ
  máy chủ thức hoặc che giới hạn gói.
- **Không tạo Render Free Postgres** cho pilot này: database đó hết hạn sau
  **30 ngày**, và bị xóa sau thêm **14 ngày** nếu không nâng cấp.
- Neon Free gồm **1 GB Postgres/project**, tối đa **20 GB cả tài khoản**,
  **100 CU-hour/project/tháng** và **5 GB truyền mạng/project/tháng**; compute nghỉ
  sau **5 phút**. Hết compute/network bị tạm dừng; vượt dung lượng làm thao tác
  tăng dung lượng thất bại. Các hạn mức này có thể thay đổi; kiểm tra Dashboard.
  AWS Singapore là vùng được chọn. Vùng Azure cũ đã ngừng tạo project mới và có
  chính sách xóa project Free không hoạt động; không dùng chúng.
- Đây là pilot nhỏ, có thể gián đoạn khi hết quota; không có cam kết uptime.
  Dữ liệu Neon bền qua restart API nhưng không thay thế backup riêng. Free có
  cửa sổ phục hồi ngắn; dùng quy trình [backup PostgreSQL](POSTGRES_OPERATIONS.md)
  với direct endpoint, nơi lưu tách máy và kiểm thử khôi phục. Đăng nhập, kết quả
  và nhóm không được lưu trong volume hoặc cache Render.

## Ranh giới tin cậy của ingress

Render nhận HTTPS, kết thúc TLS và chuyển tới cổng HTTP của container. Cổng này
không trực tiếp public; HTTP công khai được chuyển HTTPS trước. Entry point
`khohoc.render_server` chỉ được dùng theo hợp đồng triển khai Render này, không
dùng để biến một server HTTP bất kỳ thành HTTPS bằng cách đặt biến môi trường.

Uvicorn chạy **một worker**, tắt proxy headers và đặt forwarded allow list rỗng,
kể cả khi môi trường có `FORWARDED_ALLOW_IPS=*`. Adapter kiểm tra hostname Render,
bỏ `Forwarded`, `X-Forwarded-*` và các header IP phổ biến, giữ địa chỉ peer do
ASGI nhận. Scheme HTTPS dựa vào entry point đã xác minh cấu hình nhà cung cấp,
không dựa vào `X-Forwarded-Proto` do request gửi.

Vì không coi XFF là địa chỉ học viên đã xác thực, ngân sách request/auth theo
peer có thể dùng chung giữa nhiều học viên qua ingress. Ngân sách theo username
vẫn hoạt động. Pilot này **không khẳng định rate limit theo IP thật của từng
điện thoại**. Không bật `--forwarded-allow-ips '*'` để giải quyết lỗi HTTPS.
Compose/Caddy trên máy chủ riêng tiếp tục dùng đúng IP gateway cố định của nó.

## Nguồn chính thức

- [Render Free và hạn mức](https://render.com/docs/free)
- [Render Web Services, port và TLS ingress](https://render.com/docs/web-services)
- [Biến môi trường mặc định](https://render.com/docs/environment-variables)
- [Blueprint specification](https://render.com/docs/blueprint-spec)
- [Pre-deploy command chỉ có ở gói trả phí](https://render.com/docs/deploys#pre-deploy-command)
- [Render health checks](https://render.com/docs/health-checks)
- [Render regions](https://render.com/docs/regions)
- [Neon pricing](https://neon.com/pricing)
- [Neon plans và hạn mức](https://neon.com/docs/introduction/plans)
- [Neon roles và neon_superuser](https://neon.com/docs/manage/roles)
- [Neon database ownership](https://neon.com/docs/manage/databases)
- [Neon tạo role với cờ CREATEROLE trực tiếp](https://github.com/neondatabase/neon/blob/main/compute_tools/src/spec_apply.rs#L819)
- [Neon SSL verify-full và system CA](https://neon.com/docs/connect/connect-securely)
- [Neon direct và pooled connections](https://neon.com/docs/connect/connection-pooling)
- [Neon regions và Azure deprecation](https://neon.com/docs/introduction/regions)
