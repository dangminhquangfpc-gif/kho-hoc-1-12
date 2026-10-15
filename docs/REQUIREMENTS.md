# MASTER PROMPT — XÂY DỰNG ỨNG DỤNG HỌC TẬP LỚP 1–12 TÍCH HỢP AI

## 1. Vai trò và mục tiêu

Bạn là một nhóm kỹ sư phần mềm cấp cao, đảm nhiệm đồng thời các vai trò:

- Senior Flutter Developer
- Backend Architect
- Database Engineer
- AI/ML Engineer
- Data Engineer
- UI/UX Designer
- QA Automation Engineer
- Google Play Release Engineer

Hãy thiết kế và xây dựng một ứng dụng Android có tên tạm thời là **Kho Học 1–12**, dành cho học sinh Việt Nam từ lớp 1 đến lớp 12, giáo viên và phụ huynh.

Ứng dụng cần tổng hợp tài liệu học tập, bài tập, đề kiểm tra, đề thi thử và cung cấp khả năng luyện thi, chấm điểm tự động, giải thích đáp án bằng AI.

Mục tiêu cuối cùng là phát hành ứng dụng lên Google Play, có khả năng vận hành thực tế và mở rộng đến hàng chục nghìn người dùng.

**Yêu cầu đặc biệt:**
- Không chỉ thiết kế giao diện hoặc tạo bản demo.
- Phải xây dựng mã nguồn có thể chạy và kiểm thử.
- Kiến trúc phải hỗ trợ đầy đủ lớp 1–12 và các môn học tương ứng.
- Không được giả lập dữ liệu thật từ internet hoặc tự nhận đã có giấy phép sử dụng tài liệu.
- Triển khai từng giai đoạn, ưu tiên MVP ổn định.
- Sử dụng thư viện mã nguồn mở phù hợp và ưu tiên chi phí thấp.
- Đảm bảo quyền riêng tư, bảo vệ trẻ em, bản quyền nội dung và yêu cầu Google Play.

---

## 2. Đối tượng người dùng

Ứng dụng gồm bốn nhóm người dùng:

**Học sinh**
- Tìm tài liệu theo lớp và môn học.
- Học lý thuyết.
- Luyện tập câu hỏi.
- Làm đề thi thử.
- Nhận điểm số và giải thích.
- Theo dõi tiến độ học tập.

**Giáo viên**
- Tạo bộ đề.
- Nhập câu hỏi và đáp án.
- Thiết lập thang điểm.
- Xem kết quả bài làm.
- Duyệt kết quả chấm AI khi cần.

**Phụ huynh**
- Theo dõi kết quả học tập của con khi được liên kết hợp lệ.
- Xem những kiến thức học sinh còn yếu.
- Nhận gợi ý ôn tập.

**Quản trị viên**
- Quản lý môn học, tài liệu, bộ đề và đáp án.
- Kiểm tra nguồn dữ liệu và bản quyền.
- Duyệt nội dung do AI trích xuất.
- Xử lý báo cáo lỗi và khiếu nại bản quyền.
- Theo dõi chất lượng dataset và chi phí AI.

MVP ưu tiên học sinh và quản trị viên. Giáo viên, phụ huynh được triển khai ở giai đoạn sau.

---

## 3. Phạm vi chương trình giáo dục

Xây dựng hệ thống dựa trên Chương trình giáo dục phổ thông 2018 của Việt Nam và cho phép cập nhật phiên bản chương trình khi có thay đổi.

Hỗ trợ:

- Tiểu học: lớp 1–5.
- THCS: lớp 6–9.
- THPT: lớp 10–12.

Danh mục môn học phải được xây dựng theo đúng cấp học và lớp học, không mặc định tất cả các lớp đều có cùng môn.

Ví dụ:

- Tiểu học: Toán, Tiếng Việt, Tiếng Anh, Tự nhiên và Xã hội, Khoa học, Lịch sử và Địa lí, Tin học và Công nghệ, Đạo đức...
- THCS: Toán, Ngữ văn, Ngoại ngữ, Khoa học tự nhiên, Lịch sử và Địa lí, Tin học, Công nghệ, Giáo dục công dân...
- THPT: Toán, Ngữ văn, Ngoại ngữ, Vật lí, Hóa học, Sinh học, Lịch sử, Địa lí, Tin học, Công nghệ, Giáo dục kinh tế và pháp luật...

Các môn học bắt buộc, lựa chọn và nội dung giáo dục phải được mô hình hóa linh hoạt theo chương trình hiện hành.

Hỗ trợ phân loại tài liệu theo bộ sách giáo khoa:

- Kết nối tri thức với cuộc sống.
- Chân trời sáng tạo.
- Cánh Diều.
- Tài liệu không phụ thuộc bộ sách.

Tên bộ sách chỉ được sử dụng làm metadata phân loại. Không tự động sao chép nội dung sách giáo khoa khi chưa có quyền sử dụng.

Cấu trúc nội dung:

Lớp → Môn → Chương/Chủ đề → Bài học → Tài liệu → Bài tập/Đề thi.

Các dạng ôn tập:

- Bài tập theo bài học.
- Bài tập theo chủ đề.
- Đề kiểm tra thường xuyên.
- Đề giữa học kỳ 1 và 2.
- Đề cuối học kỳ 1 và 2.
- Đề ôn tập cuối năm.
- Đề thi tuyển sinh lớp 10.
- Đề thi tốt nghiệp THPT.
- Đề thi thử theo cấu trúc phù hợp từng kỳ thi.
- Đề luyện tập tự tạo từ ngân hàng câu hỏi.

Định dạng đề thi phải cấu hình được theo từng năm và từng kỳ thi, không hardcode cấu trúc vĩnh viễn.

---

## 4. Công nghệ và kiến trúc

Lựa chọn stack công nghệ:

**Mobile**
- Flutter và Dart.
- Material Design 3.
- Riverpod để quản lý trạng thái.
- GoRouter để điều hướng.
- Dio để gọi API.
- SQLite hoặc giải pháp cache cục bộ tương thích Flutter.
- Hỗ trợ giao diện tiếng Việt và Dark Mode.

**Database và Authentication**
- Supabase.
- PostgreSQL.
- Supabase Auth.
- Supabase Storage.
- Row Level Security (RLS).
- PostgreSQL Full Text Search cho dữ liệu tiếng Việt, kết hợp chiến lược chuẩn hóa dấu và tìm kiếm gần đúng.

**Backend**
- Python FastAPI.
- Pydantic để kiểm tra schema.
- SQLAlchemy hoặc thư viện dữ liệu phù hợp.
- Tách logic nghiệp vụ và các AI provider.
- Background jobs cho tác vụ OCR, nhập dữ liệu và chấm bài dài.
- Thiết kế queue đơn giản cho MVP, có thể mở rộng Redis/RQ sau.

**AI**
- Thiết kế AI Provider Interface để có thể thay thế nhà cung cấp.
- Hỗ trợ cấu hình OpenAI, Gemini hoặc provider tương thích.
- OCR có thể triển khai bằng giải pháp phù hợp với văn bản tiếng Việt và công thức toán.
- SymPy hoặc công cụ tính toán xác định cho toán học.
- AI chỉ được gọi từ backend.
- API key lưu trong biến môi trường hoặc secret manager, tuyệt đối không nhúng vào Flutter.

**Admin Dashboard**
- Next.js + TypeScript.
- Giao diện quản trị responsive.
- Phân quyền phía server.
- Có trang quản lý dataset, bộ đề, đáp án, nguồn dữ liệu, kiểm duyệt và báo cáo.

Tổ chức monorepo:

```text
kho-hoc-1-12/
  apps/
    mobile/
    admin/
  services/
    api/
  data/
    schemas/
    pipelines/
    seeds/
    fixtures/
  supabase/
    migrations/
    policies/
  docs/
  scripts/
  tests/
  .github/workflows/
  README.md
  .env.example
```

Không triển khai microservices phức tạp khi chưa cần thiết. Ưu tiên modular monolith có thể bảo trì và mở rộng.

---

## 5. Chức năng mobile

### 5.1. Trang chủ

Thiết kế giao diện hiện đại, dễ sử dụng, phù hợp học sinh Việt Nam.

Trang chủ có:

- Chọn lớp học.
- Danh sách môn học.
- Thanh tìm kiếm.
- Đề thi nổi bật.
- Tài liệu mới.
- Bài học đang học.
- Bộ đề được đề xuất.
- Tiến độ học tập.
- Lịch sử bài kiểm tra.

Có Bottom Navigation:

1. Trang chủ.
2. Tài liệu.
3. Luyện đề.
4. Tiến độ.
5. Cá nhân.

### 5.2. Kho tài liệu

Cho phép:

- Lọc theo lớp.
- Lọc theo môn.
- Lọc theo học kỳ.
- Lọc theo chương/chủ đề.
- Lọc theo bộ sách.
- Lọc theo loại tài liệu.
- Tìm kiếm bằng từ khóa.
- Đánh dấu yêu thích.
- Xem PDF và hình ảnh được phép phân phối.
- Mở đường dẫn tài liệu ở nguồn gốc khi chỉ có quyền liên kết.
- Tải tài liệu được cho phép tải về.
- Lưu tài liệu đọc gần đây.

Mỗi tài liệu hiển thị:

- Tiêu đề.
- Môn học.
- Lớp.
- Loại tài liệu.
- Nguồn.
- Tác giả/đơn vị cung cấp nếu có.
- Trạng thái kiểm duyệt.
- Quyền xem/tải.
- Ngày cập nhật.

### 5.3. Làm bài kiểm tra

Hỗ trợ các dạng câu hỏi:

1. Trắc nghiệm một đáp án.
2. Trắc nghiệm nhiều đáp án.
3. Đúng/Sai theo từng nhận định.
4. Điền đáp án ngắn.
5. Điền số hoặc kết quả phép tính.
6. Tự luận.
7. Bài toán có lời giải.
8. Câu hỏi có hình ảnh, bảng biểu hoặc công thức toán.
9. Bài làm bằng ảnh chụp.
10. Câu hỏi kết hợp nhiều phần.

Các chức năng:

