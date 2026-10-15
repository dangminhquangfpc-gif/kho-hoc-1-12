# Chi phí

MVP không gọi AI, không mua dịch vụ và không có API đơn giá giả định. Khi cấu hình provider, đặt input_price_per_million_tokens, output_price_per_million_tokens, OCR_price_per_image, active_users, requests_per_user, average_input_tokens, average_output_tokens và cache_hit_rate.

Chi phí ước tính = active_users × requests_per_user × (1 − cache_hit_rate) × (average_input_tokens × input_price + average_output_tokens × output_price) / 1_000_000 + OCR_count × OCR_price. Tính các kịch bản 100/1.000/10.000 người dùng với thông số đo thực tế. Cần bổ sung bảng log AI cost và quota ở giai đoạn 2. Giá Supabase/hosting phải đối chiếu nhà cung cấp tại thời điểm deploy.
