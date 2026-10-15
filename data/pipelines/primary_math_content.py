"""Original primary-school teaching material; explicit topic-to-lesson mappings."""

from math5_worked_solutions import (
    solution,
    WORKED,
    METHODS,
)
from build_math5_lessons import SKILLS as MATH5


def item(name, rule, method, example, steps, answer, tasks, solutions, mistake):
    assert len(tasks) == len(solutions) == 2
    return dict(
        name=name,
        rule=rule,
        method=method,
        example=example,
        worked=solution(steps, answer),
        tasks=tasks,
        answers=[solution(s, a) for s, a in solutions],
        mistake=mistake,
    )


STATIC = {}


def add(key, *args):
    STATIC[key] = item(*args)


add(
    "components_add",
    "Thành phần phép cộng, phép trừ",
    "Trong phép cộng, các số được cộng là số hạng, kết quả là tổng. Trong phép trừ, có số bị trừ, số trừ và hiệu.",
    "1. Đọc phép tính.\n2. Xác định phép cộng hay phép trừ.\n3. Gọi đúng tên từng thành phần theo vị trí.",
    "Nêu tên các thành phần của 8 + 5 = 13 và 13 − 5 = 8.",
    [
        "Ở phép cộng: 8 và 5 là hai số hạng; 13 là tổng.",
        "Ở phép trừ: 13 là số bị trừ, 5 là số trừ, 8 là hiệu.",
    ],
    "Số hạng: 8, 5; tổng: 13. Số bị trừ: 13; số trừ: 5; hiệu: 8.",
    ["Trong 7 + 6 = 13, tổng là số nào?", "Trong 15 − 4 = 11, số trừ là số nào?"],
    [
        (
            [
                "Phép tính đã cho là phép cộng.",
                "Kết quả của phép cộng là 13 nên tổng là 13.",
            ],
            "13.",
        ),
        (
            [
                "Phép tính đã cho là phép trừ.",
                "Số đứng sau dấu trừ là 4 nên số trừ là 4.",
            ],
            "4.",
        ),
    ],
    "Không đổi tên số bị trừ và số trừ.",
)
add(
    "unknown_add",
    "Tìm thành phần chưa biết trong phép cộng, phép trừ",
    "Số hạng chưa biết = tổng − số hạng đã biết. Số bị trừ = hiệu + số trừ. Số trừ = số bị trừ − hiệu.",
    "1. Gọi đúng tên thành phần chưa biết.\n2. Chọn quy tắc.\n3. Tính rồi thay vào phép tính ban đầu để kiểm tra.",
    "Tìm số còn thiếu trong □ + 25 = 63.",
    [
        "Số cần tìm là một số hạng.",
        "Số hạng chưa biết là:",
        "63 − 25 = 38",
        "Thử lại: 38 + 25 = 63.",
    ],
    "38.",
    ["Tìm □ trong □ − 18 = 27.", "Tìm □ trong 72 − □ = 29."],
    [
        (
            [
                "Số cần tìm là số bị trừ.",
                "Số bị trừ là:",
                "27 + 18 = 45",
                "Thử lại: 45 − 18 = 27.",
            ],
            "45.",
        ),
        (
            [
                "Số cần tìm là số trừ.",
                "Số trừ là:",
                "72 − 29 = 43",
                "Thử lại: 72 − 43 = 29.",
            ],
            "43.",
        ),
    ],
    "Muốn tìm số trừ phải lấy số bị trừ trừ hiệu, không lấy hiệu trừ số bị trừ.",
)
add(
    "unknown_multiply",
    "Tìm thành phần trong phép nhân, phép chia",
    "Thừa số chưa biết = tích : thừa số đã biết. Số bị chia = thương × số chia. Số chia = số bị chia : thương (trong phép chia hết, thương khác 0). Không chia cho 0.",
    "1. Xác định thành phần chưa biết.\n2. Dùng quan hệ nhân và chia.\n3. Thay kết quả vào để kiểm tra.",
    "Tìm □ trong □ × 6 = 42.",
    [
        "Số cần tìm là một thừa số.",
        "Thừa số chưa biết là:",
        "42 : 6 = 7",
        "Thử lại: 7 × 6 = 42.",
    ],
    "7.",
    ["Tìm □ trong □ : 4 = 8.", "Tìm □ trong 54 : □ = 6."],
    [
        (
            [
                "Số cần tìm là số bị chia.",
                "Số bị chia là:",
                "8 × 4 = 32",
                "Thử lại: 32 : 4 = 8.",
            ],
            "32.",
        ),
        (
            [
                "Số cần tìm là số chia.",
                "Số chia là:",
                "54 : 6 = 9",
                "Thử lại: 54 : 9 = 6.",
            ],
            "9.",
        ),
    ],
    "Không lấy tích nhân thêm thừa số khi đang tìm thừa số còn thiếu.",
)
add(
    "unit_fraction",
    "Một phần mấy",
    "Chia một hình hoặc một nhóm đồ vật thành các phần bằng nhau. Một trong hai phần là một phần hai; một trong ba phần là một phần ba; tương tự với các phần khác.",
    "1. Kiểm tra các phần chia có bằng nhau không.\n2. Đếm số phần bằng nhau.\n3. Muốn tìm một phần mấy của một nhóm, lấy số đồ vật chia cho số phần.",
    "Có 12 chiếc bánh chia đều vào 3 đĩa. Một đĩa có bao nhiêu chiếc bánh và chiếm một phần mấy số bánh?",
    [
        "Số bánh trong mỗi đĩa là:",
        "12 : 3 = 4 (chiếc)",
        "Mỗi đĩa là một trong ba phần bằng nhau nên chiếm một phần ba số bánh.",
    ],
    "4 chiếc bánh; một phần ba số bánh.",
    [
        "Có 16 viên bi chia đều thành 4 nhóm. Mỗi nhóm có mấy viên bi?",
        "Có 18 bông hoa chia đều thành 6 phần. Một phần sáu số hoa là bao nhiêu bông?",
    ],
    [
        (["Số viên bi mỗi nhóm là:", "16 : 4 = 4 (viên)"], "4 viên bi."),
        (["Một phần sáu số hoa là:", "18 : 6 = 3 (bông)"], "3 bông hoa."),
    ],
    "Các phần phải bằng nhau; không chỉ đếm số mảnh khi mảnh lớn nhỏ khác nhau.",
)
add(
    "midpoint",
    "Điểm ở giữa và trung điểm",
    "Điểm M ở giữa hai điểm A và B khi A, M, B thẳng hàng và M nằm trong đoạn AB. M là trung điểm AB nếu M ở giữa A, B và MA = MB.",
    "1. Kiểm tra ba điểm thẳng hàng và vị trí ở giữa.\n2. Đo hai đoạn nối điểm ở giữa với hai đầu mút.\n3. Chỉ kết luận trung điểm khi hai đoạn bằng nhau.",
    "A, M, B theo thứ tự trên một đường thẳng; AM = 3 cm, MB = 3 cm. M có là trung điểm AB không? AB dài bao nhiêu?",
    [
        "M ở giữa A và B; AM = MB = 3 cm nên M là trung điểm AB.",
        "Độ dài đoạn AB là:",
        "3 + 3 = 6 (cm)",
    ],
    "M là trung điểm AB; AB dài 6 cm.",
    [
        "A, N, B theo thứ tự trên đường thẳng; AN = 2 cm, NB = 4 cm. N có là trung điểm AB không? Vì sao?",
        "M là trung điểm AB, AB = 8 cm. Tính AM.",
    ],
    [
        (
            [
                "N ở giữa A và B nhưng AN = 2 cm, NB = 4 cm.",
                "Vì AN khác NB nên N không là trung điểm AB.",
            ],
            "N không là trung điểm AB.",
        ),
        (
            ["Vì M là trung điểm AB nên AM = MB.", "Độ dài AM là:", "8 : 2 = 4 (cm)"],
            "4 cm.",
        ),
    ],
    "Điểm ở giữa chưa chắc là trung điểm.",
)
add(
    "circle_parts",
    "Tâm, bán kính, đường kính",
    "Tâm O nằm ở giữa hình tròn. Đoạn nối tâm với một điểm trên đường tròn là bán kính. Đường kính đi qua tâm và có hai đầu trên đường tròn; đường kính dài gấp đôi bán kính.",
    "1. Xác định tâm.\n2. Phân biệt bán kính và đường kính bằng hai đầu mút.\n3. Đường kính = bán kính × 2; bán kính = đường kính : 2. Dùng compa để vẽ đường tròn khi được hướng dẫn.",
    "Hình tròn tâm O có bán kính 3 cm. Tính đường kính.",
    ["Đường kính dài gấp đôi bán kính.", "Đường kính hình tròn là:", "3 × 2 = 6 (cm)"],
    "6 cm.",
    [
        "Hình tròn có đường kính 8 cm. Tính bán kính.",
        "OA, OB là hai bán kính của cùng hình tròn tâm O; OA = 4 cm. Tính OB.",
    ],
    [
        (
            [
                "Bán kính bằng một nửa đường kính.",
                "Bán kính hình tròn là:",
                "8 : 2 = 4 (cm)",
            ],
            "4 cm.",
        ),
        (
            [
                "Các bán kính của cùng một hình tròn có độ dài bằng nhau.",
                "Vì OA = 4 cm nên OB = 4 cm.",
            ],
            "4 cm.",
        ),
    ],
    "Không coi mọi dây nối hai điểm trên đường tròn là đường kính; đường kính phải đi qua tâm. Bài này chưa tính chu vi hay diện tích.",
)
add(
    "right_angle",
    "Góc vuông và góc không vuông",
    "Hai cạnh của góc gặp nhau ở đỉnh. Có thể dùng góc vuông của ê-ke để kiểm tra một góc có vuông hay không.",
    "1. Đặt đỉnh góc vuông của ê-ke trùng đỉnh góc cần kiểm tra.\n2. Đặt một cạnh ê-ke trùng một cạnh góc.\n3. Nếu cạnh kia cũng trùng thì góc đó vuông.",
    "Dùng ê-ke kiểm tra góc tạo bởi hai cạnh kề của một tờ giấy hình chữ nhật.",
    [
        "Đặt đỉnh ê-ke vào góc tờ giấy.",
        "Hai cạnh góc vuông của ê-ke trùng với hai cạnh tờ giấy nên đó là góc vuông.",
    ],
    "Góc đã kiểm tra là góc vuông.",
    [
        "Hình vuông có mấy góc vuông?",
        "Muốn kiểm tra một góc có vuông hay không, em dùng dụng cụ gì và đặt như thế nào?",
    ],
    [
        (
            [
                "Hình vuông có bốn góc.",
                "Dùng ê-ke kiểm tra từng góc: cả bốn đều là góc vuông.",
            ],
            "4 góc vuông.",
        ),
        (
            [
                "Dùng ê-ke; đặt đỉnh góc vuông của ê-ke trùng đỉnh góc.",
                "Đặt một cạnh trùng một cạnh góc rồi kiểm tra cạnh còn lại.",
            ],
            "Dùng ê-ke và đặt theo hai bước trên.",
        ),
    ],
    "Không chỉ nhìn nghiêng bằng mắt để kết luận góc vuông.",
)
add(
    "shapes",
    "Nhận biết hình phẳng",
    "Hình tam giác có 3 cạnh, hình tứ giác có 4 cạnh. Hình chữ nhật có 4 góc vuông và hai cặp cạnh đối diện bằng nhau. Hình vuông có 4 góc vuông và 4 cạnh bằng nhau. Hình tròn có đường bao cong khép kín.",
    "1. Quan sát đường bao.\n2. Đếm cạnh, đỉnh của hình có cạnh thẳng.\n3. Với hình chữ nhật, hình vuông, kiểm tra góc và độ dài cạnh khi đã học các dụng cụ đo.",
    "Một hình có 4 góc vuông, hai cạnh dài 6 cm và hai cạnh còn lại dài 4 cm. Gọi tên hình.",
    [
        "Hình có bốn góc vuông nên là hình chữ nhật.",
        "Hai độ dài cạnh kề là 6 cm và 4 cm, không bằng nhau nên hình không phải hình vuông.",
    ],
    "Hình chữ nhật.",
    [
        "Một hình có 3 cạnh thẳng khép kín. Đó là hình gì?",
        "Một hình có 4 góc vuông và bốn cạnh cùng dài 3 cm. Đó là hình gì?",
    ],
    [
        (
            ["Đếm được 3 cạnh thẳng khép kín.", "Hình có ba cạnh là hình tam giác."],
            "Hình tam giác.",
        ),
        (
            [
                "Hình có bốn góc vuông và bốn cạnh bằng nhau.",
                "Đó là các đặc điểm của hình vuông.",
            ],
            "Hình vuông.",
        ),
    ],
    "Hình được xoay vẫn giữ tên; không gọi tên chỉ dựa vào hướng đặt.",
)
add(
    "solids",
    "Khối lập phương và khối hộp chữ nhật",
    "Khối lập phương có 6 mặt là các hình vuông bằng nhau. Khối hộp chữ nhật có 6 mặt là các hình chữ nhật, các mặt đối diện bằng nhau. Cả hai có 8 đỉnh và 12 cạnh.",
    "1. Quan sát mô hình hoặc hộp thật.\n2. Xác định các mặt, đỉnh, cạnh.\n3. Phân biệt bằng hình dạng và kích thước các mặt; xoay mô hình để không bỏ mặt khuất.",
    "Một con xúc xắc dạng khối lập phương có bao nhiêu mặt?",
    [
        "Quan sát và xoay mô hình khối lập phương.",
        "Đếm cả mặt trên, mặt dưới và bốn mặt xung quanh được 6 mặt.",
    ],
    "6 mặt.",
    [
        "Một hộp dạng khối hộp chữ nhật có bao nhiêu mặt?",
        "Khối có 6 mặt vuông bằng nhau là khối gì?",
    ],
    [
        (
            [
                "Đếm các cặp mặt đối diện của hộp được 3 cặp.",
                "Mỗi cặp có 2 mặt nên hộp có 6 mặt.",
            ],
            "6 mặt.",
        ),
        (
            [
                "Các mặt đều là hình vuông bằng nhau.",
                "Khối có đặc điểm đó là khối lập phương.",
            ],
            "Khối lập phương.",
        ),
    ],
    "Phân biệt hình phẳng với khối; không chỉ đếm những mặt đang nhìn thấy.",
)
add(
    "cylinder_sphere",
    "Khối trụ và khối cầu",
    "Quả bóng thường gợi hình khối cầu. Lon sữa có hai mặt đáy tròn bằng nhau và mặt xung quanh cong gợi hình khối trụ.",
    "1. Quan sát các mặt của vật.\n2. So sánh với mô hình khối trụ, khối cầu.\n3. Gọi dạng khối gần đúng của vật; không coi mọi vật tròn đều là khối cầu.",
    "Một quả bóng tròn và một lon nước có dạng khối nào?",
    [
        "Quả bóng tròn đều gợi dạng khối cầu.",
        "Lon nước có hai đáy tròn bằng nhau gợi dạng khối trụ.",
    ],
    "Quả bóng: khối cầu; lon nước: khối trụ.",
    [
        "Viên bi tròn có dạng khối gì?",
        "Hộp có hai đáy tròn bằng nhau và mặt bên cong gợi dạng khối gì?",
    ],
    [
        (
            [
                "Viên bi có dạng tròn đều như mô hình khối cầu.",
                "Vì vậy viên bi gợi dạng khối cầu.",
            ],
            "Khối cầu.",
        ),
        (
            [
                "Vật có hai đáy tròn bằng nhau và mặt xung quanh cong.",
                "Đặc điểm này phù hợp với mô hình khối trụ.",
            ],
            "Khối trụ.",
        ),
    ],
    "Không nhầm hình tròn (hình phẳng) với khối cầu (khối không gian).",
)
add(
    "perimeter",
    "Chu vi các hình",
    "Chu vi của hình có các cạnh thẳng là tổng độ dài các cạnh. Chu vi hình chữ nhật = (chiều dài + chiều rộng) × 2; chu vi hình vuông = cạnh × 4. Độ dài phải cùng đơn vị.",
    "1. Xác định các cạnh bao quanh hình.\n2. Đổi về cùng đơn vị rồi cộng hoặc dùng công thức phù hợp.\n3. Ghi đơn vị độ dài và đáp số.",
    "Tam giác có ba cạnh 3 cm, 4 cm, 5 cm. Tính chu vi.",
    ["Chu vi hình tam giác là:", "3 + 4 + 5 = 12 (cm)"],
    "12 cm.",
    [
        "Hình chữ nhật dài 8 cm, rộng 3 cm. Tính chu vi.",
        "Hình vuông có cạnh 5 cm. Tính chu vi.",
    ],
    [
        (["Chu vi hình chữ nhật là:", "(8 + 3) × 2 = 22 (cm)"], "22 cm."),
        (["Chu vi hình vuông là:", "5 × 4 = 20 (cm)"], "20 cm."),
    ],
    "Không nhầm chu vi với diện tích; phải tính đủ mọi cạnh bao quanh hình.",
)
add(
    "area_intro",
    "Diện tích và xăng-ti-mét vuông",
    "Diện tích chỉ phần mặt phẳng mà hình chiếm. Một hình vuông cạnh 1 cm có diện tích 1 cm². Có thể tính diện tích bằng cách đếm các ô vuông đơn vị không chồng nhau, phủ kín hình.",
    "1. Xác định ô vuông đơn vị.\n2. Đếm đủ các ô phủ hình, không đếm hai lần.\n3. Ghi số đo theo cm² khi mỗi ô có diện tích 1 cm².",
    "Một hình được ghép từ 6 ô vuông, mỗi ô có diện tích 1 cm², không chồng nhau. Tính diện tích hình.",
    [
        "Mỗi ô có diện tích 1 cm²; hình gồm 6 ô không chồng nhau.",
        "Diện tích hình là 6 cm².",
    ],
    "6 cm².",
    [
        "Hình A gồm 8 ô vuông 1 cm² không chồng nhau. Tính diện tích.",
        "Hình B có 5 ô, hình C có 7 ô cùng loại 1 cm². Hình nào có diện tích lớn hơn?",
    ],
    [
        (
            ["Hình có 8 ô, mỗi ô diện tích 1 cm².", "Diện tích hình A là 8 cm²."],
            "8 cm².",
        ),
        (
            [
                "Diện tích B là 5 cm²; diện tích C là 7 cm².",
                "Vì 7 lớn hơn 5 nên C có diện tích lớn hơn.",
            ],
            "Hình C.",
        ),
    ],
    "Các ô dùng để so sánh phải bằng nhau; cm² khác cm.",
)
add(
    "rectangle_area",
    "Diện tích hình chữ nhật, hình vuông",
    "Diện tích hình chữ nhật = chiều dài × chiều rộng (cùng đơn vị). Diện tích hình vuông = cạnh × cạnh. Đơn vị diện tích là đơn vị vuông.",
    "1. Xác định chiều dài và chiều rộng hoặc cạnh.\n2. Đổi cùng đơn vị rồi nhân.\n3. Viết câu lời giải, phép tính kèm đơn vị vuông và đáp số.",
    "Hình chữ nhật dài 7 cm, rộng 4 cm. Tính diện tích.",
    ["Diện tích hình chữ nhật là:", "7 × 4 = 28 (cm²)"],
    "28 cm².",
    [
        "Hình chữ nhật dài 9 cm, rộng 3 cm. Tính diện tích.",
        "Hình vuông cạnh 6 cm. Tính diện tích.",
    ],
    [
        (["Diện tích hình chữ nhật là:", "9 × 3 = 27 (cm²)"], "27 cm²."),
        (["Diện tích hình vuông là:", "6 × 6 = 36 (cm²)"], "36 cm²."),
    ],
    "Không dùng công thức chu vi thay cho diện tích.",
)
add(
    "two_steps",
    "Bài toán giải bằng hai bước tính",
    "Một số bài cần tìm kết quả trung gian trước khi trả lời câu hỏi cuối. Mỗi phép tính phải gắn với một ý nghĩa rõ ràng.",
    "1. Đọc dữ kiện và câu hỏi.\n2. Tìm đại lượng cần biết trước.\n3. Viết hai câu lời giải với phép tính tương ứng rồi đáp số.",
    "Buổi sáng cửa hàng bán 24 kg gạo, buổi chiều bán nhiều hơn buổi sáng 8 kg. Cả ngày bán bao nhiêu ki-lô-gam gạo?",
    [
        "Buổi chiều bán được số gạo là:",
        "24 + 8 = 32 (kg)",
        "Cả ngày bán được số gạo là:",
        "24 + 32 = 56 (kg)",
    ],
    "56 kg gạo.",
    [
        "Lan có 18 nhãn vở, Mai có ít hơn Lan 6 nhãn vở. Hai bạn có tất cả bao nhiêu nhãn vở?",
        "Có 4 túi, mỗi túi 6 quả cam. Đã ăn 5 quả. Còn lại bao nhiêu quả?",
    ],
    [
        (
            [
                "Mai có số nhãn vở là:",
                "18 − 6 = 12 (nhãn vở)",
                "Hai bạn có tất cả số nhãn vở là:",
                "18 + 12 = 30 (nhãn vở)",
            ],
            "30 nhãn vở.",
        ),
        (
            [
                "Lúc đầu có số quả cam là:",
                "4 × 6 = 24 (quả)",
                "Số quả cam còn lại là:",
                "24 − 5 = 19 (quả)",
            ],
            "19 quả cam.",
        ),
    ],
    "Không cộng tất cả số đã cho khi chưa hiểu mỗi số chỉ điều gì.",
)
add(
    "three_steps",
    "Bài toán có ba bước tính",
    "Bài toán ba bước cần xác định lần lượt các đại lượng trung gian; mỗi kết quả là dữ kiện cho bước tiếp theo.",
    "1. Tóm tắt dữ kiện.\n2. Tìm thứ tự ba phép tính.\n3. Mỗi bước có câu lời giải, phép tính và đơn vị; kết luận đáp số.",
    "Có 3 thùng, mỗi thùng 24 quyển vở. Mua thêm 18 quyển rồi chia đều cho 9 bạn. Mỗi bạn được mấy quyển?",
    [
        "Ba thùng có số quyển vở là:",
        "3 × 24 = 72 (quyển)",
        "Tổng số quyển vở sau khi mua thêm là:",
        "72 + 18 = 90 (quyển)",
        "Mỗi bạn được số quyển vở là:",
        "90 : 9 = 10 (quyển)",
    ],
    "10 quyển vở.",
    [
        "Có 4 hộp, mỗi hộp 15 bút. Thêm 20 bút rồi chia đều cho 8 bạn. Mỗi bạn được mấy bút?",
        "Có 5 túi, mỗi túi 12 viên bi. Cho đi 18 viên, số còn lại chia đều vào 6 hộp. Mỗi hộp có mấy viên?",
    ],
    [
        (
            [
                "Bốn hộp có số bút là:",
                "4 × 15 = 60 (bút)",
                "Tổng số bút là:",
                "60 + 20 = 80 (bút)",
                "Mỗi bạn được số bút là:",
                "80 : 8 = 10 (bút)",
            ],
            "10 bút.",
        ),
        (
            [
                "Năm túi có số viên bi là:",
                "5 × 12 = 60 (viên)",
                "Số bi còn lại là:",
                "60 − 18 = 42 (viên)",
                "Mỗi hộp có số viên bi là:",
                "42 : 6 = 7 (viên)",
            ],
            "7 viên bi.",
        ),
    ],
    "Kiểm tra đại lượng trung gian và đơn vị, không bỏ bước cần thiết.",
)
add(
    "remainder",
    "Phép chia hết, phép chia có dư",
    "Chia hết có số dư bằng 0. Chia có dư: số bị chia = số chia × thương + số dư; số dư bé hơn số chia và lớn hơn 0.",
    "1. Tìm tích gần số bị chia nhất nhưng không lớn hơn nó.\n2. Lấy số bị chia trừ tích đó để tìm dư.\n3. Kiểm tra dư bé hơn số chia.",
    "Chia đều 17 que tính thành các nhóm 5 que. Được mấy nhóm và còn thừa mấy que?",
    [
        "Ta có 5 × 3 = 15 và 5 × 4 = 20 lớn hơn 17.",
        "Số que còn thừa là:",
        "17 − 15 = 2 (que)",
        "Vậy 17 : 5 = 3 (dư 2).",
    ],
    "3 nhóm, thừa 2 que.",
    ["Tính 24 : 6 và cho biết có chia hết không.", "Tính 29 : 4 và kiểm tra số dư."],
    [
        (
            ["24 : 6 = 4 vì 6 × 4 = 24.", "Số dư bằng 0 nên đây là phép chia hết."],
            "4; chia hết.",
        ),
        (
            ["4 × 7 = 28; 29 − 28 = 1.", "Vậy 29 : 4 = 7 (dư 1); dư 1 bé hơn 4."],
            "7 dư 1.",
        ),
    ],
    "Số dư phải nhỏ hơn số chia, không thể bằng số chia.",
)
add(
    "multiply_compare",
    "Gấp một số và so sánh gấp mấy lần",
    "Muốn gấp một số lên một số lần, lấy số đó nhân với số lần. Muốn biết số lớn gấp mấy lần số bé, lấy số lớn chia cho số bé khác 0.",
    "1. Phân biệt tìm số mới hay tìm số lần.\n2. Gấp lên thì nhân; so sánh gấp mấy lần thì chia.\n3. Ghi đáp số đúng đại lượng.",
    "Một sợi dây dài 6 cm, sợi dây khác dài gấp 4 lần. Sợi dây thứ hai dài bao nhiêu?",
    ["Sợi dây thứ hai dài là:", "6 × 4 = 24 (cm)"],
    "24 cm.",
    [
        "Số lớn là 35, số bé là 7. Số lớn gấp mấy lần số bé?",
        "Gấp 8 lên 3 lần được số nào?",
    ],
    [
        (["Số lớn gấp số bé số lần là:", "35 : 7 = 5 (lần)"], "5 lần."),
        (["Số cần tìm là:", "8 × 3 = 24"], "24."),
    ],
    "Gấp 4 lần khác với thêm 4 đơn vị.",
)
add(
    "reduce_times",
    "Giảm một số đi một số lần",
    "Muốn giảm một số đi một số lần, lấy số đó chia cho số lần (khác 0). Giảm đi một số lần khác với bớt một số đơn vị.",
    "1. Đọc đúng số lần cần giảm.\n2. Chọn phép chia.\n3. Tính và kiểm tra bằng phép nhân.",
    "Một đoạn dây dài 24 cm. Sau khi cắt, độ dài còn lại bằng độ dài ban đầu giảm đi 3 lần. Đoạn còn lại dài bao nhiêu?",
    ["Đoạn dây còn lại dài là:", "24 : 3 = 8 (cm)", "Thử lại: 8 × 3 = 24."],
    "8 cm.",
    ["Giảm 42 đi 6 lần được số nào?", "Giảm 36 đi 4 lần được số nào?"],
    [
        (["Số cần tìm là:", "42 : 6 = 7"], "7."),
        (["Số cần tìm là:", "36 : 4 = 9"], "9."),
    ],
    "Giảm 6 lần phải chia cho 6, không trừ 6.",
)
add(
    "roman",
    "Chữ số La Mã",
    "Các chữ số I, V, X biểu thị 1, 5, 10. Trong phạm vi đã học: IV là 4, IX là 9; các số như VI = 6, XI = 11, XII = 12.",
    "1. Nhận biết I, V, X.\n2. Đọc theo các nhóm đã học; chú ý IV và IX.\n3. Đối chiếu với số tự nhiên, không ghép tùy ý.",
    "Đọc các số IV, VIII, XII.",
    ["IV là 4; VIII gồm V và III nên là 8.", "XII gồm X và II nên là 12."],
    "4; 8; 12.",
    ["Viết 9 và 11 bằng chữ số La Mã.", "Sắp xếp II, VI, IV theo thứ tự tăng dần."],
    [
        (["9 viết là IX; 11 gồm X và I.", "Vì vậy 11 viết là XI."], "IX; XI."),
        (
            ["II = 2, VI = 6, IV = 4.", "Vì 2 < 4 < 6 nên thứ tự là II, IV, VI."],
            "II; IV; VI.",
        ),
    ],
    "Không viết 4 thành IIII trong cách viết đang học.",
)
add(
    "clock",
    "Xem đồng hồ",
    "Một giờ có 60 phút. Kim ngắn chỉ giờ, kim dài chỉ phút; mỗi khoảng giữa hai số liền nhau trên mặt đồng hồ ứng với 5 phút.",
    "1. Xem kim ngắn ở số nào hoặc giữa hai số nào.\n2. Đếm số phút theo kim dài.\n3. Đọc giờ và phút; chú ý kim giờ đã đi một phần quãng đường.",
    "Kim phút chỉ số 6, kim giờ ở giữa 8 và 9. Đồng hồ chỉ mấy giờ?",
    [
        "Kim phút chỉ số 6 nên số phút là 6 × 5 = 30 phút.",
        "Kim giờ ở giữa 8 và 9 nên đồng hồ chỉ 8 giờ 30 phút.",
    ],
    "8 giờ 30 phút.",
    [
        "Kim phút chỉ số 3, kim giờ vừa qua số 7. Đồng hồ chỉ mấy giờ?",
        "Một tiết học bắt đầu lúc 9 giờ, kéo dài 35 phút. Kết thúc lúc nào?",
    ],
    [
        (
            [
                "Kim phút chỉ số 3 ứng với 15 phút.",
                "Kim giờ vừa qua 7 nên thời gian là 7 giờ 15 phút.",
            ],
            "7 giờ 15 phút.",
        ),
        (
            ["Bắt đầu lúc 9 giờ, thêm 35 phút.", "Kết thúc lúc 9 giờ 35 phút."],
            "9 giờ 35 phút.",
        ),
    ],
    "Kim dài chỉ số 6 là 30 phút, không phải 6 phút.",
)
add(
    "calendar",
    "Ngày, tháng, năm và xem lịch",
    "Một tuần có 7 ngày. Một năm có 12 tháng. Các tháng 4, 6, 9, 11 có 30 ngày; tháng 2 có 28 hoặc 29 ngày; các tháng còn lại có 31 ngày.",
    "1. Xác định tháng, năm trên tờ lịch.\n2. Tìm ngày rồi đọc thứ ở đúng cột.\n3. Khi tính ngày tiếp theo, chú ý hết tháng và thứ lặp sau 7 ngày.",
    "Ngày 10 là thứ Hai. Ngày 17 cùng tháng là thứ mấy?",
    [
        "Từ ngày 10 đến ngày 17 cách nhau:",
        "17 − 10 = 7 (ngày)",
        "Sau 7 ngày thì thứ lặp lại nên ngày 17 cũng là thứ Hai.",
    ],
    "Thứ Hai.",
    ["Ngày tiếp sau ngày 30 tháng 4 là ngày nào?", "Tháng 9 có bao nhiêu ngày?"],
    [
        (
            [
                "Tháng 4 có 30 ngày.",
                "Ngày sau ngày cuối tháng là ngày đầu tháng tiếp theo.",
            ],
            "Ngày 1 tháng 5.",
        ),
        (
            ["Tháng 9 thuộc nhóm tháng có 30 ngày.", "Vậy tháng 9 có 30 ngày."],
            "30 ngày.",
        ),
    ],
    "Không coi mọi tháng đều có 30 ngày; xem đúng tháng và năm.",
)
add(
    "money",
    "Tiền Việt Nam",
    "Đơn vị tiền Việt Nam là đồng. Tổng tiền bằng tổng giá trị các tờ tiền; tiền thừa bằng số tiền đưa trừ số tiền phải trả.",
    "1. Đọc mệnh giá từng tờ, không chỉ đếm số tờ.\n2. Cộng tổng tiền.\n3. Nếu mua hàng, tính số tiền phải trả và tiền còn lại.",
    "Em có một tờ 10 000 đồng và một tờ 5 000 đồng, mua vở hết 8 000 đồng. Còn bao nhiêu tiền?",
    [
        "Tổng số tiền em có là:",
        "10 000 + 5 000 = 15 000 (đồng)",
        "Số tiền còn lại là:",
        "15 000 − 8 000 = 7 000 (đồng)",
    ],
    "7 000 đồng.",
    [
        "Hai tờ 2 000 đồng và một tờ 5 000 đồng có tổng bao nhiêu tiền?",
        "Đưa 20 000 đồng mua hàng hết 13 000 đồng. Nhận lại bao nhiêu tiền?",
    ],
    [
        (
            [
                "Hai tờ 2 000 đồng có giá trị 4 000 đồng.",
                "Tổng số tiền là:",
                "4 000 + 5 000 = 9 000 (đồng)",
            ],
            "9 000 đồng.",
        ),
        (["Số tiền được trả lại là:", "20 000 − 13 000 = 7 000 (đồng)"], "7 000 đồng."),
    ],
    "Nhiều tờ tiền hơn chưa chắc có giá trị lớn hơn.",
)
add(
    "data",
    "Thu thập, phân loại, bảng số liệu",
    "Mỗi quan sát phải được ghi nhận đúng một lần. Phân loại theo cùng một tiêu chí; cộng các số đếm để kiểm tra đủ dữ liệu.",
    "1. Chọn tiêu chí.\n2. Đọc từng kết quả và ghi vào đúng nhóm.\n3. Lập bảng, tính tổng và trả lời câu hỏi từ số liệu.",
    "Có các thẻ: đỏ, xanh, đỏ, vàng, xanh, đỏ. Lập bảng đếm theo màu.",
    [
        "Đếm được đỏ: 3 thẻ; xanh: 2 thẻ; vàng: 1 thẻ.",
        "Kiểm tra: 3 + 2 + 1 = 6 (thẻ), đúng bằng số thẻ ban đầu.",
    ],
    "Đỏ: 3; xanh: 2; vàng: 1.",
    [
        "Số liệu 2, 4, 2, 3, 4, 2 có mấy số 2?",
        "Bảng ghi tổ Một: 8 bạn, tổ Hai: 9 bạn, tổ Ba: 7 bạn. Có tất cả mấy bạn?",
    ],
    [
        (
            ["Số 2 xuất hiện ở vị trí thứ nhất, thứ ba và thứ sáu.", "Đếm được 3 lần."],
            "3 lần.",
        ),
        (["Tổng số bạn là:", "8 + 9 + 7 = 24 (bạn)"], "24 bạn."),
    ],
    "Không bỏ lần lặp lại và không tự thêm số liệu ngoài bảng.",
)
add(
    "chance",
    "Khả năng xảy ra của sự kiện",
    "Chắc chắn: nhất định xảy ra trong tình huống đã cho. Không thể: không có khả năng xảy ra. Có thể: có khả năng xảy ra nhưng không chắc chắn.",
    "1. Xem tất cả kết quả có thể của tình huống.\n2. Đối chiếu sự kiện cần xét.\n3. Chọn chắc chắn, có thể hoặc không thể và giải thích.",
    "Túi chỉ có 3 viên bi đỏ. Lấy một viên không nhìn. Có lấy được bi xanh không?",
    [
        "Trong túi không có viên bi xanh.",
        "Vì vậy lấy được bi xanh là sự kiện không thể xảy ra.",
    ],
    "Không thể.",
    [
        "Túi có 2 bi đỏ và 1 bi xanh. Lấy một viên có thể được bi đỏ không?",
        "Hộp chỉ có bút chì. Lấy một đồ vật trong hộp thì có chắc chắn là bút chì không?",
    ],
    [
        (
            [
                "Túi có bi đỏ nên có khả năng lấy được bi đỏ.",
                "Nhưng cũng có bi xanh nên không chắc chắn lấy được bi đỏ.",
            ],
            "Có thể.",
        ),
        (
            [
                "Mọi đồ vật trong hộp đều là bút chì.",
                "Lấy bất kì đồ vật nào trong hộp cũng được bút chì.",
            ],
            "Chắc chắn.",
        ),
    ],
    "Có thể không có nghĩa là chắc chắn; không suy đoán kết quả lần sau từ một lần thử.",
)
add(
    "position",
    "Vị trí và định hướng",
    "Có thể mô tả vị trí bằng trên, dưới, trước, sau, bên trái, bên phải. Khi xác định trái, phải cần nói rõ theo hướng nhìn của ai.",
    "1. Chọn vật hoặc người làm mốc.\n2. Xác định hướng nhìn.\n3. Nói rõ vị trí so với mốc.",
    "Ba bạn đứng cùng hướng: An ở bên trái Bình, Chi ở bên phải Bình. Ai ở giữa?",
    ["Theo thứ tự từ trái sang phải là An, Bình, Chi.", "Bình đứng giữa An và Chi."],
    "Bình.",
    [
        "Sách nằm trên bàn, cặp nằm dưới bàn. Vật nào ở dưới bàn?",
        "Ba thẻ theo thứ tự trái sang phải là đỏ, vàng, xanh. Thẻ nào ở bên trái thẻ vàng?",
    ],
    [
        (["Chọn bàn làm mốc.", "Theo mô tả, cặp nằm dưới bàn."], "Cặp."),
        (
            ["Thứ tự là đỏ, vàng, xanh.", "Thẻ đứng trước vàng theo phía trái là đỏ."],
            "Thẻ đỏ.",
        ),
    ],
    "Không đổi hướng nhìn giữa chừng khi dùng trái và phải.",
)
add(
    "simple_shapes",
    "Các hình phẳng quen thuộc",
    "Hình tam giác có 3 cạnh thẳng; hình vuông và hình chữ nhật có 4 cạnh thẳng. Hình vuông có 4 cạnh bằng nhau. Hình tròn có đường bao cong.",
    "1. Quan sát đường bao hình.\n2. Đếm cạnh thẳng nếu có.\n3. So sánh với các hình mẫu; hình xoay đi vẫn giữ tên.",
    "Một hình có ba cạnh thẳng khép kín. Đó là hình gì?",
    ["Đếm được 3 cạnh thẳng.", "Hình có ba cạnh thẳng khép kín là hình tam giác."],
    "Hình tam giác.",
    [
        "Hình có đường bao cong tròn khép kín, không có góc nhọn, gợi hình gì?",
        "Một hình vuông có bao nhiêu cạnh?",
    ],
    [
        (
            [
                "Đường bao cong tròn phù hợp với hình tròn.",
                "Hình không có các cạnh thẳng như tam giác hay hình vuông.",
            ],
            "Hình tròn.",
        ),
        (
            ["Quan sát và đếm lần lượt các cạnh của hình vuông.", "Đếm được bốn cạnh."],
            "4 cạnh.",
        ),
    ],
    "Không gọi tên hình chỉ dựa vào màu hoặc kích thước.",
)
add(
    "segments",
    "Điểm, đoạn thẳng, đường thẳng và đường cong",
    "Điểm được đánh dấu và đặt tên bằng chữ in hoa. Đoạn thẳng có hai đầu mút. Đường thẳng kéo dài về hai phía. Đường cong không thẳng. Ba điểm thẳng hàng cùng nằm trên một đường thẳng.",
    "1. Tìm các điểm được đánh dấu.\n2. Xác định hai đầu mút của đoạn.\n3. Dùng thước kiểm tra độ thẳng và đo từ vạch 0 khi cần.",
    "Vẽ hai điểm A và B rồi nối bằng thước. Đoạn thẳng đó được gọi tên thế nào?",
    [
        "Hai đầu mút là A và B.",
        "Đoạn nối hai điểm bằng nét thẳng được gọi là đoạn thẳng AB.",
    ],
    "Đoạn thẳng AB.",
    [
        "A, B, C cùng nằm trên một đường thẳng. Ba điểm đó có thẳng hàng không?",
        "Một đoạn bắt đầu ở vạch 0 cm và kết thúc ở vạch 5 cm trên thước. Dài bao nhiêu?",
    ],
    [
        (
            [
                "Cả A, B, C đều nằm trên cùng đường thẳng.",
                "Theo định nghĩa, đó là ba điểm thẳng hàng.",
            ],
            "Có, ba điểm thẳng hàng.",
        ),
        (["Đọc thước từ vạch 0 đến vạch 5 cm.", "Độ dài đoạn là 5 cm."], "5 cm."),
    ],
    "Không nhầm đoạn thẳng có hai đầu mút với đường thẳng kéo dài.",
)
add(
    "broken_line",
    "Đường gấp khúc và hình tứ giác",
    "Đường gấp khúc gồm các đoạn thẳng nối tiếp nhau. Độ dài đường gấp khúc bằng tổng độ dài các đoạn. Hình tứ giác có bốn cạnh.",
    "1. Xác định các đoạn nối tiếp.\n2. Cộng độ dài các đoạn cùng đơn vị.\n3. Với hình khép kín, đếm số cạnh để nhận biết tứ giác.",
    "Đường gấp khúc ABC có AB = 3 cm, BC = 4 cm. Tính độ dài.",
    ["Độ dài đường gấp khúc ABC là:", "3 + 4 = 7 (cm)"],
    "7 cm.",
    [
        "Đường gấp khúc gồm các đoạn 2 cm, 5 cm, 3 cm. Dài bao nhiêu?",
        "Một hình khép kín có bốn cạnh thẳng. Gọi tên hình.",
    ],
    [
        (["Độ dài đường gấp khúc là:", "2 + 5 + 3 = 10 (cm)"], "10 cm."),
        (["Hình có bốn cạnh thẳng khép kín.", "Đó là hình tứ giác."], "Hình tứ giác."),
    ],
    "Cộng đủ từng đoạn, không chỉ đo khoảng cách giữa hai đầu đường gấp khúc.",
)
add(
    "drawing",
    "Thực hành gấp, ghép và vẽ đoạn thẳng",
    "Vẽ đoạn thẳng cần hai đầu mút và thước. Khi ghép hình, các mảnh không chồng lên nhau, không để hở phần cần phủ.",
    "1. Chuẩn bị thước và giấy; dùng kéo theo hướng dẫn của người lớn.\n2. Vẽ từ vạch 0 theo độ dài yêu cầu hoặc xếp thử các mảnh.\n3. Đo lại, kiểm tra hình đã ghép.",
    "Vẽ đoạn thẳng AB dài 5 cm.",
    [
        "Chấm điểm A trùng vạch 0 của thước.",
        "Chấm B ở vạch 5 cm rồi nối A với B bằng cạnh thước.",
        "Đo lại để kiểm tra.",
    ],
    "Đoạn AB dài 5 cm (học sinh tự vẽ).",
    [
        "Vẽ đoạn CD dài 3 cm.",
        "Một hình vuông được cắt theo đường chéo thành hai mảnh. Ghép lại có giữ nguyên hình ban đầu không?",
    ],
    [
        (
            ["Đặt C ở vạch 0, D ở vạch 3 cm.", "Nối C với D rồi kiểm tra bằng thước."],
            "Đoạn CD dài 3 cm.",
        ),
        (
            [
                "Đặt hai mảnh theo đúng đường cắt, không chồng lên nhau.",
                "Hai mảnh phủ kín hình vuông ban đầu.",
            ],
            "Có, nếu ghép đúng theo đường cắt.",
        ),
    ],
    "Không bắt đầu đo từ mép thước khi mép không trùng vạch 0.",
)
add(
    "week",
    "Ngày trong tuần",
    "Một tuần có bảy ngày: thứ Hai, thứ Ba, thứ Tư, thứ Năm, thứ Sáu, thứ Bảy, Chủ nhật. Sau Chủ nhật là thứ Hai của tuần tiếp theo.",
    "1. Đọc thứ của ngày đã biết.\n2. Đếm theo đúng thứ tự bảy ngày.\n3. Phân biệt hôm qua, hôm nay, ngày mai.",
    "Hôm nay là thứ Tư. Ngày mai là thứ mấy?",
    ["Theo thứ tự, sau thứ Tư là thứ Năm.", "Vì vậy ngày mai là thứ Năm."],
    "Thứ Năm.",
    ["Hôm nay là thứ Hai. Hôm qua là thứ mấy?", "Một tuần có bao nhiêu ngày?"],
    [
        (["Ngày trước thứ Hai là Chủ nhật.", "Vậy hôm qua là Chủ nhật."], "Chủ nhật."),
        (["Đếm từ thứ Hai đến Chủ nhật.", "Có tất cả bảy ngày."], "7 ngày."),
    ],
    "Sau Chủ nhật phải chuyển sang thứ Hai, không dừng việc đếm.",
)
add(
    "clock_whole",
    "Xem giờ đúng",
    "Khi kim dài chỉ số 12, đồng hồ chỉ giờ đúng. Kim ngắn chỉ số nào thì đọc giờ theo số đó.",
    "1. Phân biệt kim dài và kim ngắn.\n2. Kiểm tra kim dài ở số 12.\n3. Đọc số mà kim ngắn đang chỉ.",
    "Kim dài chỉ 12, kim ngắn chỉ 7. Đồng hồ chỉ mấy giờ?",
    ["Kim dài ở số 12 nên đây là giờ đúng.", "Kim ngắn chỉ 7 nên đồng hồ chỉ 7 giờ."],
    "7 giờ.",
    [
        "Kim dài chỉ 12, kim ngắn chỉ 3. Đọc giờ.",
        "Muốn đồng hồ chỉ 9 giờ đúng, đặt hai kim thế nào?",
    ],
    [
        (["Kim dài chỉ 12 là giờ đúng.", "Kim ngắn chỉ 3 nên đọc 3 giờ."], "3 giờ."),
        (
            ["Đặt kim dài ở số 12.", "Đặt kim ngắn ở số 9."],
            "Kim dài chỉ 12, kim ngắn chỉ 9.",
        ),
    ],
    "Không đọc số 12 thành số giờ khi đó là vị trí của kim dài.",
)
add(
    "even_odd",
    "Số chẵn, số lẻ",
    "Số chẵn có chữ số tận cùng là 0, 2, 4, 6, 8. Số lẻ có chữ số tận cùng là 1, 3, 5, 7, 9. Số 0 là số chẵn.",
    "1. Xem chữ số hàng đơn vị.\n2. Đối chiếu hai nhóm chữ số.\n3. Kết luận chẵn hoặc lẻ.",
    "Phân loại các số 124, 307, 560.",
    ["124 tận cùng 4 nên chẵn; 307 tận cùng 7 nên lẻ.", "560 tận cùng 0 nên chẵn."],
    "Chẵn: 124, 560; lẻ: 307.",
    ["Số 1 235 chẵn hay lẻ?", "Viết ba số chẵn liên tiếp bắt đầu từ 18."],
    [
        (
            ["Chữ số tận cùng của 1 235 là 5.", "5 thuộc nhóm tận cùng của số lẻ."],
            "Số lẻ.",
        ),
        (
            [
                "Các số chẵn liên tiếp hơn kém nhau 2.",
                "Từ 18, cộng 2 được 20; cộng 2 nữa được 22.",
            ],
            "18; 20; 22.",
        ),
    ],
    "Xét chữ số hàng đơn vị, không xét tổng các chữ số.",
)
add(
    "letter_expression",
    "Biểu thức chứa chữ",
    "Biểu thức chứa chữ có giá trị khi thay chữ bằng số. Cùng một chữ trong biểu thức phải thay bằng cùng một số ở mỗi lần tính.",
    "1. Đọc giá trị của chữ đã cho.\n2. Thay vào đúng vị trí.\n3. Tính theo thứ tự phép tính rồi nêu kết quả.",
    "Tính 3 × a + 5 với a = 4.",
    [
        "Thay a bằng 4:",
        "3 × a + 5 = 3 × 4 + 5.",
        "Nhân trước, cộng sau:",
        "3 × 4 + 5 = 12 + 5 = 17.",
    ],
    "17.",
    ["Tính b − 18 với b = 50.", "Tính (m + 6) : 3 với m = 12."],
    [
        (["Thay b bằng 50.", "50 − 18 = 32."], "32."),
        (["Thay m bằng 12.", "(12 + 6) : 3 = 18 : 3 = 6."], "6."),
    ],
    "Thay chữ trước khi tính; không bỏ qua dấu ngoặc.",
)
add(
    "angle_degree",
    "Đo góc và phân loại góc",
    "Đơn vị đo góc là độ, kí hiệu °. Góc vuông 90°, góc bẹt 180°. Góc nhọn bé hơn 90°; góc tù lớn hơn 90° và bé hơn 180°.",
    "1. Đặt tâm thước đo góc trùng đỉnh góc.\n2. Đặt vạch 0 trùng một cạnh.\n3. Đọc theo thang có vạch 0 vừa chọn, rồi so sánh với 90° và 180°.",
    "Phân loại các góc có số đo 45°, 90°, 120°, 180°.",
    [
        "45° bé hơn 90° nên là góc nhọn; 90° là góc vuông.",
        "120° lớn hơn 90° và bé hơn 180° nên là góc tù; 180° là góc bẹt.",
    ],
    "Nhọn; vuông; tù; bẹt.",
    [
        "Góc 60° là góc gì?",
        "Khi đo góc, cạnh đầu đi qua vạch 0 của thang trong. Cạnh kia đi qua 130° thang trong và 50° thang ngoài. Đọc số đo góc.",
    ],
    [
        (["60° bé hơn 90°.", "Vì vậy góc đó là góc nhọn."], "Góc nhọn."),
        (
            [
                "Phải đọc cùng thang có vạch 0 đã chọn.",
                "Cạnh đầu dùng thang trong nên đọc 130°.",
            ],
            "130°; không đọc thang ngoài ở lần đo này.",
        ),
    ],
    "Không đọc nhầm hai thang số trên thước đo góc.",
)
add(
    "perpendicular",
    "Hai đường thẳng vuông góc",
    "Hai đường thẳng vuông góc cắt nhau tạo thành các góc vuông. Có thể dùng ê-ke để kiểm tra hoặc vẽ.",
    "1. Dùng ê-ke kiểm tra góc tại giao điểm.\n2. Khi vẽ, đặt một cạnh góc vuông trùng đường đã cho.\n3. Kẻ theo cạnh góc vuông còn lại, kéo dài hai phía nếu cần.",
    "Nêu cách vẽ đường thẳng qua điểm A thuộc đường thẳng d và vuông góc với d.",
    [
        "Đặt đỉnh góc vuông của ê-ke ở A, một cạnh trùng d.",
        "Kẻ đường thẳng theo cạnh góc vuông còn lại.",
        "Hai đường tạo góc vuông tại A nên đường mới vuông góc d.",
    ],
    "Đường qua A vẽ theo cạnh ê-ke còn lại.",
    [
        "Hai đường cắt nhau tạo góc 90°. Chúng có vuông góc không?",
        "Hai cạnh kề của hình chữ nhật có quan hệ gì?",
    ],
    [
        (
            ["Góc 90° là góc vuông.", "Hai đường tạo góc vuông nên vuông góc nhau."],
            "Có, hai đường vuông góc.",
        ),
        (
            [
                "Hai cạnh kề hình chữ nhật tạo thành góc vuông.",
                "Do đó chúng vuông góc nhau.",
            ],
            "Vuông góc.",
        ),
    ],
    "Hai đường cắt nhau chưa chắc vuông góc; phải kiểm tra góc vuông.",
)
add(
    "parallel",
    "Hai đường thẳng song song",
    "Hai đường thẳng song song trong mặt phẳng không cắt nhau dù kéo dài về hai phía. Hai cạnh đối diện của hình chữ nhật nằm trên hai đường thẳng song song.",
    "1. Nhận biết đường cần song song.\n2. Có thể dùng ê-ke và thước để vẽ một đường vuông góc trung gian, rồi đường thứ hai vuông góc với đường trung gian.\n3. Kiểm tra đường mới đi qua điểm yêu cầu.",
    "Hình chữ nhật ABCD có các đỉnh theo thứ tự. Nêu hai cặp cạnh song song.",
    [
        "AB và CD là hai cạnh đối diện.",
        "AD và BC là hai cạnh đối diện còn lại nên mỗi cặp nằm trên hai đường song song.",
    ],
    "AB song song CD; AD song song BC.",
    [
        "Hai đường thẳng cắt nhau có song song không?",
        "Nêu cách vẽ đường qua A ngoài d và song song d bằng hai lần dựng vuông góc.",
    ],
    [
        (
            [
                "Hai đường song song không cắt nhau.",
                "Hai đường đã cắt nhau nên không song song.",
            ],
            "Không.",
        ),
        (
            [
                "Qua A vẽ đường h vuông góc d.",
                "Qua A vẽ đường k vuông góc h; khi đó k song song d.",
            ],
            "Đường k qua A và song song d.",
        ),
    ],
    "Không kết luận song song chỉ vì đoạn vẽ ngắn chưa gặp nhau.",
)
add(
    "parallelogram",
    "Hình bình hành và hình thoi",
    "Hình bình hành có hai cặp cạnh đối diện song song và bằng nhau. Hình thoi có bốn cạnh bằng nhau, các cặp cạnh đối diện song song.",
    "1. Xác định các cạnh đối diện.\n2. Kiểm tra song song và độ dài.\n3. Nếu bốn cạnh bằng nhau và có đặc điểm hình bình hành thì nhận biết hình thoi.",
    "ABCD là hình bình hành, AB = 7 cm, BC = 4 cm. Tìm CD và AD.",
    [
        "Các cạnh đối diện của hình bình hành bằng nhau.",
        "Vậy CD = AB = 7 cm; AD = BC = 4 cm.",
    ],
    "CD = 7 cm; AD = 4 cm.",
    [
        "Hình thoi có cạnh 5 cm. Ba cạnh còn lại dài bao nhiêu?",
        "Trong hình bình hành, hai cạnh đối diện có song song không?",
    ],
    [
        (
            [
                "Hình thoi có bốn cạnh bằng nhau.",
                "Một cạnh dài 5 cm nên mỗi cạnh còn lại cũng dài 5 cm.",
            ],
            "Mỗi cạnh còn lại dài 5 cm.",
        ),
        (
            [
                "Hai cặp cạnh đối diện song song là đặc điểm hình bình hành.",
                "Vì vậy hai cạnh đối diện song song nhau.",
            ],
            "Có.",
        ),
    ],
    "Hình thoi không nhất thiết có bốn góc vuông.",
)
add(
    "sum_difference",
    "Tìm hai số biết tổng và hiệu",
    "Số bé = (tổng − hiệu) : 2; số lớn = (tổng + hiệu) : 2. Có thể tìm một số rồi lấy tổng trừ số đó để tìm số còn lại.",
    "1. Xác định tổng, hiệu.\n2. Tìm số bé hoặc số lớn theo quy tắc.\n3. Tìm số còn lại, thử lại tổng và hiệu.",
    "Tổng hai số là 48, hiệu là 12. Tìm hai số.",
    [
        "Số bé là:",
        "(48 − 12) : 2 = 18",
        "Số lớn là:",
        "48 − 18 = 30",
        "Kiểm tra: 18 + 30 = 48; 30 − 18 = 12.",
    ],
    "Số bé: 18; số lớn: 30.",
    ["Tổng 70, hiệu 10. Tìm hai số.", "Tổng 96, hiệu 24. Tìm hai số."],
    [
        (
            ["Số bé là:", "(70 − 10) : 2 = 30", "Số lớn là:", "70 − 30 = 40"],
            "30 và 40.",
        ),
        (
            ["Số bé là:", "(96 − 24) : 2 = 36", "Số lớn là:", "96 − 36 = 60"],
            "36 và 60.",
        ),
    ],
    "Không nhầm bài biết tổng và hiệu với bài biết tổng và tỉ số.",
)
add(
    "mean",
    "Số trung bình cộng",
    "Muốn tìm số trung bình cộng của nhiều số, lấy tổng các số đó chia cho số các số hạng.",
    "1. Cộng tất cả số đã cho.\n2. Đếm đúng số số hạng.\n3. Chia tổng cho số số hạng; ghi đúng đơn vị.",
    "Ba ngày một cửa hàng bán 12, 15, 18 kg gạo. Trung bình mỗi ngày bán bao nhiêu?",
    [
        "Ba ngày bán số gạo là:",
        "12 + 15 + 18 = 45 (kg)",
        "Trung bình mỗi ngày bán số gạo là:",
        "45 : 3 = 15 (kg)",
    ],
    "15 kg.",
    [
        "Tìm trung bình cộng của 20 và 30.",
        "Ba lớp trồng 24, 27, 30 cây. Trung bình mỗi lớp trồng bao nhiêu?",
    ],
    [
        (["Tổng hai số là 20 + 30 = 50.", "Trung bình cộng là 50 : 2 = 25."], "25."),
        (
            [
                "Tổng số cây là:",
                "24 + 27 + 30 = 81 (cây)",
                "Trung bình mỗi lớp trồng là:",
                "81 : 3 = 27 (cây)",
            ],
            "27 cây.",
        ),
    ],
    "Chia cho số số hạng, không chia cho số lớn nhất hoặc số ngày không liên quan.",
)
add(
    "unit_method",
    "Bài toán rút về đơn vị",
    "Nếu mỗi phần bằng nhau, tìm giá trị một phần bằng cách lấy tổng giá trị chia cho số phần; sau đó tìm số phần hoặc giá trị cần hỏi.",
    "1. Xác định các phần bằng nhau.\n2. Tính giá trị một phần.\n3. Nhân hoặc chia tiếp theo câu hỏi.",
    "Ba quyển vở cùng loại giá 18 000 đồng. Năm quyển giá bao nhiêu?",
    [
        "Một quyển vở giá là:",
        "18 000 : 3 = 6 000 (đồng)",
        "Năm quyển vở giá là:",
        "6 000 × 5 = 30 000 (đồng)",
    ],
    "30 000 đồng.",
    [
        "Bốn túi có 28 kg gạo như nhau. Bảy túi có bao nhiêu?",
        "Năm hộp có 40 bút như nhau. Muốn có 24 bút cần mấy hộp?",
    ],
    [
        (
            [
                "Mỗi túi có số gạo là:",
                "28 : 4 = 7 (kg)",
                "Bảy túi có số gạo là:",
                "7 × 7 = 49 (kg)",
            ],
            "49 kg.",
        ),
        (
            [
                "Mỗi hộp có số bút là:",
                "40 : 5 = 8 (bút)",
                "Số hộp cần là:",
                "24 : 8 = 3 (hộp)",
            ],
            "3 hộp.",
        ),
    ],
    "Bước đầu phải đưa về một phần; không giả sử các phần bằng nhau nếu đề không cho.",
)
add(
    "fractions_intro",
    "Phân số và phép chia",
    "Chia một đơn vị thành các phần bằng nhau; phân số có mẫu số chỉ số phần bằng nhau, tử số chỉ số phần được lấy. Thương a : b có thể viết a/b với b khác 0.",
    "1. Kiểm tra các phần bằng nhau.\n2. Đếm tổng số phần làm mẫu, số phần lấy làm tử.\n3. Đọc tử trước, mẫu sau; khi viết thương, giữ đúng thứ tự.",
    "Một chiếc bánh chia thành 4 phần bằng nhau, lấy 3 phần. Viết phân số chỉ phần bánh đã lấy.",
    ["Bánh chia thành 4 phần bằng nhau nên mẫu số là 4.", "Lấy 3 phần nên tử số là 3."],
    "3/4 chiếc bánh.",
    [
        "Viết thương 5 : 6 dưới dạng phân số.",
        "Một đơn vị chia 8 phần bằng nhau, lấy 2 phần. Viết phân số.",
    ],
    [
        (["Số bị chia làm tử, số chia làm mẫu.", "5 : 6 = 5/6."], "5/6."),
        (
            [
                "Tổng số phần bằng nhau là 8, số phần lấy là 2.",
                "Phân số biểu thị là 2/8.",
            ],
            "2/8.",
        ),
    ],
    "Mẫu số không được bằng 0 và các phần của một đơn vị phải bằng nhau.",
)
add(
    "fraction_equal",
    "Tính chất cơ bản của phân số",
    "Nhân cả tử và mẫu với cùng một số tự nhiên khác 0 được phân số bằng phân số đã cho. Chia cả tử và mẫu cho cùng một ước chung khác 0 cũng giữ nguyên giá trị.",
    "1. Chọn cùng một số để nhân hoặc chia ở cả tử và mẫu.\n2. Thực hiện đủ hai phép tính.\n3. Kiểm tra phân số mới bằng phân số cũ.",
    "Viết một phân số bằng 2/3 có mẫu số 12.",
    ["Vì 3 × 4 = 12, nhân cả tử và mẫu với 4.", "2/3 = (2 × 4)/(3 × 4) = 8/12."],
    "8/12.",
    ["Viết phân số bằng 3/5 có mẫu số 20.", "Chia tử và mẫu của 12/18 cho 6."],
    [
        (["Vì 5 × 4 = 20, nhân tử và mẫu với 4.", "3/5 = 12/20."], "12/20."),
        (["12 : 6 = 2; 18 : 6 = 3.", "12/18 = 2/3."], "2/3."),
    ],
    "Không nhân tử và mẫu với hai số khác nhau.",
)
add(
    "common_denominator",
    "Quy đồng mẫu số",
    "Quy đồng là viết các phân số thành các phân số bằng chúng nhưng có cùng mẫu số. Có thể chọn tích hai mẫu làm mẫu chung hoặc chọn mẫu lớn nếu nó chia hết cho mẫu bé.",
    "1. Chọn mẫu chung.\n2. Tìm thừa số cần nhân ở mỗi phân số.\n3. Nhân cả tử và mẫu, giữ nguyên giá trị từng phân số.",
    "Quy đồng mẫu số 1/2 và 2/3.",
    [
        "Chọn mẫu chung 6.",
        "1/2 = (1 × 3)/(2 × 3) = 3/6.",
        "2/3 = (2 × 2)/(3 × 2) = 4/6.",
    ],
    "3/6 và 4/6.",
    ["Quy đồng 1/3 và 1/4.", "Quy đồng 3/5 và 7/10."],
    [
        (["Chọn mẫu chung 12.", "1/3 = 4/12; 1/4 = 3/12."], "4/12 và 3/12."),
        (
            ["Chọn mẫu chung 10 vì 10 chia hết cho 5.", "3/5 = 6/10; giữ nguyên 7/10."],
            "6/10 và 7/10.",
        ),
    ],
    "Không thay mẫu mà giữ nguyên tử.",
)
add(
    "fraction_compare",
    "So sánh phân số",
    "Cùng mẫu: so sánh tử số. Khác mẫu: có thể quy đồng rồi so sánh tử. Phân số có tử bằng mẫu thì bằng 1; tử bé hơn mẫu thì bé hơn 1.",
    "1. Xem hai mẫu số.\n2. Quy đồng nếu cần.\n3. So sánh và kết luận bằng dấu <, > hoặc =.",
    "So sánh 2/3 và 3/4.",
    ["Quy đồng: 2/3 = 8/12; 3/4 = 9/12.", "Vì 8 < 9 nên 8/12 < 9/12."],
    "2/3 < 3/4.",
    ["So sánh 3/7 và 5/7.", "So sánh 4/5 với 1."],
    [
        (["Hai phân số cùng mẫu 7.", "Vì 3 < 5 nên 3/7 < 5/7."], "3/7 < 5/7."),
        (
            ["Phân số 4/5 có tử số 4 bé hơn mẫu số 5.", "Vì vậy 4/5 bé hơn 1."],
            "4/5 < 1.",
        ),
    ],
    "Không so sánh tử số trực tiếp khi mẫu số khác nhau.",
)
add(
    "fraction_of",
    "Tìm phân số của một số",
    "Muốn tìm a/b của một số, lấy số đó chia cho b rồi nhân với a; cũng có thể nhân số đó với phân số a/b.",
    "1. Xác định số ban đầu và phân số cần tìm.\n2. Chia cho mẫu, nhân với tử.\n3. Ghi câu lời giải, đơn vị và đáp số.",
    "Tìm 3/4 của 20 quả cam.",
    ["Số quả cam cần tìm là:", "20 : 4 × 3 = 15 (quả)"],
    "15 quả cam.",
    [
        "Tìm 2/3 của 18 kg gạo.",
        "Một lớp có 35 học sinh, 3/5 số học sinh tham gia câu lạc bộ. Có bao nhiêu bạn tham gia?",
    ],
    [
        (["Số gạo cần tìm là:", "18 : 3 × 2 = 12 (kg)"], "12 kg gạo."),
        (["Số học sinh tham gia là:", "35 : 5 × 3 = 21 (học sinh)"], "21 học sinh."),
    ],
    "Không chia cho tử rồi nhân với mẫu.",
)