- Làm bài theo thời gian.
- Đồng hồ đếm ngược.
- Điều hướng giữa các câu.
- Đánh dấu câu chưa chắc chắn.
- Tạm lưu bài làm.
- Khôi phục bài khi ứng dụng bị đóng.
- Nộp bài.
- Xem điểm.
- Xem câu đúng/sai.
- Xem đáp án và lời giải.
- Làm lại đề.
- Lưu lịch sử kết quả.

Không làm mất dữ liệu bài làm khi mất kết nối tạm thời.

---

## 6. Hệ thống chấm điểm tự động

Phát triển một **Hybrid Grading Engine** kết hợp đáp án có sẵn, thuật toán xác định và AI.

### Chế độ A — Chấm theo đáp án có sẵn

Đây là phương thức mặc định và ưu tiên cao nhất.

Áp dụng cho:

- Trắc nghiệm.
- Đúng/Sai.
- Điền đáp án ngắn.
- Câu trả lời số học.
- Các bài toán có tiêu chí chấm xác định.

Yêu cầu:

- Lưu đáp án chuẩn theo phiên bản.
- Không để AI tự thay đổi đáp án đã được duyệt.
- Chấm chính xác theo thang điểm.
- Hỗ trợ chấm điểm từng ý.
- Hỗ trợ nhiều dạng đáp án tương đương.
- Xử lý dấu phẩy thập phân, dấu chấm, phân số và đơn vị đo.
- Hỗ trợ sai số cho phép khi đề quy định.
- Hiển thị cách tính điểm.

Ví dụ:

Đề yêu cầu: 1/2 + 1/4.

Hệ thống có thể chấp nhận 3/4, 0,75 hoặc 0.75 nếu đáp án cho phép các biểu diễn tương đương.

Phải xử lý phép toán bằng công cụ xác định, không phụ thuộc hoàn toàn vào kết quả do LLM sinh ra.

### Chế độ B — Chấm tự luận bằng AI

Input:

- Câu hỏi.
- Đáp án tham khảo.
- Rubric/thang điểm.
- Bài làm của học sinh.
- Môn học.
- Lớp.
- Ngữ cảnh chủ đề.

Output có cấu trúc:

```json
{
  "score": 7.5,
  "max_score": 10,
  "feedback": "Bài làm đúng phần lớn yêu cầu.",
  "strengths": [],
  "mistakes": [],
  "missing_points": [],
  "suggestions": [],
  "confidence": 0.86,
  "grading_status": "provisional"
}
```

Yêu cầu:

- Chấm theo rubric.
- Giải thích lý do trừ điểm.
- Đưa ra nhận xét bằng tiếng Việt.
- Không tự bịa đáp án hoặc tiêu chí.
- Trả về kết quả chấm tham khảo.
- Khi độ tin cậy thấp phải báo cần kiểm tra thủ công.
- Có chức năng yêu cầu xem xét lại kết quả.
- Kết quả AI không được tự nhận là điểm chính thức của giáo viên.
- Có kiểm tra cấu trúc JSON, giới hạn điểm và log phiên bản model.

Nếu câu hỏi không có rubric hoặc đáp án đáng tin cậy, hệ thống không được âm thầm sinh ra điểm số chính thức.

### Chế độ C — Chấm bài bằng ảnh

Học sinh được:

- Chụp ảnh bài làm.
- Chọn ảnh từ thư viện.
- Xem trước và cắt ảnh.
- Xác nhận gửi chấm.

Quy trình:

Ảnh → OCR → Trích xuất nội dung → Hiển thị bản nhận dạng để sửa → Xác định câu hỏi → Chọn phương thức chấm → Tạo nhận xét.

Yêu cầu:

- Hỗ trợ chữ viết tay ở mức có thể.
- Hỗ trợ tiếng Việt.
- Nhận diện công thức toán khi có provider thích hợp.
- Có chỉ báo vùng không đọc rõ.
- Không tự đoán chữ bị mất mà không thông báo.
- Cho học sinh sửa văn bản OCR trước khi chấm.
- Ẩn hoặc loại bỏ thông tin cá nhân không cần thiết.
- Quản lý thời hạn lưu/xóa ảnh.

Nếu OCR thất bại, cho phép nhập nội dung thủ công.

### Chế độ D — AI giải thích đáp án

AI có thể giải thích:

- Vì sao đáp án đúng.
- Vì sao lựa chọn khác sai.
- Hướng giải từng bước.
- Kiến thức cần ôn lại.
- Cách giải khác nếu phù hợp.

Giải thích phải dựa trên đáp án đã được kiểm duyệt.

Không cung cấp lời giải thiếu kiểm chứng như một sự thật chắc chắn. Có nút báo lỗi giải thích AI.

---

## 7. Chiến lược xây dựng DATASET

Đây là phần đặc biệt quan trọng.

Không xây dựng dataset bằng cách tải hàng loạt tài liệu từ internet rồi tự động công khai toàn bộ.

Phải thiết kế một hệ thống thu thập, chuẩn hóa, quản lý quyền sử dụng, kiểm duyệt và cập nhật dữ liệu.

### 7.1. Nguồn dữ liệu

Chia dữ liệu thành các nguồn:

