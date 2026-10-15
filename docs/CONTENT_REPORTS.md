# Báo lỗi và phản hồi nội dung — bản thử .14

Học viên đăng nhập trước khi mở đề. Trong câu hỏi đang làm hoặc sau khi nộp,
chọn **Báo lỗi nội dung**; trong tài liệu cũng có nút này. Chọn loại vấn đề,
mô tả từ 5–1.500 ký tự rồi gửi. Không gửi mật khẩu/thông tin riêng tư. Theo dõi
trạng thái và trả lời tại **Cá nhân → Tài khoản → Phản hồi của tôi**.

Giáo viên/quản lý mở **Xử lý phản hồi nội dung** trong màn hình tài khoản.
Giáo viên xem phản hồi của học sinh mình cấp tài khoản hoặc đang ở nhóm mình
sở hữu; người quản lý hệ thống xem học viên/giáo viên thuộc phạm vi quản lý.
Khi học sinh rời nhóm, giáo viên không còn quyền này nếu không phải người cấp
tài khoản. Nội dung báo lỗi và trích đoạn có thể được các giáo viên đang quản
lý học viên xem, tương tự quyền xem lịch sử học hiện có.

Chọn **Xem xét và trả lời**, ghi giải thích 5–2.000 ký tự và chọn Đang xem xét,
Đã xử lý hoặc Không cần sửa. Hai trạng thái cuối đóng phản hồi; không mở lại
phiếu cũ. Học viên có thể gửi phiếu mới sau khi phiếu trước đóng. Một nội dung
chỉ có một phiếu đang mở cho mỗi người, tối đa 20 phiếu/24 giờ. Hai người cùng
xử lý dùng revision: cập nhật cũ bị từ chối, cần tải lại danh sách.

Phản hồi **không sửa điểm, đáp án hoặc tài liệu**. Nếu xác nhận lỗi, người biên
tập phải sửa/duyệt lại nội dung theo công cụ quản trị hiện có; snapshot và điểm
bài đã làm vẫn giữ nguyên. Chưa có chấm lại thủ công, email hoặc thông báo đẩy.
Không coi phản hồi của giáo viên tự đăng ký là xác nhận chuyên môn của nhà xuất
bản. Bài làm khách phải được thực hiện lại khi đã đăng nhập để báo lỗi từ bài
làm thuộc tài khoản; không tự chuyển bài của khách sang tài khoản.

Tài khoản chỉ xem phiếu của chính mình; hộp xử lý kiểm tra quyền server. Câu
hỏi phải thuộc snapshot bài làm của người gửi; tài liệu phải đã xuất bản và xác
nhận quyền sử dụng. Phiếu giữ tên/trích đoạn lúc gửi, không giữ đáp án hay toàn
bộ câu trả lời. Xóa tài khoản xóa phiếu của người đó; nếu người xử lý xóa tài
khoản, phần trả lời và định danh người xử lý trong phiếu của người khác được
thay bằng ghi chú hệ thống. Bản xuất/sao lưu đã tạo trước đó vẫn cần được quản
lý theo quy trình xóa dữ liệu.

## Nâng cấp PostgreSQL

Schema lên **2**, thêm bảng `content_reports`. Trước khi nâng cấp, dừng nhận
truy cập và lịch backup, tạo bản backup đã kiểm tra. Dùng database owner chạy
`python -m khohoc.server_admin migrate`, rồi `grant-runtime`, sau đó khởi động
API mới. Migration 1 → 2 có thể chạy lặp, không thay bảng học viên/kết quả cũ;
API shared không tự chạy DDL. API mới từ chối schema 1 cho tới khi migration
hoàn tất. Không chạy lẫn worker cũ/mới trong lúc chuyển phiên bản. Xem
[SHARED_SERVER.md](SHARED_SERVER.md) cho môi trường/secret và lệnh cụ thể.

Công cụ backup đọc schema thực tế 1 hoặc 2 và ghi vào archive, khôi phục đối
chiếu version trong archive. Archive schema 1 cũ vẫn được giải mã/restore;
phải migrate và grant-runtime ở database khôi phục trước khi chạy API mới.
Chuyển SQLite v13 chưa có bảng phản hồi vẫn được hỗ trợ. Windows local tự thêm
bảng/version khi khởi động; **sao lưu và chép nguyên thư mục state trước khi
chạy bản mới**. Không hỗ trợ hạ phiên bản shared sau migration.
