# Bảng điểm theo nhóm — bản thử .13

Đăng nhập giáo viên hoặc quản lý → Cá nhân → Quản lý học viên và kết quả →
Nhóm học viên → mở một nhóm → **Tải bảng điểm CSV** (web/Windows demo). Trên
app điện thoại, nút **Sao chép bảng điểm CSV** đưa nội dung vào clipboard;
dán vào tệp CSV hoặc công cụ nhập CSV của ứng dụng bảng tính. Chỉ chia sẻ tệp
với người được phép xem thông tin học viên.

Các cột: nhóm, tên đăng nhập, họ tên, lớp, số bài đã nộp, điểm trung bình (%),
thời gian nộp gần nhất (UTC). Trung bình là trung bình cộng phần trăm từng lần
nộp có điểm tối đa > 0, không cộng điểm thô của các đề có thang điểm khác nhau.
Chưa nộp bài: số bài 0, điểm và thời gian trống. Mỗi lần làm lại là một lần nộp.
Đây là toàn bộ kết quả mọi môn của thành viên hiện tại, kể cả trước khi tham
gia nhóm; không giới hạn 500 kết quả gần nhất như màn hình chi tiết. Học viên
rời nhóm sẽ không còn trong bản xuất mới. Bản CSV đã tải trước đó vẫn tồn tại
trên thiết bị giáo viên; xóa khi không còn cần thiết.

API: `GET /classroom/groups/{group_id}/results.csv`, đăng nhập bằng cookie hoặc
Bearer hiện có. Chỉ chủ nhóm được truy cập; giáo viên khác/quản lý không sở hữu
nhận 404, học sinh nhận 403, chưa đăng nhập nhận 401. Không sử dụng mã tham gia
nhóm làm quyền truy cập. UTF-8 BOM hỗ trợ Excel tiếng Việt; CSV writer xử lý dấu
phẩy/xuống dòng, và ô văn bản bắt đầu bằng ký tự công thức được thêm dấu nháy
đơn để tránh chạy công thức trong bảng tính. Header `Cache-Control: no-store`.

Chức năng không đổi schema, không sửa điểm đã nộp, không đưa mật khẩu, token,
câu trả lời hoặc mã tham gia nhóm vào tệp. Chưa có bảng hoàn thành theo từng
bài giao, lọc khoảng ngày hoặc ứng dụng native lưu tệp trực tiếp. Dùng chung
nhiều thiết bị vẫn cần một backend HTTPS được triển khai; Windows demo tiếp
tục chạy local.

Nâng cấp demo: dừng bản cũ, sao lưu và chép nguyên thư mục `state` sang thư mục
bản mới trước khi chạy. Giữ cùng cổng localhost để giữ lịch sử trình duyệt.
