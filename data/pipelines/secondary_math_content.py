"""Original worked teaching material for explicitly mapped secondary Math units."""

from math5_worked_solutions import solution
from primary_math_content import resolve as primary
from build_math5_lessons import SKILLS as MATH5
from math5_worked_solutions import WORKED, RULES, METHODS, EXAMPLES, TASKS, MISTAKES

CONTENT = {}


def add(
    key,
    rule,
    method,
    examples,
    mistake="Kiểm tra điều kiện áp dụng, thứ tự tính và kết luận theo đúng câu hỏi.",
):
    cases = []
    for raw in examples.strip().split("\n---\n"):
        prompt, steps, answer = raw.strip().split("\n|\n")
        cases.append((prompt, steps.splitlines(), answer))
    assert len(cases) == 3, key
    e, *tasks = cases
    CONTENT[key] = dict(
        name=key,
        rule=rule,
        method=method,
        example=e[0],
        worked=solution(e[1], e[2]),
        tasks=[x[0] for x in tasks],
        answers=[solution(x[1], x[2]) for x in tasks],
        mistake=mistake,
    )


add(
    "sets",
    "Tập hợp gồm các phần tử xác định. Viết x ∈ A khi x là phần tử A, x ∉ A khi không thuộc. Có thể liệt kê phần tử hoặc nêu tính chất đặc trưng. Không tính lặp cùng một phần tử.",
    "1. Xác định điều kiện của phần tử.\n2. Liệt kê hoặc mô tả bằng tính chất.\n3. Kiểm tra từng phần tử và dùng kí hiệu thuộc đúng.",
    """
Viết tập hợp A các số tự nhiên nhỏ hơn 5; xét 3 và 7 có thuộc A không.
|
Các số tự nhiên nhỏ hơn 5 là 0, 1, 2, 3, 4.
A = {0; 1; 2; 3; 4}; 3 có trong danh sách, 7 không có.
|
A = {0; 1; 2; 3; 4}; 3 ∈ A; 7 ∉ A.
---
Liệt kê tập hợp các số tự nhiên chẵn lớn hơn 1 và nhỏ hơn 9.
|
Các số chẵn cần xét là 2, 4, 6, 8.
Mỗi số đều thỏa cả hai điều kiện về khoảng.
|
{2; 4; 6; 8}.
---
Cho B = {1; 2; 2; 3}. B có mấy phần tử khác nhau?
|
Số 2 xuất hiện hai lần nhưng chỉ là một phần tử.
Các phần tử khác nhau là 1, 2, 3.
|
3 phần tử.
""",
)
add(
    "powers",
    "Với n nguyên dương, a^n là tích n thừa số a. Với a khác 0, a^0 = 1. Cùng cơ số: a^m × a^n = a^(m+n); a^m : a^n = a^(m−n) khi m≥n và a≠0; (a^m)^n = a^(mn).",
    "1. Xác định cơ số và số mũ, giữ ngoặc với cơ số âm.\n2. Chọn quy tắc cùng cơ số hoặc lũy thừa của lũy thừa.\n3. Tính và kiểm tra điều kiện chia.",
    """
Tính 2^3 × 2^4.
|
Hai lũy thừa cùng cơ số 2 nên cộng các số mũ.
2^3 × 2^4 = 2^7 = 128.
|
128.
---
Tính (−2)^4 và −2^4.
|
(−2)^4 là tích bốn số −2 nên bằng 16.
−2^4 là số đối của 2^4 nên bằng −16.
|
16 và −16.
---
Tính (3^2)^3 : 3^4.
|
(3^2)^3 = 3^6.
3^6 : 3^4 = 3^2 = 9.
|
9.
""",
)
add(
    "divisibility",
    "a chia hết cho b khác 0 khi tồn tại số nguyên k sao cho a = bk. Nếu từng số hạng chia hết cho m thì tổng chia hết cho m. Trong số tự nhiên, chia hết cho 2, 5 xét chữ số tận cùng; cho 3, 9 xét tổng chữ số.",
    "1. Xác định số chia và điều kiện khác 0.\n2. Dùng dấu hiệu thích hợp hoặc biểu diễn thành tích.\n3. Kiểm tra kết luận, không suy ngược tính chất tổng tùy ý.",
    """
Xét 4 536 có chia hết cho 2, 3, 9 không.
|
Chữ số tận cùng là 6 nên chia hết cho 2.
Tổng chữ số: 4 + 5 + 3 + 6 = 18; 18 chia hết cho 3 và 9.
|
Chia hết cho cả 2, 3, 9.
---
Trong 125, 230, 342, số nào chia hết cho 5?
|
Số chia hết cho 5 tận cùng 0 hoặc 5.
125 tận cùng 5, 230 tận cùng 0; 342 tận cùng 2.
|
125 và 230.
---
Không tính tổng, xét 18 + 24 có chia hết cho 6 không.
|
18 = 6 × 3; 24 = 6 × 4 nên cả hai chia hết cho 6.
Theo tính chất chia hết của tổng, 18 + 24 chia hết cho 6.
|
Có.
""",
)
add(
    "prime_gcd_lcm",
    "Số nguyên tố là số tự nhiên lớn hơn 1 chỉ có hai ước dương 1 và chính nó. ƯCLN lấy các thừa số nguyên tố chung với số mũ nhỏ nhất; BCNN lấy chung và riêng với số mũ lớn nhất.",
    "1. Phân tích mỗi số thành thừa số nguyên tố.\n2. Chọn thừa số và số mũ theo ƯCLN hoặc BCNN.\n3. Nhân lại, kiểm tra tính chia hết.",
    """
Tìm ƯCLN và BCNN của 18 và 24.
|
18 = 2 × 3^2; 24 = 2^3 × 3.
ƯCLN = 2 × 3 = 6; BCNN = 2^3 × 3^2 = 72.
|
ƯCLN: 6; BCNN: 72.
---
Số 29 có phải số nguyên tố không?
|
Chỉ cần thử các số nguyên tố 2, 3, 5 vì bình phương 7 đã lớn hơn 29.
29 không chia hết cho 2, 3 hoặc 5 nên chỉ có ước dương 1 và 29.
|
29 là số nguyên tố.
---
Tìm ƯCLN của 12 và 20; dùng để rút gọn 12/20.
|
12 = 2^2 × 3; 20 = 2^2 × 5 nên ƯCLN là 4.
12/20 = (12 : 4)/(20 : 4) = 3/5.
|
ƯCLN là 4; phân số tối giản 3/5.
""",
)
add(
    "integers",
    "Số nguyên gồm số nguyên âm, 0 và số nguyên dương. Cộng cùng dấu: cộng giá trị tuyệt đối và giữ dấu; khác dấu: trừ hai giá trị tuyệt đối, lấy dấu số có giá trị tuyệt đối lớn hơn. Trừ a−b = a+(−b). Nhân/chia cùng dấu được dương, khác dấu được âm; số chia khác 0.",
    "1. Nhận biết dấu và phép tính.\n2. Áp dụng quy tắc dấu rồi tính giá trị tuyệt đối.\n3. Khi có ngoặc, đổi dấu từng số hạng nếu bỏ ngoặc sau dấu trừ.",
    """
Tính (−7) + 12 − 9.
|
(−7) + 12 = 5 vì 12 − 7 = 5 và số có giá trị tuyệt đối lớn hơn mang dấu dương.
5 − 9 = 5 + (−9) = −4.
|
−4.
---
Tính (−6) × (−4) : (−3).
|
(−6) × (−4) = 24 vì hai thừa số cùng dấu.
24 : (−3) = −8 vì hai số khác dấu.
|
−8.
---
Rút gọn rồi tính 10 − (3 − 8).
|
Bỏ ngoặc sau dấu trừ, đổi dấu các số hạng trong ngoặc: 10 − 3 + 8.
10 − 3 + 8 = 7 + 8 = 15.
|
15.
""",
)
add(
    "signed_fractions",
    "Phân số a/b có a, b là số nguyên, b khác 0. Có thể chuyển dấu âm ở mẫu lên tử. Cộng/trừ cần cùng mẫu; nhân tử với tử và mẫu với mẫu; chia bằng nhân phân số đảo của số chia khác 0.",
    "1. Chuẩn hóa dấu và kiểm tra mẫu khác 0.\n2. Quy đồng khi cộng/trừ; đảo đúng phân số khi chia.\n3. Rút gọn và so sánh với yêu cầu.",
    """
Tính −2/3 + 5/6.
|
Quy đồng: −2/3 = −4/6.
−4/6 + 5/6 = 1/6.
|
1/6.
---
Tính (−3/4) : (9/8).
|
Nhân với phân số đảo của 9/8: (−3/4) × (8/9).
Kết quả = −24/36 = −2/3.
|
−2/3.
---
So sánh −3/5 và −1/2.
|
Quy đồng: −3/5 = −6/10; −1/2 = −5/10.
Vì −6 < −5 nên −6/10 < −5/10.
|
−3/5 < −1/2.
""",
)
add(
    "fraction_problems",
    "Tìm a/b của một số: nhân số đó với a/b. Tìm số biết a/b của nó bằng c: lấy c chia cho a/b (a/b khác 0). Phân biệt phần đã biết và toàn bộ.",
    "1. Tóm tắt phần và toàn bộ.\n2. Chọn nhân hay chia theo đại lượng cần tìm.\n3. Giải có đơn vị và kiểm tra lại.",
    """
Một lớp có 40 học sinh, 3/5 tham gia hoạt động. Có mấy bạn tham gia?
|
Số bạn tham gia là:
40 × 3/5 = 24 (học sinh)
|
24 học sinh.
---
3/4 số bi của An bằng 18 viên. An có bao nhiêu viên bi?
|
Số bi của An là:
18 : (3/4) = 24 (viên)
|
24 viên bi.
---
Một cửa hàng giảm 15% giá 200 000 đồng. Tính giá sau giảm.
|
Số tiền giảm là 200 000 × 15/100 = 30 000 (đồng).
Giá sau giảm là 200 000 − 30 000 = 170 000 (đồng).
|
170 000 đồng.
""",
)
add(
    "symmetry",
    "Trục đối xứng: gấp theo trục, hai phần hình trùng khít. Tâm đối xứng: quay hình nửa vòng quanh tâm thì hình trùng chính nó. Một hình có thể có một, nhiều hoặc không có các đối xứng này.",
    "1. Xác định phép gấp hoặc quay nửa vòng.\n2. Kiểm tra toàn bộ hình, không chỉ một phần.\n3. Nêu trục hoặc tâm cụ thể, tránh suy mọi hình đều có.",
    """
Nêu trục và tâm đối xứng của hình chữ nhật không phải hình vuông.
|
Hai đường qua trung điểm hai cặp cạnh đối diện là hai trục đối xứng.
Giao điểm hai đường chéo là tâm đối xứng; hai đường chéo không phải trục trong trường hợp này.
|
2 trục đối xứng; tâm là giao điểm hai đường chéo.
---
Hình tròn có bao nhiêu trục đối xứng? Tâm đối xứng ở đâu?
|
Mọi đường thẳng qua tâm đều chia hình tròn thành hai phần đối xứng.
Quay nửa vòng quanh tâm vẫn giữ nguyên hình tròn.
|
Vô số trục; tâm đối xứng là tâm hình tròn.
---
Tam giác đều có tâm đối xứng không? Có mấy trục đối xứng?
|
Ba đường nối đỉnh với trung điểm cạnh đối diện là ba trục đối xứng.
Quay nửa vòng không đưa tam giác đều về chính nó nên không có tâm đối xứng.
|
3 trục; không có tâm đối xứng.
""",
)
add(
    "quadrilateral_area",
    "Chu vi là tổng độ dài các cạnh. Diện tích hình chữ nhật ab; bình hành ah; hình thoi d₁d₂/2; hình thang (a+b)h/2. Độ dài trong mỗi công thức phải cùng đơn vị; h là chiều cao tương ứng.",
    "1. Nhận dạng hình và dữ kiện.\n2. Chọn công thức với đúng đáy, chiều cao hoặc đường chéo.\n3. Tính kèm đơn vị vuông, phân biệt chu vi.",
    """
Hình bình hành có đáy 8 cm, chiều cao tương ứng 5 cm. Tính diện tích.
|
Diện tích hình bình hành là:
8 × 5 = 40 (cm²)
|
40 cm².
---
Hình thoi có hai đường chéo 6 cm và 8 cm. Tính diện tích.
|
Diện tích hình thoi là:
6 × 8 : 2 = 24 (cm²)
|
24 cm².
---
Hình thang có hai đáy 10 m, 6 m, chiều cao 4 m. Tính diện tích.
|
Diện tích hình thang là:
(10 + 6) × 4 : 2 = 32 (m²)
|
32 m².
""",
)
add(
    "probability",
    "Không gian mẫu gồm các kết quả của phép thử. Khi các kết quả đồng khả năng và hữu hạn, P(A) = số kết quả thuận lợi/số kết quả có thể. Xác suất thực nghiệm là số lần sự kiện xảy ra chia số lần thử, không phải lời đảm bảo cho lần sau.",
    "1. Mô tả phép thử và các kết quả.\n2. Kiểm tra đồng khả năng nếu dùng định nghĩa cổ điển.\n3. Đếm thuận lợi và tổng rồi lập tỉ số.",
    """
Gieo xúc xắc cân đối 6 mặt. Tính xác suất xuất hiện số chẵn.
|
Có 6 kết quả đồng khả năng: 1, 2, 3, 4, 5, 6.
Các số chẵn là 2, 4, 6 nên P = 3/6 = 1/2.
|
1/2.
---
Tung đồng xu cân đối. Xác suất xuất hiện mặt ngửa là bao nhiêu?
|
Có hai kết quả đồng khả năng: sấp và ngửa.
Một kết quả thuận lợi nên P = 1/2.
|
1/2.
---
Trong 50 lần thử có 18 lần xuất hiện A. Tính xác suất thực nghiệm của A.
|
Lấy số lần A xuất hiện chia tổng số lần thử.
18/50 = 9/25 = 0,36.
|
9/25, tức 0,36.
""",
)
add(
    "ratios",
    "Tỉ lệ thức a/b = c/d có b,d khác 0 tương đương ad = bc. Dãy tỉ số bằng nhau có thể dùng tính chất (a+c)/(b+d) khi mẫu tổng khác 0. Tỉ lệ thuận y=kx; tỉ lệ nghịch xy=k với x khác 0.",
    "1. Xác định dạng tỉ lệ và điều kiện mẫu.\n2. Dùng tích chéo hoặc hệ số không đổi.\n3. Thử lại vào dữ kiện.",
    """
Tìm x trong x/6 = 5/3.
|
Nhân chéo: 3x = 6 × 5 = 30.
Chia hai vế cho 3 được x = 10.
|
x = 10.
---
Hai số x, y có x/2 = y/3 và x + y = 25. Tìm x, y.
|
Tỉ số chung bằng (x+y)/(2+3) = 25/5 = 5.
x = 2 × 5 = 10; y = 3 × 5 = 15.
|
x = 10; y = 15.
---
Công việc cố định: 4 người làm 6 ngày. Năng suất như nhau, 8 người làm mấy ngày?
|
Số người và số ngày tỉ lệ nghịch, tích không đổi.
Số ngày là 4 × 6 : 8 = 3 (ngày).
|
3 ngày.
""",
)
add(
    "roots_real",
    "Căn bậc hai số học √a chỉ xác định trong số thực khi a≥0 và luôn không âm. (√a)²=a; √(x²)=|x|. Số vô tỉ không viết được thành tỉ số hai số nguyên; số thực gồm hữu tỉ và vô tỉ.",
    "1. Kiểm tra biểu thức dưới căn không âm.\n2. Phân biệt căn số học với nghiệm phương trình x²=a.\n3. Dùng giá trị tuyệt đối đúng khi căn của bình phương.",
    """
Tính √49 và tìm x thỏa x² = 49.
|
Căn bậc hai số học của 49 là 7.
Phương trình x² = 49 có hai nghiệm đối nhau 7 và −7.
|
√49 = 7; x = 7 hoặc x = −7.
---
Tính √((−5)²).
|
Áp dụng √(x²) = |x|.
Kết quả = |−5| = 5.
|
5.
---
Số √2 là hữu tỉ hay vô tỉ? So sánh √2 với 1 và 2.
|
√2 không biểu diễn được thành tỉ số hai số nguyên nên là vô tỉ.
Vì 1² < 2 < 2² và các số đang xét không âm nên 1 < √2 < 2.
|
Vô tỉ; 1 < √2 < 2.
""",
)
add(
    "angle_lines",
    "Hai góc kề bù có tổng 180°; hai góc đối đỉnh bằng nhau. Tia phân giác chia một góc thành hai góc bằng nhau. Hai đường song song tạo góc đồng vị hoặc so le trong bằng nhau khi bị cắt bởi đường thứ ba.",
    "1. Nhận diện đúng vị trí các góc.\n2. Nêu tính chất trước khi tính.\n3. Nếu suy song song, dùng dấu hiệu với cặp góc tương ứng.",
    """
Hai góc kề bù, một góc 65°. Tính góc còn lại.
|
Tổng hai góc kề bù bằng 180°.
Góc còn lại: 180° − 65° = 115°.
|
115°.
---
Tia Oz phân giác góc xOy bằng 80°. Tính góc xOz.
|
Phân giác chia góc thành hai phần bằng nhau.
Góc xOz bằng 80° : 2 = 40°.
|
40°.
---
Hai đường thẳng bị cắt bởi đường thứ ba, có một cặp góc so le trong đều 70°. Hai đường có song song không?
|
Cặp góc đã cho đúng vị trí so le trong và bằng nhau.
Theo dấu hiệu nhận biết, hai đường thẳng song song.
|
Có, hai đường song song.
""",
)
add(
    "triangle_angles",
    "Tổng ba góc của tam giác bằng 180°. Tam giác cân có hai góc ở đáy bằng nhau. Góc ngoài tam giác bằng tổng hai góc trong không kề với nó.",
    "1. Xác định các góc trong và ngoài.\n2. Dùng tổng 180° hoặc tính chất tam giác cân.\n3. Kiểm tra cả ba góc đều dương.",
    """
Tam giác ABC có góc A = 50°, góc B = 60°. Tính góc C.
|
Tổng ba góc bằng 180°.
C = 180° − 50° − 60° = 70°.
|
70°.
---
Tam giác cân tại A có góc A = 40°. Tính hai góc đáy.
|
Hai góc đáy B và C bằng nhau.
Mỗi góc bằng (180° − 40°) : 2 = 70°.
|
B = C = 70°.
---
Góc ngoài tại C của tam giác có hai góc trong không kề là 35° và 65°. Tính góc ngoài.
|
Góc ngoài bằng tổng hai góc trong không kề.
35° + 65° = 100°.
|
100°.
""",
)
add(
    "congruent",
    "Hai tam giác bằng nhau có các cạnh, góc tương ứng bằng nhau. Các trường hợp: cạnh–cạnh–cạnh; cạnh–góc–cạnh với góc xen giữa; góc–cạnh–góc. Tam giác vuông còn có trường hợp cạnh huyền–cạnh góc vuông.",
    "1. Ghi thứ tự các đỉnh tương ứng.\n2. Nêu đủ các dữ kiện của một trường hợp bằng nhau.\n3. Kết luận các cạnh hoặc góc tương ứng cần tìm.",
    """
AB = DE, AC = DF, BC = EF. Chứng minh hai tam giác ABC và DEF bằng nhau.
|
Ba cặp cạnh tương ứng bằng nhau theo giả thiết.
Suy ra tam giác ABC bằng tam giác DEF theo cạnh–cạnh–cạnh.
|
ΔABC = ΔDEF (c.c.c).
---
AB = DE, góc BAC = góc EDF, AC = DF. Dùng trường hợp nào?
|
Góc đã cho nằm xen giữa hai cạnh tương ứng.
Hai tam giác bằng nhau theo cạnh–góc–cạnh.
|
c.g.c; A tương ứng D, B tương ứng E, C tương ứng F.
---
Hai tam giác vuông có cạnh huyền cùng dài 5 cm và một cạnh góc vuông cùng dài 3 cm. Có bằng nhau không?
|
Cặp cạnh huyền bằng nhau và một cặp cạnh góc vuông bằng nhau.
Áp dụng trường hợp cạnh huyền–cạnh góc vuông.
|
Có, hai tam giác vuông bằng nhau.
""",
)
add(
    "triangle_relations",
    "Trong tam giác, cạnh lớn hơn đối diện góc lớn hơn. Tổng hai cạnh lớn hơn cạnh còn lại. Đường vuông góc là đoạn ngắn nhất từ một điểm tới đường thẳng. Trung tuyến, phân giác, trung trực và đường cao có các điểm đồng quy tương ứng.",
    "1. Xác định cạnh đối diện góc hoặc loại đường đặc biệt.\n2. Chọn đúng bất đẳng thức hoặc tính chất đồng quy.\n3. Nêu kết luận với đầy đủ giả thiết.",
    """
Ba độ dài 3 cm, 4 cm, 8 cm có là ba cạnh tam giác không?
|
Tổng hai độ dài nhỏ là 3 + 4 = 7 cm, bé hơn 8 cm.
Không thỏa bất đẳng thức tam giác.
|
Không.
---
G là trọng tâm tam giác, AM là trung tuyến và AM = 9 cm. Tính AG.
|
Trọng tâm cách đỉnh một đoạn bằng 2/3 trung tuyến.
AG = 9 × 2/3 = 6 (cm).
|
6 cm.
---
P nằm trên đường trung trực AB và PA = 5 cm. Tính PB.
|
Điểm trên đường trung trực cách đều hai đầu mút.
PB = PA = 5 cm.
|
5 cm.
""",
)
add(
    "polynomials",
    "Đơn thức là tích của số và các biến với số mũ nguyên không âm. Đơn thức đồng dạng có cùng phần biến. Đa thức là tổng các đơn thức; thu gọn bằng cộng hệ số của các hạng đồng dạng. Bậc của đa thức khác 0 là bậc lớn nhất của hạng còn lại.",
    "1. Nhận dạng hệ số và phần biến.\n2. Nhóm các hạng đồng dạng.\n3. Cộng hoặc trừ hệ số; xác định bậc sau thu gọn.",
    """
Thu gọn 3x²y + 2xy² − x²y; tìm bậc.
|
3x²y và −x²y đồng dạng, tổng là 2x²y.
Đa thức thu gọn: 2x²y + 2xy²; mỗi hạng có bậc 3.
|
2x²y + 2xy²; bậc 3.
---
Cho P(x)=2x²−3x+1, Q(x)=x²+4x−2. Tính P+Q.
|
Nhóm các hệ số cùng lũy thừa của x.
P+Q = (2+1)x² + (−3+4)x + (1−2) = 3x²+x−1.
|
3x²+x−1.
---
Với P, Q trên, tính P−Q.
|
Đổi dấu từng hạng của Q khi bỏ ngoặc sau dấu trừ.
P−Q = 2x²−3x+1−x²−4x+2 = x²−7x+3.
|
x²−7x+3.
""",
)
add(
    "polynomial_product",
    "Nhân đơn thức với đa thức: nhân với từng hạng rồi cộng. Nhân hai đa thức: nhân từng hạng của đa thức này với từng hạng của đa thức kia. Chia đa thức cho đơn thức khác 0 khi từng hạng chia được thì chia từng hạng.",
    "1. Viết đủ các tích riêng hoặc thương từng hạng.\n2. Dùng quy tắc dấu và số mũ.\n3. Thu gọn, có thể nhân ngược để kiểm tra phép chia.",
    """
Tính (x+2)(x+3).
|
Nhân phân phối: x²+3x+2x+6.
Gộp hạng đồng dạng được x²+5x+6.
|
x²+5x+6.
---
Chia 6x³−9x² cho 3x với x khác 0.
|
Chia từng hạng cho 3x: 6x³/(3x)=2x², −9x²/(3x)=−3x.
Thương là 2x²−3x; nhân lại với 3x được đa thức ban đầu.
|
2x²−3x.
---
Chia x²+5x+6 cho x+2 theo phép chia đa thức.
|
Vì (x+2)(x+3)=x²+5x+6 nên phép chia hết.
Thương là x+3, dư bằng 0.
|
Thương x+3; dư 0.
""",
)
add(
    "identities",
    "(a±b)²=a²±2ab+b²; a²−b²=(a−b)(a+b). (a±b)³=a³±3a²b+3ab²±b³. a³+b³=(a+b)(a²−ab+b²); a³−b³=(a−b)(a²+ab+b²). Phân tích nhân tử còn có đặt nhân tử chung và nhóm hạng.",
    "1. Nhận đúng dạng và dấu.\n2. Thay a, b vào đủ các hạng.\n3. Thu gọn hoặc nhân ngược để kiểm tra.",
    """
Khai triển (x−2)².
|
Dùng bình phương của hiệu: x²−2×x×2+2².
Thu gọn được x²−4x+4.
|
x²−4x+4.
---
Phân tích x³−8 thành nhân tử.
|
8=2³, áp dụng hiệu hai lập phương.
x³−8=(x−2)(x²+2x+4).
|
(x−2)(x²+2x+4).
---
Phân tích x³+3x²+3x+1 và 3x²−12 thành nhân tử.
|
Đa thức thứ nhất là lập phương của tổng: (x+1)³.
Đa thức thứ hai: 3(x²−4)=3(x−2)(x+2).
|
(x+1)³; 3(x−2)(x+2).
""",
)
add(
    "linear_equation",
    "Phương trình bậc nhất ax+b=0 với a khác 0 có nghiệm x=−b/a. Được cộng cùng biểu thức hoặc nhân/chia cùng số khác 0 ở hai vế. Bài toán có lời văn cần đặt ẩn, điều kiện và đối chiếu nghiệm.",
    "1. Đặt điều kiện nếu có mẫu hoặc bối cảnh.\n2. Biến đổi tương đương, chuyển vế đổi dấu.\n3. Giải, thử lại rồi kết luận.",
    """
Giải 3x−7=8.
|
Cộng 7 vào hai vế: 3x=15.
Chia hai vế cho 3: x=5; thay lại 3×5−7=8.
|
x=5.
---
Giải 2(x−3)=x+4.
|
Khai triển và chuyển vế: 2x−6=x+4 nên x=10.
Thử lại: 2×(10−3)=14 và 10+4=14.
|
x=10.
---
Ba quyển vở cùng loại và 5 000 đồng tiền bút hết 26 000 đồng. Một quyển vở giá bao nhiêu?
|
Gọi x đồng là giá một quyển, x>0; có 3x+5 000=26 000.
Suy ra 3x=21 000, x=7 000, thỏa điều kiện.
|
7 000 đồng.
""",
)
add(
    "rational_expressions",
    "Phân thức A/B xác định khi B khác 0. Nhân/chia cả tử và mẫu với cùng đa thức khác 0 tại giá trị xét giữ nguyên giá trị. Cộng/trừ cần mẫu chung; chia phân thức bằng nhân phân thức đảo và số chia phải khác 0.",
    "1. Ghi điều kiện từ biểu thức ban đầu.\n2. Phân tích nhân tử, quy đồng hoặc rút gọn nhân tử chung.\n3. Tính và giữ điều kiện gốc sau rút gọn.",
    """
Rút gọn (x²−1)/(x−1).
|
Điều kiện x≠1; tử x²−1=(x−1)(x+1).
Khử nhân tử x−1 khác 0 được x+1.
|
x+1, với x≠1.
---
Tính 1/x + 1/(x+1).
|
Điều kiện x≠0 và x≠−1; mẫu chung x(x+1).
Tổng = (x+1+x)/(x(x+1)) = (2x+1)/(x(x+1)).
|
(2x+1)/(x(x+1)), x≠0,−1.
---
Tính (x/2) : (x²/4).
|
Số chia phải khác 0 nên x≠0.
(x/2)×(4/x²)=2/x sau rút gọn nhân tử x.
|
2/x, x≠0.
""",
)
add(
    "quadrilaterals",
    "Tổng góc tứ giác 360°. Hình bình hành có hai cặp cạnh đối song song, cạnh đối bằng nhau, đường chéo cắt nhau tại trung điểm. Hình chữ nhật có bốn góc vuông, đường chéo bằng nhau; hình thoi có bốn cạnh bằng nhau, hai đường chéo vuông góc; hình vuông có cả hai đặc điểm. Hình thang cân có góc kề một đáy bằng nhau và hai đường chéo bằng nhau.",
    "1. Xác định giả thiết của tứ giác.\n2. Chọn dấu hiệu nhận biết phù hợp, không đảo mệnh đề tùy ý.\n3. Suy cạnh, góc hoặc đường chéo theo đúng loại hình.",
    """
Tứ giác có ba góc 70°, 100°, 80°. Tính góc còn lại.
|
Tổng các góc tứ giác bằng 360°.
Góc còn lại: 360°−70°−100°−80°=110°.
|
110°.
---
ABCD là hình bình hành có hai đường chéo cắt nhau tại O, AC=10 cm. Tính AO.
|
Hai đường chéo hình bình hành cắt nhau tại trung điểm mỗi đường.
AO=AC/2=5 cm.
|
5 cm.
---
Một hình bình hành có một góc vuông và hai cạnh kề bằng nhau. Nó là hình gì?
|
Hình bình hành có một góc vuông là hình chữ nhật.
Có thêm hai cạnh kề bằng nhau nên bốn cạnh bằng nhau, đó là hình vuông.
|
Hình vuông.
""",
)
add(
    "thales_similarity",
    "Đường song song một cạnh tam giác cắt hai cạnh còn lại tạo các đoạn tương ứng tỉ lệ. Đường trung bình nối hai trung điểm thì song song cạnh thứ ba và bằng nửa cạnh đó. Hai tam giác đồng dạng có các góc tương ứng bằng nhau, các cạnh tương ứng tỉ lệ; các trường hợp g.g, c.g.c, c.c.c dùng đúng thứ tự.",
    "1. Viết các đỉnh tương ứng và điều kiện song song hoặc đồng dạng.\n2. Lập tỉ số đúng cạnh.\n3. Giải độ dài; cùng đơn vị và tỉ số dương.",
    """
Trong ΔABC, D thuộc AB, E thuộc AC, DE song song BC. AD=3, AB=6, AC=10 cm. Tính AE.
|
Theo Thales: AD/AB=AE/AC=3/6=1/2.
AE=10×1/2=5 cm.
|
5 cm.
---
M, N là trung điểm AB, AC của tam giác ABC; BC=12 cm. Tính MN.
|
MN là đường trung bình nên MN song song BC và MN=BC/2.
MN=12/2=6 cm.
|
6 cm.
---
ΔABC đồng dạng ΔDEF theo thứ tự, AB=4, DE=6, BC=8 cm. Tính EF.
|
Tỉ số DE/AB=6/4=3/2.
EF/BC=3/2 nên EF=8×3/2=12 cm.
|
12 cm.
""",
)
add(
    "angle_bisector_ratio",
    "Phân giác trong của một góc tam giác chia cạnh đối diện thành hai đoạn tỉ lệ với hai cạnh kề. Trong ΔABC, AD phân giác A, D trên BC thì BD/DC=AB/AC.",
    "1. Xác định phân giác trong và cạnh đối diện.\n2. Lập tỉ lệ đúng thứ tự.\n3. Kết hợp tổng hoặc độ dài đã biết để tìm đoạn.",
    """
AD là phân giác trong ΔABC, AB=6, AC=9, BC=10 cm. Tính BD và DC.
|
BD/DC=6/9=2/3, tổng hai đoạn là 10 cm.
BD=10×2/5=4 cm; DC=10−4=6 cm.
|
BD=4 cm; DC=6 cm.
---
AD là phân giác, AB=4, AC=6, BD=2 cm. Tính DC.
|
BD/DC=AB/AC=2/3.
2/DC=2/3 nên DC=3 cm.
|
3 cm.
---
AD phân giác, BD=3, DC=5, AC=10 cm. Tính AB.
|
AB/AC=BD/DC=3/5.
AB=10×3/5=6 cm.
|
6 cm.
""",
)
add(
    "pythagoras",
    "Tam giác vuông có bình phương cạnh huyền bằng tổng bình phương hai cạnh góc vuông. Đảo lại, nếu bình phương cạnh lớn nhất bằng tổng hai bình phương cạnh kia thì tam giác vuông.",
    "1. Xác định đúng cạnh huyền đối diện góc vuông hoặc cạnh lớn nhất.\n2. Viết hệ thức bình phương.\n3. Lấy căn dương để tìm độ dài và ghi đơn vị.",
    """
Tam giác vuông có hai cạnh góc vuông 6 cm, 8 cm. Tính cạnh huyền.
|
Bình phương cạnh huyền: 6²+8²=36+64=100.
Cạnh huyền bằng √100=10 cm.
|
10 cm.
---
Tam giác có các cạnh 5, 12, 13 cm. Có vuông không?
|
Cạnh lớn nhất là 13; 5²+12²=25+144=169=13².
Theo định lí đảo, tam giác vuông.
|
Có, vuông ở góc đối diện cạnh 13 cm.
---
Tam giác vuông có cạnh huyền 13 m, một cạnh góc vuông 5 m. Tính cạnh kia.
|
Bình phương cạnh kia: 13²−5²=169−25=144.
Độ dài là √144=12 m.
|
12 m.
""",
)
add(
    "solids_volume",
    "Lăng trụ đứng có V=S_đáy×h, S_xq=chu vi đáy×h. Hình chóp đều có V=S_đáy×h/3; S_xq=nửa chu vi đáy×trung đoạn. Chiều cao vuông góc mặt đáy khác với cạnh bên hoặc trung đoạn.",
    "1. Nhận dạng lăng trụ hay hình chóp, tìm diện tích đáy.\n2. Chọn chiều cao vuông góc cho thể tích; trung đoạn cho diện tích chóp đều.\n3. Tính với cùng đơn vị và ghi đơn vị vuông/khối.",
    """
Lăng trụ đứng có đáy tam giác vuông cạnh góc vuông 3 cm, 4 cm và chiều cao lăng trụ 10 cm. Tính thể tích.
|
Diện tích đáy: 3×4/2=6 cm².
Thể tích: 6×10=60 cm³.
|
60 cm³.
---
Chóp tứ giác đều có cạnh đáy 6 cm, chiều cao 4 cm. Tính thể tích.
|
Diện tích đáy vuông: 6×6=36 cm².
Thể tích: 36×4/3=48 cm³.
|
48 cm³.
---
Chóp tam giác đều có chu vi đáy 18 cm, trung đoạn 5 cm. Tính diện tích xung quanh.
|
Nửa chu vi đáy: 18/2=9 cm.
Diện tích xung quanh: 9×5=45 cm².
|
45 cm².
""",
)
add(
    "functions_linear",
    "Hàm số gán mỗi giá trị x thuộc tập xác định đúng một giá trị y. Hàm bậc nhất y=ax+b với a khác 0 có đồ thị là đường thẳng và hệ số góc a. Hai đường thẳng y=ax+b, y=a′x+b′ song song khi a=a′, b≠b′.",
    "1. Xác định tập giá trị x được phép.\n2. Thay số tính y hoặc dùng hai điểm để vẽ đường thẳng.\n3. So sánh hệ số góc khi xét vị trí; nêu kết luận.",
    """
Cho y=2x−3. Tính y tại x=4 và nêu hai điểm để vẽ đồ thị.
|
Tại x=4: y=2×4−3=5.
Chọn x=0 được (0;−3), x=2 được (2;1); nối hai điểm này thành đường thẳng.
|
y=5; đồ thị đi qua (0;−3) và (2;1).
---
Đường thẳng y=−3x+2 có hệ số góc bao nhiêu? Hàm tăng hay giảm?
|
Hệ số của x là −3 nên hệ số góc bằng −3.
Vì a<0 nên hàm số giảm trên R.
|
Hệ số góc −3; nghịch biến trên R.
---
Hai đường y=2x+1 và y=2x−4 có vị trí thế nào?
|
Hai hệ số góc cùng bằng 2.
Hai tung độ gốc khác nhau nên hai đường song song.
|
Song song.
""",
)
add(
    "systems",
    "Hệ hai phương trình bậc nhất hai ẩn cần một cặp (x;y) thỏa cả hai. Có thể giải bằng thế hoặc cộng đại số; cần nhân phù hợp để khử một ẩn. Hệ có thể có một, vô số hoặc không có nghiệm.",
    "1. Kiểm tra ẩn và điều kiện bối cảnh.\n2. Dùng thế hoặc cộng để khử một ẩn.\n3. Tìm ẩn còn lại và thử vào cả hai phương trình.",
    """
Giải hệ x+y=7, x−y=1.
|
Cộng hai phương trình: 2x=8 nên x=4.
Thay vào x+y=7 được y=3; cả hai phương trình đều thỏa.
|
(x;y)=(4;3).
---
Giải hệ 2x+y=8, x−y=1.
|
Từ phương trình thứ hai: y=x−1.
Thay vào phương trình đầu: 3x−1=8 nên x=3, y=2.
|
(3;2).
---
Mười vé gồm vé 20 000 đồng và 30 000 đồng, tổng tiền 240 000 đồng. Có mấy vé mỗi loại?
|
Gọi x, y là số vé tương ứng; x+y=10, 20x+30y=240 (nghìn đồng).
Trừ phương trình thứ hai cho 20 lần phương trình đầu: 10y=40 nên y=4, x=6.
|
6 vé 20 000 đồng và 4 vé 30 000 đồng.
""",
)
add(
    "inequality",
    "Cộng cùng một số vào hai vế giữ chiều bất đẳng thức. Nhân hoặc chia hai vế với số âm phải đổi chiều. Bất phương trình bậc nhất ax+b>0 (hoặc các dấu khác) giải tương tự phương trình nhưng phải xét dấu a.",
    "1. Thu gọn và chuyển hạng.\n2. Khi chia hệ số của ẩn, kiểm tra âm hay dương.\n3. Viết tập nghiệm và thử một giá trị.",
    """
Giải −2x+6>0.
|
Chuyển vế: −2x>−6.
Chia số âm −2 phải đổi chiều, được x<3.
|
x<3.
---
Giải 3x−4≤8.
|
3x≤12.
Chia số dương 3 giữ chiều: x≤4.
|
x≤4.
---
Biết a<b. So sánh −3a+2 và −3b+2.
|
Nhân a<b với −3 đổi chiều: −3a>−3b.
Cộng 2 vào hai vế giữ chiều.
|
−3a+2>−3b+2.
""",
)
add(
    "radical_transform",
    "Với a,b≥0: √(ab)=√a√b; với a≥0,b>0: √(a/b)=√a/√b. Luôn có √(x²)=|x|. Căn bậc ba có nghĩa với mọi số thực và ∛(x³)=x.",
    "1. Ghi điều kiện căn và mẫu.\n2. Tách thừa số chính phương hoặc dùng liên hợp khi thích hợp.\n3. Thu gọn và giữ dấu giá trị tuyệt đối.",
    """
Rút gọn √72−√8.
|
√72=6√2; √8=2√2.
Hiệu bằng 4√2.
|
4√2.
---
Rút gọn 1/(√3−1).
|
Nhân tử và mẫu với √3+1.
Mẫu bằng 3−1=2 nên kết quả là (√3+1)/2.
|
(√3+1)/2.
---
Tính ∛(−125) và √((x−2)²).
|
Vì (−5)³=−125 nên ∛(−125)=−5.
Căn số học của bình phương bằng giá trị tuyệt đối: |x−2|.
|
−5; |x−2|.
""",
)
add(
    "trig_right",
    "Trong tam giác vuông, với góc nhọn α: sinα=đối/huyền, cosα=kề/huyền, tanα=đối/kề, cotα=kề/đối. Có sin²α+cos²α=1. Độ dài và góc phải được xác định theo cùng góc đang xét.",
    "1. Chọn góc nhọn và xác định cạnh đối, kề, huyền.\n2. Chọn tỉ số chứa dữ kiện và ẩn.\n3. Tính độ dài hoặc góc; kiểm tra chế độ độ/radian của máy.",
    """
Tam giác ABC vuông tại A, AB=3, AC=4, BC=5. Tính sin B và cos B.
|
Đối với B, cạnh đối là AC=4, cạnh kề AB=3 và huyền BC=5.
sin B=4/5; cos B=3/5.
|
sin B=4/5; cos B=3/5.
---
Một thang dài 10 m tạo góc 30° với mặt đất ngang. Đầu thang cao bao nhiêu?
|
Chiều cao đối diện góc 30°, thang là cạnh huyền.
h=10 sin30°=10×1/2=5 m.
|
5 m.
---
Tam giác vuông có hai cạnh góc vuông kề và đối góc α lần lượt 6, 8 cm. Tính tanα.
|
Theo định nghĩa tanα=đối/kề.
tanα=8/6=4/3.
|
4/3.
""",
)
add(
    "circle_geometry",
    "Đường tròn tâm O bán kính R gồm các điểm cách O bằng R. Góc nội tiếp bằng nửa số đo cung bị chắn. Tứ giác nội tiếp có tổng hai góc đối 180°. Tam giác vuông có tâm ngoại tiếp là trung điểm cạnh huyền; tâm nội tiếp là giao các phân giác trong.",
    "1. Xác định tâm, bán kính và cung bị chắn.\n2. Ghi đúng tính chất của góc, dây hoặc tứ giác nội tiếp.\n3. Suy số đo hoặc độ dài; phân biệt tâm ngoại tiếp/nội tiếp.",
    """
Góc nội tiếp chắn cung 100°. Tính góc đó.
|
Góc nội tiếp bằng nửa số đo cung bị chắn.
Góc cần tìm bằng 100°/2=50°.
|
50°.
---
ABCD nội tiếp đường tròn, góc A=80°. Tính góc C.
|
Hai góc A và C đối nhau nên tổng 180°.
C=180°−80°=100°.
|
100°.
---
Tam giác vuông có cạnh huyền dài 10 cm. Tính bán kính ngoại tiếp.
|
Tâm ngoại tiếp là trung điểm cạnh huyền.
Bán kính bằng nửa cạnh huyền: 10/2=5 cm.
|
5 cm.
""",
)
add(
    "circle_positions",
    "Đường thẳng cách tâm một khoảng d: cắt đường tròn nếu d<R, tiếp xúc nếu d=R, không giao nếu d>R. Hai đường tròn tâm cách d: so sánh d với R+r và |R−r| để xét giao/tiếp xúc; trường hợp đồng tâm cần xét riêng.",
    "1. Xác định khoảng cách d và bán kính.\n2. So sánh đúng các ngưỡng.\n3. Nêu số giao điểm; không bỏ trường hợp tiếp xúc trong.",
    """
Đường tròn bán kính 5 cm, đường thẳng cách tâm 3 cm. Có bao nhiêu giao điểm?
|
d=3<R=5.
Đường thẳng cắt đường tròn tại hai điểm.
|
2 giao điểm.
---
Hai đường tròn bán kính 5 cm, 2 cm, khoảng cách tâm 7 cm. Xét vị trí.
|
R+r=7 cm và d=7 cm.
Hai đường tròn tiếp xúc ngoài.
|
Tiếp xúc ngoài, 1 giao điểm.
---
Hai đường tròn bán kính 5 cm, 2 cm, khoảng cách tâm 3 cm. Xét vị trí.
|
R−r=3 cm và d=3 cm.
Hai đường tròn tiếp xúc trong.
|
Tiếp xúc trong, 1 giao điểm.
""",
)
add(
    "arc_sector",
    "Với góc ở tâm n độ, độ dài cung l=πRn/180, diện tích quạt S=πR²n/360. Diện tích vành khuyên giữa hai đường tròn đồng tâm là π(R²−r²), R≥r. Đa giác đều có các cạnh và các góc bằng nhau.",
    "1. Kiểm tra góc theo độ và bán kính.\n2. Chọn công thức độ dài cung, diện tích quạt hoặc vành khuyên.\n3. Giữ π nếu yêu cầu chính xác; ghi đơn vị.",
    """
Tính độ dài cung 60° của đường tròn bán kính 6 cm.
|
Áp dụng l=πRn/180.
l=π×6×60/180=2π cm.
|
2π cm.
---
Tính diện tích quạt 90°, bán kính 4 cm.
|
Quạt chiếm 90/360=1/4 hình tròn.
S=π×4²×1/4=4π cm².
|
4π cm².
---
Tính diện tích vành khuyên bán kính ngoài 5 m, trong 3 m.
|
Lấy diện tích hình tròn ngoài trừ hình tròn trong.
S=π(25−9)=16π m².
|
16π m².
""",
)
add(
    "quadratic",
    "Phương trình ax²+bx+c=0, a≠0: Δ=b²−4ac. Δ>0 có hai nghiệm (−b±√Δ)/(2a); Δ=0 có nghiệm kép; Δ<0 không có nghiệm thực. Nếu có hai nghiệm kể cả trùng, tổng bằng −b/a, tích bằng c/a.",
    "1. Thu gọn và xác định a,b,c.\n2. Tính Δ hoặc phân tích nhân tử.\n3. Tìm nghiệm, kiểm tra điều kiện gốc nếu phương trình được biến đổi từ dạng khác.",
    """
Giải x²−5x+6=0.
|
Δ=25−24=1.
Hai nghiệm là (5−1)/2=2 và (5+1)/2=3; cũng có (x−2)(x−3)=0.
|
x=2 hoặc x=3.
---
Không giải phương trình 2x²−7x+3=0, tìm tổng và tích nghiệm; kiểm tra có nghiệm thực.
|
Δ=49−24=25>0 nên có hai nghiệm thực.
Theo Viète, tổng là 7/2 và tích là 3/2.
|
Tổng 7/2; tích 3/2.
---
Giải x⁴−5x²+4=0.
|
Đặt t=x²≥0, được t²−5t+4=(t−1)(t−4)=0.
t=1 hoặc 4 nên x=±1 hoặc ±2.
|
x∈{−2;−1;1;2}.
""",
)
add(
    "quadratic_function",
    "Hàm y=ax²+bx+c, a≠0, có trục đối xứng x=−b/(2a), đỉnh I(−b/(2a);−Δ/(4a)). a>0 parabol mở lên, a<0 mở xuống. Tam thức có dấu của a bên ngoài hai nghiệm phân biệt và dấu ngược bên trong; nếu không có nghiệm thực thì luôn cùng dấu a.",
    "1. Xác định a,b,c và đỉnh.\n2. Xét hướng mở, giao trục và các điểm đối xứng.\n3. Dùng nghiệm để lập bảng dấu hoặc các khoảng tăng giảm.",
    """
Tìm đỉnh và giá trị nhỏ nhất của y=x²−4x+3.
|
y=(x−2)²−1, bình phương không âm.
Đỉnh I(2;−1); giá trị nhỏ nhất −1 tại x=2.
|
I(2;−1); min y=−1.
---
Giải bất phương trình x²−5x+6<0.
|
Tam thức có hai nghiệm 2,3 và a=1>0.
Tam thức âm trong khoảng giữa hai nghiệm.
|
2<x<3.
---
Cho y=−2x². Tính y tại x=−3, x=3 và hướng mở đồ thị.
|
Cả hai giá trị x đều có x²=9 nên y=−18.
Hệ số a=−2<0 nên parabol mở xuống.
|
y(−3)=y(3)=−18; mở xuống.
""",
)
add(
    "rotational_solids",
    "Hình trụ: V=πr²h, S_xq=2πrh. Hình nón: V=πr²h/3, S_xq=πrl với l là đường sinh. Hình cầu: S=4πr², V=4πr³/3. Không nhầm chiều cao nón với đường sinh.",
    "1. Xác định loại hình và bán kính, chiều cao/đường sinh.\n2. Chọn công thức và thống nhất đơn vị.\n3. Ghi rõ đang tìm diện tích hay thể tích.",
    """
Hình trụ có r=3 cm, h=5 cm. Tính thể tích.
|
Diện tích đáy là 9π cm².
V=9π×5=45π cm³.
|
45π cm³.
---
Hình nón có r=3 cm, h=4 cm. Tính thể tích và diện tích xung quanh.
|
Đường sinh l=√(3²+4²)=5 cm.
V=π×9×4/3=12π cm³; S_xq=π×3×5=15π cm².
|
12π cm³; 15π cm².
---
Hình cầu bán kính 3 m. Tính diện tích và thể tích.
|
S=4π×3²=36π m².
V=4π×3³/3=36π m³.
|
36π m²; 36π m³.
""",
)
add(
    "frequency_tables",
    "Tần số là số lần xuất hiện một giá trị; tần số tương đối bằng tần số chia cỡ mẫu. Tổng tần số bằng cỡ mẫu, tổng tần số tương đối bằng 1. Ghép nhóm phải dùng các khoảng không chồng nhau và ghi quy ước đầu mút.",
    "1. Liệt kê giá trị hoặc nhóm.\n2. Đếm từng quan sát đúng một lần.\n3. Chia cho tổng để có tần số tương đối và kiểm tra tổng.",
    """
Dữ liệu 1,2,2,3,3,3. Lập tần số và tần số tương đối.
|
Cỡ mẫu n=6; tần số của 1,2,3 lần lượt 1,2,3.
Tần số tương đối tương ứng 1/6,1/3,1/2; tổng bằng 1.
|
1:1 (1/6); 2:2 (1/3); 3:3 (1/2).
---
Nhóm [10;20) có 8 quan sát trong tổng 40. Tính tần số tương đối.
|
Tần số tương đối là 8/40=1/5.
Đổi sang phần trăm được 20%.
|
20%.
---
Với hai nhóm [0;5) và [5;10), giá trị 5 vào nhóm nào?
|
Nhóm đầu không chứa đầu mút 5.
Nhóm sau chứa 5 và không chứa 10 nên giá trị 5 chỉ vào nhóm sau.
|
Nhóm [5;10).
""",
)
add(
    "statistics",
    "Trung bình bằng tổng giá trị chia cỡ mẫu; trung vị là giá trị giữa sau sắp xếp (cỡ chẵn lấy trung bình hai giá trị giữa); mốt có tần số lớn nhất. Khoảng biến thiên R=max−min; khoảng tứ phân vị ΔQ=Q₃−Q₁. Phương sai mẫu mô tả s²=(1/n)Σ(xᵢ−x̄)², độ lệch chuẩn s=√s²; không nhầm với công thức ước lượng chia n−1.",
    "1. Sắp xếp và xác định cỡ mẫu, quy ước tứ phân vị trong bài.\n2. Tính đúng đại lượng, với phương sai dùng tất cả độ lệch.\n3. Kiểm tra đơn vị; phương sai có đơn vị bình phương.",
    """
Tìm trung bình, trung vị và mốt của 1,2,2,3,7.
|
Dãy đã sắp xếp; tổng là 15, cỡ mẫu 5 nên trung bình bằng 3.
Giá trị giữa là 2; 2 xuất hiện nhiều nhất nên trung vị và mốt đều 2.
|
Trung bình 3; trung vị 2; mốt 2.
---
Tính phương sai và độ lệch chuẩn của 1,3 (dùng chia n).
|
Trung bình (1+3)/2=2; các độ lệch là −1 và 1.
Phương sai (1+1)/2=1; độ lệch chuẩn √1=1.
|
s²=1; s=1.
---
Với dãy 1,2,3,4,5,6,7,8, lấy Q₁,Q₃ là trung vị nửa dưới/nửa trên. Tính R, ΔQ.
|
R=8−1=7; Q₁=(2+3)/2=2,5; Q₃=(6+7)/2=6,5.
ΔQ=6,5−2,5=4.
|
R=7; ΔQ=4.
""",
)
add(
    "propositions",
    "Mệnh đề có giá trị đúng hoặc sai. Phủ định đảo giá trị chân lí. P⇒Q chỉ sai khi P đúng, Q sai. Phủ định “với mọi x, P(x)” là “tồn tại x sao cho không P(x)”; phủ định “tồn tại” dùng “với mọi”.",
    "1. Xác định câu có khẳng định rõ hay không.\n2. Xét đúng/sai hoặc phủ định đúng lượng từ.\n3. Với mệnh đề kéo theo, có thể tìm phản ví dụ.",
    """
Xét mệnh đề “Mọi số nguyên tố đều lẻ”. Viết phủ định và xác định đúng/sai.
|
Số 2 là số nguyên tố nhưng không lẻ nên mệnh đề sai.
Phủ định: “Có ít nhất một số nguyên tố không lẻ”, là mệnh đề đúng.
|
Mệnh đề sai; phủ định đúng.
---
Viết phủ định “Tồn tại số thực x sao cho x²<0”.
|
Đổi “tồn tại” thành “với mọi”, phủ định x²<0 thành x²≥0.
Được “Với mọi số thực x, x²≥0”.
|
∀x∈R, x²≥0.
---
Mệnh đề “Nếu n chia hết cho 4 thì n chia hết cho 2” đúng không?
|
Nếu n=4k thì n=2(2k), với k nguyên.
Vì vậy n chia hết cho 2.
|
Đúng.
""",
)
add(
    "set_operations",
    "Giao A∩B gồm phần tử thuộc cả hai; hợp A∪B thuộc ít nhất một; hiệu A trừ B gồm các phần tử thuộc A nhưng không thuộc B. Phần bù chỉ có nghĩa khi đã xác định tập vũ trụ. Với khoảng trên R, giữ đúng đầu mút đóng/mở.",
    "1. Viết điều kiện thuộc từng tập.\n2. Dùng “và” cho giao, “hoặc” cho hợp.\n3. Kiểm tra các đầu mút và phần tử bị loại.",
    """
A={1;2;3}, B={3;4}. Tìm giao và hợp.
|
Phần tử chung duy nhất là 3.
Gộp tất cả không lặp: 1,2,3,4.
|
A∩B={3}; A∪B={1;2;3;4}.
---
Tìm [1;5]∩(3;7).
|
Cần đồng thời x≥1, x≤5, x>3, x<7.
Kết hợp được 3<x≤5.
|
(3;5].
---
Tập vũ trụ U={1;2;3;4;5}, A={2;4}. Tìm phần bù của A trong U.
|
Lấy các phần tử U không thuộc A.
Loại 2,4 còn 1,3,5.
|
{1;3;5}.
""",
)
add(
    "linear_two_variables",
    "Bất phương trình bậc nhất hai ẩn có dạng ax+by≤c hoặc dấu tương tự, a,b không đồng thời 0. Đường ax+by=c là biên; lấy/không lấy biên theo dấu. Hệ có miền nghiệm là giao các nửa mặt phẳng.",
    "1. Vẽ đường biên bằng hai điểm.\n2. Thử một điểm không nằm trên biên để chọn phía.\n3. Lấy giao cho hệ; nếu tối ưu tuyến tính trên đa giác bị chặn, xét các đỉnh.",
    """
Mô tả miền nghiệm x+y≤4.
|
Biên qua (4;0),(0;4) và được lấy vì dấu ≤.
Điểm O(0;0) thỏa 0≤4 nên chọn nửa mặt phẳng chứa O, kể cả biên.
|
Nửa mặt phẳng chứa O với biên x+y=4.
---
Điểm (2;1) có thỏa x≥0, y≥0, x+y≤4 không?
|
2≥0, 1≥0 và 2+1=3≤4.
Điểm thỏa đồng thời cả ba bất phương trình.
|
Có.
---
Tìm max P=2x+y với x≥0,y≥0,x≤3,x+y≤4.
|
Miền nghiệm có đỉnh (0;0),(3;0),(3;1),(0;4).
P tại các đỉnh lần lượt 0,6,7,4; giá trị lớn nhất 7 tại (3;1).
|
Max P=7 tại (3;1).
""",
)
add(
    "triangle_trig",
    "Định lí cosin: a²=b²+c²−2bc cos A. Định lí sin: a/sin A=b/sin B=c/sin C=2R. Diện tích S=bc sin A/2. Với góc 0°–180°, sin không âm; cos đổi dấu khi qua 90°.",
    "1. Đặt a,b,c đối diện A,B,C.\n2. Chọn hệ thức chứa dữ kiện và ẩn; thống nhất đơn vị góc.\n3. Tính và chọn giá trị độ dài dương.",
    """
Hai cạnh 3 cm, 4 cm tạo góc 60°. Tính cạnh đối góc 60°.
|
Theo cosin, cạnh cần tìm có bình phương 3²+4²−2×3×4×cos60°=13.
Độ dài bằng √13 cm.
|
√13 cm.
---
Tam giác có a=6 cm, góc A=30°. Tính bán kính ngoại tiếp.
|
a/sin A=2R nên 2R=6/(1/2)=12.
Suy ra R=6 cm.
|
6 cm.
---
Tính sin150°, cos120° và diện tích tam giác có hai cạnh 4,6 cm tạo góc 30°.
|
sin150°=sin30°=1/2; cos120°=−cos60°=−1/2.
Diện tích bằng 4×6×sin30°/2=6 cm².
|
1/2; −1/2; 6 cm².
""",
)
add(
    "vectors_plane",
    "Vectơ có hướng và độ dài; vectơ không có độ dài 0. Quy tắc tam giác AB+BC=AC; AB−AC=CB. Với u=(a;b), v=(c;d), cộng theo tọa độ và ku=(ka;kb). Vectơ AB=(x_B−x_A;y_B−y_A).",
    "1. Phân biệt vectơ với độ dài.\n2. Viết tọa độ hoặc dùng quy tắc nối điểm.\n3. Tính từng tọa độ, kiểm tra hướng.",
    """
A(1;2), B(4;6). Tìm vectơ AB và độ dài AB.
|
AB=(4−1;6−2)=(3;4).
Độ dài AB=√(3²+4²)=5.
|
AB=(3;4); độ dài 5.
---
u=(2;−1), v=(−3;4). Tính 2u+v.
|
2u=(4;−2).
2u+v=(4−3;−2+4)=(1;2).
|
(1;2).
---
Rút gọn vectơ AB+BC−AC.
|
Theo quy tắc tam giác, AB+BC=AC.
Hiệu AC−AC là vectơ không.
|
Vectơ không.
""",
)
add(
    "dot_product",
    "Tích vô hướng u·v=|u||v|cosθ, trong tọa độ phẳng là ac+bd. Với hai vectơ khác không, vuông góc khi tích vô hướng bằng 0. Góc giữa hai vectơ thuộc [0°;180°].",
    "1. Tính tích vô hướng và độ dài.\n2. Nếu tìm góc, chia tích cho tích hai độ dài khác 0.\n3. Lấy góc trong khoảng quy định.",
    """
u=(1;2), v=(3;4). Tính u·v.
|
Nhân các tọa độ tương ứng rồi cộng.
u·v=1×3+2×4=11.
|
11.
---
Tính góc giữa (1;0) và (1;1).
|
Tích vô hướng bằng 1, hai độ dài bằng 1 và √2.
cosθ=1/√2 nên θ=45°.
|
45°.
---
u=(2;1), v=(1;−2) có vuông góc không?
|
Cả hai vectơ khác không.
u·v=2×1+1×(−2)=0 nên vuông góc.
|
Có.
""",
)
add(
    "lines_plane",
    "Đường thẳng có vectơ pháp tuyến n=(a;b) khác không: ax+by+c=0. Qua M(x₀;y₀): a(x−x₀)+b(y−y₀)=0. Vectơ chỉ phương u vuông góc n. Khoảng cách M đến đường: |ax₀+by₀+c|/√(a²+b²).",
    "1. Xác định điểm và vectơ chỉ phương/pháp tuyến.\n2. Lập phương trình hoặc giải hệ khi tìm giao.\n3. Tính góc bằng trị tuyệt đối tích vô hướng của hai pháp tuyến, khoảng cách dùng công thức.",
    """
Viết đường thẳng qua (1;2), có pháp tuyến (2;−1).
|
2(x−1)−(y−2)=0.
Thu gọn được 2x−y=0; điểm (1;2) thỏa.
|
2x−y=0.
---
Tính khoảng cách từ O(0;0) đến 3x+4y−10=0.
|
Áp dụng công thức khoảng cách.
d=|−10|/√(9+16)=10/5=2.
|
2.
---
Tìm giao của x+y=3 và x−y=1.
|
Cộng hai phương trình được 2x=4 nên x=2.
Thay vào được y=1.
|
(2;1).
""",
)
add(
    "circle_coordinates",
    "Đường tròn tâm I(a;b), bán kính R>0 có phương trình (x−a)²+(y−b)²=R². Dạng x²+y²+Dx+Ey+F=0 có tâm (−D/2;−E/2), bán kính bình phương (D²+E²)/4−F, phải dương.",
    "1. Đưa về tổng hai bình phương hoặc đọc tâm, bán kính.\n2. Kiểm tra R²>0.\n3. Tiếp tuyến tại điểm trên đường tròn có pháp tuyến là bán kính nối tâm tới điểm.",
    """
Viết đường tròn tâm (1;−2), bán kính 3.
|
Thay a=1,b=−2,R=3 vào công thức.
Được (x−1)²+(y+2)²=9.
|
(x−1)²+(y+2)²=9.
---
Tìm tâm và bán kính của x²+y²−4x+6y−3=0.
|
Hoàn thành bình phương: (x−2)²+(y+3)²=16.
Tâm (2;−3), bán kính 4.
|
I(2;−3), R=4.
---
Tìm tiếp tuyến của x²+y²=25 tại M(3;4).
|
OM=(3;4) là pháp tuyến tiếp tuyến.
3(x−3)+4(y−4)=0, tức 3x+4y=25.
|
3x+4y=25.
""",
)
add(
    "conics",
    "Elip x²/a²+y²/b²=1 với a>b>0 có c²=a²−b². Hypebol x²/a²−y²/b²=1 có c²=a²+b². Parabol y²=2px, p>0, có tiêu điểm (p/2;0), đường chuẩn x=−p/2.",
    "1. Nhận đúng dấu và dạng chính tắc.\n2. Đọc a²,b² hoặc 2p, không nhầm với a,b,p.\n3. Tính tiêu điểm và kiểm tra điều kiện.",
    """
Tìm tiêu điểm của elip x²/25+y²/9=1.
|
a=5,b=3 nên c=√(25−9)=4.
Hai tiêu điểm trên trục Ox là (−4;0),(4;0).
|
(−4;0), (4;0).
---
Tìm tiêu điểm của hypebol x²/9−y²/16=1.
|
a=3,b=4 nên c=√(9+16)=5.
Hai tiêu điểm là (−5;0),(5;0).
|
(−5;0), (5;0).
---
Tìm tiêu điểm và đường chuẩn của y²=8x.
|
2p=8 nên p=4.
Tiêu điểm (2;0), đường chuẩn x=−2.
|
F(2;0); x=−2.
""",
)
add(
    "counting",
    "Quy tắc cộng dùng cho các lựa chọn loại trừ nhau; quy tắc nhân dùng cho các công đoạn liên tiếp. P_n=n!, A_n^k=n!/(n−k)!, C_n^k=n!/(k!(n−k)!), 0≤k≤n. Chỉnh hợp có thứ tự, tổ hợp không có thứ tự.",
    "1. Xác định lựa chọn theo công đoạn hay theo trường hợp.\n2. Xem có xét thứ tự và có lặp không.\n3. Chọn quy tắc/công thức, tránh đếm trùng.",
    """
Có 3 áo và 2 quần. Có bao nhiêu cách chọn một bộ gồm một áo, một quần?
|
Mỗi áo đi với 2 quần; hai công đoạn độc lập về lựa chọn.
Số cách là 3×2=6.
|
6 cách.
---
Chọn 2 bạn từ 5 bạn để cùng làm một nhiệm vụ, không phân vai. Có bao nhiêu cách?
|
Không xét thứ tự nên dùng tổ hợp.
C_5^2=5×4/2=10.
|
10 cách.
---
Chọn lớp trưởng và lớp phó từ 5 bạn, mỗi bạn một vai. Có bao nhiêu cách? Xếp cả 5 bạn thành hàng có bao nhiêu cách?
|
Hai vai khác nhau nên có 5×4=20 cách phân vai.
Xếp cả 5 bạn là hoán vị: 5!=120 cách.
|
20 cách; 120 cách.
""",
)
add(
    "binomial",
    "Nhị thức Newton: (a+b)^n=Σ C_n^k a^(n−k)b^k, k từ 0 đến n với n nguyên không âm. Khi có dấu trừ, thay b bằng số âm và giữ dấu từng lũy thừa.",
    "1. Xác định a,b,n.\n2. Viết hạng tổng quát hoặc các hệ số nhị thức.\n3. Chọn hạng có số mũ cần tìm; kiểm tra dấu.",
    """
Khai triển (x+1)^3.
|
Các hệ số là 1,3,3,1.
(x+1)^3=x³+3x²+3x+1.
|
x³+3x²+3x+1.
---
Tìm hệ số x² trong (x+2)^4.
|
Hạng tổng quát C_4^k x^(4−k)2^k; cần 4−k=2 nên k=2.
Hệ số C_4^2×2²=6×4=24.
|
24.
---
Tìm hệ số x trong (1−x)^3.
|
Khai triển: 1−3x+3x²−x³.
Hệ số của x là −3.
|
−3.
""",
)
add(
    "trig_angles",
    "Độ và radian: 180°=π rad. Góc cùng tia cuối sai khác 2kπ. sin²x+cos²x=1; sin(a+b)=sin a cos b+cos a sin b; cos(a+b)=cos a cos b−sin a sin b. Công thức nhân đôi suy ra khi a=b.",
    "1. Thống nhất đơn vị góc.\n2. Đưa về góc đặc biệt hoặc áp dụng công thức phù hợp.\n3. Kiểm tra góc phần tư để chọn dấu.",
    """
Đổi 450° sang radian và tính sin450°.
|
450°=450π/180=5π/2.
450° cùng tia cuối với 90° nên sin450°=1.
|
5π/2 rad; sin=1.
---
Tính sin75°.
|
75°=45°+30°; áp dụng công thức cộng.
sin75°=(√2/2)(√3/2)+(√2/2)(1/2)=(√6+√2)/4.
|
(√6+√2)/4.
---
Cho sinα=3/5, 0<α<π/2. Tính cosα và cos2α.
|
cosα>0, cosα=√(1−9/25)=4/5.
cos2α=1−2sin²α=1−18/25=7/25.
|
cosα=4/5; cos2α=7/25.
""",
)
add(
    "trig_functions",
    "sin x, cos x xác định trên R, có chu kì 2π và giá trị trong [−1;1]. tan x loại x=π/2+kπ, chu kì π; cot x loại x=kπ, chu kì π. Đối số lượng giác trong các quy tắc này dùng radian.",
    "1. Xác định điểm bị loại nếu có mẫu sin/cos.\n2. Dùng miền giá trị cơ bản và hệ số để tìm miền giá trị mới.\n3. Chu kì của sin(ax+b), cos(ax+b) là 2π/|a| khi a≠0.",
    """
Tìm tập giá trị của y=2sin x−1.
|
−1≤sin x≤1 nên −2≤2sin x≤2.
Trừ 1 được −3≤y≤1; hai đầu đều đạt.
|
[−3;1].
---
Tìm tập xác định của y=tan x.
|
Cần cos x≠0.
Loại x=π/2+kπ với k nguyên.
|
R bỏ các số π/2+kπ, k∈Z.
---
Tìm chu kì cơ bản của y=sin2x.
|
Hệ số của x là 2.
Chu kì cơ bản T=2π/2=π.
|
π.
""",
)
add(
    "trig_equations",
    "sin x=sinα: x=α+2kπ hoặc x=π−α+2kπ. cos x=cosα: x=±α+2kπ. tan x=tanα: x=α+kπ tại các điểm xác định. k luôn là số nguyên.",
    "1. Kiểm tra điều kiện và miền giá trị vế phải.\n2. Đưa về giá trị góc đặc biệt hoặc dùng góc phụ trợ.\n3. Viết đủ các họ nghiệm, rút theo khoảng nếu đề yêu cầu.",
    """
Giải sin x=1/2 trên R.
|
sin(π/6)=1/2.
Hai họ nghiệm là x=π/6+2kπ hoặc x=5π/6+2kπ.
|
x=π/6+2kπ hoặc 5π/6+2kπ, k∈Z.
---
Giải cos2x=0.
|
2x=π/2+kπ.
Chia 2: x=π/4+kπ/2.
|
x=π/4+kπ/2, k∈Z.
---
Giải tan x=1 trên [0;2π).
|
Nghiệm tổng quát x=π/4+kπ.
Trong khoảng đã cho có π/4 và 5π/4.
|
π/4; 5π/4.
""",
)
add(
    "sequences",
    "Dãy số là hàm trên các số nguyên dương (hoặc tập chỉ số được quy định). Số hạng u_n khác tổng S_n=u₁+...+u_n. Cấp số cộng: u_n=u₁+(n−1)d, S_n=n(u₁+u_n)/2. Cấp số nhân: u_n=u₁q^(n−1), S_n=u₁(1−q^n)/(1−q) khi q≠1; q=1 thì S_n=nu₁.",
    "1. Xác định cách cho dãy và chỉ số đầu.\n2. Kiểm tra hiệu không đổi hoặc tỉ số không đổi (khi mẫu khác 0).\n3. Phân biệt tìm số hạng và tổng.",
    """
Cho u_n=2n+1, n≥1. Tính u₁,u₃ và xét tăng giảm.
|
u₁=3, u₃=7.
u_(n+1)−u_n=2>0 nên dãy tăng.
|
u₁=3; u₃=7; dãy tăng.
---
Cấp số cộng có u₁=3, d=2. Tính u₁₀ và S₁₀.
|
u₁₀=3+9×2=21.
S₁₀=10×(3+21)/2=120.
|
u₁₀=21; S₁₀=120.
---
Cấp số nhân có u₁=2, q=3. Tính u₄ và S₄.
|
u₄=2×3³=54.
S₄=2(1−3⁴)/(1−3)=80.
|
u₄=54; S₄=80.
""",
)
add(
    "grouped_statistics",
    "Mẫu ghép nhóm được xấp xỉ bằng giá trị đại diện là trung điểm nhóm. Trung bình x̄=(Σnᵢxᵢ)/n. Tứ phân vị trong nhóm [L;L+h) nội suy Q_p=L+(pn−N_trước)h/n_nhóm, với p=1/4,1/2,3/4. Đây là ước lượng từ bảng ghép nhóm.",
    "1. Lập tần số tích lũy và giá trị đại diện.\n2. Tìm nhóm chứa vị trí pn.\n3. Dùng đúng tần số nhóm, độ rộng nhóm và n; nêu tính gần đúng.",
    """
Hai nhóm [0;10), [10;20) có tần số 2,2. Tính trung bình ghép nhóm.
|
Giá trị đại diện là 5,15; cỡ mẫu 4.
Trung bình xấp xỉ (2×5+2×15)/4=10.
|
Khoảng 10.
---
Ba nhóm [0;10),[10;20),[20;30) có tần số 2,4,2. Tìm trung vị ghép nhóm.
|
n=8, n/2=4; nhóm giữa chứa vị trí 4, có L=10,h=10,N_trước=2,n_nhóm=4.
Trung vị xấp xỉ 10+(4−2)×10/4=15.
|
Khoảng 15.
---
Với ba nhóm tần số 2,4,2 trên, tìm Q₁,Q₃ và khoảng tứ phân vị.
|
Vị trí 2 và 6 nằm ở ranh giới nhóm; nội suy cho Q₁=10, Q₃=20.
Khoảng tứ phân vị bằng 20−10=10.
|
Q₁≈10; Q₃≈20; ΔQ≈10.
""",
)
add(
    "space_parallel",
    "Hai đường trong không gian có thể cắt, song song, chéo nhau hoặc trùng. Đường d không thuộc mặt phẳng (P) và song song một đường trong (P) thì d song song (P). Hai mặt phẳng có hai cặp đường cắt nhau tương ứng song song thì song song. Phép chiếu song song bảo toàn tính thẳng hàng và tỉ số trên cùng đường khi hình chiếu không suy biến.",
    "1. Vẽ và ghi rõ các điểm thuộc mặt phẳng nào.\n2. Chọn dấu hiệu, kiểm tra điều kiện không thuộc hoặc hai đường cắt nhau.\n3. Không suy quan hệ không gian chỉ từ hình nhìn trên giấy.",
    """
Trong hình hộp ABCD.A′B′C′D′, chứng minh AB song song mặt phẳng A′B′C′D′.
|
AB song song A′B′ và A′B′ nằm trong mặt phẳng trên.
AB không nằm trong mặt phẳng trên nên AB song song mặt phẳng đó.
|
AB ∥ (A′B′C′D′).
---
Trong hình hộp trên, giải thích vì sao hai mặt đáy song song.
|
AB,AD cắt nhau tại A; A′B′,A′D′ cắt nhau tại A′.
Hai cặp cạnh tương ứng song song nên hai mặt phẳng đáy song song.
|
(ABCD) ∥ (A′B′C′D′).
---
Phép chiếu song song biến đoạn AB thành đoạn A′B′ không suy biến. M là trung điểm AB. Ảnh M′ ở đâu?
|
Phép chiếu song song bảo toàn tỉ số trên đường thẳng không bị chiếu thành điểm.
AM/MB=1 nên A′M′/M′B′=1 và M′ thuộc đoạn A′B′.
|
M′ là trung điểm A′B′.
""",
)
add(
    "space_perpendicular",
    "Một đường vuông góc hai đường cắt nhau trong mặt phẳng thì vuông góc mặt phẳng đó. Hai mặt phẳng vuông góc nếu một mặt chứa đường vuông góc mặt kia. Góc đường–mặt phẳng là góc với hình chiếu vuông góc, thuộc [0°;90°]. Khoảng cách điểm–mặt phẳng là độ dài đường vuông góc.",
    "1. Xác định chân chiếu và hai đường cắt nhau để kiểm tra vuông góc.\n2. Dùng tam giác vuông hoặc định nghĩa góc, khoảng cách.\n3. Nêu rõ độ dài nào đang tính.",
    """
Hình lập phương ABCD.A′B′C′D′ cạnh 2 cm. Chứng minh AB vuông góc mặt phẳng ADD′A′.
|
AB vuông góc AD và AA′; hai đường này cắt nhau tại A và nằm trong mặt phẳng ADD′A′.
Theo dấu hiệu, AB vuông góc mặt phẳng ADD′A′.
|
AB ⟂ (ADD′A′).
---
Với hình lập phương cạnh 2 cm trên, tính khoảng cách từ A′ đến (ABCD).
|
A′A vuông góc với hai cạnh AB,AD của mặt đáy nên vuông góc mặt đáy.
A là chân chiếu, khoảng cách là A′A=2 cm.
|
2 cm.
---
Tìm sin của góc giữa đường chéo AC′ và mặt đáy lập phương cạnh 2 cm.
|
Hình chiếu AC′ lên đáy là AC. AC′=2√3, CC′=2.
Trong tam giác vuông ACC′, sin góc giữa AC′ và AC bằng CC′/AC′=1/√3.
|
1/√3.
""",
)
add(
    "limits_sequence",
    "1/n→0 khi n→∞; q^n→0 nếu |q|<1. Tổng, tích, thương có giới hạn theo quy tắc khi các giới hạn hữu hạn và mẫu giới hạn khác 0. Với biểu thức chứa n lớn, chia theo bậc cao nhất hoặc nhân liên hợp.",
    "1. Nhận dạng hữu tỉ, căn hay lũy thừa.\n2. Chia bậc cao nhất hoặc liên hợp, không coi ∞ là số thực.\n3. Dùng giới hạn cơ bản và điều kiện.",
    """
Tính giới hạn (2n+1)/(n+3) khi n→∞.
|
Chia tử và mẫu cho n: (2+1/n)/(1+3/n).
Giới hạn bằng 2/1=2.
|
2.
---
Tính giới hạn √(n²+n)−n khi n→∞.
|
Nhân liên hợp được n/(√(n²+n)+n)=1/(√(1+1/n)+1).
Giới hạn bằng 1/2.
|
1/2.
---
Tính giới hạn 3(1/2)^n+1/n khi n→∞.
|
Vì |1/2|<1 nên (1/2)^n→0; 1/n→0.
Giới hạn tổng bằng 3×0+0=0.
|
0.
""",
)
add(
    "limits_continuity",
    "Giới hạn hai phía tồn tại khi hai giới hạn một phía cùng tồn tại và bằng nhau. Hàm liên tục tại x₀ khi có giá trị f(x₀) và lim f(x)=f(x₀). Không thay trực tiếp nếu xuất hiện dạng 0/0; cần biến đổi trước.",
    "1. Kiểm tra tập xác định và dạng khi thay giá trị.\n2. Khử dạng chưa xác định bằng biến đổi hợp lệ ở lân cận.\n3. So hai phía và giá trị hàm khi xét liên tục.",
    """
Tính lim (x²−1)/(x−1) khi x→1.
|
Với x≠1, rút gọn biểu thức thành x+1.
Giới hạn bằng 2.
|
2.
---
Cho f(x)=(x²−1)/(x−1) khi x≠1 và f(1)=k. Tìm k để liên tục tại 1.
|
Giới hạn của nhánh khi x→1 bằng 2.
Cần f(1)=k=2 để bằng giới hạn.
|
k=2.
---
Hàm f(x)=1/x có giới hạn hữu hạn khi x→0 không?
|
Khi x→0+, 1/x→+∞; khi x→0−, 1/x→−∞.
Hai phía khác nhau nên không có giới hạn hai phía hữu hạn tại 0.
|
Không.
""",
)
add(
    "real_powers",
    "Với cơ số a>0, lũy thừa số mũ thực tuân theo a^x a^y=a^(x+y), (a^x)^y=a^(xy). a^(m/n)=ⁿ√(a^m), n nguyên dương. Số mũ âm cho nghịch đảo; không dùng mọi công thức cơ số dương cho cơ số âm và số mũ thực tùy ý.",
    "1. Kiểm tra cơ số và loại số mũ.\n2. Đưa về cơ số quen thuộc hoặc căn.\n3. Tính và giữ điều kiện.",
    """
Tính 8^(2/3).
|
Căn bậc ba của 8 là 2.
8^(2/3)=2²=4.
|
4.
---
Tính 2^(−3).
|
Số mũ âm cho nghịch đảo: 2^(−3)=1/2³.
2³=8 nên kết quả 1/8.
|
1/8.
---
Rút gọn a^(1/2) × a^(3/2) với a>0.
|
Cùng cơ số, cộng số mũ: 1/2+3/2=2.
Tích bằng a².
|
a², a>0.
""",
)
add(
    "logarithms",
    "log_a b=c khi a^c=b, với a>0,a≠1,b>0. log_a(uv)=log_a u+log_a v; log_a(u/v)=log_a u−log_a v cho u,v>0. Hàm a^x tăng nếu a>1, giảm nếu 0<a<1; log_a x có cùng chiều tương ứng trên (0;+∞).",
    "1. Ghi điều kiện cơ số, biểu thức trong log.\n2. Đổi về lũy thừa hoặc dùng công thức đúng điều kiện.\n3. Xét chiều tăng/giảm trước khi biến đổi bất phương trình.",
    """
Tính log_2 8.
|
Cần tìm số c sao cho 2^c=8.
Vì 2³=8 nên log_2 8=3.
|
3.
---
Tìm tập xác định y=log_3(x−1).
|
Điều kiện x−1>0.
Suy ra x>1.
|
(1;+∞).
---
Hàm y=(1/2)^x tăng hay giảm? Hàm y=log_2 x thì sao?
|
Cơ số 1/2 trong (0;1) nên hàm mũ giảm trên R.
Cơ số 2>1 nên log_2 x tăng trên (0;+∞).
|
Hàm mũ giảm; hàm log tăng trên các miền đã nêu.
""",
)
add(
    "exp_log_equations",
    "Phương trình mũ có thể đưa về cùng cơ số dương khác 1 rồi so số mũ. Phương trình log cần biểu thức trong log dương. Bất phương trình đổi chiều khi cơ số trong (0;1).",
    "1. Đặt điều kiện.\n2. Đưa hai vế về cùng cơ số hoặc cùng log.\n3. Giải, giao điều kiện và thử lại.",
    """
Giải 2^x=8.
|
8=2³, cơ số 2 dương khác 1.
So số mũ được x=3.
|
x=3.
---
Giải log_2(x−1)≥2.
|
Điều kiện x>1; viết 2=log_2 4.
Cơ số 2>1 nên x−1≥4, tức x≥5, đã thỏa điều kiện.
|
x≥5.
---
Giải (1/2)^x>1/4.
|
1/4=(1/2)².
Vì cơ số trong (0;1), đổi chiều khi so số mũ, được x<2.
|
x<2.
""",
)
add(
    "derivative",
    "Đạo hàm tại x₀ là giới hạn [f(x₀+h)−f(x₀)]/h khi h→0 nếu tồn tại. Nó là hệ số góc tiếp tuyến; tiếp tuyến y=f′(x₀)(x−x₀)+f(x₀). Nếu s(t) là quãng tọa độ, vận tốc tức thời v(t)=s′(t).",
    "1. Lập tỉ số sai phân hoặc chọn quy tắc đạo hàm đã học.\n2. Tính tại điểm được yêu cầu, kiểm tra tồn tại.\n3. Diễn giải đúng tiếp tuyến hoặc đơn vị vận tốc.",
    """
Dùng định nghĩa tính đạo hàm của f(x)=x².
|
[f(x+h)−f(x)]/h=[2xh+h²]/h=2x+h với h≠0.
Cho h→0, được f′(x)=2x.
|
f′(x)=2x.
---
Viết tiếp tuyến y=x² tại x=1.
|
f(1)=1, f′(1)=2.
Tiếp tuyến y=2(x−1)+1=2x−1.
|
y=2x−1.
---
Vật có tọa độ s(t)=3t² mét, t giây. Tính vận tốc tại t=2.
|
v(t)=s′(t)=6t m/s.
v(2)=12 m/s.
|
12 m/s.
""",
)
add(
    "derivative_rules",
    "(x^n)′=nx^(n−1) tại các điểm xác định; (u+v)′=u′+v′, (uv)′=u′v+uv′, (u/v)′=(u′v−uv′)/v² với v≠0. (sin x)′=cos x theo radian; (e^x)′=e^x, (ln x)′=1/x với x>0. Hàm hợp nhân thêm đạo hàm hàm bên trong.",
    "1. Xác định tập xác định và dạng tổng/tích/thương/hợp.\n2. Áp dụng quy tắc, giữ đủ các hạng và dấu.\n3. Thu gọn và ghi điều kiện.",
    """
Tính đạo hàm f(x)=x³−3x.
|
Đạo hàm từng hạng: (x³)′=3x², (−3x)′=−3.
Suy ra f′(x)=3x²−3.
|
3x²−3.
---
Tính đạo hàm (x+1)/(x−1).
|
Điều kiện x≠1; tử đạo hàm thương là (x−1)−(x+1)=−2.
Đạo hàm bằng −2/(x−1)².
|
−2/(x−1)², x≠1.
---
Tính đạo hàm sin(2x) và e^x+ln x.
|
Dùng hàm hợp: (sin2x)′=2cos2x, x∈R.
Với x>0, (e^x+ln x)′=e^x+1/x.
|
2cos2x; e^x+1/x (x>0).
""",
)
add(
    "second_derivative",
    "Đạo hàm cấp hai f″ là đạo hàm của f′ tại các điểm tồn tại. Trong chuyển động, gia tốc là đạo hàm của vận tốc: a(t)=s″(t). Không bình phương đạo hàm để lấy cấp hai.",
    "1. Tính f′.\n2. Đạo hàm lần nữa trên miền xác định.\n3. Thay giá trị và ghi đơn vị nếu có.",
    """
Tính đạo hàm cấp hai của x⁴.
|
f′(x)=4x³.
f″(x)=12x².
|
12x².
---
s(t)=t³ mét, t giây. Tính gia tốc lúc t=2.
|
v(t)=3t²; a(t)=6t.
a(2)=12 m/s².
|
12 m/s².
---
f(x)=sin x, x tính radian. Tìm f″.
|
f′(x)=cos x.
Đạo hàm của cos x là −sin x nên f″(x)=−sin x.
|
−sin x.
""",
)
add(
    "monotonicity",
    "Trên một khoảng, f′>0 suy ra đồng biến, f′<0 suy ra nghịch biến. Cực trị xảy ra khi đạo hàm đổi dấu (hoặc điểm không có đạo hàm được xét riêng), không phải mọi nghiệm f′=0 đều là cực trị. Khảo sát gồm tập xác định, đạo hàm, giới hạn, bảng biến thiên và các điểm đặc trưng để vẽ.",
    "1. Tìm tập xác định và các điểm phân chia xét dấu.\n2. Lập dấu f′, suy chiều biến thiên và cực trị.\n3. Tính giá trị tại điểm đặc biệt, giới hạn và phác đồ thị đúng hình dạng.",
    """
Khảo sát chiều biến thiên và cực trị f(x)=x³−3x.
|
Tập xác định R; f′=3(x−1)(x+1), dương ngoài [−1;1], âm trong (−1;1).
Hàm tăng trên (−∞;−1),(1;+∞), giảm trên (−1;1).
f(−1)=2 là cực đại; f(1)=−2 là cực tiểu. Giới hạn ở −∞ là −∞, ở +∞ là +∞; đồ thị đi qua O và đối xứng tâm O.
|
Cực đại tại (−1;2), cực tiểu tại (1;−2); các khoảng biến thiên như trên.
---
f(x)=x³ có cực trị tại 0 không?
|
f′=3x², bằng 0 tại 0 nhưng dương ở hai phía.
Đạo hàm không đổi dấu; hàm tăng qua 0 nên không có cực trị tại đó.
|
Không.
---
Với y=x²−4x+3, nêu bảng biến thiên bằng lời và các giao trục để vẽ đồ thị.
|
f′=2x−4: âm khi x<2, dương khi x>2; hàm giảm tới −1 rồi tăng.
Đỉnh (2;−1), giao Ox tại (1;0),(3;0), giao Oy tại (0;3); trục đối xứng x=2, parabol mở lên.
|
Dùng đỉnh, giao trục và chiều biến thiên đã nêu để vẽ parabol.
""",
)
add(
    "optimization",
    "Tìm giá trị lớn/nhỏ trên đoạn: xét điểm tới hạn trong đoạn và hai đầu mút. Bài toán thực tế cần mô hình và miền biến phù hợp, sau đó dùng đạo hàm hoặc bất đẳng thức; không lấy nghiệm ngoài miền.",
    "1. Đặt biến, điều kiện và hàm mục tiêu.\n2. Tìm điểm tới hạn.\n3. So các giá trị hợp lệ và biên, diễn giải đáp số.",
    """
Tìm max, min của f(x)=x²−4x+3 trên [0;3].
|
f′=2x−4=0 tại x=2 trong đoạn.
f(0)=3,f(2)=−1,f(3)=0; so sánh các giá trị.
|
Max 3 tại 0; min −1 tại 2.
---
Hình chữ nhật chu vi 20 m. Tìm diện tích lớn nhất.
|
Gọi một cạnh x, cạnh kia 10−x với 0<x<10; S=x(10−x).
S′=10−2x đổi từ dương sang âm tại x=5 nên max S=25 m².
|
25 m², khi hình vuông cạnh 5 m.
---
Lợi nhuận mô hình P(x)=−x²+12x−20, 0≤x≤10. Tìm x cho lợi nhuận lớn nhất.
|
P′=−2x+12=0 tại x=6, nằm trong miền.
P(0)=−20,P(6)=16,P(10)=0 nên lớn nhất tại 6.
|
x=6; lợi nhuận mô hình bằng 16 đơn vị tiền đã chọn.
""",
)
add(
    "asymptotes",
    "x=a là tiệm cận đứng nếu ít nhất một giới hạn một phía ở a vô cực. y=L là tiệm cận ngang nếu f(x)→L khi x→+∞ hoặc −∞. y=ax+b là tiệm cận xiên nếu f(x)−(ax+b)→0 khi x ra vô cực, a≠0.",
    "1. Xác định miền và các điểm mẫu bằng 0.\n2. Tính giới hạn tại điểm và vô cực, không coi mọi nghiệm mẫu là tiệm cận.\n3. Dùng chia đa thức để tìm phần tuyến tính nếu có.",
    """
Tìm tiệm cận của f(x)=(2x+1)/(x−1).
|
f(x)=2+3/(x−1), x≠1.
Khi x→1 có giới hạn vô cực; khi x→±∞, f→2.
|
Tiệm cận đứng x=1; ngang y=2.
---
Tìm tiệm cận của f(x)=x+1+1/(x−2).
|
Tại x=2, số hạng 1/(x−2) vô cực nên x=2 là tiệm cận đứng.
f(x)−(x+1)=1/(x−2)→0 khi x→±∞.
|
x=2; tiệm cận xiên y=x+1.
---
Hàm (x²−1)/(x−1) có tiệm cận đứng x=1 không?
|
Với x≠1, hàm bằng x+1 nên giới hạn tại 1 là 2, hữu hạn.
Điểm bị khuyết không tạo tiệm cận đứng.
|
Không.
""",
)
add(
    "vectors_space",
    "Trong Oxyz, AB=(x_B−x_A;y_B−y_A;z_B−z_A). Cộng vectơ và nhân số theo từng tọa độ. |u|=√(u₁²+u₂²+u₃²); u·v=u₁v₁+u₂v₂+u₃v₃. Hai vectơ khác không vuông góc khi tích vô hướng bằng 0.",
    "1. Viết đủ ba tọa độ theo đúng thứ tự.\n2. Trừ điểm cuối–đầu hoặc tính từng tọa độ.\n3. Dùng độ dài/tích vô hướng nếu tìm khoảng cách, góc.",
    """
A(1;2;3),B(3;1;5). Tìm AB và độ dài.
|
AB=(2;−1;2).
|AB|=√(4+1+4)=3.
|
AB=(2;−1;2), độ dài 3.
---
u=(1;2;−1),v=(2;0;3). Tính 2u−v và u·v.
|
2u−v=(2;4;−2)−(2;0;3)=(0;4;−5).
u·v=1×2+2×0+(−1)×3=−1.
|
(0;4;−5); −1.
---
Tìm trung điểm đoạn nối A(0;2;4), B(2;4;6).
|
Tọa độ trung điểm là trung bình cộng từng cặp tọa độ.
M=((0+2)/2;(2+4)/2;(4+6)/2)=(1;3;5).
|
M(1;3;5).
""",
)
add(
    "planes_space",
    "Mặt phẳng có pháp tuyến n=(A;B;C) khác không: Ax+By+Cz+D=0. Qua M₀(x₀;y₀;z₀): A(x−x₀)+B(y−y₀)+C(z−z₀)=0. Khoảng cách M đến mặt phẳng là |Ax_M+By_M+Cz_M+D|/√(A²+B²+C²).",
    "1. Xác định pháp tuyến khác không và điểm đi qua.\n2. Lập phương trình rồi thu gọn.\n3. Khi tính khoảng cách, lấy trị tuyệt đối tử.",
    """
Viết mặt phẳng qua (1;2;3), pháp tuyến (2;−1;2).
|
Phương trình: 2(x−1)−(y−2)+2(z−3)=0.
Thu gọn 2x−y+2z−6=0.
|
2x−y+2z−6=0.
---
Tính khoảng cách từ O tới mặt phẳng 2x−y+2z−6=0.
|
Tử là |−6|=6; mẫu √(4+1+4)=3.
d=6/3=2.
|
2.
---
M(1;0;2) có thuộc mặt phẳng x+2y−z+1=0 không?
|
Thay tọa độ: 1+0−2+1=0.
Điểm thỏa phương trình nên thuộc mặt phẳng.
|
Có.
""",
)
add(
    "lines_space",
    "Đường thẳng qua M₀(x₀;y₀;z₀), chỉ phương u=(a;b;c) khác không có tham số x=x₀+at,y=y₀+bt,z=z₀+ct. Dạng chính tắc chỉ viết các phân thức khi các mẫu tương ứng khác 0; nếu một thành phần bằng 0 thì tọa độ đó cố định.",
    "1. Xác định điểm và chỉ phương.\n2. Lập tham số; khi tìm giao mặt phẳng thì thay vào phương trình mặt.\n3. Giải tham số, đối chiếu đủ ba tọa độ.",
    """
Viết đường thẳng qua (1;2;3) có chỉ phương (2;−1;1).
|
Dùng x=x₀+at và tương tự cho y,z.
x=1+2t,y=2−t,z=3+t, t∈R.
|
(x;y;z)=(1+2t;2−t;3+t).
---
M(3;1;4) có thuộc đường thẳng trên không?
|
Từ x=3 suy ra t=1.
Với t=1, y=1,z=4 đều đúng.
|
Có, t=1.
---
Tìm giao của đường thẳng trên với mặt phẳng z=5.
|
3+t=5 nên t=2.
x=5,y=0,z=5.
|
(5;0;5).
""",
)
add(
    "angles_space",
    "Góc hai đường thẳng: cosθ=|u·v|/(|u||v|), θ∈[0;90°]. Góc hai mặt phẳng dùng hai pháp tuyến và công thức tương tự. Góc đường–mặt: sinα=|u·n|/(|u||n|), α∈[0;90°]. Các vectơ dùng đều khác không.",
    "1. Chọn đúng chỉ phương hoặc pháp tuyến.\n2. Tính tích vô hướng và độ dài.\n3. Phân biệt công thức sin của đường–mặt với cos của hai đường/hai mặt.",
    """
Tính góc hai đường có chỉ phương (1;0;0), (1;1;0).
|
Tích vô hướng bằng 1, tích độ dài bằng √2.
cosθ=1/√2 nên θ=45°.
|
45°.
---
Tính góc đường chỉ phương (0;0;1) với mặt phẳng z=0.
|
Pháp tuyến mặt là (0;0;1).
sinα=1 nên α=90°.
|
90°.
---
Tính góc hai mặt phẳng x=0 và y=0.
|
Pháp tuyến là (1;0;0),(0;1;0), tích vô hướng bằng 0.
cosθ=0 nên θ=90°.
|
90°.
""",
)
add(
    "sphere_coordinates",
    "Mặt cầu tâm I(a;b;c), bán kính R>0: (x−a)²+(y−b)²+(z−c)²=R². Hoàn thành bình phương từ dạng khai triển; nếu R²≤0 thì không phải mặt cầu bán kính dương. Tiếp diện tại điểm trên cầu vuông góc bán kính tại đó.",
    "1. Đưa về tổng ba bình phương hoặc đọc tâm, bán kính.\n2. Kiểm tra R²>0.\n3. Muốn tiếp diện, dùng vectơ nối tâm tới tiếp điểm làm pháp tuyến.",
    """
Viết mặt cầu tâm (1;−2;3), bán kính 4.
|
Thay tâm và bán kính vào công thức.
(x−1)²+(y+2)²+(z−3)²=16.
|
(x−1)²+(y+2)²+(z−3)²=16.
---
Tìm tâm, bán kính của x²+y²+z²−2x+4y−6z−2=0.
|
Hoàn thành bình phương được (x−1)²+(y+2)²+(z−3)²=16.
Tâm (1;−2;3), bán kính 4.
|
I(1;−2;3), R=4.
---
Tìm tiếp diện mặt cầu trên tại M(1;−2;7).
|
IM=(0;0;4) là pháp tuyến; M nằm trên cầu vì IM=4.
Tiếp diện 4(z−7)=0, tức z=7.
|
z=7.
""",
)
add(
    "antiderivative",
    "F là nguyên hàm của f trên một khoảng nếu F′=f. Mọi nguyên hàm trên khoảng đó khác nhau một hằng số C. ∫x^n dx=x^(n+1)/(n+1)+C với n≠−1 ở miền có nghĩa; ∫1/x dx=ln|x|+C trên từng khoảng không chứa 0.",
    "1. Xác định miền và dạng hàm.\n2. Dùng bảng nguyên hàm hoặc thay biến phù hợp.\n3. Thêm hằng số C và lấy đạo hàm để kiểm tra.",
    """
Tìm nguyên hàm của 2x.
|
Một hàm có đạo hàm bằng 2x là x².
Họ nguyên hàm là x²+C.
|
x²+C.
---
Tìm nguyên hàm sin2x trên R.
|
Vì (cos2x)′=−2sin2x nên chia hệ số −2.
Nguyên hàm là −cos2x/2+C; đạo hàm trở lại sin2x.
|
−cos2x/2+C.
---
Tìm nguyên hàm 1/x trên khoảng (0;+∞).
|
Với x>0, (ln x)′=1/x.
Họ nguyên hàm là ln x+C trên khoảng đã cho.
|
ln x+C.
""",
)
add(
    "integral",
    "Nếu F′=f liên tục trên [a;b] thì ∫_a^b f(x)dx=F(b)−F(a). Đổi cận làm đổi dấu, hai cận bằng nhau cho 0. Tích phân xác định là số, không thêm C ở đáp số.",
    "1. Xác định cận và tính liên tục/miền xác định.\n2. Tìm một nguyên hàm.\n3. Thay cận trên trừ cận dưới, kiểm tra dấu.",
    """
Tính ∫ từ 0 đến 1 của 3x² dx.
|
Nguyên hàm là x³.
Giá trị bằng 1³−0³=1.
|
1.
---
Tính ∫ từ 0 đến π của sin x dx.
|
Nguyên hàm là −cos x.
Giá trị −cosπ+cos0=1+1=2.
|
2.
---
Biết ∫ từ 2 đến 5 của f(x) dx bằng 7. Tính tích phân từ 5 đến 2.
|
Đổi cận làm đổi dấu tích phân.
Kết quả là −7.
|
−7.
""",
)
add(
    "integral_geometry",
    "Diện tích giữa hai đồ thị f,g trên [a;b] là ∫|f−g| dx; nếu đổi thứ tự trên khoảng thì tách tại giao điểm. Thể tích tròn xoay quanh Ox với bán kính f(x) liên tục là π∫f(x)² dx; vành tròn cần hiệu bình phương bán kính ngoài–trong.",
    "1. Tìm giao điểm, miền giới hạn và trục quay.\n2. Xác định dấu hoặc bán kính ngoài/trong.\n3. Lập tích phân, tính và ghi đơn vị diện tích/thể tích.",
    """
Tính diện tích giữa y=x và y=x² trên [0;1].
|
Trên [0;1], x≥x² nên S=∫(x−x²)dx.
S=[x²/2−x³/3] từ 0 tới 1 bằng 1/6.
|
1/6 đơn vị diện tích.
---
Quay miền 0≤y≤x, 0≤x≤1 quanh Ox. Tính thể tích.
|
Mỗi tiết diện có bán kính x nên V=π∫ từ 0 đến 1 của x² dx.
V=π/3.
|
π/3 đơn vị thể tích.
---
Tính diện tích giữa y=x−1 và trục Ox trên [0;2].
|
Hàm âm trên [0;1], dương trên [1;2] nên S=∫_0^1(1−x)dx+∫_1^2(x−1)dx.
Hai phần đều bằng 1/2 nên tổng là 1.
|
1 đơn vị diện tích.
""",
)
add(
    "probability_rules",
    "P(A∪B)=P(A)+P(B)−P(A∩B); xung khắc có giao rỗng. Nếu A,B độc lập thì P(A∩B)=P(A)P(B). Xung khắc khác độc lập; hai biến cố xung khắc có xác suất dương không độc lập.",
    "1. Xác định hợp/giao và quan hệ giữa biến cố.\n2. Chỉ nhân xác suất khi có giả thiết độc lập hoặc xác suất có điều kiện phù hợp.\n3. Kiểm tra kết quả trong [0;1].",
    """
P(A)=0,4; P(B)=0,3; P(A∩B)=0,1. Tính P(A∪B).
|
Dùng công thức cộng có trừ phần giao.
0,4+0,3−0,1=0,6.
|
0,6.
---
A,B độc lập, P(A)=1/2, P(B)=1/3. Tính xác suất cả hai.
|
Theo giả thiết độc lập, nhân hai xác suất.
P(A∩B)=1/2×1/3=1/6.
|
1/6.
---
Hai biến cố xung khắc có xác suất 0,2 và 0,5. Tính xác suất hợp; chúng độc lập không?
|
Giao có xác suất 0 nên hợp có xác suất 0,7.
Tích hai xác suất bằng 0,1 khác 0 nên không độc lập.
|
0,7; không độc lập.
""",
)
add(
    "conditional_bayes",
    "P(A|B)=P(A∩B)/P(B) khi P(B)>0. Với phân hoạch Bᵢ có xác suất dương, P(A)=ΣP(Bᵢ)P(A|Bᵢ). Bayes: P(Bⱼ|A)=P(Bⱼ)P(A|Bⱼ)/P(A), P(A)>0.",
    "1. Xác định biến cố đã biết và biến cố cần hỏi.\n2. Tính mẫu số bằng xác suất toàn phần nếu cần.\n3. Áp dụng đúng thứ tự điều kiện và kiểm tra mẫu dương.",
    """
P(A∩B)=0,2; P(B)=0,5. Tính P(A|B).
|
P(B)>0 nên công thức có nghĩa.
P(A|B)=0,2/0,5=0,4.
|
0,4.
---
Túi có 3 bi đỏ, 2 bi xanh. Lấy hai viên không hoàn lại; biết viên đầu đỏ. Xác suất viên sau đỏ?
|
Sau điều kiện viên đầu đỏ, còn 2 đỏ trong 4 viên.
Xác suất có điều kiện là 2/4=1/2.
|
1/2.
---
Máy A làm 60% sản phẩm với 1% lỗi, máy B làm 40% với 2% lỗi. Một sản phẩm được chọn ngẫu nhiên bị lỗi. Xác suất nó từ A?
|
P(lỗi)=0,6×0,01+0,4×0,02=0,014.
Theo Bayes, P(A|lỗi)=0,006/0,014=3/7.
|
3/7.
""",
)
add(
    "grouped_spread",
    "Với giá trị đại diện xᵢ, tần số nᵢ, phương sai ghép nhóm xấp xỉ s²=(Σnᵢ(xᵢ−x̄)²)/n; s=√s². Khoảng biến thiên của bảng ghép nhóm dùng hiệu cận trên nhóm cuối và cận dưới nhóm đầu, không khẳng định đó là chênh lệch chính xác của dữ liệu gốc.",
    "1. Tính n, các trung điểm nhóm và trung bình.\n2. Tính tổng bình phương độ lệch có trọng số.\n3. Chia n, lấy căn; ghi đây là đại lượng từ số liệu ghép nhóm.",
    """
Các nhóm [0;10),[10;20),[20;30) có tần số 2,4,2. Tính phương sai ghép nhóm.
|
Trung điểm 5,15,25; n=8, trung bình bằng 15.
s²=[2×100+4×0+2×100]/8=50.
|
s²≈50.
---
Với bảng trên, tính độ lệch chuẩn.
|
Phương sai ghép nhóm bằng 50.
s=√50=5√2.
|
s≈5√2.
---
Với bảng trên, tính khoảng biến thiên theo các cận nhóm.
|
Cận trên nhóm cuối 30, cận dưới nhóm đầu 0.
Khoảng biến thiên của bảng ghép nhóm là 30−0=30.
|
30; không phải chênh lệch chính xác đã biết của dữ liệu gốc.
""",
)
add(
    "decimal_signed",
    "Số thập phân âm tuân theo quy tắc dấu của số hữu tỉ. Cộng/trừ đặt dấu phẩy thẳng cột sau khi xử lí dấu; nhân theo số chữ số thập phân; chia chuyển dấu phẩy cả hai số cùng số hàng để số chia thành số tự nhiên.",
    "1. Tách bước xét dấu và bước tính giá trị.\n2. Tính với trị tuyệt đối đúng dấu phẩy.\n3. Gắn dấu, thử lại bằng phép tính ngược.",
    """
Tính −1,25+2,5.
|
Hai số trái dấu; lấy 2,50−1,25=1,25.
Số có trị tuyệt đối lớn hơn dương nên kết quả dương.
|
1,25.
---
Tính (−3,2)×(−0,5).
|
Hai thừa số âm nên tích dương.
3,2×0,5=1,6.
|
1,6.
---
Tính 5,4:(−0,3).
|
Thương âm; 5,4:0,3=54:3=18.
Gắn dấu âm được −18.
|
−18.
""",
)
add(
    "repeating_decimals",
    "Phân số tối giản có mẫu chỉ gồm thừa số nguyên tố 2,5 cho thập phân hữu hạn; có thừa số nguyên tố khác thì cho thập phân vô hạn tuần hoàn. Kí hiệu 0,(3) nghĩa 0,333...; phân biệt với số thập phân làm tròn 0,33.",
    "1. Rút gọn phân số.\n2. Phân tích mẫu hoặc thực hiện phép chia.\n3. Ghi đúng chu kì, không coi số làm tròn là bằng số ban đầu.",
    """
Viết 1/3 dưới dạng thập phân.
|
Chia 1 cho 3 được các chữ số 3 lặp vô hạn.
Vì vậy 1/3=0,(3), không bằng chính xác 0,33.
|
0,(3).
---
Phân số 7/20 có thập phân hữu hạn không? Viết dạng đó.
|
20=2²×5 chỉ có thừa số 2,5.
7/20=35/100=0,35.
|
Có; 0,35.
---
Đổi 0,(27) thành phân số.
|
Đặt x=0,272727... thì 100x=27,272727...
Trừ hai đẳng thức được 99x=27 nên x=27/99=3/11.
|
3/11.
""",
)
add(
    "equation_transform",
    "Phương trình tích bằng 0 khi ít nhất một thừa số bằng 0. Phương trình có ẩn ở mẫu phải đặt mẫu khác 0 trước quy đồng. Nghiệm thu được cần so điều kiện gốc vì rút gọn có thể làm mất điểm bị loại.",
    "1. Ghi điều kiện, phân tích nhân tử nếu cần.\n2. Đưa về phương trình bậc nhất hoặc phương trình tích.\n3. Kiểm tra từng nghiệm với điều kiện gốc.",
    """
Giải (x−1)(2x+3)=0.
|
x−1=0 hoặc 2x+3=0.
Suy ra x=1 hoặc x=−3/2.
|
x=1 hoặc −3/2.
---
Giải 1/(x−1)=2/(x+1).
|
Điều kiện x≠1,−1. Nhân chéo được x+1=2x−2.
x=3, thỏa điều kiện.
|
x=3.
---
Giải (x²−1)/(x−1)=3.
|
Điều kiện x≠1; rút gọn được x+1=3.
x=2 thỏa điều kiện; x=1 không được đưa vào tập nghiệm.
|
x=2.
""",
)
add(
    "volume_space",
    "Thể tích lăng trụ V=Bh; hình chóp V=Bh/3, B là diện tích đáy, h vuông góc đáy. Thể tích không dùng đường cao của mặt bên thay cho chiều cao khối.",
    "1. Chọn đáy thuận tiện và tìm chiều cao vuông góc.\n2. Tính diện tích đáy.\n3. Nhân với chiều cao, chia 3 nếu là chóp và ghi đơn vị khối.",
    """
Chóp có đáy tam giác vuông hai cạnh 3,4 cm, chiều cao 5 cm. Tính thể tích.
|
Diện tích đáy 3×4/2=6 cm².
Thể tích 6×5/3=10 cm³.
|
10 cm³.
---
Lăng trụ có đáy diện tích 12 m², cao 7 m. Tính thể tích.
|
Dùng V=Bh.
V=12×7=84 m³.
|
84 m³.
---
Hình chóp có thể tích 20 cm³, đáy diện tích 12 cm². Tính chiều cao.
|
Từ V=Bh/3 suy ra h=3V/B.
h=3×20/12=5 cm.
|
5 cm.
""",
)
add(
    "budget",
    "Lập kế hoạch chi tiêu cần xác định tiền có, khoản thiết yếu, khoản dự phòng; tổng chi không vượt ngân sách. Tỉ lệ một khoản bằng khoản đó chia tổng; đây là bài toán số học, không bảo đảm lợi nhuận đầu tư.",
    "1. Liệt kê khoản và đơn vị tiền.\n2. Tính tổng, số dư và tỉ lệ.\n3. Điều chỉnh nếu vượt ngân sách, kiểm tra đủ khoản.",
    """
Có 500 000 đồng, dự kiến chi 200 000 và 150 000 đồng. Còn bao nhiêu?
|
Tổng chi 200 000+150 000=350 000 đồng.
Số dư 500 000−350 000=150 000 đồng.
|
150 000 đồng.
---
Ngân sách 1 000 000 đồng, chi sách 250 000 đồng. Tỉ lệ chi sách bao nhiêu?
|
Tỉ lệ bằng 250 000/1 000 000=1/4.
Đổi ra phần trăm là 25%.
|
25%.
---
Có 300 000 đồng, kế hoạch chi 180 000, 90 000, 50 000 đồng. Có đủ không?
|
Tổng chi 320 000 đồng.
Vượt ngân sách 320 000−300 000=20 000 đồng nên phải giảm chi hoặc bổ sung nguồn hợp lệ.
|
Không đủ, thiếu 20 000 đồng.
""",
)
add(
    "compound_interest",
    "Lãi kép sau n kì, lãi suất r mỗi kì và không rút/nộp thêm: A=P(1+r)^n. r viết dạng số thập phân; n và r phải cùng đơn vị kì. Mô hình không tự tính thuế, phí hay rủi ro.",
    "1. Xác định vốn, lãi suất mỗi kì, số kì.\n2. Đổi phần trăm sang số thập phân.\n3. Tính giá trị theo mô hình và phân biệt tiền cuối với tiền lãi.",
    """
Gửi 1 000 000 đồng lãi kép 5%/năm trong 2 năm, không thêm/rút. Tính tiền cuối theo mô hình.
|
P=1 000 000, r=0,05, n=2.
A=1 000 000×1,05²=1 102 500 đồng.
|
1 102 500 đồng.
---
Vốn 1 000 000 đồng, lãi kép 1%/tháng trong 3 tháng. Tính tiền cuối.
|
r=0,01 mỗi tháng, n=3.
A=1 000 000×1,01³=1 030 301 đồng.
|
1 030 301 đồng.
---
Vốn 1 000, lãi 10% mỗi kì trong 2 kì. So lãi đơn và lãi kép.
|
Lãi đơn cho tiền cuối 1 000×(1+2×0,1)=1 200.
Lãi kép cho 1 000×1,1²=1 210, hơn 10 đơn vị tiền.
|
1 200 và 1 210; chênh 10.
""",
)
add(
    "finance_linear",
    "Chi phí gồm khoản cố định b và khoản a cho mỗi đơn vị dùng x thường được mô hình bằng C=ax+b. Điều kiện x≥0, thường là số nguyên. Mô hình chỉ áp dụng đúng bảng giá và miền đã cho.",
    "1. Xác định phí cố định và phí theo đơn vị.\n2. Lập hàm chi phí.\n3. Giải phương trình so sánh hoặc bất phương trình ngân sách, xét điều kiện nguyên.",
    """
Phí cố định 20 000 đồng, thêm 500 đồng mỗi phút. Dùng 30 phút trả bao nhiêu?
|
C(x)=20 000+500x với x≥0.
C(30)=20 000+15 000=35 000 đồng.
|
35 000 đồng.
---
Gói A: 10 000+1 000x, gói B: 20 000+500x (đồng). Dùng mấy phút thì bằng tiền?
|
Giải 10 000+1 000x=20 000+500x.
500x=10 000 nên x=20.
|
20 phút.
---
Với phí 20 000+500x, ngân sách 50 000 đồng, dùng tối đa mấy phút nguyên?
|
20 000+500x≤50 000 nên x≤60.
x nguyên không âm, lớn nhất là 60.
|
60 phút.
""",
)
add(
    "dilution",
    "Nồng độ phần trăm khối lượng = khối lượng chất tan/khối lượng dung dịch ×100%. Thêm nước tinh khiết giữ khối lượng chất tan, thay tổng khối lượng. Không dùng thể tích thay khối lượng khi chưa có giả thiết khối lượng riêng.",
    "1. Tính khối lượng chất tan ban đầu.\n2. Lập tổng khối lượng sau pha.\n3. Tính nồng độ mới, kiểm tra cân bằng chất tan.",
    """
Có 100 g dung dịch muối 20%, thêm 100 g nước. Tính nồng độ mới.
|
Chất tan có 100×20%=20 g.
Dung dịch mới 200 g nên nồng độ 20/200×100%=10%.
|
10%.
---
Muốn pha 200 g dung dịch muối 5% từ muối và nước, cần bao nhiêu mỗi loại?
|
Muối cần 200×5%=10 g.
Nước cần 200−10=190 g.
|
10 g muối, 190 g nước.
---
Trộn 100 g dung dịch muối 10% với 100 g dung dịch muối 20%. Nồng độ mới?
|
Chất tan tổng 10+20=30 g; khối lượng dung dịch 200 g.
Nồng độ 30/200×100%=15%.
|
15%.
""",
)
add(
    "gene_probability",
    "Mô hình một gen: A trội hoàn toàn so với a; trong phép lai Aa×Aa, mỗi bố mẹ cho giao tử A hoặc a với xác suất 1/2, độc lập. Bốn tổ hợp AA,Aa,aA,aa đồng khả năng; mô hình không dùng để kết luận mọi tính trạng thực đều như vậy.",
    "1. Ghi giả thiết trội hoàn toàn, giao tử đồng khả năng và độc lập.\n2. Liệt kê tổ hợp, phân loại kiểu gen/kiểu hình.\n3. Đếm kết quả thuận lợi hoặc dùng quy tắc nhân.",
    """
Trong mô hình Aa×Aa, xác suất kiểu hình trội là bao nhiêu?
|
Có bốn tổ hợp đồng khả năng: AA,Aa,aA,aa.
Ba tổ hợp đầu có alen A nên kiểu hình trội có xác suất 3/4.
|
3/4.
---
Xác suất con có kiểu gen dị hợp trong mô hình trên?
|
Aa và aA đều là dị hợp, có 2 trong 4 tổ hợp.
Xác suất 2/4=1/2.
|
1/2.
---
Hai con độc lập theo mô hình trên, xác suất cả hai đều aa?
|
Mỗi con aa có xác suất 1/4.
Độc lập nên xác suất đồng thời bằng 1/4×1/4=1/16.
|
1/16.
""",
)
add(
    "trapezoid_integral",
    "Quy tắc hình thang ghép: h=(b−a)/n, T_n=h[(f(a)+f(b))/2+Σf(a+ih)], i=1,...,n−1. Đây là xấp xỉ tích phân, không mặc nhiên bằng tích phân chính xác.",
    "1. Chia đều đoạn thành n phần và lập bảng giá trị.\n2. Hai đầu mút lấy nửa trọng số.\n3. Tính T_n, ghi dấu xấp xỉ và so kết quả đúng nếu biết.",
    """
Xấp xỉ ∫ từ 0 đến 1 của x² dx bằng hình thang n=2.
|
h=1/2, giá trị hàm tại 0,1/2,1 là 0,1/4,1.
T₂=(1/2)[(0+1)/2+1/4]=3/8=0,375; tích phân đúng 1/3.
|
Xấp xỉ 0,375.
---
Với cùng tích phân, dùng n=1.
|
h=1, chỉ hai đầu mút 0 và 1.
T₁=1×(0+1)/2=0,5.
|
Xấp xỉ 0,5.
---
Dùng hình thang n=2 cho ∫ từ 0 đến 1 của x dx.
|
Các giá trị 0,1/2,1; h=1/2.
T₂=(1/2)[1/2+1/2]=1/2, đúng bằng tích phân hàm bậc nhất này.
|
1/2.
""",
)
add(
    "climate_data",
    "Phân tích khí hậu cần số liệu có nguồn, thời gian, địa điểm và đơn vị. Chọn biểu đồ phù hợp cho nhiệt độ, lượng mưa; không cộng nhiệt độ để nói “tổng nhiệt” khi câu hỏi yêu cầu trung bình. Ví dụ dưới dùng dữ liệu giả định để luyện, không phải số liệu khí tượng Việt Nam.",
    "1. Ghi nguồn, năm, đơn vị của bảng gốc khi làm với SGK.\n2. Tính tổng hoặc trung bình theo đúng đại lượng.\n3. Vẽ biểu đồ và giới hạn nhận xét trong dữ liệu.",
    """
Dữ liệu giả định ba tháng có nhiệt độ trung bình 26,28,30°C. Trung bình ba số là bao nhiêu?
|
Tổng ba số đo 26+28+30=84.
Trung bình 84/3=28°C.
|
28°C (bộ số giả định).
---
Ba tháng giả định có mưa 40,60,100 mm. Tổng lượng mưa?
|
Lượng mưa theo tháng được cộng khi tìm tổng.
40+60+100=200 mm.
|
200 mm.
---
Từ ba tháng giả định nhiệt độ tăng liên tiếp, có thể kết luận mọi tháng của năm đều tăng không?
|
Chỉ có dữ liệu ba tháng, các tháng còn lại chưa được quan sát.
Không đủ dữ kiện để suy xu thế cho cả năm.
|
Không.
""",
)
add(
    "population_data",
    "Đọc số liệu dân số phải kiểm tra năm, đơn vị, phạm vi và nguồn; số lượng khác với tỉ trọng. Các ví dụ dưới là mô hình giả định, không phải số liệu dân số quốc gia.",
    "1. Ghi thông tin nguồn bảng SGK hoặc cơ quan thống kê.\n2. Tính tổng, tỉ trọng hay tốc độ theo đúng câu hỏi.\n3. Trình bày biểu đồ, không gán số giả định thành số thực tế.",
    """
Một quần thể giả định có ba nhóm 20,30,50 người. Nhóm thứ hai chiếm bao nhiêu phần trăm?
|
Tổng số người 20+30+50=100.
Tỉ trọng nhóm thứ hai 30/100×100%=30%.
|
30%.
---
Dân số mô hình từ 100 nghìn lên 102 nghìn. Tỉ lệ tăng?
|
Mức tăng 102−100=2 nghìn.
Tỉ lệ tăng 2/100×100%=2%.
|
2%.
---
Có thể so trực tiếp “2 triệu người” với “500 nghìn người” chỉ theo 2 và 500 không?
|
Đơn vị khác nhau nên phải đổi trước.
2 triệu=2 000 nghìn, lớn hơn 500 nghìn.
|
Không; 2 triệu lớn hơn 500 nghìn.
""",
)
add(
    "social_data",
    "Điều tra về mạng xã hội cần bảo vệ danh tính, mô tả cách chọn mẫu và tránh suy tương quan thành nhân quả. Tỉ lệ trong mẫu không tự đại diện mọi học sinh. Các số dưới là ví dụ giả định.",
    "1. Thiết kế câu hỏi trung lập, không thu thông tin định danh không cần thiết.\n2. Tính tần số, tỉ lệ theo cỡ mẫu đúng.\n3. Nêu giới hạn mẫu và không suy nguyên nhân khi chưa có căn cứ.",
    """
Mẫu giả định 40 bạn có 30 bạn dùng mạng xã hội hằng ngày. Tỉ lệ trong mẫu?
|
Tỉ lệ 30/40=3/4.
Đổi thành phần trăm là 75%.
|
75% trong mẫu.
---
Một khảo sát chỉ hỏi thành viên câu lạc bộ công nghệ. Có thể khẳng định kết quả đại diện toàn trường không?
|
Mẫu chỉ từ một nhóm có đặc điểm riêng.
Chưa có căn cứ về tính đại diện cho toàn trường.
|
Không đủ căn cứ.
---
Thấy nhóm dùng mạng lâu có điểm thấp hơn trong một bảng khảo sát. Có chứng minh mạng xã hội gây điểm thấp không?
|
Quan sát mối liên hệ không loại trừ các yếu tố khác.
Muốn kết luận nhân quả cần thiết kế và bằng chứng phù hợp hơn.
|
Chưa chứng minh quan hệ nhân quả.
""",
)
add(
    "theorem_proof",
    "Định lí gồm giả thiết và kết luận; chứng minh dùng suy luận từ giả thiết và các kết quả đã biết. Hình vẽ giúp nhận dạng nhưng không thay chứng minh. Một ví dụ phù hợp không chứng minh mệnh đề “mọi”.",
    "1. Viết giả thiết và điều cần chứng minh.\n2. Chọn tính chất liên quan.\n3. Nêu từng suy luận, tránh dùng chính kết luận làm lí do.",
    """
Chứng minh hai góc đối đỉnh bằng nhau.
|
Gọi hai góc đối đỉnh là α,β và góc kề bù chung là γ.
α+γ=180°, β+γ=180° nên α=β khi trừ cùng γ.
|
Hai góc đối đỉnh bằng nhau.
---
Giả thiết “hai góc cùng bù với góc 70°”; kết luận cần chứng minh “hai góc bằng nhau”. Chứng minh.
|
Mỗi góc có số đo 180°−70°=110°.
Vì cùng bằng 110° nên hai góc bằng nhau.
|
Hai góc đều 110°.
---
Đã kiểm tra một hình bình hành có góc vuông. Có chứng minh mọi hình bình hành đều có góc vuông không?
|
Một ví dụ không bao quát mọi hình bình hành.
Hình bình hành có thể có góc nhọn, góc tù, nên kết luận ấy không đúng.
|
Không.
""",
)
add(
    "triangle_centers",
    "Ba trung tuyến đồng quy ở trọng tâm G, chia trung tuyến theo tỉ số đỉnh–G : G–trung điểm = 2:1. Ba phân giác trong đồng quy tại điểm cách đều các cạnh. Ba trung trực đồng quy tại điểm cách đều các đỉnh. Ba đường cao đồng quy tại trực tâm.",
    "1. Nhận dạng đúng loại đường đặc biệt.\n2. Dùng tính chất tương ứng của điểm đồng quy.\n3. Không đổi lẫn khoảng cách tới cạnh và tới đỉnh.",
    """
G là trọng tâm, AM là trung tuyến dài 9 cm. Tính AG,GM.
|
AG=2AM/3=6 cm.
GM=AM/3=3 cm.
|
AG=6 cm; GM=3 cm.
---
I là giao các phân giác trong tam giác, khoảng cách từ I tới AB là 2 cm. Khoảng cách tới BC và CA?
|
I cách đều ba cạnh tam giác.
Hai khoảng cách còn lại đều 2 cm.
|
2 cm và 2 cm.
---
Tam giác ABC vuông tại A, BC=10 cm. Xác định tâm ngoại tiếp và trực tâm.
|
Tâm ngoại tiếp là trung điểm BC, bán kính 5 cm.
AB,AC đã là hai đường cao nên trực tâm là A.
|
Tâm ngoại tiếp: trung điểm BC, R=5 cm; trực tâm A.
""",
)
add(
    "regular_polygon",
    "Đa giác đều có n cạnh bằng nhau và n góc bằng nhau, n≥3. Mỗi góc trong bằng (n−2)180°/n; góc ở tâm chắn một cạnh bằng 360°/n. Không chỉ có cạnh bằng nhau mà đã đủ kết luận mọi đa giác đều.",
    "1. Xác định n và loại góc.\n2. Dùng công thức góc trong hoặc góc ở tâm đúng.\n3. Với lục giác đều nội tiếp, mỗi cạnh bằng bán kính.",
    """
Tính góc trong của ngũ giác đều.
|
Tổng góc trong bằng (5−2)×180°=540°.
Mỗi góc bằng 540°/5=108°.
|
108°.
---
Lục giác đều nội tiếp đường tròn bán kính 4 cm. Tính cạnh.
|
Mỗi góc ở tâm chắn một cạnh bằng 360°/6=60°.
Tam giác tạo bởi hai bán kính và cạnh là đều nên cạnh bằng bán kính.
|
4 cm.
---
Tính góc ở tâm chắn một cạnh bát giác đều.
|
Tám góc ở tâm bằng nhau và tổng bằng 360°.
Mỗi góc bằng 360°/8=45°.
|
45°.
""",
)
add(
    "scaled_figures",
    "Các hình đồng dạng có cùng hình dạng với tỉ số độ dài tương ứng k>0. Diện tích tỉ lệ k²; góc tương ứng giữ nguyên. Việc thay đổi riêng một chiều của hình chữ nhật thường không giữ đồng dạng.",
    "1. Ghép các độ dài tương ứng.\n2. Kiểm tra một tỉ số chung.\n3. Dùng k cho độ dài, k² cho diện tích.",
    """
Hình chữ nhật 2×3 cm được phóng đều tỉ số 2. Kích thước, diện tích mới?
|
Hai cạnh mới là 4 cm và 6 cm.
Diện tích mới 24 cm², bằng 4 lần diện tích gốc 6 cm².
|
4×6 cm; 24 cm².
---
Ảnh 10×15 cm thu đều còn một nửa. Kích thước mới?
|
Tỉ số k=1/2 áp dụng cho cả hai chiều.
Kích thước mới 5×7,5 cm.
|
5×7,5 cm.
---
Hai hình đồng dạng có tỉ số độ dài 3. Diện tích hình lớn gấp mấy lần?
|
Tỉ số diện tích bằng bình phương tỉ số độ dài.
3²=9.
|
9 lần.
""",
)
add(
    "approx_error",
    "Nếu A là giá trị đúng, a gần đúng thì sai số tuyệt đối |A−a|; sai số tương đối |A−a|/|a| khi a≠0. Biết |A−a|≤d thì A∈[a−d;a+d]. Làm tròn cần nêu hàng hoặc độ chính xác.",
    "1. Phân biệt số đúng, số gần đúng và cận sai số.\n2. Tính trị tuyệt đối hoặc lập khoảng.\n3. Nếu đổi phần trăm, nhân tỉ số với 100%.",
    """
Giá trị đúng 100, đo được 98. Tính sai số tuyệt đối, tương đối.
|
Sai số tuyệt đối |100−98|=2.
Theo quy ước dùng số gần đúng ở mẫu, sai số tương đối là 2/98=1/49, xấp xỉ 2,04%.
|
2; 1/49 (khoảng 2,04%).
---
Kết quả a=10 có sai số tuyệt đối không quá 0,1. Giá trị đúng thuộc khoảng nào?
|
10−0,1=9,9; 10+0,1=10,1.
Giá trị đúng nằm trong đoạn hai đầu này.
|
[9,9;10,1].
---
Làm tròn 7,346 đến hàng phần trăm.
|
Hàng phần trăm là 4, chữ số ngay sau là 6≥5.
Tăng hàng phần trăm thêm 1, bỏ hàng phía sau được 7,35.
|
7,35.
""",
)

