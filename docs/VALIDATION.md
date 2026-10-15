# Kết quả xác minh

Bản mã nguồn hiện hành **.19 / 0.2.0+19**. Kết quả .19 ở ngay dưới;
các mốc .18 trở về trước được giữ để đối chiếu lịch sử, không mô tả đầy đủ
hành vi hiện hành. Build đạt không đồng nghĩa đã phát hành APK công khai
hoặc được Google Play xét duyệt.

## Bản .19 — học trên thiết bị khi chưa có backend

### Đã hoàn tất kiểm tra local

| Phạm vi | Kết quả |
| --- | --- |
| Flutter | **229 kiểm thử đạt**, analyzer **không có lỗi** |
| Gói dữ liệu ngoại tuyến | **6 kiểm thử Python đạt** trong `services/api/tests/test_offline_bundle.py` |
| Tái tạo dữ liệu | `scripts/build_offline_bundle.py --check` và `scripts/build_offline_grading_cases.py --check` đạt; asset/oracle khớp nguồn hiện tại |
| Đối chiếu bộ chấm Dart/Python | Toàn bộ **7.886 câu** với đáp án đúng và câu trả lời rỗng khớp oracle backend; thêm **151 trường hợp biên** đạt |
| Build web | Flutter release build đạt |
| Build Android | APK debug build đạt; chưa coi là bản đã được Google Play duyệt |

Bộ xuất đọc fixture được chỉ định, không đọc database tài khoản hoặc trạng
thái người học. Có 7.886 câu đang dùng, 1.461 đề, 2.866 mục tài liệu/nguồn
và 733 hướng dẫn Toán lớp 1–12. Kiểm thử đối chiếu với publication thật của
preview, mã câu thay thế, ID đề đúng lớp/môn, quyền phân phối và giấy phép,
phân loại bài học và tính tái tạo. Các mục nguồn ngoài chỉ có siêu dữ
liệu/liên kết; gói không chứa toàn bộ PDF Internet.

`apps/mobile/test/offline_grading_parity_test.dart` dùng oracle do Python
backend tạo, độc lập với bộ chấm Dart. 151 ca biên gồm chuẩn hóa Unicode,
số/đơn vị, đáp án chọn và trạng thái tự luận; tự luận vẫn **chờ đánh giá
thủ công**, không tự cho điểm. Điểm ngoại tuyến là kết quả tự luyện, không
tự gửi vào điểm lớp. Đáp án được đóng gói trong app; không dùng ngân hàng
này như đề bí mật cho đánh giá có giám sát.

Các kiểm thử repository/UI kiểm tra tạo/nộp/lấy lại/xóa kết quả tự luyện,
lưu cục bộ, tách bài/lịch sử máy chủ và ngoại tuyến, không mở tài khoản hay
nhóm trong chế độ ngoại tuyến và giữ điểm tài khoản phía máy chủ riêng.
Kiểm thử mock/storage này không thay bằng chứng chạy SharedPreferences và
vòng đời ứng dụng trên Android thật.

### QA trình duyệt, gói cài và CI của .19

- Trình duyệt dùng asset thật, chặn toàn bộ API/ngoài miền: làm đề 13 câu,
  lưu và tải lại câu trả lời, nộp được 1/13, mở tiến độ/lịch sử và hướng dẫn
  hình tròn lớp 5 với lời giải/đáp số đầy đủ. Không có lỗi JavaScript hoặc
  yêu cầu API/ngoài miền; tài khoản, bài đang làm và lịch sử máy chủ đã gieo
  trước được giữ nguyên. Đây là Chromium web, không phải ảnh Android.
- APK version 19 cùng application ID/chứng thư debug với .18, xác minh
  chữ ký, CRC, asset đúng nguồn và ZIP alignment 16 KB đạt; quyền không đổi.
  Gói ZIP tải xuống chứa đúng một APK đã ký.
