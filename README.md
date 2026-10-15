# Tự học 111


Monorepo MVP phát triển theo docs/PRODUCT_PLAN.md. Ứng dụng QuizApp Firebase cũ ở lib/ và android/ được giữ nguyên; ứng dụng mới ở apps/mobile/. Hướng dẫn cũ được giữ ở docs/LEGACY_QUIZAPP_README.md. Chưa hoàn thành tất cả tiêu chí MVP hoặc sẵn sàng Google Play.

Bản mã nguồn **2026.10.15.20** chuẩn bị máy chủ thử miễn phí với **Render Free
Singapore + Neon Free PostgreSQL tại AWS Singapore**. Bộ công cụ Windows giúp
kiểm tra database mới, khởi tạo schema/tài khoản quản lý, nhập nội dung công
khai và tạo role API `tuhoc_app` có quyền hạn chế. Chủ app cần tự tạo tài khoản
nhà cung cấp rồi chạy công cụ; hiện **chưa có backend HTTPS công khai hoạt động**.
Xem [thử hosting miễn phí](docs/FREE_HOSTING.md).

Phiên đăng nhập Android/iOS được lưu an toàn theo đúng backend để khôi phục sau
khi mở lại app: Android KeyStore bảo vệ khóa mã hóa, iOS dùng Keychain. Web tiếp
tục dùng cookie HttpOnly. Không lưu mật khẩu hoặc token thô trong SharedPreferences. Xem
[giới hạn và vòng đời phiên](docs/SECURE_SESSIONS.md).

Chế độ **Học trên thiết bị** từ .19 vẫn hoạt động khi chưa có backend:
đọc hướng dẫn, làm/nộp đề và xem lịch sử với dữ liệu đóng gói. Điểm tự luyện
lưu riêng trên thiết bị, không tự nhập thành kết quả tài khoản hoặc gửi cho
giáo viên. Ngân hàng hiện có 7.886 câu, 1.461 đề, 2.866 mục tài liệu/nguồn và
733 hướng dẫn Toán; chưa thẩm định hoặc phủ đầy đủ SGK mọi môn/lớp.
Xem [học ngoại tuyến](docs/OFFLINE_STUDY.md).

Không có trợ lý AI trả phí, không cần khóa API. OCR miễn phí vẫn dùng để nhận
chữ tiếng Việt/Anh, sửa và xác nhận trước khi chèn vào câu trả lời.
Xem [OCR](docs/OCR.md), [thử Android](docs/PHONE_TEST.md) và
[chuẩn bị Google Play](docs/PLAY_STORE_CHECKLIST.md).
Các mục ghi phiên bản cũ bên dưới là lịch sử phát triển.

Bản thử 2026.10.15.6: chọn nhiều chủ đề, bổ sung 731 câu Toán 5, tài khoản học viên và quản lý kết quả trên backend local. Hướng dẫn: [Tài khoản và quản lý học viên](docs/CLASSROOM_ACCOUNTS.md).

Bản thử 2026.10.15.7: trình bày lại lời giải và đáp số trong 75 tài liệu Toán 5; [phạm vi và cách kiểm chứng](docs/TEXTBOOK_LESSONS.md).

Bản thử 2026.10.15.8: thêm 267 hướng dẫn Toán lớp 1–4, 476 ví dụ và 952 bài tự luyện có lời giải. [Phạm vi và phần còn thiếu](docs/PRIMARY_MATH_GUIDES.md).

Bản thử 2026.10.15.9: thêm 391 hướng dẫn Toán 6–12 (230 bài đánh số cùng phần ôn tập/thực hành). [Phạm vi và giới hạn](docs/SECONDARY_MATH_GUIDES.md).

## Thành phần

