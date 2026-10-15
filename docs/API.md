
## Thư viện và quản trị phiên bản local

Public: `GET /documents` (grade, subject, semester, topic, textbook, kind, search, limit, offset); `GET /documents/{id}`; `GET /documents/{id}/file?download=true`. Chỉ nội dung đã duyệt/xuất bản có quyền hợp lệ được hiển thị. Tài liệu link_only chỉ mở nguồn gốc; không phân phối file/nội dung. Bằng chứng cấp phép và tên file nội bộ chỉ dành cho admin.

Admin: `/admin/documents` và `/admin/documents/import`, `/admin/documents/{id}/approve?rights_confirmed=true`, `/admin/documents/{id}/publish`. Không tải tài liệu từ URL ngoài hoặc nhận upload file ở bước này.

Admin câu hỏi: `GET /admin/questions/{id}`, `GET /admin/questions/{id}/versions`, `PUT /admin/questions/{id}` với question/expected_version/note, `POST /admin/questions/{id}/rollback` với target_version/expected_version/note. Sửa/rollback tạo revision mới, về draft, hủy rights và đưa đề liên quan về draft; snapshot bài đang làm giữ nguyên. Duyệt/publish nhận expected_version và dùng compare-and-set. `GET /admin/exams` là metadata riêng tư để kiểm tra seed. Script fixture từ chối nội dung đã sửa, không tự duyệt theo ID.

Demo gateway không chuyển Authorization admin. Không phải API production hay Supabase Storage adapter.