def numeric_unit(
    key, name, rule, example, example_lines, final, tasks, workings, finals
):
    add(
        key,
        name,
        rule,
        "1. Đọc tên đơn vị và đại lượng cần tìm.\n2. Viết quan hệ giữa các đơn vị hoặc chọn phép tính đúng.\n3. Tính, ghi đơn vị và đáp số; kiểm tra chiều đổi.",
        example,
        example_lines,
        final,
        tasks,
        [(workings[i], finals[i]) for i in range(2)],
        "Không cộng các số đo khác đơn vị khi chưa đổi; không bỏ đơn vị ở đáp số.",
    )


numeric_unit(
    "length_cm",
    "Đo độ dài bằng xăng-ti-mét",
    "Đơn vị xăng-ti-mét viết là cm. Đặt đầu đoạn ở vạch 0, đọc số ở đầu kia. So sánh độ dài bằng cùng một đơn vị.",
    "Đoạn AB từ vạch 0 đến vạch 6 cm. AB dài bao nhiêu?",
    ["Đầu A ở vạch 0, đầu B ở vạch 6 cm.", "Độ dài đoạn AB là 6 cm."],
    "6 cm.",
    [
        "Hai bút dài 8 cm và 5 cm. Bút nào dài hơn?",
        "Ghép hai đoạn dài 4 cm và 3 cm liên tiếp. Tổng dài bao nhiêu?",
    ],
    [
        ["Vì 8 > 5 nên bút 8 cm dài hơn.", "Độ chênh lệch là 8 − 5 = 3 (cm)."],
        ["Tổng độ dài là:", "4 + 3 = 7 (cm)"],
    ],
    ["Bút dài 8 cm.", "7 cm."],
)
numeric_unit(
    "length_units",
    "Đề-xi-mét, mét, ki-lô-mét",
    "1 dm = 10 cm; 1 m = 10 dm = 100 cm; 1 km = 1 000 m.",
    "Đổi 3 m thành xăng-ti-mét.",
    ["Vì 1 m = 100 cm nên:", "3 m = 300 cm."],
    "300 cm.",
    ["Đổi 5 dm thành cm.", "Đổi 2 km thành m."],
    [
        ["Vì 1 dm = 10 cm nên:", "5 dm = 50 cm."],
        ["Vì 1 km = 1 000 m nên:", "2 km = 2 000 m."],
    ],
    ["50 cm.", "2 000 m."],
)
numeric_unit(
    "mm",
    "Mi-li-mét",
    "Mi-li-mét viết là mm; 1 cm = 10 mm; 1 m = 1 000 mm.",
    "Đổi 4 cm thành mm.",
    ["Mỗi xăng-ti-mét bằng 10 mi-li-mét.", "4 × 10 = 40 (mm)"],
    "40 mm.",
    ["Đổi 7 cm thành mm.", "Đổi 30 mm thành cm."],
    [
        ["Độ dài cần đổi là:", "7 × 10 = 70 (mm)"],
        ["Độ dài theo cm là:", "30 : 10 = 3 (cm)"],
    ],
    ["70 mm.", "3 cm."],
)
numeric_unit(
    "kg",
    "Ki-lô-gam",
    "Ki-lô-gam viết là kg, dùng đo khối lượng. Đọc cân khi kim hoặc màn hình ổn định; đặt vật theo hướng dẫn.",
    "Một túi gạo nặng 5 kg, túi khác nặng 3 kg. Hai túi nặng bao nhiêu?",
    ["Hai túi gạo nặng là:", "5 + 3 = 8 (kg)"],
    "8 kg.",
    [
        "Có 9 kg đường, dùng 4 kg. Còn bao nhiêu?",
        "Hai quả cân 2 kg và 5 kg có tổng khối lượng bao nhiêu?",
    ],
    [
        ["Số đường còn lại là:", "9 − 4 = 5 (kg)"],
        ["Tổng khối lượng là:", "2 + 5 = 7 (kg)"],
    ],
    ["5 kg.", "7 kg."],
)
numeric_unit(
    "litre",
    "Lít",
    "Lít viết là l, dùng đo lượng chất lỏng. Dùng ca có vạch chia và đọc lượng chất lỏng ở đúng vạch.",
    "Can có 8 l nước, rót ra 3 l. Can còn bao nhiêu?",
    ["Can còn số lít nước là:", "8 − 3 = 5 (l)"],
    "5 l nước.",
    [
        "Bình có 4 l, thêm 2 l. Có bao nhiêu?",
        "Hai can có 5 l và 3 l dầu. Tổng bao nhiêu?",
    ],
    [
        ["Lượng nước sau khi thêm là:", "4 + 2 = 6 (l)"],
        ["Tổng lượng dầu là:", "5 + 3 = 8 (l)"],
    ],
    ["6 l.", "8 l."],
)
numeric_unit(
    "gram",
    "Gam",
    "Gam viết là g; 1 kg = 1 000 g. Gam thường dùng cho các vật nhẹ.",
    "Một gói bánh nặng 250 g, gói kẹo nặng 150 g. Tổng nặng bao nhiêu?",
    ["Tổng khối lượng là:", "250 + 150 = 400 (g)"],
    "400 g.",
    ["Đổi 2 kg thành g.", "Có 700 g bột, dùng 200 g. Còn bao nhiêu?"],
    [
        ["Vì 1 kg = 1 000 g nên:", "2 kg = 2 000 g."],
        ["Khối lượng bột còn lại là:", "700 − 200 = 500 (g)"],
    ],
    ["2 000 g.", "500 g."],
)
numeric_unit(
    "millilitre",
    "Mi-li-lít",
    "Mi-li-lít viết là ml; 1 l = 1 000 ml. Khi đọc bình chia độ, nhìn ngang mức chất lỏng.",
    "Bình có 500 ml nước, rót thêm 200 ml. Có bao nhiêu?",
    ["Lượng nước trong bình là:", "500 + 200 = 700 (ml)"],
    "700 ml.",
    ["Đổi 3 l thành ml.", "Có 800 ml sữa, dùng 250 ml. Còn bao nhiêu?"],
    [
        ["Vì 1 l = 1 000 ml nên:", "3 l = 3 000 ml."],
        ["Lượng sữa còn lại là:", "800 − 250 = 550 (ml)"],
    ],
    ["3 000 ml.", "550 ml."],
)
numeric_unit(
    "temperature",
    "Nhiệt độ và độ C",
    "Nhiệt độ được đo bằng nhiệt kế. Đơn vị độ C viết là °C. Đọc đúng thang đo; nhiệt độ cao hơn ứng với số lớn hơn trong các ví dụ số dương này.",
    "Buổi sáng 24°C, buổi trưa 30°C. Buổi trưa nóng hơn bao nhiêu độ C?",
    ["Mức tăng nhiệt độ là:", "30 − 24 = 6 (°C)"],
    "6°C.",
    [
        "Nhiệt kế chỉ 28°C. Đọc nhiệt độ.",
        "Hai nơi có nhiệt độ 25°C và 32°C. Nơi nào nóng hơn?",
    ],
    [
        ["Số trên thang là 28 và đơn vị là độ C.", "Đọc: hai mươi tám độ C."],
        [
            "Vì 32 > 25 nên nơi 32°C có nhiệt độ cao hơn.",
            "Chênh lệch: 32 − 25 = 7 (°C).",
        ],
    ],
    ["28°C.", "Nơi có nhiệt độ 32°C."],
)
numeric_unit(
    "large_mass",
    "Yến, tạ, tấn",
    "1 yến = 10 kg; 1 tạ = 10 yến = 100 kg; 1 tấn = 10 tạ = 1 000 kg.",
    "Đổi 3 tạ thành kg.",
    ["Vì 1 tạ = 100 kg nên:", "3 tạ = 300 kg."],
    "300 kg.",
    ["Đổi 5 yến thành kg.", "Đổi 2 tấn 3 tạ thành kg."],
    [
        ["Vì 1 yến = 10 kg nên:", "5 yến = 50 kg."],
        [
            "2 tấn = 2 000 kg; 3 tạ = 300 kg.",
            "Tổng khối lượng là:",
            "2 000 + 300 = 2 300 (kg)",
        ],
    ],
    ["50 kg.", "2 300 kg."],
)
numeric_unit(
    "area_units4",
    "Đơn vị diện tích",
    "1 dm² = 100 cm²; 1 m² = 100 dm² = 10 000 cm²; 1 cm² = 100 mm². Hai đơn vị diện tích liền nhau trong bảng này hơn kém 100 lần.",
    "Đổi 3 dm² thành cm².",
    ["Vì 1 dm² = 100 cm² nên:", "3 dm² = 300 cm²."],
    "300 cm².",
    ["Đổi 2 m² thành dm².", "Đổi 500 mm² thành cm²."],
    [
        ["Vì 1 m² = 100 dm² nên:", "2 m² = 200 dm²."],
        ["Vì 100 mm² = 1 cm² nên:", "500 : 100 = 5 (cm²)"],
    ],
    ["200 dm².", "5 cm²."],
)
numeric_unit(
    "second_century",
    "Giây và thế kỉ",
    "1 phút = 60 giây; 1 thế kỉ = 100 năm. Thế kỉ XXI gồm các năm 2001 đến 2100; năm 2000 thuộc thế kỉ XX.",
    "Đổi 3 phút thành giây.",
    ["Số giây là:", "3 × 60 = 180 (giây)"],
    "180 giây.",
    ["Đổi 2 thế kỉ thành năm.", "Năm 2026 thuộc thế kỉ nào?"],
    [
        ["Số năm là:", "2 × 100 = 200 (năm)"],
        ["2026 nằm trong khoảng từ 2001 đến 2100.", "Khoảng này thuộc thế kỉ XXI."],
    ],
    ["200 năm.", "Thế kỉ XXI."],
)
add(
    "graph_picture",
    "Đọc biểu đồ tranh",
    "Mỗi hình trong biểu đồ có thể đại diện một hoặc nhiều đồ vật. Phải đọc chú giải trước khi đếm.",
    "1. Đọc tên nhóm và chú giải.\n2. Đếm số hình rồi nhân với giá trị mỗi hình.\n3. So sánh hoặc tính tổng theo câu hỏi.",
    "Biểu đồ: An có ★★★, Bình có ★★. Mỗi ★ chỉ 2 quyển sách. Mỗi bạn có bao nhiêu sách?",
    [
        "An có 3 hình sao nên có: 3 × 2 = 6 (quyển).",
        "Bình có 2 hình sao nên có: 2 × 2 = 4 (quyển).",
    ],
    "An: 6 quyển; Bình: 4 quyển.",
    [
        "Với biểu đồ trên, hai bạn có tất cả bao nhiêu sách?",
        "Một nhóm có ★★★★, mỗi ★ chỉ 5 cây. Nhóm có bao nhiêu cây?",
    ],
    [
        (["Tổng số sách là:", "6 + 4 = 10 (quyển)"], "10 quyển sách."),
        (["Số cây là:", "4 × 5 = 20 (cây)"], "20 cây."),
    ],
    "Không mặc định mỗi hình luôn chỉ một đồ vật.",
)
add(
    "graph_column",
    "Đọc biểu đồ cột",
    "Biểu đồ cột thể hiện số lượng theo chiều cao cột. Đọc tên cột, đơn vị và khoảng cách giữa các vạch chia.",
    "1. Đọc tên biểu đồ và đơn vị.\n2. Dóng đỉnh mỗi cột sang trục số.\n3. Dùng số đọc được để so sánh, cộng hoặc trừ.",
    "Biểu đồ số sách của ba tổ, mỗi mức cao ứng với 1 quyển:\n```\n5 |   █\n4 |   █\n3 | █ █\n2 | █ █ █\n1 | █ █ █\n0 +-------\n    A B C\n```\nTổ nào có nhiều sách nhất?",
    [
        "Đỉnh các cột cho biết A: 3 quyển, B: 5 quyển, C: 2 quyển.",
        "Vì 5 lớn nhất nên tổ B có nhiều sách nhất.",
    ],
    "Tổ B: 5 quyển.",
    [
        "Với biểu đồ trên, A và C có tất cả bao nhiêu quyển?",
        "Với biểu đồ trên, B nhiều hơn C bao nhiêu quyển?",
    ],
    [
        (["Tổng số sách của A và C là:", "3 + 2 = 5 (quyển)"], "5 quyển."),
        (["Số sách B nhiều hơn C là:", "5 − 2 = 3 (quyển)"], "3 quyển."),
    ],
    "Đọc đúng giá trị mỗi vạch, không chỉ đếm nét vẽ trang trí.",
)
add(
    "event_count",
    "Số lần xuất hiện của sự kiện",
    "Đếm mỗi lần thử đúng một lần; tổng số lần của các kết quả phân loại phải bằng số lần thử đã ghi.",
    "1. Ghi kết quả từng lần.\n2. Đếm theo sự kiện cần xét.\n3. Kiểm tra tổng, không suy rằng lần thử sau chắc chắn giống các lần trước.",
    "Năm lần tung đồng xu cho kết quả: sấp, ngửa, sấp, sấp, ngửa. Mặt sấp xuất hiện mấy lần?",
    ["Mặt sấp ở lần thứ nhất, thứ ba và thứ tư.", "Đếm được 3 lần."],
    "3 lần.",
    [
        "Với kết quả trên, mặt ngửa xuất hiện mấy lần?",
        "Kết quả 6 lần là A, B, A, A, B, A. A xuất hiện mấy lần?",
    ],
    [
        (["Mặt ngửa xuất hiện ở lần thứ hai và thứ năm.", "Đếm được 2 lần."], "2 lần."),
        (
            ["A xuất hiện ở lần thứ nhất, thứ ba, thứ tư, thứ sáu.", "Đếm được 4 lần."],
            "4 lần.",
        ),
    ],
    "Không bỏ kết quả lặp lại; số lần xuất hiện không bảo đảm lần thử tiếp theo.",
)

