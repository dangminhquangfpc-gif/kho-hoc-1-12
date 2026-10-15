"""Original starter review for all catalog subjects; shared foundations are explicit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANK = {}


def cards(subject, text, band="all"):
    rows = []
    for line in text.strip().splitlines():
        topic, prompt, correct, b, c, d, reason = line.split("|")
        rows.append(
            dict(
                topic=topic,
                question=prompt,
                choices=[correct, b, c, d],
                explanation=reason,
            )
        )
    BANK[(subject, band)] = rows


cards(
    "tieng_viet",
    """
đọc hiểu|Đọc: “Mai tưới cây vào buổi sáng.” Ai tưới cây?|Mai|Cây|Buổi sáng|Không có ai|Từ Mai chỉ người thực hiện việc tưới cây trong câu.
từ chỉ sự vật|Từ nào gọi tên một đồ vật?|bút|chạy|nhanh|đẹp|Bút là tên đồ vật; các từ còn lại không gọi tên đồ vật.
từ chỉ hoạt động|Từ nào chỉ một hoạt động?|đọc|bàn|xanh|tròn|Đọc là hoạt động; bàn là đồ vật, xanh và tròn là đặc điểm.
dấu câu|Câu hỏi “Bạn tên là gì” cần kết thúc bằng dấu nào?|Dấu hỏi chấm|Dấu phẩy|Dấu hai chấm|Dấu gạch ngang|Câu dùng để hỏi thường kết thúc bằng dấu hỏi chấm.
viết câu|Cách viết nào phù hợp ở đầu một câu?|Viết hoa chữ cái đầu|Luôn viết toàn chữ thường|Không cần chữ cái|Luôn bỏ dấu tiếng Việt|Chữ cái đầu của câu được viết hoa.
đọc hiểu|Đọc: “Sau cơn mưa, sân trường còn ướt.” Sân trường ướt sau sự việc nào?|Cơn mưa|Giờ ăn trưa|Buổi biểu diễn|Lần quét sân|Cụm từ sau cơn mưa nêu sự việc xảy ra trước khi sân còn ướt.
""",
    "primary",
)
cards(
    "ngu_van",
    """
đọc hiểu|Khi nhận xét một nhân vật, cách lập luận nào có căn cứ nhất?|Dẫn chi tiết trong văn bản rồi phân tích|Chỉ nói mình thích nhân vật|Đoán ý tác giả không đọc bài|Chép lời bình mà không xem văn bản|Nhận xét cần dựa vào chi tiết và giải thích quan hệ giữa chi tiết với nhận xét.
người kể chuyện|Câu “Tôi bước vào lớp và nhìn thấy bạn Nam” gợi người kể ở ngôi nào?|Ngôi thứ nhất|Ngôi thứ hai|Luôn là ngôi thứ ba|Không thể có người kể|Đại từ tôi cho thấy người kể trực tiếp kể từ vị trí ngôi thứ nhất.
so sánh|Câu “Mặt hồ sáng như gương” sử dụng biện pháp nào?|So sánh|Liệt kê|Nói giảm|Đảo ngữ|Từ như nối mặt hồ với gương để làm nổi bật đặc điểm sáng.
lập luận|Một đoạn nghị luận nên có quan hệ nào giữa lí lẽ và bằng chứng?|Bằng chứng hỗ trợ lí lẽ và luận điểm|Bằng chứng không liên quan chủ đề|Lí lẽ chỉ cần dài|Mọi ý kiến đều tự chứng minh|Bằng chứng cần phù hợp để người đọc kiểm tra lí lẽ của người viết.
tóm tắt|Điều nào phù hợp khi tóm tắt văn bản?|Giữ ý chính và diễn đạt ngắn gọn|Thêm sự kiện không có trong bài|Chép mọi câu|Chỉ kể cảm xúc của mình|Tóm tắt giữ thông tin chính, không thêm nội dung làm sai lệch văn bản.
viết và sửa|Sau khi viết bản nháp, nên làm gì?|Kiểm tra bố cục, lập luận và diễn đạt|Xóa toàn bộ dẫn chứng|Bỏ mọi dấu câu|Không đọc lại|Đọc lại giúp sửa lỗi và làm rõ quan hệ giữa các ý.
""",
)
cards(
    "tieng_anh",
    """
vocabulary|Choose the word for an animal that says “meow”.|cat|desk|book|chair|A cat is an animal; desk, book and chair are objects.
be verb|Choose: “She ___ my friend.”|is|am|are|be|Use is with she in the present simple of be.
plural nouns|Choose the plural of “book”.|books|bookes|bookies|book's|The regular plural of book is books; an apostrophe does not form this plural.
possessive adjectives|Choose: “I have a bag. It is ___ bag.”|my|your|his|her|My shows that the bag belongs to the speaker I.
prepositions|A ball is inside a box. Choose: “The ball is ___ the box.”|in|under|behind|above|In describes being inside something.
reading|Read: “Ben has two pencils and one ruler.” How many pencils does Ben have?|Two|One|Three|Four|The sentence explicitly says two pencils.
""",
    "primary",
)
cards(
    "tieng_anh",
    """
present simple|Choose: “Lan ___ to school every day.”|walks|walk|walking|to walk|A third-person singular subject takes walks in an affirmative present simple sentence.
past simple|Choose: “We ___ the museum yesterday.”|visited|visit|visits|visiting|Yesterday points to the past; the regular past form is visited.
comparatives|Choose: “This bag is ___ than that bag.”|heavier|heaviest|heavy|most heavy|Than calls for a comparative; heavy becomes heavier.
modals|Choose: “You must ___ a helmet.”|wear|wears|wearing|wore|A modal such as must is followed by the base form wear.
conditionals|Choose: “If it rains tomorrow, we ___ indoors.”|will stay|stayed|had stayed|stays|In a typical first conditional, the main clause uses will plus a base verb.
reading|Read: “Minh cycles to school to reduce air pollution.” Why does Minh cycle?|To reduce air pollution|To buy a car|To miss lessons|To increase traffic|The text states the purpose with to reduce air pollution.
""",
    "lower",
)
cards(
    "tieng_anh",
    """
passive voice|Choose: “The report ___ by the team yesterday.”|was completed|completes|is completing|has completing|The subject receives the action; yesterday requires the past passive was completed.
relative clauses|Choose: “The student ___ won the prize is my cousin.”|who|where|when|whose|Who acts as the subject of a relative clause referring to a person.
second conditional|Choose: “If I had more time, I ___ another language.”|would learn|will learns|am learn|had learning|For this hypothetical present condition, use would plus the base form.
present perfect|Choose: “She has ___ the project.”|finished|finish|finishes|finishing|Present perfect uses has or have followed by a past participle.
academic reading|An article gives data and identifies its sources. What best helps evaluate the claim?|Check the evidence and source reliability|Trust the title alone|Ignore all numbers|Count only the pictures|Evaluation depends on evidence quality and the reliability of its sources.
cohesion|Choose the connector: “The task was difficult. ___, we completed it.”|However|Because|For example|In addition to|However signals a contrast between difficulty and successful completion.
""",
    "upper",
)
cards(
    "dao_duc",
    """
trung thực|Em làm vỡ đồ dùng của lớp. Hành động nào thể hiện trung thực?|Báo với thầy cô và nhận trách nhiệm|Đổ lỗi cho bạn|Giấu mảnh vỡ|Nói rằng chưa ai thấy|Trung thực là nói đúng sự việc và chịu trách nhiệm phù hợp.
quan tâm|Thấy bạn bị ngã trong sân trường, em nên làm gì trước?|Báo người lớn và hỏi bạn có cần giúp không|Cười trêu bạn|Kéo mạnh tay bạn ngay|Bỏ đi|Nhờ người lớn giúp và quan tâm bạn là cách phù hợp, tránh làm bạn đau thêm.
giữ lời hứa|Em đã hứa trả sách cho bạn hôm nay. Cách làm nào phù hợp?|Trả đúng hẹn hoặc báo sớm nếu có trở ngại|Giữ luôn sách|Không cần nói gì|Đổ lỗi cho người khác|Giữ lời hứa gồm thực hiện lời hứa và trao đổi có trách nhiệm khi gặp trở ngại.
bảo vệ đồ dùng|Sau khi dùng đồ dùng học tập chung, em nên làm gì?|Cất đúng nơi và giữ gìn sạch sẽ|Vứt dưới đất|Mang về mà không hỏi|Làm dấu phá hỏng|Đồ dùng chung cần được giữ gìn để mọi người đều sử dụng được.
tôn trọng|Khi bạn có ý kiến khác em, cách ứng xử nào phù hợp?|Lắng nghe và trao đổi lịch sự|Chế giễu bạn|Ngắt lời liên tục|Không cho bạn nói|Tôn trọng thể hiện qua lắng nghe và trao đổi mà không xúc phạm.
bảo vệ môi trường|Hành động nào giúp giữ lớp sạch?|Bỏ rác đúng nơi quy định|Vứt rác sau bàn|Đẩy rác sang lớp khác|Đốt rác trong lớp|Bỏ rác đúng nơi giúp bảo vệ môi trường học tập.
""",
)
cards(
    "the_chat",
    """
