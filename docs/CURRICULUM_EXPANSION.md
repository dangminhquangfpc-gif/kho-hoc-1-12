# Dữ liệu mở rộng theo chủ đề — 15/10/2026

Bản thử gồm 1.566 câu hỏi, 219 đề và 199 tài liệu đọc. Danh mục có 135 tổ hợp lớp–môn; mỗi tổ hợp đã có ít nhất một đề và một ghi chú. Đây là mức bao phủ danh mục, **không phải bao phủ đầy đủ chương trình hoặc toàn bộ SGK**.

## Phạm vi

- Giữ 108 câu, 12 đề và 4 PDF mẫu cũ để không thay đổi các bài làm đã lưu.
- Toán lớp 1–12: 72 chủ đề/dạng, mỗi dạng 10 biến thể số liệu, tổng 720 câu, 84 đề (72 đề chủ đề + 12 đề tổng hợp) và 72 ghi chú. Không gọi 720 biến thể là 720 dạng bài khác nhau.
- Các môn còn lại: 123 bộ ôn, mỗi bộ 6 câu, tổng 738 câu, 123 đề và 123 ghi chú. Nhiều kiến thức nền được sử dụng lại giữa các lớp; Tiếng Anh được chia cấp tiểu học/THCS/THPT. Vật lí, Hóa học và Sinh học THPT có bộ chủ đề riêng cho lớp 10, 11, 12. Đây vẫn là bộ khởi đầu, chưa phải ngân hàng hoàn chỉnh cho từng môn.
- Tài liệu mới đọc ngay trong ứng dụng; chỉ 4 tài liệu cũ có PDF. Không gắn nút tải PDF cho tài liệu chưa có PDF.

## Quan hệ với Kết nối tri thức

Nội dung được tự biên soạn theo các mảng kiến thức GDPT 2018 hướng tới bộ Kết nối tri thức với cuộc sống; không sao chép bài đọc, hình ảnh hoặc câu hỏi từ SGK. Nhãn `ket_noi_tri_thuc` hiện biểu thị hướng phân loại chủ đề, chưa xác nhận từng bài/ấn bản/trang. Không có tuyên bố nhà xuất bản bảo trợ hoặc tài liệu chính thức.

Cổng Hành trang số của Nhà xuất bản Giáo dục Việt Nam, https://hanhtrangso.nxbgd.vn/, đã kiểm tra truy cập ngày 15/10/2026. Trang được dựng động; chưa xác minh mục lục từng sách. Chưa xác định ấn bản cụ thể người dùng đang học. Do đó `curriculum_coverage.json` ghi rõ `provisional_topic_mapping`, `edition: null`; không tạo số bài, số trang hoặc thông tin xuất bản giả.

Các bước còn cần để gọi là bám sát đầy đủ SGK hiện hành: thu thập mục lục chính xác và năm/ấn bản của từng lớp–môn từ nguồn chính thức; đối chiếu từng mục tiêu học tập; giáo viên duyệt mức độ, câu chữ và đáp án; thêm các dạng còn thiếu; ghi người duyệt và bằng chứng nguồn. Trạng thái duyệt mẫu của demo chỉ phục vụ chạy local, không thay cho thẩm định chuyên môn.

## Tái tạo và kiểm tra

Chạy hai trình dựng theo thứ tự:

```bash
/workspace/venvs/khohoc/bin/python data/pipelines/build_curriculum_seeds.py
/workspace/venvs/khohoc/bin/python data/pipelines/build_subject_seeds.py
PYTHONPATH=services/api /workspace/venvs/khohoc/bin/pytest services/api/tests
```

Trình dựng giữ tài liệu ngoài phạm vi ID do nó quản lí. Dữ liệu được nhập theo lô để tôn trọng giới hạn 500 câu/100 tài liệu của API; không nới giới hạn hoặc bỏ kiểm tra trùng. Kiểm tra gồm ID/câu trùng, môn hợp lệ theo lớp, tham chiếu đề, đáp án đúng/sai và ví dụ Toán tính độc lập. Một số câu nền dùng chung được ghi ngữ cảnh môn/lớp trong đề và được công khai là nội dung ôn lại.

API `/coverage?grade=N` cung cấp số câu/chủ đề/đề/tài liệu đã công khai theo từng môn. Giao diện hiển thị các số này khi chọn lớp/môn, kèm giới hạn dữ liệu. Backend vẫn SQLite local; chưa có Supabase hoặc AI.

## Cập nhật demo

Giải nén bản mới vào thư mục riêng. Không chép thư mục `state` vào gói phát hành. Có thể sao lưu/chép `state` từ bản cũ sang bản mới khi đã dừng cả hai bản để giữ bài làm. Các ID mẫu cũ giữ nguyên; việc nhập lại từ chối nội dung đã bị sửa thay vì tự động duyệt đè. Bộ đề mới có ID mới và không sửa snapshot của bài đang làm.