DIGIT_WORDS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def read_number(n):
    def group(v, full=False):
        h, rest = divmod(v, 100)
        t, u = divmod(rest, 10)
        out = []
        if h or full:
            out += [DIGIT_WORDS[h], "trăm"]
        if t >= 2:
            out += [DIGIT_WORDS[t], "mươi"]
        elif t == 1:
            out += ["mười"]
        elif u and (h or full):
            out += ["linh"]
        if u:
            out += [
                "mốt"
                if u == 1 and t >= 2
                else "lăm"
                if u == 5 and t >= 1
                else DIGIT_WORDS[u]
            ]
        return " ".join(out)

    if n == 0:
        return "không"
    if n == 1_000_000:
        return "một triệu"
    high, low = divmod(n, 1000)
    return (
        (group(high) + " nghìn" + (" " + group(low, low < 100) if low else ""))
        if high
        else group(low)
    )


def arithmetic(kind, grade, number, digits=2):
    if kind in ("add", "sub"):
        if grade == 1:
            pairs = [(24 + number % 4 * 10, 3), (31 + number % 3 * 10, 12), (45, 23)]
        elif grade == 2 and digits == 2:
            pairs = [(27 + number % 3 * 10, 18), (36, 27), (48, 16)]
        else:
            base = 10 ** (digits - 1)
            pairs = [
                (base + 237 % (base) + number, base + 158 % (base)),
                (base * 2 + 145 % (base), base + 126 % (base)),
                (base * 3 + 96 % (base), base + 65 % (base)),
            ]
        if kind == "sub":
            pairs = [(a + b, b) for a, b in pairs]
        op = "+" if kind == "add" else "−"
        name = "Phép cộng" if kind == "add" else "Phép trừ"
        rule = f"{name}: đặt các chữ số cùng hàng thẳng cột, tính từ phải sang trái; cộng có thể nhớ sang hàng bên trái, trừ có thể phải đổi một đơn vị ở hàng bên trái."

        if grade == 1:
            rule = f"{name} không nhớ: đặt các chữ số cùng hàng thẳng cột và tính từ phải sang trái. Các ví dụ này không cần nhớ hoặc đổi đơn vị ở hàng bên trái."

        def solve(a, b):
            value = a + b if kind == "add" else a - b
            width = max(len(str(a)), len(str(b)), len(str(value))) + 2
            column = (
                f"```\n{str(a).rjust(width)}\n{op} {str(b).rjust(width - 2)}\n"
                + ("-" * width)
                + f"\n{str(value).rjust(width)}\n```"
            )
            inverse = (
                f"{value} − {b} = {a}." if kind == "add" else f"{value} + {b} = {a}."
            )
            return (
                [
                    "Đặt tính, các chữ số cùng hàng thẳng cột:",
                    column,
                    "Tính từ hàng đơn vị sang các hàng bên trái."
                    if grade == 1
                    else "Tính từ hàng đơn vị sang các hàng bên trái, thực hiện nhớ hoặc đổi khi cần.",
                    f"{a} {op} {b} = {value}.",
                    "Thử lại: " + inverse,
                ],
                str(value) + ".",
            )
    else:
        divisor = 3 if digits != 22 else 12
        base = (
            10 ** (digits - 1) if kind == "multiply" else 10 ** (digits - 1) // divisor
        )
        qs = (
            [12 + number % 5, 21 + number % 4, 25 + number % 3]
            if digits <= 2
            else [base + 24 + number, base + 37 + number, base + 16 + number]
        )
        if digits == 22:
            qs = [124 + number, 136 + number, 142 + number]
        pairs = [
            (q, divisor) if kind == "multiply" else (q * divisor, divisor) for q in qs
        ]
        op = "×" if kind == "multiply" else ":"
        name = "Phép nhân" if kind == "multiply" else "Phép chia"
        rule = (
            "Nhân lần lượt từ hàng đơn vị sang trái, nhớ sang hàng bên trái khi cần; với thừa số hai chữ số, tích riêng thứ hai lùi sang trái một cột."
            if kind == "multiply"
            else "Chia từ trái sang phải, lần lượt chia, nhân, trừ rồi hạ chữ số tiếp theo. Nếu một lượt chia có thương 0 ở giữa, vẫn phải viết 0. Số chia khác 0."
        )

        def solve(a, b):
            if kind == "multiply":
                value = a * b
                if b < 10:
                    carry = 0
                    lines = []
                    for ch in reversed(str(a)):
                        digit = int(ch)
                        v = digit * b + carry
                        lines.append(
                            f"{digit} × {b}"
                            + (f" + {carry}" if carry else "")
                            + f" = {v}; viết {v % 10}, nhớ {v // 10}."
                        )
                        carry = v // 10
                    if carry:
                        lines.append(f"Viết thêm số nhớ {carry} vào bên trái.")
                else:
                    tens, ones = divmod(b, 10)
                    lines = [
                        f"Tích riêng thứ nhất: {a} × {ones} = {a * ones}.",
                        f"Tích riêng theo hàng chục: {a} × {tens * 10} = {a * tens * 10}.",
                        f"Cộng hai tích riêng: {a * ones} + {a * tens * 10} = {value}.",
                    ]
                lines += [f"Vậy {a} × {b} = {value}."]
            else:
                value = a // b
                lines = []
                r = 0
                started = False
                for ch in str(a):
                    part = r * 10 + int(ch)
                    if not started and part < b:
                        r = part
                        continue
                    started = True
                    q, r = divmod(part, b)
                    lines += [f"{part} : {b} được {q}, dư {r}; viết {q} vào thương."]
                lines += [f"Vậy {a} : {b} = {value}.", f"Thử lại: {value} × {b} = {a}."]
            return lines, str(value) + "."

    worked = solve(*pairs[0])
    others = [solve(*p) for p in pairs[1:]]
    return item(
        name,
        rule,
        "1. Đặt tính theo đúng hàng.\n2. Thực hiện từng lượt tính và ghi đủ chữ số.\n3. Thử lại bằng phép tính ngược, rồi ghi đáp số.",
        f"Tính {pairs[0][0]} {op} {pairs[0][1]}.",
        *worked,
        [f"Tính {a} {op} {b}." for a, b in pairs[1:]],
        others,
        "Không bỏ số nhớ hoặc chữ số 0 ở giữa kết quả; kiểm tra hàng và thứ tự tính.",
    )