- AAB engineering .19 build/preflight đạt, 10 thư viện native 64-bit và
  BundleConfig đạt kiểm tra alignment 16 KB; asset khớp nguồn. AAB vẫn
  **chưa ký**, không dùng để upload Google Play.
- Source `c27cbe05c9f846dbf3c6c99aeda9b6474bcfc975`: hai lượt MVP CI đạt,
  gồm Flutter 229, backend **187 đạt / 19 bỏ qua**, launcher 4 đạt,
  PostgreSQL riêng **38 đạt / 10 không chọn** và kiểm tra RLS đạt. Các ca
  bỏ qua không được tính là đã đạt. Android AAB và iOS unsigned CI cùng
  source đều đạt; iOS kiểm tra tên app, SDK 26+ và privacy manifest.
- Native OCR thật đạt khi tắt Wi-Fi/dữ liệu. Kiểm thử học ngoại tuyến thật
  đã qua mở lần đầu, lớp 12, lưu/mở lại/nộp 1/13 và tiến độ; sau đó thất bại
  do finder chỉ khớp runtime type `FilledButton`, trong khi nút Lịch sử
  dùng `FilledButton.icon`. Đã sửa finder trong kiểm thử và thêm chờ chuyển
  màn hình; **đang chạy lại**, chưa coi lịch sử/hướng dẫn native là đã đạt.

### Chưa nghiệm thu/phát hành production

- Chưa nghiệm thu cập nhật .18 → .19 trên điện thoại vật lý, hành vi chọn
  ảnh/quyền hệ điều hành, bộ nhớ thấp, hệ điều hành trang nhớ 16 KB hoặc
  Windows runtime thật. Tải xuống công khai .19 đang chờ kiểm tra cuối.
- Chưa có backend production, tài khoản Play Console, khóa upload hoặc
  nghiệm thu đầy đủ nội dung/quy trình trẻ em. Native ML Kit vẫn có công bố
  dữ liệu chẩn đoán; học ngoại tuyến không chứng minh SDK không nối mạng.

Hướng dẫn và giới hạn: [OFFLINE_STUDY.md](OFFLINE_STUDY.md),
[PHONE_TEST.md](PHONE_TEST.md), [trạng thái cửa hàng](store/RELEASE_STATUS.md).

## Mốc ban đầu — 14/10/2026

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

## Bản 2026.10.15.10 — vai trò, nhóm và ngân hàng câu hỏi

98 kiểm thử backend đạt; sau khi sửa bộ lọc đường dẫn nhóm ở preview/gateway, kiểm thử preview được chạy lại và đạt. 23 kiểm thử Flutter, analyze và web release build đạt. Thêm 5.246 câu và 164 đề tự biên soạn; kiểm tra schema, câu/lựa chọn không trùng, mọi ID đề tồn tại đúng lớp/môn, chấm đáp án đúng, miền số lớp 1/xác suất, độc lập tính tốc độ và khối lượng riêng. Kiểm tra giáo viên khác không xem kết quả/đề nhóm, học sinh không tạo đề hoặc lách bằng ID tùy ý; học sinh vẫn ôn câu sai đã lưu của mình.

Gói giải nén nâng cấp giữ nguyên tài khoản/kết quả cũ, có 7.886 câu hoạt động và 470 đề. Chromium trên gateway/backend thật: giáo viên tạo nhóm và đề hai chủ đề, học sinh chưa tham gia không xem đề được, tham gia nhóm rồi mở đề trong giao diện; API chấm 10/10 và giao diện báo cáo giáo viên hiện 100%. Đã đối chiếu toàn bộ payload gói cuối với tệp thực tế chạy QA. ZIP không chứa state. Chưa nghiệm thu Windows/Android thật hoặc thẩm định sư phạm độc lập; chưa nhập nguyên văn hàng loạt đề Internet.

## Bản 2026.10.15.11 — Tự học 111 và chuẩn bị cửa hàng

