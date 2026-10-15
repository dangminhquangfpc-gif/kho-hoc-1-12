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