def table_skill(k):
    return item(
        f"Bảng nhân {k}, bảng chia {k}",
        f"Mỗi lần thêm {k}, tích trong bảng nhân {k} tăng {k}. Từ a × {k} = b suy ra b : {k} = a.\n"
        + "\n".join(f"{k} × {i} = {k * i}; {k * i} : {k} = {i}." for i in range(1, 11)),
        "1. Hiểu các nhóm có số phần tử bằng nhau.\n2. Tính tích bằng bảng nhân.\n3. Dùng quan hệ nhân và chia để kiểm tra thương.",
        f"Có 4 nhóm, mỗi nhóm {k} bút. Có tất cả bao nhiêu bút?",
        ["Số bút có tất cả là:", f"{k} × 4 = {k * 4} (bút)"],
        f"{k * 4} bút.",
        [
            f"Tính {k} × 6.",
            f"Có {k * 8} que tính chia đều thành các nhóm {k} que. Có mấy nhóm?",
        ],
        [
            ([f"Theo bảng nhân {k}:", f"{k} × 6 = {k * 6}."], f"{k * 6}."),
            (["Số nhóm là:", f"{k * 8} : {k} = 8 (nhóm)"], "8 nhóm."),
        ],
        "Bảng nhân tăng đều theo số đang học; không đổi vị trí các thành phần của phép chia tùy ý.",
    )


