# Bản nháp chính sách quyền riêng tư — Tự học 111

**Trạng thái: chưa công bố.** Phạm vi: bản 0.2.0+18, ngày 15/10/2026.
Tài liệu mô tả mã nguồn hiện tại để đơn vị phát hành hoàn thiện chính sách.
Không dùng tài liệu làm URL chính sách đã có hiệu lực khi các ô sau còn trống.

| Thông tin cần công bố | Giá trị hiện tại |
| --- | --- |
| Tên và địa chỉ đơn vị chịu trách nhiệm | CHƯA CÓ |
| Email hỗ trợ và yêu cầu về dữ liệu | CHƯA CÓ |
| URL chính sách công khai, truy cập không cần đăng nhập | CHƯA CÓ |
| URL yêu cầu xóa tài khoản ngoài ứng dụng | CHƯA CÓ |
| Máy chủ, đơn vị lưu trữ và khu vực xử lý dữ liệu | CHƯA CÓ backend production |
| Ngày chính sách có hiệu lực | CHƯA ẤN ĐỊNH |

## Dữ liệu tài khoản và học tập

Tự học 111 phục vụ luyện tập lớp 1–12 và quản lý nhóm học viên. Khi đăng ký,
ứng dụng gửi tên đăng nhập, tên hiển thị, mật khẩu, vai trò học sinh/giáo viên
và lớp nếu người dùng chọn đến máy chủ được cấu hình. Luồng đăng ký hiện
không yêu cầu email, số điện thoại, địa chỉ, ngày sinh hay vị trí thiết bị.
Mật khẩu được băm bằng scrypt với salt riêng; cơ sở dữ liệu không lưu mật
khẩu gốc. Máy chủ lưu mã tài khoản, quan hệ cấp tài khoản, nhóm và thành viên.

Khi làm bài, máy chủ lưu đề, câu trả lời, bản nháp khi đồng bộ, thời gian nộp
và kết quả để chấm bài, tiếp tục bài trên thiết bị khác và hiển thị tiến độ.
**Chế độ khách cũng dùng máy chủ để tạo và chấm bài.** Lịch sử và bài đang làm
còn được lưu trên thiết bị; chế độ khách không đồng nghĩa mọi dữ liệu chỉ ở
trên thiết bị. Phần luyện tập/tài liệu cần backend; riêng nhận chữ từ ảnh có
thể mở không cần tài khoản hay backend.

Phiên đăng nhập có thời hạn 8 giờ. Web dùng cookie HttpOnly/SameSite=Strict;
bản native giữ token đăng nhập trong bộ nhớ. Ứng dụng lưu lựa chọn máy chủ,
mã tài khoản đang dùng, tùy chọn, bài đang làm và lịch sử trên thiết bị. Đây
không phải kho lưu trữ được ứng dụng mã hóa riêng. Bản local dùng SQLite
trong thư mục `state`; cấu hình máy chủ dùng chung hỗ trợ PostgreSQL và HTTPS.
Chưa có máy chủ production đang vận hành để công bố đơn vị lưu trữ thật.

## Người có thể xem kết quả

Giáo viên xem kết quả của học viên họ cấp tài khoản và học viên thuộc nhóm
họ quản lý. Học viên tự đăng ký có thể tham gia bằng mã nhóm. Giáo viên không
được đặt lại mật khẩu/xóa tài khoản tự đăng ký chỉ vì học viên tham gia nhóm;
người cấp tài khoản và quản lý hệ thống có quyền quản lý tài khoản theo phạm
vi được cấp. Vai trò giáo viên tự đăng ký hiện chưa được xác minh nghề nghiệp.

Giáo viên có thể xuất bảng điểm nhóm: bản web tải CSV, bản native sao chép CSV
vào bộ nhớ tạm khi giáo viên chọn. Bản xuất sau đó nằm ngoài khả năng thu hồi
của ứng dụng. Không dùng mã nhóm hoặc chia sẻ CSV như cơ chế xác nhận đồng ý
của phụ huynh; quy trình này chưa được xây dựng.

## Phản hồi nội dung và nhật ký kỹ thuật

Khi gửi phản hồi, máy chủ lưu loại vấn đề, nội dung mô tả, mã nội dung, trích
đoạn và thời gian. Người xử lý lưu câu trả lời và trạng thái. Người gửi và
người quản lý có quyền theo phạm vi tài khoản/nhóm có thể xem phiếu. Không
nhập thông tin riêng tư không cần thiết vào phần mô tả.

Máy chủ có nhật ký hoạt động quản trị/tài khoản và bộ đếm chống lạm dụng.
Ở cấu hình dùng chung, thông tin kết nối được dùng để giới hạn yêu cầu; bộ
đếm cơ sở dữ liệu dùng khóa băm theo cửa sổ thời gian. Hạ tầng lưu trữ/proxy
thật có thể có nhật ký truy cập riêng. Chưa có lịch lưu giữ thống nhất cho
nhật ký ứng dụng, proxy và bản sao lưu để công bố cho người dùng.

## Nhận chữ từ ảnh

Bản 0.2.0+18 không tích hợp trợ giảng AI trả phí hay gửi yêu cầu đến nhà cung
cấp mô hình AI. Không cần khóa AI. Chức năng nhận chữ trên thiết bị được giữ
lại; bản hiện tại không có quảng cáo hay thanh toán trong ứng dụng.

