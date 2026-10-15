# Hướng dẫn kiểm tra Google Play — Tự học 111

Phạm vi: 0.2.0+18. Tài liệu dành cho chuẩn bị nội bộ và trường App access
trong Play Console sau khi có backend HTTPS thật. Hiện chưa có tài khoản
reviewer hay máy chủ production để người duyệt đăng nhập; không gửi thông tin
mẫu bên dưới như tài khoản có thể dùng. Không đưa tài khoản học sinh thật,
khóa AI, token quản trị hoặc khóa ký vào gói xét duyệt.

## Phiếu bàn giao trước khi gửi

| Mục | Điền sau khi kiểm tra thật |
| --- | --- |
| AAB/versionCode/SHA-256 | CHƯA ĐIỀN; bản engineering/debug không thay bản upload đã ký |
| Backend HTTPS và thời gian duy trì cho reviewer | CHƯA CÓ |
| Email hỗ trợ | CHƯA CÓ |
| Privacy Policy URL / URL yêu cầu xóa ngoài app | CHƯA CÓ |
| Tài khoản giáo viên và mật khẩu | Cấp riêng trong App access; dữ liệu giả lập |
| Tài khoản học sinh và mật khẩu | Cấp riêng trong App access; dữ liệu giả lập |
| Nhóm mẫu / mã tham gia / đề được giao | Tạo trên đúng backend reviewer |
| Người chịu trách nhiệm khôi phục dữ liệu demo | CHƯA CÓ |

Mỗi tài khoản mẫu cần mật khẩu riêng ít nhất 10 ký tự, đã vượt bước đổi mật
khẩu bắt buộc nếu được cấp hàng loạt, không có OTP hoặc giới hạn truy cập
theo mạng của người phát triển. Luồng hiện không dùng OTP; không tự mô tả có
email xác minh. Đăng ký giáo viên/học sinh dùng tên đăng nhập; email không
phải trường bắt buộc. Không hướng reviewer tới localhost hoặc IP nội bộ.

## Tạo dữ liệu tổng hợp cho bản kiểm tra

1. Trên backend dành cho xét duyệt, đăng ký một giáo viên mẫu và hai học sinh
   mẫu; dùng tên giả rõ ràng, không nhập ngày sinh/địa chỉ học sinh thật.
2. Giáo viên vào Cá nhân → Tài khoản → Quản lý học viên và kết quả, tạo
   nhóm; học sinh tự đăng ký tham gia bằng mã. Thêm một học viên do giáo viên
   cấp để kiểm tra luồng đặt lại mật khẩu của tài khoản được cấp.
3. Chọn lớp/môn có dữ liệu đã rà; giáo viên tạo đề từ ít nhất hai chủ đề rồi
   giao cho nhóm. Duy trì một bài chưa làm, một bài đang làm, một bài đã nộp.
4. Cung cấp tài khoản riêng dùng kiểm tra xóa để không xóa tài khoản reviewer
   chính. Chuẩn bị cách tạo lại dữ liệu sau khi reviewer kiểm tra.
5. Kiểm tra các bước bên dưới trên đúng AAB đã ký và thiết bị Android thật;
   lưu kết quả, phiên bản thiết bị và lỗi còn lại vào hồ sơ phát hành.

## Luồng chức năng cần kiểm tra