def numbers_skill(limit, n):
    values = (
        [3, 4, 5]
        if limit == 5
        else [6, 8, 10]
        if limit == 10
        else [23 + n % 4, 35, 46]
        if limit == 100
        else [324 + n, 506, 720]
        if limit == 1000
        else [3245 + n, 5060, 7200]
        if limit == 10000
        else [32450 + n, 50600, 72000]
        if limit == 100000
        else [324500 + n, 506000, 720000]
    )

    def solve(v):
        parts = [
            str(int(c) * 10**i) for i, c in enumerate(reversed(str(v))) if c != "0"
        ]
        return (
            [
                f"Xét lần lượt các chữ số theo hàng trong số {v}.",
                f"{v} = " + " + ".join(reversed(parts)) + ".",
                f"Đọc là: {read_number(v)}.",
            ],
            f"{read_number(v)}.",
        )

    return item(
        f"Các số trong phạm vi {limit}",
        "Mỗi chữ số có giá trị theo hàng của nó. Mười đơn vị bằng một chục; mười chục bằng một trăm; tiếp tục như vậy ở các hàng cao hơn đã học.",
        "1. Xác định các hàng từ phải sang trái.\n2. Đọc theo thứ tự từ hàng cao nhất.\n3. Viết thành tổng giá trị từng chữ số và kiểm tra các chữ số 0.",
        f"Đọc và phân tích số {values[0]}.",
        *solve(values[0]),
        [f"Đọc và phân tích số {v}." for v in values[1:]],
        [solve(v) for v in values[1:]],
        "Không bỏ chữ số 0 ở giữa khi viết số; mỗi hàng có đúng một chữ số.",
    )


