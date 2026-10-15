"""Deterministic, original topic practice; not a transcription of any textbook."""

from fractions import Fraction as F
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
TOPICS = []


def topic(grade, slug, name, rule, mistake, make):
    TOPICS.append((grade, slug, name, rule, mistake, make))


# Each factory returns a prompt, exact answer, and a worked solution.
topic(
    1,
    "dem_so",
    "Đếm và số liền sau",
    "Số liền sau hơn số đã cho một đơn vị.",
    "Không bỏ qua số khi đếm tiếp.",
    lambda i: (
        f"Số liền sau {i + 10} là số nào?",
        i + 11,
        f"Đếm tiếp một đơn vị: {i + 10} + 1 = {i + 11}.",
    ),
)
topic(
    1,
    "cong_trong_20",
    "Cộng trong phạm vi 20",
    "Cộng là gộp hai nhóm đồ vật hoặc đếm thêm.",
    "Đếm tiếp từ số ban đầu, không đếm lại chính số đó.",
    lambda i: (
        f"Tính {i} + 5.",
        i + 5,
        f"Bắt đầu từ {i}, đếm thêm 5 đơn vị được {i + 5}.",
    ),
)
topic(
    1,
    "tru_trong_20",
    "Trừ trong phạm vi 20",
    "Trừ là bớt đi; có thể kiểm tra bằng phép cộng.",
    "Kết quả phép trừ này không được lớn hơn số ban đầu.",
    lambda i: (
        f"Tính {i + 8} − {i}.",
        8,
        f"Bớt {i} khỏi {i + 8} còn 8; kiểm tra: 8 + {i} = {i + 8}.",
    ),
)
topic(
    1,
    "so_sanh",
    "So sánh hai số",
    "Số đứng sau trên tia số là số lớn hơn.",
    "Đọc yêu cầu tìm số lớn hơn hay nhỏ hơn trước khi trả lời.",
    lambda i: (
        f"Giữa {i + 10} và {i + 7}, số nào lớn hơn?",
        i + 10,
        f"{i + 10} hơn {i + 7} ba đơn vị, nên chọn {i + 10}.",
    ),
)
topic(
    1,
    "chuc_don_vi",
    "Chục và đơn vị",
    "Một chục bằng mười đơn vị.",
    "Một chữ số ở hàng chục không có cùng giá trị với hàng đơn vị.",
    lambda i: (
        f"Số gồm {i % 8 + 1} chục và {i % 10} đơn vị là bao nhiêu?",
        (i % 8 + 1) * 10 + i % 10,
        f"{i % 8 + 1} chục = {(i % 8 + 1) * 10}; thêm {i % 10} đơn vị được {(i % 8 + 1) * 10 + i % 10}.",
    ),
)
topic(
    1,
    "bai_toan_them",
    "Bài toán thêm đồ vật",
    "Tìm số ban đầu và số được thêm, rồi dùng phép cộng.",
    "Viết đúng phép tính và kiểm tra bằng đồ vật.",
    lambda i: (
        f"Lan có {i} nhãn vở, được tặng thêm 3 nhãn vở. Lan có tất cả bao nhiêu nhãn vở? Chỉ nhập số.",
        i + 3,
        f"Số nhãn vở là {i} + 3 = {i + 3}.",
    ),
)

topic(
    2,
    "cong_co_nho",
    "Cộng có nhớ",
    "Cộng hàng đơn vị trước; nếu được ít nhất 10 thì đổi thành một chục.",
    "Không quên cộng phần nhớ vào hàng chục.",
    lambda i: (
        f"Tính tổng {20 + i} + 19.",
        39 + i,
        f"{20 + i} + 19 = {20 + i} + 20 − 1 = {39 + i}.",
    ),
)
topic(
    2,
    "tru_co_nho",
    "Trừ có nhớ",
    "Có thể đổi một chục thành mười đơn vị để trừ.",
    "Không giữ nguyên hàng chục sau khi đã đổi một chục.",
    lambda i: (
        f"Tính hiệu {40 + i} − 18.",
        22 + i,
        f"{40 + i} − 18 = {40 + i} − 20 + 2 = {22 + i}.",
    ),
)
topic(
    2,
    "nhan_2",
    "Phép nhân và bảng nhân 2",
    "Nhân 2 là cộng hai số hạng bằng nhau.",
    "Không nhầm nhân 2 với cộng thêm 2.",
    lambda i: (
        f"Có {i} đôi tất. Mỗi đôi có 2 chiếc. Có tất cả bao nhiêu chiếc tất?",
        2 * i,
        f"{i} nhóm, mỗi nhóm 2 chiếc: 2 × {i} = {2 * i}.",
    ),
)
topic(
    2,
    "chia_2",
    "Chia đều cho 2",
    "Chia đều cho 2 nghĩa là tách thành hai phần bằng nhau.",
    "Kết quả phải nhân lại với 2 để kiểm tra.",
    lambda i: (
        f"Chia đều {2 * i} cái bánh cho 2 bạn. Mỗi bạn được mấy cái?",
        i,
        f"{2 * i} : 2 = {i}; mỗi bạn nhận {i} cái.",
    ),
)
topic(
    2,
    "do_dai",
    "Cộng độ dài",
    "Các độ dài phải cùng đơn vị trước khi cộng.",
    "Không cộng trực tiếp số đo có đơn vị khác nhau.",
    lambda i: (
        f"Hai đoạn dây dài {10 + i} cm và 12 cm. Tổng độ dài là bao nhiêu cm? Chỉ nhập số.",
        22 + i,
        f"Cùng đơn vị cm: {10 + i} + 12 = {22 + i} cm.",
    ),
)
topic(
    2,
    "gio_phut",
    "Giờ và phút",
    "Một giờ bằng 60 phút.",
    "Phân biệt thời điểm trên đồng hồ và khoảng thời gian.",
    lambda i: (
        f"Bắt đầu học lúc 8 giờ, học trong {i * 5} phút. Khi kết thúc, số phút trên đồng hồ là bao nhiêu?",
        i * 5,
        f"{i * 5} phút nhỏ hơn 60 phút; thời điểm kết thúc là 8 giờ {i * 5} phút.",
    ),
)

