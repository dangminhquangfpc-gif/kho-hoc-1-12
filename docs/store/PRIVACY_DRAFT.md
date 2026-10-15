# Bản nháp chính sách quyền riêng tư — Tự học 111

CHƯA CÔNG BỐ. Cần tên đơn vị phát hành, email hỗ trợ, URL chính sách và địa chỉ yêu cầu xóa dữ liệu thật.
Bản nháp này mô tả chức năng đang có, không thay thế việc xét duyệt pháp lý/chính sách cửa hàng.

Ứng dụng phục vụ học tập lớp 1–12 và quản lý nhóm học viên.
Khi đăng ký, hệ thống lưu tên đăng nhập, tên hiển thị, vai trò và lớp học nếu được chọn.
Mật khẩu được xử lý bằng scrypt với salt riêng; không lưu mật khẩu gốc.
Khi đăng nhập, phiên có thời hạn 8 giờ. Trên web dùng cookie HttpOnly/SameSite;
ứng dụng native hiện giữ token trong bộ nhớ, không có SDK quảng cáo/analytics bên thứ ba được tích hợp.

Hệ thống lưu câu trả lời, điểm do backend chấm, thời điểm nộp, đề và chủ đề để hiển thị tiến độ.
Giáo viên xem kết quả học viên họ cấp tài khoản hoặc học viên tham gia nhóm bằng mã mời;
quản lý hệ thống có phạm vi quản lý rộng hơn. Vai trò giáo viên tự đăng ký chưa được xác minh nghề nghiệp.
Việc tham gia nhóm không cho giáo viên quyền đặt lại mật khẩu/xóa tài khoản tự đăng ký của học viên.

Chế độ khách lưu bài làm/lịch sử trên thiết bị. Đăng nhập có dữ liệu trên backend đang cấu hình.
Bản local lưu SQLite trong thư mục state của máy chạy; chưa có dịch vụ cloud production vận hành.
Không gửi bài tới dịch vụ AI/OCR; các dịch vụ đó chưa được tích hợp hoạt động.
Khi mở nguồn tham khảo ngoài, trình duyệt truy cập website bên thứ ba theo chính sách của họ;
việc này cần được xét lại cho chế độ trẻ em trước khi phát hành.

Hiện dữ liệu học tập được giữ tới khi người dùng hoặc quản lý xóa; chưa có thời hạn tự động xóa.
Người dùng tự đăng ký có thể xóa tài khoản và kết quả của mình trong Tài khoản bằng mật khẩu xác nhận.
Tài khoản/kết quả học viên do giáo viên cấp không bị xóa khi giáo viên xóa tài khoản.
Các bản đã chia sẻ trong kết quả học viên khác có thể được giữ như hồ sơ học tập của học viên đó.
Tài khoản quản lý hệ thống cần bàn giao trước khi xóa. Yêu cầu xóa qua website và xử lý backup
cần được thiết lập cùng đơn vị phát hành/backend thật; hiện chưa có kênh công khai đang vận hành.

Trước khi dùng với học sinh thật, cần chính sách đồng ý của phụ huynh/người giám hộ,
phạm vi chia sẻ, xác minh giáo viên và hướng dẫn quản lý tài khoản phù hợp tuổi.
Chưa tuyên bố đáp ứng đầy đủ mọi yêu cầu về dữ liệu trẻ em hoặc cửa hàng.