khởi động|Trước khi vận động, việc nào phù hợp?|Khởi động theo hướng dẫn của giáo viên|Bắt đầu ngay bằng động tác khó nhất|Không kiểm tra không gian|Nhịn uống nước cả buổi|Khởi động và làm theo hướng dẫn giúp chuẩn bị cơ thể cho hoạt động.
an toàn|Nếu đau hoặc chóng mặt khi tập, em nên làm gì?|Dừng tập và báo giáo viên|Cố tập mạnh hơn|Giấu triệu chứng|Tự uống thuốc của bạn|Dừng hoạt động và báo người phụ trách giúp được hỗ trợ phù hợp.
hợp tác|Trong trò chơi theo đội, cách nào thể hiện hợp tác?|Thực hiện luật và phối hợp với đồng đội|Cố tình cản bạn cùng đội|Tự thay luật|Chỉ trách người khác|Hợp tác cần tôn trọng luật và hỗ trợ các thành viên.
không gian tập|Trước khi tập chạy trong sân, nên kiểm tra điều gì?|Mặt sân và chướng ngại vật|Màu bút trong cặp|Tên ứng dụng điện thoại|Số trang sách|Mặt sân và chướng ngại vật ảnh hưởng trực tiếp đến an toàn vận động.
trang phục|Trang phục khi học thể chất nên như thế nào?|Phù hợp hoạt động và hướng dẫn nhà trường|Vướng víu để gây chú ý|Có vật sắc nhọn trong túi|Luôn mang dép trơn|Trang phục phù hợp giúp vận động thuận tiện và giảm nguy cơ vướng hoặc trượt.
ứng xử thể thao|Sau một trận chơi, cách ứng xử nào phù hợp?|Tôn trọng kết quả và ghi nhận nỗ lực của các bạn|Xúc phạm đội thắng|Đổ lỗi và gây gổ|Tự ý sửa điểm|Tinh thần thể thao gồm tôn trọng luật, kết quả và người cùng tham gia.
""",
)
cards(
    "nghe_thuat",
    """
nhịp điệu|Khi cả nhóm hát cùng nhau, điều gì giúp hát đều?|Lắng nghe và giữ nhịp chung|Mỗi người tự đổi nhịp|Hát càng lớn càng tốt|Không nghe người khác|Nhịp chung giúp các thành viên phối hợp khi hát.
màu sắc|Muốn tạo một bức tranh có các mảng dễ phân biệt, có thể dùng điều gì?|Sự khác nhau về màu và độ đậm nhạt|Chỉ dùng một nét không đổi|Bỏ hết mảng hình|Che mọi hình bằng cùng một màu|Màu và độ đậm nhạt giúp phân biệt mảng và tạo điểm nhấn.
quan sát|Trước khi vẽ một chiếc lá, việc nào hữu ích?|Quan sát hình dáng và đường gân|Không nhìn chiếc lá|Chỉ sao chép tên lá|Xóa mọi nét quan sát|Quan sát giúp người vẽ nhận biết đặc điểm của đối tượng.
biểu diễn|Khi bạn đang biểu diễn, khán giả nên làm gì?|Lắng nghe và cổ vũ phù hợp|La hét để ngắt tiết mục|Chạy lên sân khấu tùy ý|Chế giễu bạn|Tôn trọng người biểu diễn góp phần tạo môi trường nghệ thuật tích cực.
vật liệu|Khi dùng kéo làm sản phẩm thủ công, cần làm gì?|Dùng theo hướng dẫn và giữ an toàn|Đùa nghịch với đầu kéo|Chĩa kéo vào bạn|Chạy khi cầm kéo mở|Dụng cụ cần được sử dụng đúng hướng dẫn và an toàn.
sáng tạo|Một sản phẩm sáng tạo có thể bắt đầu bằng việc nào?|Thử nhiều cách sắp xếp hình và màu|Chỉ chép mà không suy nghĩ|Không thử ý tưởng|Luôn loại mọi ý kiến khác|Thử nghiệm giúp khám phá cách thể hiện ý tưởng riêng.
""",
)
cards(
    "trai_nghiem",
    """
tự quản|Để chuẩn bị cặp sách cho ngày mai, em nên làm gì?|Xem thời khóa biểu và kiểm tra đồ cần mang|Mang mọi đồ trong nhà|Không cần kiểm tra|Chỉ mang đồ chơi|Thời khóa biểu giúp chuẩn bị đúng đồ dùng cần thiết.
làm việc nhóm|Khi nhóm nhận nhiệm vụ, bước nào hữu ích?|Thống nhất mục tiêu và chia việc phù hợp|Ai cũng chờ người khác|Một bạn làm hết mà không trao đổi|Bỏ qua nhiệm vụ|Mục tiêu rõ và phân công giúp nhóm phối hợp.
quản lí thời gian|Cách nào giúp hoàn thành việc đúng hạn?|Lập kế hoạch và theo dõi tiến độ|Chờ đến phút cuối|Không ghi nhiệm vụ|Làm việc khác suốt thời gian|Kế hoạch giúp chủ động sắp xếp thời gian.
giải quyết mâu thuẫn|Khi bất đồng với bạn, em nên bắt đầu thế nào?|Bình tĩnh nói rõ ý kiến và lắng nghe|Dọa bạn|Đăng lời xúc phạm|Giật đồ của bạn|Trao đổi bình tĩnh giúp hiểu vấn đề và tìm cách giải quyết.
cảm xúc|Khi lo lắng vì việc học, cách nào phù hợp?|Chia sẻ với người lớn đáng tin cậy|Giấu mọi khó khăn mãi|Tự trách mình liên tục|Bỏ hết hoạt động|Chia sẻ giúp nhận hỗ trợ và tìm cách xử lí khó khăn.
trách nhiệm|Sau hoạt động chung, nhóm nên làm gì?|Thu dọn và đánh giá việc đã làm|Bỏ lại đồ dùng|Đổ lỗi cho người vắng mặt|Không cần kết thúc hoạt động|Thu dọn và nhìn lại giúp rèn trách nhiệm và cải thiện lần sau.
""",
)
cards(
    "tu_nhien_xa_hoi",
    """
giác quan|Bộ phận nào giúp chúng ta nghe âm thanh?|Tai|Mắt|Mũi|Da|Tai là cơ quan tiếp nhận âm thanh.
thực vật|Bộ phận nào của nhiều cây giúp hút nước từ đất?|Rễ|Hoa|Quả|Hạt khô|Rễ hấp thụ nước và chất khoáng từ đất.
vệ sinh|Trước khi ăn, việc nào giúp giữ vệ sinh?|Rửa tay đúng cách|Chỉ lau tay vào áo|Chạm tay vào rác|Không cần làm gì|Rửa tay đúng cách giúp giảm chất bẩn và vi sinh vật trên tay.
gia đình|Khi thấy ổ điện bị hỏng, em nên làm gì?|Tránh chạm và báo người lớn|Tự chọc vào ổ|Đổ nước vào ổ|Rủ bạn thử chạm|Điện có thể nguy hiểm; trẻ em cần báo người lớn để xử lí.
thời tiết|Khi trời mưa, đồ dùng nào giúp tránh bị ướt?|Áo mưa phù hợp|Vở giấy|Mũ giấy|Quạt cầm tay|Áo mưa giúp che cơ thể khỏi nước mưa.
động vật|Con vật nào sau đây thường sống dưới nước?|Cá|Mèo|Gà|Trâu|Cá là động vật thích nghi với môi trường nước.
""",
)
cards(
    "tin_hoc_cong_nghe",
    """
thông tin|Thông tin giúp chúng ta làm gì?|Hiểu sự việc và lựa chọn cách xử lí|Luôn bỏ qua mọi quyết định|Thay thế mọi suy nghĩ|Không liên quan học tập|Thông tin hỗ trợ nhận biết và ra quyết định.
thiết bị|Thiết bị nào thường dùng để nhập chữ vào máy tính?|Bàn phím|Màn hình|Loa|Máy chiếu|Bàn phím có các phím để nhập chữ và lệnh.
an toàn số|Khi người lạ hỏi mật khẩu tài khoản, em nên làm gì?|Không cung cấp và báo người lớn đáng tin cậy|Gửi ngay|Đăng mật khẩu công khai|Nhờ người lạ giữ hộ|Mật khẩu cần được bảo vệ để tránh truy cập trái phép.
sản phẩm công nghệ|Đèn bàn có công dụng chính nào?|Chiếu sáng chỗ học tập|Làm lạnh nước|In tài liệu|Đo chiều cao|Đèn bàn là sản phẩm giúp cung cấp ánh sáng.
sử dụng đồ dùng|Trước khi sử dụng một đồ dùng mới, nên làm gì?|Đọc hoặc nghe hướng dẫn phù hợp|Tự tháo mọi bộ phận|Dùng sai mục đích để thử|Bỏ qua cảnh báo|Hướng dẫn giúp dùng sản phẩm đúng cách và an toàn.
thiết kế|Khi làm một đồ vật thủ công, bước nào nên có?|Lên ý tưởng và chọn vật liệu phù hợp|Cắt vật liệu tùy ý ngay|Không xem yêu cầu|Chỉ đặt tên sản phẩm|Thiết kế cần hiểu yêu cầu, chọn phương án và vật liệu.
""",
)
cards(
    "khoa_hoc",
    """