topic(
    3,
    "nhan_chia",
    "Nhân số với số có một chữ số",
    "Có thể tách số theo hàng chục và hàng đơn vị rồi nhân.",
    "Nhân tất cả các hàng của số, không chỉ hàng đơn vị.",
    lambda i: (
        f"Tính {20 + i} × 3.",
        (20 + i) * 3,
        f"20 × 3 + {i} × 3 = 60 + {3 * i} = {(20 + i) * 3}.",
    ),
)
topic(
    3,
    "chia_het",
    "Chia hết",
    "Phép chia hết có số dư bằng 0.",
    "Kiểm tra thương bằng phép nhân.",
    lambda i: (
        f"Tính {4 * (20 + i)} : 4.",
        20 + i,
        f"Vì {20 + i} × 4 = {4 * (20 + i)}, thương bằng {20 + i}.",
    ),
)
topic(
    3,
    "chu_vi_hcn",
    "Chu vi hình chữ nhật",
    "Chu vi hình chữ nhật bằng hai lần tổng chiều dài và chiều rộng.",
    "Không nhầm chu vi với diện tích.",
    lambda i: (
        f"Hình chữ nhật dài {i + 5} cm, rộng 4 cm. Chu vi bằng bao nhiêu cm?",
        2 * (i + 9),
        f"Chu vi = ({i + 5} + 4) × 2 = {2 * (i + 9)} cm.",
    ),
)
topic(
    3,
    "dien_tich_hcn",
    "Diện tích hình chữ nhật",
    "Diện tích hình chữ nhật bằng chiều dài nhân chiều rộng.",
    "Đơn vị diện tích là đơn vị vuông, khác đơn vị độ dài.",
    lambda i: (
        f"Hình chữ nhật dài {i + 4} cm, rộng 3 cm. Diện tích bằng bao nhiêu cm²?",
        3 * (i + 4),
        f"Diện tích = {i + 4} × 3 = {3 * (i + 4)} cm².",
    ),
)
topic(
    3,
    "gia_tri_chu_so",
    "Giá trị chữ số theo hàng",
    "Giá trị một chữ số phụ thuộc vào vị trí hàng của nó.",
    "Chữ số và giá trị của chữ số là hai khái niệm khác nhau.",
    lambda i: (
        f"Trong số {10000 + i * 100 + 23}, chữ số ở hàng trăm có giá trị bao nhiêu?",
        (i % 10) * 100,
        f"Hàng trăm có chữ số {i % 10}, nên giá trị là {i % 10} × 100 = {(i % 10) * 100}.",
    ),
)
topic(
    3,
    "doi_thoi_gian",
    "Đổi giờ sang phút",
    "Đổi số giờ sang phút bằng cách nhân với 60.",
    "Không dùng hệ cơ số 100 để đổi giờ và phút.",
    lambda i: (f"{i} giờ bằng bao nhiêu phút?", i * 60, f"{i} × 60 = {i * 60} phút."),
)

topic(
    4,
    "cong_phan_so",
    "Cộng phân số cùng mẫu",
    "Cộng các tử số và giữ nguyên mẫu số.",
    "Không cộng hai mẫu số với nhau.",
    lambda i: (
        f"Tính {i}/13 + 2/13. Có thể nhập phân số tối giản.",
        F(i + 2, 13),
        f"({i} + 2)/13 = {F(i + 2, 13)}.",
    ),
)
topic(
    4,
    "tru_phan_so",
    "Trừ phân số cùng mẫu",
    "Trừ tử số và giữ nguyên mẫu số.",
    "Rút gọn kết quả nếu tử số và mẫu số có ước chung.",
    lambda i: (
        f"Tính {i + 2}/15 − 1/15.",
        F(i + 1, 15),
        f"({i + 2} − 1)/15 = {F(i + 1, 15)}.",
    ),
)
topic(
    4,
    "nhan_phan_so",
    "Nhân phân số",
    "Nhân tử với tử, mẫu với mẫu, rồi rút gọn.",
    "Mẫu số phải khác 0.",
    lambda i: (
        f"Tính {i}/11 × 2/3.",
        F(2 * i, 33),
        f"({i} × 2)/(11 × 3) = {F(2 * i, 33)}.",
    ),
)
topic(
    4,
    "trung_binh",
    "Số trung bình cộng",
    "Lấy tổng các số chia cho số lượng số hạng.",
    "Chia cho số lượng số, không chia cho số lớn nhất.",
    lambda i: (
        f"Tìm trung bình cộng của {i + 10}, {i + 12}, {i + 14}.",
        i + 12,
        f"Tổng là {3 * i + 36}; chia cho 3 được {i + 12}.",
    ),
)
topic(
    4,
    "doi_dien_tich",
    "Đơn vị diện tích",
    "1 m² bằng 10 000 cm² vì 1 m bằng 100 cm.",
    "Đổi diện tích theo bình phương tỉ số đổi độ dài.",
    lambda i: (
        f"{i} m² bằng bao nhiêu cm²?",
        i * 10000,
        f"{i} × 10 000 = {i * 10000} cm².",
    ),
)
topic(
    4,
    "tim_so",
    "Tìm hai số khi biết tổng và hiệu",
    "Số lớn = (tổng + hiệu) : 2; số bé = (tổng − hiệu) : 2.",
    "Tổng và hiệu ở bài này phải cho hai số tự nhiên.",
    lambda i: (
        f"Hai số có tổng {2 * i + 20}, hiệu 6. Số lớn là bao nhiêu?",
        i + 13,
        f"Số lớn = ({2 * i + 20} + 6) : 2 = {i + 13}; số bé là {i + 7}.",
    ),
)

