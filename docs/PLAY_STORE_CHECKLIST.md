# Google Play — chưa sẵn sàng phát hành

Chưa đăng ký Play Console, chưa ký hoặc tải AAB lên Google Play. Kiểm tra chính sách gốc tại ngày phát hành: target API, Families, AI content reporting, Data Safety, account deletion, closed testing và Play Billing nếu bán tính năng số.

Cần application ID chính thức (vn.khohoc.kho_hoc_mobile hiện là ID phát triển), logo, screenshot thực tế, Privacy Policy URL/Terms, email hỗ trợ, content rating, đối tượng độ tuổi, SDK inventory và quyền nội dung. Android API 36 là mục tiêu trong yêu cầu dự án; xác minh lại tại thời điểm release.

Signing keys/keystore ở secret storage ngoài Git. Không dùng debug signing cho release production. Sau khi toolchain Android sẵn sàng, chạy flutter build appbundle --release sau khi cấu hình ký. Flutter template development chưa đủ cho release.

Tài khoản Play Console: phí tham chiếu 25 USD một lần; yêu cầu xác minh danh tính và kiểm thử kín 12 tester/14 ngày cho tài khoản thuộc diện áp dụng cần kiểm tra lại trên nguồn gốc: https://support.google.com/googleplay/android-developer/answer/6112435 và https://support.google.com/googleplay/android-developer/answer/14151465 . Không tự thanh toán phí hoặc xuất bản.
