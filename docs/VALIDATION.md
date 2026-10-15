# Kết quả xác minh — 14/10/2026

| Thành phần | Kết quả hiện tại |
|---|---|
| Backend unit/integration | 21 kiểm thử đạt: quyền riêng tư, snapshot, import, chấm điểm, AI chưa cấu hình |
| API chạy thực tế | HTTP chọn lớp/đề → nộp → kết quả → xóa đạt |
| PostgreSQL 17 | Migration chạy và chạy lại; 7 kiểm tra quyền/RLS đạt trong DB riêng |
| Dataset | 60 câu hỏi gốc qua schema/duplicate validator; chuyên gia chưa kiểm duyệt |
| Next.js | Build và typecheck đạt |
| Admin browser | Token sai bị từ chối; login, export 60 câu, logout và export unauthorized đạt |
| Flutter tests | 2 kiểm thử đạt sau sửa lỗi map đáp án và selector hộp xác nhận |
| Flutter analyzer | Đạt: No issues found, kể cả mã đăng ký font và giấy phép |
| Flutter web | Build đạt (mã thoát 0); browser đạt sau khi đóng gói font: mở đề → trả lời → tải lại/khôi phục → nộp → điểm → lịch sử. Source hiển thị số câu và nội dung đáp án dễ đọc. |
| Android | APK debug build đạt (mã thoát 0), chữ ký xác minh đạt; target/compile API 36, min API 24, tên Kho Học 1–12. Chưa chạy trên thiết bị Android. |
| Setup script | Script cuối chạy đạt (mã thoát 0), gồm JDK/SDK, trust store, proxy, frozen locks. install_script/start_skill đã lưu vào bản nháp; chưa xuất bản môi trường. |
| GitHub Actions | Đã tạo workflow; chưa chạy trên GitHub |
| Supabase hosted, thiết bị Android, AAB release | Chưa thực thi |

SQLite development và kiểm thử PostgreSQL auth shim không chứng minh đã triển khai Supabase production. Dataset được publish chỉ trên instance development cô lập để kiểm thử, không có duyệt chuyên môn hoặc công khai lên internet.

APK: apps/mobile/build/app/outputs/flutter-apk/app-debug.apk (~76 MB), applicationId vn.khohoc.kho_hoc_mobile, version 0.1.0+1. Đây là build development dùng backend của bạn; không phải gói release Google Play.

Sau khi exec transport bị ngắt, đã chạy lại các bước với log và mã thoát trên đĩa; API/web services đã restart và xác minh health/assets. Không coi artifact tồn tại đơn thuần là kết quả command thành công.

Xác minh cuối: mobile smoke script trong apps/admin/tests/mobile-smoke.cjs đạt với mã thoát 0 sau khi khởi động lại API/web server. APK cuối cũng được apksigner verify xác nhận; aapt đọc đúng target 36/min 24.

## Chuẩn bị thử điện thoại

- Đã thêm cấu hình HTTPS, kiểm tra health/danh mục rồi lưu URL; không đổi server khi còn bài/lịch sử.
- 3 Flutter tests passed; kiểm thử URL từ chối HTTP, mật khẩu, query và đường dẫn.
- Backend preview: kiểm thử nạp 4 đề, chặn admin/docs/OpenAPI, rate limit passed; HTTP thật tải đề → nộp → kết quả → xóa passed ở cổng thử nội bộ 8001.
- APK debug mới build thành công, chữ ký kiểm tra thành công. Chưa thử thiết bị thật.
- `render.yaml` và Dockerfile là cấu hình chuẩn bị; chưa build Docker hoặc triển khai hosting, chưa có URL HTTPS được xác nhận. Xem PHONE_TEST.md.

## MVP local mở rộng và demo một cổng

- 108 câu/12 đề tự biên soạn, 4 ghi chú Toán kèm PDF tiếng Việt thật; kiểm tra schema/catalog/chấm điểm/dedupe bộ đề ngôn ngữ đạt.
- 58 backend tests đạt: tài liệu theo quyền xem/tải, lọc và tìm không dấu, chặn PDF vượt thư mục; câu hỏi phiên bản/snapshot/rollback; seed không tự duyệt nội dung admin đã chỉnh sửa.
- 6 Flutter tests đạt cho luyện đề/lưu bài, URL backend, đọc tài liệu và yêu thích/đọc gần đây, xóa lịch sử khi bản ghi server đã mất và giữ lỗi khi server không sẵn sàng. Luồng web thật đánh dấu câu → reload/khôi phục → nộp → kết quả/lịch sử đạt.
- Luồng web thư viện thật: tìm không dấu → yêu thích → đọc → PDF cùng origin đạt. Demo web chạy cổng8080, API public dưới /api, admin bị gateway chặn404. Backend vẫn ở loopback8000.
- Next production build và TypeScript đạt; quản trị edit/rollback và nhập/duyệt/publish tài liệu đạt trên database thử riêng. Devserver localhost3000 xác minh đăng nhập/xuất108 câu/đăng xuất/401. Cookie Secure production cần HTTPS; không tuyên bố đã kiểm thử production authentication trên HTTP.
- Android debug với url_launcher đã build thành công, apksigner verify exit0. Chưa chạy máy thật/emulator, chưa ký release/AAB.
- Đã lưu hướng dẫn gateway/seed mới trong draft cloud. Draft vẫn cần Review/Save/Publish để dùng cho phiên mới; chưa publish.
- Chưa có Supabase adapter/Auth/Storage, hosted backend, AI provider hoặc OCR; người dùng đã chọn tiếp tục chế độ local. PDF mở bằng browser/system viewer; chưa có upload/parser/OCR PDF hay renderer PDF trong Flutter.

