# Dataset

Chỉ dùng câu hỏi tự biên soạn ở data/seeds/questions.json. Các câu hỏi minh họa không xuất phát từ crawl hay sách giáo khoa. Attribution: nhóm phát triển Kho Học; trạng thái ban đầu draft, quyền original_content. Cần chuyên gia duyệt trước dùng cho học sinh.

Import JSON/CSV → schema validation → normalized hash duplicate check → draft → review → publish. Quyền được xác nhận độc lập với trạng thái nội dung. Metadata source URL chỉ là bằng chứng nguồn, không tự chứng minh giấy phép.

Không tải tài liệu internet trong MVP. Nguồn bên ngoài cần đăng ký license/evidence, kiểm tra điều khoản và robots, rate limit, human review; link-only nếu không có quyền phân phối. Phần parser PDF/DOCX/OCR chưa triển khai.
