# Tài liệu theo phần học và Luyện đề — 15/10/2026

## Phân loại

Tài liệu chỉ hiển thị nội dung có phần đọc trong app, gồm kiến thức/cách làm/ví dụ/bài tập; không hiển thị đề kiểm tra hoặc các kho liên kết bên ngoài như một bài hướng dẫn đã hoàn chỉnh. Luyện đề có 219 đề làm/chấm trong app và lối vào các đề nguồn ngoài với bộ lọc giữa/cuối kỳ, năm và bộ sách. Các nguồn tham khảo còn giữ trong dữ liệu quản trị; không xóa ID hoặc bài làm cũ.

API `/documents?section=lessons|exams|references` phân loại ở backend. Đề thi nhận diện theo kind=exam hoặc đợt kiểm tra/tốt nghiệp, nên tài liệu hướng dẫn ôn tốt nghiệp cũng nằm trong nhóm luyện thi. API `/curriculum?grade=N&subject=S` trả mục lục và tình trạng tài liệu từng mục; có tài liệu là trạng thái bản soạn chờ thẩm định, không phải đã kiểm chứng toàn bộ kiến thức hoặc học sinh đã học xong.

## Nội dung mới

75 ghi chú Toán 5 được soạn theo 75 bài của mục lục tham khảo Kết nối tri thức; gồm 278 lượt bài tập (một số dạng/bài được ôn lại). Mỗi ghi chú có kiến thức/cách làm, ví dụ từng bước, bài tập, lời giải và lỗi cần tránh. Bài ôn tập chung gộp các kĩ năng liên quan thay vì chỉ một lời nhắc chung. Phần lời giải bài tập thu gọn trong giao diện. Tài liệu sắp theo số bài, có chương/chủ đề và học kỳ.

Nội dung là bản soạn gốc, không chép bài đọc hoặc lời giải của trang nguồn. Tên bài và đường dẫn dùng nhận diện mục lục. Chưa có thẩm định độc lập của giáo viên. 75/75 là có ghi chú cho mỗi mục trong nguồn tham khảo, không phải lời cam kết đủ mọi dạng bài của mọi ấn bản.

## Mục lục và giới hạn kiểm chứng

`data/seeds/textbook_units.json` ghi 2.618 mục từ 101 sách/mục lục trên Loigiaihay. Chỉ trích metadata tên mục, chương và URL ở danh sách nội dung chính; không dùng các liên kết sidebar làm bài của sách. Chưa xác định năm/ấn bản từng sách: edition=null. Các bản khác nhau chưa được kiểm kê hết, không suy rằng mọi ấn bản hoàn toàn giống nhau.

Các mục chưa có bài hướng dẫn được hiển thị rõ là thiếu. Các lớp/môn chưa có mục lục được ghi chưa xác minh, không hiển thị phần trăm hoàn thành 0/0. Những ghi chú chủ đề cũ vẫn đọc được nhưng không tự động tính là đã phủ một bài SGK khi chưa có ánh xạ kiểm chứng.

Đã tìm API metadata chính chủ trên Hành trang số: endpoint slide công khai trả HTTP 200 và xác nhận nhóm Kết nối tri thức; endpoint danh sách sách theo loại/lớp trả HTTP 401 khi không đăng nhập. Endpoint tìm kiếm công khai trả HTTP 200 nhưng không có bản ghi khi thử Toán/Tiếng Việt, nên chưa cung cấp được mục lục chính chủ. Không trích credential, không vượt xác thực, không tải/phân phối sách nguyên bản. Vì chưa có mục lục gốc đủ 135 tổ hợp lớp–môn và chưa có thẩm định nội dung, yêu cầu “không thiếu phần nào của từng môn và mọi ấn bản” vẫn chưa thể xác nhận.

## Tái tạo