trạng thái của nước|Khi nước lỏng đông lại, nó chuyển chủ yếu sang trạng thái nào?|Rắn|Khí|Không có trạng thái|Luôn biến mất|Nước đóng băng trở thành nước đá ở trạng thái rắn.
ánh sáng|Vật nào tự phát ra ánh sáng khi hoạt động?|Bóng đèn đang sáng|Quyển vở|Chiếc bàn|Hòn đá thông thường|Bóng đèn đang hoạt động là nguồn sáng; các vật kia không tự phát sáng trong điều kiện thường.
chuỗi thức ăn|Trong chuỗi cỏ → châu chấu → chim, châu chấu ăn gì?|Cỏ|Chim|Cả cỏ và chim theo sơ đồ|Không ăn gì|Mũi tên thể hiện hướng truyền thức ăn từ cỏ đến châu chấu.
hỗn hợp|Cách nào có thể tách cát không tan khỏi nước?|Lọc bằng vật liệu lọc phù hợp|Chỉ khuấy mạnh|Thêm cát|Đổi tên hỗn hợp|Lọc giữ lại các hạt cát không tan và cho nước đi qua.
môi trường|Việc nào giúp tiết kiệm nước?|Khóa vòi sau khi dùng|Để vòi chảy liên tục|Xả nước không mục đích|Giấu chỗ rò nước|Khóa vòi tránh lãng phí nước.
dinh dưỡng|Một chế độ ăn phù hợp nên như thế nào?|Đa dạng thực phẩm và phù hợp nhu cầu|Chỉ ăn một loại mãi|Bỏ mọi bữa sáng|Chỉ uống nước ngọt|Đa dạng thực phẩm giúp cung cấp các nhóm chất cần thiết; nhu cầu cụ thể tùy người.
""",
)
cards(
    "khoa_hoc_tu_nhien",
    """
tế bào|Đơn vị cấu trúc cơ bản của cơ thể sống là gì?|Tế bào|Hạt cát|Giọt mực|Sợi kim loại|Tế bào là đơn vị cấu trúc và chức năng cơ bản của cơ thể sống.
khối lượng riêng|Khối lượng riêng được tính bằng công thức nào?|Khối lượng chia thể tích|Khối lượng nhân thể tích|Thể tích chia thời gian|Lực chia chiều dài|D = m/V với các đại lượng và đơn vị nhất quán.
nguyên tử|Hạt nào trong nguyên tử mang điện tích âm?|Electron|Proton|Neutron|Hạt nhân nói chung|Electron mang điện tích âm; proton dương và neutron không mang điện.
phản ứng hóa học|Trong một phản ứng hóa học thông thường của hệ kín, đại lượng nào được bảo toàn?|Tổng khối lượng|Màu của mọi chất|Trạng thái của mọi chất|Thể tích mọi chất luôn không đổi|Định luật bảo toàn khối lượng áp dụng khi xét đầy đủ các chất trong hệ kín.
mạch điện|Để có dòng điện trong một mạch đơn giản dùng pin, điều kiện nào cần thiết?|Có đường dẫn kín nối qua nguồn|Chỉ cần dây đứt|Không cần nguồn|Luôn tháo cả hai đầu dây|Mạch phải kín và có nguồn để duy trì dòng điện trong ví dụ này.
quang hợp|Trong quang hợp, cây xanh sử dụng năng lượng chủ yếu từ đâu?|Ánh sáng|Tiếng động|Ma sát của lá|Nhiệt từ dây điện|Ánh sáng cung cấp năng lượng cho quá trình quang hợp.
""",
)
cards(
    "lich_su_dia_li",
    """
bản đồ|Trên bản đồ có chú giải, chú giải giúp làm gì?|Hiểu ý nghĩa các kí hiệu|Thay đổi vị trí địa lí|Xóa mọi khoảng cách|Tự thay đổi thời tiết|Chú giải giải thích các kí hiệu được dùng trên bản đồ.
phương hướng|Nếu bản đồ quy ước phía trên là bắc, phía bên phải là hướng nào?|Đông|Tây|Nam|Bắc|Trong quy ước này, đông ở bên phải, tây ở bên trái.
tư liệu lịch sử|Khi tìm hiểu một sự kiện lịch sử, cách nào đáng tin cậy hơn?|Đối chiếu các tư liệu và xem nguồn gốc|Tin mọi lời truyền miệng|Chỉ nhìn tiêu đề|Bỏ qua thời gian|Nguồn gốc và đối chiếu tư liệu giúp kiểm tra thông tin lịch sử.
trình tự thời gian|Để sắp xếp các sự kiện theo thời gian, nên dựa vào gì?|Mốc thời gian của các sự kiện|Độ dài tên sự kiện|Màu chữ|Số người kể lại|Trình tự lịch sử dựa trên thời điểm diễn ra sự kiện.
địa hình|Địa hình đồng bằng thường có đặc điểm nào so với miền núi?|Tương đối bằng phẳng hơn|Luôn có đỉnh cao nhất|Không có đất|Không bao giờ có sông|Đồng bằng nhìn chung thấp và tương đối bằng phẳng; không có nghĩa hoàn toàn phẳng.
di sản|Cách nào giúp bảo vệ di sản ở địa phương?|Tôn trọng quy định khi tham quan|Viết lên hiện vật|Mang hiện vật về|Phá bảng giới thiệu|Bảo vệ di sản cần giữ gìn hiện vật và tuân thủ quy định.
""",
)
cards(
    "tin_hoc",
    """
thuật toán|Một thuật toán cần có đặc điểm nào?|Các bước rõ ràng để giải một bài toán xác định|Chỉ là tên máy tính|Không có đầu vào hay mục tiêu|Mọi bước đều ngẫu nhiên|Thuật toán mô tả trình tự thực hiện để giải quyết bài toán.
dữ liệu|Dữ liệu và thông tin có quan hệ nào?|Dữ liệu được xử lí có thể cung cấp thông tin|Hai khái niệm không bao giờ liên quan|Dữ liệu luôn là ảnh|Thông tin chỉ có trong sách|Xử lí và diễn giải dữ liệu có thể giúp thu nhận thông tin.
bảng tính|Trong bảng tính, công thức thường bắt đầu bằng kí tự nào?|=|#|?|;|Dấu bằng cho biết nội dung ô là công thức.
an toàn tài khoản|Biện pháp nào tăng bảo vệ tài khoản?|Mật khẩu riêng và xác thực nhiều yếu tố khi có|Dùng một mật khẩu cho mọi nơi|Gửi mã xác thực cho người lạ|Đăng mật khẩu lên mạng|Mật khẩu riêng và nhiều yếu tố giảm nguy cơ mất quyền truy cập.
vòng lặp|Trong lập trình, vòng lặp được dùng khi nào?|Khi cần thực hiện lặp lại một nhóm thao tác|Chỉ khi in đúng một kí tự|Để bỏ mọi điều kiện|Để ngăn chương trình chạy|Vòng lặp diễn tả thao tác lặp theo số lần hoặc điều kiện.
nguồn thông tin|Khi thấy một tin gây bất ngờ trên mạng, nên làm gì trước khi chia sẻ?|Kiểm tra nguồn và đối chiếu thông tin|Chia sẻ ngay|Chỉ xem số lượt thích|Đổi tiêu đề rồi đăng|Kiểm chứng giúp hạn chế lan truyền thông tin sai.
""",
)
cards(
    "cong_nghe",
    """
