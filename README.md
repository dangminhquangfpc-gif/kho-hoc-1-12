# Tự học 111


Monorepo MVP phát triển theo docs/PRODUCT_PLAN.md. Ứng dụng QuizApp Firebase cũ ở lib/ và android/ được giữ nguyên; ứng dụng mới ở apps/mobile/. Hướng dẫn cũ được giữ ở docs/LEGACY_QUIZAPP_README.md. Chưa hoàn thành tất cả tiêu chí MVP hoặc sẵn sàng Google Play.

Bản thử 2026.10.15.6: chọn nhiều chủ đề, bổ sung 731 câu Toán 5, tài khoản học viên và quản lý kết quả trên backend local. Hướng dẫn: [Tài khoản và quản lý học viên](docs/CLASSROOM_ACCOUNTS.md).

Bản thử 2026.10.15.7: trình bày lại lời giải và đáp số trong 75 tài liệu Toán 5; [phạm vi và cách kiểm chứng](docs/TEXTBOOK_LESSONS.md).

Bản thử 2026.10.15.8: thêm 267 hướng dẫn Toán lớp 1–4, 476 ví dụ và 952 bài tự luyện có lời giải. [Phạm vi và phần còn thiếu](docs/PRIMARY_MATH_GUIDES.md).

Bản thử 2026.10.15.9: thêm 391 hướng dẫn Toán 6–12 (230 bài đánh số cùng phần ôn tập/thực hành). [Phạm vi và giới hạn](docs/SECONDARY_MATH_GUIDES.md).

## Thành phần

- apps/mobile: Flutter, Riverpod, GoRouter, Dio; chọn lớp/môn/đề, làm bài, chấm qua API, đánh dấu câu, lưu bài/lịch sử; kho tài liệu, yêu thích/đọc gần đây và tiến độ cục bộ.
- services/api: FastAPI, SQLAlchemy, deterministic grader; public DTO không chứa đáp án, guest attempt token, admin import/duyệt/xuất bản.
- apps/admin: Next.js/TypeScript, auth cục bộ server-side; JSON/CSV import, duyệt, sửa/khôi phục phiên bản và quản lý tài liệu.
- supabase/migrations: schema đích/RLS; chưa nối Supabase Auth/Storage production.
- data/: 108 câu hỏi gốc, 12 đề Toán/Tiếng Việt/Ngữ văn/Tiếng Anh; 4 ghi chú tự biên soạn kèm PDF tiếng Việt.

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

Android emulator dùng --dart-define=API_BASE_URL=http://10.0.2.2:8000; phải cung cấp đường kết nối từ emulator tới backend. API cloud mặc định bind loopback; emulator/điện thoại khác máy không tự kết nối được. Thiết bị thật cần backend HTTPS được triển khai an toàn sau khi hoàn thiện production auth; không bật public dev token.

```bash
flutter analyze
flutter test
flutter build web --pwa-strategy=none --no-wasm-dry-run --no-web-resources-cdn --dart-define=API_BASE_URL=/api
flutter build apk --debug
```

APK cần Android SDK/JDK và license. Hướng dẫn AAB/signing trong docs/PLAY_STORE_CHECKLIST.md; release chưa nghiệm thu.

## Database

Supabase: áp dụng SQL trong supabase/migrations bằng CLI hoặc SQL editor có quyền thích hợp. Không chạy bootstrap_local.sql trên hosted Supabase. RLS kiểm thử qua scripts/test_rls.sh trên container PostgreSQL local riêng. API local dùng bảng local_*; adapter sang schema đích, Auth và Storage chưa triển khai (docs/DATABASE_SCHEMA.md).

## Kiểm thử và phạm vi còn lại

```bash
PYTHONPATH=services/api /workspace/venvs/khohoc/bin/pytest services/api/tests
/workspace/venvs/khohoc/bin/ruff check services/api data/pipelines scripts
/workspace/venvs/khohoc/bin/python data/pipelines/import_cli.py data/seeds/questions.json
npm run typecheck --prefix apps/admin
npm run build --prefix apps/admin
bash scripts/test_rls.sh
```

Xem docs/VALIDATION.md để biết chính xác lệnh đã chạy và docs/ROADMAP.md cho phần chưa làm. Chưa có kho PDF, OCR, AI provider, dashboard giáo viên/phụ huynh, tài khoản hoặc thanh toán trong ứng dụng mới. Không crawl hoặc tuyên bố quyền dùng tài liệu bên ngoài.

Gradle proxy được cấu hình từ proxy có sẵn ở /workspace/cache/gradle/gradle.properties. Nếu sandbox chặn cache Dart trong ~/.dart-tool hoặc ~/.dartServer, cấp quyền ghi đúng thư mục công cụ hoặc chạy kiểm tra với quyền phù hợp; không đổi HOME hoặc tắt xác minh TLS.