- apps/mobile: Flutter, Riverpod, GoRouter, Dio; học trên thiết bị với dữ liệu đóng gói hoặc dùng API cho tài khoản/lớp học; chọn lớp/môn/đề, lưu bài/lịch sử, đọc hướng dẫn, nhận chữ từ ảnh và xem tiến độ.
- services/api: FastAPI, SQLAlchemy, deterministic grader; public DTO không chứa đáp án, guest attempt token, admin import/duyệt/xuất bản.
- apps/admin: Next.js/TypeScript, auth cục bộ server-side; JSON/CSV import, duyệt, sửa/khôi phục phiên bản và quản lý tài liệu.
- supabase/migrations: schema đích/RLS; chưa nối Supabase Auth/Storage production.
- data/: ngân hàng câu hỏi/đề/tài liệu tự biên soạn, mục lục và nguồn tham khảo;
  số lượng hiện hành ở đầu README, kèm PDF mẫu tiếng Việt được phép phân phối.

## Cài đặt trong cloud workspace

```bash
bash scripts/install_cloud.sh
```

Runtime cần Python 3.12, Node 24, Flutter 3.35.7/Dart 3.9.2, Temurin JDK 21.0.12.1. Dependencies khóa ở requirements.lock.txt, package-lock.json và mobile/pubspec.lock. scripts/install_cloud.sh không nâng cấp lockfile. Token dev chỉ được tạo ngoài checkout, không phải credential của dịch vụ bên ngoài.

## Chạy backend và seed

```bash
bash scripts/dev_api.sh
```

Trong terminal khác:

```bash
set -a
source /workspace/state/khohoc.env
set +a
/workspace/venvs/khohoc/bin/python scripts/seed_local.py
```

Lệnh này chỉ nhập nháp. Duyệt bằng admin. Để kiểm thử fixture trên máy development riêng có thể thêm --publish-fixtures; không dùng lựa chọn này thay thế chuyên gia kiểm duyệt cho production.

## Admin

```bash
set -a
source /workspace/state/khohoc.env
set +a
cd apps/admin
npm run dev
```

Đăng nhập bằng token được cấu hình cục bộ. Không chia sẻ hoặc đưa token vào Git. Next.js giữ token ở server. Không deploy dashboard cục bộ ra internet; Supabase Auth/JWT production còn thiếu.

## Mobile