thiết kế kĩ thuật|Bước nào giúp xác định yêu cầu thiết kế?|Tìm hiểu nhu cầu và điều kiện sử dụng|Làm sản phẩm mà không hỏi mục tiêu|Chỉ chọn màu đẹp|Bỏ qua người dùng|Thiết kế cần bắt đầu từ nhu cầu và điều kiện thực tế.
vật liệu|Khi chọn vật liệu, nên xét điều gì?|Tính chất, công dụng và điều kiện sử dụng|Chỉ tên gọi|Chỉ màu hộp đựng|Không cần độ bền|Vật liệu phải phù hợp yêu cầu và môi trường sử dụng.
an toàn điện|Khi thiết bị điện có dấu hiệu hỏng, hành động nào phù hợp?|Ngừng sử dụng và nhờ người có chuyên môn xử lí|Tự chạm dây trần|Tiếp tục dùng khi có khói|Đổ nước lên thiết bị đang cấp điện|Thiết bị hỏng có thể gây nguy hiểm và cần được xử lí đúng chuyên môn.
bản vẽ|Bản vẽ kĩ thuật có công dụng gì?|Truyền đạt thông tin về hình dạng và kích thước|Thay thế mọi vật liệu|Làm thiết bị tự chạy|Chỉ trang trí trang giấy|Bản vẽ là phương tiện truyền đạt thông tin kĩ thuật.
quy trình|Một quy trình sản xuất hợp lí cần điều gì?|Các bước có thứ tự và kiểm tra chất lượng|Không có bước kiểm tra|Mọi bước đảo tùy ý|Chỉ đóng gói|Thứ tự và kiểm tra giúp đạt yêu cầu sản phẩm.
bền vững|Lựa chọn nào giúp sử dụng sản phẩm bền vững hơn?|Bảo dưỡng và dùng đúng hướng dẫn|Thay mới khi chưa cần|Bỏ qua sửa chữa phù hợp|Dùng sai công dụng|Dùng đúng và bảo dưỡng có thể kéo dài tuổi thọ và giảm lãng phí.
""",
)
cards(
    "gdcd",
    """
tôn trọng sự thật|Hành vi nào thể hiện tôn trọng sự thật?|Kiểm tra thông tin trước khi khẳng định|Bịa chi tiết để câu chuyện hay hơn|Che giấu chứng cứ|Nói theo số đông bất kể đúng sai|Tôn trọng sự thật cần trung thực và có căn cứ.
tự lập|Tự lập trong học tập được thể hiện thế nào?|Chủ động làm việc và hỏi hỗ trợ khi cần|Để bạn làm toàn bộ|Không bao giờ được hỏi ai|Chép đáp án để khỏi suy nghĩ|Tự lập là chủ động có trách nhiệm, vẫn có thể tìm sự hỗ trợ phù hợp.
hợp tác|Khi làm việc chung, hành động nào có trách nhiệm?|Hoàn thành phần việc và trao đổi với nhóm|Không báo khi không làm được|Nhận công của người khác|Cố tình giấu thông tin cần thiết|Trách nhiệm cá nhân góp phần vào kết quả chung.
bảo vệ trẻ em|Khi bị đe dọa hoặc xâm hại, học sinh nên tìm ai?|Người lớn đáng tin cậy hoặc cơ quan hỗ trợ phù hợp|Người đang đe dọa mình để xin giữ bí mật|Người lạ yêu cầu thông tin riêng|Không được tìm ai|Tìm hỗ trợ đáng tin cậy giúp bảo vệ an toàn; không cần chịu đựng một mình.
tiêu dùng|Trước khi mua một món đồ, nên xem điều gì?|Nhu cầu, giá và khả năng chi trả|Chỉ lời quảng cáo|Chỉ lời thúc giục|Không cần thông tin|Tiêu dùng có trách nhiệm cần cân nhắc thông tin và điều kiện thực tế.
môi trường|Trách nhiệm bảo vệ môi trường thể hiện ở việc nào?|Giảm rác và giữ gìn không gian chung|Vứt rác nơi ít người thấy|Đốt mọi loại rác tùy ý|Không cần tuân thủ quy định|Hành vi cá nhân có tác động tới môi trường chung.
""",
)
cards(
    "huong_nghiep",
    """
tự nhận thức|Để lựa chọn hướng học tập, nên bắt đầu bằng điều gì?|Tìm hiểu sở thích, năng lực và giá trị của bản thân|Chỉ chọn theo bạn|Chỉ nghe quảng cáo|Không xem điều kiện cá nhân|Tự nhận thức là một cơ sở để lựa chọn hướng phát triển phù hợp.
tìm hiểu nghề|Nguồn nào hữu ích khi tìm hiểu một nghề?|Mô tả công việc và trao đổi với người làm nghề|Một tin đồn không có nguồn|Chỉ tên nghề|Chỉ hình ảnh đồng phục|Hiểu nhiệm vụ và điều kiện nghề giúp lựa chọn có căn cứ.
lập kế hoạch|Một kế hoạch học tập khả thi cần gì?|Mục tiêu, bước thực hiện và thời gian|Chỉ mong muốn chung|Không có mốc theo dõi|Không có hành động|Các bước cụ thể giúp biến mục tiêu thành việc có thể thực hiện.
kĩ năng giao tiếp|Trong thảo luận nhóm, cách nào hỗ trợ giao tiếp?|Lắng nghe, đặt câu hỏi và phản hồi lịch sự|Ngắt mọi lời nói|Chỉ nói về mình|Không đọc nhiệm vụ|Giao tiếp hiệu quả cần cả chia sẻ và tiếp nhận thông tin.
thích ứng|Khi kế hoạch gặp trở ngại, nên làm gì?|Đánh giá nguyên nhân và điều chỉnh hợp lí|Giữ nguyên bất kể tình huống|Bỏ mọi mục tiêu ngay|Đổ lỗi mà không kiểm tra|Điều chỉnh dựa trên nguyên nhân giúp duy trì tiến bộ.
sức khỏe tinh thần|Khi áp lực kéo dài ảnh hưởng sinh hoạt, nên làm gì?|Tìm hỗ trợ từ người đáng tin cậy hoặc chuyên môn phù hợp|Tự giấu mọi khó khăn|Dùng lời xúc phạm bản thân|Coi mọi sự hỗ trợ là thất bại|Tìm hỗ trợ là hành động phù hợp để chăm sóc sức khỏe tinh thần.
""",
)
cards(
    "lich_su",
    """
tư liệu|Một tư liệu lịch sử cần được đánh giá theo yếu tố nào?|Nguồn gốc, bối cảnh và nội dung|Chỉ độ dài|Chỉ số lần chia sẻ|Chỉ màu bìa|Đánh giá nguồn gốc và bối cảnh giúp hiểu giá trị và giới hạn của tư liệu.
nguyên nhân và kết quả|Khi giải thích một sự kiện, cần phân biệt điều gì?|Nguyên nhân, diễn biến và kết quả|Tên dài và tên ngắn|Màu bản đồ và màu ảnh|Số trang nhiều và ít|Ba thành phần có quan hệ nhưng không phải là một.
niên đại|Hai sự kiện lần lượt diễn ra năm 1945 và 1954. Sự kiện nào trước?|Sự kiện năm 1945|Sự kiện năm 1954|Cùng thời điểm|Không thể sắp xếp theo năm|Trong Công nguyên, năm 1945 trước năm 1954.
đối chiếu|Nếu hai tư liệu kể khác nhau về một sự kiện, nên làm gì?|Đối chiếu bối cảnh và nguồn khác|Xóa một tư liệu ngay|Chọn tư liệu dài hơn luôn đúng|Không cần kiểm tra|Đối chiếu giúp xác định điểm phù hợp và giới hạn của mỗi nguồn.
di sản văn hóa|Bảo tồn di sản lịch sử nhằm điều gì?|Giữ giá trị và truyền hiểu biết cho thế hệ sau|Xóa mọi dấu tích|Biến mọi hiện vật thành hàng bán|Ngăn mọi nghiên cứu|Di sản giúp hiểu quá khứ và có giá trị với cộng đồng.
đọc dòng thời gian|Dòng thời gian giúp người học nhận biết điều gì?|Trình tự và khoảng cách thời gian giữa sự kiện|Độ cao địa hình|Chỉ lượng mưa|Tên nguyên tố|Dòng thời gian biểu diễn mốc và thứ tự các sự kiện.
""",
)
cards(
    "quoc_phong",
    """