MAPPING = {
    6: """1:sets 2:p:number1000000 3:p:compare1000000 4:p:add6,p:sub6 5:p:mul4,p:div4
6:powers 7:p:operations 8:divisibility 9:divisibility 10:prime_gcd_lcm 11:prime_gcd_lcm 12:prime_gcd_lcm
13:integers 14:integers 15:integers 16:integers 17:integers,divisibility
18:p:shapes,regular_polygon 19:quadrilaterals 20:quadrilateral_area 21:symmetry 22:symmetry
23:signed_fractions 24:signed_fractions,m:mixed 25:signed_fractions 26:signed_fractions 27:fraction_problems
28:decimal_signed 29:decimal_signed 30:approx_error,p:estimate 31:fraction_problems
32:p:segments 33:p:segments,p:midpoint 34:p:segments 35:p:midpoint 36:p:right_angle 37:p:angle_degree
38:p:data 39:p:data,p:graph_picture 40:p:graph_column 41:p:graph_column
42:p:chance 43:probability""",
    7: """1:signed_fractions 2:signed_fractions 3:powers 4:p:operations,linear_equation
5:repeating_decimals 6:roots_real 7:roots_real,integers 8:angle_lines 9:angle_lines
10:angle_lines 11:theorem_proof 12:triangle_angles 13:congruent 14:congruent
15:congruent 16:triangle_angles,triangle_centers 17:p:data 18:m:pie 19:p:data
20:ratios 21:ratios 22:ratios 23:ratios 24:poly_one 25:poly_one 26:poly_one
27:polynomial_product 28:polynomial_product 29:p:chance 30:probability
31:triangle_relations 32:triangle_relations 33:triangle_relations 34:triangle_centers 35:triangle_centers
36:m:box_area,m:box_volume,m:cube_volume 37:solids_volume""",
    8: """1:polynomials 2:polynomials 3:polynomials 4:polynomial_product 5:polynomial_product
6:identities 7:identities 8:identities 9:identities 10:quadrilaterals 11:quadrilaterals
12:quadrilaterals 13:quadrilaterals 14:quadrilaterals 15:thales_similarity 16:thales_similarity
17:angle_bisector_ratio 18:p:data 19:p:graph_column,m:pie 20:p:data,p:graph_column
21:rational_expressions 22:rational_expressions 23:rational_expressions 24:rational_expressions
25:linear_equation 26:linear_equation 27:functions_linear 28:functions_linear 29:functions_linear
30:probability 31:probability 32:probability 33:thales_similarity 34:thales_similarity
35:pythagoras 36:thales_similarity,pythagoras 37:scaled_figures 38:solids_volume 39:solids_volume""",
    9: """1:systems 2:systems 3:systems 4:equation_transform 5:inequality 6:inequality
7:roots_real 8:radical_transform 9:radical_transform 10:radical_transform
11:trig_right 12:trig_right 13:circle_geometry 14:circle_geometry 15:arc_sector
16:circle_positions 17:circle_positions 18:quadratic_function 19:quadratic 20:quadratic
21:quadratic 22:frequency_tables 23:frequency_tables 24:frequency_tables
25:probability 26:probability 27:circle_geometry 28:circle_geometry 29:circle_geometry
30:regular_polygon 31:rotational_solids 32:rotational_solids""",
    10: """1:propositions 2:set_operations 3:linear_two_variables 4:linear_two_variables
5:triangle_trig 6:triangle_trig 7:vectors_plane 8:vectors_plane 9:vectors_plane 10:vectors_plane
11:dot_product 12:approx_error 13:statistics 14:statistics 15:functions_linear,quadratic_function
16:quadratic_function 17:quadratic_function 18:quadratic 19:lines_plane 20:lines_plane
21:circle_coordinates 22:conics 23:counting 24:counting 25:binomial 26:probability 27:probability""",
    11: """1:trig_angles 2:trig_angles 3:trig_functions 4:trig_equations 5:sequences 6:sequences 7:sequences
8:grouped_statistics 9:grouped_statistics 10:space_parallel 11:space_parallel 12:space_parallel
13:space_parallel 14:space_parallel 15:limits_sequence 16:limits_continuity 17:limits_continuity
18:real_powers 19:logarithms 20:logarithms 21:exp_log_equations 22:space_perpendicular
23:space_perpendicular 24:space_perpendicular 25:space_perpendicular 26:space_perpendicular
27:volume_space 28:probability_rules 29:probability_rules 30:probability_rules
31:derivative 32:derivative_rules 33:second_derivative""",
    12: """1:monotonicity 2:optimization 3:asymptotes 4:monotonicity,asymptotes 5:optimization
6:vectors_space 7:vectors_space 8:vectors_space 9:grouped_statistics,grouped_spread
10:grouped_spread 11:antiderivative 12:integral 13:integral_geometry 14:planes_space
15:lines_space 16:angles_space 17:sphere_coordinates 18:conditional_bayes 19:conditional_bayes""",
}
MAPPING = {
    g: {int(p.split(":", 1)[0]): p.split(":", 1)[1].split(",") for p in text.split()}
    for g, text in MAPPING.items()
}
YEAR = {
    6: ["integers", "signed_fractions", "quadrilateral_area", "probability", "p:data"],
    7: [
        "signed_fractions",
        "ratios",
        "polynomial_product",
        "triangle_relations",
        "probability",
    ],
    8: [
        "identities",
        "rational_expressions",
        "linear_equation",
        "thales_similarity",
        "probability",
    ],
    9: [
        "systems",
        "quadratic",
        "radical_transform",
        "circle_geometry",
        "frequency_tables",
    ],
    10: ["set_operations", "quadratic_function", "vectors_plane", "conics", "counting"],
    11: [
        "trig_equations",
        "sequences",
        "exp_log_equations",
        "space_perpendicular",
        "derivative_rules",
    ],
    12: [
        "monotonicity",
        "integral_geometry",
        "planes_space",
        "sphere_coordinates",
        "conditional_bayes",
    ],
}


