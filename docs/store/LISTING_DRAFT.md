# Nội dung nháp Google Play — Tự học 111

Phạm vi: bản 0.2.0+18. Đây là nội dung để duyệt trước khi nhập Play Console;
chưa phải trang cửa hàng đã công bố. Không có trợ giảng AI trả phí trong bản này.

## Tên và mô tả

**Tên ứng dụng:** Tự học 111

**Mô tả ngắn:** Luyện đề, đọc hướng dẫn, nhận chữ từ ảnh và quản lý nhóm học tập.

**Mô tả đầy đủ dự kiến:**

Tự học 111 giúp học sinh chọn lớp, môn và luyện tập theo chủ đề. Sau khi nộp
bài, học sinh xem kết quả và lời giải của các câu đã có hướng dẫn.

- Luyện đề có sẵn, lưu bài đang làm và xem lại lịch sử.
- Đọc tài liệu gồm kiến thức, cách làm, ví dụ và bài tập tự luyện.
- Nhận chữ in tiếng Việt/Anh từ ảnh ngay trên thiết bị; sửa và kiểm tra văn
  bản trước khi dùng cho câu trả lời. OCR có thể đọc sai chữ viết tay, công
  thức hoặc hình vẽ.
- Đăng ký vai trò học sinh hoặc giáo viên. Học sinh làm bài và tham gia nhóm;
  giáo viên tạo đề từ nhiều chủ đề, cấp tài khoản học viên, giao bài và theo
  dõi kết quả trong phạm vi nhóm quản lý.
- Khi dùng tài khoản và máy chủ chung, tiếp tục bài và xem kết quả trên các
  thiết bị. Nhận chữ từ ảnh dùng được mà không cần tài khoản hay máy chủ.

Tài liệu và câu hỏi trong app được tự biên soạn, hướng tới chương trình Kết
nối tri thức với cuộc sống. Mức độ bao phủ giữa các môn/lớp chưa đồng đều;
không cam kết thay thế toàn bộ sách giáo khoa. Một số nguồn Internet được
đính kèm đề luyện tự biên soạn; một số chỉ mở trang nguồn. Không mặc định
các đề trong app là bản sao đầy đủ của PDF trên Internet.

Đăng nhập, tài liệu, luyện đề và quản lý nhóm cần kết nối máy chủ do đơn vị
vận hành cung cấp. Chức năng nhận chữ không tải ảnh OCR lên máy chủ; SDK ML
Kit trên Android/iOS có thể gửi dữ liệu chẩn đoán tới Google theo công bố của
Google. Đọc chính sách quyền riêng tư trước khi sử dụng tài khoản.

Ứng dụng hiện không có quảng cáo hoặc thanh toán trong app. Tự học 111 không
tuyên bố được nhà xuất bản sách giáo khoa chứng nhận hoặc bảo trợ.

## Trường nhập cần hoàn thiện

| Trường Play Console | Giá trị/việc cần làm |
| --- | --- |
| Ngôn ngữ mặc định | Tiếng Việt |
| Danh mục dự kiến | Giáo dục |
| Loại ứng dụng | Ứng dụng; không có quảng cáo/mua hàng tích hợp |
| Tên nhà phát triển, email hỗ trợ, website | Chưa có thông tin công khai được xác nhận |
| Privacy Policy URL, URL yêu cầu xóa tài khoản | Chưa có URL đang vận hành; xem [PRIVACY_DRAFT.md](PRIVACY_DRAFT.md) |
| Đối tượng tuổi/Target audience và Families | Phải quyết định theo người dùng thật lớp 1–12; quy trình trẻ em chưa hoàn tất |
| App access | Có chức năng cần đăng nhập; cung cấp hai tài khoản tổng hợp học sinh/giáo viên và backend HTTPS thật |
| Data Safety | Hoàn thiện từ [bảng đối chiếu](DATA_SAFETY_WORKSHEET.md), không chọn “không thu thập dữ liệu” |
| Content rating | Tự khai sau khi rà liên kết ngoài và nội dung thật của bản gửi |
| Icon/ảnh nổi bật/ảnh chụp | Dùng bộ tài nguyên riêng đã duyệt và ảnh chụp bản .18; không dùng tài khoản học sinh thật |

## Nội dung cần tránh khi xuất bản

- Không quảng bá AI, “AI miễn phí”, chấm tự luận tự động hoặc dịch vụ chưa có.
- Không viết “đầy đủ mọi bài SGK”, “mọi đề Internet đã nhập” hoặc “100% chính xác”.
- Không quảng bá toàn bộ app chạy offline: hiện chỉ OCR độc lập dùng được khi backend mất kết nối.
- Không ghi “không thu thập dữ liệu”: tài khoản, bài làm và SDK có các luồng dữ liệu cần khai.
- Không ghi “miễn phí vĩnh viễn”: bản hiện tại không có mua hàng; chi phí backend,
  tài khoản nhà phát triển và mô hình vận hành chưa được quyết định.

## Gợi ý bộ ảnh chụp thật

1. Chọn lớp/môn và danh sách luyện đề.
2. Bài đang làm với câu hỏi đọc được; không hiển thị thông tin định danh.
3. Kết quả và lời giải sau khi nộp.
4. Hướng dẫn có kiến thức, ví dụ, bài tập và đáp số.
5. Nhận chữ từ ảnh với nội dung mẫu không chứa thông tin cá nhân.
6. Tài khoản giáo viên: nhóm và kết quả của học viên giả lập.

Trước khi nhập nội dung lên Play Console, đối chiếu lại với đúng bản AAB và
backend được dùng để xét duyệt. Quy trình kiểm thử: [REVIEWER_GUIDE.md](REVIEWER_GUIDE.md).