topic(
    5,
    "cong_thap_phan",
    "Cộng số thập phân",
    "Đặt các dấu phẩy thẳng cột rồi cộng theo từng hàng.",
    "Không đặt số thẳng cột chỉ theo chữ số cuối cùng.",
    lambda i: (
        f"Tính {i},25 + 2,5. Nhập dấu phẩy hoặc dấu chấm thập phân.",
        F(4 * i + 11, 4),
        f"{i},25 + 2,50 = {float(F(4 * i + 11, 4)):g}.",
    ),
)
topic(
    5,
    "nhan_thap_phan",
    "Nhân số thập phân",
    "Nhân như số tự nhiên, rồi xác định số chữ số thập phân.",
    "Đếm chữ số thập phân của cả hai thừa số.",
    lambda i: (
        f"Tính {i},5 × 2.",
        2 * i + 1,
        f"({i} + 0,5) × 2 = {2 * i} + 1 = {2 * i + 1}.",
    ),
)
topic(
    5,
    "ti_so_phan_tram",
    "Tỉ số phần trăm",
    "p% của a bằng a × p : 100.",
    "10% là một phần mười, không phải cộng thêm 10.",
    lambda i: (
        f"Tìm 10% của {i * 100 + 50}.",
        i * 10 + 5,
        f"{i * 100 + 50} × 10 : 100 = {i * 10 + 5}.",
    ),
)
topic(
    5,
    "dien_tich_tam_giac",
    "Diện tích tam giác",
    "Diện tích bằng một nửa tích đáy với chiều cao tương ứng.",
    "Chiều cao phải vuông góc với đáy được chọn.",
    lambda i: (
        f"Tam giác có đáy {i + 4} cm, chiều cao tương ứng 6 cm. Diện tích bằng bao nhiêu cm²?",
        3 * (i + 4),
        f"S = {i + 4} × 6 : 2 = {3 * (i + 4)} cm².",
    ),
)
topic(
    5,
    "the_tich_hop",
    "Thể tích hình hộp chữ nhật",
    "Thể tích bằng chiều dài nhân chiều rộng nhân chiều cao.",
    "Ba kích thước phải cùng đơn vị.",
    lambda i: (
        f"Hộp chữ nhật dài {i + 2} cm, rộng 3 cm, cao 4 cm. Thể tích bằng bao nhiêu cm³?",
        12 * (i + 2),
        f"V = {i + 2} × 3 × 4 = {12 * (i + 2)} cm³.",
    ),
)
topic(
    5,
    "van_toc",
    "Quãng đường và vận tốc",
    "Chuyển động đều: quãng đường bằng vận tốc nhân thời gian.",
    "Đổi thời gian về đơn vị phù hợp với vận tốc.",
    lambda i: (
        f"Xe đi đều với vận tốc {30 + i} km/giờ trong 2 giờ. Quãng đường bằng bao nhiêu km?",
        2 * (30 + i),
        f"s = v × t = {30 + i} × 2 = {2 * (30 + i)} km.",
    ),
)

