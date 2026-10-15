"""Original lessons aligned with a checked secondary-source Math 5 index."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = {}


def skill(key, rule, method, example, worked, tasks, answers, mistake):
    SKILLS[key] = (rule, method, example, worked, tasks, answers, mistake)


skill(
    "natural",
    "Giá trị của một chữ số phụ thuộc hàng của nó; so sánh từ hàng cao nhất.",
    "Tách số thành các hàng; khi so sánh, tìm hàng đầu tiên khác nhau.",
    "Phân tích số 42 305.",
    "42 305 = 40 000 + 2 000 + 300 + 5; chữ số 3 có giá trị 300.",
    [
        "Giá trị chữ số 7 trong 57 204 là bao nhiêu?",
        "Sắp xếp tăng dần: 30 120; 30 102; 29 999.",
    ],
    ["7 000.", "29 999 < 30 102 < 30 120."],
    "Không coi chữ số ở mọi hàng đều có cùng giá trị.",
)
skill(
    "operations",
    "Thực hiện trong ngoặc trước; nhân chia trước cộng trừ.",
    "Viết kết quả từng bước và kiểm tra phép tính ngược.",
    "Tính 240 : (4 + 2) + 15.",
    "4 + 2 = 6; 240 : 6 = 40; 40 + 15 = 55.",
    ["Tính 36 × 4 + 28.", "Tính (125 + 75) : 5."],
    ["36 × 4 + 28 = 144 + 28 = 172.", "(125 + 75) : 5 = 200 : 5 = 40."],
    "Không làm tất cả phép tính từ trái sang phải khi có nhân/chia và cộng/trừ.",
)
skill(
    "fraction",
    "Phân số a/b biểu thị a phần khi một đơn vị chia thành b phần bằng nhau, b khác 0.",
    "Muốn rút gọn, chia cả tử và mẫu cho cùng một ước chung khác 0.",
    "Rút gọn 12/18.",
    "Chia tử và mẫu cho 6: 12/18 = 2/3.",
    ["Rút gọn 15/20.", "So sánh 2/3 và 3/4."],
    ["15/20 = 3/4.", "2/3 = 8/12 < 9/12 = 3/4."],
    "Không chỉ chia tử số hoặc chỉ chia mẫu số.",
)
skill(
    "decimal_fraction",
    "Phân số thập phân có mẫu số 10, 100, 1 000,...",
    "Nhân hoặc chia cả tử và mẫu để đưa mẫu về một lũy thừa của 10 khi có thể.",
    "Viết 3/5 thành phân số thập phân.",
    "3/5 = (3 × 2)/(5 × 2) = 6/10.",
    ["Viết 7/20 thành phân số thập phân.", "Rút gọn 45/100."],
    ["7/20 = 35/100.", "45/100 = 9/20."],
    "Không phải mọi phân số đều viết được thành số thập phân hữu hạn.",
)
skill(
    "fraction_ops",
    "Cộng trừ cần cùng mẫu; nhân thì nhân tử với tử và mẫu với mẫu; chia thì nhân với phân số đảo của số chia khác 0.",
    "Quy đồng khi cộng/trừ; rút gọn sau phép tính.",
    "Tính 2/3 × 3/4 và 2/3 : 4/5.",
    "2/3 × 3/4 = 6/12 = 1/2; 2/3 : 4/5 = 2/3 × 5/4 = 5/6.",
    ["Tính 3/5 + 1/5.", "Tính 3/4 : 3/8."],
    ["3/5 + 1/5 = 4/5.", "3/4 × 8/3 = 2."],
    "Không đảo phân số bị chia khi thực hiện phép chia.",
)
skill(
    "unlike_fraction",
    "Cộng/trừ hai phân số khác mẫu cần quy đồng mẫu số.",
    "Chọn mẫu chung, viết hai phân số tương đương, tính trên tử rồi rút gọn.",
    "Tính 3/4 − 1/6.",
    "Mẫu chung 12: 3/4 = 9/12; 1/6 = 2/12; hiệu = 7/12.",
    ["Tính 1/2 + 2/5.", "Tính 5/6 − 1/4."],
    ["5/10 + 4/10 = 9/10.", "10/12 − 3/12 = 7/12."],
    "Không cộng hoặc trừ hai mẫu số.",
)
skill(
    "mixed",
    "Hỗn số gồm phần nguyên và phần phân số; trong dạng thông thường phần phân số bé hơn 1.",
    "Đổi hỗn số thành phân số: phần nguyên × mẫu + tử, giữ mẫu.",
    "Đổi 2 và 3/5 thành phân số.",
    "(2 × 5 + 3)/5 = 13/5.",
    ["Đổi 3 và 1/4 thành phân số.", "Đổi 11/3 thành hỗn số."],
    ["(3 × 4 + 1)/4 = 13/4.", "11 : 3 được 3 dư 2, nên 11/3 = 3 và 2/3."],
    "Không bỏ phần nguyên khi đổi.",
)
skill(
    "plane",
    "Chu vi là độ dài đường bao; diện tích là số đo phần mặt phẳng.",
    "Nhận dạng hình, chọn đúng công thức và dùng đơn vị phù hợp.",
    "Hình chữ nhật dài 8 cm, rộng 5 cm. Tính chu vi và diện tích.",
    "P = (8 + 5) × 2 = 26 cm; S = 8 × 5 = 40 cm².",
    [
        "Hình vuông cạnh 6 cm có chu vi và diện tích bao nhiêu?",
        "Hình chữ nhật dài 12 m, rộng 4 m có diện tích bao nhiêu?",
    ],
    ["P = 24 cm; S = 36 cm².", "S = 12 × 4 = 48 m²."],
    "Không dùng cm cho kết quả diện tích.",
)
skill(
    "decimal",
    "Mỗi hàng thập phân bên phải bằng một phần mười hàng ngay bên trái.",
    "Dùng bảng hàng: đơn vị, phần mười, phần trăm, phần nghìn.",
    "Phân tích số 3,407.",
    "3,407 = 3 + 4/10 + 0/100 + 7/1 000.",
    [
        "Viết 2 + 5/10 + 3/100 dưới dạng số thập phân.",
        "Chữ số 6 trong 1,26 chỉ mấy phần trăm?",
    ],
    ["2,53.", "6 phần trăm, giá trị 0,06."],
    "Không nhầm phần mười với phần trăm.",
)
skill(
    "compare_decimal",
    "So sánh phần nguyên trước; nếu bằng nhau, so sánh từng hàng thập phân.",
    "Có thể thêm chữ số 0 ở cuối phần thập phân để cùng số hàng.",
    "So sánh 4,7 và 4,65.",
    "4,7 = 4,70; hàng phần mười có 7 > 6, nên 4,7 > 4,65.",
    ["So sánh 3,09 và 3,1.", "Sắp xếp tăng dần: 2,5; 2,05; 2,15."],
    ["3,09 < 3,10 = 3,1.", "2,05 < 2,15 < 2,5."],
    "Không so sánh theo số lượng chữ số sau dấu phẩy.",
)
skill(
    "measure_decimal",
    "Đổi số đo về cùng đơn vị rồi biểu diễn phần lẻ bằng số thập phân.",
    "Viết quan hệ đơn vị trước khi tính.",
    "Viết 2 m 35 cm theo đơn vị m.",
    "35 cm = 0,35 m; 2 m 35 cm = 2,35 m.",
    ["Viết 4 kg 250 g theo kg.", "Viết 3 m 8 cm theo m."],
    ["4,25 kg.", "3,08 m."],
    "Không viết 3 m 8 cm thành 3,8 m.",
)
skill(
    "round",
    "Làm tròn dựa vào chữ số ngay bên phải hàng cần giữ: từ 5 trở lên tăng 1.",
    "Chọn hàng làm tròn, xét chữ số kế tiếp, bỏ các hàng phía sau phù hợp.",
    "Làm tròn 7,346 đến hàng phần trăm.",
    "Hàng phần trăm là 4, chữ số tiếp theo 6 ≥ 5; kết quả 7,35.",
    ["Làm tròn 2,74 đến hàng phần mười.", "Làm tròn 8,96 đến hàng đơn vị."],
    ["2,7.", "9."],
    "Chỉ xét chữ số ngay bên phải hàng cần giữ.",
)
skill(
    "land_area",
    "1 km² = 1 000 000 m²; 1 ha = 10 000 m²; 1 km² = 100 ha.",
    "Chọn đơn vị đích và nhân/chia đúng hệ số.",
    "Đổi 2,5 ha thành m².",
    "2,5 × 10 000 = 25 000 m².",
    ["Đổi 3 km² thành ha.", "Đổi 45 000 m² thành ha."],
    ["3 × 100 = 300 ha.", "45 000 : 10 000 = 4,5 ha."],
    "Không nhầm 1 ha với 100 m².",
)
skill(
    "area_units",
    "Mỗi bậc liền kề của bảng đơn vị diện tích thông thường hơn/kém nhau 100 lần.",
    "Đổi theo số bậc; không áp dụng hệ số đổi độ dài cho diện tích.",
    "Đổi 3,2 m² thành dm².",
    "1 m² = 100 dm²; 3,2 m² = 320 dm².",
    ["Đổi 450 cm² thành dm².", "Đổi 2 m² thành cm²."],
    ["450 : 100 = 4,5 dm².", "2 × 10 000 = 20 000 cm²."],
    "Không nhân 10 cho mỗi bậc diện tích.",
)
skill(
    "add_decimal",
    "Cộng số thập phân cần đặt các dấu phẩy thẳng cột.",
    "Bổ sung số 0 nếu cần, cộng như số tự nhiên rồi giữ vị trí dấu phẩy.",
    "Tính 12,35 + 4,8.",
    "Viết 4,8 = 4,80; cộng theo hàng được 17,15.",
    ["Tính 3,45 + 2,7.", "Tính 0,86 + 1,25."],
    ["3,45 + 2,70 = 6,15.", "0,86 + 1,25 = 2,11."],
    "Không đặt thẳng cột theo chữ số cuối mà bỏ qua dấu phẩy.",
)
skill(
    "subtract_decimal",
    "Trừ số thập phân cần các dấu phẩy thẳng cột.",
    "Thêm chữ số 0 vào cuối phần thập phân; trừ theo từng hàng.",
    "Tính 10 − 3,75.",
    "10 = 10,00; 10,00 − 3,75 = 6,25.",
    ["Tính 8,2 − 1,46.", "Tính 5 − 0,85."],
    ["8,20 − 1,46 = 6,74.", "5,00 − 0,85 = 4,15."],
    "Không bỏ phần nhớ khi phải đổi một đơn vị ở hàng cao hơn.",
)
skill(
    "multiply_decimal",
    "Nhân như số tự nhiên rồi đặt dấu phẩy theo tổng số chữ số thập phân của hai thừa số.",
    "Tính tích chưa có dấu phẩy; đếm số chữ số phần thập phân.",
    "Tính 2,4 × 1,5.",
    "24 × 15 = 360; hai thừa số có tổng 2 chữ số thập phân, nên tích 3,60 = 3,6.",
    ["Tính 0,8 × 0,5.", "Tính 3,25 × 4."],
    ["0,4.", "13."],
    "Không đếm số chữ số thập phân của chỉ một thừa số.",
)
skill(
    "divide_decimal",
    "Có thể nhân cả số bị chia và số chia với cùng một lũy thừa của 10 để số chia thành số tự nhiên.",
    "Dời dấu phẩy ở cả hai số cùng số hàng rồi chia.",
    "Tính 7,2 : 0,3.",
    "Nhân cả hai số với 10: 72 : 3 = 24.",
    ["Tính 4,5 : 0,5.", "Tính 6,4 : 4."],
    ["45 : 5 = 9.", "1,6."],
    "Không chỉ dời dấu phẩy ở số chia.",
)
skill(
    "powers_ten",
    "Nhân với 10, 100,... dời dấu phẩy sang phải; chia thì dời sang trái. Nhân 0,1 tương đương chia 10.",
    "Đếm số chữ số 0 hoặc số hàng thập phân của hệ số rồi dời đúng hướng.",
    "Tính 3,45 × 100 và 3,45 × 0,1.",
    "3,45 × 100 = 345; 3,45 × 0,1 = 0,345.",
    ["Tính 12,6 : 100.", "Tính 0,48 : 0,01."],
    ["0,126.", "0,48 × 100 = 48."],
    "Không nhầm nhân 0,1 với nhân 10.",
)
skill(
    "triangle",
    "Diện tích tam giác bằng đáy × chiều cao tương ứng : 2.",
    "Xác định chiều cao vuông góc với đáy; đổi cùng đơn vị trước khi tính.",
    "Tam giác có đáy 8 cm, chiều cao tương ứng 5 cm.",
    "S = 8 × 5 : 2 = 20 cm².",
    [
        "Đáy 12 m, cao 7 m. Tính diện tích.",
        "Diện tích 30 cm², đáy 10 cm. Tính chiều cao.",
    ],
    ["42 m².", "h = 30 × 2 : 10 = 6 cm."],
    "Chiều cao phải ứng với đáy được chọn.",
)
skill(
    "trapezoid",
    "Diện tích hình thang bằng tổng hai đáy × chiều cao : 2.",
    "Tìm hai đáy song song và chiều cao vuông góc.",
    "Hai đáy dài 10 cm và 6 cm, chiều cao 4 cm.",
    "S = (10 + 6) × 4 : 2 = 32 cm².",
    [
        "Hai đáy 12 m và 8 m, cao 5 m. Tính diện tích.",
        "Diện tích 45 cm², tổng hai đáy 18 cm. Tính chiều cao.",
    ],
    ["50 m².", "h = 45 × 2 : 18 = 5 cm."],
    "Không dùng cạnh bên xiên thay cho chiều cao.",
)
skill(
    "circle",
    "Đường kính d = 2r. Dùng π ≈ 3,14: chu vi C = 2r × 3,14; diện tích S = r × r × 3,14.",
    "Xác định bán kính hay đường kính đề cho trước; dùng giá trị π theo yêu cầu.",
    "Hình tròn bán kính 3 cm, dùng π = 3,14.",
    "d = 6 cm; C = 18,84 cm; S = 28,26 cm².",
    [
        "Bán kính 5 cm: tính chu vi với π = 3,14.",
        "Đường kính 4 cm: tính diện tích với π = 3,14.",
    ],
    ["31,4 cm.", "r = 2 cm; S = 12,56 cm²."],
    "Không đưa đường kính trực tiếp vào công thức r × r × π.",
)
skill(
    "drawing",
    "Đo và vẽ hình cần xác định kích thước, điểm mốc và dụng cụ phù hợp.",
    "Phác hình; đo bằng thước, kiểm tra góc bằng ê-ke; với đường tròn dùng compa theo hướng dẫn.",
    "Vẽ hình chữ nhật 6 cm × 4 cm.",
    "Vẽ cạnh dài 6 cm; dựng hai cạnh vuông góc dài 4 cm; nối cạnh còn lại và kiểm tra các góc.",
    [
        "Vẽ tam giác có đáy 8 cm và chiều cao 3 cm, rồi tính diện tích.",
        "Ghép hai tam giác bằng nhau thành hình chữ nhật; so sánh tổng diện tích trước và sau ghép.",
    ],
    [
        "Diện tích = 8 × 3 : 2 = 12 cm²; kiểm tra chiều cao vuông góc.",
        "Diện tích được giữ nguyên khi ghép không chồng lấn, không để khoảng trống.",
    ],
    "Giữ an toàn khi dùng dụng cụ có đầu nhọn.",
)
skill(
    "ratio",
    "Tỉ số a/b so sánh a với b; tỉ số phần trăm bằng a/b × 100%, với b khác 0.",
    "Xác định số được so sánh và số làm chuẩn; dùng cùng đơn vị.",
    "Có 12 bạn nữ trong 30 học sinh.",
    "Tỉ số nữ so với cả lớp = 12/30 = 2/5; tỉ số phần trăm = 40%.",
    [
        "Tìm tỉ số phần trăm của 9 và 25.",
        "18 bạn trong nhóm 60 bạn chiếm bao nhiêu phần trăm?",
    ],
    ["9 : 25 × 100% = 36%.", "18 : 60 × 100% = 30%."],
    "Không đảo hai số trong tỉ số.",
)
skill(
    "map",
    "Tỉ lệ 1:n nghĩa là một đơn vị trên bản đồ bằng n đơn vị thực tế.",
    "Đổi về cùng đơn vị; thực tế = trên bản đồ × n.",
    "Bản đồ tỉ lệ 1:100 000 có đoạn dài 3 cm.",
    "Khoảng cách thực = 300 000 cm = 3 km.",
    [
        "Tỉ lệ 1:10 000, đoạn bản đồ 5 cm. Tính khoảng cách thực theo m.",
        "Khoảng cách thực 2 km, bản đồ 1:100 000. Đoạn bản đồ dài bao nhiêu cm?",
    ],
    ["50 000 cm = 500 m.", "200 000 cm : 100 000 = 2 cm."],
    "Không trộn cm và km khi nhân tỉ lệ.",
)
skill(
    "sum_ratio",
    "Tìm hai số khi biết tổng và tỉ số: tổng số phần là mẫu + tử của tỉ số đã chọn.",
    "Vẽ sơ đồ phần bằng nhau; chia tổng cho số phần rồi nhân từng số phần.",
    "Hai số có tổng 40 và tỉ số 2:3.",
    "Có 5 phần; mỗi phần 40 : 5 = 8; hai số 16 và 24.",
    ["Tổng 72, tỉ số 4:5. Tìm hai số.", "Tổng 84, tỉ số số bé:số lớn = 3:4."],
    ["Mỗi phần 8; hai số 32 và 40.", "Mỗi phần 12; hai số 36 và 48."],
    "Không dùng hiệu số phần khi đề cho tổng.",
)
skill(
    "difference_ratio",
    "Tìm hai số khi biết hiệu và tỉ số: hiệu số phần là số phần lớn trừ số phần bé.",
    "Chia hiệu cho hiệu số phần, rồi nhân số phần của mỗi số.",
    "Hai số có hiệu 18, tỉ số số bé:số lớn = 2:5.",
    "Hiệu 3 phần; mỗi phần 6; số bé 12, số lớn 30.",
    ["Hiệu 24, tỉ số số bé:số lớn = 3:7.", "Hiệu 15, tỉ số số bé:số lớn = 4:5."],
    ["Mỗi phần 6; hai số 18 và 42.", "Mỗi phần 15; hai số 60 và 75."],
    "Không chia hiệu cho tổng số phần.",
)
skill(
    "percentage_value",
    "p% của a bằng a × p : 100.",
    "Đổi phần trăm thành phân số có mẫu 100 hoặc số thập phân.",
    "Tìm 15% của 240.",
    "240 × 15 : 100 = 36.",
    ["Tìm 25% của 360.", "Một sản phẩm giá 200 000 đồng giảm 10%. Tính giá sau giảm."],
    ["90.", "Giảm 20 000 đồng; giá sau giảm 180 000 đồng."],
    "Phân biệt số tiền giảm với số tiền còn phải trả.",
)
skill(
    "calculator",
    "Máy tính hỗ trợ tính toán; người dùng vẫn phải chọn phép tính và kiểm tra kết quả.",
    "Ước lượng trước; nhập đúng số, dấu phép tính; đọc màn hình và đối chiếu.",
    "Dùng máy tính tìm 12,5 × 8.",
    "Ước lượng gần 13 × 8 = 104; nhập 12.5 × 8 = được 100; kết quả hợp lí.",
    [
        "Dùng máy tính kiểm tra 125 × 24.",
        "Tính 18% của 250 bằng máy tính và giải thích phép tính.",
    ],
    ["3 000.", "250 × 18 : 100 = 45."],
    "Dấu chấm trên nhiều máy tính tương ứng dấu phẩy thập phân.",
)
skill(
    "volume",
    "Thể tích đo phần không gian một hình chiếm; có thể đếm các khối đơn vị bằng nhau.",
    "Chọn khối đơn vị, đếm theo hàng/lớp rồi cộng hoặc nhân.",
    "Một khối được xếp 3 hàng, mỗi hàng 4 khối lập phương đơn vị, và có 2 lớp.",
    "Có 3 × 4 × 2 = 24 khối đơn vị; thể tích 24 đơn vị khối.",
    [
        "Khối có 5 hàng, mỗi hàng 3 khối, 2 lớp. Tính số khối.",
        "Hai khối lần lượt chứa 18 và 25 khối đơn vị giống nhau. Khối nào lớn hơn?",
    ],
    ["30 khối đơn vị.", "Khối 25 đơn vị lớn hơn 7 đơn vị khối."],
    "Phải dùng các khối đơn vị cùng kích thước để so sánh.",
)
skill(
    "volume_units",
    "1 dm³ = 1 000 cm³; 1 m³ = 1 000 dm³ = 1 000 000 cm³.",
    "Mỗi bậc thể tích liền kề nhân/chia 1 000.",
    "Đổi 2,5 dm³ thành cm³.",
    "2,5 × 1 000 = 2 500 cm³.",
    ["Đổi 3 200 cm³ thành dm³.", "Đổi 0,4 m³ thành dm³."],
    ["3,2 dm³.", "400 dm³."],
    "Không dùng hệ số 100 của diện tích cho thể tích.",
)
skill(
    "nets",
    "Hình khai triển cho thấy các mặt khi trải phẳng; hình lập phương có 6 mặt vuông bằng nhau.",
    "Xác định mặt đáy, mặt bên và các cạnh ghép; thử gấp trên mô hình giấy an toàn.",
    "Hình hộp chữ nhật có kích thước 6 cm, 4 cm, 3 cm.",
    "Có 3 cặp mặt: 6 × 4, 6 × 3 và 4 × 3; khi gấp, các cạnh tương ứng phải khớp.",
    [
        "Một hình khai triển lập phương cần bao nhiêu mặt vuông bằng nhau?",
        "Mặt bên của hình trụ khi trải phẳng có dạng gì?",
    ],
    [
        "6 mặt; không phải mọi cách xếp 6 hình vuông đều gấp được thành lập phương.",
        "Hình chữ nhật; hai đáy là hai hình tròn.",
    ],
    "Kiểm tra các mặt có chồng lên nhau khi gấp hay không.",
)
skill(
    "box_area",
    "Diện tích xung quanh hộp chữ nhật = chu vi đáy × chiều cao; toàn phần cộng thêm diện tích hai đáy.",
    "Chọn đáy với chiều dài và rộng; tính diện tích bên rồi cộng hai đáy nếu cần.",
    "Hộp dài 6 cm, rộng 4 cm, cao 3 cm.",
    "Sxq = (6 + 4) × 2 × 3 = 60 cm²; Stp = 60 + 2 × 6 × 4 = 108 cm².",
    ["Hộp 5 cm × 3 cm × 4 cm: tính Sxq.", "Với hộp đó, tính Stp."],
    ["64 cm².", "64 + 30 = 94 cm²."],
    "Diện tích toàn phần chỉ tính đủ 6 mặt khi hộp kín.",
)
skill(
    "cube_area",
    "Lập phương cạnh a có diện tích xung quanh 4a² và toàn phần 6a².",
    "Tính diện tích một mặt rồi nhân số mặt cần tính.",
    "Lập phương cạnh 3 cm.",
    "Một mặt 9 cm²; Sxq = 36 cm²; Stp = 54 cm².",
    ["Cạnh 4 cm: tính Sxq.", "Cạnh 5 cm: tính Stp."],
    ["64 cm².", "150 cm²."],
    "Không nhầm diện tích với thể tích a³.",
)
skill(
    "box_volume",
    "Thể tích hình hộp chữ nhật V = dài × rộng × cao.",
    "Đổi ba kích thước về cùng đơn vị rồi nhân.",
    "Hộp dài 8 cm, rộng 5 cm, cao 3 cm.",
    "V = 8 × 5 × 3 = 120 cm³.",
    [
        "Hộp 6 cm × 4 cm × 2 cm: tính thể tích.",
        "Hộp thể tích 180 cm³, đáy 6 cm × 5 cm: tính chiều cao.",
    ],
    ["48 cm³.", "h = 180 : (6 × 5) = 6 cm."],
    "Đơn vị kết quả là đơn vị khối.",
)
skill(
    "cube_volume",
    "Thể tích hình lập phương cạnh a là a × a × a.",
    "Nhân ba kích thước bằng nhau và ghi đơn vị khối.",
    "Lập phương cạnh 4 cm.",
    "V = 4 × 4 × 4 = 64 cm³.",
    ["Cạnh 3 cm: tính thể tích.", "Cạnh 5 cm: tính thể tích."],
    ["27 cm³.", "125 cm³."],
    "Không dùng 6a² để tính thể tích.",
)
skill(
    "time_units",
    "1 giờ = 60 phút, 1 phút = 60 giây; thời gian không đổi theo hệ cơ số 100.",
    "Tách phần giờ và phút hoặc đổi tất cả về một đơn vị.",
    "Đổi 2 giờ 15 phút thành phút.",
    "2 × 60 + 15 = 135 phút.",
    ["Đổi 150 phút thành giờ và phút.", "Đổi 1,5 giờ thành phút."],
    ["2 giờ 30 phút.", "90 phút."],
    "0,5 giờ là 30 phút, không phải 50 phút.",
)
skill(
    "time_add",
    "Cộng/trừ số đo thời gian theo từng đơn vị, đổi 60 phút thành một giờ khi cần.",
    "Khi trừ không đủ phút, đổi một giờ thành 60 phút.",
    "Tính 3 giờ 10 phút − 1 giờ 45 phút.",
    "3 giờ 10 phút = 2 giờ 70 phút; hiệu = 1 giờ 25 phút.",
    ["Tính 1 giờ 40 phút + 2 giờ 35 phút.", "Tính 5 giờ 20 phút − 2 giờ 50 phút."],
    ["4 giờ 15 phút.", "2 giờ 30 phút."],
    "Không đổi thời gian bằng cách thêm hoặc bớt 100 phút.",
)
skill(
    "time_multiply",
    "Nhân/chia số đo thời gian cần giữ quan hệ 60 phút mỗi giờ.",
    "Có thể đổi hoàn toàn về phút trước khi tính, sau đó đổi lại.",
    "Tính 1 giờ 20 phút × 3.",
    "1 giờ 20 phút = 80 phút; 80 × 3 = 240 phút = 4 giờ.",
    ["Tính 2 giờ 15 phút × 2.", "Tính 3 giờ 30 phút : 2."],
    ["4 giờ 30 phút.", "210 phút : 2 = 105 phút = 1 giờ 45 phút."],
    "Không chia phần giờ và phần phút độc lập nếu có số dư cần đổi.",
)
skill(
    "speed",
    "Chuyển động đều: v = s/t, s = v × t, t = s/v; t và v trong phép chia phải khác 0.",
    "Đổi thời gian theo đơn vị của vận tốc; chọn công thức từ đại lượng cần tìm.",
    "Xe đi 90 km trong 1,5 giờ.",
    "v = 90 : 1,5 = 60 km/giờ.",
    [
        "Vận tốc 40 km/giờ, thời gian 2,5 giờ: tính quãng đường.",
        "Quãng đường 120 km, vận tốc 60 km/giờ: tính thời gian.",
    ],
    ["100 km.", "2 giờ."],
    "Không dùng số phút trực tiếp với vận tốc km/giờ.",
)
skill(
    "data",
    "Thu thập số liệu cần câu hỏi rõ; phân loại theo tiêu chí; kiểm tra số lượng quan sát.",
    "Lập bảng và ghi mỗi quan sát vào đúng nhóm; cộng tần số để kiểm tra.",
    "Có 6 kết quả: đỏ, xanh, đỏ, vàng, xanh, đỏ.",
    "Bảng đếm: đỏ 3; xanh 2; vàng 1; tổng 6.",
    [
        "Với số liệu 2, 3, 2, 4, 3, 2: giá trị 2 xuất hiện mấy lần?",
        "Từ số liệu đó, lập bảng đếm các giá trị.",
    ],
    ["3 lần.", "2: 3 lần; 3: 2 lần; 4: 1 lần; tổng 6."],
    "Không bỏ một quan sát vì nó trùng với quan sát trước.",
)
skill(
    "pie",
    "Biểu đồ quạt tròn biểu diễn các phần của một tổng; các tỉ lệ phần trăm cộng thành 100%.",
    "Đọc chú giải và tỉ lệ; số lượng của nhóm = tổng × tỉ lệ : 100.",
    "Biểu đồ sở thích của 40 bạn có nhóm thích đọc sách 25%.",
    "Số bạn thích đọc = 40 × 25 : 100 = 10 bạn.",
    [
        "Nhóm chiếm 30% của 50 bạn có bao nhiêu bạn?",
        "Ba nhóm có 20%, 35%, và phần còn lại. Phần còn lại bao nhiêu phần trăm?",
    ],
    ["15 bạn.", "100% − 20% − 35% = 45%."],
    "Không dùng phần trăm nếu chưa biết tổng khi cần tính số lượng.",
)
skill(
    "frequency",
    "Tỉ số số lần xuất hiện một sự kiện so với số lần thử bằng số lần xuất hiện chia tổng lần thử.",
    "Đếm số lần sự kiện xuất hiện và tất cả lần thử; viết phân số rồi rút gọn.",
    "Trong 20 lần thử, có 8 lần xuất hiện màu đỏ.",
    "Tỉ số thực nghiệm = 8/20 = 2/5 = 40%.",
    [
        "Trong 30 lần thử có 9 lần xuất hiện sự kiện A. Tìm tỉ số.",
        "Một nhóm ghi 12 lần mặt sấp và 8 lần mặt ngửa. Tỉ số mặt ngửa là bao nhiêu?",
    ],
    ["9/30 = 3/10 = 30%.", "8/(12 + 8) = 2/5 = 40%."],
    "Tỉ số ghi nhận không bảo đảm lần thử tiếp theo sẽ có đúng kết quả ấy.",
)

MAP = {
    1: ["natural"],
    2: ["operations"],
    3: ["fraction"],
    4: ["decimal_fraction"],
    5: ["fraction_ops"],
    6: ["unlike_fraction"],
    7: ["mixed"],
    8: ["plane", "measure_decimal"],
    9: ["natural", "unlike_fraction", "mixed"],
    10: ["decimal"],
    11: ["compare_decimal"],
    12: ["measure_decimal"],
    13: ["round"],
    14: ["decimal", "compare_decimal", "round"],
    15: ["land_area"],
    16: ["area_units"],
    17: ["measure_decimal", "area_units"],
    18: ["land_area", "area_units"],
    19: ["add_decimal"],
    20: ["subtract_decimal"],
    21: ["multiply_decimal"],
    22: ["divide_decimal"],
    23: ["powers_ten"],
    24: ["add_decimal", "subtract_decimal", "multiply_decimal", "divide_decimal"],
    25: ["triangle"],
    26: ["trapezoid"],
    27: ["circle"],
    28: ["drawing"],
    29: ["triangle", "trapezoid", "circle"],
    30: ["decimal", "compare_decimal", "round"],
    31: ["add_decimal", "subtract_decimal", "multiply_decimal", "divide_decimal"],
    32: ["plane", "drawing"],
    33: ["plane", "triangle", "trapezoid", "circle"],
    34: ["measure_decimal", "land_area", "area_units"],
    35: ["fraction", "decimal", "plane"],
    36: ["ratio"],
    37: ["map"],
    38: ["sum_ratio"],
    39: ["difference_ratio"],
    40: ["ratio"],
    41: ["percentage_value"],
    42: ["calculator"],
    43: ["calculator", "percentage_value"],
    44: ["ratio", "sum_ratio", "difference_ratio", "percentage_value"],
    45: ["volume"],
    46: ["volume_units"],
    47: ["volume_units"],
    48: ["volume", "volume_units"],
    49: ["nets"],
    50: ["box_area"],
    51: ["cube_area"],
    52: ["box_volume"],
    53: ["cube_volume"],
    54: ["box_volume", "cube_volume"],
    55: ["nets", "box_area", "cube_area", "box_volume", "cube_volume"],
    56: ["time_units"],
    57: ["time_add"],
    58: ["time_multiply"],
    59: ["speed"],
    60: ["speed"],
    61: ["speed", "time_units"],
    62: ["speed", "time_add", "time_multiply"],
    63: ["data"],
    64: ["pie"],
    65: ["frequency"],
    66: ["data", "pie"],
    67: ["data", "pie", "frequency"],
    68: ["natural", "fraction", "decimal"],
    69: [
        "operations",
        "fraction_ops",
        "add_decimal",
        "multiply_decimal",
        "divide_decimal",
    ],
    70: ["ratio", "sum_ratio", "difference_ratio", "percentage_value"],
    71: ["plane", "triangle", "trapezoid", "circle", "nets"],
    72: ["measure_decimal", "land_area", "volume_units", "time_units"],
    73: ["speed", "time_units"],
    74: ["data", "pie", "frequency"],
    75: ["decimal", "percentage_value", "box_volume", "speed", "data"],
}


def build():
    books = json.loads(
        (ROOT / "data/seeds/textbook_units.json").read_text(encoding="utf-8")
    )["books"]
    book = next(b for b in books if b["grade"] == 5 and b["subject"] == "toan")
    documents = []
    seen = set()
    for unit in book["units"]:
        match = re.search(r"Bài\s+(\d+)", unit["title"], re.I)
        if not match:
            raise ValueError("Unexpected Math5 unit: " + unit["title"])
        number = int(match.group(1))
        seen.add(number)
        keys = MAP[number]
        items = [SKILLS[key] for key in keys]
        sections = [
            dict(
                heading="Mục tiêu và phạm vi",
                text=f"Ôn và luyện nội dung {unit['title']}. Ghi chú này tự biên soạn theo mục lục nguồn tham khảo; chưa xác minh mọi ấn bản với nhà xuất bản. Bài có thể cần thêm dạng nâng cao sau khi giáo viên thẩm định.",
            )
        ]
        for i, (rule, method, example, worked, tasks, answers, mistake) in enumerate(
            items, 1
        ):
            prefix = f"{i}. " if len(items) > 1 else ""
            sections.extend(
                [
                    dict(
                        heading=prefix + "Kiến thức và cách làm",
                        text=rule + "\nCách làm: " + method,
                    ),
                    dict(
                        heading=prefix + "Ví dụ từng bước",
                        text=example + "\nLời giải: " + worked,
                    ),
                    dict(
                        heading=prefix + "Bài tập tự luyện",
                        text="\n".join(
                            f"{j}. {task}" for j, task in enumerate(tasks, 1)
                        ),
                    ),
                    dict(
                        heading=prefix + "Lời giải bài tập",
                        text="\n".join(
                            f"{j}. {answer}" for j, answer in enumerate(answers, 1)
                        ),
                    ),
                    dict(heading=prefix + "Lỗi cần tránh", text=mistake),
                ]
            )
        documents.append(
            dict(
                id=f"kntt_math5_lesson_{number:02d}",
                grade=5,
                subject="toan",
                title=unit["title"],
                topic=unit["chapter"],
                chapter=unit["chapter"],
                lesson_order=number,
                curriculum_unit_id=unit["id"],
                textbook="ket_noi_tri_thuc",
                kind="study_notes",
                semester=1 if number <= 35 else 2,
                summary=f"Kiến thức, cách làm, ví dụ có lời giải và {2 * len(items)} bài tập tự luyện.",
                sections=sections,
                author="Kho Học 1–12",
                source_name="Ghi chú tự biên soạn; mục lục tham khảo Loigiaihay",
                source_url=unit["source_url"],
                source_type="original",
                license="original_content",
                rights_evidence="Nội dung giải thích và bài tập được soạn riêng; chỉ tên bài/chủ đề và liên kết dùng nhận diện mục lục nguồn. Chưa thẩm định chuyên môn độc lập.",
                distribution_allowed=True,
                download_allowed=False,
            )
        )
    assert seen == set(range(1, 76))
    (ROOT / "data/library/curriculum_documents.json").write_text(
        json.dumps(dict(documents=documents), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Authored",
        len(documents),
        "Math 5 lesson notes; practice tasks",
        sum(2 * len(MAP[n]) for n in seen),
    )


if __name__ == "__main__":
    build()