Font tiếng Việt Noto Sans và Roboto được đóng gói trong ứng dụng cùng giấy phép OFL để không phụ thuộc tải font Google lúc chạy web.

## Demo trên một cổng localhost

Sau khi chạy backend, nạp bộ đề bằng `scripts/seed_local.py --publish-fixtures` và tài liệu bằng `scripts/seed_library.py --publish-fixtures` với token cục bộ như trên. Build web với `API_BASE_URL=/api`, rồi chạy:

```bash
bash scripts/dev_demo.sh
```

Mở http://localhost:8080 trong cùng môi trường hoặc qua chức năng xem trước/chuyển tiếp cổng 8080 của công cụ bạn dùng. `localhost` trên máy cá nhân không trỏ tới máy cloud này. Gateway chuyển tiếp API công khai và chặn đường dẫn quản trị; Flutter không gọi cổng 8000 trên máy của người xem. Token admin không được chuyển qua gateway.

Có 5 mục điều hướng: Trang chủ, Tài liệu, Luyện đề, Tiến độ, Cá nhân. PDF mở bằng trình duyệt/ứng dụng PDF, không có renderer PDF tích hợp. Bản thử không cần tài khoản. Xem docs/ROADMAP.md cho phần Supabase/AI/production còn thiếu.

## Windows: localhost phải chạy trên máy bạn

`localhost` trong Chrome trỏ tới máy đang mở Chrome, không trỏ tới máy cloud. Chạy bản local Windows từ ZIP đã đóng gói: Extract All → mở thư mục `kho-hoc-demo-windows` → nhấp đúp `start-demo.bat` → đợi `DEMO READY` → mở http://localhost:8080 và giữ cửa sổ khởi động mở.

ZIP chứa CPython 3.12.10 64-bit chính thức từ NuGet của Python Software Foundation (SHA512 được kiểm tra theo catalog), 44 wheel Windows đã pin/kiểm tra SHA256, frontend build sẵn, backend thật và dữ liệu mẫu. Thư viện cài offline vào `.demo-venv`; bài làm lưu riêng ở `state/demo.sqlite`. Gói không chứa token cloud, dữ liệu bài làm trước đó hoặc giao diện quản trị Next.js.

Nếu cổng bị chiếm, chạy `start-demo.bat --api-port 8011 --port 8091`. Không tự dừng chương trình khác. Bản giải nén đã kiểm tra backend/giao diện/PDF trên Linux với đường dẫn có tiếng Việt và khoảng trắng; Windows runtime/conditional dependencies đã kiểm tra tĩnh, chưa chạy máy Windows thực.

## Demo chạy trên máy Windows của người xem

Nếu mở localhost:8080 trên máy cá nhân thấy ERR_CONNECTION_REFUSED, máy đó chưa chạy demo; server trong cloud không tự nối tới localhost của người xem. Gói Windows đã đóng sẵn tại `/workspace/artifacts/kho-hoc-demo-windows.zip`. Giải nén toàn bộ và nhấp đúp `start-demo.bat`; trình duyệt chỉ mở sau khi API và giao diện đã sẵn sàng.

Gói chứa Python Software Foundation 3.12.10 (Windows64-bit), web Flutter đã build, backend thật, dữ liệu/PDF tự biên soạn và44 wheels được xác minh SHA256. Không cần cài Flutter/Node/Supabase hoặc tải dependency khi khởi động trên Windows. Lần đầu tạo venv trong thư mục gói; dữ liệu ở `state/demo.sqlite`. Launcher chỉ nghe loopback, không mở admin, không dùng credential/database production. `uvloop` chỉ dùng ngoài Windows; colorama/tzdata được khóa riêng cho Windows.

Đóng gói lại: chuẩn bị runtime NuGet chính thức và wheelhouse/provenance tại artifact directory, rồi chạy `python scripts/build_windows_demo.py --artifacts /workspace/artifacts`. Builder kiểm tra hash, PE64, dependency closure và ZIP; không kèm .env, state, SDK hoặc checkout Git.

Backend/giao diện và khởi động từ ZIP đã kiểm tra trên Linux, kể cả đường dẫn có dấu/khoảng trắng. Runtime và batch Windows chưa chạy trên máy Windows thực tế.


## Dữ liệu mở rộng 15/10/2026

Bản thử hiện có 1.566 câu, 219 đề và 199 tài liệu; có dữ liệu cho mọi tổ hợp lớp–môn trong danh mục. Đây là dữ liệu tự biên soạn hướng tới Kết nối tri thức, chưa đối chiếu toàn bộ SGK hiện hành. Xem [phạm vi và mức độ bao phủ](docs/CURRICULUM_EXPANSION.md) để phân biệt biến thể Toán, bộ ôn nền và phần còn thiếu.


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