def resolve(key, grade):
    from copy import deepcopy

    if key == "poly_one":
        value = deepcopy(CONTENT["polynomials"])
        value["rule"] = (
            "Đa thức một biến x là tổng các hạng ax^n với n nguyên không âm. Thu gọn và sắp theo số mũ; bậc là số mũ lớn nhất có hệ số khác 0. Giá trị đa thức tại x₀ tính bằng thay x=x₀."
        )
        value["example"] = "Cho P(x)=2x²−3x+1. Tìm bậc và giá trị tại x=2."
        value["worked"] = solution(
            ["Bậc cao nhất có hệ số khác 0 là 2.", "P(2)=2×4−3×2+1=3."],
            "Bậc 2; P(2)=3.",
        )
        return value
    if key.startswith("p:"):
        return primary(key[2:], grade, 1)
    if key.startswith("m:"):
        k = key[2:]
        rule, _, example, _, tasks, _, mistake = MATH5[k]
        worked, *answers = WORKED[k]
        return dict(
            name=k,
            rule=RULES.get(k, rule),
            method=METHODS[k],
            example=EXAMPLES.get(k, example),
            worked=worked,
            tasks=TASKS.get(k, tasks),
            answers=answers,
            mistake=MISTAKES.get(k, mistake),
        )
    return deepcopy(CONTENT[key])