| Bước | Thao tác | Kết quả cần quan sát |
| --- | --- | --- |
| Mở app | Mở bản cài mới với backend HTTPS đã cấu hình | Màn hình đọc được, không bắt nhập khóa dịch vụ; không có mục trợ giảng AI |
| Chọn nội dung | Chọn lớp/môn, mở tài liệu, luyện đề | Nội dung thật có thể đọc/làm; tài liệu nêu phạm vi, không hứa phủ hết SGK |
| Làm bài khách | Bắt đầu, nhập câu trả lời, tiếp tục bài đã lưu, nộp | Chấm trên backend; kết quả và lời giải hiển thị; không kẹt nút nộp |
| Đăng ký học sinh | Cá nhân → Tài khoản → Đăng ký, chọn Học sinh | Đăng nhập được; không được tạo đề giáo viên |
| Học sinh vào nhóm | Nhập mã nhóm mẫu, mở Bài được giao | Chỉ thấy nội dung được phép, làm và nộp bài giao được |
| Giáo viên | Đăng nhập tài khoản giáo viên, chọn nhiều chủ đề khi tạo đề | Tạo/giao đề, quản lý đúng nhóm của mình; không thấy lớp giáo viên khác |
| Cấp tài khoản | Giáo viên cấp học viên mẫu; học viên đăng nhập | Có bước đổi mật khẩu tạm, không cấp quyền giáo viên cho học viên |
| Theo dõi | Học sinh nộp; giáo viên làm mới nhóm/bài giao | Kết quả lấy từ máy chủ, chỉ đúng học viên thuộc phạm vi; CSV dùng dữ liệu giả |
| Đồng bộ | Cùng tài khoản trên hai thiết bị, lưu rồi mở lại bản máy chủ | Có thể tiếp tục bài; thay đổi xung đột không âm thầm ghi đè bài đã nộp |
| Báo lỗi | Gửi phiếu lỗi ở câu hỏi/tài liệu | Người gửi thấy phiếu; giáo viên có quyền xử lý theo phạm vi, không thay điểm bài cũ |
| Xóa tài khoản | Dùng tài khoản xóa riêng, Cá nhân → Tài khoản → Xóa tài khoản, nhập mật khẩu → Xóa vĩnh viễn | Tài khoản/phiên/kết quả thuộc tài khoản bị xóa; kiểm tra đăng nhập cũ và thiết bị thứ hai |
| Lỗi mạng | Ngắt backend khi đang dùng; mở Nhận chữ từ ảnh trên thiết bị | Thông báo và thử lại rõ ràng; OCR độc lập mở được, không làm mất bản bài đang lưu |

## Nhận chữ từ ảnh

Vào Cá nhân → Nhận chữ từ ảnh hoặc nút Nhập từ ảnh hoặc văn bản của
câu có ô nhập. Chọn ảnh PNG/JPEG/WebP rõ chữ in tiếng Việt/Anh qua bộ chọn ảnh
hệ điều hành. Ảnh tối đa 8 MiB và 16 triệu điểm ảnh; HEIC chưa hỗ trợ. Ứng
dụng chưa có luồng chụp ảnh camera hoặc cắt ảnh.

Kiểm tra văn bản, sửa nếu cần, chọn xác nhận đã kiểm tra rồi dùng văn bản hoặc
sao chép. Sửa tiếp phải xác nhận lại; hủy không nộp bài. Văn bản được chèn vào
ô trả lời, người dùng vẫn tự chọn Nộp bài. Không có lời giải AI trả phí và
không có màn hình yêu cầu khóa. Chữ viết tay, phân số, số mũ và hình vẽ có thể
đọc sai. Trên native, Google ML Kit nhận chữ cục bộ nhưng có công bố dữ liệu
chẩn đoán; xem chính sách và [Data Safety](DATA_SAFETY_WORKSHEET.md).

Cần kiểm tra thực tế quyền chọn ảnh, hủy picker, quay lại app, xoay màn hình,
bộ nhớ thấp và tiếng Việt trên thiết bị Android; bài integration test không
thay thế toàn bộ luồng picker hệ điều hành. Không yêu cầu quyền truy cập tất
cả ảnh/camera để thực hiện ca chọn một ảnh.

## Trước khi cung cấp App access

- Backend phải hoạt động từ mạng ngoài, chứng chỉ HTTPS hợp lệ, có dữ liệu
  mẫu và không còn chặn chế độ production vì thành phần chưa hoàn tất.
- Mật khẩu reviewer được gửi qua trường riêng của Play Console; không ghi
  mật khẩu dùng thật vào repository, ZIP hay trang hỗ trợ công khai.
- Chính sách quyền riêng tư và kênh yêu cầu xóa phải mở được không cần cài app
  hoặc đăng nhập. Yêu cầu xóa cần có người xử lý và thời hạn công bố thật.
- Hoàn thành quyết định nhóm tuổi, quy trình người giám hộ/xác minh giáo viên,
  rà website ngoài và thẩm định nội dung. Hiện chưa có các xác nhận này.
- Khai Data Safety theo backend/SDK thật, không suy ra “không thu thập dữ liệu”
  chỉ vì đã bỏ trợ giảng AI hoặc ảnh OCR được xử lý cục bộ.

Chỉ chuyển tài liệu này thành hướng dẫn gửi reviewer sau khi các mục CHƯA CÓ
được thay bằng dữ liệu thật và các luồng đã được kiểm tra trên bản upload.
