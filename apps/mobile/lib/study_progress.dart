import 'repository.dart';

class TopicProgress {
  TopicProgress(this.grade, this.subject, this.topic, this.name);
  final int grade;
  final String subject, topic, name;
  int attempted = 0, correct = 0;
  double score = 0, maxScore = 0;
  final wrongQuestionIds = <String>[];
  double get percent => maxScore == 0 ? 0 : 100 * score / maxScore;
}

class StudyProgress {
  StudyProgress(this.completed, this.graded, this.averagePercent, this.topics);
  final int completed, graded;
  final double? averagePercent;
  final List<TopicProgress> topics;

  /// Local history is newest first. Only the latest answer to each question
  /// contributes to topic progress, including partial-credit true/false items.
  factory StudyProgress.fromHistory(List<Json> history) {
    final groups = <String, TopicProgress>{};
    final seen = <String>{};
    int completed = 0, graded = 0;
    double percentSum = 0;
    for (final row in history) {
      final result = row['result'];
      if (result is! Map) continue;
      completed++;
      final score = result['score'], maxScore = result['max_score'];
      if (score is num &&
          maxScore is num &&
          maxScore > 0 &&
          score >= 0 &&
          score <= maxScore) {
        graded++;
        percentSum += 100 * score / maxScore;
      }
      final questions = {
        for (final q in row['questions'] as List? ?? [])
          if (q is Map) q['id']: q,
      };
      for (final detail in result['details'] as List? ?? []) {
        if (detail is! Map) continue;
        final q = questions[detail['question_id']];
        if (q is! Map ||
            q['grade'] is! int ||
            q['subject'] is! String ||
            q['topic'] is! String) {
          continue;
        }
        final grade = q['grade'] as int;
        final subject = q['subject'] as String, topic = q['topic'] as String;
        final identity = '${row['backend_url']}/$grade/$subject/${q['id']}';
        if (!seen.add(identity)) continue;
        final earned = detail['score'], possible = detail['max_score'];
        if (earned is! num ||
            possible is! num ||
            possible <= 0 ||
            earned < 0 ||
            earned > possible) {
          continue;
        }
        final key = '$grade/$subject/$topic';
        final group = groups.putIfAbsent(
          key,
          () => TopicProgress(
            grade,
            subject,
            topic,
            q['topic_name'] as String? ??
                legacyTopicNames[topic] ??
                topic.replaceAll('_', ' '),
          ),
        );
        group.attempted++;
        group.score += earned;
        group.maxScore += possible;
        if (earned == possible) {
          group.correct++;
        } else {
          group.wrongQuestionIds.add(q['id'] as String);
        }
      }
    }
    final topics = groups.values.toList()
      ..sort((a, b) {
        final accuracy = a.percent.compareTo(b.percent);
        return accuracy != 0
            ? accuracy
            : '${a.grade}/${a.subject}/${a.topic}'.compareTo(
                '${b.grade}/${b.subject}/${b.topic}',
              );
      });
    return StudyProgress(
      completed,
      graded,
      graded == 0 ? null : percentSum / graded,
      topics,
    );
  }
}

