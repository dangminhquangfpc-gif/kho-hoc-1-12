# Hybrid grading

Ưu tiên đáp án đã duyệt → thuật toán xác định → người duyệt/AI ở giai đoạn 2. Không gọi AI trong MVP. Numeric dùng Fraction/Decimal, không eval hoặc thực thi biểu thức người dùng. Kiểm tra dimension khi đổi đơn vị; tolerance theo schema.

AIProvider ở services/api/khohoc/ai.py là Protocol có output Pydantic giới hạn điểm, confidence và provisional. UnconfiguredProvider báo lỗi rõ ràng. Chưa có OCR hoặc chấm tự luận tự động. Thiếu rubric phải từ chối chấm AI. Điểm AI không là điểm chính thức.

Cần thêm provider backend, timeout/retry bounded, prompt injection defense, redaction, consent, quotas, model/rubric version, audit, AI feedback reports và đánh giá chuyên môn trước kích hoạt.