topic(
    6,
    "so_nguyen",
    "Cộng và trừ số nguyên",
    "Cộng hai số trái dấu: trừ hai giá trị tuyệt đối và lấy dấu của số có giá trị tuyệt đối lớn hơn.",
    "Phân biệt dấu âm của số với dấu phép trừ.",
    lambda i: (
        f"Tính (−{i + 12}) + {i + 5}.",
        -7,
        f"Giá trị tuyệt đối chênh {i + 12} − {i + 5} = 7; số âm có giá trị tuyệt đối lớn hơn nên kết quả là −7.",
    ),
)
topic(
    6,
    "chia_het",
    "Dấu hiệu chia hết",
    "Một số chia hết cho 3 nếu tổng các chữ số chia hết cho 3.",
    "Dấu hiệu chia hết cho 3 không chỉ xét chữ số cuối.",
    lambda i: (
        f"Số {3 * (100 + i)} chia cho 3 được thương bao nhiêu?",
        100 + i,
        f"{3 * (100 + i)} = 3 × {100 + i}, nên thương là {100 + i}.",
    ),
)
topic(
    6,
    "ucln",
    "Ước chung lớn nhất",
    "Ước chung lớn nhất là số lớn nhất chia hết cả hai số đã cho.",
    "ƯCLN không được lớn hơn số nhỏ hơn trong hai số.",
    lambda i: (
        f"Tìm ƯCLN của {2 * (i + 1)} và {3 * (i + 1)}.",
        i + 1,
        f"2 và 3 nguyên tố cùng nhau, nên ƯCLN(2 × {i + 1}, 3 × {i + 1}) = {i + 1}.",
    ),
)
topic(
    6,
    "bcnn",
    "Bội chung nhỏ nhất",
    "BCNN của hai số dương bằng tích hai số chia cho ƯCLN.",
    "Không nhầm ước chung với bội chung.",
    lambda i: (
        f"Tìm BCNN của {2 * (i + 1)} và {3 * (i + 1)}.",
        6 * (i + 1),
        f"ƯCLN là {i + 1}; BCNN = {2 * (i + 1)} × {3 * (i + 1)} : {i + 1} = {6 * (i + 1)}.",
    ),
)
topic(
    6,
    "phan_so_khac_mau",
    "Cộng phân số khác mẫu",
    "Quy đồng mẫu số trước khi cộng các tử số.",
    "Giữ nguyên giá trị phân số khi quy đồng.",
    lambda i: (
        f"Tính {i}/12 + 1/6.",
        F(i + 2, 12),
        f"1/6 = 2/12; tổng = ({i} + 2)/12 = {F(i + 2, 12)}.",
    ),
)
topic(
    6,
    "dien_tich_hinh_thang",
    "Diện tích hình thang",
    "S = (đáy lớn + đáy nhỏ) × chiều cao : 2.",
    "Chiều cao là khoảng cách vuông góc giữa hai đáy.",
    lambda i: (
        f"Hình thang có hai đáy {i + 6} cm và {i + 2} cm, chiều cao 4 cm. Diện tích bằng bao nhiêu cm²?",
        4 * i + 16,
        f"S = ({i + 6} + {i + 2}) × 4 : 2 = {4 * i + 16} cm².",
    ),
)

topic(
    7,
    "so_huu_ti",
    "Số hữu tỉ",
    "Các phép tính trên số hữu tỉ có thể thực hiện bằng phân số.",
    "Chú ý dấu âm khi cộng các số hữu tỉ.",
    lambda i: (f"Tính −{i}/7 + 2/7.", F(2 - i, 7), f"(−{i} + 2)/7 = {F(2 - i, 7)}."),
)
topic(
    7,
    "luy_thua",
    "Lũy thừa",
    "Bình phương của a là a nhân a.",
    "Bình phương của số âm là số không âm.",
    lambda i: (
        f"Tính (−{i + 1})².",
        (i + 1) ** 2,
        f"(−{i + 1}) × (−{i + 1}) = {(i + 1) ** 2}.",
    ),
)
topic(
    7,
    "ti_le_thuan",
    "Đại lượng tỉ lệ thuận",
    "Nếu y tỉ lệ thuận với x theo hệ số k thì y = kx.",
    "Hệ số tỉ lệ phải giữ nguyên trong toàn bộ bài.",
    lambda i: (
        f"y tỉ lệ thuận với x theo hệ số 3. Khi x = {i + 2}, y bằng bao nhiêu?",
        3 * (i + 2),
        f"y = 3x = 3 × {i + 2} = {3 * (i + 2)}.",
    ),
)
topic(
    7,
    "ti_le_nghich",
    "Đại lượng tỉ lệ nghịch",
    "Nếu y tỉ lệ nghịch với x theo hệ số a thì xy = a.",
    "Tích xy không đổi; thương y/x không phải hằng số.",
    lambda i: (
        f"Hai đại lượng x, y thỏa mãn xy = {12 * (i + 1)}. Khi x = 3, y bằng bao nhiêu?",
        4 * (i + 1),
        f"y = {12 * (i + 1)} : 3 = {4 * (i + 1)}.",
    ),
)
topic(
    7,
    "goc_tam_giac",
    "Tổng ba góc của tam giác",
    "Tổng ba góc trong một tam giác bằng 180°.",
    "Không cộng góc ngoài thay cho góc trong.",
    lambda i: (
        f"Hai góc trong tam giác bằng {40 + i}° và 60°. Góc còn lại bằng bao nhiêu độ?",
        80 - i,
        f"180 − {40 + i} − 60 = {80 - i}°.",
    ),
)
topic(
    7,
    "xac_suat_don_gian",
    "Xác suất của biến cố đơn giản",
    "Trong mô hình đồng khả năng, xác suất bằng số kết quả thuận lợi chia tổng số kết quả.",
    "Xác suất luôn nằm trong đoạn từ 0 đến 1.",
    lambda i: (
        f"Hộp có {i + 2} thẻ đỏ và 3 thẻ xanh giống nhau về kích thước. Rút ngẫu nhiên một thẻ. Xác suất rút thẻ đỏ là bao nhiêu?",
        F(i + 2, i + 5),
        f"Tổng {i + 5} thẻ; có {i + 2} thẻ đỏ, nên P = {F(i + 2, i + 5)}.",
    ),
)