102 kiểm thử backend, 23 kiểm thử Flutter đạt; analyze, Ruff và web release build đạt. 12 câu có mệnh đề thừa được thay bằng ID phiên bản mới, bản cũ giữ trong snapshot lịch sử. 991 thẻ nguồn có đề tự biên soạn 20–24 câu cùng lớp/môn; 525 thẻ chưa đủ ngân hàng vẫn là tham khảo. Không khẳng định đã chuyển nguyên văn đề nguồn hoặc đủ ma trận chương/học kỳ. Tổng 1.461 đề cố định và 7.886 câu hoạt động.

Gói giải nén nâng cấp giữ nguyên tài khoản, kết quả và đề riêng giáo viên. Chromium qua gateway/backend thực: tên Tự học 111, câu Đúng/Sai sạch trên giao diện; thẻ Toán 5 mở đề 24 câu, API chấm 24/24; xóa tài khoản qua gateway làm phiên hết hiệu lực. AAB release engineering 0.2.0+11 biên dịch đạt, manifest có đúng tên/application ID và targetSdkVersion 36, ZIP nguyên vẹn, jarsigner xác nhận unsigned. Chưa phải AAB được ký/cấu hình backend production để tải lên Play.

iOS đã thêm project, Podfile, privacy manifest UserDefaults CA92.1 và workflow build engineering không ký trên macOS có SDK 26+. Trên môi trường Linux chỉ kiểm tra cấu hình/plist; không tuyên bố đã tạo IPA có chữ ký hoặc kiểm thử iPhone thật. Chưa có tài khoản Play Console/Apple Developer/backend HTTPS, chưa triển khai/gửi xét duyệt. Chi tiết nguồn chính sách hiện hành và các bước còn thiếu: store/RELEASE_STATUS.md.

## Bản 2026.10.15.16 — OCR local và nền tảng trợ lý AI

Backend đầy đủ: **224 passed, 20 skipped**; PostgreSQL container: **54 passed,
55 deselected**, có kiểm tra quota AI nguyên tử. Flutter: **43 passed** và
analyze sạch; Ruff, kiểm tra khoảng trắng và web release build đạt. Kiểm thử
đăng ký được cập nhật cuộn đến nút trong ListView khi thêm mục OCR.

`node scripts/test_browser_ocr.cjs` chạy Tesseract thật trong Chromium: đọc
đúng chữ in tiếng Việt, 12 cm/5 cm/60 cm² với chỉ số confidence 95. Kiểm tra
PNG/JPEG/WebP, tệp giả/SVG/MIME sai/ảnh quá lớn, tác vụ đồng thời, hủy ngay
worker, hủy chọn tệp và timeout. Không có request ngoài origin hoặc ảnh trong
localStorage/IndexedDB. `prepare_ocr_assets.py --verify` xác nhận 14 tệp local;
packager đối chiếu tất cả checksum với bản web biên dịch, giữ giấy phép.

AI dùng provider mô phỏng để kiểm tra consent/host, xác thực, tham chiếu bài
của chính học viên sau khi nộp, phản hồi sai/quá lớn, timeout, quota và điểm
không đổi. Không có khóa hoặc yêu cầu đến nhà cung cấp AI thật; chưa đánh giá
chất lượng mô hình. Mặc định API báo chưa cấu hình và không tạo lời giải giả.

Shared HTTPS smoke đạt xác minh TLS, tài khoản/phân quyền, trạng thái AI tắt,
đồng bộ hai thiết bị, khởi động lại, database lỗi và khôi phục PostgreSQL mã
hóa với phiên cũ bị thu hồi. Docker image mới đã build. Không triển khai lên
máy chủ Internet. Các giới hạn còn lại được ghi trong [AI_OCR.md](AI_OCR.md).