def activity_keys(grade, title):
    t = title.casefold()
    if "gene" in t:
        return ["gene_probability"]
    if "pha chế" in t:
        return ["dilution"]
    if "lãi kép" in t:
        return ["compound_interest"]
    if "mạng xã hội" in t:
        return ["social_data"]
    if "tài chính" in t:
        return ["finance_linear", "compound_interest"]
    if "chi tiêu" in t:
        return ["budget"]
    if "dân số" in t:
        return ["population_data"]
    if "khí hậu" in t:
        return ["climate_data"]
    if "gang tay" in t:
        return ["grouped_statistics", "grouped_spread"]
    if "máy tính" in t:
        return ["m:calculator"]
    if "tấm thiệp" in t:
        return ["quadrilateral_area", "symmetry"]
    if "hộp quà" in t:
        return ["m:box_area", "solids_volume"]
    if "đo chiều cao" in t:
        return ["thales_similarity", "pythagoras"]
    if "hình thang" in t and "tích phân" in t:
        return ["integral", "trapezoid_integral"]
    if "thí nghiệm" in t:
        return ["probability"]
    if "excel" in t:
        return ["frequency_tables", "p:graph_column"]
    if "phân thức" in t:
        return ["rational_expressions", "functions_linear"]
    if "đa thức" in t:
        return ["polynomial_product", "identities"]
    if "phương trình" in t:
        return ["systems", "quadratic_function"]
    if "khảo sát" in t:
        return ["monotonicity", "asymptotes"]
    if "vẽ hình" in t:
        return ["p:drawing", "symmetry"]
    raise ValueError(f"Activity needs explicit authored mapping: {grade}: {title}")