topic(
    8,
    "da_thuc",
    "Giá trị của đa thức",
    "Thay giá trị của biến vào đa thức và thực hiện đúng thứ tự phép tính.",
    "Tính lũy thừa trước phép nhân và phép cộng.",
    lambda i: (
        f"Cho P(x) = x² + 2x + 1. Tính P({i}).",
        (i + 1) ** 2,
        f"P({i}) = {i * i} + {2 * i} + 1 = {(i + 1) ** 2}.",
    ),
)
topic(
    8,
    "hang_dang_thuc",
    "Hằng đẳng thức",
    "(a + b)² = a² + 2ab + b².",
    "Không bỏ hạng tử 2ab khi bình phương một tổng.",
    lambda i: (
        f"Cho biểu thức x² + {2 * i}x + {i * i}. Khi x = 2, biểu thức bằng bao nhiêu?",
        (i + 2) ** 2,
        f"x² + {2 * i}x + {i * i} = (x + {i})²; tại x = 2 được {(i + 2) ** 2}.",
    ),
)
topic(
    8,
    "phuong_trinh_bac_nhat",
    "Phương trình bậc nhất",
    "Chuyển vế đổi dấu, rồi chia hai vế cho hệ số khác 0 của ẩn.",
    "Phải thực hiện cùng một phép biến đổi ở cả hai vế.",
    lambda i: (
        f"Giải phương trình 3x − {i + 4} = {2 * i + 5}. Nhập giá trị x.",
        i + 3,
        f"3x = {2 * i + 5} + {i + 4} = {3 * i + 9}; x = {i + 3}.",
    ),
)
topic(
    8,
    "ham_so_bac_nhat",
    "Hàm số bậc nhất",
    "Với y = ax + b, thay x vào để tính giá trị y.",
    "Hệ số b là số cộng thêm, không phải hệ số nhân với x.",
    lambda i: (
        f"Hàm số y = 2x − 3. Tính y khi x = {i + 4}.",
        2 * i + 5,
        f"y = 2 × {i + 4} − 3 = {2 * i + 5}.",
    ),
)
topic(
    8,
    "pytago",
    "Định lí Pythagore",
    "Trong tam giác vuông: bình phương cạnh huyền bằng tổng bình phương hai cạnh góc vuông.",
    "Chỉ áp dụng công thức này khi tam giác vuông.",
    lambda i: (
        f"Tam giác ABC vuông tại A, AB = {3 * i} cm và AC = {4 * i} cm. Độ dài BC bằng bao nhiêu cm?",
        5 * i,
        f"c² = {3 * i}² + {4 * i}² = {25 * i * i}; c = {5 * i} cm vì độ dài dương.",
    ),
)
topic(
    8,
    "thales",
    "Tỉ số trong tam giác",
    "Đường thẳng song song với một cạnh của tam giác tạo ra các tỉ số tương ứng bằng nhau.",
    "Ghép đúng các cạnh tương ứng trong tỉ số.",
    lambda i: (
        f"Trong tam giác ABC, M thuộc AB, N thuộc AC và MN song song BC. AM/AB = 1/2, AC = {2 * (i + 5)} cm. AN bằng bao nhiêu cm?",
        i + 5,
        f"AN/AC = AM/AB = 1/2; AN = {2 * (i + 5)} × 1/2 = {i + 5} cm.",
    ),
)

topic(
    9,
    "can_bac_hai",
    "Căn bậc hai số học",
    "Căn bậc hai số học của a không âm là số không âm có bình phương bằng a.",
    "Căn bậc hai số học không mang dấu âm.",
    lambda i: (
        f"Số không âm nào có bình phương bằng {(i + 5) ** 2}?",
        i + 5,
        f"{i + 5} ≥ 0 và {i + 5}² = {(i + 5) ** 2}, nên kết quả là {i + 5}.",
    ),
)
topic(
    9,
    "he_phuong_trinh",
    "Hệ hai phương trình bậc nhất",
    "Có thể cộng hoặc trừ các phương trình để khử một ẩn.",
    "Sau khi tìm một ẩn, thay lại để tìm và kiểm tra ẩn còn lại.",
    lambda i: (
        f"Hệ phương trình x + y = {2 * i + 5}, x − y = 3. Tìm x.",
        i + 4,
        f"Cộng hai phương trình: 2x = {2 * i + 8}, nên x = {i + 4}; y = {i + 1}.",
    ),
)
topic(
    9,
    "phuong_trinh_bac_hai",
    "Phương trình bậc hai",
    "Nếu tích hai biểu thức bằng 0 thì ít nhất một thừa số bằng 0.",
    "Tìm đủ nghiệm, rồi chọn nghiệm theo yêu cầu của đề.",
    lambda i: (
        f"Phương trình (x − {i})(x − {i + 3}) = 0 có nghiệm lớn hơn bằng bao nhiêu?",
        i + 3,
        f"Nghiệm là x = {i} hoặc x = {i + 3}; nghiệm lớn hơn là {i + 3}.",
    ),
)
topic(
    9,
    "duong_tron",
    "Chu vi đường tròn",
    "Chu vi đường tròn bằng 2πr.",
    "Phân biệt bán kính và đường kính.",
    lambda i: (
        f"Đường tròn bán kính {i + 2} cm. Chu vi viết dưới dạng aπ cm. Tìm a.",
        2 * (i + 2),
        f"C = 2π × {i + 2} = {2 * (i + 2)}π cm, nên a = {2 * (i + 2)}.",
    ),
)
topic(
    9,
    "ti_so_luong_giac",
    "Tỉ số lượng giác trong tam giác vuông",
    "Sin của góc nhọn bằng cạnh đối chia cạnh huyền.",
    "Cạnh đối được xác định theo góc đang xét.",
    lambda i: (
        f"Tam giác ABC vuông tại A, AB = {3 * i}, AC = {4 * i}, BC = {5 * i}. Tính sin B.",
        F(4, 5),
        f"Đối với góc B, cạnh đối là AC và cạnh huyền là BC; sin B = {4 * i}/{5 * i} = 4/5.",
    ),
)
topic(
    9,
    "xac_suat",
    "Xác suất trong mô hình đồng khả năng",
    "Liệt kê số kết quả thuận lợi và tổng số kết quả đồng khả năng.",
    "Không đếm trùng kết quả thuận lợi.",
    lambda i: (
        f"Chọn ngẫu nhiên một số nguyên từ 1 đến {2 * i + 10}. Xác suất chọn được số chẵn bằng bao nhiêu?",
        F(1, 2),
        f"Có {i + 5} số chẵn trong {2 * i + 10} số; xác suất = {i + 5}/{2 * i + 10} = 1/2.",
    ),
)

