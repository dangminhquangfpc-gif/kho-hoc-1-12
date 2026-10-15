"""Original, explicitly authored worked solutions at primary-school level.

Each entry supplies the example and both practice solutions, not a wrapper
around the old answer-only strings. Textbook mapping is secondary-source only.
"""


def solution(steps, answer):
    return "Lời giải\n" + "\n".join(steps) + "\nĐáp số: " + answer


WORKED = {}


def worked(key, example, first, second):
    WORKED[key] = tuple(
        solution(steps, answer) for steps, answer in (example, first, second)
    )


worked(
    "natural",
    (
        [
            "Số 42 305 gồm 4 chục nghìn, 2 nghìn, 3 trăm, 0 chục và 5 đơn vị.",
            "Ta có: 42 305 = 40 000 + 2 000 + 300 + 5.",
            "Chữ số 3 ở hàng trăm nên có giá trị là: 3 × 100 = 300.",
        ],
        "42 305 = 40 000 + 2 000 + 300 + 5; giá trị chữ số 3 là 300.",
    ),
    (
        [
            "Trong số 57 204, chữ số 7 ở hàng nghìn.",
            "Giá trị của chữ số 7 là:",
            "7 × 1 000 = 7 000.",
        ],
        "7 000.",
    ),
    (
        [
            "Số 29 999 có 2 chục nghìn; hai số còn lại có 3 chục nghìn nên 29 999 bé nhất.",
            "Hai số 30 102 và 30 120 có các chữ số đến hàng trăm giống nhau.",
            "Ở hàng chục, 0 < 2 nên 30 102 < 30 120.",
        ],
        "29 999; 30 102; 30 120.",
    ),
)
worked(
    "operations",
    (
        [
            "Ta thực hiện phép cộng trong ngoặc trước, rồi phép chia, cuối cùng là phép cộng:",
            "240 : (4 + 2) + 15",
            "= 240 : 6 + 15",
            "= 40 + 15",
            "= 55.",
        ],
        "55.",
    ),
    (
        [
            "Thực hiện phép nhân trước, phép cộng sau:",
            "36 × 4 + 28",
            "= 144 + 28",
            "= 172.",
        ],
        "172.",
    ),
    (
        [
            "Thực hiện phép cộng trong ngoặc trước:",
            "(125 + 75) : 5",
            "= 200 : 5",
            "= 40.",
        ],
        "40.",
    ),
)
worked(
    "fraction",
    (
        [
            "Tử số 12 và mẫu số 18 cùng chia hết cho 6.",
            "Chia cả tử số và mẫu số cho 6:",
            "12/18 = (12 : 6)/(18 : 6) = 2/3.",
            "Vì 2 và 3 không cùng chia hết cho số tự nhiên nào lớn hơn 1 nên 2/3 là phân số tối giản.",
        ],
        "2/3.",
    ),
    (
        [
            "Tử số 15 và mẫu số 20 cùng chia hết cho 5.",
            "15/20 = (15 : 5)/(20 : 5) = 3/4.",
            "Phân số 3/4 là phân số tối giản.",
        ],
        "3/4.",
    ),
    (
        [
            "Quy đồng mẫu số hai phân số:",
            "2/3 = (2 × 4)/(3 × 4) = 8/12;",
            "3/4 = (3 × 3)/(4 × 3) = 9/12.",
            "Vì 8 < 9 nên 8/12 < 9/12. Vậy 2/3 < 3/4.",
        ],
        "2/3 < 3/4.",
    ),
)
worked(
    "decimal_fraction",
    (
        [
            "Vì 5 × 2 = 10 nên nhân cả tử số và mẫu số với 2:",
            "3/5 = (3 × 2)/(5 × 2) = 6/10.",
            "Phân số 6/10 có mẫu số là 10 nên là phân số thập phân.",
        ],
        "6/10.",
    ),
    (
        [
            "Vì 20 × 5 = 100 nên nhân cả tử số và mẫu số với 5:",
            "7/20 = (7 × 5)/(20 × 5) = 35/100.",
        ],
        "35/100.",
    ),
    (
        [
            "Tử số 45 và mẫu số 100 cùng chia hết cho 5.",
            "45/100 = (45 : 5)/(100 : 5) = 9/20.",
            "Phân số 9/20 là phân số tối giản.",
        ],
        "9/20.",
    ),
)
worked(
    "fraction_ops",
    (
        [
            "Nhân hai phân số:",
            "2/3 × 3/4 = (2 × 3)/(3 × 4) = 6/12 = 1/2.",
            "Chia hai phân số:",
            "2/3 : 4/5 = 2/3 × 5/4 = 10/12 = 5/6.",
        ],
        "1/2 và 5/6.",
    ),
    (
        [
            "Hai phân số có cùng mẫu số 5 nên cộng hai tử số và giữ nguyên mẫu số:",
            "3/5 + 1/5 = (3 + 1)/5 = 4/5.",
        ],
        "4/5.",
    ),
    (
        [
            "Phân số đảo ngược của 3/8 là 8/3.",
            "Lấy phân số thứ nhất nhân với phân số đảo ngược của phân số thứ hai:",
            "3/4 : 3/8 = 3/4 × 8/3 = 24/12 = 2.",
        ],
        "2.",
    ),
)
worked(
    "unlike_fraction",
    (
        [
            "Quy đồng mẫu số:",
            "3/4 = 9/12; 1/6 = 2/12.",
            "Thực hiện phép trừ:",
            "3/4 − 1/6 = 9/12 − 2/12 = 7/12.",
        ],
        "7/12.",
    ),
    (
        [
            "Quy đồng mẫu số:",
            "1/2 = 5/10; 2/5 = 4/10.",
            "Thực hiện phép cộng:",
            "1/2 + 2/5 = 5/10 + 4/10 = 9/10.",
        ],
        "9/10.",
    ),
    (
        [
            "Quy đồng mẫu số:",
            "5/6 = 10/12; 1/4 = 3/12.",
            "Thực hiện phép trừ:",
            "5/6 − 1/4 = 10/12 − 3/12 = 7/12.",
        ],
        "7/12.",
    ),
)
worked(
    "mixed",
    (
        [
            "Lấy phần nguyên nhân với mẫu số rồi cộng tử số; giữ nguyên mẫu số:",
            "2 và 3/5 = (2 × 5 + 3)/5 = 13/5.",
        ],
        "13/5.",
    ),
    (
        [
            "Lấy 3 nhân với 4 rồi cộng 1, được 13; giữ mẫu số 4:",
            "3 và 1/4 = (3 × 4 + 1)/4 = 13/4.",
        ],
        "13/4.",
    ),
    (
        [
            "Chia tử số cho mẫu số:",
            "11 : 3 = 3 (dư 2).",
            "Thương 3 là phần nguyên; số dư 2 là tử số của phần phân số, mẫu số vẫn là 3.",
            "Vậy 11/3 = 3 và 2/3.",
        ],
        "3 và 2/3.",
    ),
)
worked(
    "plane",
    (
        [
            "Chu vi hình chữ nhật là:",
            "(8 + 5) × 2 = 26 (cm)",
            "Diện tích hình chữ nhật là:",
            "8 × 5 = 40 (cm²)",
        ],
        "Chu vi: 26 cm; diện tích: 40 cm².",
    ),
    (
        [
            "Chu vi hình vuông là:",
            "6 × 4 = 24 (cm)",
            "Diện tích hình vuông là:",
            "6 × 6 = 36 (cm²)",
        ],
        "Chu vi: 24 cm; diện tích: 36 cm².",
    ),
    (["Diện tích hình chữ nhật là:", "12 × 4 = 48 (m²)"], "48 m²."),
)
worked(
    "decimal",
    (
        [
            "Số 3,407 có phần nguyên là 3; phần thập phân có 4 phần mười, 0 phần trăm và 7 phần nghìn.",
            "Ta viết:",
            "3,407 = 3 + 4/10 + 0/100 + 7/1 000.",
        ],
        "3 + 4/10 + 0/100 + 7/1 000.",
    ),
    (
        [
            "Ta có: 5/10 = 0,5 và 3/100 = 0,03.",
            "Do đó:",
            "2 + 5/10 + 3/100 = 2 + 0,5 + 0,03 = 2,53.",
        ],
        "2,53.",
    ),
    (
        [
            "Trong số 1,26, chữ số 6 ở hàng phần trăm.",
            "Giá trị của chữ số 6 là:",
            "6/100 = 0,06.",
        ],
        "6 phần trăm, tức 0,06.",
    ),
)
worked(
    "compare_decimal",
    (
        [
            "Viết 4,7 = 4,70.",
            "Hai số có phần nguyên cùng bằng 4.",
            "Ở hàng phần mười, 7 > 6 nên 4,70 > 4,65.",
        ],
        "4,7 > 4,65.",
    ),
    (
        [
            "Viết 3,1 = 3,10.",
            "Hai số có phần nguyên cùng bằng 3.",
            "Ở hàng phần mười, 0 < 1 nên 3,09 < 3,10.",
        ],
        "3,09 < 3,1.",
    ),
    (
        [
            "Viết 2,5 = 2,50. Ba số có phần nguyên cùng bằng 2.",
            "Các chữ số hàng phần mười lần lượt là 5, 0 và 1.",
            "Vì 0 < 1 < 5 nên 2,05 < 2,15 < 2,50.",
        ],
        "2,05; 2,15; 2,5.",
    ),
)
worked(
    "measure_decimal",
    (
        [
            "Vì 1 m = 100 cm nên 35 cm = 35/100 m = 0,35 m.",
            "Vậy 2 m 35 cm = 2 m + 0,35 m = 2,35 m.",
        ],
        "2,35 m.",
    ),
    (
        [
            "Vì 1 kg = 1 000 g nên 250 g = 250/1 000 kg = 0,25 kg.",
            "Vậy 4 kg 250 g = 4 kg + 0,25 kg = 4,25 kg.",
        ],
        "4,25 kg.",
    ),
    (
        [
            "Vì 1 m = 100 cm nên 8 cm = 8/100 m = 0,08 m.",
            "Vậy 3 m 8 cm = 3 m + 0,08 m = 3,08 m.",
        ],
        "3,08 m.",
    ),
)
worked(
    "round",
    (
        [
            "Chữ số hàng phần trăm của 7,346 là 4; chữ số ngay bên phải là 6.",
            "Vì 6 lớn hơn 5 nên tăng chữ số hàng phần trăm thêm 1 và bỏ chữ số hàng phần nghìn.",
            "Làm tròn 7,346 đến hàng phần trăm được 7,35.",
        ],
        "7,35.",
    ),
    (
        [
            "Chữ số hàng phần mười của 2,74 là 7; chữ số ngay bên phải là 4.",
            "Vì 4 bé hơn 5 nên giữ nguyên chữ số 7 và bỏ chữ số hàng phần trăm.",
            "Làm tròn 2,74 đến hàng phần mười được 2,7.",
        ],
        "2,7.",
    ),
    (
        [
            "Chữ số hàng đơn vị của 8,96 là 8; chữ số ngay bên phải là 9.",
            "Vì 9 lớn hơn 5 nên tăng chữ số hàng đơn vị thêm 1 và bỏ phần thập phân.",
            "Làm tròn 8,96 đến hàng đơn vị được 9.",
        ],
        "9.",
    ),
)
worked(
    "land_area",
    (
        ["Vì 1 ha = 10 000 m² nên:", "2,5 ha = 2,5 × 10 000 m² = 25 000 m²."],
        "25 000 m².",
    ),
    (["Vì 1 km² = 100 ha nên:", "3 km² = 3 × 100 ha = 300 ha."], "300 ha."),
    (
        ["Vì 10 000 m² = 1 ha nên:", "45 000 m² = 45 000 : 10 000 ha = 4,5 ha."],
        "4,5 ha.",
    ),
)
worked(
    "area_units",
    (["Vì 1 m² = 100 dm² nên:", "3,2 m² = 3,2 × 100 dm² = 320 dm²."], "320 dm²."),
    (["Vì 100 cm² = 1 dm² nên:", "450 cm² = 450 : 100 dm² = 4,5 dm²."], "4,5 dm²."),
    (
        ["Vì 1 m² = 10 000 cm² nên:", "2 m² = 2 × 10 000 cm² = 20 000 cm²."],
        "20 000 cm².",
    ),
)
worked(
    "add_decimal",
    (
        [
            "Viết 4,8 = 4,80; đặt tính sao cho các chữ số cùng hàng và dấu phẩy thẳng cột:",
            "```\n  12,35\n+  4,80\n-------\n  17,15\n```",
            "Cộng từ phải sang trái như cộng số tự nhiên; viết dấu phẩy ở tổng thẳng cột với các dấu phẩy của hai số hạng.",
            "12,35 + 4,8 = 17,15.",
        ],
        "17,15.",
    ),
    (
        [
            "Viết 2,7 = 2,70 rồi đặt tính:",
            "```\n   3,45\n+  2,70\n-------\n   6,15\n```",
            "Cộng theo từng hàng, nhớ sang hàng bên trái khi cần; giữ dấu phẩy thẳng cột.",
            "3,45 + 2,7 = 6,15.",
        ],
        "6,15.",
    ),
    (
        [
            "Đặt tính rồi cộng:",
            "```\n   0,86\n+  1,25\n-------\n   2,11\n```",
            "6 + 5 = 11, viết 1 nhớ 1; 8 + 2 + 1 = 11, viết 1 nhớ 1; 0 + 1 + 1 = 2.",
            "0,86 + 1,25 = 2,11.",
        ],
        "2,11.",
    ),
)
worked(
    "subtract_decimal",
    (
        [
            "Viết 10 = 10,00; đặt các chữ số cùng hàng và dấu phẩy thẳng cột:",
            "```\n  10,00\n-  3,75\n-------\n   6,25\n```",
            "Trừ từ phải sang trái, đổi một đơn vị ở hàng bên trái khi cần.",
            "10 − 3,75 = 6,25.",
        ],
        "6,25.",
    ),
    (
        [
            "Viết 8,2 = 8,20 rồi đặt tính:",
            "```\n   8,20\n-  1,46\n-------\n   6,74\n```",
            "Trừ theo từng hàng và viết dấu phẩy của hiệu thẳng cột với các dấu phẩy đã cho.",
            "8,2 − 1,46 = 6,74.",
        ],
        "6,74.",
    ),
    (
        [
            "Viết 5 = 5,00 rồi đặt tính:",
            "```\n   5,00\n-  0,85\n-------\n   4,15\n```",
            "Thực hiện phép trừ có nhớ từ phải sang trái.",
            "5 − 0,85 = 4,15.",
        ],
        "4,15.",
    ),
)
worked(
    "multiply_decimal",
    (
        [
            "Nhân như nhân các số tự nhiên:",
            "24 × 15 = 360.",
            "Hai thừa số 2,4 và 1,5 có tất cả hai chữ số ở phần thập phân.",
            "Tách ở tích 360 hai chữ số từ phải sang trái, được 3,60.",
            "Vậy 2,4 × 1,5 = 3,60 = 3,6.",
        ],
        "3,6.",
    ),
    (
        [
            "Nhân như nhân các số tự nhiên: 8 × 5 = 40.",
            "Hai thừa số có tất cả hai chữ số ở phần thập phân nên tích là 0,40.",
            "0,8 × 0,5 = 0,40 = 0,4.",
        ],
        "0,4.",
    ),
    (
        [
            "Nhân như nhân các số tự nhiên: 325 × 4 = 1 300.",
            "Hai thừa số có tất cả hai chữ số ở phần thập phân nên tích là 13,00.",
            "3,25 × 4 = 13,00 = 13.",
        ],
        "13.",
    ),
)
worked(
    "divide_decimal",
    (
        [
            "Chuyển dấu phẩy của cả số bị chia và số chia sang phải một chữ số:",
            "7,2 : 0,3 = 72 : 3.",
            "Thực hiện phép chia: 72 : 3 = 24.",
            "Thử lại: 24 × 0,3 = 7,2.",
        ],
        "24.",
    ),
    (
        [
            "Chuyển dấu phẩy của cả hai số sang phải một chữ số:",
            "4,5 : 0,5 = 45 : 5 = 9.",
            "Thử lại: 9 × 0,5 = 4,5.",
        ],
        "9.",
    ),
    (
        [
            "Chia phần nguyên: 6 : 4 được 1, dư 2.",
            "Viết dấu phẩy vào bên phải thương 1; hạ chữ số 4 được 24 phần mười.",
            "24 : 4 = 6, viết 6 vào hàng phần mười của thương.",
            "6,4 : 4 = 1,6. Thử lại: 1,6 × 4 = 6,4.",
        ],
        "1,6.",
    ),
)
worked(
    "powers_ten",
    (
        [
            "Nhân với 100: chuyển dấu phẩy sang phải hai chữ số, được 3,45 × 100 = 345.",
            "Nhân với 0,1: chuyển dấu phẩy sang trái một chữ số, được 3,45 × 0,1 = 0,345.",
        ],
        "345 và 0,345.",
    ),
    (
        [
            "Chia cho 100: chuyển dấu phẩy sang trái hai chữ số.",
            "Viết thêm chữ số 0 ở bên trái khi cần: 12,6 : 100 = 0,126.",
        ],
        "0,126.",
    ),
    (
        [
            "Chia cho 0,01 có thể chuyển dấu phẩy của cả hai số sang phải hai chữ số:",
            "0,48 : 0,01 = 48 : 1 = 48.",
        ],
        "48.",
    ),
)
worked(
    "triangle",
    (["Diện tích hình tam giác là:", "8 × 5 : 2 = 20 (cm²)"], "20 cm²."),
    (["Diện tích hình tam giác là:", "12 × 7 : 2 = 42 (m²)"], "42 m²."),
    (
        [
            "Tích của độ dài đáy và chiều cao là:",
            "30 × 2 = 60 (cm²)",
            "Chiều cao tương ứng với đáy 10 cm là:",
            "60 : 10 = 6 (cm)",
        ],
        "6 cm.",
    ),
)
worked(
    "trapezoid",
    (["Diện tích hình thang là:", "(10 + 6) × 4 : 2 = 32 (cm²)"], "32 cm²."),
    (["Diện tích hình thang là:", "(12 + 8) × 5 : 2 = 50 (m²)"], "50 m²."),
    (
        [
            "Tích của tổng độ dài hai đáy và chiều cao là:",
            "45 × 2 = 90 (cm²)",
            "Chiều cao hình thang là:",
            "90 : 18 = 5 (cm)",
        ],
        "5 cm.",
    ),
)
worked(
    "circle",
    (
        [
            "Đường kính hình tròn là:",
            "3 × 2 = 6 (cm)",
            "Chu vi hình tròn là:",
            "6 × 3,14 = 18,84 (cm)",
            "Diện tích hình tròn là:",
            "3 × 3 × 3,14 = 28,26 (cm²)",
        ],
        "Đường kính: 6 cm; chu vi: 18,84 cm; diện tích: 28,26 cm².",
    ),
    (["Chu vi hình tròn là:", "5 × 2 × 3,14 = 31,4 (cm)"], "31,4 cm."),
    (
        [
            "Bán kính hình tròn là:",
            "4 : 2 = 2 (cm)",
            "Diện tích hình tròn là:",
            "2 × 2 × 3,14 = 12,56 (cm²)",
        ],
        "12,56 cm².",
    ),
)
worked(
    "drawing",
    (
        [
            "Vẽ đoạn thẳng AB dài 6 cm.",
            "Dùng ê-ke vẽ AD và BC cùng vuông góc với AB, cùng phía với AB, mỗi đoạn dài 4 cm.",
            "Nối C với D. Dùng thước và ê-ke kiểm tra AB = CD = 6 cm, AD = BC = 4 cm và bốn góc vuông.",
        ],
        "Hình chữ nhật ABCD có chiều dài 6 cm, chiều rộng 4 cm (học sinh tự vẽ).",
    ),
    (
        [
            "Vẽ đoạn thẳng AB dài 8 cm. Tại A, dựng AH vuông góc với AB và dài 3 cm; nối H với B.",
            "Tam giác ABH có đáy AB = 8 cm và chiều cao AH = 3 cm.",
            "Diện tích hình tam giác là:",
            "8 × 3 : 2 = 12 (cm²)",
        ],
        "Hình vẽ theo hướng dẫn; diện tích: 12 cm².",
    ),
    (
        [
            "Cắt một hình chữ nhật theo đường chéo để được hai tam giác vuông bằng nhau.",
            "Ghép hai tam giác đó trở lại thành hình chữ nhật, không chồng lên nhau và không để khoảng trống.",
            "Các mảnh ghép không thay đổi nên diện tích hình chữ nhật bằng tổng diện tích hai tam giác.",
        ],
        "Diện tích sau ghép bằng tổng diện tích hai tam giác trước ghép.",
    ),
)
worked(
    "ratio",
    (
        [
            "Tỉ số của số bạn nữ và số học sinh cả lớp là:",
            "12 : 30 = 12/30 = 2/5.",
            "Tỉ số phần trăm của số bạn nữ và số học sinh cả lớp là:",
            "12 : 30 = 0,4; 0,4 × 100 = 40.",
            "Vậy số bạn nữ chiếm 40% số học sinh cả lớp.",
        ],
        "2/5; 40%.",
    ),
    (
        [
            "Tìm thương của 9 và 25:",
            "9 : 25 = 0,36.",
            "Nhân thương đó với 100: 0,36 × 100 = 36.",
            "Tỉ số phần trăm của 9 và 25 là 36%.",
        ],
        "36%.",
    ),
    (
        [
            "Tỉ số của số bạn đã cho và số bạn cả nhóm là:",
            "18 : 60 = 0,3.",
            "Ta có: 0,3 = 30/100 = 30%.",
            "Vậy 18 bạn chiếm 30% số bạn cả nhóm.",
        ],
        "30%.",
    ),
)
worked(
    "map",
    (
        [
            "Khoảng cách thực tế là:",
            "3 × 100 000 = 300 000 (cm)",
            "Đổi: 300 000 cm = 3 km.",
        ],
        "3 km.",
    ),
    (
        [
            "Khoảng cách thực tế là:",
            "5 × 10 000 = 50 000 (cm)",
            "Đổi: 50 000 cm = 500 m.",
        ],
        "500 m.",
    ),
    (
        [
            "Đổi: 2 km = 200 000 cm.",
            "Độ dài đoạn thẳng trên bản đồ là:",
            "200 000 : 100 000 = 2 (cm)",
        ],
        "2 cm.",
    ),
)
worked(
    "sum_ratio",
    (
        [
            "Theo tỉ số 2 : 3, coi số bé gồm 2 phần bằng nhau thì số lớn gồm 3 phần như thế.",
            "Tổng số phần bằng nhau là:",
            "2 + 3 = 5 (phần)",
            "Số bé là:",
            "40 : 5 × 2 = 16",
            "Số lớn là:",
            "40 − 16 = 24",
            "Thử lại: 16 + 24 = 40 và 16 : 24 = 2 : 3.",
        ],
        "Số bé: 16; số lớn: 24.",
    ),
    (
        [
            "Coi số bé gồm 4 phần bằng nhau thì số lớn gồm 5 phần như thế.",
            "Tổng số phần bằng nhau là:",
            "4 + 5 = 9 (phần)",
            "Số bé là:",
            "72 : 9 × 4 = 32",
            "Số lớn là:",
            "72 − 32 = 40",
        ],
        "Số bé: 32; số lớn: 40.",
    ),
    (
        [
            "Coi số bé gồm 3 phần bằng nhau thì số lớn gồm 4 phần như thế.",
            "Tổng số phần bằng nhau là:",
            "3 + 4 = 7 (phần)",
            "Số bé là:",
            "84 : 7 × 3 = 36",
            "Số lớn là:",
            "84 − 36 = 48",
        ],
        "Số bé: 36; số lớn: 48.",
    ),
)
worked(
    "difference_ratio",
    (
        [
            "Coi số bé gồm 2 phần bằng nhau thì số lớn gồm 5 phần như thế.",
            "Hiệu số phần bằng nhau là:",
            "5 − 2 = 3 (phần)",
            "Số bé là:",
            "18 : 3 × 2 = 12",
            "Số lớn là:",
            "12 + 18 = 30",
            "Thử lại: 30 − 12 = 18 và 12 : 30 = 2 : 5.",
        ],
        "Số bé: 12; số lớn: 30.",
    ),
    (
        [
            "Coi số bé gồm 3 phần bằng nhau thì số lớn gồm 7 phần như thế.",
            "Hiệu số phần bằng nhau là:",
            "7 − 3 = 4 (phần)",
            "Số bé là:",
            "24 : 4 × 3 = 18",
            "Số lớn là:",
            "18 + 24 = 42",
        ],
        "Số bé: 18; số lớn: 42.",
    ),
    (
        [
            "Coi số bé gồm 4 phần bằng nhau thì số lớn gồm 5 phần như thế.",
            "Hiệu số phần bằng nhau là:",
            "5 − 4 = 1 (phần)",
            "Số bé là:",
            "15 : 1 × 4 = 60",
            "Số lớn là:",
            "60 + 15 = 75",
        ],
        "Số bé: 60; số lớn: 75.",
    ),
)
worked(
    "percentage_value",
    (["15% của 240 là:", "240 : 100 × 15 = 36."], "36."),
    (["25% của 360 là:", "360 : 100 × 25 = 90."], "90."),
    (
        [
            "Số tiền được giảm là:",
            "200 000 : 100 × 10 = 20 000 (đồng)",
            "Giá sản phẩm sau khi giảm là:",
            "200 000 − 20 000 = 180 000 (đồng)",
        ],
        "180 000 đồng.",
    ),
)
worked(
    "calculator",
    (
        [
            "Ước lượng: 12,5 gần 13 nên tích gần 13 × 8 = 104.",
            "Trên máy dùng dấu chấm thập phân, bấm lần lượt: 1, 2, dấu chấm, 5, ×, 8, =.",
            "Màn hình hiển thị 100; kết quả gần với ước lượng.",
            "Vậy 12,5 × 8 = 100.",
        ],
        "100.",
    ),
    (
        [
            "Bấm các phím: 1, 2, 5, ×, 2, 4, =. Màn hình hiển thị 3000.",
            "Kiểm tra: 125 × 24 = 125 × (20 + 4) = 2 500 + 500 = 3 000.",
        ],
        "3 000.",
    ),
    (
        [
            "18% của 250 được tính bằng: 250 : 100 × 18.",
            "Bấm các phím: 2, 5, 0, ÷, 1, 0, 0, ×, 1, 8, =. Màn hình hiển thị 45.",
            "Vậy 18% của 250 là 45.",
        ],
        "45.",
    ),
)
worked(
    "volume",
    (
        [
            "Số khối lập phương đơn vị trong một lớp là:",
            "3 × 4 = 12 (khối)",
            "Số khối lập phương đơn vị trong hai lớp là:",
            "12 × 2 = 24 (khối)",
            "Mỗi khối lập phương đơn vị có thể tích 1 đơn vị khối nên thể tích hình đã cho là 24 đơn vị khối.",
        ],
        "24 đơn vị khối.",
    ),
    (
        [
            "Số khối lập phương đơn vị trong một lớp là:",
            "5 × 3 = 15 (khối)",
            "Số khối lập phương đơn vị trong hai lớp là:",
            "15 × 2 = 30 (khối)",
        ],
        "30 khối lập phương đơn vị.",
    ),
    (
        [
            "Hai hình được xếp từ các khối lập phương đơn vị giống nhau.",
            "Vì 25 > 18 nên hình có 25 khối có thể tích lớn hơn.",
            "Thể tích chênh lệch là:",
            "25 − 18 = 7 (đơn vị khối)",
        ],
        "Hình gồm 25 khối lớn hơn 7 đơn vị khối.",
    ),
)
worked(
    "volume_units",
    (
        ["Vì 1 dm³ = 1 000 cm³ nên:", "2,5 dm³ = 2,5 × 1 000 cm³ = 2 500 cm³."],
        "2 500 cm³.",
    ),
    (
        ["Vì 1 000 cm³ = 1 dm³ nên:", "3 200 cm³ = 3 200 : 1 000 dm³ = 3,2 dm³."],
        "3,2 dm³.",
    ),
    (["Vì 1 m³ = 1 000 dm³ nên:", "0,4 m³ = 0,4 × 1 000 dm³ = 400 dm³."], "400 dm³."),
)
worked(
    "nets",
    (
        [
            "Hình hộp chữ nhật có 6 mặt, gồm 3 cặp mặt đối diện bằng nhau.",
            "Hai mặt có kích thước 6 cm và 4 cm; hai mặt có kích thước 6 cm và 3 cm; hai mặt có kích thước 4 cm và 3 cm.",
            "Khi làm mô hình, ghép các cạnh có cùng độ dài và kiểm tra các mặt không chồng lên nhau.",
        ],
        "Ba cặp mặt: 6 cm × 4 cm; 6 cm × 3 cm; 4 cm × 3 cm.",
    ),
    (
        [
            "Hình lập phương có 6 mặt và mỗi mặt là một hình vuông bằng nhau.",
            "Vì vậy hình khai triển cần đủ 6 hình vuông bằng nhau.",
            "Cần kiểm tra cách ghép: không phải mọi cách xếp 6 hình vuông đều gấp được thành hình lập phương.",
        ],
        "6 mặt vuông bằng nhau, ghép đúng vị trí.",
    ),
    (
        [
            "Hình trụ có hai mặt đáy là hai hình tròn bằng nhau.",
            "Cắt mặt xung quanh theo một đường thẳng song song với trục rồi trải phẳng, ta được một hình chữ nhật.",
        ],
        "Mặt xung quanh trải phẳng là hình chữ nhật.",
    ),
)
worked(
    "box_area",
    (
        [
            "Chu vi mặt đáy là:",
            "(6 + 4) × 2 = 20 (cm)",
            "Diện tích xung quanh hình hộp chữ nhật là:",
            "20 × 3 = 60 (cm²)",
            "Diện tích hai mặt đáy là:",
            "6 × 4 × 2 = 48 (cm²)",
            "Diện tích toàn phần hình hộp chữ nhật là:",
            "60 + 48 = 108 (cm²)",
        ],
        "Diện tích xung quanh: 60 cm²; diện tích toàn phần: 108 cm².",
    ),
    (
        [
            "Chu vi mặt đáy là:",
            "(5 + 3) × 2 = 16 (cm)",
            "Diện tích xung quanh hình hộp chữ nhật là:",
            "16 × 4 = 64 (cm²)",
        ],
        "64 cm².",
    ),
    (
        [
            "Diện tích xung quanh hình hộp chữ nhật là:",
            "(5 + 3) × 2 × 4 = 64 (cm²)",
            "Diện tích hai mặt đáy là:",
            "5 × 3 × 2 = 30 (cm²)",
            "Diện tích toàn phần hình hộp chữ nhật là:",
            "64 + 30 = 94 (cm²)",
        ],
        "94 cm².",
    ),
)
worked(
    "cube_area",
    (
        [
            "Diện tích một mặt hình lập phương là:",
            "3 × 3 = 9 (cm²)",
            "Diện tích xung quanh hình lập phương là:",
            "9 × 4 = 36 (cm²)",
            "Diện tích toàn phần hình lập phương là:",
            "9 × 6 = 54 (cm²)",
        ],
        "Diện tích xung quanh: 36 cm²; diện tích toàn phần: 54 cm².",
    ),
    (
        [
            "Diện tích một mặt hình lập phương là:",
            "4 × 4 = 16 (cm²)",
            "Diện tích xung quanh hình lập phương là:",
            "16 × 4 = 64 (cm²)",
        ],
        "64 cm².",
    ),
    (
        [
            "Diện tích một mặt hình lập phương là:",
            "5 × 5 = 25 (cm²)",
            "Diện tích toàn phần hình lập phương là:",
            "25 × 6 = 150 (cm²)",
        ],
        "150 cm².",
    ),
)
worked(
    "box_volume",
    (["Thể tích hình hộp chữ nhật là:", "8 × 5 × 3 = 120 (cm³)"], "120 cm³."),
    (["Thể tích hình hộp chữ nhật là:", "6 × 4 × 2 = 48 (cm³)"], "48 cm³."),
    (
        [
            "Diện tích mặt đáy là:",
            "6 × 5 = 30 (cm²)",
            "Chiều cao hình hộp chữ nhật là:",
            "180 : 30 = 6 (cm)",
        ],
        "6 cm.",
    ),
)
worked(
    "cube_volume",
    (["Thể tích hình lập phương là:", "4 × 4 × 4 = 64 (cm³)"], "64 cm³."),
    (["Thể tích hình lập phương là:", "3 × 3 × 3 = 27 (cm³)"], "27 cm³."),
    (["Thể tích hình lập phương là:", "5 × 5 × 5 = 125 (cm³)"], "125 cm³."),
)
worked(
    "time_units",
    (
        [
            "Hai giờ bằng số phút là:",
            "2 × 60 = 120 (phút)",
            "Hai giờ mười lăm phút bằng số phút là:",
            "120 + 15 = 135 (phút)",
        ],
        "135 phút.",
    ),
    (
        [
            "Chia 150 cho 60 để tìm số giờ:",
            "150 : 60 = 2 (dư 30).",
            "Vậy 150 phút = 2 giờ 30 phút.",
        ],
        "2 giờ 30 phút.",
    ),
    (["Một phẩy năm giờ bằng số phút là:", "1,5 × 60 = 90 (phút)"], "90 phút."),
)
worked(
    "time_add",
    (
        [
            "Vì 10 phút không trừ được 45 phút nên đổi 1 giờ thành 60 phút:",
            "3 giờ 10 phút = 2 giờ 70 phút.",
            "Trừ theo từng đơn vị:",
            "2 giờ 70 phút − 1 giờ 45 phút = 1 giờ 25 phút.",
        ],
        "1 giờ 25 phút.",
    ),
    (
        [
            "Cộng theo từng đơn vị:",
            "1 giờ 40 phút + 2 giờ 35 phút = 3 giờ 75 phút.",
            "Vì 75 phút = 1 giờ 15 phút nên 3 giờ 75 phút = 4 giờ 15 phút.",
        ],
        "4 giờ 15 phút.",
    ),
    (
        [
            "Đổi: 5 giờ 20 phút = 4 giờ 80 phút.",
            "Trừ theo từng đơn vị:",
            "4 giờ 80 phút − 2 giờ 50 phút = 2 giờ 30 phút.",
        ],
        "2 giờ 30 phút.",
    ),
)
worked(
    "time_multiply",
    (
        [
            "Đổi: 1 giờ 20 phút = 80 phút.",
            "Nhân số đo thời gian với 3:",
            "80 phút × 3 = 240 phút.",
            "Đổi: 240 phút = 4 giờ.",
        ],
        "4 giờ.",
    ),
    (
        [
            "Đổi: 2 giờ 15 phút = 135 phút.",
            "Nhân số đo thời gian với 2:",
            "135 phút × 2 = 270 phút.",
            "Đổi: 270 phút = 4 giờ 30 phút.",
        ],
        "4 giờ 30 phút.",
    ),
    (
        [
            "Đổi: 3 giờ 30 phút = 210 phút.",
            "Chia số đo thời gian cho 2:",
            "210 phút : 2 = 105 phút.",
            "Đổi: 105 phút = 1 giờ 45 phút.",
        ],
        "1 giờ 45 phút.",
    ),
)
worked(
    "speed",
    (["Vận tốc của xe là:", "90 : 1,5 = 60 (km/giờ)"], "60 km/giờ."),
    (["Quãng đường đi được là:", "40 × 2,5 = 100 (km)"], "100 km."),
    (["Thời gian đi hết quãng đường là:", "120 : 60 = 2 (giờ)"], "2 giờ."),
)
worked(
    "data",
    (
        [
            "Đếm từng kết quả theo màu, kể cả những lần cùng màu xuất hiện lại.",
            "Màu đỏ: 3 lần; màu xanh: 2 lần; màu vàng: 1 lần.",
            "Kiểm tra tổng số kết quả: 3 + 2 + 1 = 6.",
        ],
        "Đỏ: 3; xanh: 2; vàng: 1; tổng: 6 kết quả.",
    ),
    (
        [
            "Trong dãy số 2, 3, 2, 4, 3, 2, số 2 xuất hiện ở vị trí thứ nhất, thứ ba và thứ sáu.",
            "Đếm được 3 lần xuất hiện.",
        ],
        "3 lần.",
    ),
    (
        [
            "Đếm số lần xuất hiện của từng giá trị trong dãy số:",
            "Giá trị 2: 3 lần; giá trị 3: 2 lần; giá trị 4: 1 lần.",
            "Kiểm tra: 3 + 2 + 1 = 6, đúng bằng số kết quả đã cho.",
        ],
        "Bảng đếm: 2 → 3 lần; 3 → 2 lần; 4 → 1 lần.",
    ),
)
worked(
    "pie",
    (["Số bạn thích đọc sách là:", "40 : 100 × 25 = 10 (bạn)"], "10 bạn."),
    (["Số bạn trong nhóm là:", "50 : 100 × 30 = 15 (bạn)"], "15 bạn."),
    (
        [
            "Tỉ lệ phần trăm của hai nhóm đã biết là:",
            "20% + 35% = 55%.",
            "Tỉ lệ phần trăm của nhóm còn lại là:",
            "100% − 55% = 45%.",
        ],
        "45%.",
    ),
)
worked(
    "frequency",
    (
        [
            "Tỉ số của số lần xuất hiện màu đỏ và tổng số lần thử là:",
            "8/20 = (8 : 4)/(20 : 4) = 2/5.",
            "Ta có: 2/5 = 40/100 = 40%.",
        ],
        "2/5, hay 40%.",
    ),
    (
        [
            "Tỉ số của số lần xuất hiện sự kiện A và tổng số lần thử là:",
            "9/30 = (9 : 3)/(30 : 3) = 3/10.",
            "Ta có: 3/10 = 30/100 = 30%.",
        ],
        "3/10, hay 30%.",
    ),
    (
        [
            "Tổng số lần tung đồng xu là:",
            "12 + 8 = 20 (lần)",
            "Tỉ số của số lần xuất hiện mặt ngửa và tổng số lần tung là:",
            "8/20 = 2/5 = 40/100 = 40%.",
        ],
        "2/5, hay 40%.",
    ),
)