Đã chạy chính ZIP .16 giải nén qua launcher/backend thật trong Chromium:
chọn ảnh tiếng Việt, thấy ảnh/chữ/confidence 95; sửa chữ làm mất xác nhận cũ.
Câu nhập đáp án giữ nội dung đã gõ, nhận văn bản một ký tự `5` từ màn hình
kiểm tra, không tự nộp; chỉ nộp khi bấm nút và xác nhận. Kết quả mở được trợ
lý với trạng thái chưa cấu hình và lựa chọn tham chiếu. Không có request
ngoài origin, ảnh trong POST hoặc lỗi JavaScript. Nâng cấp từ database .15
giữ nguyên từng dòng tài khoản, kết quả, nhóm và phản hồi cũ. Backend/web/docs
và toàn bộ 14 tài sản OCR trong ZIP khớp nguồn/build; ZIP không chứa state.
Runtime/batch Windows chỉ kiểm tra tĩnh, chưa chạy máy Windows thật.

## Bản .17 — OCR native và cấu hình khóa AI

- Backend: **225 passed,20 skipped**. Công cụ cấu hình/launcher: **57 passed**,
  gồm quyền tệp, rollback khi lỗi, Windows ACL mô phỏng và chọn duy nhất nguồn
  môi trường hoặc tệp. Flutter đầy đủ: **55 passed** (8 kiểm thử lifecycle/ảnh
  native), analyze sạch; Ruff và web release build đạt.
- Android ARM64 debug build đạt, versionCode17/minSdk24/targetSdk36, chữ ký
  Android Debug được xác minh, có sẵn tài sản mô hình ML Kit Latin. Đây là
  APK thử nghiệm có địa chỉ backend mặc định chưa triển khai; OCR local dùng
  được, chức năng máy chủ cần backend HTTPS thật trong phần Kết nối máy chủ.
- iOS engineering unsigned build bằng Xcode/iOS SDK26.5 đạt trên macOS;
  version17/minimumOS15.5, có LatinOCRResources.bundle và privacy manifest,
  không có provisioning profile phân phối. Chưa có IPA được ký hoặc OCR iOS
  runtime/thiết bị vật lý được kiểm chứng.
- ML Kit thật trên Android emulator API35 đạt: đọc trang PNG tự tạo gồm chữ
  tiếng Việt có dấu và số12/5/60; Wi-Fi/dữ liệu di động tắt khi chạy, không
  dùng OCR/đáp án mô phỏng. Pipeline giải mã/chuẩn hóa/model là mã sản phẩm,
  chỉ bỏ qua UI picker hệ điều hành. Giữ nguyên ảnh gốc, previewPNG và
  confidence=null đúng API. Run38725379799 tại commitb65c199a1fb9cb748ffa82c2ae2c790068bfc1a8.
- Chính ZIP Windows .17 giải nén: OCR picker thật confidence95, sửa chữ bỏ
  xác nhận, giữ đáp án cũ và nhập một ký tự5 không tự nộp, mở trợ lý báo chưa
  cấu hình. Không request ngoài origin/ảnh trongPOST/lỗiJS. Sau đó dùng helper
  và khóa synthetic để xác nhận launcher/backend đọc cấu hình qua API đăng
  nhập; **không gửi bất kỳ yêu cầu tới provider AI**. Không coi configured=true
  với khóa synthetic là kết nối AI thật.
- Nâng cấp .16 giữ nguyên từng dòng tài khoản/kết quả/nhóm/phản hồi. ZIP không
  chứa state/khóa; helper/docs/web/backend trong gói khớp nguồn/build.

Sửa thêm lối mở OCR-only khi xác thực máy chủ lỗi: không gọi auth/status/môn
học từ màn hình OCR, có nhận/sửa/xác nhận/sao chép và giữ nguyên account,
bản nháp/lịch sử. Hai kiểm thử mới đã xác nhận các dữ liệu này và chức năng
thử xác thực lại. Web và APK được build lại sau thay đổi này; không coi kết
quả nhận chữ trên Android giả lập là kiểm tra picker hoặc thiết bị vật lý.