topic(
    10,
    "tap_hop",
    "Tập hợp và giao hai tập hợp",
    "Giao hai tập hợp gồm các phần tử xuất hiện trong cả hai tập hợp.",
    "Không nhầm giao với hợp.",
    lambda i: (
        f"A = {{{i}, {i + 1}, {i + 2}}}, B = {{{i + 2}, {i + 3}}}. Phần tử duy nhất của A ∩ B là số nào?",
        i + 2,
        f"Chỉ có {i + 2} thuộc cả A và B, nên A ∩ B = {{{i + 2}}}.",
    ),
)
topic(
    10,
    "dinh_parabol",
    "Hàm số bậc hai",
    "Hoành độ đỉnh của y = ax² + bx + c là −b/(2a), với a khác 0.",
    "Không bỏ dấu âm trong công thức hoành độ đỉnh.",
    lambda i: (
        f"Parabol y = x² − {2 * i}x + 3 có hoành độ đỉnh bằng bao nhiêu?",
        i,
        f"a = 1, b = −{2 * i}; x đỉnh = −(−{2 * i})/(2 × 1) = {i}.",
    ),
)
topic(
    10,
    "tich_vo_huong",
    "Tích vô hướng của vectơ",
    "Trong mặt phẳng, (a,b)·(c,d) = ac + bd.",
    "Tích vô hướng là một số, không phải một vectơ.",
    lambda i: (
        f"Cho u = ({i}; 2), v = (3; −1). Tính u·v.",
        3 * i - 2,
        f"u·v = {i} × 3 + 2 × (−1) = {3 * i - 2}.",
    ),
)
topic(
    10,
    "khoang_cach",
    "Khoảng cách trong mặt phẳng",
    "Khoảng cách giữa hai điểm bằng căn bậc hai của tổng bình phương hiệu tọa độ.",
    "Khoảng cách luôn không âm.",
    lambda i: (
        f"Trong Oxy, A(1; 2), B({1 + 3 * i}; {2 + 4 * i}). Tính AB.",
        5 * i,
        f"AB = √(({3 * i})² + ({4 * i})²) = {5 * i}.",
    ),
)
topic(
    10,
    "to_hop",
    "Tổ hợp",
    "Số cách chọn 2 phần tử từ n phần tử là n(n−1)/2 khi không xét thứ tự.",
    "Nếu chọn một nhóm thì đổi thứ tự không tạo nhóm mới.",
    lambda i: (
        f"Có {i + 3} học sinh. Chọn 2 học sinh vào một nhóm, không phân vai. Có bao nhiêu cách?",
        (i + 3) * (i + 2) // 2,
        f"C({i + 3},2) = {i + 3} × {i + 2} / 2 = {(i + 3) * (i + 2) // 2}.",
    ),
)
topic(
    10,
    "trung_binh",
    "Số trung bình của mẫu số liệu",
    "Số trung bình bằng tổng giá trị quan sát chia số quan sát.",
    "Không nhầm số trung bình với trung vị.",
    lambda i: (
        f"Mẫu số liệu gồm {i}, {i + 2}, {i + 4}, {i + 6}. Tính số trung bình.",
        i + 3,
        f"Tổng = {4 * i + 12}; chia 4 được {i + 3}.",
    ),
)

