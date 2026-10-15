# Tiến độ

Trạng thái mới nhất: bản thử **.18 / 0.2.0+18**. Các mốc bên dưới ghi lại tiến
độ từng bản; không coi hạn chế của một mốc cũ là trạng thái hiện hành. Xem phần
.18 cuối tài liệu và [OCR.md](OCR.md) cho phạm vi nhận chữ đang có.

## Giai đoạn 1
- Đã có: kiến trúc, schema, 108 câu hỏi gốc/12 đề, catalog lớp/môn, FastAPI chấm điểm xác định, quyền admin cục bộ, capability cho guest, snapshot bài, nhập/duyệt/xuất bản, Flutter luyện đề/lưu bài/lịch sử, Next.js admin; thư viện 4 ghi chú/PDF gốc, tìm kiếm tiếng Việt không dấu, yêu thích/đọc gần đây; đánh dấu câu và tiến độ thiết bị; sửa câu hỏi/rollback revision, duyệt lại và giữ nguyên snapshot bài đang làm.
- Cần hoàn thành trước nghiệm thu MVP toàn bộ: Supabase Auth/Storage và adapter schema production; rate limiting phân tán; kiểm thử Android thiết bị và AAB (APK debug đã build được); kiểm duyệt chuyên môn; policy/privacy cuối cùng.
- Database SQL có RLS được kiểm tra trên PostgreSQL local với shim auth.uid; không khẳng định đã triển khai Supabase hosted.

## Giai đoạn 2
Đã có OCR chữ in tiếng Việt/Anh cục bộ ở web/Windows và tích hợp ML Kit native
Android/iOS, xem trước/sửa/xác nhận văn bản, nhập văn bản vào câu tự luận và
trợ giảng AI trả phí ở .16/.17 đã được gỡ từ .18 theo yêu cầu chủ app.
Giữ OCR miễn phí; còn camera/cắt ảnh,
chấm tự luận theo rubric, báo lỗi/lưu phản hồi AI, đánh giá sư
phạm và quản lý chi phí; chưa hoàn tất giai đoạn này.

## Giai đoạn 3
Giáo viên/phụ huynh và liên kết có xác nhận; đồng bộ đa thiết bị; phân tích năng lực; mở rộng môn/lớp; cache nâng cao.

## Giai đoạn 4
JWT/server auth production, backup/retention, kiểm thử tải, Google Play policy mới nhất, signing bảo mật và kiểm thử kín. Chưa deploy hoặc xuất bản.


## Dữ liệu mở rộng 15/10/2026

Bản thử hiện có 1.566 câu, 219 đề và 199 tài liệu; có dữ liệu cho mọi tổ hợp lớp–môn trong danh mục. Đây là dữ liệu tự biên soạn hướng tới Kết nối tri thức, chưa đối chiếu toàn bộ SGK hiện hành. Xem `docs/CURRICULUM_EXPANSION.md` để phân biệt biến thể Toán, bộ ôn nền và phần còn thiếu.


### Thư viện Internet 15/10/2026

Bổ sung 1.934 mục nguồn Internet, tổng 2.133 tài liệu/liên kết; gồm 1.444 trang đề giữa/cuối kỳ KNTT và 104 mục tốt nghiệp dùng chung. Đây là liên kết nguồn, không phải PDF/câu hỏi của bên thứ ba được sao chép vào app. Chi tiết, quyền sử dụng và phần còn thiếu: `docs/INTERNET_LIBRARY.md`.


## Mốc bản thử 2026.10.15.6

- Ngân hàng: 2.640 câu đang dùng, 306 đề cố định; 75 bài Toán 5 đã gắn mục lục nguồn
  thứ cấp; 1.934 liên kết nguồn Internet. Chưa phủ đủ SGK mọi môn/lớp và
  chưa thẩm định chuyên môn độc lập.
- Hoàn tất module local mới: tạo đề 1–50 câu theo lớp/môn/chủ đề/bộ sách/độ
  khó; snapshot và chấm theo đáp án server; phân tích chủ đề từ lần làm mới
  nhất; ôn lại câu chưa đúng, tính lại thống kê sau khi sửa/xóa kết quả.
- Đã sửa khôi phục phiên cũ và cache giao diện ở bản .4. Đề kiểm tra ở Luyện
  đề; Tài liệu giữ điều kiện gắn đúng bài SGK và đủ phần hướng dẫn/luyện tập.
- Giai đoạn 1 còn: kiểm thử thiết bị Android thật, hoàn thiện quản trị bộ đề,
  báo lỗi nội dung/xem xét lại bài, kiểm duyệt sư phạm, chính sách cuối cùng.
- Giai đoạn 2 chưa hoàn tất: chưa có AI provider, nhận dạng ảnh/OCR, quota,
  consent và chấm tự luận được tích hợp. Không tự sinh điểm AI giả.