```bash
export PUB_CACHE=/workspace/cache/pub XDG_CONFIG_HOME=/workspace/cache/config
export JAVA_HOME=/workspace/toolchains/jdk-21
export PATH=/workspace/toolchains/jdk-21/bin:/workspace/toolchains/flutter-3.35.7/bin:$PATH
cd apps/mobile
flutter run -d web-server --web-hostname=127.0.0.1 --web-port=8080 --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

Android emulator phát triển dùng --dart-define=API_BASE_URL=http://10.0.2.2:8000; phải cung cấp đường kết nối từ emulator tới backend. API cloud mặc định bind loopback; emulator/điện thoại khác máy không tự kết nối được. Thiết bị thật dùng chế độ Học trên thiết bị mà không cần backend. Đăng nhập, nhóm và đồng bộ qua Internet cần backend HTTPS dùng chung; dùng cấu hình pilot có kiểm soát trong [FREE_HOSTING.md](docs/FREE_HOSTING.md), không public backend development hoặc token quản trị.

```bash
flutter analyze
flutter test
flutter build web --pwa-strategy=none --no-wasm-dry-run --no-web-resources-cdn --dart-define=API_BASE_URL=/api
flutter build apk --debug
```

APK cần Android SDK/JDK và license. Hướng dẫn AAB/signing trong docs/PLAY_STORE_CHECKLIST.md; release chưa nghiệm thu.

## Database

API dùng chung hiện có schema PostgreSQL riêng với migration rõ ràng và role
runtime hạn chế. Công cụ .20 khởi tạo database Neon mới; không tự migrate hoặc
duyệt/nạp fixture khi web service khởi động. Chuyển nội dung công khai dùng
[content-only transfer](docs/CONTENT_TRANSFER.md), không sao chép database chứa
tài khoản/bài làm để đưa dữ liệu mẫu lên máy chủ.

Supabase: áp dụng SQL trong supabase/migrations bằng CLI hoặc SQL editor có quyền thích hợp. Không chạy bootstrap_local.sql trên hosted Supabase. RLS kiểm thử qua scripts/test_rls.sh trên container PostgreSQL local riêng. API local dùng bảng local_*; adapter sang schema đích, Auth và Storage chưa triển khai (docs/DATABASE_SCHEMA.md).

## Thử máy chủ miễn phí từ Windows

Bộ công cụ .20 cần Python 3.12 trên Windows và kết nối Internet để cài dependency
đã khóa; đây không phải bộ demo Windows tự chạy localhost. Giải nén bộ công cụ
rồi mở **`1-KIEM-TRA.bat`** để xem kế hoạch chỉ đọc. Chuỗi kết nối **direct owner**
của Neon được nhập ẩn trên máy bạn, không lưu vào gói, log, APK hoặc cấu hình
Render. Sau khi kiểm tra, **`2-KHOI-TAO.bat`** áp dụng khởi tạo database mới.

Công cụ tạo tài khoản quản lý và URL role runtime `tuhoc_app` trong thư mục riêng
trên máy của chủ app. Chỉ nhập URL runtime vào biến bí mật của Render; không
đưa owner URL lên web service. Gói nội dung gồm dữ liệu công khai đã có trong
app, không có tài khoản, phiên hoặc bài làm học viên. Hướng dẫn chi tiết và
giới hạn ngủ/quota: [FREE_HOSTING.md](docs/FREE_HOSTING.md).

Sau khi Render triển khai thành công và `/api/ready` trả 200, nhập URL HTTPS
thật kết thúc bằng `/api` trong app. Đăng nhập, tạo nhóm và thử cùng tài khoản
học viên trên hai thiết bị. Chưa có tài khoản nhà cung cấp hoặc URL thật nên
chưa nghiệm thu luồng này trên Internet. Hosting miễn phí vẫn cần sao lưu và
theo dõi hạn mức; chế độ production/cửa hàng tiếp tục được khóa.

## Kiểm thử và phạm vi còn lại

```bash
PYTHONPATH=services/api /workspace/venvs/khohoc/bin/pytest services/api/tests
/workspace/venvs/khohoc/bin/ruff check services/api data/pipelines scripts
/workspace/venvs/khohoc/bin/python data/pipelines/import_cli.py data/seeds/questions.json
npm run typecheck --prefix apps/admin
npm run build --prefix apps/admin
bash scripts/test_rls.sh
```

Xem docs/VALIDATION.md, docs/OCR.md để biết phạm vi kiểm tra và docs/ROADMAP.md
cho phần chưa làm. Đã có tài khoản, nhóm giáo viên, kết quả, tài liệu và OCR;
trợ lý AI trả phí đã được gỡ ở bản .18.
Chưa có liên kết phụ huynh hoặc thanh toán. Không tuyên bố quyền dùng
tài liệu bên ngoài chỉ vì nguồn được mở công khai.

Gradle proxy được cấu hình từ proxy có sẵn ở /workspace/cache/gradle/gradle.properties. Nếu sandbox chặn cache Dart trong ~/.dart-tool hoặc ~/.dartServer, cấp quyền ghi đúng thư mục công cụ hoặc chạy kiểm tra với quyền phù hợp; không đổi HOME hoặc tắt xác minh TLS.

Font tiếng Việt Noto Sans và Roboto được đóng gói trong ứng dụng cùng giấy phép OFL để không phụ thuộc tải font Google lúc chạy web.

## Demo trên một cổng localhost

Sau khi chạy backend, nạp bộ đề bằng `scripts/seed_local.py --publish-fixtures` và tài liệu bằng `scripts/seed_library.py --publish-fixtures` với token cục bộ như trên. Build web với `API_BASE_URL=/api`, rồi chạy:

```bash
bash scripts/dev_demo.sh
```

Mở http://localhost:8080 trong cùng môi trường hoặc qua chức năng xem trước/chuyển tiếp cổng 8080 của công cụ bạn dùng. `localhost` trên máy cá nhân không trỏ tới máy cloud này. Gateway chuyển tiếp API công khai và chặn đường dẫn quản trị; Flutter không gọi cổng 8000 trên máy của người xem. Token admin không được chuyển qua gateway.

Có 5 mục điều hướng: Trang chủ, Tài liệu, Luyện đề, Tiến độ, Cá nhân. PDF mở bằng trình duyệt/ứng dụng PDF, không có renderer PDF tích hợp. Bản thử không cần tài khoản. Xem docs/ROADMAP.md cho phần production và nghiệm thu còn thiếu.

## Windows: localhost phải chạy trên máy bạn

`localhost` trong Chrome trỏ tới máy đang mở Chrome, không trỏ tới máy cloud. Chạy bản local Windows từ ZIP đã đóng gói: Extract All → mở thư mục `kho-hoc-demo-windows` → nhấp đúp `start-demo.bat` → đợi `DEMO READY` → mở http://localhost:8080 và giữ cửa sổ khởi động mở.

ZIP chứa CPython 3.12.10 64-bit chính thức từ NuGet của Python Software Foundation (SHA512 được kiểm tra theo catalog), 44 wheel Windows đã pin/kiểm tra SHA256, frontend build sẵn, backend thật và dữ liệu mẫu. Thư viện cài offline vào `.demo-venv`; bài làm lưu riêng ở `state/demo.sqlite`. Gói không chứa token cloud, dữ liệu bài làm trước đó hoặc giao diện quản trị Next.js.

Nếu cổng bị chiếm, chạy `start-demo.bat --api-port 8011 --port 8091`. Không tự dừng chương trình khác. Bản giải nén đã kiểm tra backend/giao diện/PDF trên Linux với đường dẫn có tiếng Việt và khoảng trắng; Windows runtime/conditional dependencies đã kiểm tra tĩnh, chưa chạy máy Windows thực.

## Tải bản thử

Tải từ [trang Releases của dự án](https://github.com/dangminhquangfpc-gif/kho-hoc-1-12/releases)
và đọc ghi chú của đúng phiên bản. Bản .19 đã phát hành để học ngoại tuyến.
Tệp APK và bộ công cụ máy chủ .20 đang được chuẩn bị cho tag
`demo-tu-hoc-111-2026-10-15-v20`; chỉ coi đã phát hành khi có tệp đính kèm và
ghi chú xác minh tương ứng, không coi thay đổi mã nguồn là đã xuất bản APK.

- Android: chọn APK Android ARM64 hoặc ZIP chứa APK, giải nén trước khi cài.
  Khi bản cập nhật đã xác minh dùng cùng mã ứng dụng/chứng thư, cài đè;
  không gỡ app/xóa dữ liệu. Xem [hướng dẫn điện thoại](docs/PHONE_TEST.md).
- Máy chủ Windows: chọn bộ công cụ thiết lập máy chủ .20, giải nén rồi làm
  theo `DOC-TRUOC.txt` và hai bước kiểm tra/khởi tạo; xem hướng dẫn ở trên.
- Windows: chọn `tu-hoc-111-demo-windows.zip`, giải nén toàn bộ, chạy
  `start-demo.bat`. Khi nâng cấp, dừng bản cũ, sao lưu rồi chép nguyên `state`
  sang bản mới; giữ cùng cổng localhost để trình duyệt thấy lịch sử cũ.

Bản thử debug có thể bị Play Protect cảnh báo nhà phát triển mới. Không có
cam kết loại bỏ cảnh báo bằng đổi tên hoặc đóng gói lại; không tắt bảo vệ
Play Protect toàn cục để thử app. Bản này chưa được Google Play xét duyệt.

Đóng gói Windows: chuẩn bị runtime NuGet chính thức và wheelhouse/provenance
ở thư mục artifact riêng, rồi chạy
`python scripts/build_windows_demo.py --artifacts <thu-muc-artifact>`. Builder kiểm tra hash, PE64, dependency
closure và ZIP; không kèm `.env`, `state`, SDK hoặc checkout Git. Backend và
giao diện đã được kiểm tra trên Linux; batch/runtime Windows cần kiểm tra
trên máy Windows thực tế trước nghiệm thu.

## Dữ liệu mở rộng 15/10/2026

Tại mốc mở rộng này có 1.566 câu, 219 đề và 199 tài liệu; có dữ liệu cho mọi tổ hợp lớp–môn trong danh mục. Đây là dữ liệu tự biên soạn hướng tới Kết nối tri thức, chưa đối chiếu toàn bộ SGK hiện hành. Số lượng hiện hành nằm ở đầu README; xem [phạm vi và mức độ bao phủ](docs/CURRICULUM_EXPANSION.md) để phân biệt biến thể Toán, bộ ôn nền và phần còn thiếu.


### Thư viện Internet 15/10/2026

Bổ sung 1.934 mục nguồn Internet, tổng 2.133 tài liệu/liên kết; gồm 1.444 trang đề giữa/cuối kỳ KNTT và 104 mục tốt nghiệp dùng chung. Đây là liên kết nguồn, không phải PDF/câu hỏi của bên thứ ba được sao chép vào app. Chi tiết, quyền sử dụng và phần còn thiếu: `docs/INTERNET_LIBRARY.md`.


### Bài học theo mục lục và phân tách Luyện đề

Tài liệu chỉ hiện bài hướng dẫn/luyện tập đọc trong app; đề nguồn ngoài chuyển sang Luyện đề. Thêm 75 bài Toán 5 có 278 lượt bài tập và lời giải thu gọn. Mục lục tham khảo 101 sách/2.618 mục giúp theo dõi phần còn thiếu; chưa đủ mọi môn/ấn bản SGK. Xem `docs/TEXTBOOK_LESSONS.md`.

Bản thử 2026.10.15.4 sửa đường khôi phục bài không nộp được khi phiên cũ
hết hạn/mất trên máy chủ; bỏ cache giao diện ZIP cũ nhưng giữ bài làm.
Thêm 344 câu/87 bộ luyện Toán 5 tự biên soạn, tổng 1 910 câu/306 đề.
Đề Internet nằm riêng trong Luyện đề; chưa sao chép nguyên PDF nguồn ngoài.
Chi tiết và giới hạn: [cập nhật luyện đề](docs/PRACTICE_UPDATE.md).

Bản thử 2026.10.15.5 thêm tạo đề theo chủ đề/độ khó/bộ sách (tối đa 50 câu),
phân tích tiến độ từ lần làm mới nhất của mỗi câu và ôn lại câu chưa đúng.
Chạy local, không gọi AI hoặc yêu cầu tài khoản. Xem
[chi tiết module](docs/LOCAL_STUDY_MODULE.md) và [lộ trình còn lại](docs/ROADMAP.md).

Bản .10 bổ sung vai trò giáo viên/học sinh, nhóm học viên, giao đề cho nhóm, 5.246 câu và 164 đề tự biên soạn. Xem [vai trò và nhóm](docs/TEACHER_GROUPS.md). Các liên kết Internet chưa được chuyển nguyên bản hàng loạt thành đề.

Bản .11 đổi tên Tự học 111, sửa mệnh đề thừa bằng phiên bản câu mới, thêm đề tự biên soạn từ thẻ tham khảo và chuẩn bị Android/iOS. [Trạng thái cửa hàng](docs/store/RELEASE_STATUS.md).

### Máy chủ dùng chung (pilot .12)

Có cấu hình PostgreSQL/Caddy HTTPS, migration offline, chuyển dữ liệu SQLite,
phân quyền database và đồng bộ bản nháp/kết quả theo tài khoản giữa các thiết bị.
Xem [hướng dẫn triển khai và kiểm thử](docs/SHARED_SERVER.md). Cấu hình này chưa
được triển khai lên Internet; gói Windows vẫn chạy local nếu chưa đặt backend
HTTPS dùng chung. Chế độ phát hành cửa hàng vẫn được khóa.

Công cụ vận hành tiếp theo: [sao lưu PostgreSQL, khôi phục và giám sát](docs/POSTGRES_OPERATIONS.md). Các lịch systemd là cấu hình để triển khai; chưa được kích hoạt trên máy chủ Internet.