Trong web/demo Windows, Tesseract xử lý ảnh trong trình duyệt. Worker,
WebAssembly và dữ liệu tiếng Việt/Anh nằm trong gói. Ứng dụng không gửi ảnh
đến backend/dịch vụ OCR từ xa và không ghi ảnh vào localStorage/IndexedDB.

Trên Android/iOS, người dùng chủ động chọn ảnh qua `image_picker`; ứng dụng
không có nút chụp camera trong luồng này. Google ML Kit nhận chữ trên thiết
bị. Ứng dụng yêu cầu Android 7.0/API 24 hoặc iOS 15.5 trở lên. Ảnh được kiểm
tra và vẽ lại để bỏ EXIF/GPS; bản PNG tạm riêng được dọn sau xử lý. Ảnh gốc
trong thư viện không bị xóa. Nếu hệ điều hành dừng ứng dụng đột ngột, bản
cache có thể còn tới khi hệ điều hành dọn. Chưa có công cụ chụp/cắt ảnh trong app.

Ảnh/văn bản của màn hình nhận chữ chỉ giữ trong bộ nhớ và không tự lưu vào
lịch sử. Người dùng cần sửa, kiểm tra và xác nhận văn bản trước khi dùng.
Khi chọn sao chép, văn bản được đưa vào bộ nhớ tạm hệ điều hành. Khi dùng
văn bản cho câu trả lời rồi lưu/nộp bài, văn bản đó được xử lý như câu trả
lời thông thường, bao gồm gửi đến máy chủ. Hủy thao tác ngăn kết quả muộn
hiển thị; không bảo đảm tác vụ nhận chữ native dừng ngay.

Google công bố ML Kit có thể gửi dữ liệu thiết bị, ứng dụng, mã định danh
theo lần cài đặt, chẩn đoán/hiệu năng và thông tin sử dụng API; tùy API có
định dạng, độ phân giải hoặc kích thước đầu vào/đầu ra. Xử lý OCR cục bộ không
đồng nghĩa SDK không có kết nối hay không thu thập dữ liệu chẩn đoán.
Không tuyên bố Google nhận nội dung ảnh để nhận dạng từ xa trong luồng này.
Đơn vị phát hành cần xác nhận phạm vi dữ liệu của đúng bản SDK gửi xét duyệt:

- Android: https://developers.google.com/ml-kit/android-data-disclosure
- iOS: https://developers.google.com/ml-kit/ios-data-disclosure
- Phiên bản và đối chiếu khai báo: [DATA_SAFETY_WORKSHEET.md](DATA_SAFETY_WORKSHEET.md).

## Lưu giữ và xóa

Tài khoản học sinh/giáo viên có thể tự xóa tại **Cá nhân → Tài khoản → Xóa tài
khoản**, nhập mật khẩu xác nhận rồi chọn **Xóa vĩnh viễn**. Máy chủ xóa tài
khoản, phiên, bản nháp/bài làm/kết quả thuộc tài khoản và phiếu do người đó
gửi. Khi người xử lý xóa tài khoản, phần phản hồi và định danh người đó trên
phiếu của người khác được thay bằng ghi chú hệ thống.

Xóa giáo viên không xóa tài khoản/kết quả của học viên. Nhóm và đề riêng của
giáo viên bị xóa; bản đề đã gắn với bài làm của học viên khác có thể còn trong
hồ sơ của học viên đó. Tài khoản quản lý hệ thống cần được bàn giao trước
khi xóa. Thao tác xóa trên thiết bị hiện tại không điều khiển bản dữ liệu đã
xuất, thiết bị khác hoặc bản sao lưu hạ tầng.

Xóa lịch sử trên thiết bị không xóa hồ sơ kết quả của lớp. Phiên/bài làm hết
hạn truy cập không đồng nghĩa dữ liệu đã được tự động xóa. Chưa có thời hạn
tự xóa chung cho hồ sơ học tập, nhật ký và backup; việc xử lý dữ liệu tồn dư
trong nhật ký/backup và yêu cầu từ người giám hộ cần được chốt trước khi
phát hành. Chưa có website/email công khai đang vận hành để yêu cầu xóa khi
không cài app; phải bổ sung kênh này trước khi gửi Google Play.

## Học sinh nhỏ tuổi và nguồn bên ngoài

Ứng dụng hướng tới lớp 1–12 nên có người dùng trẻ em. Hiện chưa có quy trình
đồng ý của người giám hộ, xác minh giáo viên hay cơ chế tuổi được thẩm định.
Đơn vị phát hành phải quyết định đối tượng tuổi thật và hoàn tất quy trình
phù hợp trước khi dùng với học sinh thật. Không tự khai ứng dụng chỉ dành
cho người lớn để tránh khai báo nhóm tuổi đang phục vụ.

Khi mở nguồn tham khảo ngoài, trình duyệt truy cập website bên thứ ba theo
chính sách của họ; website đó có thể có quảng cáo, đăng nhập hoặc nội dung
khác. Cần rà lại danh sách nguồn và luồng liên kết cho đối tượng trẻ em.

Các mục chưa hoàn tất ở trên là yêu cầu chuẩn bị phát hành, chưa phải cam
kết chính sách đã được triển khai. Hướng dẫn kiểm thử dành cho người duyệt:
[REVIEWER_GUIDE.md](REVIEWER_GUIDE.md).
