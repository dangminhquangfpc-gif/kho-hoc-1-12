# Kho Học 1–12 — MVP

Mục tiêu: học sinh dùng không cần tài khoản, chọn lớp → môn → đề → làm bài → nộp → điểm và lời giải → lịch sử cục bộ. Không quảng cáo, chat hoặc thanh toán trong MVP.

Kho gốc là QuizApp Firebase; giữ nguyên ứng dụng cũ để tránh phá workflow. MVP mới ở apps/mobile, services/api và apps/admin. Giai đoạn 1 chưa được nghiệm thu Android cho đến khi có build và kiểm thử thiết bị.

Nội dung thí điểm: Toán lớp 1, 5, 9, 12, mở rộng Ngữ văn/Tiếng Việt và Tiếng Anh sau rà soát chuyên môn. 60 câu hỏi gốc là fixture phát triển, không phải dataset Bộ GDĐT và không được coi là đã được giáo viên duyệt. Chỉ quản trị viên có thể xuất bản sau xác nhận quyền và kiểm duyệt.

Danh mục lớp 1–12 có phiên bản chương trình; môn lựa chọn không được coi là bắt buộc. Metadata hiện là cấu hình khởi đầu cần đối chiếu văn bản chương trình trước phát hành.

Thứ tự: thiết kế → migrations/RLS/seed → backend chấm xác định → mobile → admin → kiểm thử → hướng dẫn → interface AI. Không tự động triển khai dịch vụ trả phí hoặc xuất bản ứng dụng.

Yêu cầu đầy đủ do chủ dự án cung cấp được lưu nguyên văn ở [REQUIREMENTS.md](REQUIREMENTS.md); ROADMAP ghi rõ phạm vi đã triển khai.