`data/pipelines/textbook_index.py` phân tích mục lục có cấu trúc. `data/pipelines/build_math5_lessons.py` dựng lại ghi chú Toán 5 từ bảng kĩ năng/cách làm/bài tập đã soạn và mục lục đã ghi nhận. Không tự tạo mục lục sách không có nguồn, không tạo ghi chú chung để đánh dấu giả rằng một bài đã hoàn tất. Cần đối chiếu mục lục gốc, soạn nội dung cho các mục thiếu và thẩm định trước khi công bố đủ chương trình.

## Quy tắc chung cho mọi lớp và môn

Danh sách `section=lessons` chỉ nhận bài Kết nối tri thức có mã bài tồn tại
trong mục lục đúng lớp/môn và đủ bốn phần: kiến thức và cách làm, ví dụ từng
bước, bài tập tự luyện, lời giải. Quy tắc này cũng áp dụng khi tính số bài
đã biên soạn trong `/curriculum`. Mã bài giả hoặc thuộc lớp/môn khác không
được tính. Ghi chú nền tảng chưa đối chiếu vẫn được giữ trong dữ liệu tham
khảo, không hiển thị như bài học bám SGK. Đề kiểm tra thuộc phần luyện đề.

Đây là kiểm tra cấu trúc và đối chiếu mục lục nguồn thứ cấp, chưa chứng minh
nội dung chính xác về sư phạm hoặc phủ đủ các ấn bản. Hiện mới có 75 bài
Toán 5 được biên soạn theo mục lục đã thu thập. Những môn/lớp khác chưa có
bài phù hợp phải hiển thị thiếu, không dùng nội dung tổng quát thay thế.

## Trình bày lời giải — bản 2026.10.15.7

Đã soạn lại 139 ví dụ và 278 lời giải bài tập trong 75 tài liệu Toán 5 hiện có. Mỗi ví dụ có đề bài rõ, phần Lời giải từng bước và Đáp số. Mỗi bài tự luyện có lời giải riêng; bài toán có lời văn ghi câu dẫn, phép tính và đơn vị, rồi đáp số. Bài vẽ/nhận xét kết thúc bằng kết luận tương ứng, không tự tạo đáp án số cho câu hỏi không có số.

Các quy tắc ưu tiên diễn đạt bằng lời phù hợp tiểu học, định nghĩa các chữ dùng trong công thức. Bài hình tròn dùng số 3,14 và giải thích bán kính/đường kính trước khi tính. Cộng/trừ thập phân có đặt tính thẳng cột, giữ căn cột trên màn hình nhỏ. Phần mở lời giải căn trái toàn chiều rộng.

Nội dung được tự biên soạn theo mục lục Kết nối tri thức và cách giải toán tiểu học; không tuyên bố đã xác minh nguyên mẫu từng trang SGK. Đã đối chiếu thêm quy tắc chu vi ở nguồn thứ cấp Bài 27 (Loigiaihay) ngày 15/10/2026; không sao chép nguyên lời giải của nguồn. Các môn/lớp còn thiếu vẫn giữ trạng thái thiếu.

`data/pipelines/math5_worked_solutions.py` chứa nội dung đã soạn; không ghép nhãn Lời giải vào chuỗi đáp án ngắn cũ. Kiểm tra số học dùng Fraction để so sánh chính xác các đẳng thức tính được; không thay cho thẩm định sư phạm.

Nâng cấp local giữ nguyên ID bài để yêu thích/đọc gần đây không bị mất. `data/library/document_upgrades.json` liệt kê hash của từng chuyển đổi đã duyệt từ bản gốc .6 sang .7. Trước khi sửa dữ liệu, kiểm tra toàn bộ câu hỏi/đề/tài liệu; chỉ nâng cấp tài liệu đang xuất bản có nội dung khớp hoàn toàn. Giữ nội dung trước đó trong nhật ký, tăng phiên bản và cập nhật ngày sửa. Nội dung người dùng đã sửa riêng không bị tự ghi đè. Sao lưu và chép toàn bộ state khi chuyển gói.