- Chức năng tạo đề/phân tích local là một phần nền tảng cho giai đoạn 3;
  đã có đăng ký học viên, tạo hàng loạt và báo cáo quản lý qua backend local.
  Chưa triển khai backend HTTPS dùng chung hoặc liên kết phụ huynh.
- Production còn: Supabase Auth/Storage, adapter dữ liệu, JWT/server roles,
  hạ tầng backup/retention, kiểm thử tải, domain/backend thật, ký AAB và các
  bước Google Play. Không yêu cầu secret trong chat hoặc tự mua dịch vụ.

Chi tiết module: [LOCAL_STUDY_MODULE.md](LOCAL_STUDY_MODULE.md).

Chi tiết tài khoản bản .6: [CLASSROOM_ACCOUNTS.md](CLASSROOM_ACCOUNTS.md).

## Bản thử 2026.10.15.7

Hoàn thiện cách trình bày 139 ví dụ và 278 lời giải trong 75 bài Toán 5: kiến thức bằng lời, cách làm từng bước, câu lời giải/phép tính/đơn vị và Đáp số; hiển thị đặt tính giữ cột. Không tăng số bài SGK được ánh xạ và chưa xác minh nguyên mẫu toàn bộ SGK. Xem [TEXTBOOK_LESSONS.md](TEXTBOOK_LESSONS.md).

## Bản thử 2026.10.15.8

Bổ sung 267 bài hướng dẫn Toán 1–4 vào các mục nguồn đã ghi nhận; tổng Toán 1–5 là 342 hướng dẫn. Có thêm 476 ví dụ và 952 bài tự luyện kèm lời giải, đáp số; chưa phải câu mới chấm tự động. Mục lục vẫn có chỗ thiếu và các môn/lớp khác còn cần soạn. Xem [PRIMARY_MATH_GUIDES.md](PRIMARY_MATH_GUIDES.md).

## Bản thử 2026.10.15.9

Sửa đọc mục lục Toán 6–12, thêm 391 hướng dẫn gồm 230 bài đánh số, 610 ví dụ và 1.220 bài luyện có lời giải. Tổng Toán 1–12 là 733 mục có hướng dẫn theo dữ liệu nguồn. Không khẳng định đầy đủ mọi dạng bài/trang/ấn bản; các môn ngoài Toán còn thiếu. Xem [SECONDARY_MATH_GUIDES.md](SECONDARY_MATH_GUIDES.md).

## Bản thử 2026.10.15.10–11 — Tự học 111

Đã có vai trò học sinh/giáo viên, nhóm, giao đề và báo cáo; thêm ngân hàng câu hỏi, sửa mệnh đề thừa bằng phiên bản mới. 991 thẻ nguồn mở đề tự biên soạn cùng lớp/môn; 525 nguồn còn thiếu câu và chưa nhập nguyên văn. Android engineering AAB, khung iOS, tự xóa tài khoản và bản nháp chính sách đã chuẩn bị. Còn tài khoản cửa hàng, backend HTTPS production, thẩm định nội dung/trẻ em, tài sản thương hiệu và kiểm thử thiết bị/ký để phát hành. Xem [trạng thái cửa hàng](store/RELEASE_STATUS.md).

## Bước tiếp theo — phục hồi dữ liệu local

Đã thêm công cụ sao lưu SQLite nhất quán và mã hóa AES-256-GCM, khôi phục vào
đường dẫn mới, kiểm tra toàn vẹn và từ chối ghi đè. Có kiểm thử dữ liệu WAL,
sai khóa/tệp bị sửa và đăng nhập học viên từ database khôi phục.
Xem [hướng dẫn sao lưu](BACKUP_RECOVERY.md). Chưa triển khai backend HTTPS,
PostgreSQL production, lịch sao lưu hay lưu trữ ngoài máy chủ; không thay đổi
trạng thái sẵn sàng xuất bản cửa hàng.

## Bản 2026.10.15.12 — pilot máy chủ dùng chung

Đã có PostgreSQL 17, migration baseline offline, chuyển dữ liệu SQLite vào
PostgreSQL trống (không chuyển session), tài khoản DB hạn chế quyền, cấu hình
Docker/Caddy HTTPS và rate limit dùng database. Bổ sung danh sách bài đang làm,
bản nháp theo tài khoản, tiếp tục trên thiết bị khác và kiểm tra revision khi
lưu/nộp để tránh ghi đè. Mất mạng giữ câu trả lời local; yêu thích/đánh dấu câu
chưa đồng bộ. Xem [hướng dẫn máy chủ dùng chung](SHARED_SERVER.md).