def compare_skill(limit, n):
    base = 1 if limit <= 10 else limit // 10
    a = base * 3 + (n % 3 if limit > 10 else 0)
    b = a + 2
    return item(
        "So sánh và sắp xếp số",
        "So sánh số lượng hoặc số tự nhiên: số có nhiều chữ số hơn thì lớn hơn; cùng số chữ số thì so từ hàng cao nhất. Dùng dấu <, >, = đúng chiều.",
        "1. Đếm số chữ số hoặc số đồ vật.\n2. So lần lượt từ hàng cao nhất.\n3. Viết dấu và đọc lại; khi sắp xếp phải dùng đủ các số.",
        f"So sánh {a} và {b}.",
        [
            "Hai số cùng số chữ số; đối chiếu các hàng từ trái sang phải.",
            f"Vì {a} bé hơn {b} nên {a} < {b}.",
        ],
        f"{a} < {b}.",
        [f"Sắp xếp tăng dần: {b}; {a}; {b + 1}.", f"So sánh {b} và {b}."],
        [
            (
                [
                    f"Số bé nhất là {a}, tiếp theo {b}, rồi {b + 1}.",
                    f"{a} < {b} < {b + 1}.",
                ],
                f"{a}; {b}; {b + 1}.",
            ),
            (
                [f"Hai số đều là {b}.", "Hai số giống nhau có giá trị bằng nhau."],
                f"{b} = {b}.",
            ),
        ],
        "Không so sánh chỉ theo chữ số hàng đơn vị khi số có nhiều chữ số.",
    )