kỉ luật|Trong hoạt động tập thể có hướng dẫn, học sinh cần làm gì?|Tuân thủ quy định và hướng dẫn an toàn|Tự ý thay đổi thao tác|Đùa nghịch khi thực hành|Bỏ qua người hướng dẫn|Kỉ luật và hướng dẫn an toàn là yêu cầu cơ bản của hoạt động tập thể.
an toàn vật lạ|Khi thấy vật nghi là vật liệu nổ, hành động nào phù hợp?|Không chạm, tránh xa và báo người có trách nhiệm|Mang về xem|Tự tháo|Ném thử|Không tiếp cận hoặc tự xử lí vật nghi nguy hiểm; cần báo đúng người phụ trách.
trách nhiệm công dân|Tìm hiểu quốc phòng và an ninh giúp học sinh làm gì?|Hiểu trách nhiệm với cộng đồng và đất nước|Tự ý thực hiện việc nguy hiểm|Thay mọi quy định pháp luật|Không cần học môn khác|Giáo dục giúp nhận thức trách nhiệm và tuân thủ quy định.
ứng phó tình huống|Khi có thông báo sơ tán của nhà trường, nên làm gì?|Theo hướng dẫn và giữ trật tự|Quay lại tìm đồ bất chấp hướng dẫn|Chen lấn|Tự chọn đường chưa biết|Giữ trật tự và theo hướng dẫn giúp sơ tán an toàn.
kiểm chứng thông tin|Trước tin liên quan an ninh chưa rõ nguồn, nên làm gì?|Kiểm chứng qua nguồn chính thức phù hợp|Chia sẻ ngay|Thêm chi tiết suy đoán|Khẳng định chỉ vì nhiều lượt xem|Tin chưa kiểm chứng có thể gây hiểu lầm và cần được xác minh.
sơ cứu và hỗ trợ|Khi gặp người bị thương, học sinh cần ưu tiên điều gì?|An toàn hiện trường và gọi hỗ trợ phù hợp|Tự làm mọi thao tác chưa học|Tụ tập cản đường|Bỏ qua nguy hiểm xung quanh|Đảm bảo an toàn và tìm hỗ trợ là ưu tiên; thao tác chỉ thực hiện trong khả năng được hướng dẫn.
""",
)
cards(
    "dia_li",
    """
tỉ lệ bản đồ|Bản đồ tỉ lệ 1:100 000 có 1 cm tương ứng khoảng cách thực bao nhiêu?|1 km|100 km|10 m|1 m|100 000 cm = 1 000 m = 1 km.
biểu đồ|Biểu đồ đường thường phù hợp để thể hiện gì?|Sự thay đổi của đại lượng theo thời gian|Luôn chỉ địa hình|Chỉ vị trí thành phố|Không thể so sánh thời điểm|Đường nối các mốc giúp nhận biết xu hướng biến đổi.
thời tiết và khí hậu|Khí hậu khác thời tiết chủ yếu ở điểm nào?|Đặc trưng dài hạn thay vì trạng thái ngắn hạn|Chỉ có ở miền núi|Luôn là lượng mưa một ngày|Không liên quan khí quyển|Khí hậu mô tả đặc trưng và quy luật dài hạn; thời tiết là trạng thái tại thời gian cụ thể.
dân số|Mật độ dân số được tính thế nào?|Dân số chia diện tích|Diện tích chia số ngày|Dân số nhân diện tích|Số nhà chia nhiệt độ|Mật độ cho biết số người trung bình trên một đơn vị diện tích.
phát triển bền vững|Phát triển bền vững cần xem xét các mặt nào?|Kinh tế, xã hội và môi trường|Chỉ sản lượng|Chỉ lợi nhuận ngắn hạn|Chỉ số nhà mới|Các mục tiêu kinh tế, xã hội và môi trường cần được xem xét cùng nhau.
đọc số liệu|Khi so sánh số liệu hai vùng, cần kiểm tra điều gì?|Đơn vị, thời điểm và cách thống kê|Chỉ màu bảng|Chỉ tên vùng|Bỏ qua nguồn|Các số liệu phải có cơ sở so sánh tương thích.
""",
)
cards(
    "vat_li",
    """
chuyển động|Vật đi đều 120 m trong 20 s có tốc độ bao nhiêu?|6 m/s|140 m/s|100 m/s|2400 m/s|Tốc độ v = s/t = 120/20 = 6 m/s.
lực|Theo định luật II Newton, nếu khối lượng không đổi, gia tốc liên hệ với hợp lực thế nào?|Tỉ lệ thuận với hợp lực|Luôn bằng 0|Tỉ lệ nghịch với hợp lực|Không liên quan hợp lực|Trong hệ quy chiếu quán tính, F = ma nên a = F/m.
điện học|Hiệu điện thế 12 V đặt vào điện trở 6 Ω cho dòng điện bao nhiêu theo định luật Ohm?|2 A|72 A|18 A|0,5 A|I = U/R = 12/6 = 2 A trong điều kiện áp dụng định luật Ohm.
công suất|Công suất được tính bằng công thức nào?|Công thực hiện chia thời gian|Công nhân thời gian|Khối lượng chia thể tích|Độ dài nhân điện trở|P = A/t cho công trung bình thực hiện trong thời gian t.
sóng|Với sóng có tốc độ v và tần số f khác 0, bước sóng bằng gì?|v/f|vf|f/v|v + f|Quan hệ v = λf cho λ = v/f.
nhiệt|Nhiệt độ tuyệt đối được đo bằng đơn vị nào?|Kelvin|Newton|Watt|Ohm|Kelvin là đơn vị SI của nhiệt độ nhiệt động lực học.
""",
)
cards(
    "hoa_hoc",
    """
nguyên tử|Số hiệu nguyên tử Z bằng đại lượng nào?|Số proton trong hạt nhân|Số neutron luôn luôn|Số phân tử|Khối lượng mẫu chất|Số proton xác định nguyên tố và bằng số hiệu nguyên tử.
mol|Một mol các hạt có số hạt xấp xỉ bao nhiêu?|6,022 × 10^23|6,022|100|10^3|Hằng số Avogadro xấp xỉ 6,022 × 10^23 mỗi mol.
phương trình phản ứng|Trong 2H₂ + O₂ → 2H₂O, tỉ lệ số mol H₂ : O₂ là bao nhiêu?|2 : 1|1 : 2|1 : 1|4 : 3|Hệ số cân bằng cho tỉ lệ mol 2 mol H₂ với 1 mol O₂.
acid và base|Theo Brønsted–Lowry, acid là chất có khả năng gì?|Cho proton H⁺|Chỉ nhận electron|Luôn không tan|Chỉ chứa kim loại|Định nghĩa Brønsted–Lowry xem acid là chất cho proton.
polymer|Polymer thường có cấu trúc đặc trưng nào?|Phân tử lớn gồm nhiều đơn vị lặp|Chỉ một nguyên tử|Luôn là kim loại tinh khiết|Không có liên kết hóa học|Đơn vị lặp liên kết tạo nên các đại phân tử polymer.
an toàn phòng thí nghiệm|Khi chưa biết tính chất một hóa chất, cần làm gì?|Xem hướng dẫn và hỏi người phụ trách|Nếm thử|Ngửi trực tiếp sát miệng lọ|Trộn tùy ý|Tuân thủ hướng dẫn và hỏi người phụ trách để đảm bảo an toàn.
""",
)
cards(
    "sinh_hoc",
    """
tế bào|Màng sinh chất có vai trò cơ bản nào?|Ngăn cách và điều hòa trao đổi với môi trường|Chỉ tạo ánh sáng|Là khoáng chất vô cơ|Không có trong tế bào|Màng bao bọc tế bào và tham gia kiểm soát trao đổi chất.
enzyme|Enzyme có vai trò chính nào trong cơ thể?|Xúc tác phản ứng sinh hóa|Thay thế mọi gene|Luôn bị tiêu hao hết sau một phản ứng|Chỉ làm chất màu|Enzyme tăng tốc độ phản ứng phù hợp mà không bị tiêu hao theo tỉ lượng phản ứng.
quang hợp|Quá trình quang hợp ở thực vật chuyển năng lượng ánh sáng chủ yếu thành dạng nào?|Năng lượng hóa học trong chất hữu cơ|Chỉ âm thanh|Chỉ năng lượng từ trường|Không có chuyển hóa|Quang hợp sử dụng ánh sáng để tổng hợp chất hữu cơ chứa năng lượng hóa học.
DNA|Trong DNA mạch kép thông thường, adenine bắt cặp với base nào?|Thymine|Uracil|Guanine|Cytosine|Theo nguyên tắc bổ sung của DNA, A bắt cặp T, G bắt cặp C.
di truyền|Gene có thể được hiểu là gì trong mô hình cơ bản?|Một đoạn DNA mang thông tin tạo sản phẩm chức năng|Một cơ quan lớn|Một loại thức ăn|Toàn bộ môi trường sống|Gene là đơn vị thông tin di truyền có thể mã hóa RNA hoặc sản phẩm protein.
sinh thái|Quan hệ giữa sinh vật và môi trường được nghiên cứu chủ yếu trong lĩnh vực nào?|Sinh thái học|Hình học|Âm học|Khoáng vật học|Sinh thái học nghiên cứu tương tác giữa sinh vật và môi trường.
""",
)
cards(
    "kinh_te_phap_luat",
    """
