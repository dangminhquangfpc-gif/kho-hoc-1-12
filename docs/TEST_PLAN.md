# Kiểm thử

Backend: PYTHONPATH=services/api python -m pytest services/api/tests. Bao phủ chọn lớp/môn/đề/nộp/kết quả/xóa, privacy trước nộp, capability token, immutable snapshot, idempotency, atomic import, duplicate, quyền admin, phân số/thập phân/đơn vị/tolerance/đúng-sai/nhiều lựa chọn và self-review essay.

DB: bootstrap_local.sql → migration → rls.sql trên PostgreSQL 17 local, ON_ERROR_STOP=1. Chạy migration lần 2 kiểm tra idempotency. Bootstrap giả lập auth contract chỉ để kiểm thử, không chứng minh Supabase hosted.

Mobile: flutter analyze, flutter test và flutter build web. Widget flow kiểm tra API giả có kiểm soát, không tuyên bố integration Android từ widget test. Kiểm thử trình duyệt dùng API thật là kiểm tra bổ sung. Android: flutter build apk --debug khi có SDK; thiết bị/emulator vẫn cần kiểm tra trước nghiệm thu.

Admin: npm ci → npm run typecheck → npm run build; kiểm tra browser login, nhập/export và quyền từ chối. OCR/AI failure tests kiểm tra interface unconfigured, không kiểm tra provider thật chưa có.

Kết quả thực thi được cập nhật ở docs/VALIDATION.md; không gộp skipped/unrun vào passed.

Browser admin: cấu hình KHOHOC_ADMIN_TOKEN và chạy node apps/admin/tests/admin-smoke.cjs khi API/admin đang chạy. Browser mobile kiểm thử bản web với API thật được ghi riêng trong VALIDATION. CI được tạo nhưng chưa khẳng định GitHub Actions đã thực thi.