topic(
    11,
    "cap_so_cong",
    "Cấp số cộng",
    "Số hạng thứ n: uₙ = u₁ + (n−1)d.",
    "Số hạng thứ n dùng n−1 lần cộng công sai.",
    lambda i: (
        f"Cấp số cộng có u₁ = {i}, công sai d = 3. Tính u₆.",
        i + 15,
        f"u₆ = {i} + (6−1) × 3 = {i + 15}.",
    ),
)
topic(
    11,
    "cap_so_nhan",
    "Cấp số nhân",
    "Số hạng thứ n: uₙ = u₁qⁿ⁻¹.",
    "Số mũ là n−1, không phải n.",
    lambda i: (
        f"Cấp số nhân có u₁ = {i}, công bội q = 2. Tính u₄.",
        8 * i,
        f"u₄ = {i} × 2³ = {8 * i}.",
    ),
)
topic(
    11,
    "dao_ham",
    "Đạo hàm của đa thức",
    "Đạo hàm của x² là 2x, của hằng số là 0.",
    "Giá trị đạo hàm phải được tính sau khi tìm biểu thức đạo hàm.",
    lambda i: (
        f"Cho f(x) = x² + 3x. Tính f′({i}).",
        2 * i + 3,
        f"f′(x) = 2x + 3; f′({i}) = {2 * i + 3}.",
    ),
)
topic(
    11,
    "logarit",
    "Logarit",
    "logₐ(aᵏ) = k với a dương và khác 1.",
    "Đối số logarit phải dương.",
    lambda i: (f"Tính log₂({2**i}).", i, f"{2**i} = 2^{i}, nên log₂({2**i}) = {i}."),
)
topic(
    11,
    "ham_mu",
    "Phương trình mũ",
    "Khi hai lũy thừa cùng cơ số dương khác 1 bằng nhau thì số mũ bằng nhau.",
    "Đưa hai vế về cùng cơ số trước khi so sánh số mũ.",
    lambda i: (
        f"Giải 2^(x + 1) = {2 ** (i + 2)}. Nhập x.",
        i + 1,
        f"{2 ** (i + 2)} = 2^{i + 2}; x + 1 = {i + 2}, nên x = {i + 1}.",
    ),
)
topic(
    11,
    "bien_co_doc_lap",
    "Xác suất của biến cố độc lập",
    "Với hai biến cố độc lập A, B: P(A ∩ B) = P(A)P(B).",
    "Chỉ nhân xác suất theo công thức này khi có điều kiện độc lập.",
    lambda i: (
        f"A và B độc lập, P(A) = {i}/12, P(B) = 1/2. Tính P(A ∩ B).",
        F(i, 24),
        f"P(A ∩ B) = ({i}/12) × (1/2) = {F(i, 24)}.",
    ),
)

topic(
    12,
    "cuc_tri",
    "Giá trị nhỏ nhất của hàm số",
    "Hoàn thành bình phương giúp tìm giá trị nhỏ nhất của một tam thức bậc hai có hệ số đầu dương.",
    "Phân biệt giá trị nhỏ nhất với vị trí đạt giá trị nhỏ nhất.",
    lambda i: (
        f"Tìm giá trị nhỏ nhất trên R của f(x) = (x − {i})² + {i + 2}.",
        i + 2,
        f"(x − {i})² ≥ 0; f(x) ≥ {i + 2}, dấu bằng khi x = {i}.",
    ),
)
topic(
    12,
    "tich_phan",
    "Tích phân của đa thức",
    "Tích phân xác định bằng giá trị nguyên hàm ở cận trên trừ giá trị ở cận dưới.",
    "Không cộng tùy tiện hằng số vào giá trị tích phân xác định.",
    lambda i: (
        f"Tính tích phân từ 0 đến {i} của hàm số 2x theo x.",
        i * i,
        f"Nguyên hàm của 2x là x²; giá trị bằng {i}² − 0² = {i * i}.",
    ),
)
topic(
    12,
    "toa_do_khong_gian",
    "Khoảng cách trong không gian",
    "Trong Oxyz, khoảng cách dùng tổng bình phương của ba hiệu tọa độ.",
    "Không bỏ tọa độ z trong bài toán không gian.",
    lambda i: (
        f"Trong Oxyz, O(0;0;0), M({i}; {2 * i}; {2 * i}). Tính OM.",
        3 * i,
        f"OM = √({i * i} + {4 * i * i} + {4 * i * i}) = √({9 * i * i}) = {3 * i}.",
    ),
)
topic(
    12,
    "vectơ_khong_gian",
    "Tích vô hướng trong không gian",
    "Tích vô hướng bằng tổng ba tích tọa độ tương ứng.",
    "Ghép đúng các tọa độ x, y và z.",
    lambda i: (
        f"Cho u = ({i}; 2; −1), v = (2; 1; 3). Tính u·v trong không gian.",
        2 * i - 1,
        f"u·v = {i} × 2 + 2 × 1 + (−1) × 3 = {2 * i - 1}.",
    ),
)
topic(
    12,
    "xac_suat_co_dieu_kien",
    "Xác suất có điều kiện",
    "P(A|B) = P(A ∩ B)/P(B), với P(B) > 0.",
    "Mẫu số là xác suất của biến cố điều kiện B.",
    lambda i: (
        f"Cho P(B) = 1/2 và P(A ∩ B) = {i}/24. Tính P(A|B).",
        F(i, 12),
        f"P(A|B) = ({i}/24)/(1/2) = {F(i, 12)}.",
    ),
)
topic(
    12,
    "mau_ghep_nhom",
    "Số trung bình của mẫu ghép nhóm",
    "Số trung bình xấp xỉ bằng tổng tích giá trị đại diện với tần số, chia tổng tần số.",
    "Dùng trung điểm mỗi nhóm làm giá trị đại diện; đây là giá trị xấp xỉ.",
    lambda i: (
        f"Mẫu ghép nhóm có hai nhóm [{i}; {i + 2}) và [{i + 2}; {i + 4}), mỗi nhóm có tần số 5. Tính số trung bình xấp xỉ.",
        i + 2,
        f"Giá trị đại diện là {i + 1} và {i + 3}; trung bình = (5 × {i + 1} + 5 × {i + 3})/10 = {i + 2}.",
    ),
)


