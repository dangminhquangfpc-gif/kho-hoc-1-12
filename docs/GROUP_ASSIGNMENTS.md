# Giao bài và theo dõi từng đề — bản thử .15

Giáo viên/quản lý → Cá nhân → Tài khoản → Quản lý học viên và kết quả → mở
nhóm → **Bài giao và tiến độ** → **Giao đề có sẵn**. Chọn lớp/môn, tìm tên đề,
chọn đề cần giao. Hệ thống tạo một mã đề riêng cho nhóm; không sửa đề nguồn.
Những đề đã tạo theo nhiều chủ đề và chọn nhóm từ trước cũng xuất hiện ở đây.
Có thể giao lại cùng nguồn thành một bài khác với mã riêng.

Học sinh → Cá nhân → Tài khoản → **Bài được giao**. Chỉ có đề thuộc nhóm hiện
đang tham gia và tiến độ của chính mình. Chọn đề để tiếp tục bài cùng mã đang
lưu trên máy hoặc bản nháp trên backend. Nếu còn một bài khác chưa xong, app giữ
nguyên câu trả lời và đề nghị hoàn thành bài đó trước; không ghi đè bài cũ.

Giáo viên mở từng đề để xem thành viên hiện tại và lọc:

- **Đã nộp**: có ít nhất một kết quả máy chủ của đúng mã đề. Số lần nộp tính mọi
  lần nộp, điểm phần trăm lấy lần nộp mới nhất, không lấy điểm cao nhất.
- **Đang làm**: chưa nộp, có bài đang làm của đúng mã đề tạo trong vòng 24 giờ.
- **Chưa nộp**: chưa nộp và không có bài đang làm còn hiệu lực. Có thể đã mở bài
  trước đây nhưng phiên đó đã quá hạn; không đồng nghĩa chưa từng mở đề.

Đã nộp mà điểm chưa xác định sẽ hiện **Chờ xem xét**, để trống điểm trong CSV.
Bài làm thử của giáo viên không tính vào nhóm. Kết quả ở đề nguồn hoặc bài giao
khác dù cùng tên/câu hỏi không tính vào bài này. Thành viên rời nhóm bị loại
khỏi bản thống kê mới; học viên mới vào nhóm được tính theo lịch sử đúng mã đề
của chính mình. Không sửa điểm và không phải sổ điểm chính thức.

Trong chi tiết đề, web/Windows có **Tải bảng điểm CSV**, điện thoại có **Sao chép
bảng điểm CSV**. Tệp web tên `tu-hoc-111-ket-qua-de-giao.csv`, UTF-8 BOM để mở
đúng tiếng Việt; có trạng thái/số lần nộp/điểm gần nhất/thời gian UTC. Chưa nộp
hoặc đang chờ điểm thì để trống điểm, không ghi 0. Chỉ chủ nhóm được xuất. Bảng
điểm tổng mọi môn ở nhóm vẫn có riêng; hai loại báo cáo khác phạm vi.

Không gửi thông báo đẩy/email và chưa đặt hạn giao bài hoặc khóa nộp theo lịch.
24 giờ là thời hạn của từng phiên luyện tập; người học có thể bắt đầu lại sau
khi hết hạn qua luồng khôi phục hiện có. Mã nhóm là cách tham gia, không phải
quyền tải kết quả. Giáo viên khác/quản lý không sở hữu nhóm không xem được bảng
điểm riêng này; học sinh không nhận danh sách/kết quả bạn cùng nhóm.

Bài giao là bản sao danh sách câu hỏi của đề đang được phép sử dụng, không phải
bản sao nguyên đề Internet/PDF. Nội dung vẫn được chụp theo snapshot khi bắt đầu
làm bài như trước. Các câu chưa xuất bản/chưa xác nhận quyền hoặc sai lớp/môn
bị từ chối giao. Không thêm câu hỏi/nội dung SGK trong đợt này.

## Dữ liệu cũ và đồng bộ

Vẫn schema **2**, không thêm bảng. .14 nâng lên .15 giữ tài khoản, nhóm, điểm và
phản hồi. Windows: dừng bản cũ, sao lưu rồi chép nguyên `state` trước khi chạy.
Shared vẫn cần một backend HTTPS chung. Khi nâng API, dùng quy trình bảo trì
hiện có; không cần migration mới nếu database đang schema 2.

Danh sách bản nháp chỉ lấy bài chưa nộp còn hiệu lực trước khi áp giới hạn 100;
100 kết quả đã nộp không còn che mất bài đang làm cũ. Thời hạn pending, khôi phục,
lưu draft và nộp đã thống nhất 24 giờ từ lúc tạo bài. Sửa thêm trường hợp dữ liệu
cũ lưu `result` là JSON null để vẫn nộp/chấm/lưu kết quả được; không thay điểm
bài đã nộp trước đó.
