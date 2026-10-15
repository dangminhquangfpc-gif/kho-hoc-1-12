# Khởi tạo nội dung công khai cho máy chủ thử nghiệm

Máy chủ dùng chung không tự duyệt hoặc xuất bản dữ liệu mẫu khi khởi động. Dùng CLI dưới đây để chuyển **nội dung đã xuất bản và đã xác nhận quyền ở nguồn** từ một SQLite đáng tin cậy sang PostgreSQL mới. Không dùng `import-sqlite` cho bước này: lệnh đó chuyển cả cơ sở dữ liệu, có thể bao gồm tài khoản và bài làm.

Việc giữ trạng thái đã xuất bản không chứng nhận nội dung đã được giáo viên, nhà xuất bản hoặc đơn vị bản quyền thẩm định toàn bộ. Ngân hàng hiện tại phục vụ thử nghiệm; mức độ đầy đủ theo chương trình và độ chính xác của nguồn vẫn cần tiếp tục rà soát. Các đề tự biên soạn ghép với nguồn tham khảo không trở thành bản sao nguyên văn đề Internet.

## 1. Xuất gói chỉ chứa nội dung

Chạy ở checkout đáng tin cậy, với Python đã cài `services/api/requirements.txt` và thư mục hiện tại là gốc repository:

```bash
export PYTHONPATH=services/api
python -m khohoc.server_admin export-content \
  --source /duong-dan-rieng/nguon-da-xuat-ban.sqlite \
  --output /thu-muc-trao-doi/noi-dung-cong-khai.json
```

Lệnh mở nguồn chỉ đọc, tạo bản chụp SQLite nhất quán trong thư mục tạm, rồi chỉ chọn câu hỏi, đề và tài liệu công khai. Tệp đầu ra phải chưa tồn tại; lệnh không ghi đè tệp nguồn hoặc tệp xuất cũ. Kết quả in số lượng và `archive_sha256`; giữ giá trị này để kiểm tra khi nhập. Không đưa đường dẫn hoặc bản chụp SQLite nguồn lên kho mã.

Gói JSON chứa đáp án, lời giải, ghi chú quyền và metadata nguồn đã công khai. Không chứa tài khoản, mật khẩu, phiên đăng nhập, bài làm, điểm học viên, nhóm, đề riêng của giáo viên, nhật ký quản trị hoặc danh tính người sửa nội dung. Đề có ID `custom_…` cũng bị loại. Câu hỏi đã bị rút trong danh sách sửa lỗi không được xuất; tham chiếu đề tới câu hỏi cũ được đổi sang câu thay thế giống API công khai.

Gói chỉ chứa bản hiện tại của mỗi câu hỏi. Khi nhập, máy chủ tạo revision hiện tại với actor chung `content-transfer`; không chuyển lịch sử sửa hoặc danh tính người sửa từ máy nguồn. Giữ bản sao lưu riêng nếu cần lịch sử kiểm toán cũ.

PDF không được nhúng vào JSON. Các tài liệu đã được phép phân phối giữ nguyên metadata PDF; manifest chứa SHA256 cho từng PDF công khai cần có. Image API trong repository cung cấp các PDF mẫu công khai ở `data/library/files`. Nếu dùng bộ tệp khác, truyền cùng `--library-root /thu-muc-pdf-cong-khai` khi xuất và nhập. Bộ kiểm tra PDF hiện có chặn đường dẫn thoát thư mục, symlink, tệp quá lớn và nội dung chủ động đã biết. Đừng đặt PDF riêng của học viên vào thư mục này.

## 2. Kiểm tra đích trước khi ghi

Thiết lập `KHOHOC_DATABASE_URL` cho PostgreSQL đích qua biến bí mật của nhà cung cấp hoặc tệp môi trường riêng, không gửi mật khẩu trong chat hay đưa vào Git. Có thể dùng `KHOHOC_DATABASE_PASSWORD_FILE` cùng URL không chứa mật khẩu. Trong container đã cài API, `PYTHONPATH` thường là `services/api`; giữ đúng cách thiết lập của image.

```bash
python -m khohoc.server_admin migrate
python -m khohoc.server_admin import-content \
  --archive /thu-muc-trao-doi/noi-dung-cong-khai.json
```

Lệnh nhập mặc định là **dry-run**: kiểm tra manifest, cấu trúc, tham chiếu câu hỏi, lớp/môn, quyền phân phối, phiên bản, xung đột và các PDF bắt buộc. Kết quả `inserted` là số bản ghi sẽ thêm, `skipped` là số bản ghi đã giống hoàn toàn. Không có nội dung nào được ghi ở bước này. PDF bị thiếu hoặc khác checksum khiến kiểm tra thất bại, không để lại nút tải xuống bị hỏng do nhập thiếu tệp.

SHA256 phát hiện dữ liệu khác nhau; không xác thực ai đã tạo gói. Chỉ nhập gói tự xuất từ nguồn đáng tin cậy. Đối chiếu hash đã ghi ở bước xuất và xem số lượng/chính nội dung JSON trước khi áp dụng.

## 3. Áp dụng gói đã kiểm tra

```bash
python -m khohoc.server_admin import-content \
  --archive /thu-muc-trao-doi/noi-dung-cong-khai.json \
  --expected-sha256 GIA_TRI_ARCHIVE_SHA256_DA_DOI_CHIEU \
  --apply
```

Lệnh chỉ thêm bản ghi mới trong một transaction. Chạy lại cùng gói sẽ bỏ qua bản ghi giống hoàn toàn. Một ID, fingerprint, phiên bản hoặc nội dung đã khác ở máy đích khiến toàn bộ thao tác thất bại; lệnh không ghi đè thay đổi của quản trị viên, không duyệt lại bản nháp và không cập nhật bài làm học viên. Muốn sửa nội dung đã tồn tại, dùng luồng sửa và duyệt trong quản trị. Chạy lệnh với tài khoản quản trị cơ sở dữ liệu ở máy vận hành, không đưa tài khoản này vào APK hoặc cấp cho học viên.

Sau khi nhập, kiểm tra `/health`, `/grades/1/subjects`, `/exams?grade=1&subject=toan` và `/documents?grade=5&subject=toan` trên địa chỉ HTTPS dùng chung. Không dùng kết quả học ngoại tuyến làm điểm tài khoản máy chủ: hai loại kết quả vẫn được tách riêng.