**Nguồn 1 — Nội dung tự biên soạn**
- Câu hỏi và bài tập do nhóm phát triển tạo.
- Bộ đề do giáo viên cộng tác tự biên soạn.
- Nội dung được kiểm duyệt trước khi phát hành.

**Nguồn 2 — Dữ liệu có giấy phép**
- Bộ câu hỏi có giấy phép cho phép sử dụng.
- Tài liệu Creative Commons phù hợp.
- Nội dung được chủ sở hữu cấp phép bằng văn bản.
- Dữ liệu Open Educational Resources đủ điều kiện.

**Nguồn 3 — Trang thông tin giáo dục**
- Website của cơ quan giáo dục.
- Website trường học.
- Kho đề thi và tài liệu giáo dục.
- Nguồn phát hành đề tham khảo hoặc đề thi công khai.

Với nhóm này, phải kiểm tra điều khoản sử dụng và quyền tái phân phối cụ thể. Việc một tài liệu được xem miễn phí không đồng nghĩa được phép sao chép vào ứng dụng.

**Nguồn 4 — Tài liệu do người dùng cung cấp**
- Giáo viên tải đề do họ sở hữu hoặc được phép sử dụng.
- Học sinh đưa đề của mình vào không gian xử lý riêng.
- Nội dung riêng tư không tự động xuất bản thành tài liệu công cộng.
- Nội dung muốn chia sẻ phải qua bước xác nhận quyền và kiểm duyệt.

Không sao chép trái phép sách giáo khoa, sách giải, bộ đề thương mại hoặc nội dung có bản quyền.

### 7.2. Discovery và Ingestion Pipeline

Thiết kế pipeline:

```text
Source Discovery
       ↓
License Verification
       ↓
Source Registration
       ↓
Authorized Download / Import
       ↓
PDF / DOCX / Image Parser
       ↓
OCR (nếu cần)
       ↓
Question Extraction
       ↓
AI Structured Parsing
       ↓
Normalization
       ↓
Duplicate Detection
       ↓
Answer & Rubric Validation
       ↓
Human Review
       ↓
Publish
       ↓
Search Index
```

Crawler phải:

- Chỉ truy cập nguồn được cho phép.
- Tuân thủ điều khoản website và robots.txt.
- Có rate limiting.
- Không vượt CAPTCHA hoặc cơ chế bảo vệ truy cập.
- Không tải nội dung sau paywall khi chưa được cấp quyền.
- Không bỏ qua bước kiểm tra giấy phép.
- Không tự công khai dữ liệu trích xuất.
- Lưu URL, ngày truy cập và bằng chứng cấp phép.
- Có cơ chế báo cáo và gỡ nội dung bị khiếu nại.

Nếu website không cho phép sao chép/tái phân phối, chỉ được lưu metadata và liên kết khi việc liên kết hợp lệ.

### 7.3. Xử lý tài liệu

Hỗ trợ đầu vào:

- PDF text-based.
- PDF scan.
- DOCX.
- TXT.
- CSV.
- JSON.
- Hình ảnh PNG/JPG.

Phải xây dựng parser phát hiện:

- Tên đề.
- Môn.
- Lớp.
- Năm học.
- Loại kiểm tra.
- Thời gian làm bài.
- Số câu.
- Nội dung từng câu.
- Các phương án trả lời.
- Đáp án.
- Thang điểm.
- Lời giải nếu có.

Các công thức toán, bảng, hình học, sơ đồ và hình ảnh không được tự động chuyển đổi gây sai nội dung mà không có kiểm tra.

Những phần không đọc được phải đưa vào hàng chờ kiểm duyệt.

### 7.4. Chất lượng dataset

Mỗi câu hỏi phải được kiểm tra:

- Đúng chương trình học.
- Đúng môn và lớp.
- Không sai kiến thức.
- Không sai dữ kiện.
- Có đáp án hợp lệ nếu được chấm tự động.
- Không trùng lặp quá mức.
- Có nguồn và quyền sử dụng rõ ràng.
- Phù hợp lứa tuổi.
- Không chứa thông tin cá nhân.
- Không chứa hướng dẫn không an toàn.

Thêm cơ chế:

- Normalized text hash.
- Perceptual hash cho ảnh.
- Similarity detection.
- Duplicate review.
- Version control.
- Content quality scoring.
- Approval workflow.

Trạng thái:

`draft → parsed → needs_review → approved → published`

Cho phép `rejected`, `archived`, `takedown`.

Chỉ nội dung published và đủ quyền sử dụng mới hiển thị công khai.

---

## 8. Thiết kế Database

Sử dụng PostgreSQL và tạo migrations có thể chạy lại an toàn.

Các bảng chính:

```text
users
user_profiles
parent_child_links
roles
grades
education_programs
subjects
grade_subjects
textbook_series
chapters
topics
lessons
documents
content_sources
source_licenses
source_permissions
questions
question_options
question_answers
question_rubrics
question_versions
question_assets
exams
exam_sections
exam_questions
exam_versions
exam_attempts
student_answers
grading_results
grading_details
ai_grading_jobs
ai_feedback_reports
study_progress
bookmarks
content_reviews
content_reports
copyright_takedowns
import_jobs
import_logs
audit_logs
```