nguồn lực|Vì nguồn lực có hạn, lựa chọn kinh tế thường phải xét điều gì?|Chi phí cơ hội và mục tiêu|Chỉ màu sản phẩm|Không có đánh đổi|Mọi lựa chọn đều miễn phí|Chọn một phương án thường đồng nghĩa bỏ qua lợi ích của phương án khác.
cung và cầu|Cầu thị trường trong mô hình cơ bản gắn với điều gì?|Mong muốn mua cùng khả năng chi trả|Chỉ mong muốn không điều kiện|Số hàng tồn kho riêng|Chỉ số quảng cáo|Cầu thể hiện lượng người mua sẵn sàng và có khả năng mua theo mức giá.
ngân sách|Lập ngân sách cá nhân cần theo dõi gì?|Thu nhập, chi tiêu và khoản dự phòng|Chỉ số lần mua|Chỉ lời quảng cáo|Không cần hạn mức|Ngân sách giúp cân đối nguồn tiền và nhu cầu.
pháp luật|Đặc điểm nào phù hợp với quy phạm pháp luật?|Quy tắc xử sự chung do Nhà nước ban hành hoặc thừa nhận và bảo đảm thực hiện|Chỉ sở thích của một người|Lời đồn không có cơ sở|Mọi lời mời mua hàng|Quy phạm pháp luật có tính quy tắc chung và được bảo đảm thực hiện theo hệ thống pháp luật.
hợp đồng|Trước khi chấp nhận một hợp đồng, cần làm gì?|Đọc và hiểu quyền, nghĩa vụ và điều kiện|Chỉ nhìn chữ kí cuối|Bỏ mọi điều khoản|Tin rằng không có trách nhiệm|Hiểu điều khoản giúp nhận biết quyền và nghĩa vụ; khi chưa rõ cần hỏi hỗ trợ phù hợp.
tiêu dùng có trách nhiệm|Quyết định mua hàng có căn cứ cần xét gì?|Nhu cầu, thông tin sản phẩm và khả năng tài chính|Chỉ lời thúc giục mua ngay|Chỉ lượt xem|Không cần nguồn gốc|Cân nhắc nhiều yếu tố giúp tránh quyết định thiếu thông tin.
""",
)
cards(
    "am_nhac",
    """
nhịp|Nhịp trong âm nhạc giúp tổ chức yếu tố nào?|Sự luân phiên phách mạnh và phách nhẹ|Chỉ màu sân khấu|Chỉ tên bài hát|Chỉ số người nghe|Nhịp tổ chức các phách theo một cấu trúc lặp.
cao độ|Cao độ thể hiện đặc điểm nào của âm?|Độ cao thấp|Độ dài bản nhạc|Màu nhạc cụ|Số khán giả|Cao độ giúp phân biệt âm cao và âm thấp.
trường độ|Trường độ biểu thị điều gì?|Độ dài ngắn của âm|Chỉ độ cao|Chỉ âm lượng|Tên tác giả|Trường độ là thời gian kéo dài của âm.
hòa tấu|Để hòa tấu tốt, người chơi cần chú ý gì?|Lắng nghe và phối hợp nhịp, sắc thái|Chỉ chơi lớn nhất|Không nhìn chỉ huy|Tự đổi tốc độ tùy ý|Hòa tấu cần sự phối hợp giữa các phần.
lắng nghe|Khi nghe một tác phẩm mới, cách học nào hữu ích?|Nhận biết giai điệu, nhịp và cảm nhận có căn cứ|Chỉ xem số lượt nghe|Không nghe hết câu nhạc|Đánh giá chỉ theo ảnh bìa|Lắng nghe các yếu tố âm nhạc giúp hiểu tác phẩm.
sắc thái|Kí hiệu hoặc chỉ dẫn sắc thái thường giúp người biểu diễn điều gì?|Điều chỉnh độ mạnh nhẹ và cách thể hiện|Thay mọi nốt bằng lời nói|Đổi tên nhạc cụ|Xóa nhịp|Sắc thái góp phần biểu đạt tính chất và cảm xúc của tác phẩm.
""",
)
cards(
    "mi_thuat",
    """
bố cục|Bố cục trong một sản phẩm mĩ thuật là gì?|Cách sắp xếp các yếu tố tạo hình|Chỉ tên tác giả|Chỉ khổ giấy|Chỉ giá màu|Bố cục tổ chức hình, mảng và khoảng trống để thể hiện ý tưởng.
tương phản|Tương phản sáng tối có thể giúp điều gì?|Tạo điểm nhấn và phân biệt mảng|Làm mọi mảng giống nhau|Xóa toàn bộ hình|Chỉ đổi tên màu|Chênh lệch sáng tối giúp nhận biết cấu trúc và điểm nhấn.
đường nét|Đường nét có thể thể hiện điều gì?|Hình dáng và cảm giác chuyển động|Chỉ trọng lượng thật|Chỉ giá vật liệu|Chỉ số người xem|Đường nét vừa mô tả hình vừa tạo cảm giác thị giác.
chất liệu|Lựa chọn chất liệu nên dựa vào gì?|Ý tưởng, tính chất vật liệu và cách sử dụng|Chỉ nhãn giá|Không cần mục tiêu|Chỉ vật liệu mới nhất|Chất liệu cần phù hợp cách thể hiện và yêu cầu sản phẩm.
phân tích tác phẩm|Nhận xét tác phẩm có căn cứ nên dựa vào gì?|Yếu tố tạo hình và bối cảnh phù hợp|Chỉ lời chê ngắn|Chỉ lượt thích|Không cần quan sát|Quan sát hình, màu, bố cục và bối cảnh giúp nhận xét rõ ràng.
quyền tác giả|Khi sử dụng hình ảnh của người khác, nên làm gì?|Kiểm tra quyền sử dụng và ghi nguồn phù hợp|Luôn xóa tên tác giả|Mặc định mọi ảnh đều tự do|Nhận là mình vẽ|Tôn trọng quyền tác giả đòi hỏi xem điều kiện sử dụng và ghi nguồn.
""",
)


# Grade-specific modules replace shared starters where curriculum domains are clear.
cards(
    "vat_li",
    """
chuyển động thẳng|Một vật đi đều với tốc độ 5 m/s trong 8 s. Quãng đường là bao nhiêu?|40 m|13 m|1,6 m|0,625 m|s = vt = 5 × 8 = 40 m.
gia tốc|Vận tốc tăng đều từ 2 m/s lên 10 m/s trong 4 s. Gia tốc bằng bao nhiêu?|2 m/s²|3 m/s²|8 m/s²|40 m/s²|a = (10 − 2)/4 = 2 m/s².
định luật Newton|Hợp lực 6 N tác dụng lên vật khối lượng 2 kg cho gia tốc bao nhiêu?|3 m/s²|12 m/s²|8 m/s²|0,333 m/s²|Theo F = ma, a = 6/2 = 3 m/s².
công cơ học|Lực 10 N cùng hướng chuyển dời 3 m thực hiện công bao nhiêu?|30 J|13 J|7 J|3 J|A = Fs khi lực cùng hướng chuyển dời, nên A = 10 × 3 = 30 J.
động năng|Vật khối lượng 2 kg chuyển động với tốc độ 3 m/s có động năng bao nhiêu?|9 J|6 J|18 J|3 J|Wđ = mv²/2 = 2 × 9/2 = 9 J.
động lượng|Động lượng của vật khối lượng 3 kg chuyển động với vận tốc 2 m/s có độ lớn bao nhiêu?|6 kg·m/s|1,5 kg·m/s|5 kg·m/s|12 kg·m/s|Độ lớn p = mv = 3 × 2 = 6 kg·m/s.
""",
    "10",
)
cards(
    "vat_li",
    """
dao động|Dao động có chu kì 0,2 s có tần số bao nhiêu?|5 Hz|0,2 Hz|2 Hz|20 Hz|f = 1/T = 1/0,2 = 5 Hz.
sóng|Sóng có tốc độ 20 m/s và tần số 5 Hz. Bước sóng bằng bao nhiêu?|4 m|100 m|25 m|0,25 m|λ = v/f = 20/5 = 4 m.
điện trường|Cường độ điện trường đặc trưng cho điều gì tại một điểm?|Tác dụng lực điện trên một đơn vị điện tích thử dương|Chỉ khối lượng điện tích|Chỉ nhiệt độ|Chỉ màu vật|Vectơ E được xác định từ F/q với điện tích thử dương trong điều kiện khảo sát.
điện trở|Điện trở 4 Ω có dòng điện 3 A chạy qua. Hiệu điện thế là bao nhiêu?|12 V|7 V|1,33 V|0,75 V|U = IR = 3 × 4 = 12 V khi áp dụng định luật Ohm.
công suất điện|Thiết bị có U = 12 V, I = 2 A. Công suất điện bằng bao nhiêu?|24 W|6 W|14 W|10 W|P = UI = 12 × 2 = 24 W.
tụ điện|Điện dung C liên hệ với điện tích Q và hiệu điện thế U thế nào?|C = Q/U|C = QU|C = U/Q²|C = Q + U|Điện dung được xác định bởi C = Q/U với U khác 0.
""",
    "11",
)
cards(
    "vat_li",
    """