def rounding_skill(place):
    a = 3746 if place <= 100 else 37460 if place <= 10000 else 374600

    def solve(v):
        lower = v // place * place
        result = lower + (place if v % place >= place // 2 else 0)
        return (
            [
                f"Số {v} nằm giữa {lower} và {lower + place}.",
                f"Phần sau hàng làm tròn là {v % place}; so với {place // 2} để chọn số gần hơn.",
                f"Làm tròn được {result}.",
            ],
            f"{result}.",
        )

    vals = [a, a + place // 5, a + place // 3]
    return item(
        f"Làm tròn đến hàng {place}",
        "Làm tròn đến hàng đã chọn: xét chữ số ngay bên phải; từ 5 trở lên thì tăng hàng làm tròn thêm 1, bé hơn 5 thì giữ nguyên; các hàng phía sau ở phần nguyên thay bằng 0.",
        "1. Xác định hàng cần làm tròn.\n2. Xét chữ số ngay bên phải.\n3. Viết kết quả và kiểm tra gần số ban đầu.",
        f"Làm tròn {vals[0]} đến hàng có giá trị {place}.",
        *solve(vals[0]),
        [f"Làm tròn {v} đến hàng có giá trị {place}." for v in vals[1:]],
        [solve(v) for v in vals[1:]],
        "Chỉ xét chữ số ngay bên phải hàng làm tròn, không xét tùy ý một chữ số khác.",
    )


add(
    "partition",
    "Mấy và mấy",
    "Một số có thể tách thành hai nhóm theo nhiều cách. Gộp hai nhóm lại phải được đúng số ban đầu.",
    "1. Đếm tổng số vật.\n2. Tách thành hai nhóm.\n3. Đếm từng nhóm rồi gộp lại để kiểm tra.",
    "Có 7 que tính, tách một nhóm 3 que. Nhóm kia có mấy que?",
    ["Lấy 3 que sang một nhóm, đếm nhóm còn lại được 4 que.", "Gộp lại: 3 + 4 = 7."],
    "4 que.",
    [
        "Tách 6 thành một nhóm 2. Nhóm kia có mấy?",
        "Nêu một cách tách 5 thành hai nhóm khác rỗng.",
    ],
    [
        (["Lấy 2 trong 6 vật ra một nhóm, còn 4 vật.", "Kiểm tra: 2 + 4 = 6."], "4."),
        (
            ["Có thể tách 5 vật thành nhóm 2 và nhóm 3.", "Kiểm tra: 2 + 3 = 5."],
            "Ví dụ: 2 và 3.",
        ),
    ],
    "Có thể có nhiều cách tách đúng; không bỏ hoặc đếm trùng vật.",
)
add(
    "number_line",
    "Tia số và số liền trước, liền sau",
    "Trên tia số, số lớn hơn nằm về bên phải. Các số tự nhiên liên tiếp hơn kém nhau 1. Số liền trước của số lớn hơn 0 bé hơn số đó 1; số liền sau lớn hơn số đó 1 đơn vị.",
    "1. Tìm vị trí của số đã cho.\n2. Lùi một bước để tìm liền trước (nếu có).\n3. Tiến một bước để tìm liền sau.",
    "Tìm số liền trước và số liền sau của 35.",
    ["Số liền trước là: 35 − 1 = 34.", "Số liền sau là: 35 + 1 = 36."],
    "34 và 36.",
    ["Số liền sau của 99 là số nào?", "Điền số còn thiếu: 18, 19, □, 21."],
    [
        (["Tăng 99 thêm 1.", "99 + 1 = 100."], "100."),
        (
            ["Dãy gồm các số liên tiếp, mỗi lần tăng 1.", "Sau 19 và trước 21 là 20."],
            "20.",
        ),
    ],
    "Số 0 không có số liền trước trong dãy số tự nhiên.",
)
add(
    "small_add",
    "Cộng trong phạm vi 10",
    "Cộng là gộp hoặc thêm. Khi thêm một số vật, tổng số vật tăng. Có thể dùng que tính hoặc đếm tiếp.",
    "1. Lấy nhóm vật thứ nhất.\n2. Thêm nhóm thứ hai.\n3. Đếm tất cả hoặc đếm tiếp, ghi phép cộng.",
    "Có 5 quả, thêm 3 quả. Có tất cả bao nhiêu?",
    ["Đếm tiếp từ 5 thêm 3 lần: 6, 7, 8.", "Số quả có tất cả là:", "5 + 3 = 8 (quả)"],
    "8 quả.",
    ["Tính 4 + 2.", "Tính 7 + 2."],
    [
        (["Đếm tiếp từ 4: 5, 6.", "4 + 2 = 6."], "6."),
        (["Đếm tiếp từ 7: 8, 9.", "7 + 2 = 9."], "9."),
    ],
    "Chỉ đếm thêm đúng số lần, không đếm lại số bắt đầu như một vật mới.",
)
add(
    "small_sub",
    "Trừ trong phạm vi 10",
    "Trừ có thể hiểu là bớt đi hoặc tìm phần còn lại. Có thể dùng vật thật, gạch bớt hình hoặc đếm lùi.",
    "1. Đếm số ban đầu.\n2. Bớt đúng số cần bớt.\n3. Đếm phần còn lại và viết phép trừ.",
    "Có 8 quả, cho đi 3 quả. Còn bao nhiêu?",
    ["Bớt 3 từ 8 còn 5.", "Số quả còn lại là:", "8 − 3 = 5 (quả)"],
    "5 quả.",
    ["Tính 7 − 2.", "Tính 9 − 4."],
    [
        (["Đếm lùi hai bước từ 7: 6, 5.", "7 − 2 = 5."], "5."),
        (["Bớt 4 vật từ nhóm 9 còn 5 vật.", "9 − 4 = 5."], "5."),
    ],
    "Không gộp thêm khi đề yêu cầu bớt.",
)
add(
    "make_ten_add",
    "Cộng qua 10",
    "Có thể tách một số để bù số kia thành 10, rồi cộng phần còn lại. Ví dụ 8 cần thêm 2 để thành 10.",
    "1. Tìm số cần bù thành 10.\n2. Tách số hạng còn lại thành hai phần.\n3. Cộng thành 10 rồi cộng phần còn lại.",
    "Tính 8 + 7.",
    ["Tách 7 = 2 + 5.", "8 + 7 = 8 + 2 + 5 = 10 + 5 = 15."],
    "15.",
    ["Tính 9 + 6.", "Tính 7 + 5."],
    [
        (["Tách 6 = 1 + 5.", "9 + 6 = 9 + 1 + 5 = 10 + 5 = 15."], "15."),
        (["Tách 5 = 3 + 2.", "7 + 5 = 7 + 3 + 2 = 10 + 2 = 12."], "12."),
    ],
    "Sau khi bù thành 10 chỉ cộng phần còn lại, không cộng lại cả số hạng.",
)
add(
    "make_ten_sub",
    "Trừ qua 10",
    "Có thể tách số trừ để trừ về 10 trước, rồi trừ phần còn lại; hoặc dùng phép cộng tương ứng để tìm hiệu.",
    "1. Tìm phần cần bớt để còn 10.\n2. Tách số trừ.\n3. Trừ lần lượt và thử lại bằng cộng.",
    "Tính 14 − 8.",
    ["Tách 8 = 4 + 4.", "14 − 8 = 14 − 4 − 4 = 10 − 4 = 6.", "Thử lại: 6 + 8 = 14."],
    "6.",
    ["Tính 13 − 5.", "Tính 16 − 9."],
    [
        (["Tách 5 = 3 + 2.", "13 − 5 = 13 − 3 − 2 = 10 − 2 = 8."], "8."),
        (["Tách 9 = 6 + 3.", "16 − 9 = 16 − 6 − 3 = 10 − 3 = 7."], "7."),
    ],
    "Không trừ thiếu phần còn lại sau khi đã về 10.",
)
add(
    "more_less",
    "Hơn, kém; thêm, bớt",
    "Hỏi hơn kém bao nhiêu dùng phép trừ. Tìm số nhiều hơn thì cộng phần hơn; tìm số ít hơn thì trừ phần kém.",
    "1. Xác định số đã biết và phần chênh lệch.\n2. Đọc rõ tìm số mới hay tìm chênh lệch.\n3. Viết câu lời giải và phép tính.",
    "An có 12 nhãn vở, Bình có 8 nhãn vở. An hơn Bình bao nhiêu?",
    ["An hơn Bình số nhãn vở là:", "12 − 8 = 4 (nhãn vở)"],
    "4 nhãn vở.",
    [
        "Lan có 15 bông hoa, Mai nhiều hơn Lan 3 bông. Mai có bao nhiêu?",
        "Có 18 quả, bớt 5 quả. Còn bao nhiêu?",
    ],
    [
        (["Mai có số bông hoa là:", "15 + 3 = 18 (bông)"], "18 bông hoa."),
        (["Số quả còn lại là:", "18 − 5 = 13 (quả)"], "13 quả."),
    ],
    "Không chọn phép tính chỉ theo một từ; phải đọc đủ ý bài toán.",
)
add(
    "round_numbers",
    "Số tròn chục, tròn trăm",
    "Số tròn chục có chữ số hàng đơn vị là 0. Số tròn trăm có hai chữ số cuối là 00.",
    "1. Quan sát chữ số cuối.\n2. Đọc theo số chục hoặc số trăm.\n3. Khi so sánh, dùng các hàng cao nhất.",
    "Đọc các số 200, 350; số nào tròn trăm?",
    [
        "200 đọc là hai trăm, có hai chữ số cuối 00 nên tròn trăm.",
        "350 đọc là ba trăm năm mươi; là số tròn chục nhưng không tròn trăm.",
    ],
    "200 tròn trăm; cả hai tròn chục.",
    ["Số gồm 7 trăm, 0 chục, 0 đơn vị là số nào?", "So sánh 400 và 600."],
    [
        (["Bảy trăm viết 700.", "Các hàng chục và đơn vị đều viết 0."], "700."),
        (
            ["Hai số có các chữ số hàng trăm là 4 và 6.", "Vì 4 < 6 nên 400 < 600."],
            "400 < 600.",
        ),
    ],
    "Số tròn chục không nhất thiết tròn trăm.",
)
add(
    "million",
    "Hàng, lớp và lớp triệu",
    "Ba hàng đơn vị, chục, trăm tạo thành lớp đơn vị; ba hàng nghìn, chục nghìn, trăm nghìn tạo thành lớp nghìn; tiếp theo là lớp triệu. 1 000 000 đọc là một triệu.",
    "1. Tách số thành từng lớp ba chữ số từ phải sang trái.\n2. Đọc mỗi lớp từ trái sang phải kèm tên lớp.\n3. Khi viết, giữ đủ ba chữ số ở các lớp phía sau.",
    "Đọc số 12 345 678 và nêu các lớp.",
    [
        "Tách số thành lớp triệu: 12; lớp nghìn: 345; lớp đơn vị: 678.",
        "Đọc: mười hai triệu ba trăm bốn mươi lăm nghìn sáu trăm bảy mươi tám.",
    ],
    "12 triệu; 345 nghìn; 678 đơn vị.",
    [
        "Viết số gồm 3 triệu, 25 nghìn, 6 đơn vị.",
        "Chữ số 4 trong 24 153 678 thuộc hàng nào, giá trị bao nhiêu?",
    ],
    [
        (
            [
                "Lớp triệu viết 3, lớp nghìn viết 025, lớp đơn vị viết 006.",
                "Ghép các lớp được 3 025 006.",
            ],
            "3 025 006.",
        ),
        (
            ["Chữ số 4 thuộc hàng triệu.", "Giá trị là 4 000 000."],
            "Hàng triệu; 4 000 000.",
        ),
    ],
    "Không bỏ các chữ số 0 dùng giữ vị trí trong mỗi lớp.",
)
add(
    "estimate",
    "Ước lượng trong tính toán",
    "Ước lượng dùng các số gần, dễ tính để dự đoán khoảng kết quả. Kết quả ước lượng không thay thế kết quả chính xác khi đề yêu cầu tính đúng.",
    "1. Chọn số tròn gần dữ kiện.\n2. Tính với số đã làm tròn.\n3. Dùng để kiểm tra tính hợp lí; tính chính xác riêng nếu được hỏi.",
    "Ước lượng 198 × 21 bằng cách làm tròn hai thừa số.",
    [
        "198 gần 200; 21 gần 20.",
        "Tính với số tròn: 200 × 20 = 4 000.",
        "Vậy tích đã cho xấp xỉ 4 000.",
    ],
    "Khoảng 4 000.",
    ["Ước lượng 398 + 203.", "Ước lượng 602 : 3."],
    [
        (
            ["398 gần 400; 203 gần 200.", "400 + 200 = 600 nên tổng khoảng 600."],
            "Khoảng 600.",
        ),
        (["602 gần 600.", "600 : 3 = 200 nên thương khoảng 200."], "Khoảng 200."),
    ],
    "Không viết dấu bằng giữa kết quả chính xác và số ước lượng khi chúng khác nhau.",
)


def property_skill(kind):
    if kind == "add_properties":
        rule = "Đổi chỗ các số hạng thì tổng không đổi. Khi cộng ba số, có thể cộng hai số đầu rồi cộng số thứ ba hoặc cộng số đầu với tổng hai số sau."
        cases = [
            (
                "Tính thuận tiện 25 + 37 + 75.",
                [
                    "Đổi chỗ và nhóm 25 với 75.",
                    "25 + 37 + 75 = (25 + 75) + 37 = 100 + 37 = 137.",
                ],
                "137.",
            ),
            (
                "Tính thuận tiện 48 + 19 + 52.",
                ["Nhóm 48 với 52.", "48 + 19 + 52 = (48 + 52) + 19 = 100 + 19 = 119."],
                "119.",
            ),
            (
                "Điền số: 126 + 75 = 75 + □.",
                ["Đổi chỗ hai số hạng thì tổng không đổi.", "Số còn thiếu là 126."],
                "126.",
            ),
        ]
    elif kind == "multiply_properties":
        rule = "Đổi chỗ hai thừa số thì tích không đổi. Khi nhân ba số, có thể thay đổi cách nhóm các thừa số mà tích không đổi."
        cases = [
            (
                "Tính thuận tiện 25 × 7 × 4.",
                ["Nhóm 25 với 4.", "25 × 7 × 4 = (25 × 4) × 7 = 100 × 7 = 700."],
                "700.",
            ),
            (
                "Tính thuận tiện 2 × 17 × 5.",
                ["Nhóm 2 với 5.", "2 × 17 × 5 = (2 × 5) × 17 = 10 × 17 = 170."],
                "170.",
            ),
            (
                "Điền số: 12 × 8 = 8 × □.",
                ["Đổi chỗ hai thừa số thì tích không đổi.", "Số cần điền là 12."],
                "12.",
            ),
        ]
    else:
        rule = "Nhân một số với một tổng: nhân số đó với từng số hạng rồi cộng các tích. a × (b + c) = a × b + a × c."
        cases = [
            (
                "Tính 6 × (20 + 3).",
                [
                    "Nhân 6 với từng số hạng.",
                    "6 × (20 + 3) = 6 × 20 + 6 × 3 = 120 + 18 = 138.",
                ],
                "138.",
            ),
            (
                "Tính 8 × (10 + 5).",
                ["Nhân 8 với từng số hạng.", "8 × (10 + 5) = 80 + 40 = 120."],
                "120.",
            ),
            (
                "Tính thuận tiện 7 × 24 + 7 × 6.",
                [
                    "Đưa thừa số chung 7 ra ngoài.",
                    "7 × 24 + 7 × 6 = 7 × (24 + 6) = 7 × 30 = 210.",
                ],
                "210.",
            ),
        ]
    e, *tasks = cases
    return item(
        "Tính chất phép tính",
        rule,
        "1. Nhận biết phép tính và các số thuận tiện.\n2. Đổi chỗ hoặc nhóm theo tính chất đúng.\n3. Tính từng bước và kiểm tra kết quả.",
        e[0],
        e[1],
        e[2],
        [x[0] for x in tasks],
        [(x[1], x[2]) for x in tasks],
        "Không áp dụng tính chất giao hoán cho phép trừ hoặc phép chia.",
    )


def fraction_operation(kind):
    cases = {
        "fraction_add": [
            (
                "Tính 1/4 + 2/4.",
                ["Hai phân số cùng mẫu, cộng tử và giữ mẫu.", "1/4 + 2/4 = 3/4."],
                "3/4.",
            ),
            (
                "Tính 1/2 + 1/3.",
                ["Quy đồng: 1/2 = 3/6; 1/3 = 2/6.", "1/2 + 1/3 = 3/6 + 2/6 = 5/6."],
                "5/6.",
            ),
            (
                "Tính 2/5 + 1/5.",
                ["Hai phân số cùng mẫu 5.", "2/5 + 1/5 = 3/5."],
                "3/5.",
            ),
        ],
        "fraction_sub": [
            (
                "Tính 5/7 − 2/7.",
                ["Hai phân số cùng mẫu, trừ tử và giữ mẫu.", "5/7 − 2/7 = 3/7."],
                "3/7.",
            ),
            (
                "Tính 3/4 − 1/6.",
                [
                    "Quy đồng: 3/4 = 9/12; 1/6 = 2/12.",
                    "3/4 − 1/6 = 9/12 − 2/12 = 7/12.",
                ],
                "7/12.",
            ),
            (
                "Tính 4/5 − 1/5.",
                ["Hai phân số cùng mẫu 5.", "4/5 − 1/5 = 3/5."],
                "3/5.",
            ),
        ],
        "fraction_multiply": [
            (
                "Tính 2/3 × 3/4.",
                ["Nhân tử với tử, mẫu với mẫu.", "2/3 × 3/4 = 6/12 = 1/2."],
                "1/2.",
            ),
            (
                "Tính 3/5 × 2/3.",
                ["Nhân tử và mẫu tương ứng.", "3/5 × 2/3 = 6/15 = 2/5."],
                "2/5.",
            ),
            (
                "Tính 1/2 × 4/5.",
                ["Nhân tử và mẫu tương ứng.", "1/2 × 4/5 = 4/10 = 2/5."],
                "2/5.",
            ),
        ],
        "fraction_divide": [
            (
                "Tính 3/4 : 3/8.",
                [
                    "Nhân phân số thứ nhất với phân số đảo ngược của phân số thứ hai.",
                    "3/4 : 3/8 = 3/4 × 8/3 = 24/12 = 2.",
                ],
                "2.",
            ),
            (
                "Tính 2/3 : 4/5.",
                [
                    "Đảo ngược phân số 4/5 được 5/4.",
                    "2/3 : 4/5 = 2/3 × 5/4 = 10/12 = 5/6.",
                ],
                "5/6.",
            ),
            (
                "Tính 1/2 : 3/4.",
                [
                    "Đảo ngược phân số 3/4 được 4/3.",
                    "1/2 : 3/4 = 1/2 × 4/3 = 4/6 = 2/3.",
                ],
                "2/3.",
            ),
        ],
    }[kind]
    rule = {
        "fraction_add": "Cộng phân số cùng mẫu: cộng tử, giữ mẫu. Khác mẫu thì quy đồng trước.",
        "fraction_sub": "Trừ phân số cùng mẫu: trừ tử, giữ mẫu. Khác mẫu thì quy đồng trước.",
        "fraction_multiply": "Nhân tử với tử, mẫu với mẫu; rút gọn kết quả nếu có thể.",
        "fraction_divide": "Chia hai phân số: nhân phân số thứ nhất với phân số đảo ngược của phân số thứ hai. Phân số dùng làm số chia phải khác 0.",
    }[kind]
    e, *tasks = cases
    return item(
        "Phép tính với phân số",
        rule,
        "1. Xác định phép tính.\n2. Quy đồng hoặc đảo ngược theo đúng quy tắc, không dùng lẫn.\n3. Tính, rút gọn và ghi đáp số.",
        e[0],
        e[1],
        e[2],
        [x[0] for x in tasks],
        [(x[1], x[2]) for x in tasks],
        "Không cộng hoặc trừ hai mẫu số; khi chia không đảo phân số bị chia.",
    )


def _resolve_base(key, grade, number):
    if key in STATIC:
        return STATIC[key]
    if key.startswith("table"):
        return table_skill(int(key[5:]))
    if key.startswith("number"):
        return numbers_skill(int(key[6:]), number)
    if key.startswith("compare"):
        return compare_skill(int(key[7:]), number)
    if key.startswith("round") and key[5:].isdigit():
        return rounding_skill(int(key[5:]))
    for prefix, kind in [
        ("add", "add"),
        ("sub", "sub"),
        ("mul", "multiply"),
        ("div", "divide"),
    ]:
        if key.startswith(prefix) and key[len(prefix) :].isdigit():
            return arithmetic(kind, grade, number, int(key[len(prefix) :]))
    if key in ("add_properties", "multiply_properties", "distribution"):
        return property_skill(key)
    if key in ("fraction_add", "fraction_sub", "fraction_multiply", "fraction_divide"):
        return fraction_operation(key)
    if key == "m5_fraction":
        rule, method, example, _, tasks, _, mistake = MATH5["fraction"]
        w, *answers = WORKED["fraction"]
        return dict(
            name="Rút gọn phân số",
            rule=rule,
            method=METHODS["fraction"],
            example=example,
            worked=w,
            tasks=tasks,
            answers=answers,
            mistake=mistake,
        )
    if key == "operations":
        return item(
            "Thứ tự thực hiện phép tính",
            "Trong biểu thức có ngoặc, thực hiện trong ngoặc trước. Không có ngoặc: nhân, chia trước; cộng, trừ sau. Cùng mức ưu tiên thì làm từ trái sang phải.",
            "1. Quan sát ngoặc và các dấu phép tính.\n2. Tính theo thứ tự.\n3. Mỗi bước viết một dòng.",
            "Tính 24 + 6 × 3.",
            ["Thực hiện nhân trước: 6 × 3 = 18.", "24 + 6 × 3 = 24 + 18 = 42."],
            "42.",
            ["Tính (24 + 6) × 3.", "Tính 48 : 6 × 2."],
            [
                (
                    ["Tính trong ngoặc: 24 + 6 = 30.", "(24 + 6) × 3 = 30 × 3 = 90."],
                    "90.",
                ),
                (
                    [
                        "Chia, nhân cùng mức ưu tiên, làm từ trái sang phải.",
                        "48 : 6 × 2 = 8 × 2 = 16.",
                    ],
                    "16.",
                ),
            ],
            "Không tính tất cả phép tính tùy ý từ trái sang phải khi khác mức ưu tiên.",
        )
    if key == "powers":
        return item(
            "Nhân, chia với 10, 100, 1 000",
            "Nhân số tự nhiên với 10, 100, 1 000: viết thêm 1, 2, 3 chữ số 0 vào bên phải. Khi chia hết cho các số đó, bỏ tương ứng các chữ số 0 tận cùng.",
            "1. Đếm số chữ số 0 của 10, 100, 1 000.\n2. Thêm hoặc bớt đúng số chữ số 0 ở tận cùng.\n3. Kiểm tra lại bằng phép tính ngược.",
            "Tính 35 × 100.",
            ["Nhân với 100, viết thêm hai chữ số 0.", "35 × 100 = 3 500."],
            "3 500.",
            ["Tính 720 : 10.", "Tính 24 × 1 000."],
            [
                (["Bỏ một chữ số 0 tận cùng.", "720 : 10 = 72."], "72."),
                (
                    ["Viết thêm ba chữ số 0 bên phải 24.", "24 × 1 000 = 24 000."],
                    "24 000.",
                ),
            ],
            "Quy tắc bỏ chữ số 0 chỉ dùng cho phép chia hết có đủ các chữ số 0 tận cùng.",
        )
    raise KeyError("No authored lesson skill: " + key)


add(
    "components_multiply",
    "Thừa số, tích; số bị chia, số chia, thương",
    "Trong phép nhân, các số được nhân là thừa số, kết quả là tích. Trong phép chia, số bị chia đứng trước dấu chia, số chia đứng sau dấu chia, kết quả là thương.",
    "1. Nhận biết phép nhân hay phép chia.\n2. Gọi tên theo đúng vị trí.\n3. Liên hệ phép nhân và phép chia để kiểm tra.",
    "Nêu tên các thành phần trong 3 × 4 = 12 và 12 : 3 = 4.",
    [
        "Trong 3 × 4 = 12, các thừa số là 3 và 4; tích là 12.",
        "Trong 12 : 3 = 4, số bị chia là 12, số chia là 3, thương là 4.",
    ],
    "Thừa số: 3, 4; tích: 12. Số bị chia: 12; số chia: 3; thương: 4.",
    [
        "Trong 5 × 2 = 10, tích là số nào?",
        "Trong 20 : 5 = 4, số bị chia và số chia là số nào?",
    ],
    [
        (["Kết quả của phép nhân gọi là tích.", "Kết quả đang là 10."], "10."),
        (
            [
                "Số đứng trước dấu chia là 20; số đứng sau dấu chia là 5.",
                "Vậy số bị chia là 20, số chia là 5.",
            ],
            "Số bị chia: 20; số chia: 5.",
        ),
    ],
    "Không đổi chỗ số bị chia và số chia khi gọi tên.",
)

add(
    "paper_shapes",
    "Lắp ghép hình",
    "Có thể ghép các mảnh hình thành hình mới. Các mảnh không chồng lên nhau và không để hở phần cần ghép.",
    "1. Quan sát mảnh có sẵn.\n2. Xoay hoặc chuyển mảnh để thử ghép.\n3. Kiểm tra đường bao và gọi tên hình mới.",
    "Một hình vuông được chia theo đường chéo thành hai mảnh tam giác. Nêu cách ghép lại thành hình vuông.",
    [
        "Xoay hai tam giác để các cạnh theo đường cắt trùng nhau.",
        "Ghép sát hai cạnh này, đường bao ngoài là hình vuông.",
    ],
    "Ghép theo đường chéo ban đầu thành hình vuông.",
    [
        "Hai mảnh ghép chồng lên nhau có phủ đúng hình ban đầu không?",
        "Sau khi ghép đúng hai mảnh từ hình vuông đã cắt, còn cần bỏ mảnh nào không?",
    ],
    [
        (
            [
                "Phần chồng làm một vùng bị tính hai lần và có thể để hở vùng khác.",
                "Cần ghép các mảnh sát nhau, không chồng.",
            ],
            "Chưa đúng; cần xếp lại.",
        ),
        (
            [
                "Hai mảnh tạo thành toàn bộ hình vuông ban đầu.",
                "Ghép đúng thì dùng đủ hai mảnh.",
            ],
            "Không bỏ mảnh nào.",
        ),
    ],
    "Không bắt buộc dùng kéo: có thể dùng mảnh giấy đã cắt sẵn; nhờ người lớn khi cần cắt.",
)

GRADE_MAP = {
    1: """
1:number5 2:number10 3:compare10 4:compare10 5:partition 6:number10,compare10,partition
7:simple_shapes 8:paper_shapes,simple_shapes 9:simple_shapes,paper_shapes
10:small_add 11:small_sub 12:small_add,small_sub 13:small_add,small_sub,partition
14:solids 15:position 16:solids,position 17:number10,compare10 18:small_add,small_sub
19:simple_shapes,solids 20:number10,small_add,small_sub,simple_shapes
21:number100 22:compare100 23:number100,number_line 24:number100,compare100
25:length_cm 26:length_cm 27:length_cm,drawing 28:length_cm,drawing
29:add2 30:add2 31:sub2 32:sub2 33:add2,sub2
34:clock_whole 35:week 36:clock_whole,week 37:clock_whole,week
38:number10,small_add,small_sub 39:number100,add2,sub2 40:simple_shapes,length_cm,clock_whole
41:number100,add2,sub2,simple_shapes,week
""",
    2: """
1:number100 2:number_line 3:components_add 4:more_less 5:add_no2,sub_no2 6:number100,components_add,more_less
7:make_ten_add 8:make_ten_add 9:more_less 10:make_ten_add,more_less
11:make_ten_sub 12:make_ten_sub 13:more_less 14:make_ten_sub,more_less
15:kg 16:litre 17:kg,litre 18:kg,litre 19:add2 20:add2 21:add2,more_less
22:sub2 23:sub2 24:sub2,more_less 25:segments 26:broken_line 27:drawing
28:segments,broken_line,drawing 29:clock 30:calendar 31:clock,calendar 32:clock,calendar
33:make_ten_add,make_ten_sub,add2,sub2 34:segments,broken_line,simple_shapes
35:kg,litre,clock 36:number100,add2,sub2,clock
37:table2 38:components_multiply 39:table2 40:table5 41:table2 42:components_multiply
43:table2 44:table5 45:table2,table5,components_multiply 46:cylinder_sphere 47:cylinder_sphere,solids
48:number1000 49:round_numbers 50:compare1000,round_numbers 51:number1000 52:number1000
53:compare1000 54:number1000,compare1000 55:length_units 56:money
58:length_units,money 59:add_no3 60:add3 61:sub_no3 62:sub3 63:add3,sub3
64:data 65:graph_picture 66:chance 67:data,graph_picture
68:number1000,compare1000 69:add2,sub2 70:add3,sub3 71:table2,table5
72:segments,broken_line,cylinder_sphere 73:length_units,kg,litre,clock,money
74:data,graph_picture,chance 75:number1000,add3,sub3,table5,data
""",
    3: """
1:number1000 2:add3,sub3 3:unknown_add 4:table2,table5 5:table3 6:table4
7:shapes,length_cm,kg,litre 8:number1000,unknown_add,table3,table4
9:table6 10:table7 11:table8 12:table9 13:unknown_multiply 14:unit_fraction
15:table6,table7,unknown_multiply,unit_fraction 16:midpoint 17:circle_parts 18:right_angle
19:shapes 21:solids 22:midpoint,circle_parts,right_angle,solids
23:mul2 24:multiply_compare 25:remainder 26:div2 27:reduce_times 28:two_steps
29:mul2,div2,reduce_times,two_steps 30:mm 31:gram 32:millilitre 33:temperature
34:mm,gram,millilitre,temperature 35:mm,gram,millilitre,temperature
36:mul3 37:div3 38:operations 39:multiply_compare 40:mul3,div3,operations
41:mul3,div3,remainder 42:operations 43:circle_parts,right_angle,mm,gram
44:mul3,div3,operations,two_steps 45:number10000 46:compare10000 47:roman 48:round10,round100
49:number10000,compare10000,roman,round100 50:perimeter 51:area_intro 52:rectangle_area
53:perimeter,area_intro,rectangle_area 54:add4 55:sub4 56:mul4 57:div4
58:add4,sub4,mul4,div4 59:number100000 60:compare100000 61:round1000,round10000
62:number100000,compare100000,round1000 63:add5 64:sub5 65:add5,sub5
66:clock,calendar 67:clock,calendar 68:money 69:clock,calendar,money
70:mul5 71:div5 72:mul5,div5,two_steps 73:data 74:chance
76:number10000,number100000,compare100000 77:add5,sub5 78:mul5,div5
79:shapes,perimeter,rectangle_area,mm,gram 80:data,chance
81:number100000,add5,mul5,rectangle_area,data
""",
    4: """
1:number100000 2:add5,sub5,mul4,div4 3:even_odd 4:letter_expression 5:three_steps
6:number100000,even_odd,letter_expression,three_steps 7:angle_degree 8:angle_degree
9:angle_degree,right_angle 10:number1000000,million 11:million 12:million 13:round100000
14:compare1000000 15:number_line 16:million,round100000,compare1000000
17:large_mass 18:area_units4 19:second_century 20:large_mass,area_units4,second_century
21:large_mass,area_units4,second_century 22:add6 23:sub6 24:add_properties
25:sum_difference 26:add6,sub6,add_properties,sum_difference
27:perpendicular 28:perpendicular,drawing 29:parallel 30:parallel,drawing
31:parallelogram 32:perpendicular,parallel,parallelogram
33:million,compare1000000,round100000 34:add6,sub6,add_properties
35:angle_degree,parallel,perpendicular,parallelogram 36:large_mass,area_units4,second_century
37:million,add6,sub6,sum_difference,angle_degree
38:mul4 39:div4 40:multiply_properties 41:powers 42:distribution
43:mul22 44:div22 45:estimate 46:mean 47:unit_method
48:mul22,div22,mean,unit_method 49:data 50:graph_column 51:event_count
52:data,graph_column,event_count 53:fractions_intro 54:fractions_intro
55:fraction_equal 56:m5_fraction 57:common_denominator 58:fraction_compare
59:fractions_intro,fraction_equal,m5_fraction,common_denominator,fraction_compare
60:fraction_add 61:fraction_sub 62:fraction_add,fraction_sub
63:fraction_multiply 64:fraction_divide 65:fraction_of
66:fraction_multiply,fraction_divide,fraction_of
67:number1000000,even_odd,million 68:add6,sub6,mul22,div22
69:fractions_intro,m5_fraction,common_denominator,fraction_compare
70:fraction_add,fraction_sub,fraction_multiply,fraction_divide
71:angle_degree,parallel,area_units4,large_mass 72:data,graph_column,event_count
73:million,fraction_add,fraction_divide,rectangle_area,data
""",
}
GRADE_MAP = {
    g: {int(part.split(":")[0]): part.split(":")[1].split(",") for part in text.split()}
    for g, text in GRADE_MAP.items()
}

# Lessons explicitly about calculations without carrying use a separate set.


def resolve(key, grade, number):
    if key == "solids" and grade == 1:
        result = dict(STATIC[key])
        result["rule"] = (
            "Khối lập phương có các mặt vuông bằng nhau. Khối hộp chữ nhật có các mặt là hình chữ nhật. Quan sát hộp thật hoặc mô hình rồi xoay để xem các mặt khuất."
        )
        return result
    if key == "money" and grade == 2:
        return item(
            "Tiền Việt Nam",
            "Đọc mệnh giá trên từng tờ tiền. Giá trị tiền tính theo đồng. Các ví dụ này dùng các khoản không quá 1 000 đồng.",
            "1. Đọc mệnh giá.\n2. Cộng tổng tiền hoặc trừ tiền đã dùng.\n3. Ghi đáp số theo đồng.",
            "Có 500 đồng và 200 đồng, dùng 300 đồng. Còn bao nhiêu?",
            [
                "Tổng tiền là:",
                "500 + 200 = 700 (đồng)",
                "Số tiền còn lại là:",
                "700 − 300 = 400 (đồng)",
            ],
            "400 đồng.",
            [
                "Hai tờ 200 đồng và một tờ 500 đồng có tổng bao nhiêu?",
                "Có 1 000 đồng, dùng 600 đồng. Còn bao nhiêu?",
            ],
            [
                (
                    ["Hai tờ 200 đồng có giá trị 400 đồng.", "400 + 500 = 900 (đồng)"],
                    "900 đồng.",
                ),
                (["Số tiền còn lại là:", "1 000 − 600 = 400 (đồng)"], "400 đồng."),
            ],
            "Đếm tổng giá trị, không chỉ đếm số tờ tiền.",
        )
    if key in ("number5", "number10"):
        top = int(key[6:])
        values = [3, 4, 5] if top == 5 else [6, 8, 10]

        def solve(v):
            return (
                [
                    f"Đặt {v} vật, đếm mỗi vật đúng một lần.",
                    f"Đếm được {v} vật; số {v} đọc là {read_number(v)}.",
                ],
                f"{v}; {read_number(v)}.",
            )

        return item(
            f"Đếm các số đến {top}",
            f"Đếm lần lượt từng vật; số cuối cùng cho biết số lượng. Không có vật nào thì dùng số 0. Trong bài này chỉ xét các số từ 0 đến {top}.",
            "1. Chỉ vào từng vật và đếm.\n2. Nói số lượng bằng số cuối cùng.\n3. Viết số và đọc lại, không bỏ sót hoặc đếm hai lần.",
            f"Đếm và viết số cho nhóm có {values[0]} chấm: " + "● " * values[0],
            *solve(values[0]),
            [f"Có nhóm gồm {v} que tính. Đọc và viết số lượng." for v in values[1:]],
            [solve(v) for v in values[1:]],
            "Mỗi vật chỉ đếm một lần; số 0 biểu thị không có vật trong nhóm.",
        )
    if key.startswith(("add_no", "sub_no")):
        digits = int(key[-1])
        kind = "add" if key.startswith("add") else "sub"
        if digits == 2:
            return arithmetic(kind, 1, number, digits)
        pairs = [(123, 212), (231, 123), (342, 125)]
        if kind == "sub":
            pairs = [(a + b, b) for a, b in pairs]
        op = "+" if kind == "add" else "−"

        def solve(a, b):
            result = a + b if kind == "add" else a - b
            return (
                [
                    "Đặt các chữ số cùng hàng thẳng cột.",
                    f"```\n  {a}\n{op} {b}\n-----\n  {result}\n```",
                    "Tính từ phải sang trái; phép tính này không cần nhớ hoặc đổi.",
                    f"{a} {op} {b} = {result}.",
                ],
                str(result) + ".",
            )

        return item(
            "Phép tính không nhớ",
            "Đặt các chữ số cùng hàng thẳng cột; tính từ đơn vị sang chục, trăm. Các ví dụ này không có nhớ hoặc đổi.",
            "1. Đặt tính.\n2. Tính từng hàng từ phải sang trái.\n3. Ghi đủ chữ số kết quả và thử lại.",
            f"Tính {pairs[0][0]} {op} {pairs[0][1]}.",
            *solve(*pairs[0]),
            [f"Tính {a} {op} {b}." for a, b in pairs[1:]],
            [solve(a, b) for a, b in pairs[1:]],
            "Không đặt lệch hàng đơn vị, chục, trăm.",
        )
    return _resolve_base(key, grade, number)
