# OCR cục bộ cho Tự học 111

`ocr.js` nhận ảnh sau thao tác chọn tệp của người dùng, kiểm tra định dạng thực
tế/kích thước rồi chạy Tesseract trong Web Worker. Ảnh không được gửi lên máy chủ,
không được ghi vào localStorage/IndexedDB; tên tệp không được ghi log. Ảnh được
vẽ lại lên canvas, bỏ EXIF/GPS trước khi đưa cho worker hoặc tạo ảnh xem trước.
Thư viện ngôn ngữ cũng tắt bộ nhớ đệm IndexedDB (`cacheMethod: none`). Các tệp
tĩnh của chương trình có thể nằm trong bộ nhớ đệm HTTP của trình duyệt.

Trang chính chỉ cần nạp `<script src="ocr/ocr.js"></script>` trước Flutter.
Mọi đường dẫn worker, core và ngôn ngữ được tính từ chính script này; không dùng
CDN hay dịch vụ OCR bên ngoài. Bản `wasm.js` chứa sẵn WebAssembly, không cần tệp
`.wasm` rời. Có bản LSTM thường và SIMD để hỗ trợ cả trình duyệt thiếu SIMD.

API:

```javascript
await window.tuHocOcr.pickAndRecognize(); // gọi ngay trong thao tác nhấn nút
// null khi hủy cửa sổ chọn tệp; hoặc:
// {text, confidence: 0..100, warnings: string[], preview_data_url: string}
window.tuHocOcr.cancel(); // hủy ngay worker, kể cả khi đang khởi tạo
window.tuHocOcr.supported(); // boolean
window.tuHocOcr.status(); // {busy, stage, progress}
await window.tuHocOcr.recognizeFile(file); // cùng kiểm tra; hỗ trợ kiểm thử
```

Lỗi là `Error.message` tiếng Việt. Nút hủy đang chạy làm promise từ chối với
`name = AbortError`. Hết 60 giây nhận dạng là `TimeoutError`; thời gian chọn ảnh
tối đa 120 giây. Chỉ một tác vụ chạy đồng thời. Worker, canvas, bitmap và input
được giải phóng sau thành công, lỗi hoặc hủy. Ảnh xem trước JPEG tối đa 900 điểm
ảnh mỗi chiều chỉ được trả về bộ nhớ của giao diện, không tự lưu lại.

Giới hạn ảnh: PNG/JPEG/WebP tĩnh, 8 MiB, 16 triệu điểm ảnh, mỗi chiều tối đa
6.000 điểm ảnh. Kích thước được đọc từ header trước khi giải mã ảnh; sau giải mã
kiểm tra lại và chỉ xử lý tối đa 8 triệu điểm ảnh/cạnh 3.200. Chữ in tiếng Việt
và tiếng Anh được hỗ trợ; chữ viết tay/công thức toán vẫn cần người dùng kiểm
tra, sửa. Độ tin cậy là chỉ số của OCR, không phải xác suất đáp án đúng.

Bridge dùng giao thức worker của Tesseract.js **6.0.1** đã ghim phiên bản:
`load → loadLanguage → initialize → recognize`, mỗi thông điệp có
`{workerId, jobId, action, payload}`. Bridge sở hữu Worker từ lúc tạo để có thể
hủy ngay trong giai đoạn tải ngôn ngữ/khởi tạo. Tệp upstream giữ nguyên; khi
nâng phiên bản phải chạy kiểm thử Chromium thật cho giao thức này.

Nguồn và giấy phép được lưu trong `PROVENANCE.json` và `licenses/`.
Tesseract.js/core: Apache-2.0. Gói npm dữ liệu ngôn ngữ khai báo MIT, trong khi
repository `naptha/tessdata` cung cấp Apache-2.0; giữ cả metadata gốc và giấy
phép repository để thể hiện rõ khác biệt này. Các license đi kèm bundle worker
được giữ nguyên trong `worker.min.js.LICENSE.txt`.

Tái tạo từ repository root:

```bash
python scripts/prepare_ocr_assets.py
python scripts/prepare_ocr_assets.py --verify
```

Script chỉ tải tarball npm đã ghim và kiểm tra SHA512 SRI trước khi đọc đúng
các member đã liệt kê; không chạy `npm install` hay script vòng đời. Giấy phép
tessdata được ghim bằng Git blob ID. `SHA256SUMS` kiểm tra toàn bộ tệp đã phân
phối, gồm bridge và provenance, không cần mạng với `--verify`.
