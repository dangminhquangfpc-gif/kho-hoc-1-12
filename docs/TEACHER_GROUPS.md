# Bản 2026.10.15.10 — vai trò, nhóm và ngân hàng câu hỏi

Đăng ký chọn Học sinh hoặc Giáo viên, không thể tự đăng ký vai trò quản lý.
Học sinh làm các đề có sẵn và ôn các câu từng trả lời sai trong kết quả của chính mình;
API từ chối tạo đề ngẫu nhiên và từ chối dùng danh sách ID để lách quyền tạo đề.
Giáo viên/quản lý chọn nhiều chủ đề, độ khó, số câu và có thể lưu đề cho một nhóm mình sở hữu.
Đề nhóm xuất hiện trong Luyện đề của thành viên; người ngoài nhóm không xem hoặc bắt đầu được.
Đề luyện riêng chỉ tạo lượt làm, không xuất bản cho nhóm.

Giáo viên tạo nhóm trong Tài khoản → Quản lý học viên. Có hai cách thêm học viên:

- Tạo hàng loạt tài khoản rồi thêm tên đăng nhập vào nhóm.
- Học sinh tự đăng ký, nhập mã nhóm tại Tài khoản. Màn hình thông báo giáo viên sẽ xem kết quả.

Giáo viên xem kết quả học viên mình cấp hoặc đã tham gia nhóm của mình. Giáo viên không đặt lại
mật khẩu/xóa tài khoản tự đăng ký chỉ vì học sinh tham gia nhóm. Bỏ thành viên/xóa nhóm giữ nguyên
kết quả và tài khoản. Mã nhóm là mã mời, chỉ chia sẻ cho học viên; học sinh không nhận mã hoặc ID
của thành viên khác từ API danh sách nhóm. Quản lý ban đầu vẫn xem học viên tự đăng ký trong hệ thống
và học viên do các giáo viên thuộc hệ thống cấp. Hai hệ quản lý độc lập không được xem chéo.
Vai trò giáo viên tự đăng ký theo yêu cầu người dùng; không khẳng định đã xác minh nghề nghiệp.

## Dữ liệu bổ sung

Thêm **5.246 câu**: 4.086 Toán các lớp 1–4, 6–12; 800 Tiếng Anh lớp 3–12;
360 Khoa học lớp 4–5, KHTN lớp 6–9 và Vật lí lớp 10–12.
Có thêm 164 đề tự biên soạn làm trực tiếp: 88 Toán, 76 Tiếng Anh/khoa học.
Giữ toàn bộ ID/nội dung bộ câu cũ, không thay đổi đáp án trong lượt làm đã lưu.
Các chủ đề Toán cốt lõi được thêm khoảng 60 biến thể; số thực tế có thể ít hơn sau loại trùng.
Dãy số và bài toán lớp 1 cũng được bổ sung, gộp các tên chủ đề đồng nghĩa cho cộng/trừ/cấu tạo số.
Đây là biến thể theo kỹ năng, chưa thẩm định sư phạm độc lập hoặc xác minh đủ từng bài KNTT.
Chưa phủ đều mọi chủ đề của mọi môn. Tiếng Anh hướng tới Global Success ở mức kỹ năng.

## Nguồn Internet

164 đề mới là nội dung tự biên soạn, không phải bản chép các đề Internet đã liên kết.
Đã kiểm tra trang https://loigiaihay.com/de-kiem-tra-giua-hoc-ki-1-toan-5-ket-noi-tri-thuc-de-so-1-a173471.html
và trang điều khoản https://loigiaihay.com/policy/vi.html ngày 15/10/2026.
Trang đề có thông báo Copyright, không tìm thấy giấy phép tái phân phối toàn bộ;
trang điều khoản được kiểm tra chủ yếu nói về tài khoản, riêng tư và dịch vụ tắt quảng cáo.
Việc đọc miễn phí không thiết lập quyền sao chép toàn bộ vào bản phân phối app.
Vì vậy không đổi metadata link_only thành câu hỏi/đề làm trực tiếp khi chưa có nội dung và quyền phù hợp.
Giao diện gọi đúng là liên kết tham khảo, tách khỏi số đề làm trực tiếp và đặt sau danh sách đề.
Pipeline pdf_exam_draft.py hiện có hỗ trợ PDF được phép dùng, đáp án đã kiểm tra, bản nháp cần duyệt;
chưa triển khai nhập nguyên bản hàng loạt các đề Internet của thư viện hiện tại.

## Nâng cấp và phạm vi chạy

Dừng bản cũ, sao lưu rồi chép toàn bộ state sang bản mới trước lần chạy đầu.
Các bảng nhóm và quyền đề riêng được tạo bổ sung, không sửa/xóa tài khoản hoặc kết quả cũ.
Giữ cổng/địa chỉ để tiếp tục dùng lịch sử trình duyệt. Tất cả thiết bị phải kết nối cùng backend
mới dùng chung tài khoản, nhóm và kết quả; các ZIP chạy riêng là các cơ sở dữ liệu riêng.
Đăng nhập từ thiết bị khác cần backend HTTPS; bản này vẫn dùng backend local, chưa phải dịch vụ hosted.
