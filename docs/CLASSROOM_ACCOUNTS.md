# Tài khoản và quản lý học viên — bản thử 2026.10.15.6

Bản local hỗ trợ học viên tự đăng ký hoặc người quản lý tạo hàng loạt tối đa 50 tài khoản mỗi lần. Tài khoản tự đăng ký được gắn với người quản lý của máy chủ. Không có chức năng tự đăng ký quyền quản lý.

## Bắt đầu trên Windows

1. Giải nén bản mới, chạy `start-demo.bat`.
2. Mở `state/TAI-KHOAN-QUAN-LY.txt` trên chính máy vừa chạy để lấy tài khoản `quanly` và mật khẩu ngẫu nhiên. Không gửi tệp này cho học viên hoặc đưa lên Git.
3. Vào Cá nhân > Tài khoản, đăng nhập và đổi mật khẩu tạm. Mật khẩu có ít nhất 10 ký tự.
4. Vào Quản lý học viên để tạo tài khoản hàng loạt, cấp lại mật khẩu, xem số bài, điểm trung bình và chi tiết từng bài. Mật khẩu cấp mới chỉ hiện một lần; học viên phải đổi khi đăng nhập lần đầu.

Người quản lý chỉ xem được học viên thuộc mình. Học viên xem kết quả của chính mình. Chấm điểm và lưu kết quả thực hiện trên backend; điểm do trình duyệt tự gửi không được sử dụng. Lịch sử thiết bị được tách theo tài khoản. Báo cáo chi tiết hiển thị tối đa 500 bài gần nhất; tổng số bài và điểm trung bình tính toàn bộ kết quả được lưu.

## Dùng chung và nâng cấp

Mỗi máy chạy một ZIP có cơ sở dữ liệu riêng. Để học viên ở máy/điện thoại khác đăng ký và người quản lý xem được kết quả, phải dùng **cùng một backend HTTPS**. Bản này hoàn thiện luồng tài khoản local, chưa triển khai máy chủ công khai hoặc Supabase production.

Trước khi nâng cấp, dừng bản cũ, sao lưu rồi chép **toàn bộ thư mục `state`** sang bản mới trước lần chạy đầu tiên. Giữ cùng địa chỉ/cổng để trình duyệt nhận lịch sử khách cũ. Không chép thư mục state của người khác.

Mật khẩu được băm bằng scrypt với muối riêng. Phiên hết hạn sau 8 giờ; web dùng cookie HttpOnly/SameSite Strict, ứng dụng native giữ token trong bộ nhớ. Đổi mật khẩu hủy các phiên khác, cấp lại mật khẩu hủy mọi phiên của học viên. Bộ giới hạn đăng nhập local chưa thay thế hạ tầng bảo vệ production.

Xóa lịch sử trên thiết bị không xóa báo cáo quản lý. Người quản lý có thể xóa tài khoản kèm bài làm/kết quả sau bước xác nhận; thao tác không có khôi phục tự động. Sao lưu cơ sở dữ liệu cần được bảo vệ vì chứa dữ liệu học viên.

## Tạo đề và dữ liệu

Chọn đồng thời tối đa 20 chủ đề, tạo 1–50 câu tùy ngân hàng. Số câu phải đủ để mỗi chủ đề được chọn có ít nhất một câu; hệ thống phân bổ luân phiên giữa các chủ đề. Các tên chủ đề trùng nghĩa được gộp và hiển thị có dấu.

Có thêm 731 câu Toán 5 tự biên soạn theo 43 nhóm kỹ năng. Tổng nguồn 2.641 câu; rút 1 câu cũ diễn đạt mơ hồ và thay bằng câu mới, còn 2.640 câu đang dùng. Có 306 đề cố định. Đây chưa phải dữ liệu SGK đầy đủ mọi môn/lớp; chưa có thẩm định chuyên môn độc lập.
