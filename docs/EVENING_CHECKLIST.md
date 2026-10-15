# Kiểm tra bản thử .16 tối nay

Dừng bản cũ → sao lưu `state` → giải nén bản .16 → chép nguyên `state` vào bản
mới → chạy `start-demo.bat`. Giữ cùng cổng localhost để giữ dữ liệu trình duyệt.
Không xóa dữ liệu cũ khi gặp lỗi; lưu nội dung thông báo và bước tái hiện.

1. Đăng nhập tài khoản cũ; kiểm tra nhóm, lịch sử và điểm cũ còn nguyên.
2. Đăng ký học sinh: làm được đề có sẵn, không tạo đề hoặc quản lý nhóm.
3. Đăng ký giáo viên: tạo nhóm, cấp tài khoản hàng loạt; học sinh đổi mật khẩu
   tạm, tham gia bằng mã nhóm. Thử thêm tài khoản giáo viên đã cấp vào nhóm.
4. Giáo viên tạo đề với nhiều chủ đề, giao cho nhóm. Tài khoản ngoài nhóm không
   được mở đề riêng. Thử các lớp/môn bạn đang dạy để ghi nhận câu còn thiếu.
5. Giáo viên mở nhóm → Bài giao và tiến độ → Giao đề có sẵn; học sinh mở Bài
   được giao. Thử một người chưa làm, một người đang làm và một người đã nộp.
   Kiểm tra bộ lọc và CSV của đúng đề, điểm lấy lần nộp gần nhất.
6. Làm bài, chuyển câu, thoát/mở lại, nộp và kiểm tra lời giải. Thử tiếp tục bài
   từ danh sách bài đang làm; không nộp từ hai bản cũ khi được báo xung đột.
7. Mở tài liệu theo lớp/môn/bài, kiểm tra kiến thức, cách làm, lời giải và đáp
   số. Gửi **Báo lỗi nội dung** nếu có sai/thiếu, ghi đúng bài và bước cần sửa.
8. Báo lỗi một câu đang làm hoặc đã nộp; vào Phản hồi của tôi. Giáo viên mở Xử
   lý phản hồi nội dung, trả lời; học viên tải lại và xem trả lời. Kiểm tra
   điểm cũ không tự thay đổi sau phản hồi.
9. Giáo viên mở nhóm, tải CSV. Kiểm tra tiếng Việt, học viên chưa nộp có điểm
   trống, số bài/điểm trung bình phù hợp. CSV tính mọi môn/mọi lần làm của thành
   viên hiện tại, không riêng đề giáo viên giao.
10. Thử đăng xuất/đăng nhập tài khoản khác: không thấy bài đang làm, phiếu phản
   hồi hoặc nhóm riêng của tài khoản trước. Thử tìm kiếm tiếng Việt có/không dấu.
11. Trên tài khoản thử riêng, đổi mật khẩu và tự xóa tài khoản; không thử xóa
    tài khoản/dữ liệu bạn muốn giữ. Kiểm tra phiên cũ không đăng nhập được nữa.
12. Cá nhân → **Ảnh và trợ lý học tập**: chọn ảnh chữ in tiếng Việt PNG/JPEG/WebP.
    Xem ảnh và chữ, sửa các số/dấu, thử hủy nhận dạng hoặc tệp không hỗ trợ.
    OCR không cần đăng nhập; chữ viết tay/công thức có thể sai và cần kiểm tra.
13. Trong một câu tự luận, mở **Nhập từ ảnh hoặc văn bản**; chỉ sau khi kiểm tra
    và xác nhận dùng văn bản thì ô trả lời mới đổi. Kiểm tra không tự nộp bài.
14. Khi chưa cấu hình AI, màn hình phải báo rõ và vẫn dùng OCR/tài liệu/luyện
    đề được. Native Android/iOS hiện chỉ nhập/dán văn bản, chưa nhận chữ từ ảnh.
15. Chỉ khi operator đã cấu hình và đánh giá dịch vụ thật: kiểm tra lớp/môn,
    văn bản và hộp xác nhận host trước khi gửi AI. Trong bài đã nộp, xem công
    bố tham chiếu đề/đáp án/lời giải và thử tắt lựa chọn để chỉ gửi văn bản đã
    sửa. Phản hồi AI cần kiểm tra, không được đổi điểm bài nộp. Không cần bật
    dịch vụ trả phí hoặc nhập khóa để kiểm tra bản thử hiện tại.

Windows demo dùng database tại máy đang chạy. Hai máy chạy hai bản local là hai
bộ dữ liệu riêng. Muốn điện thoại/máy khác đồng bộ cần một backend HTTPS chung
được triển khai; hiện chưa có endpoint Internet của bạn.

OCR cục bộ đã chạy thật trong Chromium; AI chỉ có kiểm thử provider mô phỏng,
chưa gọi hoặc đánh giá chất lượng dịch vụ thật. Xem [AI_OCR.md](AI_OCR.md).

Chưa hoàn tất: thẩm định đầy đủ SGK mọi môn/lớp; đề Internet chưa chuyển nguyên
văn toàn bộ; AI thật/chấm rubric/báo lỗi phản hồi AI; OCR native/cắt ảnh/chữ
viết tay; chấm lại thủ công; liên kết phụ huynh; kiểm thử thiết bị thật;
domain/máy chủ production, offsite/cảnh báo thật; xác minh giáo viên, chính
sách cuối cùng và tài khoản/ký/phát hành Google Play/App Store. Không coi
bản .16 là ứng dụng đã phát hành chính thức.
