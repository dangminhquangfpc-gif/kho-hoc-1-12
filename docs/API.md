
## Thư viện và quản trị phiên bản local

Public: `GET /documents` (grade, subject, semester, topic, textbook, kind, search, limit, offset); `GET /documents/{id}`; `GET /documents/{id}/file?download=true`. Chỉ nội dung đã duyệt/xuất bản có quyền hợp lệ được hiển thị. Tài liệu link_only chỉ mở nguồn gốc; không phân phối file/nội dung. Bằng chứng cấp phép và tên file nội bộ chỉ dành cho admin.

Admin: `/admin/documents` và `/admin/documents/import`, `/admin/documents/{id}/approve?rights_confirmed=true`, `/admin/documents/{id}/publish`. Không tải tài liệu từ URL ngoài hoặc nhận upload file ở bước này.

Admin câu hỏi: `GET /admin/questions/{id}`, `GET /admin/questions/{id}/versions`, `PUT /admin/questions/{id}` với question/expected_version/note, `POST /admin/questions/{id}/rollback` với target_version/expected_version/note. Sửa/rollback tạo revision mới, về draft, hủy rights và đưa đề liên quan về draft; snapshot bài đang làm giữ nguyên. Duyệt/publish nhận expected_version và dùng compare-and-set. `GET /admin/exams` là metadata riêng tư để kiểm tra seed. Script fixture từ chối nội dung đã sửa, không tự duyệt theo ID.

Demo gateway không chuyển Authorization admin. Không phải API production hay Supabase Storage adapter.

## Trợ lý AI ở bản .16

`GET /ai/status` yêu cầu đăng nhập, trả trạng thái cấu hình, host nhà cung cấp,
tên mô hình và hạn mức ngày; không trả khóa. Mặc định `configured=false`.

`POST /ai/explain` yêu cầu đăng nhập, `grade`, `subject`, văn bản `text`
(3–6.000 ký tự), `consent=true` và `expected_provider_host` khớp host vừa được
hiển thị. Cặp `attempt_id`/`question_id` là tùy chọn: chỉ dùng câu của chính tài
khoản trong bài đã nộp, tham chiếu snapshot đề/đáp án/lời giải, không gửi lại
đáp án riêng đã lưu của học sinh. Không nhận ảnh hoặc URL đích từ người dùng.

Phản hồi chứa hướng dẫn, các bước, điểm chưa chắc chắn, `grounded`,
`provisional=true`, `needs_review=true` và metadata token; không thay đổi điểm.
Lỗi: 401 chưa đăng nhập, 404 không sở hữu bài/câu, 409 bài chưa nộp hoặc host
đổi, 422 dữ liệu không hợp lệ/quá lớn, 429 hết hạn mức, 503 chưa cấu hình,
502 phản hồi dịch vụ không hợp lệ, 504 hết thời gian. Yêu cầu đã dành quota
vẫn tính lượt khi nhà cung cấp lỗi. Xem [AI_OCR.md](AI_OCR.md).
