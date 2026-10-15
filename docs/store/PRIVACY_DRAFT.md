# Bản nháp chính sách quyền riêng tư — Tự học 111

CHƯA CÔNG BỐ. Cần tên đơn vị phát hành, email hỗ trợ, URL chính sách và địa chỉ yêu cầu xóa dữ liệu thật.
Bản nháp này mô tả chức năng đang có, không thay thế việc xét duyệt pháp lý/chính sách cửa hàng.

Ứng dụng phục vụ học tập lớp 1–12 và quản lý nhóm học viên.
Khi đăng ký, hệ thống lưu tên đăng nhập, tên hiển thị, vai trò và lớp học nếu được chọn.
Mật khẩu được xử lý bằng scrypt với salt riêng; không lưu mật khẩu gốc.
Khi đăng nhập, phiên có thời hạn 8 giờ. Trên web dùng cookie HttpOnly/SameSite;
ứng dụng native hiện giữ token trong bộ nhớ. Chưa tích hợp SDK quảng cáo;
bản native .17 có SDK nhận chữ Google ML Kit với dữ liệu chẩn đoán được mô tả bên dưới.

Hệ thống lưu câu trả lời, điểm do backend chấm, thời điểm nộp, đề và chủ đề để hiển thị tiến độ.
Giáo viên xem kết quả học viên họ cấp tài khoản hoặc học viên tham gia nhóm bằng mã mời;
quản lý hệ thống có phạm vi quản lý rộng hơn. Vai trò giáo viên tự đăng ký chưa được xác minh nghề nghiệp.
Việc tham gia nhóm không cho giáo viên quyền đặt lại mật khẩu/xóa tài khoản tự đăng ký của học viên.

Khi báo lỗi nội dung, hệ thống lưu loại vấn đề, mô tả, mã nội dung, trích đoạn
lúc báo và thời gian; người xử lý lưu giải thích và trạng thái. Giáo viên đang
quản lý học viên/người quản lý hệ thống có thể xem theo phạm vi quyền. Không
gửi phiếu tới dịch vụ AI hoặc bên ngoài. Không nhập thông tin riêng tư vào phiếu.
Phiếu được giữ tới khi người gửi xóa tài khoản; khi người xử lý xóa tài khoản,
phần trả lời và định danh người đó trên phiếu của học viên được thay bằng ghi
chú hệ thống. Chưa có lịch tự xóa phản hồi theo thời gian.

Chế độ khách lưu bài làm/lịch sử trên thiết bị. Đăng nhập có dữ liệu trên backend đang cấu hình.
Bản local lưu SQLite trong thư mục state của máy chạy; chưa có dịch vụ cloud production vận hành.
Khi mở nguồn tham khảo ngoài, trình duyệt truy cập website bên thứ ba theo chính sách của họ;
việc này cần được xét lại cho chế độ trẻ em trước khi phát hành.

Trong bản web/demo Windows .17, nhận chữ ảnh bằng Tesseract chạy trong trình
duyệt. Worker, WebAssembly và dữ liệu tiếng Việt/Anh nằm trong gói; ảnh không
được gửi đến backend hoặc dịch vụ OCR bên ngoài. Ảnh được vẽ lại để bỏ metadata
EXIF/GPS trước khi xử lý/xem trước; không ghi ảnh vào localStorage/IndexedDB.
Ảnh và văn bản ở màn hình OCR chỉ giữ trong bộ nhớ, không tự lưu vào lịch sử.
Nếu người dùng chủ động dùng văn bản cho ô trả lời, văn bản đó được lưu/nộp
theo quy tắc bài làm thông thường.

Bản native Android/iOS .17 có chọn ảnh từ thư viện bằng image_picker và nhận
chữ trên thiết bị bằng Google ML Kit, không có nút chụp camera trong luồng này.
Ứng dụng yêu cầu Android 7.0/API 24 hoặc iOS 15.5 trở lên.
Ứng dụng kiểm tra và vẽ lại ảnh để bỏ EXIF/GPS rồi dùng một bản PNG tạm riêng;
bản tạm được dọn sau xử lý, ảnh gốc trong thư viện không bị xóa. Nếu hệ điều
hành dừng ứng dụng đột ngột, bản cache có thể còn tới khi hệ điều hành dọn.
Ảnh không được tải lên backend hoặc gửi trong nội dung yêu cầu AI. Việc hủy
chặn kết quả đến muộn hiển thị trên màn hình; không bảo đảm bộ native dừng xử
lý ngay. Văn bản vẫn cần người dùng sửa và xác nhận trước khi dùng cho bài làm.
Chưa có công cụ chụp/cắt ảnh trong ứng dụng.

