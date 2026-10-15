# Kiểm tra bản thử .14 tối nay

Dừng bản cũ → sao lưu `state` → giải nén bản .14 → chép nguyên `state` vào bản
mới → chạy `start-demo.bat`. Giữ cùng cổng localhost để giữ dữ liệu trình duyệt.
Không xóa dữ liệu cũ khi gặp lỗi; lưu nội dung thông báo và bước tái hiện.

1. Đăng nhập tài khoản cũ; kiểm tra nhóm, lịch sử và điểm cũ còn nguyên.
2. Đăng ký học sinh: làm được đề có sẵn, không tạo đề hoặc quản lý nhóm.
3. Đăng ký giáo viên: tạo nhóm, cấp tài khoản hàng loạt; học sinh đổi mật khẩu
   tạm, tham gia bằng mã nhóm. Thử thêm tài khoản giáo viên đã cấp vào nhóm.
4. Giáo viên tạo đề với nhiều chủ đề, giao cho nhóm. Tài khoản ngoài nhóm không
   được mở đề riêng. Thử các lớp/môn bạn đang dạy để ghi nhận câu còn thiếu.
5. Làm bài, chuyển câu, thoát/mở lại, nộp và kiểm tra lời giải. Thử tiếp tục bài
   từ danh sách bài đang làm; không nộp từ hai bản cũ khi được báo xung đột.
6. Mở tài liệu theo lớp/môn/bài, kiểm tra kiến thức, cách làm, lời giải và đáp
   số. Gửi **Báo lỗi nội dung** nếu có sai/thiếu, ghi đúng bài và bước cần sửa.
7. Báo lỗi một câu đang làm hoặc đã nộp; vào Phản hồi của tôi. Giáo viên mở Xử
   lý phản hồi nội dung, trả lời; học viên tải lại và xem trả lời. Kiểm tra
   điểm cũ không tự thay đổi sau phản hồi.
8. Giáo viên mở nhóm, tải CSV. Kiểm tra tiếng Việt, học viên chưa nộp có điểm
   trống, số bài/điểm trung bình phù hợp. CSV tính mọi môn/mọi lần làm của thành
   viên hiện tại, không riêng đề giáo viên giao.
9. Thử đăng xuất/đăng nhập tài khoản khác: không thấy bài đang làm, phiếu phản
   hồi hoặc nhóm riêng của tài khoản trước. Thử tìm kiếm tiếng Việt có/không dấu.
10. Trên tài khoản thử riêng, đổi mật khẩu và tự xóa tài khoản; không thử xóa
    tài khoản/dữ liệu bạn muốn giữ. Kiểm tra phiên cũ không đăng nhập được nữa.

Windows demo dùng database tại máy đang chạy. Hai máy chạy hai bản local là hai
bộ dữ liệu riêng. Muốn điện thoại/máy khác đồng bộ cần một backend HTTPS chung
được triển khai; hiện chưa có endpoint Internet của bạn.

Chưa hoàn tất: thẩm định đầy đủ SGK mọi môn/lớp; đề Internet chưa chuyển nguyên
văn toàn bộ; AI/OCR thật; chấm lại thủ công; liên kết phụ huynh; kiểm thử thiết
bị thật; domain/máy chủ production, offsite/cảnh báo thật; xác minh giáo viên,
chính sách cuối cùng và tài khoản/ký/phát hành Google Play/App Store. Không coi
bản .14 là ứng dụng đã phát hành chính thức.
