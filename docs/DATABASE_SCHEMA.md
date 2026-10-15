# Schema và quan hệ

education_programs → grades; subjects ↔ grades qua grade_subjects (requirement).
content_sources → questions → question_versions (payload riêng chứa đáp án); exams → exam_questions → question_versions.
exam_attempts → student_answers / grading_results. Snapshot của attempt khóa phiên bản đề. user_roles liên kết auth.users; client không có quyền ghi roles hoặc điểm.

MVP API local dùng cùng các khái niệm nhưng lưu question payload, exam question IDs và attempt snapshot dưới JSON để tránh nhân rộng bảng trước khi cần. Supabase migration là schema đích chuẩn hóa. Chuyển repository adapter sang schema đích và kiểm thử RLS là công việc bắt buộc trước production.

Không truy cập trực tiếp answer tables qua Supabase client. Backend kết nối bằng DB role tin cậy sau khi kiểm tra quyền. Không dùng service_role trong mobile/admin browser.
