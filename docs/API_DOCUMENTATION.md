# API local MVP

OpenAPI sinh từ FastAPI tại /openapi.json. Server mặc định chỉ bind loopback.

GET /health; GET /grades; GET /grades/{grade}/subjects.
GET /exams?grade=5&subject=toan&search=...; GET /exams/{id} không trả đáp án.
POST /exams/{id}/attempts → id, token, câu hỏi, thời điểm bắt đầu.
POST /attempts/{id}/submit body {"answers":{"question_id":["A"]}} với header X-Attempt-Token.
GET /attempts/{id}/result; DELETE /attempts/{id}, cùng header.

Khả năng làm khách: token phải được giữ ở thiết bị, server chỉ lưu SHA-256. Không có endpoint list guest attempt. Retry cùng payload trả cùng kết quả; payload khác trả 409. Bài luyện tập nộp trong 24h, thời lượng là gợi ý; không coi là kỳ thi có giám sát.

Admin: Authorization: Bearer token từ cấu hình server. GET /admin/questions; POST /admin/import; POST /admin/questions/{id}/approve?rights_confirmed=true; POST /admin/questions/{id}/publish; POST /admin/exams; POST /admin/exams/{id}/publish. Batch import atomic, duplicate trả 409, schema lỗi trả 422, quyền thiếu trả 403. Chỉ dành development: production mode fail closed.

Đúng/sai: mảng true/false theo thứ tự nhận định. Nhiều đáp án: exact set; đúng/sai chấm từng ý. Numeric chấp nhận phân số/thập phân và đơn vị cấu hình. Tự luận trả null score và needs_manual_review, không bịa điểm.


Tạo đề và ôn theo chủ đề local: xem [LOCAL_STUDY_MODULE.md](LOCAL_STUDY_MODULE.md) cho `/practice-options` và `/practice-attempts`.