Google công bố ML Kit có thể thu thập/gửi thông tin thiết bị, ứng dụng, mã
định danh theo lần cài đặt và thông tin chẩn đoán, hiệu năng, sử dụng API;
tùy API có thông tin định dạng, độ phân giải hoặc kích thước đầu vào/đầu ra.
Luồng OCR trên thiết bị không gửi nội dung ảnh để nhận dạng từ xa. Không vì
vậy mà khẳng định bản native không có kết nối hoặc dữ liệu gửi tới Google.
Chính sách, loại dữ liệu và cách khai SDK cần được đối chiếu lại với bản SDK
và ứng dụng gửi xét duyệt:

- Android: https://developers.google.com/ml-kit/android-data-disclosure
- iOS: https://developers.google.com/ml-kit/ios-data-disclosure

Mã nhận dạng theo lần cài đặt cần được đánh giá cùng quy trình xóa dữ liệu và
yêu cầu trẻ em; bản nháp này chưa xác nhận cơ sở xử lý hay đồng ý cần thiết
để dùng SDK với học sinh thật.

Trợ giảng AI mặc định tắt và hiện chưa có provider thật được cấu hình/đánh giá
cho người dùng. Bản .17 thêm công cụ cấu hình khóa riêng trên máy vận hành;
khóa không được đưa vào app native, web hoặc gói demo phát hành. Khi người
vận hành bật dịch vụ, người đăng nhập phải kiểm tra văn
bản và xác nhận gửi tới host nhà cung cấp được nêu trong mỗi yêu cầu. Hệ
thống gửi lớp, môn và văn bản đã sửa qua backend; ảnh và cookie/token đăng
nhập không nằm trong nội dung gửi AI. Với lựa chọn tham chiếu câu đã nộp, máy
chủ còn gửi đề gốc, lựa chọn, đáp án và lời giải đã lưu của câu đó. Hộp thoại
nêu rõ việc sửa ô văn bản không sửa tham chiếu; có thể tắt lựa chọn để chỉ gửi
văn bản đã kiểm tra. Tên hoặc thông tin riêng tư nằm trong nội dung vẫn có
thể bị gửi, vì vậy cần loại bỏ trước khi gửi và chọn chế độ phù hợp.

Phản hồi AI chỉ tham khảo, không thay đổi điểm hoặc đáp án. Ứng dụng không tự
lưu nội dung yêu cầu/phản hồi AI hay ảnh vào nhật ký AI. Nhật ký kỹ thuật giữ
ID tài khoản, thời điểm, model, trạng thái, số ký tự và số token của lượt thành
công; quota giữ bộ đếm. Chưa có lịch tự xóa/ẩn danh nhật ký AI. Điều khoản lưu
giữ, huấn luyện và bên xử lý dữ liệu của nhà cung cấp thật còn cần thẩm định;
không khẳng định provider không lưu dữ liệu chỉ vì app không lưu văn bản.
Xác nhận trên màn hình chưa thay thế quy trình người giám hộ cần thiết trước
khi dùng với trẻ em. Chi tiết kỹ thuật: [AI_OCR.md](../AI_OCR.md).

Hiện dữ liệu học tập được giữ tới khi người dùng hoặc quản lý xóa; chưa có thời hạn tự động xóa.
Người dùng tự đăng ký có thể xóa tài khoản và kết quả của mình trong Tài khoản bằng mật khẩu xác nhận.
Tài khoản/kết quả học viên do giáo viên cấp không bị xóa khi giáo viên xóa tài khoản.
Các bản đã chia sẻ trong kết quả học viên khác có thể được giữ như hồ sơ học tập của học viên đó.
Tài khoản quản lý hệ thống cần bàn giao trước khi xóa. Yêu cầu xóa qua website và xử lý backup
cần được thiết lập cùng đơn vị phát hành/backend thật; hiện chưa có kênh công khai đang vận hành.

Trước khi dùng với học sinh thật, cần chính sách đồng ý của phụ huynh/người giám hộ,
phạm vi chia sẻ, xác minh giáo viên và hướng dẫn quản lý tài khoản phù hợp tuổi.
Chưa tuyên bố đáp ứng đầy đủ mọi yêu cầu về dữ liệu trẻ em hoặc cửa hàng.