def build():
    questions, exams, notes, coverage = [], [], [], []
    for grade, slug, name, rule, mistake, make in TOPICS:
        slug = slug.replace("ơ", "o")
        ids = []
        for i in range(1, 11):
            prompt, answer, solution = make(i)
            qid = f"kntt_math_{grade}_{slug}_{i:02d}"
            ids.append(qid)
            questions.append(
                dict(
                    id=qid,
                    grade=grade,
                    subject="toan",
                    topic=slug,
                    textbook="ket_noi_tri_thuc",
                    type="numeric",
                    difficulty="easy" if grade <= 5 else "medium",
                    question=prompt,
                    options=[],
                    correct_answer=[str(answer)],
                    max_score=1,
                    explanation=solution,
                    tolerance=0,
                    source_type="original",
                    license="original_content",
                    rights_evidence="Tự biên soạn; biến thể luyện tập theo chủ đề GDPT 2018 hướng tới Kết nối tri thức. Chưa đối chiếu từng bài/ấn bản SGK và chưa thẩm định chuyên môn độc lập.",
                )
            )
        exams.append(
            dict(
                id=f"kntt_math_{grade}_{slug}",
                grade=grade,
                subject="toan",
                textbook="ket_noi_tri_thuc",
                topic=slug,
                title=f"Toán {grade} · {name} · Luyện theo chủ đề KNTT",
                duration_minutes=20,
                question_ids=ids,
            )
        )
        example, answer, solution = make(1)
        notes.append(
            dict(
                id=f"kntt_note_{grade}_{slug}",
                grade=grade,
                subject="toan",
                title=f"Toán {grade}: {name}",
                topic=name,
                textbook="ket_noi_tri_thuc",
                kind="study_notes",
                semester=None,
                summary=f"Ghi chú tự biên soạn: {name.lower()}; có ví dụ và lỗi thường gặp.",
                sections=[
                    dict(heading="Kiến thức cần nhớ", text=rule),
                    dict(heading="Ví dụ có lời giải", text=example + "\n" + solution),
                    dict(heading="Lỗi thường gặp", text=mistake),
                    dict(
                        heading="Tự luyện",
                        text="\n".join(make(j)[0] for j in (2, 3, 4)),
                    ),
                    dict(
                        heading="Đáp án tự kiểm tra",
                        text="\n".join(f"{j - 1}. " + make(j)[2] for j in (2, 3, 4)),
                    ),
                    dict(
                        heading="Phạm vi tài liệu",
                        text="Ghi chú độc lập theo chủ đề; hướng tới bộ Kết nối tri thức, chưa đối chiếu chính xác từng bài hoặc ấn bản. Không phải bản chép SGK hay tài liệu chính thức của nhà xuất bản.",
                    ),
                ],
                author="Kho Học 1–12",
                source_name="Nội dung tự biên soạn theo chủ đề",
                source_type="original",
                license="original_content",
                rights_evidence="Soạn riêng cho bản thử; không sao chép SGK. Chưa được thẩm định chuyên môn độc lập.",
                distribution_allowed=True,
                download_allowed=False,
            )
        )
        coverage.append(
            dict(
                grade=grade,
                subject="toan",
                topic=slug,
                title=name,
                question_count=len(ids),
                exercise_families=1,
                alignment_status="topic_level_pending_edition_review",
            )
        )
    for grade in range(1, 13):
        ids = [
            q["id"]
            for q in questions
            if q["grade"] == grade and q["id"].endswith(("_01", "_02"))
        ]
        exams.append(
            dict(
                id=f"kntt_math_{grade}_mixed",
                grade=grade,
                subject="toan",
                textbook="ket_noi_tri_thuc",
                topic="tong_hop",
                title=f"Toán {grade} · Tổng hợp 6 chủ đề · KNTT",
                duration_minutes=30,
                question_ids=ids,
            )
        )

    def save(path, value):
        (ROOT / path).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    save("data/seeds/curriculum_questions.json", dict(questions=questions))
    save("data/seeds/curriculum_exams.json", exams)
    base = json.loads(
        (ROOT / "data/library/documents.json").read_text(encoding="utf-8")
    )
    base["documents"] = [
        d for d in base["documents"] if not d["id"].startswith("kntt_note_")
    ] + notes
    save("data/library/documents.json", base)
    save(
        "data/seeds/curriculum_coverage.json",
        dict(
            textbook="ket_noi_tri_thuc",
            edition=None,
            status="provisional_topic_mapping",
            publisher_reference="https://hanhtrangso.nxbgd.vn/",
            reference_note="Cổng nhà xuất bản đã kiểm tra truy cập; chưa xác minh mục lục của từng ấn bản. Nội dung tự biên soạn, không trích nội dung sách.",
            exercise_families=len(TOPICS),
            variant_count=len(questions),
            topics=coverage,
        ),
    )
    print(
        f"Generated {len(questions)} variants / {len(TOPICS)} topic families, {len(exams)} exams, {len(notes)} notes"
    )


if __name__ == "__main__":
    build()