Bản cuối sau Việt hóa metadata và xử lý xóa lịch sử: 6 Flutter tests đạt, debug web build đạt, APK debug build lại đạt (157.7s), chữ ký APK xác minh thành công. Demo đang dùng build web debug; build web release trước đó cũng đã đạt.

## Gói demo desktop Windows

- Sửa hướng dẫn localhost: trình duyệt khách không truy cập trực tiếp localhost của cloud; tạo launcher chạy backend + frontend ngay trên máy cá nhân.
- Khóa dependency theo nền tảng: uvloop chỉ ngoài Windows; colorama/tzdata pin và chỉ Windows. 44 Windows wheels đủ toàn bộ Requires-Dist được kiểm tra theo marker Windows/Python 3.12, SHA256 manifest được xác minh trước cài offline.
- CPython 3.12.10 NuGet 64-bit có python.exe, venv, ensurepip và DLL runtime; SHA512 bytes khớp catalog nguồn. License/provenance được đóng gói.
- ZIP 57,504,932 bytes, kiểm tra CRC mọi entry; không chứa .env/state/.git hoặc virtualenv có sẵn. Đã giải nén và chạy launcher trên Linux/Python3.12 ở đường dẫn tiếng Việt/khoảng trắng; startup READY, UI web/API/PDF và vòng làm/nộp/xóa bài thật đạt. Kiểm tra SIGINT dừng đúng hai service thuộc launcher; không dừng service khác.
- Sáu kiểm thử fixture/preview sau thay đổi UTF-8 đạt. Không có Wine/Windows runtime executor, nên chưa xác nhận chạy batch/DLL trực tiếp trên Windows; không tuyên bố đã thử máy Windows thực.

## Gói localhost cho Windows

- PSF Python3.12.10 NuGet lấy từ api.nuget.org; SHA512 khớp catalog chính thức, executable PE AMD64, có venv/ensurepip và DLL runtime.
- 44 wheels Windows CPython3.12: hash manifest SHA256, khóa version, tất cả dependency có điều kiện cho Windows được thỏa mãn (colorama/tzdata; bỏ uvloop theo marker). ZIP không chứa state/credential; CRC toàn bộ ZIP đạt.
- Launcher thực tế chạy từ ZIP đã giải nén vào thư mục có dấu và khoảng trắng, dùng runtime Linux cho kiểm thử. API/proxy/web readiness đạt; làm/nộp đề có điểm1/13; PDF hợp lệ; admin bị chặn404. Cổng trùng được phát hiện trước khi cài đặt, không dừng tiến trình khác.
- Ruff/shell syntax đạt; 6 regression API tests fixture/preview sau chỉnh UTF-8 đạt. Chưa chạy Python.exe/.bat trên Windows thật; không tuyên bố đã kiểm thử Windows-native.


## Expanded local demo — 15/10/2026

60 backend tests passed after adding the curriculum bank and coverage endpoint. The final grade-specific physics/chemistry/biology modules subsequently passed content integrity and preview integration checks (3 tests). Flutter analyze passed, 6 Flutter tests passed, and the release web build completed. A ZIP extracted into a Vietnamese path successfully upgraded a database from the earlier package. HTTP checks confirmed 135 grade–subject pairs, totals of 1,566 questions/219 exams/199 notes, full marks for four new math/science exams, hidden answer keys, and blocked admin routes. Browser practice/reload/resume/submit/history smoke passed. Windows wheel closure, runtime provenance and ZIP CRC checks passed; Windows native execution remains unrun in this Linux environment. Textbook chapter-by-chapter alignment and independent teacher review remain pending; see CURRICULUM_EXPANSION.md.


## Internet library — 15/10/2026

63 backend tests passed, including source provenance, correct grade/period classification, namespace rules for national exams, and period/year filtering. Flutter analyze passed; 7 Flutter tests passed including paginated document retrieval; release web build passed. A package extracted into a Vietnamese path upgraded the previous demo database and exposed 2,133 documents/1,934 link-only sources. HTTP checks verified term/year filters, private evidence omission, denied local PDF copies and blocked admin. Source HTTP 200 records with book evidence and hashes are stored in data/library/source_checks.json. Windows native execution remains unrun.