Đã kiểm thử PostgreSQL thật và HTTPS nội bộ bằng CA được xác minh; chưa có máy
chủ/tên miền Internet của người dùng được triển khai. `shared` là pilot có kiểm
soát; chế độ phát hành `production` vẫn bị khóa. Còn sao lưu PostgreSQL tự động,
giám sát/retention, thẩm định nội dung và quyền riêng tư, kiểm thử thiết bị thật
và tài khoản/ký cửa hàng. Không coi volume database là bản sao lưu.

## Vận hành PostgreSQL sau bản .12

Bổ sung archive AES-256-GCM dạng luồng, khóa chống job chồng, trạng thái backup,
retention có kiểm tra (giữ ít nhất hai bản hợp lệ) và khôi phục vào database mới
`recovery_*`, thu hồi session trong bản khôi phục. Nguồn backup tự đọc cấu hình
API, tránh sao lưu nhầm database cũ sau khi chuyển sang bản phục hồi.

Có `/ready` kiểm tra schema, trả 503 khi DB/schema chưa sẵn sàng; hạn thời gian
truy vấn/kết nối PostgreSQL, monitor HTTPS và unit systemd backup hàng ngày/
kiểm tra mỗi 5 phút. Đã kiểm thử restore PostgreSQL thật và luồng HTTPS mất DB,
phục hồi dữ liệu, đăng nhập lại. [Runbook vận hành](POSTGRES_OPERATIONS.md).

Chưa cài lịch trên máy chủ Internet, chưa cấu hình offsite/nhà cung cấp cảnh báo
hoặc đối soát yêu cầu xóa sau snapshot. Không thay đổi trạng thái phát hành cửa
hàng, không mở khóa production và không yêu cầu tải lại ZIP Windows cho phần này.

## Bản thử .13 — báo cáo kết quả nhóm

Giáo viên/quản lý xuất CSV nhóm mình sở hữu từ màn hình Nhóm học viên. Bảng dùng
điểm đã chấm trên máy chủ, gồm cả thành viên chưa nộp bài, trung bình phần trăm
mọi môn/mọi lần nộp và thời gian nộp gần nhất (UTC). Thành viên hiện tại được
thống kê toàn bộ lịch sử được phép xem, không riêng đề giao cho nhóm. Không
phải bảng theo dõi hoàn thành từng bài giao hoặc sổ điểm chính thức.

Web tải tệp UTF-8 có BOM; app điện thoại sao chép CSV vào clipboard để lưu bằng
ứng dụng bảng tính. Kiểm tra sở hữu ở backend, không đưa mã phiên vào liên kết;
tệp không có mật khẩu, lời giải hay đáp án học viên. Xem CLASSROOM_REPORTS.md.
Backend Internet, thiết bị thật, nội dung thẩm định và ký/phát hành cửa hàng
vẫn chưa hoàn tất.

## Bản thử .14 — báo lỗi và xem xét phản hồi

Bổ sung báo lỗi câu hỏi trong bài thuộc tài khoản và tài liệu đã xuất bản; danh
sách riêng của người gửi, hộp xử lý cho giáo viên/quản lý theo phạm vi học viên,
chống trùng/quota và revision chống ghi đè. Không tự sửa điểm hay xác nhận lại
nội dung SGK. Schema 2 có migration bổ sung từ 1, hỗ trợ chuyển SQLite cũ và
backup/restore PostgreSQL schema 1–2. Sửa lớp lọc preview local để cho phép
danh sách/khôi phục/lưu bản nháp theo tài khoản đi qua; gateway ngoài đã có
nhưng lớp preview bên trong còn chặn ở bản .13. Xem CONTENT_REPORTS.md.

Checklist kiểm tra toàn bộ bản thử: EVENING_CHECKLIST.md. Còn nội dung chuyên
môn, chấm lại, AI/OCR, thiết bị thật và triển khai/phát hành; chưa hoàn tất toàn
bộ kế hoạch hoặc vận hành production.

## Bản thử .15 — giao bài và tiến độ theo đề

Giáo viên giao bản sao riêng của đề có sẵn cho nhóm, xem tiến độ/thành viên chưa
nộp và CSV riêng từng đề. Đề tạo theo chủ đề có nhóm cũng được thống kê. Học viên
có Bài được giao, tiếp tục bản nháp cùng mã đề và chỉ thấy kết quả của mình.
Dùng TeacherExam hiện có, không đổi schema 2. Sửa thời hạn bản nháp đồng nhất
24 giờ với nộp bài, không để 100 bài đã hoàn thành che mất bài đang làm và hỗ
trợ nộp dữ liệu legacy JSON null. Xem GROUP_ASSIGNMENTS.md.

Chưa có hạn giao bài/thông báo đẩy, chấm lại thủ công, AI/OCR hoặc liên kết phụ
huynh. Nội dung chuyên môn và triển khai production/thiết bị/cửa hàng vẫn còn;
không coi .15 là hoàn tất toàn bộ kế hoạch.

