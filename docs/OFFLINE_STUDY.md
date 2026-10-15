# Học trên thiết bị — bản .19

Bản .19 sửa trường hợp đã cài APK nhưng Trang chủ báo không tải được dữ
liệu vì chưa có máy chủ HTTPS. Ứng dụng đóng gói dữ liệu tự luyện để chọn
lớp/môn, đọc hướng dẫn, mở đề, lưu bài, nộp và xem kết quả ngay trên thiết bị.
Không cần tài khoản, khóa API hoặc tải thêm dữ liệu học để bắt đầu.

## Cách dùng

1. Cài đè APK .19 lên .18 từ bản phát hành của dự án; không gỡ app trước.
2. Mở app và kiểm tra thẻ **Học trên thiết bị** ở Trang chủ. Android chưa
   cấu hình backend HTTPS tự dùng chế độ này lần đầu. Nếu đang ở chế độ máy
   chủ, chọn **Chuyển sang học trên thiết bị**.
3. Chọn lớp, môn, mở đề hoặc tài liệu. Bài đang làm có thể tiếp tục sau khi
   đóng/mở app; nộp bài để xem kết quả và lời giải có trong dữ liệu.
4. Trong Cá nhân, dùng **Kết nối máy chủ lớp học** khi người quản lý đã cung
   cấp URL HTTPS thật để đăng nhập, dùng nhóm và đồng bộ bài trên máy chủ.

Web/Windows vẫn mặc định dùng API cùng máy chủ như trước; có thể chọn học
trên thiết bị. Thay đổi chế độ giữ riêng bài và lịch sử của mỗi chế độ.
Không chuyển một bài đang làm trên máy chủ thành bài ngoại tuyến hoặc ngược
lại. Một địa chỉ `.invalid` trong bản thử là chỗ giữ cấu hình, không phải
máy chủ đang hoạt động.

## Dữ liệu đã đóng gói

| Nội dung .19 | Số lượng / phạm vi |
| --- | --- |
| Câu hỏi đang dùng | 7.886 câu từ các fixture tự biên soạn của dự án |
| Đề luyện | 1.461 đề |
| Mục tài liệu/nguồn | 2.866 mục; không đồng nghĩa 2.866 bài hướng dẫn đầy đủ |
| Hướng dẫn Toán lớp 1–12 | 733 bài |
| Nguồn Internet, PDF | Có siêu dữ liệu/liên kết; không đóng gói toàn bộ PDF bên ngoài |

Dữ liệu nằm trong `apps/mobile/assets/offline/content.json`, được xuất bằng
`scripts/build_offline_bundle.py` từ danh sách fixture cố định, không từ cơ
sở dữ liệu người dùng. Không đọc tài khoản, biến môi trường, khóa hoặc trạng
thái máy chủ để tạo gói. Bộ câu đã thay thế không được đưa trở lại chỉ vì
còn trong fixture cũ.

Các nguồn tham khảo cần Internet khi mở trang ngoài; PDF không có trong gói
không thể đọc ngoại tuyến. Đề tự biên soạn gắn thẻ nguồn vẫn là đề tự biên
soạn, không được mô tả thành bản chép nguyên PDF. Hướng dẫn ngoài Toán và
mức độ bao phủ SGK còn thiếu; chưa có nghiệm thu chuyên môn toàn bộ nội dung.

## Kết quả và quyền riêng tư

Sáu dạng câu được xử lý tại thiết bị: một đáp án, nhiều đáp án, đúng/sai,
câu trả lời ngắn, số và tự luận. Các dạng có quy tắc xác định dùng cách chấm
tương ứng backend. **Tự luận để chờ đánh giá thủ công**, không tự cho điểm
hoặc khẳng định AI đã chấm. Kết quả tự luyện không phải điểm giáo viên giám
sát và không tự tải lên tài khoản khi chuyển sang chế độ máy chủ.

Bài làm, kết quả và lịch sử ngoại tuyến lưu riêng trong tùy chọn ứng dụng
trên thiết bị; ứng dụng không tự mã hóa kho này. Xóa bài trong Lịch sử sẽ
xóa bản tự luyện tương ứng tại thiết bị. Gỡ ứng dụng/xóa dữ liệu có thể làm
mất dữ liệu cục bộ; cài đè bản cùng mã ứng dụng/chứng thư giữ vùng dữ liệu
theo cơ chế Android. Không hứa đồng bộ hoặc khôi phục trên thiết bị khác.

Chế độ học với máy chủ dùng API để tạo và chấm bài, kể cả làm bài khách;
đăng nhập bổ sung đồng bộ theo tài khoản. Lịch sử máy chủ và lịch sử ngoại
tuyến được tách riêng. Không chấp nhận điểm tự gửi từ bản ngoại tuyến làm
điểm trên lớp.

**Đáp án được đóng gói để tự luyện.** Người có APK có thể trích xuất tài
liệu/đáp án. Không sử dụng ngân hàng này như đề bí mật hoặc kỳ thi có yêu
cầu chống gian lận. Đề đánh giá có giám sát cần ngân hàng câu hỏi riêng do
máy chủ giữ và chấm.

OCR vẫn nhận chữ trên thiết bị, không tải ảnh lên backend. Google ML Kit
native có thể gửi dữ liệu chẩn đoán tới Google theo công bố SDK; chọn chế
độ học trên thiết bị không tắt hành vi SDK. Mở liên kết ngoài cũng tạo kết
nối tới website nguồn. Xem [quyền riêng tư](store/PRIVACY_DRAFT.md) và
[Data Safety](store/DATA_SAFETY_WORKSHEET.md).

## Phạm vi phát hành

Bản .19 không tự tạo backend, tài khoản Play Console hoặc khóa ký phát
hành. APK debug để kiểm tra, chưa phải bản Google Play đã duyệt. Play
Protect có thể tiếp tục cảnh báo ứng dụng/nhà phát triển mới; không cần
tắt bảo vệ toàn cục. Trạng thái kiểm thử và điều kiện gửi cửa hàng ở
[RELEASE_STATUS.md](store/RELEASE_STATUS.md).