nhiệt độ|Nhiệt độ 27 °C xấp xỉ bằng bao nhiêu kelvin nếu dùng T = t + 273?|300 K|246 K|27 K|273 K|T ≈ 27 + 273 = 300 K; giá trị chính xác dùng 273,15.
khí lí tưởng|Với một lượng khí lí tưởng ở nhiệt độ không đổi, nếu thể tích tăng gấp đôi thì áp suất thế nào?|Giảm còn một nửa|Tăng gấp đôi|Không đổi|Tăng gấp bốn|Định luật Boyle: pV không đổi ở nhiệt độ và lượng khí không đổi.
nhiệt lượng|Vật nhận 200 J nhiệt và được thực hiện công 50 J. Theo quy ước ΔU = Q + A, nội năng đổi bao nhiêu?|Tăng 250 J|Tăng 150 J|Giảm 250 J|Không đổi|Q = 200 J, A = 50 J vì vật nhận công; ΔU = 250 J.
từ trường|Dây thẳng dài 0,5 m mang dòng 2 A đặt vuông góc từ trường 0,1 T. Lực từ có độ lớn bao nhiêu?|0,1 N|1 N|10 N|0 N|F = BIl sin 90° = 0,1 × 2 × 0,5 = 0,1 N.
cảm ứng điện từ|Suất điện động cảm ứng xuất hiện khi yếu tố nào thay đổi theo thời gian?|Từ thông qua mạch|Tên dây dẫn|Màu lớp sơn|Khối lượng giá đỡ mà từ thông không đổi|Theo định luật Faraday, biến thiên từ thông tạo suất điện động cảm ứng.
phóng xạ|Sau hai chu kì bán rã, số hạt nhân phóng xạ chưa phân rã còn bằng bao nhiêu ban đầu?|1/4|1/2|2|0|Mỗi chu kì còn một nửa; sau hai chu kì còn (1/2)² = 1/4.
""",
    "12",
)
cards(
    "hoa_hoc",
    """
cấu tạo nguyên tử|Nguyên tử trung hòa có 11 proton thì có bao nhiêu electron?|11|22|0|12|Nguyên tử trung hòa có số electron bằng số proton.
đồng vị|Các đồng vị của cùng một nguyên tố có đặc điểm nào?|Cùng số proton, khác số neutron|Khác số proton, cùng số neutron|Khác số proton luôn|Không có hạt nhân|Số proton xác định nguyên tố; số neutron khác nhau tạo các đồng vị.
bảng tuần hoàn|Các nguyên tố trong bảng tuần hoàn hiện đại được sắp xếp chủ yếu theo gì?|Số hiệu nguyên tử tăng dần|Tên chữ cái|Màu chất|Số neutron giảm dần|Số hiệu nguyên tử là số proton và tăng dần theo thứ tự bảng.
liên kết ion|Liên kết ion được tạo chủ yếu do tương tác nào?|Hút tĩnh điện giữa các ion trái dấu|Hút giữa hai điện tích cùng dấu|Chỉ dùng chung neutron|Không có tương tác|Ion dương và ion âm hút nhau bằng lực tĩnh điện.
oxi hóa khử|Trong một quá trình oxi hóa, chất tham gia theo nghĩa electron làm gì?|Nhường electron|Nhận electron|Luôn nhận proton|Chỉ đổi trạng thái|Oxi hóa là nhường electron; khử là nhận electron.
tốc độ phản ứng|Với phản ứng có chất khí, tăng áp suất bằng cách giảm thể tích ở nhiệt độ không đổi thường làm gì với nồng độ khí?|Tăng nồng độ khí|Luôn giảm về 0|Không thay đổi số hạt trên đơn vị thể tích|Biến khí thành kim loại|Cùng số mol trong thể tích nhỏ hơn cho nồng độ lớn hơn; tác động lên tốc độ còn tùy phản ứng.
""",
    "10",
)
cards(
    "hoa_hoc",
    """
cân bằng hóa học|Ở trạng thái cân bằng động, tốc độ phản ứng thuận và nghịch như thế nào?|Bằng nhau|Đều bằng 0 bắt buộc|Thuận luôn lớn hơn|Nghịch luôn lớn hơn|Các phản ứng vẫn diễn ra, nhưng tốc độ thuận và nghịch bằng nhau.
acid và base|Theo Brønsted–Lowry, base có khả năng gì?|Nhận proton H⁺|Chỉ cho proton|Luôn chứa kim loại|Không bao giờ phản ứng|Base là chất nhận proton theo định nghĩa này.
pH|Dung dịch có pH = 3 so với dung dịch pH = 5 có nồng độ H⁺ lớn gấp bao nhiêu?|100 lần|2 lần|10 lần|1/100 lần|pH = −log[H⁺]; chênh 2 đơn vị tương ứng tỉ số 10².
hợp chất hữu cơ|Phần lớn hợp chất hữu cơ có đặc điểm nào?|Chứa carbon|Không có nguyên tử|Chỉ chứa kim loại|Luôn là khí|Hợp chất hữu cơ thuộc hóa học carbon, với một số hợp chất carbon thuộc nhóm vô cơ.
alkane|Công thức phân tử chung của alkane mạch hở là gì?|CₙH₂ₙ₊₂|CₙH₂ₙ|CₙH₂ₙ₋₂|CₙHₙ|Alkane mạch hở là hydrocarbon no, có công thức CₙH₂ₙ₊₂ với n ít nhất 1.
alcohol|Nhóm chức đặc trưng của alcohol là gì?|Nhóm −OH gắn với carbon no|Nhóm −COOH|Chỉ liên kết ba|Chỉ ion Na⁺|Alcohol có nhóm hydroxyl gắn với nguyên tử carbon no.
""",
    "11",
)
cards(
    "hoa_hoc",
    """
ester|Ester có thể được tạo trong phản ứng giữa các chất nào ở mô hình cơ bản?|Carboxylic acid và alcohol|Hai kim loại|Hai khí hiếm|Muối ăn và cát|Phản ứng ester hóa giữa carboxylic acid và alcohol tạo ester và nước trong điều kiện phù hợp.
carbohydrate|Công thức phân tử của glucose là gì?|C₆H₁₂O₆|CO₂|CH₄|NaCl|Glucose là monosaccharide có công thức C₆H₁₂O₆.
protein|Đơn vị cấu tạo của protein là gì?|Các amino acid|Chỉ phân tử nước|Chỉ ion kim loại|Các hạt cát|Protein gồm các amino acid nối nhau qua liên kết peptide.
polymer|Phản ứng trùng hợp ethylene tạo polymer nào?|Polyethylene|Tinh bột|Protein|Cellulose|Các phân tử ethylene liên kết tạo polyethylene với mắt xích −CH₂−CH₂−.
điện hóa|Trong một pin điện hóa đang phát điện, tại anode diễn ra quá trình gì?|Oxi hóa|Chỉ khử|Không có phản ứng|Luôn tạo nước|Anode là nơi oxi hóa; cathode là nơi khử trong cả pin và điện phân.
kim loại|Tính dẫn điện của kim loại liên quan chủ yếu đến yếu tố nào?|Electron có thể chuyển động trong mạng kim loại|Chỉ màu bề mặt|Không có hạt mang điện|Chỉ neutron chuyển động|Electron trong cấu trúc kim loại có thể tham gia chuyển dời có hướng tạo dòng điện.
""",
    "12",
)
cards(
    "sinh_hoc",
    """
tế bào nhân sơ|Tế bào nhân sơ khác tế bào nhân thực cơ bản ở điểm nào?|Không có nhân được bao bởi màng nhân|Không có màng sinh chất|Không có vật chất di truyền|Luôn lớn hơn mọi tế bào nhân thực|Vật chất di truyền của tế bào nhân sơ không nằm trong nhân có màng bao.
màng sinh chất|Thành phần cấu trúc chủ yếu của màng sinh chất là gì?|Lớp kép phospholipid và protein|Chỉ tinh bột|Chỉ DNA|Chỉ muối vô cơ|Mô hình khảm động mô tả lớp kép phospholipid với các protein.
thẩm thấu|Thẩm thấu là sự di chuyển chủ yếu của chất nào qua màng bán thấm?|Nước|Hạt cát|Mọi protein|Mọi tế bào|Nước di chuyển qua màng có tính thấm chọn lọc theo chênh lệch thế nước.
enzyme|Enzyme thường tác động lên phản ứng thế nào?|Làm giảm năng lượng hoạt hóa|Làm tăng năng lượng hoạt hóa bắt buộc|Biến phản ứng thành không cần chất phản ứng|Làm mất mọi quy luật|Enzyme xúc tác bằng cách giảm năng lượng hoạt hóa của phản ứng phù hợp.
ATP|ATP có vai trò nổi bật nào trong tế bào?|Truyền năng lượng cho các hoạt động tế bào|Chỉ lưu thông tin di truyền|Chỉ tạo vách tế bào|Là nguyên tố hóa học|ATP là phân tử tham gia tích lũy và chuyển năng lượng.
nguyên phân|Trong mô hình cơ bản, một tế bào nguyên phân một lần tạo bao nhiêu tế bào con?|2|1|3|8|Một lần nguyên phân và phân chia tế bào chất thường tạo hai tế bào con.
""",
    "10",
)
cards(
    "sinh_hoc",
    """