// Labels also cover saved attempts from versions before topic_name was returned.
const legacyTopicNames = {
  "natural": "Số tự nhiên",
  "operations": "Thứ tự thực hiện phép tính",
  "fraction": "Rút gọn phân số",
  "decimal_fraction": "Phân số thập phân",
  "fraction_ops": "Phép tính với phân số",
  "unlike_fraction": "Phân số khác mẫu",
  "mixed": "Hỗn số",
  "plane": "Chu vi và diện tích",
  "decimal": "Số thập phân",
  "compare_decimal": "So sánh số thập phân",
  "measure_decimal": "Số đo thập phân",
  "round": "Làm tròn số",
  "land_area": "Đơn vị đo diện tích đất",
  "area_units": "Đổi đơn vị diện tích",
  "add_decimal": "Cộng số thập phân",
  "subtract_decimal": "Trừ số thập phân",
  "multiply_decimal": "Nhân số thập phân",
  "divide_decimal": "Chia số thập phân",
  "powers_ten": "Nhân chia với lũy thừa của 10",
  "triangle": "Diện tích tam giác",
  "trapezoid": "Diện tích hình thang",
  "circle": "Hình tròn",
  "drawing": "Vẽ và ghép hình",
  "ratio": "Tỉ số phần trăm",
  "map": "Tỉ lệ bản đồ",
  "sum_ratio": "Tìm hai số biết tổng và tỉ số",
  "difference_ratio": "Tìm hai số biết hiệu và tỉ số",
  "percentage_value": "Giá trị phần trăm",
  "calculator": "Sử dụng máy tính",
  "volume": "Thể tích",
  "volume_units": "Đơn vị thể tích",
  "nets": "Hình khai triển",
  "box_area": "Diện tích hình hộp chữ nhật",
  "cube_area": "Diện tích hình lập phương",
  "box_volume": "Thể tích hình hộp chữ nhật",
  "cube_volume": "Thể tích hình lập phương",
  "time_units": "Đơn vị thời gian",
  "time_add": "Cộng trừ thời gian",
  "time_multiply": "Nhân chia thời gian",
  "speed": "Quãng đường và vận tốc",
  "data": "Thu thập số liệu",
  "pie": "Biểu đồ hình quạt",
  "frequency": "Tỉ số số lần xuất hiện",
  "am_van": "Âm và vần",
  "bai_toan": "Bài toán",
  "bien_phap_tu_tu": "Biện pháp tu từ",
  "cau_tao_so": "Cấu tạo số",
  "dai_so": "Đại số",
  "danh_gia_bang_chung": "Đánh giá bằng chứng",
  "dau_cau": "Dấu câu",
  "day_so": "Dãy số",
  "doc_hieu": "Đọc hiểu",
  "doc_tieng": "Đọc tiếng",
  "lap_luan": "Lập luận",
  "lien_ket_lap_luan": "Liên kết lập luận",
  "loi_dan": "Lời dẫn",
  "luan_cu": "Luận cứ",
  "luan_de": "Luận đề",
  "mu_logarit": "Mũ và logarit",
  "ngoi_ke": "Ngôi kể",
  "nguyen_ham": "Nguyên hàm",
  "phan_biet_y_kien_su_kien": "Phân biệt ý kiến và sự kiện",
  "phep_cong": "Phép cộng",
  "phep_lien_ket": "Phép liên kết",
  "phep_tru": "Phép trừ",
  "quan_he_tu": "Quan hệ từ",
  "so_tu_nhien": "Số tự nhiên",
  "suy_luan": "Suy luận",
  "thanh_phan_cau": "Thành phần câu",
  "thoi_gian": "Thời gian",
  "thong_ke": "Thống kê",
  "toa_do": "Tọa độ",
  "tu_trai_nghia": "Từ trái nghĩa",
  "ATP": "ATP",
  "DNA": "DNA",
  "pH": "pH",
  "academic_reading": "Đọc hiểu học thuật",
  "reading": "Đọc hiểu tiếng Anh",
  "reading_evidence": "Đọc hiểu: dẫn chứng",
  "reading_inference": "Đọc hiểu: suy luận",
  "reading_main_idea": "Đọc hiểu: ý chính",
  "reading_scope": "Đọc hiểu: phạm vi",
  "vocabulary": "Từ vựng",
  "be": "Động từ to be",
  "be_verb": "Động từ to be",
  "greetings": "Chào hỏi",
  "numbers": "Số đếm",
  "past_simple": "Thì quá khứ đơn",
  "present_simple": "Thì hiện tại đơn",
  "present_perfect": "Thì hiện tại hoàn thành",
  "past_perfect": "Thì quá khứ hoàn thành",
  "plural_nouns": "Danh từ số nhiều",
  "possessive_adjectives": "Tính từ sở hữu",
  "prepositions": "Giới từ",
  "comparatives": "So sánh hơn",
  "conditionals": "Câu điều kiện",
  "first_conditional": "Câu điều kiện loại 1",
  "second_conditional": "Câu điều kiện loại 2",
  "third_conditional": "Câu điều kiện loại 3",
  "passive_voice": "Câu bị động",
  "relative_clauses": "Mệnh đề quan hệ",
  "reported_speech": "Câu tường thuật",
  "modals": "Động từ khuyết thiếu",
  "concession": "Mệnh đề nhượng bộ",
  "cohesion": "Liên kết văn bản",
  "chuyen_dong": "Chuyển động",
  "hinh_hoc": "Hình học",
  "so_hoc": "Số học",
  "phan_so": "Phân số",
  "ham_so": "Hàm số",
  "dao_ham": "Đạo hàm",
  "tich_phan": "Tích phân",
  "phuong_trinh": "Phương trình",
  "xac_suat": "Xác suất",
  "tong_hop": "Ôn tổng hợp",
  "kien_thuc_nen": "Kiến thức nền",
};

const subjectNames = {
  "toan": "Toán",
  "tieng_viet": "Tiếng Việt",
  "dao_duc": "Đạo đức",
  "the_chat": "Giáo dục thể chất",
  "nghe_thuat": "Nghệ thuật",
  "trai_nghiem": "Hoạt động trải nghiệm",
  "tu_nhien_xa_hoi": "Tự nhiên và Xã hội",
  "tieng_anh": "Tiếng Anh",
  "tin_hoc_cong_nghe": "Tin học và Công nghệ",
  "khoa_hoc": "Khoa học",
  "lich_su_dia_li": "Lịch sử và Địa lí",
  "ngu_van": "Ngữ văn",
  "khoa_hoc_tu_nhien": "Khoa học tự nhiên",
  "tin_hoc": "Tin học",
  "cong_nghe": "Công nghệ",
  "gdcd": "Giáo dục công dân",
  "huong_nghiep": "Hoạt động trải nghiệm, hướng nghiệp",
  "lich_su": "Lịch sử",
  "quoc_phong": "Giáo dục quốc phòng và an ninh",
  "dia_li": "Địa lí",
  "vat_li": "Vật lí",
  "hoa_hoc": "Hóa học",
  "sinh_hoc": "Sinh học",
  "kinh_te_phap_luat": "Giáo dục kinh tế và pháp luật",
  "am_nhac": "Âm nhạc",
  "mi_thuat": "Mĩ thuật",
};