# Wording and notation suited to the grade: rules in words before letter formulas.
RULES = {
    "decimal_fraction": "Phân số thập phân là phân số có mẫu số là 10; 100; 1 000; ... Muốn viết một phân số thành phân số thập phân, có thể nhân hoặc chia cả tử số và mẫu số với cùng một số tự nhiên khác 0 để được mẫu số thích hợp.",
    "divide_decimal": "Muốn chia một số thập phân cho một số thập phân, chuyển dấu phẩy của cả số bị chia và số chia sang phải cùng một số chữ số để số chia trở thành số tự nhiên, rồi thực hiện phép chia. Số chia phải khác 0.",
    "plane": "Chu vi hình chữ nhật = (chiều dài + chiều rộng) × 2. Diện tích hình chữ nhật = chiều dài × chiều rộng. Chu vi hình vuông = độ dài cạnh × 4. Diện tích hình vuông = độ dài cạnh × độ dài cạnh. Các độ dài phải cùng đơn vị; diện tích ghi bằng đơn vị vuông.",
    "circle": "Trong một hình tròn, đường kính dài gấp hai lần bán kính.\nMuốn tính chu vi hình tròn, lấy độ dài đường kính nhân với số 3,14; hoặc lấy bán kính nhân với 2 rồi nhân với số 3,14.\nMuốn tính diện tích hình tròn, lấy bán kính nhân với bán kính rồi nhân với số 3,14.\nCông thức: d = r × 2; C = d × 3,14 = r × 2 × 3,14; S = r × r × 3,14 (r là bán kính, d là đường kính, C là chu vi, S là diện tích). Đây là cách tính gần đúng dùng trong các bài tập này.",
    "triangle": "Muốn tính diện tích hình tam giác, lấy độ dài đáy nhân với chiều cao tương ứng (cùng một đơn vị đo) rồi chia cho 2. Công thức: S = a × h : 2 (S là diện tích, a là độ dài đáy, h là chiều cao tương ứng).",
    "trapezoid": "Muốn tính diện tích hình thang, lấy tổng độ dài hai đáy nhân với chiều cao (cùng một đơn vị đo) rồi chia cho 2. Công thức: S = (a + b) × h : 2 (a, b là độ dài hai đáy; h là chiều cao).",
    "ratio": "Tỉ số của a và b viết là a/b hoặc a : b (b khác 0). Muốn tìm tỉ số phần trăm của hai số, tìm thương của chúng, nhân thương đó với 100 rồi viết thêm kí hiệu % vào bên phải số tìm được.",
    "sum_ratio": "Khi biết tổng và tỉ số của hai số, biểu diễn hai số bằng các phần bằng nhau. Tổng số phần bằng nhau bằng số phần của số bé cộng số phần của số lớn. Lấy tổng hai số chia cho tổng số phần để tìm giá trị một phần, rồi tìm mỗi số.",
    "difference_ratio": "Khi biết hiệu và tỉ số của hai số, biểu diễn hai số bằng các phần bằng nhau. Lấy số phần của số lớn trừ số phần của số bé để tìm hiệu số phần. Lấy hiệu hai số chia cho hiệu số phần để tìm giá trị một phần, rồi tìm mỗi số.",
    "percentage_value": "Muốn tìm p% của một số, có thể lấy số đó chia cho 100 rồi nhân với p; hoặc lấy số đó nhân với p rồi chia cho 100.",
    "cube_area": "Muốn tính diện tích xung quanh hình lập phương, lấy diện tích một mặt nhân với 4. Muốn tính diện tích toàn phần hình lập phương, lấy diện tích một mặt nhân với 6. Diện tích một mặt bằng độ dài cạnh nhân với chính nó.",
    "box_area": "Muốn tính diện tích xung quanh hình hộp chữ nhật, lấy chu vi mặt đáy nhân với chiều cao (cùng một đơn vị đo). Diện tích toàn phần bằng diện tích xung quanh cộng diện tích hai mặt đáy.",
    "speed": "Trong chuyển động đều: vận tốc = quãng đường : thời gian; quãng đường = vận tốc × thời gian; thời gian = quãng đường : vận tốc. Thời gian dùng để tính vận tốc phải lớn hơn 0; vận tốc dùng để tính thời gian phải lớn hơn 0. Nếu vận tốc tính bằng km/giờ thì quãng đường tính bằng km và thời gian tính bằng giờ.",
    "frequency": "Tỉ số của số lần xuất hiện một sự kiện và tổng số lần thử bằng số lần xuất hiện sự kiện đó chia cho tổng số lần thử. Tổng số lần thử phải lớn hơn 0. Có thể viết kết quả dưới dạng phân số và rút gọn.",
}
METHODS = {
    "natural": "1. Xác định từng hàng từ phải sang trái: đơn vị, chục, trăm, nghìn, ...\n2. Giá trị chữ số bằng chữ số nhân với giá trị của hàng.\n3. Khi so sánh, so từ hàng cao nhất; sắp xếp theo yêu cầu và kiểm tra lại.",
    "operations": "1. Tính trong ngoặc trước.\n2. Với biểu thức không có ngoặc, tính nhân và chia trước, cộng và trừ sau.\n3. Các phép tính cùng mức ưu tiên thực hiện từ trái sang phải; mỗi bước viết một dòng.",
    "fraction": "1. Tìm số tự nhiên lớn hơn 1 mà cả tử và mẫu cùng chia hết.\n2. Chia cả tử và mẫu cho số đó; tiếp tục đến khi được phân số tối giản.\n3. Khi so sánh phân số khác mẫu, quy đồng rồi so sánh các tử số.",
    "decimal_fraction": "1. Xem mẫu số có thể nhân hoặc chia với số nào để được 10; 100; 1 000; ...\n2. Làm cùng phép tính đó ở tử số.\n3. Kiểm tra phân số mới bằng phân số ban đầu.",
    "fraction_ops": "1. Cộng, trừ: quy đồng nếu cần, tính với tử số và giữ mẫu chung.\n2. Nhân: nhân tử với tử, mẫu với mẫu.\n3. Chia: nhân phân số thứ nhất với phân số đảo ngược của phân số thứ hai khác 0. Rút gọn kết quả.",
    "unlike_fraction": "1. Chọn mẫu số chung và quy đồng.\n2. Cộng hoặc trừ các tử số, giữ nguyên mẫu số chung.\n3. Rút gọn kết quả nếu có thể.",
    "mixed": "1. Đổi hỗn số thành phân số: lấy phần nguyên nhân với mẫu rồi cộng tử; giữ mẫu.\n2. Đổi phân số lớn hơn 1 thành hỗn số: chia tử cho mẫu; thương là phần nguyên, số dư là tử của phần phân số.\n3. Giữ mẫu số và kiểm tra lại.",
    "plane": "1. Nhận dạng hình và đổi các độ dài về cùng đơn vị.\n2. Nêu rõ cần tìm chu vi hay diện tích rồi chọn quy tắc.\n3. Viết câu lời giải, phép tính kèm đơn vị và đáp số.",
    "decimal": "1. Tách phần nguyên và phần thập phân.\n2. Xác định hàng phần mười, phần trăm, phần nghìn, ...\n3. Viết theo yêu cầu; giữ chữ số 0 ở những hàng cần thiết.",
    "compare_decimal": "1. So sánh phần nguyên.\n2. Nếu phần nguyên bằng nhau, so lần lượt hàng phần mười, phần trăm, ...\n3. Kết luận ở hàng đầu tiên khác nhau; có thể thêm số 0 vào tận cùng bên phải phần thập phân.",
    "measure_decimal": "1. Viết quan hệ giữa các đơn vị.\n2. Đổi phần số đo ở đơn vị bé sang đơn vị cần tìm.\n3. Cộng với phần số đo ở đơn vị lớn; ghi đơn vị kết quả.",
    "round": "1. Xác định hàng cần làm tròn.\n2. Xét chữ số ngay bên phải: bé hơn 5 thì giữ nguyên; từ 5 trở lên thì tăng chữ số ở hàng làm tròn thêm 1.\n3. Bỏ phần thập phân phía sau hàng làm tròn; với phần nguyên, thay các chữ số phía sau bằng 0.",
    "land_area": "1. Chọn đơn vị cần đổi và viết quan hệ: 1 ha = 10 000 m²; 1 km² = 100 ha.\n2. Nhân hoặc chia với hệ số tương ứng.\n3. Ghi đủ đơn vị và kiểm tra chiều đổi.",
    "area_units": "1. Xác định hai đơn vị trong bảng km², hm², dam², m², dm², cm², mm².\n2. Hai đơn vị liền nhau hơn kém 100 lần: đổi sang đơn vị bé thì nhân, sang đơn vị lớn thì chia.\n3. Nếu qua nhiều bậc, thực hiện đủ từng bậc và ghi đơn vị.",
    "add_decimal": "1. Đặt tính sao cho các chữ số cùng hàng thẳng cột, các dấu phẩy thẳng cột; có thể viết thêm 0 ở tận cùng bên phải phần thập phân.\n2. Cộng như cộng số tự nhiên từ phải sang trái, nhớ sang hàng kế tiếp khi cần.\n3. Viết dấu phẩy ở tổng thẳng cột với các dấu phẩy của hai số hạng.",
    "subtract_decimal": "1. Đặt tính theo từng hàng, các dấu phẩy thẳng cột; thêm 0 ở tận cùng bên phải phần thập phân nếu cần.\n2. Trừ như trừ số tự nhiên từ phải sang trái; đổi một đơn vị ở hàng bên trái khi cần.\n3. Viết dấu phẩy ở hiệu thẳng cột với các dấu phẩy đã cho; thử lại bằng phép cộng.",
    "multiply_decimal": "1. Nhân như nhân các số tự nhiên.\n2. Đếm tổng số chữ số ở phần thập phân của hai thừa số.\n3. Dùng dấu phẩy tách ở tích bấy nhiêu chữ số kể từ phải sang trái; thêm 0 khi cần.",
    "divide_decimal": "1. Xác định số chữ số ở phần thập phân của số chia.\n2. Chuyển dấu phẩy của cả hai số sang phải cùng số chữ số đó.\n3. Chia cho số tự nhiên vừa nhận được; nếu số bị chia còn phần thập phân, viết dấu phẩy ở thương khi bắt đầu chia phần thập phân. Thử lại bằng phép nhân.",
    "powers_ten": "1. Xác định phép nhân hay chia và hệ số.\n2. Nhân 10; 100; ... thì chuyển dấu phẩy sang phải, chia thì chuyển sang trái. Nhân 0,1; 0,01; ... thì làm ngược lại; chia cho các số này thì chuyển sang phải.\n3. Chuyển đúng số chữ số; viết thêm 0 khi cần.",
    "triangle": "1. Xác định đáy và chiều cao vuông góc tương ứng; đổi cùng đơn vị.\n2. Tính đáy × chiều cao : 2. Nếu tìm chiều cao, lấy diện tích × 2 : độ dài đáy.\n3. Viết câu lời giải, phép tính và đáp số có đơn vị.",
    "trapezoid": "1. Xác định hai đáy song song và chiều cao vuông góc với hai đáy; đổi cùng đơn vị.\n2. Tính (đáy lớn + đáy bé) × chiều cao : 2. Nếu tìm chiều cao, lấy diện tích × 2 : tổng hai đáy.\n3. Ghi đúng đơn vị của đại lượng cần tìm.",
    "circle": "1. Xác định đề cho bán kính hay đường kính. Nếu cần bán kính mà đề cho đường kính, lấy đường kính chia cho 2.\n2. Tính chu vi hoặc diện tích theo quy tắc với số 3,14.\n3. Chu vi ghi đơn vị độ dài; diện tích ghi đơn vị vuông. Viết đáp số riêng ở cuối bài.",
    "drawing": "1. Chuẩn bị thước, ê-ke hoặc compa; xác định độ dài và góc cần vẽ.\n2. Vẽ lần lượt các cạnh, các điểm và nối hình theo yêu cầu.\n3. Đo, kiểm tra lại; nếu có tính diện tích thì viết lời giải và đáp số.",
    "ratio": "1. Xác định số được so sánh và số làm chuẩn; đổi về cùng đơn vị.\n2. Lập tỉ số theo đúng thứ tự.\n3. Nếu tìm tỉ số phần trăm, tính thương, nhân với 100 rồi ghi kí hiệu %. Không đổi thứ tự hai số.",
    "map": "1. Đọc tỉ lệ bản đồ và đổi về cùng đơn vị.\n2. Với tỉ lệ 1 : n, độ dài thực tế = độ dài trên bản đồ × n; độ dài trên bản đồ = độ dài thực tế : n.\n3. Đổi kết quả sang đơn vị đề yêu cầu; ghi đáp số.",
    "sum_ratio": "1. Biểu diễn số phần của mỗi số theo tỉ số đã cho.\n2. Tìm tổng số phần bằng nhau.\n3. Lấy tổng hai số chia cho tổng số phần, rồi nhân số phần của từng số. Kiểm tra cả tổng và tỉ số.",
    "difference_ratio": "1. Biểu diễn số phần của mỗi số theo tỉ số đã cho.\n2. Tìm hiệu số phần bằng nhau.\n3. Lấy hiệu hai số chia cho hiệu số phần, rồi nhân số phần của từng số. Kiểm tra cả hiệu và tỉ số.",
    "percentage_value": "1. Xác định số ban đầu và tỉ lệ phần trăm cần tìm.\n2. Lấy số ban đầu chia cho 100 rồi nhân với số chỉ phần trăm.\n3. Nếu đề hỏi giá sau giảm, lấy giá ban đầu trừ số tiền giảm; nếu tăng thêm thì cộng. Ghi đáp số đúng đại lượng.",
    "calculator": "1. Ước lượng để biết khoảng kết quả hợp lí.\n2. Nhập số và phép tính theo đúng thứ tự; dấu chấm trên máy có thể tương ứng dấu phẩy thập phân.\n3. Đọc màn hình, ghi kết quả theo cách viết tiếng Việt và kiểm tra lại.",
    "volume": "1. Chọn các khối lập phương đơn vị cùng kích thước.\n2. Đếm số khối trong mỗi lớp rồi tính số khối của tất cả các lớp.\n3. Nêu số đơn vị khối; khi so sánh phải dùng cùng khối đơn vị.",
    "volume_units": "1. Viết quan hệ 1 dm³ = 1 000 cm³; 1 m³ = 1 000 dm³.\n2. Đổi qua mỗi bậc bằng cách nhân hoặc chia cho 1 000.\n3. Kiểm tra kết quả và đơn vị khối.",
    "nets": "1. Xác định số mặt và hình dạng của từng mặt.\n2. Ghép các cạnh tương ứng có cùng độ dài.\n3. Thử gấp mô hình giấy, kiểm tra các mặt không chồng lấn; thao tác với kéo theo hướng dẫn an toàn.",
    "box_area": "1. Xác định chiều dài, chiều rộng mặt đáy và chiều cao; đổi cùng đơn vị.\n2. Tính chu vi đáy rồi nhân chiều cao để được diện tích xung quanh.\n3. Nếu tính diện tích toàn phần của hộp kín, cộng thêm diện tích hai đáy; ghi đơn vị vuông.",
    "cube_area": "1. Tính diện tích một mặt: cạnh × cạnh.\n2. Nhân với 4 để tính diện tích xung quanh, hoặc với 6 để tính diện tích toàn phần.\n3. Viết câu lời giải và đáp số có đơn vị vuông.",
    "box_volume": "1. Đổi chiều dài, chiều rộng, chiều cao về cùng đơn vị.\n2. Lấy chiều dài × chiều rộng × chiều cao. Nếu tìm chiều cao, lấy thể tích chia cho diện tích đáy.\n3. Ghi đúng đơn vị: thể tích là đơn vị khối, chiều cao là đơn vị độ dài.",
    "cube_volume": "1. Xác định độ dài cạnh và đơn vị.\n2. Lấy cạnh × cạnh × cạnh.\n3. Ghi câu lời giải, phép tính kèm đơn vị khối và đáp số.",
    "time_units": "1. Nhớ 1 giờ = 60 phút; 1 phút = 60 giây.\n2. Đổi sang đơn vị bé thì nhân với 60; đổi sang đơn vị lớn thì chia cho 60 và giữ phần dư ở đơn vị bé nếu cần.\n3. Kiểm tra phần thập phân của giờ, không coi một giờ bằng 100 phút.",
    "time_add": "1. Đặt các số đo cùng đơn vị tương ứng với nhau.\n2. Cộng hoặc trừ từng đơn vị; khi không đủ phút để trừ, đổi một giờ thành 60 phút.\n3. Đổi 60 phút thành một giờ nếu cần; ghi kết quả và đáp số.",
    "time_multiply": "1. Có thể đổi số đo thời gian về phút hoặc giây.\n2. Thực hiện phép nhân hoặc chia.\n3. Đổi về giờ, phút hoặc giây theo yêu cầu; ghi đáp số.",
    "speed": "1. Xác định đại lượng cần tìm: vận tốc, quãng đường hay thời gian.\n2. Đổi đơn vị phù hợp, chẳng hạn 1 giờ 30 phút = 1,5 giờ khi vận tốc tính bằng km/giờ.\n3. Viết câu lời giải, áp dụng quy tắc tương ứng và ghi đáp số có đơn vị.",
    "data": "1. Đọc toàn bộ số liệu và xác định cách phân loại.\n2. Đếm mỗi quan sát đúng một lần, kể cả khi giá trị lặp lại.\n3. Lập bảng đếm và cộng các số lần để kiểm tra tổng.",
    "pie": "1. Đọc tên nhóm, chú giải và tỉ lệ phần trăm.\n2. Nếu tìm số lượng, lấy tổng chia cho 100 rồi nhân số chỉ phần trăm; nếu tìm phần còn lại, lấy 100% trừ các phần đã biết.\n3. Ghi đúng đơn vị và kiểm tra tổng các tỉ lệ bằng 100%.",
    "frequency": "1. Đếm số lần xuất hiện sự kiện và tổng số lần thử.\n2. Viết tỉ số theo đúng thứ tự rồi rút gọn.\n3. Có thể đổi sang phần trăm; đây là số liệu ghi nhận, không bảo đảm kết quả của lần thử tiếp theo.",
}
EXAMPLES = {
    "circle": "Một hình tròn có bán kính 3 cm. Tính đường kính, chu vi và diện tích hình tròn đó (dùng số 3,14).",
    "triangle": "Một hình tam giác có đáy dài 8 cm và chiều cao tương ứng 5 cm. Tính diện tích hình tam giác.",
    "trapezoid": "Một hình thang có hai đáy dài 10 cm và 6 cm, chiều cao 4 cm. Tính diện tích hình thang.",
    "ratio": "Một lớp có 30 học sinh, trong đó có 12 bạn nữ. Tìm tỉ số và tỉ số phần trăm của số bạn nữ và số học sinh cả lớp.",
    "map": "Trên bản đồ tỉ lệ 1 : 100 000, một đoạn thẳng dài 3 cm. Tính khoảng cách thực tế tương ứng theo ki-lô-mét.",
    "sum_ratio": "Tổng hai số là 40. Tỉ số của số bé và số lớn là 2 : 3. Tìm hai số đó.",
    "difference_ratio": "Hiệu của số lớn và số bé là 18. Tỉ số của số bé và số lớn là 2 : 5. Tìm hai số đó.",
    "volume": "Một hình được xếp từ các khối lập phương đơn vị bằng nhau thành 2 lớp. Mỗi lớp có 3 hàng, mỗi hàng có 4 khối. Tính thể tích hình đó theo đơn vị khối.",
    "nets": "Một hình hộp chữ nhật có chiều dài 6 cm, chiều rộng 4 cm, chiều cao 3 cm. Nêu số mặt và kích thước của các cặp mặt đối diện.",
    "box_area": "Một hình hộp chữ nhật có chiều dài 6 cm, chiều rộng 4 cm, chiều cao 3 cm. Tính diện tích xung quanh và diện tích toàn phần.",
    "cube_area": "Một hình lập phương có cạnh 3 cm. Tính diện tích xung quanh và diện tích toàn phần.",
    "box_volume": "Một hình hộp chữ nhật có chiều dài 8 cm, chiều rộng 5 cm, chiều cao 3 cm. Tính thể tích hình đó.",
    "cube_volume": "Một hình lập phương có cạnh 4 cm. Tính thể tích hình đó.",
    "speed": "Một ô tô chuyển động đều đi được 90 km trong 1,5 giờ. Tính vận tốc của ô tô.",
    "data": "Có 6 kết quả ghi màu theo thứ tự: đỏ, xanh, đỏ, vàng, xanh, đỏ. Lập bảng đếm số lần xuất hiện từng màu và kiểm tra tổng.",
    "pie": "Biểu đồ hình quạt tròn về sở thích của 40 bạn cho biết nhóm thích đọc sách chiếm 25%. Hỏi có bao nhiêu bạn thích đọc sách?",
    "frequency": "Trong 20 lần thử có 8 lần xuất hiện màu đỏ. Tìm tỉ số của số lần xuất hiện màu đỏ và tổng số lần thử; viết dưới dạng phân số tối giản và phần trăm.",
}
TASKS = {
    "circle": [
        "Một hình tròn có bán kính 5 cm. Tính chu vi hình tròn (dùng số 3,14).",
        "Một hình tròn có đường kính 4 cm. Tính diện tích hình tròn (dùng số 3,14).",
    ],
    "drawing": [
        "Vẽ một tam giác có đáy 8 cm và chiều cao tương ứng 3 cm, rồi tính diện tích.",
        "Cắt một hình chữ nhật theo đường chéo thành hai tam giác vuông bằng nhau, rồi ghép lại. So sánh diện tích hình chữ nhật sau ghép với tổng diện tích hai tam giác trước ghép.",
    ],
    "sum_ratio": [
        "Tổng hai số là 72. Tỉ số của số bé và số lớn là 4 : 5. Tìm hai số.",
        "Tổng hai số là 84. Tỉ số của số bé và số lớn là 3 : 4. Tìm hai số.",
    ],
    "difference_ratio": [
        "Hiệu của số lớn và số bé là 24. Tỉ số của số bé và số lớn là 3 : 7. Tìm hai số.",
        "Hiệu của số lớn và số bé là 15. Tỉ số của số bé và số lớn là 4 : 5. Tìm hai số.",
    ],
    "box_area": [
        "Một hình hộp chữ nhật có chiều dài 5 cm, chiều rộng 3 cm, chiều cao 4 cm. Tính diện tích xung quanh.",
        "Một hình hộp chữ nhật có chiều dài 5 cm, chiều rộng 3 cm, chiều cao 4 cm. Tính diện tích toàn phần.",
    ],
    "speed": [
        "Một xe chuyển động đều với vận tốc 40 km/giờ trong 2,5 giờ. Tính quãng đường xe đi được.",
        "Một xe chuyển động đều đi quãng đường 120 km với vận tốc 60 km/giờ. Tính thời gian xe đi hết quãng đường đó.",
    ],
    "data": [
        "Trong dãy số 2, 3, 2, 4, 3, 2, giá trị 2 xuất hiện mấy lần?",
        "Lập bảng đếm số lần xuất hiện của mỗi giá trị trong dãy số 2, 3, 2, 4, 3, 2 và kiểm tra tổng.",
    ],
}
MISTAKES = {
    "circle": "Không dùng đường kính thay cho bán kính khi tính diện tích. Nếu đề cho đường kính, phải chia cho 2 để tìm bán kính trước. Chu vi và diện tích dùng hai loại đơn vị khác nhau.",
    "cube_area": "Không nhầm diện tích với thể tích. Diện tích dùng đơn vị vuông; thể tích dùng đơn vị khối.",
}
