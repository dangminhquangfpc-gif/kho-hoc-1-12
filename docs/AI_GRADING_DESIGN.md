# Hybrid grading

Ưu tiên đáp án đã duyệt → thuật toán xác định → người duyệt. Numeric dùng Fraction/Decimal, không eval hoặc thực thi biểu thức người dùng. Kiểm tra dimension khi đổi đơn vị; tolerance theo schema. Trợ lý AI ở bản .16 chỉ giải thích, không tham gia tính hay thay đổi điểm.

AIProvider ở services/api/khohoc/ai.py vẫn là Protocol cho thiết kế chấm tự luận tương lai; UnconfiguredProvider báo lỗi rõ ràng. Chưa tích hợp chấm tự luận tự động. Thiếu rubric phải từ chối chấm AI. Điểm AI không là điểm chính thức.

Bản .16 có adapter trợ lý riêng trong `ai_tutor.py`: provider tương thích Chat Completions qua HTTPS, thời hạn tổng 20 giây, phản hồi có cấu trúc và giới hạn kích thước, xác nhận host/dữ liệu, quota nguyên tử, audit chỉ metadata. Không tự retry để tránh gửi dữ liệu hoặc tính phí lặp. OCR tiếng Việt chạy local trong trình duyệt, có bước sửa/xác nhận. Xem [AI_OCR.md](AI_OCR.md) cho cách cấu hình, quyền và kiểm chứng.

Vẫn cần rubric/model version cho chấm tự luận, đánh giá chuyên môn với provider thật, bộ đánh giá công thức/chữ viết tay, phản hồi lỗi nội dung AI và quy trình người duyệt trước khi xem xét tính năng chấm điểm. Không có dịch vụ AI thật được kích hoạt trong demo mặc định.