## Bản thử .16 — nhận chữ cục bộ và nền tảng trợ giảng AI

OCR Tesseract chạy trong trình duyệt, kèm worker/core và dữ liệu tiếng Việt/Anh
đã ghim phiên bản, giấy phép/checksum. Có xem trước, sửa và xác nhận trước khi
đưa văn bản vào ô tự luận; ảnh không tải lên máy chủ. Đã chạy nhận chữ thật
bằng Chromium và kiểm tra không gọi URL ngoài. Bản native chưa nhận chữ từ
ảnh, vẫn nhập/dán văn bản được. Chưa có công cụ cắt ảnh trong app.

Backend có trợ giảng văn bản theo tài khoản, chỉ gọi khi cấu hình provider và
người dùng xác nhận gửi tới đúng host. Có tham chiếu tùy chọn từ câu đã nộp
thuộc tài khoản; hộp thoại nói rõ gửi thêm đề/lựa chọn/đáp án/lời giải đã lưu,
hoặc chọn chỉ gửi văn bản đã sửa. Khóa nằm trong tệp riêng của backend; quota
database, hạn kích thước/thời gian, kiểm tra phản hồi và nhật ký metadata/số
token. Hướng dẫn luôn tham khảo, không thay đổi điểm hoặc đáp án.

AI vẫn tắt mặc định; kiểm thử provider mô phỏng không chứng minh chất lượng
mô hình thật. Còn chấm rubric, báo lỗi/xem xét phản hồi AI, nhập đề OCR có
người duyệt, chi phí, retention và chính sách trẻ em/nhà cung cấp. Không tăng
phạm vi dữ liệu đã thẩm định SGK. Backend Internet, thiết bị thật và ký/phát
hành cửa hàng vẫn chưa hoàn tất. Xem [AI_OCR.md](AI_OCR.md).

## Bản .17 — OCR native và cấu hình AI thật

Đã thêm OCR ảnh thư viện trên Android 7.0/API 24+ và iOS15.5+, chuẩn hóa ảnh
bỏ metadata, xem trước/sửa/xác nhận, hủy kết quả muộn và dọn cache tạm. Android
APK debug và iOS unsigned engineering đã build đạt. Kiểm thử ML Kit thật trên
Android emulator đọc được chữ in tiếng Việt khi Wi-Fi/dữ liệu di động tắt;
chưa nghiệm thu picker/quyền/chất lượng trên điện thoại vật lý hoặc OCR iOS
runtime. ML Kit có dữ liệu chẩn đoán SDK; không coi native hoàn toàn không có
lưu lượng mạng. OCR web/Windows tiếp tục dùng Tesseract local.

Có configure-ai.bat nhập khóa ẩn, tệp cấu hình/khóa riêng và hỗ trợ secret từ
môi trường. Đã kiểm tra cấu hình được launcher/backend tiếp nhận bằng khóa
synthetic, không gọi nhà cung cấp. Đã chuẩn bị yêu cầu bí mật trong cấu hình
cloud; chưa được cung cấp khóa thật nên chưa bật/đánh giá AI thật. Xem
[AI_ACTIVATION.md](AI_ACTIVATION.md). Còn camera/cắt ảnh, HEIC, chấm tự luận,
đánh giá mô hình, backend HTTPS của chủ app, ký/kiểm thử/phát hành cửa hàng.

## Bản .18 — giữ OCR miễn phí, chuẩn bị Google Play

Theo yêu cầu chủ app, đã tạm gỡ trợ lý AI trả phí khỏi giao diện, API, proxy,
launcher và công cụ cấu hình khóa. Cấu hình/khóa cũ không thể kích hoạt lại
provider và được giữ nguyên trong thư mục riêng của người vận hành. OCR web/
Windows/native tiếp tục hoạt động, không cần khóa; không thêm phí dịch vụ OCR.

Thay biểu tượng Flutter mặc định bằng bộ nhận diện Tự học 111: Android adaptive/
monochrome, iOS/web và icon512/feature1024×500 cho cửa hàng. Chuẩn bị Data Safety,
chính sách và luồng reviewer đúng với dữ liệu tài khoản/bài khách/ML Kit.

Preflight có nhánh AAB unsigned engineering không đọc khóa ký, kiểm thư viện
64-bit và cấu hình căn16KB; nhánh phát hành kiểm HTTPS/health/ready/metadata/
ký upload và các xác nhận đã duyệt. Không coi engineering AAB là gói upload.

Còn adapter production/backend HTTPS thật, Play Console/khóa ký, quy trình trẻ
em/xác minh giáo viên, thẩm định nội dung, thiết bị vật lý/screenshot native và
kiểm thử kín. Không mua/triển khai/phát hành cửa hàng trong mốc này. Xem
[Google Play checklist](PLAY_STORE_CHECKLIST.md) và [xác minh](VALIDATION.md).
