# Thư viện mẫu tự biên soạn

`documents.json` chứa bốn ghi chú Toán cho lớp 1, 5, 9 và 12. Nội dung được soạn riêng cho bản thử Kho Học 1–12; không lấy từ sách giáo khoa, kho đề hoặc website bên ngoài. Đây là tài liệu mẫu phục vụ kiểm thử, chưa có thẩm định chuyên môn độc lập.

`files/` chứa các bản PDF tương ứng, dựng bằng Chromium từ nội dung trong JSON và phông Noto Sans đã có giấy phép OFL trong `apps/mobile/assets/fonts/`. `sources/` lưu bản HTML dùng để dựng PDF. Mỗi bản PDF đều nêu rõ trạng thái tài liệu mẫu.

Sau khi đã cài dependency admin, dựng lại PDF bằng `node data/library/generate_pdf.cjs`. Trình dựng chỉ đọc các trang ghi chú và phông từ máy cục bộ, chặn tài nguyên bên ngoài. PDF mẫu đã được lưu sẵn nên khởi chạy API không cần Chromium.

Metadata `original_content` chỉ đánh dấu nguồn tự biên soạn của các ví dụ này. Các nguồn bên ngoài phải có bằng chứng riêng và được duyệt trước khi phân phối. Nội dung `link_only` chỉ lưu metadata và đường dẫn HTTPS; không lưu lại nội dung hoặc cung cấp tải PDF.

API công khai hiển thị nguồn, tác giả và giấy phép. Bằng chứng quyền sử dụng đầy đủ chỉ có trong API quản trị vì thỏa thuận cấp phép của nguồn khác có thể chứa thông tin riêng tư. Kiểm tra PDF cục bộ giới hạn 10 MiB, cấm liên kết tượng trưng và đường dẫn vượt thư mục; kiểm tra chữ ký và một số nội dung hoạt động phổ biến. Đây chưa phải bộ làm sạch PDF tổng quát hay dịch vụ quét mã độc.

Nhập các tài liệu dưới dạng bản nháp:

```bash
source /workspace/state/khohoc.env
export KHOHOC_ADMIN_TOKEN
/workspace/venvs/khohoc/bin/python scripts/seed_library.py
```

Thêm `--publish-fixtures` chỉ để duyệt và công khai các ví dụ trong môi trường phát triển biệt lập. Đây không phải bước thẩm định chuyên môn cho phát hành chính thức.


## Dữ liệu mở rộng 15/10/2026

Bản thử hiện có 1.566 câu, 219 đề và 199 tài liệu; có dữ liệu cho mọi tổ hợp lớp–môn trong danh mục. Đây là dữ liệu tự biên soạn hướng tới Kết nối tri thức, chưa đối chiếu toàn bộ SGK hiện hành. Xem `docs/CURRICULUM_EXPANSION.md` để phân biệt biến thể Toán, bộ ôn nền và phần còn thiếu.