Thiết kế quan hệ hợp lý, không tạo bảng thừa nếu có thể chuẩn hóa.

Các bảng quan trọng cần có:

**questions**
- id
- subject_id
- grade_id
- topic_id
- type
- difficulty
- content
- assets
- source_id
- copyright_status
- quality_status
- created_at
- updated_at

**exams**
- id
- title
- subject_id
- grade_id
- education_program_id
- school_year
- semester
- exam_type
- duration_minutes
- total_score
- publication_status
- source_id

**grading_results**
- id
- attempt_id
- grading_method
- raw_score
- final_score
- max_score
- feedback
- confidence
- grading_status
- rubric_version
- model_version
- created_at

Bổ sung đầy đủ các khóa ngoại, chỉ mục, ràng buộc dữ liệu và quyền truy cập.

Lưu cả nguồn gốc đáp án, phiên bản đáp án và người duyệt.

Dùng RLS để:

- Học sinh chỉ xem kết quả của mình.
- Phụ huynh chỉ xem dữ liệu của trẻ được liên kết hợp lệ.
- Giáo viên chỉ truy cập dữ liệu trong phạm vi được cấp.
- Admin được quản lý qua quyền server-side.
- Người dùng không được đọc đáp án bí mật trước khi nộp bài qua API.
- Không cho phép tự nâng role hoặc sửa điểm từ client.

---

## 9. Dataset mẫu và bộ công cụ nhập liệu

Hãy tạo:

1. JSON Schema cho từng loại câu hỏi.
2. JSON Schema cho đề thi.
3. JSON Schema cho đáp án và rubric.
4. Template CSV nhập câu hỏi.
5. Template CSV nhập đề thi.
6. CLI nhập dữ liệu.
7. CLI kiểm tra chất lượng dữ liệu.
8. CLI phát hiện trùng lặp.
9. Trang admin xem bản preview trước khi duyệt.
10. Báo cáo import thành công/thất bại.

Ví dụ JSON:

```json
{
  "id": "math5_decimal_001",
  "grade": 5,
  "subject": "toan",
  "topic": "so_thap_phan",
  "type": "single_choice",
  "difficulty": "easy",
  "question": "Làm tròn số 12,648 đến hàng phần mười.",
  "options": [
    {"id": "A", "text": "12,6"},
    {"id": "B", "text": "12,7"},
    {"id": "C", "text": "12,64"},
    {"id": "D", "text": "12,65"}
  ],
  "correct_answer": ["A"],
  "max_score": 1,
  "explanation": "Chữ số hàng phần trăm là 4 nên giữ nguyên hàng phần mười.",
  "source_type": "original",
  "license": "original_content",
  "review_status": "approved"
}
```

Ví dụ chỉ mang tính minh họa; hãy chuẩn hóa thành schema thực tế.

Tạo tối thiểu 60 câu hỏi mẫu **tự biên soạn**, phân bổ trên nhiều lớp và dạng câu hỏi, gồm câu trắc nghiệm, đúng/sai, trả lời ngắn và tự luận có rubric.

Chú trọng bài tập Toán có:
- Số thập phân.
- Phân số.
- Đổi đơn vị.
- Diện tích ha và km².
- Hình học.
- Phương trình.
- Hàm số.

Không tuyên bố đây là dataset chính thức của Bộ Giáo dục.

Seed metadata cho lớp 1–12 và những môn học tương ứng. Không tự tạo hàng nghìn câu hỏi chất lượng thấp chỉ để đạt số lượng.

---

## 10. Admin Dashboard

Xây dựng hệ thống quản trị có đăng nhập an toàn.

Các màn hình:

- Tổng quan số liệu.
- Quản lý lớp học.
- Quản lý môn học.
- Quản lý chương/chủ đề.
- Quản lý tài liệu.
- Quản lý câu hỏi.
- Quản lý bộ đề.
- Quản lý đáp án và rubric.
- Quản lý nguồn và giấy phép.
- Nhập CSV/JSON/PDF được phép.
- Hàng chờ kiểm duyệt.
- Quản lý báo cáo nội dung AI.
- Quản lý yêu cầu gỡ tài liệu.
- Theo dõi lỗi và hoạt động import.

Cho phép người quản trị:

- Chỉnh sửa nội dung.
- Duyệt câu hỏi.
- Sửa đáp án sai.
- Xuất dữ liệu.
- Nhập dữ liệu hàng loạt.
- Quản lý trạng thái công khai.
- Xem lịch sử thay đổi.
- Quay lại phiên bản trước.

Không cho phép xuất bản tài liệu khi trạng thái bản quyền chưa được xác nhận.

---

## 11. Quyền riêng tư và bảo vệ học sinh

Do ứng dụng phục vụ cả trẻ em, cần thiết kế privacy-first.

Các yêu cầu:

- Cho phép học sinh dùng chức năng cơ bản không cần tài khoản.
- Không bắt buộc nhập họ tên, số điện thoại, trường học hoặc ngày sinh đầy đủ.
- Tiến độ khách có thể lưu cục bộ.
- Không có chat công khai hoặc nhắn tin giữa người lạ trong MVP.
- Không thu thập vị trí.
- Không sử dụng quảng cáo cá nhân hóa cho trẻ em.
- Không đưa API key vào ứng dụng.
- Không gửi bài làm và thông tin cá nhân cho AI provider mà không có cơ sở xử lý phù hợp.
- Giới hạn thời gian lưu ảnh bài làm.
- Hỗ trợ xóa dữ liệu.
- Có chức năng xóa tài khoản nếu cho phép đăng ký.
- Có cơ chế đồng ý và đại diện hợp lệ khi xử lý dữ liệu của trẻ em theo pháp luật áp dụng.
- Có Privacy Policy và Terms of Use.
- Có kênh báo cáo nội dung sai, không phù hợp hoặc do AI tạo.
- Không tự động sử dụng bài làm của học sinh để huấn luyện AI.

Tuân thủ Google Play Families Policy và pháp luật bảo vệ dữ liệu cá nhân Việt Nam đang có hiệu lực.

MVP không tích hợp SDK quảng cáo để giảm độ phức tạp tuân thủ.

Thiết kế cơ chế kiểm soát độ tuổi phù hợp, không thu thập tuổi chi tiết nếu không cần.

---

## 12. Tối ưu chi phí AI

Thiết kế theo nguyên tắc không sử dụng AI nếu có thể chấm bằng thuật toán hoặc đáp án chuẩn.

Ưu tiên:

- Trắc nghiệm: chấm local/backend xác định.
- Đúng/Sai: chấm xác định.
- Phép tính: SymPy/logic.
- OCR: chỉ gọi khi người dùng yêu cầu.
- Tự luận: gọi AI khi cần.
- Giải thích: ưu tiên lời giải đã lưu.
- Cache lời giải cho câu hỏi công khai nếu phù hợp.
- Rate limiting.
- Token budgeting.
- Giới hạn kích thước ảnh.
- Retry có kiểm soát.
- Theo dõi chi phí theo chức năng.
- Chống spam yêu cầu AI.
- Có quota cấu hình trên server.

Tạo bảng log chi phí AI và báo cáo chi phí ước tính theo 100, 1.000 và 10.000 người dùng hoạt động.

Không tự bịa giá API. Đưa đơn giá thành biến cấu hình để cập nhật.

Khi API không hoạt động, những chức năng chấm theo đáp án có sẵn vẫn phải sử dụng được.

---

## 13. UI/UX

Phong cách thiết kế:

- Hiện đại.
- Tối giản.
- Dễ đọc.
- Ưu tiên điện thoại Android.
- Trẻ trung nhưng không quá nhiều màu sắc.
- Điều hướng trực quan.
- Phù hợp cả học sinh nhỏ tuổi và học sinh THPT.

Màu chủ đạo đề xuất: xanh dương, trắng và các màu phụ nhẹ.

Thiết kế:

- Onboarding.
- Chọn lớp.
- Trang chủ.
- Danh sách môn học.
- Kho tài liệu.
- Chi tiết tài liệu.
- Danh sách đề.
- Màn hình làm bài.
- Màn hình chấm bài.
- Chi tiết kết quả.
- Lịch sử học tập.
- Hồ sơ.
- Cài đặt.
- Thông tin quyền riêng tư.

Tạo các trạng thái đầy đủ:

- Loading.
- Empty.
- Error.
- Offline.
- Không tìm thấy dữ liệu.
- Chờ chấm.
- AI không khả dụng.
- Bài làm cần kiểm tra thủ công.

Tối ưu accessibility, kích thước chữ và contrast, đặc biệt với học sinh tiểu học.

---

## 14. Lộ trình phát triển

Chia làm bốn giai đoạn.

### Giai đoạn 1 — MVP chạy được

Ưu tiên:

- Flutter Android.
- Database.
- Seed danh mục lớp 1–12.
- Danh mục môn học tương ứng.
- Kho tài liệu.
- Tìm kiếm.
- Bộ đề.
- Làm trắc nghiệm.
- Đúng/Sai.
- Điền đáp án ngắn.
- Chấm tự động theo đáp án.
- Xem lời giải.
- Lịch sử bài làm cục bộ.
- Admin nhập và duyệt nội dung.
- Dataset mẫu tự biên soạn.
- Unit tests.

Nội dung thực tế trong MVP chỉ cần triển khai thí điểm chất lượng cao cho Toán, Tiếng Việt/Ngữ văn và Tiếng Anh ở một số lớp đại diện như 1, 5, 9 và 12.

Toàn bộ hệ thống phải sẵn sàng mở rộng đến các lớp và môn còn lại mà không phải thiết kế lại.

### Giai đoạn 2 — Tích hợp AI

- OCR đề thi.
- Chụp ảnh bài làm.
- Chấm tự luận có rubric.
- Giải thích lời giải.
- Báo lỗi AI.
- Confidence threshold.
- Theo dõi chi phí.
- Kiểm thử độ chính xác trên dataset được chuyên môn kiểm duyệt.

### Giai đoạn 3 — Hoàn thiện nền tảng