AI thật còn chờ khóa được nhập trong cài đặt môi trường bảo mật hoặc công cụ
Windows. Chưa nghiệm thu chất lượng AI, ảnh viết tay/công thức/HEIC hoặc điện
thoại thật; ML Kit telemetry được công bố riêng trong bản nháp quyền riêng tư.

## Bản .18 — OCR miễn phí và chuẩn bị Google Play

- Backend + launcher: **185 đạt, 19 bỏ qua** (PostgreSQL yêu cầu DB riêng);
  toàn bộ Ruff đạt. Có hồi quy không còn endpoint AI, không tạo remote
  client dù cấu hình cũ bật, không đọc/xóa khóa/cấu hình cũ trong state.
- Flutter: **54 kiểm thử đạt**, analyzer không có lỗi. Sau sửa release R8,
  8 kiểm thử native OCR đạt lại, thêm xác nhận MethodChannel luôn script0
  Latin. Không dùng kết quả mô phỏng này để khẳng định máy thật.
- Tesseract thật Chromium đạt với PNG/JPEG/WebP; kiểm tra giới hạn, hủy,
  timeout và không request ngoài/không lưu ảnh đạt. Bộ 14 tệp OCR checksum đạt.
- ZIP Windows .18 giải nén, khởi động backend/gateway và browser thật: OCR
  picker tiếng Việt confidence95; sửa chữ bỏ xác nhận; nhập một ký tự5 không
  tự nộp; tự nộp/xem điểm không có nút/request AI. Mất API auth vẫn mở OCR,
  nhận ảnh thật, xác nhận/sao chép và giữ nguyên toàn bộ preference. Không
  ảnh trong POST, request ngoài origin hay lỗi JavaScript.
- Nâng cấp state thử .17: giữ nguyên từng dòng 32 tài khoản,17 liên kết
  attempt,13 kết quả,10 nhóm, các quan hệ thành viên/đề giáo viên/phiếu phản
  hồi. Đây là dữ liệu tổng hợp kiểm thử, không phải dữ liệu học viên thật.
- AAB release unsigned **build đạt** với thu gọn R8. Sửa quy trình tạo lại
  registrant theo release sau bước pub get --enforce-lockfile; 8 quy tắc
  R8 chỉ cho các lớp model ngôn ngữ tùy chọn không đóng gói. Không tắt R8.
  Gói 60.039.725 byte, SHA256
  `90acf53dcff465c6dea73a513b5bfcec7a8a5dbf3b91b146c058548a4c568baf`.
  Kiểm tra 10 ELF arm64/x86_64 có PT_LOAD>=16KB và BundleConfig yêu cầu
  PAGE_ALIGNMENT_16K. Chưa chạy runtime hệ điều hành16KB; gói không ký,
  không được coi là gói gửi Play. Lockfile không đổi sau build.
- APK Android debug ARM64 build đạt, versionCode18/minAPI24/target36,
  chữ ký AndroidDebug được apksigner xác minh và zipalign -P16 đạt.
  APK thử chưa có backend mặc định được triển khai; chức năng máy chủ cần
  URL HTTPS thật được cấu hình. OCR miễn phí hoạt động độc lập.
- Bộ 40 tài sản nhận diện được tái tạo ngoại tuyến và so byte/checksum đạt;
  đã xem icon48px và feature1024×500. Ảnh browser412×915 là ảnh web kiểm thử,
  không phải screenshot native được nghiệm thu cho Play.

Chưa có backend production/Play Console, khóa upload, quy trình trẻ em/giám
hộ đã duyệt, thẩm định nội dung toàn bộ hay thiết bị vật lý. Không gọi dịch
vụ AI thật trong bản này. Các quy trình CI được lưu cùng source .18; kết quả
từng run cần xem ở PR/checks đúng commit.