add(
    "lines_rays",
    "Qua hai điểm phân biệt có duy nhất một đường thẳng. Tia có một gốc và kéo dài mãi theo một hướng. Hai tia trùng phải cùng gốc và cùng hướng; hai tia đối nhau cùng gốc, tạo thành một đường thẳng.",
    "1. Xác định gốc tia và thứ tự điểm.\n2. Kiểm tra thẳng hàng và cùng phía hay khác phía gốc.\n3. Phân biệt đoạn hữu hạn với tia kéo dài một phía.",
    """
Ba điểm O,A,B theo thứ tự trên một đường thẳng. Hai tia OA,OB có trùng không?
|
Hai tia cùng gốc O.
A và B cùng phía đối với O nên hai tia cùng hướng và trùng nhau.
|
Có, hai tia trùng nhau.
---
A,O,B thẳng hàng theo thứ tự. Hai tia OA,OB có quan hệ gì?
|
Cùng gốc O, A và B nằm khác phía đối với O.
Hai tia tạo thành đường thẳng nên đối nhau.
|
Hai tia đối nhau.
---
Ba điểm A,B,C không thẳng hàng. Có mấy đường thẳng qua từng cặp điểm?
|
Mỗi cặp tạo một đường: AB,AC,BC.
Ba đường khác nhau vì ba điểm không thẳng hàng.
|
3 đường thẳng.
""",
)
add(
    "double_bar",
    "Biểu đồ cột kép dùng các cặp cột với chú giải để so hai dãy số theo cùng nhóm. Phải đọc đúng trục, đơn vị, thời điểm và kí hiệu mỗi dãy.",
    "1. Đọc chú giải hai dãy.\n2. Đọc từng cặp cột hoặc bảng số liệu tương ứng.\n3. Tính chênh lệch, tổng theo đúng dãy.",
    """
Sách đọc hai kì: A có 2 rồi 3 quyển; B có 4 rồi 3 quyển. Bạn nào tăng số sách?
|
A tăng từ 2 lên 3, tăng 1 quyển.
B từ 4 xuống 3, giảm 1 quyển.
|
A tăng 1 quyển.
---
Với số liệu trên, tổng số sách kì đầu là bao nhiêu?
|
Kì đầu A có 2, B có 4.
Tổng 2+4=6 quyển.
|
6 quyển.
---
Với số liệu trên, kì sau hai bạn đọc bằng nhau không?
|
Kì sau A có 3, B có 3.
Cùng 3 quyển nên bằng nhau.
|
Có, mỗi bạn 3 quyển.
""",
)
add(
    "line_chart",
    "Biểu đồ đoạn thẳng biểu diễn dữ liệu theo thứ tự, thường là thời gian. Mỗi điểm có hoành độ là thời điểm, tung độ là giá trị; đoạn nối giúp nhìn xu thế nhưng không tự chứng minh nguyên nhân.",
    "1. Đọc trục thời gian, đơn vị và các điểm.\n2. So các giá trị liên tiếp.\n3. Nêu xu thế trong khoảng có dữ liệu, không tự ngoại suy.",
    """
Ba tháng liên tiếp có giá trị 5,8,6. Mô tả xu thế.
|
Từ tháng 1 đến 2 tăng 8−5=3 đơn vị.
Từ tháng 2 đến 3 giảm 8−6=2 đơn vị.
|
Tăng 3 rồi giảm 2; tháng 2 lớn nhất.
---
Với số liệu trên, giá trị cuối tăng bao nhiêu so với đầu?
|
Giá trị đầu 5, cuối 6.
Chênh lệch 6−5=1.
|
Tăng 1 đơn vị.
---
Từ ba giá trị trên có chắc tháng 4 bằng 4 không?
|
Dữ liệu chỉ cho ba tháng; việc kéo dài xu thế là dự đoán thêm.
Không có căn cứ để khẳng định giá trị tháng 4.
|
Không chắc.
""",
)
add(
    "chords",
    "Trong cùng một đường tròn, hai cung nhỏ bằng nhau khi dây tương ứng bằng nhau. Đường kính vuông góc một dây thì đi qua trung điểm dây đó. Dây gần tâm hơn thì dài hơn; dùng tam giác vuông từ tâm tới trung điểm dây để tính.",
    "1. Xác định cùng đường tròn và cung đang xét.\n2. Hạ vuông góc từ tâm tới dây.\n3. Dùng Pythagore cho nửa dây rồi nhân 2.",
    """
Đường tròn bán kính 5 cm, khoảng cách tâm tới dây AB bằng 3 cm. Tính AB.
|
Gọi H chân đường vuông góc thì H là trung điểm AB.
AH=√(5²−3²)=4 cm nên AB=8 cm.
|
8 cm.
---
Hai dây AB,CD bằng nhau trong cùng đường tròn. Cung nhỏ AB bằng 60°. Cung nhỏ CD bằng bao nhiêu?
|
Hai dây bằng nhau chắn hai cung nhỏ bằng nhau.
Cung nhỏ CD cũng bằng 60°.
|
60°.
---
Trong đường tròn bán kính 5 cm, hai dây cách tâm 3 cm và 4 cm. Dây nào dài hơn?
|
Dây thứ nhất dài 2√(25−9)=8 cm.
Dây thứ hai dài 2√(25−16)=6 cm; dây gần tâm dài hơn.
|
Dây cách tâm 3 cm dài hơn: 8 cm so với 6 cm.
""",
)
add(
    "quadratic_words",
    "Lập phương trình bậc hai cho bài toán cần chọn ẩn, điều kiện từ hình học/số lượng/thời gian, biểu diễn đại lượng và đối chiếu nghiệm. Nghiệm âm hoặc ngoài khoảng có thể phải loại dù đúng phương trình.",
    "1. Đặt ẩn và điều kiện.\n2. Viết phương trình theo quan hệ đề bài.\n3. Giải và thử lại bối cảnh, nêu đủ nghiệm phù hợp.",
    """
Hình chữ nhật có diện tích 24 m², dài hơn rộng 2 m. Tìm hai kích thước.
|
Gọi rộng x>0, dài x+2; x(x+2)=24 nên x²+2x−24=0.
Nghiệm 4 và −6; loại −6 nên rộng 4 m, dài 6 m.
|
4 m và 6 m.
---
Hai số tự nhiên liên tiếp có tích 56. Tìm hai số.
|
Gọi số nhỏ n≥0; n(n+1)=56 nên n²+n−56=0.
Nghiệm 7 và −8; chọn n=7.
|
7 và 8.
---
Độ cao mô hình h(t)=−5t²+20t, 0≤t≤4 giây. Khi nào h=15 m?
|
−5t²+20t=15 tương đương t²−4t+3=0.
Nghiệm 1 và 3 đều thuộc [0;4].
|
t=1 giây hoặc 3 giây.
""",
)
add(
    "radical_equations",
    "Với căn bậc hai số học, phải đặt biểu thức dưới căn không âm. Nếu √A=B thì cần B≥0 và A=B². Bình phương có thể sinh nghiệm ngoại lai nên phải kiểm tra điều kiện gốc.",
    "1. Ghi đầy đủ điều kiện hai vế.\n2. Bình phương tương đương khi đã có điều kiện dấu.\n3. Giải phương trình rồi thế lại từng nghiệm.",
    """
Giải √(x+1)=x−1.
|
Cần x≥1. Bình phương: x+1=x²−2x+1 nên x(x−3)=0.
Chỉ x=3 thỏa điều kiện; kiểm tra √4=2.
|
x=3.
---
Giải √(2x+3)=√(x+5).
|
Điều kiện x≥−3/2. Hai căn không âm nên bình phương: 2x+3=x+5.
x=2 thỏa điều kiện và hai vế cùng √7.
|
x=2.
---
Giải √((x−1)²)=2.
|
Vế trái bằng |x−1|.
x−1=2 hoặc x−1=−2 nên x=3 hoặc x=−1.
|
x=−1 hoặc x=3.
""",
)
add(
    "hand_measurement",
    "Đo gang tay là khoảng cách giữa đầu ngón cái và đầu ngón út khi xòe tay theo cùng quy trình. Ghi đơn vị, sai số thước, cách chọn mẫu và không thu tên học sinh nếu không cần. Các số dưới là mẫu giả định để luyện thống kê.",
    "1. Thống nhất cách đo và lập bảng số đo ẩn danh.\n2. Kiểm tra dữ liệu, sắp xếp hoặc ghép nhóm.\n3. Tính đặc trưng, ghi rõ số chính xác của mẫu hay ước lượng ghép nhóm.",
    """
Năm số đo giả định 18,19,20,21,22 cm. Tính trung bình, trung vị và khoảng biến thiên.
|
Tổng 100 cm, trung bình 100/5=20 cm; giá trị giữa là 20 cm.
Khoảng biến thiên 22−18=4 cm.
|
Trung bình 20 cm; trung vị 20 cm; khoảng biến thiên 4 cm.
---
Ghép các số trên vào [18;20),[20;22),[22;24). Tính trung bình ghép nhóm.
|
Tần số 2,2,1; đại diện nhóm 19,21,23 cm.
Trung bình xấp xỉ (2×19+2×21+23)/5=20,6 cm.
|
Khoảng 20,6 cm.
---
Vì trung bình mẫu giả định là 20 cm, có thể nói mọi bạn đều có gang tay 20 cm không?
|
Trung bình là đại lượng tổng hợp, các số đo riêng có thể khác.
Trong mẫu đã có 18 cm và 22 cm nên kết luận “mọi bạn” sai.
|
Không.
""",
)
# Topic-specific corrections: a lesson about rays/chords must teach those concepts.
MAPPING[6][33] = ["lines_rays"]
MAPPING[6][41] = ["double_bar"]
MAPPING[7][19] = ["line_chart"]
MAPPING[9][14] = ["chords"]
MAPPING[9][21] = ["quadratic_words"]
MAPPING[10][18] = ["radical_equations"]
CONTENT["vectors_plane"]["rule"] = CONTENT["vectors_plane"]["rule"].replace(
    "Vectơ không có độ dài 0.", "Vectơ 0 có độ dài bằng 0."
)
add(
    "euclid_parallel",
    "Tiên đề Euclid: qua một điểm nằm ngoài một đường thẳng, có duy nhất một đường thẳng song song đường thẳng đó trong mặt phẳng. Hai đường song song cắt bởi đường thứ ba có góc đồng vị, so le trong bằng nhau; góc trong cùng phía bù nhau.",
    "1. Xác định điểm ở ngoài và các đường trong cùng mặt phẳng.\n2. Dùng tính duy nhất hoặc quan hệ góc.\n3. Không dùng giả thiết chỉ “chưa thấy giao điểm” để suy song song.",
    """
Qua A ngoài d vẽ hai đường b,c đều song song d. b và c có thể khác nhau không?
|
Tiên đề Euclid cho duy nhất một đường qua A song song d.
Vì vậy b và c phải trùng nhau.
|
Không; b và c trùng nhau.
---
Hai đường song song bị cắt bởi một đường, một góc đồng vị là 65°. Góc đồng vị còn lại?
|
Hai góc đồng vị bằng nhau khi hai đường song song.
Góc cần tìm bằng 65°.
|
65°.
---
Hai góc trong cùng phía của hai đường song song, một góc 110°. Tính góc kia.
|
Hai góc trong cùng phía bù nhau.
Góc kia bằng 180°−110°=70°.
|
70°.
""",
)
add(
    "direct_inverse",
    "Đại lượng y tỉ lệ thuận x khi y=kx, k khác 0; các tỉ số y/x bằng k tại x≠0. Tỉ lệ nghịch khi xy=k khác 0, hay y=k/x. Mô hình phải được đề cho hoặc có căn cứ, không suy chỉ từ một cặp số.",
    "1. Phân biệt tỉ số không đổi và tích không đổi.\n2. Tìm k từ cặp giá trị đã biết.\n3. Tính giá trị mới và kiểm tra quan hệ.",
    """
y tỉ lệ thuận x, x=2 thì y=6. Khi x=4, y bao nhiêu?
|
k=6/2=3 nên y=3x.
Với x=4, y=12.
|
12.
---
y tỉ lệ nghịch x, x=3 thì y=4. Khi x=6, y bao nhiêu?
|
k=3×4=12 nên y=12/x.
Với x=6, y=2.
|
2.
---
Trong mô hình tỉ lệ nghịch, x tăng gấp 3 thì y thay đổi thế nào?
|
Tích xy không đổi và x khác 0.
Nếu x mới bằng 3x, y mới phải bằng y/3.
|
y giảm 3 lần.
""",
)
add(
    "circle_intro",
    "Đường tròn tâm O bán kính R gồm các điểm M có OM=R. OM<R thì M trong, OM>R thì M ngoài. Tâm là tâm đối xứng; mọi đường thẳng qua tâm là trục đối xứng. Đường kính bằng hai lần bán kính.",
    "1. Tìm tâm, bán kính và khoảng cách đến điểm.\n2. So khoảng cách với bán kính.\n3. Khi xét đường kính, kiểm tra đi qua tâm.",
    """
Đường tròn tâm O bán kính 5 cm. OA=3, OB=5, OC=7 cm. Xác định vị trí A,B,C.
|
OA<5 nên A trong; OB=5 nên B trên đường tròn.
OC>5 nên C ngoài đường tròn.
|
A trong; B trên; C ngoài.
---
Hình tròn có đường kính 12 cm. Tính bán kính.
|
Bán kính bằng nửa đường kính.
12/2=6 cm.
|
6 cm.
---
M,N thuộc đường tròn tâm O, O nằm giữa M,N, OM=4 cm. Tính MN.
|
OM=ON=4 cm vì đều là bán kính.
MN=OM+ON=8 cm; MN là đường kính.
|
8 cm.
""",
)
add(
    "triangle_circles",
    "Tâm ngoại tiếp tam giác là giao trung trực, cách đều ba đỉnh. Tâm nội tiếp là giao phân giác trong, cách đều ba cạnh. Với diện tích S, nửa chu vi p, bán kính nội tiếp r=S/p. Tam giác vuông có R bằng nửa cạnh huyền; tam giác đều cạnh a có R=a√3/3, r=a√3/6.",
    "1. Xác định loại tâm và tam giác.\n2. Dùng cạnh huyền, diện tích–nửa chu vi hoặc công thức tam giác đều.\n3. Ghi bán kính dương và đơn vị.",
    """
Tam giác vuông có ba cạnh 3,4,5 cm. Tính bán kính ngoại tiếp và nội tiếp.
|
R=5/2=2,5 cm; S=3×4/2=6 cm², p=(3+4+5)/2=6 cm.
r=S/p=1 cm.
|
R=2,5 cm; r=1 cm.
---
Tam giác đều cạnh 6 cm. Tính R,r.
|
R=6√3/3=2√3 cm.
r=6√3/6=√3 cm.
|
R=2√3 cm; r=√3 cm.
---
Tam giác có diện tích 24 cm², nửa chu vi 12 cm. Tính bán kính nội tiếp.
|
Diện tích bằng nửa chu vi nhân bán kính nội tiếp.
r=24/12=2 cm.
|
2 cm.
""",
)
add(
    "arithmetic_sequence",
    "Cấp số cộng có hiệu u_(n+1)−u_n=d không đổi. u_n=u₁+(n−1)d; S_n=n(u₁+u_n)/2, n là số nguyên dương. Công sai có thể âm hoặc bằng 0.",
    "1. Xác định u₁,d hoặc lập hệ từ các số hạng.\n2. Chọn công thức số hạng hay tổng.\n3. Kiểm tra chỉ số bắt đầu từ 1.",
    """
Cấp số cộng u₁=3,d=2. Tính u₁₀,S₁₀.
|
u₁₀=3+9×2=21.
S₁₀=10(3+21)/2=120.
|
u₁₀=21; S₁₀=120.
---
Cấp số cộng có u₃=7,u₇=15. Tìm u₁,d.
|
u₇−u₃=4d=8 nên d=2.
u₁=u₃−2d=7−4=3.
|
u₁=3; d=2.
---
Cấp số cộng u₁=3,d=2. Số 21 là số hạng thứ mấy?
|
3+(n−1)×2=21 nên n−1=9.
n=10 là số nguyên dương hợp lệ.
|
Thứ 10.
""",
)
add(
    "geometric_sequence",
    "Cấp số nhân có u_(n+1)=q u_n. u_n=u₁q^(n−1); nếu q≠1, S_n=u₁(1−q^n)/(1−q). Với q=1, S_n=nu₁; không chia cho số hạng bằng 0 khi tìm q.",
    "1. Xác định u₁,q và kiểm tra mẫu nếu lấy tỉ số.\n2. Chọn công thức số hạng hoặc tổng.\n3. Xét riêng q=1.",
    """
Cấp số nhân u₁=2,q=3. Tính u₄,S₄.
|
u₄=2×3³=54.
S₄=2(1−3⁴)/(1−3)=80.
|
u₄=54; S₄=80.
---
Cấp số nhân có u₂=6,u₃=18. Tìm q và u₁.
|
Vì u₂≠0, q=18/6=3.
u₁=u₂/q=6/3=2.
|
q=3; u₁=2.
---
Cấp số nhân u₁=8,q=1/2. Tính u₄.
|
u₄=8×(1/2)³.
8×1/8=1.
|
1.
""",
)
MAPPING[6][2] = ["p:number1000000", "p:roman"]
MAPPING[6][28] = ["m:decimal", "decimal_signed"]
MAPPING[7][10] = ["euclid_parallel"]
MAPPING[7][22] = ["direct_inverse"]
MAPPING[7][23] = ["direct_inverse"]
MAPPING[9][13] = ["circle_intro"]
MAPPING[9][28] = ["triangle_circles"]
MAPPING[11][6] = ["arithmetic_sequence"]
MAPPING[11][7] = ["geometric_sequence"]