trao đổi nước|Ở thực vật, phần lớn nước thoát ra chủ yếu qua cấu trúc nào của lá?|Khí khổng|Rễ củ|Hạt phấn|Quả chín|Khí khổng là con đường chủ yếu của thoát hơi nước ở nhiều loài thực vật.
quang hợp|Sắc tố nào có vai trò quan trọng trong hấp thụ ánh sáng cho quang hợp?|Chlorophyll|Hemoglobin|Keratin|Insulin|Chlorophyll trong bộ máy quang hợp hấp thụ năng lượng ánh sáng.
hô hấp tế bào|Hô hấp tế bào góp phần chủ yếu vào việc nào?|Giải phóng năng lượng từ chất hữu cơ để tạo ATP|Chỉ hấp thụ ánh sáng|Luôn tổng hợp tinh bột từ CO₂|Không tạo chuyển hóa năng lượng|Hô hấp tế bào khai thác năng lượng hóa học và tạo ATP.
tuần hoàn|Vai trò cơ bản của hệ tuần hoàn là gì?|Vận chuyển các chất trong cơ thể|Chỉ tạo hình dáng|Chỉ hấp thụ ánh sáng|Không trao đổi với mô|Tuần hoàn vận chuyển oxygen, chất dinh dưỡng và các chất khác.
cảm ứng|Cảm ứng ở sinh vật là khả năng gì?|Tiếp nhận và phản ứng với kích thích|Luôn giữ nguyên mọi hoạt động|Chỉ tạo giao tử|Chỉ tăng khối lượng|Cảm ứng giúp sinh vật đáp ứng với thay đổi của môi trường.
sinh sản hữu tính|Sinh sản hữu tính có đặc điểm cơ bản nào?|Có sự kết hợp giao tử tạo hợp tử|Chỉ phân đôi|Không có vật chất di truyền|Luôn chỉ cần một tế bào sinh dưỡng|Sự kết hợp giao tử là dấu hiệu cơ bản của sinh sản hữu tính.
""",
    "11",
)
cards(
    "sinh_hoc",
    """
DNA|Trong DNA mạch kép, nếu A chiếm 20% tổng số nucleotide thì T chiếm bao nhiêu?|20%|30%|40%|60%|Theo nguyên tắc bổ sung, số A bằng số T trong DNA mạch kép.
phiên mã|Phiên mã tạo sản phẩm cơ bản nào từ khuôn DNA?|RNA|Lipid|Tinh bột|Khoáng chất|Phiên mã dùng thông tin DNA để tổng hợp RNA.
dịch mã|Trong dịch mã, trình tự nucleotide trên mRNA quy định chủ yếu điều gì?|Trình tự amino acid của chuỗi polypeptide|Chỉ màu tế bào|Chỉ nhiệt độ|Số hạt cát|Các bộ ba mã hóa được đọc để lắp các amino acid thành chuỗi.
phân li|Trong phép lai Aa × Aa, theo mô hình Mendel đơn giản, tỉ lệ kiểu gene aa là bao nhiêu?|1/4|1/2|3/4|1|Mỗi bên tạo giao tử A và a với xác suất 1/2; aa có xác suất 1/2 × 1/2 = 1/4.
chọn lọc tự nhiên|Chọn lọc tự nhiên tác động trực tiếp chủ yếu lên yếu tố nào?|Kiểu hình của cá thể trong môi trường|Chỉ tên loài|Mọi cá thể luôn như nhau|Chỉ màu trang sách|Các khác biệt kiểu hình ảnh hưởng khả năng sống và sinh sản trong môi trường.
sinh thái|Trong chuỗi cỏ → thỏ → cáo, sinh vật sản xuất là gì?|Cỏ|Thỏ|Cáo|Cả thỏ và cáo|Cỏ tự tổng hợp chất hữu cơ nên là sinh vật sản xuất trong chuỗi.
""",
    "12",
)


def build():
    catalog = json.loads((ROOT / "data/seeds/catalog.json").read_text(encoding="utf-8"))
    questions, exams, notes, coverage = [], [], [], []
    for g in catalog["grades"]:
        grade = g["id"]
        for subject in g["subjects"]:
            sid = subject["id"]
            if sid == "toan":
                continue
            band = "primary" if grade <= 5 else "lower" if grade <= 9 else "upper"
            entries = BANK.get(
                (sid, str(grade)), BANK.get((sid, band), BANK.get((sid, "all")))
            )
            if entries is None:
                raise ValueError(f"Missing bank: {grade}/{sid}")
            ids = []
            for index, entry in enumerate(entries):
                qid = f"kntt_core_{grade}_{sid}_{index + 1:02d}"
                ids.append(qid)
                # Rotate answer placement; never teach that A is always correct.
                rotation = (grade + index) % 4
                options = entry["choices"][rotation:] + entry["choices"][:rotation]
                answer = "ABCD"[options.index(entry["choices"][0])]
                questions.append(
                    dict(
                        id=qid,
                        grade=grade,
                        subject=sid,
                        topic=entry["topic"],
                        textbook="ket_noi_tri_thuc",
                        type="single_choice",
                        difficulty="easy",
                        question=f"Ôn {subject['name']} lớp {grade}: {entry['question']}",
                        options=[dict(id=k, text=v) for k, v in zip("ABCD", options)],
                        correct_answer=[answer],
                        max_score=1,
                        explanation=entry["explanation"],
                        source_type="original",
                        license="original_content",
                        rights_evidence="Tự biên soạn bộ khởi đầu ôn kiến thức nền. Có nội dung dùng lại giữa các lớp; chưa phải phủ hết yêu cầu riêng của từng lớp hoặc từng ấn bản KNTT.",
                    )
                )
            exams.append(
                dict(
                    id=f"kntt_core_{grade}_{sid}",
                    grade=grade,
                    subject=sid,
                    topic="kien_thuc_nen",
                    textbook="ket_noi_tri_thuc",
                    title=f"{subject['name']} {grade} · Ôn kiến thức nền · KNTT",
                    duration_minutes=15,
                    question_ids=ids,
                )
            )
            notes.append(
                dict(
                    id=f"kntt_core_note_{grade}_{sid}",
                    grade=grade,
                    subject=sid,
                    title=f"{subject['name']} {grade}: bộ ôn kiến thức nền",
                    topic="Kiến thức nền",
                    textbook="ket_noi_tri_thuc",
                    kind="study_notes",
                    semester=None,
                    summary="Bộ khởi đầu tự biên soạn, gồm 6 điểm kiến thức và ví dụ. Một số điểm nền tảng được dùng lại giữa các lớp.",
                    sections=[
                        dict(
                            heading=entry["topic"].capitalize(),
                            text=entry["question"]
                            + "\nTrả lời: "
                            + entry["choices"][0]
                            + ".\n"
                            + entry["explanation"],
                        )
                        for entry in entries
                    ]
                    + [
                        dict(
                            heading="Phạm vi sử dụng",
                            text="Đây là bộ ôn nền tảng, chưa đối chiếu từng bài SGK Kết nối tri thức hiện hành; không đại diện đầy đủ cho chương trình riêng của lớp. Một số nội dung được dùng lại giữa các lớp.",
                        )
                    ],
                    author="Kho Học 1–12",
                    source_name="Bộ ôn kiến thức nền tự biên soạn",
                    source_type="original",
                    license="original_content",
                    rights_evidence="Soạn riêng cho bản thử, không sao chép SGK, chưa được thẩm định chuyên môn độc lập.",
                    distribution_allowed=True,
                    download_allowed=False,
                )
            )
            coverage.append(
                dict(
                    grade=grade,
                    subject=sid,
                    question_count=len(ids),
                    depth="starter_foundations",
                    alignment_status="pending_grade_and_edition_review",
                    shared_foundations=(sid, str(grade)) not in BANK,
                )
            )

    def save(path, value):
        (ROOT / path).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    save("data/seeds/subject_questions.json", dict(questions=questions))
    save("data/seeds/subject_exams.json", exams)
    save(
        "data/seeds/subject_coverage.json",
        dict(status="starter_not_complete_curriculum", coverage=coverage),
    )
    base = json.loads(
        (ROOT / "data/library/documents.json").read_text(encoding="utf-8")
    )
    base["documents"] = [
        d for d in base["documents"] if not d["id"].startswith("kntt_core_note_")
    ] + notes
    save("data/library/documents.json", base)
    print(
        f"Generated {len(questions)} questions / {len(exams)} grade-subject starters / {len(notes)} notes"
    )


if __name__ == "__main__":
    build()