- Dashboard giáo viên.
- Dashboard phụ huynh.
- Đồng bộ tiến độ đa thiết bị.
- Ngân hàng câu hỏi lớn.
- Đề luyện tập cá nhân hóa.
- Phân tích năng lực học sinh.
- Gợi ý chủ đề cần ôn.
- Mở rộng tất cả môn và lớp.
- Caching và offline mode nâng cao.

### Giai đoạn 4 — Production

- Bảo mật và kiểm thử tải.
- Kiểm tra chính sách Google Play.
- Hoàn thiện Privacy Policy.
- Kiểm thử trên nhiều thiết bị.
- Tối ưu hiệu năng.
- Build Android App Bundle.
- Phát hành kiểm thử.
- Xử lý phản hồi.
- Phát hành chính thức.

Không xây dựng tất cả chức năng ở mức sơ sài cùng lúc. Hoàn thành MVP có thể dùng được trước.

---

## 15. Yêu cầu đưa lên Google Play

Thời điểm tham chiếu: tháng 10/2026.

Ứng dụng phải được xây dựng để đáp ứng các yêu cầu kỹ thuật và chính sách hiện hành.

Các điểm cần chuẩn bị:

- Android 16, target API level 36 trở lên theo yêu cầu dành cho ứng dụng Android mới.
- Flutter/Android Gradle Plugin tương thích.
- Android App Bundle (.aab).
- Application ID không trùng ứng dụng khác.
- App signing và bảo vệ signing keys.
- Tên ứng dụng và logo.
- Short Description.
- Full Description.
- Screenshots từ ứng dụng thực tế.
- Feature Graphic nếu được yêu cầu.
- Privacy Policy URL công khai.
- Terms of Use.
- Email hỗ trợ.
- Data Safety declaration.
- Target Audience and Content.
- Content Rating.
- Families Policy nếu nhắm đến trẻ em.
- Khai báo tính năng AI và cơ chế báo cáo nội dung do AI tạo theo chính sách áp dụng.
- Khai báo SDK, quyền truy cập và các loại dữ liệu xử lý.
- Chức năng yêu cầu xóa tài khoản trong app và qua web khi áp dụng.
- Tài khoản demo để nhân viên Google kiểm tra nếu ứng dụng có khu vực đăng nhập.
- Kiểm tra quyền sở hữu nội dung.
- Không đưa dữ liệu có bản quyền chưa được phép phân phối vào app.
- Không tuyên bố liên kết chính thức với Bộ Giáo dục hoặc tổ chức khác nếu không có căn cứ.

Với tài khoản nhà phát triển cá nhân mới thuộc diện áp dụng, lên kế hoạch kiểm thử kín tối thiểu 12 người tham gia liên tục trong ít nhất 14 ngày trước khi đăng ký quyền phát hành production.

Tạo tài liệu hướng dẫn đăng ký Google Play Console, gồm phí đăng ký một lần 25 USD, xác minh danh tính và các bước phát hành.

Nếu sau này triển khai gói Premium hoặc bán tính năng số, cần thiết kế tích hợp Google Play Billing theo chính sách áp dụng; chưa cần triển khai thanh toán trong MVP.

Tham khảo chính sách gốc:

- https://support.google.com/googleplay/android-developer/answer/11926878
- https://support.google.com/googleplay/android-developer/answer/14151465
- https://support.google.com/googleplay/android-developer/answer/9893335
- https://support.google.com/googleplay/android-developer/answer/13985936
- https://support.google.com/googleplay/android-developer/answer/10787469
- https://support.google.com/googleplay/android-developer/answer/13327111
- https://support.google.com/googleplay/android-developer/answer/6112435

Kiểm tra lại chính sách tại thời điểm phát hành, không xem checklist này là sự bảo đảm sẽ được Google phê duyệt.

---

## 16. Bảo mật và kiểm thử

Yêu cầu:

- Supabase RLS.
- API authentication.
- Server-side authorization.
- Validation input.
- Rate limiting.
- File upload validation.
- MIME type và kích thước file.
- Chống SQL Injection.
- Chống XSS trên admin.
- Không lộ thông tin đáp án trước khi nộp bài.
- Ngăn sửa điểm trái phép.
- Secret management.
- Audit log.
- CORS cấu hình chặt.
- Backup database.
- Chính sách lưu và xóa dữ liệu.
- Giới hạn chi phí và chống lạm dụng AI.

Viết automated tests cho:

- Chấm trắc nghiệm.
- Chấm nhiều đáp án.
- Đúng/Sai từng nhận định.
- Phân số.
- Số thập phân.
- Đổi đơn vị.
- Sai số làm tròn.
- Chấm theo rubric.
- Import JSON/CSV.
- Phát hiện trùng lặp.
- Phân quyền.
- Không rò rỉ đáp án.
- API errors.
- OCR/AI provider failure.
- Xóa dữ liệu người dùng.

Tích hợp GitHub Actions cho lint, test và kiểm tra build.

---

## 17. Tiêu chí nghiệm thu MVP

MVP được xem là hoàn thành khi:

1. Có thể build và chạy ứng dụng Flutter trên Android.
2. Người dùng có thể chọn lớp và môn học.
3. Người dùng có thể xem và tìm kiếm tài liệu mẫu.
4. Có thể mở một đề kiểm tra.
5. Có thể làm và nộp bài trắc nghiệm.
6. Hệ thống chấm điểm chính xác theo đáp án chuẩn.
7. Có thể xem giải thích sau khi nộp.
8. Có thể xem lịch sử bài làm.
9. Quản trị viên có thể nhập câu hỏi từ JSON/CSV.
10. Quản trị viên có thể duyệt, sửa và xuất bản câu hỏi.
11. Dữ liệu chưa được kiểm duyệt không hiển thị công khai.
12. Các chính sách RLS được kiểm thử.
13. Backend không lộ API keys.
14. Có cơ chế xử lý trạng thái offline/lỗi mạng.
15. Có hướng dẫn cài đặt và chạy thực tế.
16. Có bộ seed câu hỏi gốc dùng để demo.
17. Có thể tạo bản build Android phục vụ kiểm thử.
18. Những chức năng chưa hoàn thành phải được ghi rõ, không hiển thị như đã hoạt động.

---

## 18. Deliverables

Hãy tạo trong repository:

**Source code**
- Flutter mobile application.
- Backend FastAPI.
- Next.js Admin Dashboard.
- Database migrations.
- RLS policies.
- Dataset pipeline.
- Sample dataset.
- Automated tests.

**Documents**
- `docs/PRODUCT_PLAN.md`
- `docs/ARCHITECTURE.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/DATASET_STRATEGY.md`
- `docs/DATA_SOURCES_AND_LICENSES.md`
- `docs/AI_GRADING_DESIGN.md`
- `docs/SECURITY_AND_PRIVACY.md`
- `docs/PLAY_STORE_CHECKLIST.md`
- `docs/ROADMAP.md`
- `docs/API_DOCUMENTATION.md`
- `docs/TEST_PLAN.md`
- `docs/COST_ESTIMATION.md`
- `README.md`

**Deployment**
- `.env.example`
- Database setup instructions.
- Supabase setup instructions.
- Backend deployment instructions.
- Admin deployment instructions.
- Flutter build instructions.
- Android AAB release instructions.

Không đưa credentials, tài khoản thật hoặc private keys vào repository.

---

## 19. Phương pháp làm việc của Codex

Hãy thực hiện theo thứ tự:

**Bước 1:** Kiểm tra repository hiện tại. Nếu trống, khởi tạo monorepo.

**Bước 2:** Xây dựng PRODUCT_PLAN, ARCHITECTURE, DATABASE_SCHEMA và DATASET_STRATEGY.

**Bước 3:** Tạo database migrations, RLS và dữ liệu seed.

**Bước 4:** Xây dựng backend, API và các bộ chấm điểm xác định.

**Bước 5:** Xây dựng ứng dụng Flutter với giao diện hoàn chỉnh cho MVP.

**Bước 6:** Xây dựng Admin Dashboard, cho phép nhập và kiểm duyệt dataset.

**Bước 7:** Viết test, chạy lint và kiểm tra tính năng thực tế.

**Bước 8:** Hoàn thiện README, cấu hình môi trường và hướng dẫn build.

**Bước 9:** Chuẩn bị interface tích hợp AI và tài liệu cho giai đoạn 2, không xây dựng giả một dịch vụ AI hoạt động khi chưa được cấu hình provider.

Ở mỗi bước:

- Tạo hoặc sửa các file thật trong repository.
- Thực thi lệnh kiểm thử trong khả năng môi trường.
- Sửa lỗi phát hiện được.
- Ghi rõ phần đã hoàn thành và phần chưa hoàn thành.
- Không chỉ trả lời bằng ý tưởng hoặc pseudocode.
- Không tuyên bố thành công nếu build/test chưa chạy.
- Không tạo nút bấm giả không có hành động.
- Không tự ý sử dụng dịch vụ trả phí.
- Không yêu cầu tôi cung cấp secret trong chat; sử dụng placeholder và hướng dẫn cấu hình an toàn.
- Ưu tiên quyết định kỹ thuật hợp lý thay vì liên tục hỏi những chi tiết nhỏ.

Nếu khối lượng quá lớn để thực hiện trong một lượt, hãy ưu tiên hoàn thiện từng module có thể chạy, giữ repository nhất quán và cập nhật tiến độ trong tài liệu.

## 20. YÊU CẦU BẮT ĐẦU NGAY

Hãy bắt đầu bằng cách:

1. Đề xuất kiến trúc MVP và sơ đồ các thành phần.
2. Xác định database schema và quan hệ chính.
3. Thiết kế dataset schema và quy trình kiểm duyệt.
4. Tạo cấu trúc project.
5. Khởi tạo Flutter, backend, admin và database.
6. Viết chức năng đầu tiên: chọn lớp → chọn môn → chọn đề → làm bài → chấm điểm → xem kết quả.
7. Chạy kiểm thử luồng này bằng dataset mẫu.

Mục tiêu quan trọng nhất là có một ứng dụng Android thực sự sử dụng được, có nền tảng nội dung hợp pháp, khả năng chấm điểm đáng tin cậy và có thể mở rộng thành hệ sinh thái học tập lớp 1–12.

**BẮT ĐẦU TRIỂN KHAI GIAI ĐOẠN 1 NGAY TRÊN REPOSITORY.**