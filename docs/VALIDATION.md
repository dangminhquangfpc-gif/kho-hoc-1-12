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


## Lesson organization — 15/10/2026

64 backend tests passed, including separated lesson/exam lists, sequential Math5 lessons 1–75, source-index coverage and explicit missing units. Flutter analyze passed; previous 7 tests passed plus the new conceal/reveal solution regression passed. Release web build passed. The package upgraded a database from the prior Internet demo; HTTP verified 82 Math5 study documents (75 indexed lessons plus 7 prior notes) and exams confined to their collection. Live browser checked Math5 navigation and Luyện đề → external exams; expanded solutions were visually verified. Windows native execution remains unrun. Official publisher catalog lookup returned 401; public searches returned no records. Full textbook/edition completeness remains unverified.

Bản thử 2026.10.15.4: đã thêm kiểm thử phục hồi phiên 404 và giữ đáp án,
loại đáp án khi câu cùng mã thay đổi; kiểm thử tách lựa chọn PDF, thiếu đáp
án/số câu trùng và không nhập phần lời giải như câu hỏi. Số liệu ngân hàng
mới: 1 910 câu/306 đề, trong đó 344 câu Toán 5 mới.

Kiểm tra local hoàn tất: 68 kiểm thử Python và 10 kiểm thử Flutter đều qua;
Flutter analyze không còn cảnh báo; web release build thành công với PWA
cache tắt. Thử công cụ PDF trên một PDF mẫu tự biên soạn thực tế: tách đúng
2 câu và đáp án thành JSON hợp lệ, luôn giữ trạng thái chờ kiểm tra, không
phát hành. Không phải thử chuyển nguyên đề Internet có bản quyền.

QA trình duyệt trên ZIP đã giải nén, nâng cấp từ DB bản trước: Toán 5 có
419 câu/95 đề; Tài liệu có đúng 75 bài và không chứa đề/link ngoài. Khôi
phục phiên không còn trên máy chủ, giữ 8 đáp án và nộp được 8/8. Một service
worker cũ và cache tài nguyên được loại bỏ khi mở bản mới; dữ liệu lưu vẫn
còn. Mở đề Internet từ Luyện đề giữ lớp 5 đã chọn. Playwright chạy Chromium
thực trên Linux; không thay thế kiểm tra Windows.

Bản thử 2026.10.15.5: 70 kiểm thử backend và 17 kiểm thử Flutter đều qua;
Flutter analyze sạch, web release build với PWA cache tắt thành công.
Các kiểm thử mới xác nhận chọn câu theo bộ lọc, không lặp, loại bản nháp,
không lộ đáp án, snapshot giữ đúng khóa khi nội dung sau đó đổi; ôn câu sai,
loại lỗi cũ sau khi làm đúng, điểm từng phần, bỏ câu chờ duyệt và tính lại
sau khi xóa lịch sử. Kiểm thử khôi phục đề tự tạo giữ đúng bộ mã câu cũ.

QA bản .5 trên ZIP đã giải nén, dùng lại DB bản .4: tạo đề theo bộ lọc
Toán 5/Số tự nhiên gồm 8 câu; nhập/lưu cả 8 đáp án; khôi phục phiên giả lập
không còn trên server và giữ nguyên thứ tự bộ câu/đáp án; nộp đạt 6/8.
Tiến độ hiển thị 75% và đề xuất đúng 2 câu chưa đúng. Ôn hai câu đạt 2/2,
thống kê chủ đề thành 100% trên 8 câu khác nhau, không đếm thành 10 câu.
Thử bằng Chromium với backend thực trên Linux, chưa chạy Windows/Android
thiết bị thật. Toàn bộ luồng tạo đề, khôi phục, nộp, ôn lại và cập nhật
tiến độ đã hoàn tất kiểm tra trên gói giải nén.

## Bản 2026.10.15.7 — lời giải tài liệu

83 kiểm thử backend và 23 kiểm thử Flutter đạt; Flutter analyze không có lỗi; web release build thành công. 75 tài liệu, 139 ví dụ và 278 lời giải tự luyện có bước giải và đáp số; kiểm tra đẳng thức bằng Fraction, kiểm tra đặt tính trên màn hình 320 px. Gói nâng cấp dùng state bản .6 đã chạy: 75 tài liệu lên phiên bản 2, 75 mục nhật ký lưu nội dung cũ, số tài khoản và kết quả không đổi. Chưa nghiệm thu Windows thật hoặc xác minh nguyên mẫu từng trang SGK.

## Bản 2026.10.15.8 — hướng dẫn Toán ngoài lớp 5

88 kiểm thử backend và 23 kiểm thử Flutter đạt; Flutter analyze và web release build đạt. Kiểm tra 267 bài mới khớp ID/tiêu đề/URL mục lục, có 476 ví dụ và 952 bài luyện kèm lời giải/đáp số, các đẳng thức tính được chính xác bằng Fraction, miền số và số chữ số của bài tính phù hợp lớp. Gói nâng cấp từ .7 nhập đủ bài, tổng Toán 1–5 có 342 hướng dẫn; số tài khoản/kết quả và phiên bản 75 bài Toán 5 giữ nguyên. Chưa xác nhận đủ toàn SGK, chưa thẩm định sư phạm độc lập hoặc nghiệm thu Windows thật.

## Bản 2026.10.15.9 — hướng dẫn Toán 6–12

93 kiểm thử backend và 23 kiểm thử Flutter đạt; analyze, web release build và Ruff đạt. Kiểm tra 391 mục khớp nguồn mục lục, gồm 230 bài đánh số liên tục; 610 ví dụ và 1.220 bài tự luyện có lời giải/đáp số. Kiểm tra độc lập 22 đáp số bằng Sympy, cùng lãi kép và quy tắc hình thang. Gói giải nén nâng cấp giữ tài khoản, kết quả và phiên bản tài liệu cũ; API trả đủ hướng dẫn cho cả 7 lớp. Chromium mở được Nguyên hàm và Bayes cùng lời giải trên backend thực. Tìm kiếm ưu tiên tên bài đã có kiểm thử hồi quy. Chưa nghiệm thu Windows/Android thật, chưa thẩm định sư phạm độc lập hoặc xác nhận mọi dạng bài/trang SGK; các môn ngoài Toán còn thiếu.
