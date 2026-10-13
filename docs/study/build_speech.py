"""[NHOM8] Speech script for the single presenter (Tâm): natural spoken text for every slide of
slides/Slides_Nhom8_LinCIR.pptx, with transitions, timing and an appendix of Kaggle details.

  python docs/study/build_speech.py   ->  slides/KichBan_ThuyetTrinh_Tam.docx (PDF: docs/study/speech_to_pdf.sh)
"""
import re
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plain_language import SYMBOLS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "slides" / "Slides_Nhom8_LinCIR.pptx"
OUT = ROOT / "slides" / "KichBan_ThuyetTrinh_Tam.docx"
ACCENT = RGBColor(0x14, 0x4F, 0xB0)
MUTED = RGBColor(0x5B, 0x6B, 0x82)
PACE = 160  # spoken Vietnamese syllables per minute (calm pace)

# per slide: (spoken paragraphs, transition sentence to the next slide)
SPEECH = {
    1: (["Em chào cô và các bạn. Em là Đào Văn Tâm, đại diện Nhóm 8, lớp M25CQHT02-B. Đề tài của nhóm là tái hiện và cải tiến "
         "phương pháp LinCIR, công bố tại hội nghị CVPR 2024, với tên đầy đủ: huấn luyện hiệu quả chỉ bằng văn bản cho bài toán "
         "truy xuất ảnh kết hợp zero-shot. Em xin trình bày trong khoảng mười lăm phút."],
        "Trước hết, em xin giới thiệu cách nhóm chia công việc."),
    2: (["Nhóm có năm thành viên, mỗi người phụ trách một phần. Em phụ trách chuyển đổi mã nguồn sang môi trường mới, kiểm chứng "
         "mã chạy đúng như bản gốc và vận hành toàn bộ thực nghiệm trên Kaggle. Bạn Trung đề xuất và cài đặt cải tiến A, đồng thời "
         "phân tích đường học. Bạn Tùng tái hiện kết quả của bài báo và đối chiếu bài báo với mã nguồn. Bạn Dũng thiết kế cách "
         "đánh giá, kiểm định thống kê, cài đặt cải tiến B và phân tích modality gap. Bạn Mekdala Nounou làm phần tổng quan lý "
         "thuyết, phân tích định tính và thiết kế slide.",
         "Em sẽ trình bày toàn bộ. Ở phần hỏi đáp, bạn phụ trách phần nào sẽ trả lời phần đó; cột bên phải là các slide mỗi bạn hỗ trợ."],
        "Bây giờ em đi vào bài toán."),
    3: (["Bài toán của bài báo là truy xuất ảnh kết hợp, viết tắt là CIR. Truy vấn gồm hai phần: một ảnh tham chiếu và một câu mô "
         "tả thay đổi. Trong ví dụ trên slide, ảnh tham chiếu là một chiếc váy họa tiết xanh, còn câu là “is shiny and silver with "
         "shorter sleeves”, tức là bóng hơn, màu bạc và tay ngắn hơn. Hệ thống phải tìm trong kho ảnh chiếc váy giữ kiểu dáng của "
         "ảnh tham chiếu nhưng áp dụng đúng các thay đổi, và trả về một danh sách ảnh được xếp hạng. Điểm khó là câu chỉ mô tả "
         "phần thay đổi, không mô tả toàn bộ ảnh đích, nên không thể chỉ tìm bằng chữ hoặc chỉ tìm bằng ảnh.",
         "Cách học có giám sát cần các bộ ba gồm ảnh tham chiếu, câu và ảnh đích do người gán nhãn. Các bộ này đắt và ít: FashionIQ "
         "chỉ có khoảng 46,6 nghìn bộ ba. Vì vậy hướng zero-shot không dùng bộ ba nào khi huấn luyện. Bài báo LinCIR giải bài toán "
         "theo hướng này và chỉ dùng văn bản để huấn luyện.",
         "Câu hỏi nhóm đặt ra là: nếu sửa một trong hai thành phần cốt lõi của LinCIR, là hàm mất mát hoặc nhiễu, thì kết quả truy "
         "xuất có tốt hơn không."],
        "Để trả lời “tốt hơn” một cách định lượng, trước hết cần thống nhất cách đo."),
    4: (["CIR vẫn là một bài toán truy xuất có xếp hạng như chương I của môn học: có nhu cầu thông tin, có truy vấn và hệ thống trả "
         "về danh sách xếp hạng. Điểm khác là thay vì khớp từ chính xác như mô hình Boolean hay chỉ mục ngược, ở đây ảnh và truy "
         "vấn đều được mã hóa thành vector CLIP, và ảnh được xếp hạng theo độ tương đồng cosine với vector truy vấn.",
         "Nhóm dùng hai độ đo. Thứ nhất là Recall tại K: số truy vấn có ảnh đích nằm trong K kết quả đầu, chia cho tổng số truy "
         "vấn. Độ đo này dùng cho FashionIQ, vì mỗi truy vấn chỉ có một ảnh đúng. Ví dụ R@10 bằng 26 nghĩa là 26% số truy vấn có "
         "ảnh đích trong mười kết quả đầu. Thứ hai là mAP tại K, dùng cho CIRCO, vì mỗi truy vấn có nhiều ảnh đúng. AP tại K lấy "
         "Precision tại các vị trí có ảnh đúng, cộng lại rồi chia cho số ảnh đúng tối đa có thể nằm trong K kết quả; mAP là trung "
         "bình trên các truy vấn. Ảnh đúng xếp càng cao thì điểm càng cao.",
         "Nhóm đánh giá trên FashionIQ val và CIRCO val, và mọi so sánh đều được kiểm định thống kê theo từng truy vấn bằng "
         "bootstrap ghép cặp và kiểm định Wilcoxon."],
        "Tiếp theo là cách các phương pháp zero-shot biến một ảnh thành thứ mà bộ mã hóa văn bản hiểu được."),
    5: (["Ý tưởng chung là biến ảnh tham chiếu thành một từ giả. Ảnh đi qua bộ mã hóa ảnh của CLIP, rồi qua một mạng chiếu nhỏ ký "
         "hiệu là phi; đầu ra là một token giả, trên slide là ký hiệu đô-la trong ngoặc vuông. Token này được ghép vào câu “a photo "
         "of token giả that”, nối với câu mô tả thay đổi. Bộ mã hóa văn bản biến cả câu thành vector truy vấn, rồi hệ thống xếp hạng "
         "ảnh trong kho theo cosine. Toàn bộ CLIP được giữ nguyên; thứ duy nhất phải học là mạng chiếu phi."],
        "Vấn đề là học phi như thế nào, và đây chính là chỗ LinCIR khác các phương pháp trước."),
    6: (["Bài báo LinCIR của Gu và các cộng sự tại NAVER, công bố ở CVPR 2024. Vấn đề họ chỉ ra là các phương pháp trước như "
         "Pic2Word và SEARLE học phi bằng ảnh, nên phải chạy bộ mã hóa ảnh ở mỗi bước huấn luyện: ảnh của bộ CC3M chiếm khoảng "
         "430 GB, trong khi chú thích chỉ 125 MB. Đồng thời chúng chỉ học với một câu mẫu cố định “a photo of token giả”, nên kém "
         "với các câu mô tả đa dạng.",
         "Ý tưởng của LinCIR là học phi chỉ từ văn bản bằng cơ chế Self-Masking Projection, và thêm nhiễu khi huấn luyện để phi "
         "dùng được cho vector ảnh. Kết quả công bố: tốt nhất trên bốn bộ đánh giá zero-shot, huấn luyện nhanh hơn Pic2Word 6 lần "
         "và SEARLE 8,4 lần với ViT-L, và trên FashionIQ còn vượt cả một phương pháp có giám sát. Mã nguồn được công khai, đây là "
         "cơ sở để nhóm dựng lại và cải tiến."],
        "Em trình bày lần lượt hai thành phần chính, bắt đầu từ Self-Masking Projection."),
    7: (["Sơ đồ này là phương pháp gốc. Lấy một câu, ví dụ “gray cat sleeps on a pillow”. Bộ mã hóa văn bản, được giữ nguyên, cho "
         "vector z c của câu. Vector này đi qua phi để thành một token giả. Song song, các từ khóa là tính từ và danh từ, được trích "
         "bằng thư viện spaCy, bị che bằng ký hiệu đô-la, nên câu trở thành “đô-la sleeps on đô-la”. Sau đó thay ký hiệu đô-la bằng "
         "token mà phi vừa tạo và mã hóa lại câu này, được vector z c mũ.",
         "Hàm mất mát là MSE giữa z c và z c mũ: câu đã che phải mang cùng nghĩa với câu gốc. Muốn vậy, token giả phải gói nội "
         "dung chính của câu vào một từ. Trên sơ đồ, ô màu xanh là phần đóng băng, ô màu cam là phần được huấn luyện."],
        "Nhưng khi dùng thật, phi lại nhận vector ảnh chứ không phải vector câu. Đó là lý do có thành phần thứ hai."),
    8: (["Trong CLIP, vector ảnh và vector văn bản nằm ở hai vùng tách biệt, hiện tượng này gọi là modality gap. Nhóm đo trên 5.000 "
         "cặp ảnh – chú thích của COCO: tâm vùng ảnh và tâm vùng văn bản cách nhau 0,82, và một ảnh với chính chú thích của nó chỉ "
         "có cosine trung bình 0,26.",
         "Phi học hoàn toàn trên văn bản nhưng khi suy luận lại nhận vector ảnh. Để phi chịu được độ lệch này, LinCIR cộng nhiễu "
         "vào z c khi huấn luyện: n bằng u nhân ép-xi-lon, trong đó u lấy ngẫu nhiên từ 0 đến 1, còn ép-xi-lon theo phân phối "
         "chuẩn, nên độ lớn của nhiễu đa dạng."],
        "Như vậy LinCIR có hai thành phần là hàm mất mát và nhiễu. Hai cải tiến của nhóm lần lượt nhắm vào từng thành phần."),
    9: (["Cải tiến A sửa hàm mất mát. MSE chỉ kéo câu đã che về gần câu gốc, nhưng không phạt trường hợp câu đã che cũng gần các "
         "câu khác, trong khi việc đánh giá lại là bài toán xếp hạng: điều quan trọng là đúng hơn các ứng viên khác. Nhóm thêm hàm "
         "mất mát đối sánh InfoNCE: L bằng L SMP cộng 0,5 nhân InfoNCE, với 511 câu khác trong cùng batch làm mẫu âm và nhiệt độ "
         "tô bằng 0,07. Chi phí chỉ tăng khoảng 2% thời gian mỗi bước, 1,474 so với 1,448 giây.",
         "Giả thuyết H1: thêm InfoNCE làm tăng R@K và mAP@K so với baseline. Em sẽ quay lại giả thuyết này ở phần kết quả."],
        "Cải tiến B nhắm vào thành phần còn lại là nhiễu."),
    10: (["Nhiễu của LinCIR đều theo mọi hướng. Nó giúp phi quen với đầu vào bị lệch, nhưng không lệch về phía vùng ảnh, là nơi phi "
          "thực sự nhận đầu vào khi suy luận. Cải tiến B thêm một thành phần có hướng: n bằng 0,5 nhân đen-ta cộng u nhân "
          "ép-xi-lon, trong đó đen-ta là vector từ tâm vùng văn bản tới tâm vùng ảnh. Đen-ta được tính một lần trên 5.000 cặp ảnh – "
          "chú thích của COCO val2017, có độ lớn 13,87; tập này khác các tập đánh giá nên không rò rỉ dữ liệu.",
          "Giả thuyết H2: phi sẽ cho kết quả nhất quán hơn giữa ảnh và văn bản, từ đó R@K và mAP@K tăng. Vì A và B sửa hai thành "
          "phần khác nhau, nhóm đặt thêm giả thuyết H3: kết hợp A và B có thể cộng hưởng."],
         "Để kiểm chứng ba giả thuyết, nhóm phải dựng lại mã và chạy thực nghiệm."),
    11: (["Mã nguồn gốc viết cho thư viện transformers phiên bản 4.34 và dùng một hàm nội bộ đã bị bỏ ở phiên bản hiện tại, nên "
          "không chạy được. Em viết lại phần mã hóa văn bản từ các mô-đun con của CLIP, thay tokenizer và sửa bốn lỗi trong mã gốc. "
          "Để chắc phần viết lại đúng, em so trực tiếp vector đầu ra với CLIP gốc trên cùng câu: sai lệch bằng 0,00 trên cả "
          "ViT-B/32 và ViT-L/14.",
          "Thực nghiệm chạy trên Kaggle với 2 GPU NVIDIA T4, mỗi GPU 16 GB, và 4 nhân CPU. Kaggle giới hạn 30 giờ GPU mỗi tuần và "
          "tối đa 12 giờ mỗi phiên. Cấu hình huấn luyện giống mã chính thức: CLIP ViT-L/14, batch 512, độ chính xác hỗn hợp fp16, "
          "AdamW với tốc độ học 10 mũ trừ 4 và weight decay 0,01; mỗi run dùng tối đa 11,4 GB bộ nhớ trên một GPU. Bài báo huấn "
          "luyện 20.000 bước; trên T4 việc này mất khoảng 13 giờ mỗi run, vượt giới hạn một phiên, nên nhóm giảm xuống 5.000 bước, "
          "như nhau cho mọi biến thể, và dùng checkpoint ở bước cuối.",
          "Tổng cộng có 12 run: bốn biến thể baseline, A, B, A+B, mỗi biến thể ba seed là 12345, 2024 và 7. Mỗi GPU chạy một run "
          "độc lập để giữ đủ batch 512, nên hai run chạy song song. Phiên huấn luyện đầu tiên chỉ xong hai run, mỗi run 6,2 giờ, "
          "vì CPU bị nghẽn ở bước trích từ khóa bằng spaCy. Em chuyển spaCy sang xử lý theo lô và bỏ hai thành phần không dùng; "
          "nạp dữ liệu nhanh gấp 3,1 lần mà kết quả che từ khóa giống hệt bản cũ. Sau đó mỗi run chỉ còn khoảng 2 giờ, tương "
          "đương 1,45 giây mỗi bước. Theo bộ đếm hạn mức của Kaggle, toàn bộ dự án, gồm chạy thử, chuẩn bị dữ liệu, ba phiên "
          "huấn luyện và phiên đánh giá, dùng 22 giờ 52 phút trong hạn mức 30 giờ."],
         "Trước khi so sánh các cải tiến, cần chắc quy trình đánh giá cho số liệu đúng."),
    12: (["Nhóm đánh giá lại checkpoint chính thức của tác giả bằng mã đã chuyển đổi. Trên FashionIQ, R@10 trung bình là 26,35, so "
          "với 26,28 trong bài báo; R@50 là 46,12 so với 46,49. Mức lệch lớn nhất ở từng nhóm sản phẩm là 0,77 điểm, và khi chạy "
          "lại, thứ hạng của từng truy vấn giống hệt. Như vậy quy trình đánh giá đáng tin cậy.",
          "Khi đọc mã, nhóm cũng thấy ba điểm khác với bài báo: mạng phi trong mã không có LayerNorm như bài báo mô tả; mã nạp "
          "thêm một bộ prompt Midjourney mà bài báo không nhắc tới; và cụm từ khóa bị che gồm cả mạo từ như “a”, “the”. Nhóm làm "
          "theo mã, vì chính mã đã tạo ra checkpoint và số liệu công bố."],
         "Bây giờ là kết quả chính."),
    13: (["Bảng này là trung bình và độ lệch chuẩn qua ba seed. Nhóm so với baseline do nhóm tự huấn luyện cùng cấu hình, không so "
          "với số của bài báo. Cải tiến B cao nhất ở cả ba cột: FashionIQ R@10 là 26,50, R@50 là 46,79 và CIRCO mAP@5 là 10,94. So "
          "với baseline, B tăng 0,60 điểm R@10 với p bằng 0,006, và 1,27 điểm R@50 với p nhỏ hơn 0,001; mức tăng 0,60 điểm R@10 "
          "tương đương khoảng 6 truy vấn đúng thêm trên mỗi 1.000 truy vấn. B chỉ huấn luyện 5.000 bước nhưng vượt cả checkpoint "
          "chính thức 20.000 bước ở hàng cuối.",
          "Ngược lại, A giảm mạnh trên CIRCO: mAP@5 giảm 2,45 điểm, khoảng tin cậy 95% từ âm 3,95 đến âm 1,07, nằm hoàn toàn dưới "
          "0. A cộng B cũng giảm tương tự. Độ lệch chuẩn giữa các seed đều nhỏ, không quá 0,5 điểm, nên các khác biệt này không "
          "đến từ ngẫu nhiên khởi tạo."],
         "Câu hỏi tiếp theo là vì sao B tốt hơn, còn A lại kém hơn."),
    14: (["Nhóm đo một đại lượng trực tiếp: với cùng một cặp ảnh – chú thích, đầu ra của phi khi nhận ảnh và khi nhận văn bản giống "
          "nhau đến mức nào, tính bằng cosine. Ở biểu đồ trái, B cao nhất với 0,84, checkpoint chính thức 0,81, baseline 0,80, A "
          "cộng B 0,69 và A thấp nhất với 0,64. Thứ tự này trùng với thứ tự CIRCO mAP@5.",
          "Cách giải thích của nhóm: InfoNCE buộc token giả mang những đặc trưng giúp phân biệt các câu văn bản với nhau; các đặc "
          "trưng này gắn với miền văn bản và không chuyển được sang vector ảnh. Còn B đưa đầu vào lúc huấn luyện về gần vùng ảnh, "
          "nên phi xử lý ảnh nhất quán hơn. Biểu đồ phải là đường học theo số bước: A thấp hơn baseline ở mọi mốc từ 1.000 đến "
          "5.000 bước, nên kết luận về A không phụ thuộc vào điểm dừng."],
         "Em xin tổng kết lại."),
    15: (["Hình bên trái là một truy vấn thật trong FashionIQ. Hàng dưới là B, xếp đúng ảnh đích ở hạng 1; hàng trên là baseline, chủ "
          "yếu trả về váy ngắn màu tối. Cũng thấy nhiều ảnh trong top 5 đúng phần lớn yêu cầu nhưng không phải ảnh được gán nhãn; "
          "đây là hiện tượng âm tính giả, làm R@K đánh giá thấp chất lượng thật của hệ thống.",
          "Kết luận: H2 được ủng hộ, B tốt hơn LinCIR có ý nghĩa thống kê. H1 bị bác bỏ, A làm CIRCO mAP@5 giảm 2,45 điểm. H3 bị "
          "bác bỏ, A cộng B kém baseline trên CIRCO. Điều nhóm rút ra là chất lượng truy xuất của LinCIR phụ thuộc chủ yếu vào "
          "việc phi xử lý ảnh nhất quán với văn bản, hơn là khả năng phân biệt giữa các câu.",
          "Đóng góp của nhóm gồm dựng lại mã, tái hiện, hai cải tiến, đánh giá có kiểm định và phân tích cơ chế. Hạn chế là mới "
          "huấn luyện 5.000 bước, chưa quét hệ số lam-đa và an-pha, chưa đánh giá trên CIRR và tập test của CIRCO. Hướng tiếp theo "
          "là chạy đủ 20.000 bước, quét các hệ số và thử hướng C: chọn từ khóa cần che theo IDF."],
         ""),
    16: (["Phần trình bày của nhóm em đến đây là hết. Em cảm ơn cô và các bạn đã lắng nghe; nhóm em rất mong nhận được câu hỏi và "
          "góp ý."],
         ""),
}
# term -> (cách đọc, viết tắt của, nghĩa). Matched as a whole word; annotated at its first occurrence in the speech.
TERMS = {
    "LinCIR": ("lin-kơ, tác giả đọc như linker", "Language-only training for Composed Image Retrieval",
               "phương pháp của bài báo: huấn luyện CIR chỉ bằng văn bản"),
    "CVPR": ("xi-vi-pi-a", "Conference on Computer Vision and Pattern Recognition", "hội nghị hàng đầu về thị giác máy tính"),
    "zero-shot": ("di-rô sót", "", "không dùng dữ liệu có nhãn của chính bài toán khi huấn luyện"),
    "CIR": ("xi-ai-a", "Composed Image Retrieval", "truy xuất ảnh kết hợp: truy vấn gồm ảnh tham chiếu và câu mô tả thay đổi"),
    "FashionIQ": ("pha-sần ai-kiu", "", "bộ dữ liệu CIR về thời trang (váy, áo sơ mi, áo phông), mỗi truy vấn có 1 ảnh đúng"),
    "CIRCO": ("xơ-cô", "Composed Image Retrieval on Common Objects in context", "bộ dữ liệu CIR trên ảnh đời thực COCO, mỗi truy vấn có nhiều ảnh đúng"),
    "CIRR": ("xi-ai-a-a", "Composed Image Retrieval on Real-life images", "bộ dữ liệu CIR ảnh đời thực; nhóm chưa dùng được vì chưa được cấp quyền ảnh"),
    "CLIP": ("clíp", "Contrastive Language–Image Pre-training", "mô hình của OpenAI đưa ảnh và văn bản vào cùng một không gian vector"),
    "Recall": ("ri-con", "", "độ phủ: tỉ lệ kết quả đúng được tìm thấy"),
    "R@10": ("Recall tại 10", "Recall at 10", "tỉ lệ truy vấn có ảnh đích trong 10 kết quả đầu"),
    "R@50": ("Recall tại 50", "Recall at 50", "tỉ lệ truy vấn có ảnh đích trong 50 kết quả đầu"),
    "R@K": ("Recall tại K", "Recall at K", "tỉ lệ truy vấn có ảnh đích trong K kết quả đầu"),
    "mAP": ("em-ây-pi", "mean Average Precision", "trung bình của AP trên các truy vấn"),
    "mAP@5": ("em-ây-pi tại 5", "mean Average Precision at 5", "mAP chỉ xét 5 kết quả đầu"),
    "mAP@K": ("em-ây-pi tại K", "mean Average Precision at K", "mAP chỉ xét K kết quả đầu"),
    "AP": ("ây-pi", "Average Precision", "trung bình Precision tại các vị trí có kết quả đúng"),
    "Precision": ("pri-xi-giần", "", "độ chính xác: tỉ lệ kết quả trả về là đúng"),
    "Boolean": ("bu-li-ần", "", "mô hình truy xuất khớp chính xác theo biểu thức AND, OR, NOT"),
    "chỉ mục ngược": ("", "inverted index", "bảng tra từ → danh sách tài liệu chứa từ đó"),
    "vector": ("véc-tơ", "", "dãy số biểu diễn một ảnh hoặc một câu"),
    "cosine": ("cô-sin", "cosine similarity", "độ tương đồng giữa hai vector, từ −1 đến 1, càng lớn càng giống"),
    "val": ("va-li-đây-sần", "validation", "tập kiểm định có đáp án công khai"),
    "bootstrap": ("bút-xtrép", "paired bootstrap", "lấy mẫu lại các truy vấn 10.000 lần để ước lượng khoảng tin cậy của chênh lệch"),
    "Wilcoxon": ("uyn-cốc-xơn", "Wilcoxon signed-rank test", "kiểm định phi tham số so sánh hai kết quả ghép cặp"),
    "token": ("tô-kần", "", "đơn vị đầu vào của bộ mã hóa văn bản (một từ hoặc mảnh từ)"),
    "phi": ("", "ký hiệu φ (phi)", "mạng chiếu 3 lớp, phần duy nhất được huấn luyện"),
    "NAVER": ("nây-vơ", "", "tập đoàn công nghệ Hàn Quốc, nơi các tác giả làm việc"),
    "Pic2Word": ("píc-tu-uơd", "Picture to Word", "phương pháp zero-shot CIR trước LinCIR (CVPR 2023), học φ bằng ảnh"),
    "SEARLE": ("xơ-lơ", "zero-Shot composEd imAge Retrieval with textuaL invErsion", "phương pháp zero-shot CIR trước LinCIR (ICCV 2023), học φ bằng ảnh"),
    "CC3M": ("xê-xê ba em", "Conceptual Captions 3 Million", "bộ khoảng 3 triệu cặp ảnh – chú thích lấy từ web"),
    "GB": ("ghi-ga-bai", "gigabyte", "đơn vị dung lượng"),
    "MB": ("mê-ga-bai", "megabyte", "đơn vị dung lượng, 1.000 MB ≈ 1 GB"),
    "ViT-L": ("vít L", "Vision Transformer – Large", "bộ mã hóa ảnh cỡ lớn của CLIP"),
    "ViT-L/14": ("vít L mười bốn", "Vision Transformer – Large, patch 14 × 14", "phiên bản CLIP nhóm dùng"),
    "ViT-B/32": ("vít B ba hai", "Vision Transformer – Base, patch 32 × 32", "phiên bản CLIP nhỏ, dùng để chạy thử trên Mac"),
    "Self-Masking Projection": ("xen ma-xking prô-giéc-sần", "SMP", "chiếu tự che: che từ khóa, thay bằng token do φ tạo từ chính câu đó"),
    "spaCy": ("xpây-xi", "", "thư viện xử lý ngôn ngữ tự nhiên, dùng để tìm tính từ và danh từ"),
    "MSE": ("em-ét-i", "Mean Squared Error", "sai số bình phương trung bình giữa hai vector"),
    "modality gap": ("mô-đa-li-ti ghép", "", "khoảng cách giữa vùng vector ảnh và vùng vector văn bản trong CLIP"),
    "COCO": ("cô-cô", "Common Objects in COntext", "bộ ảnh đời thực của Microsoft; val2017 là tập kiểm định năm 2017"),
    "InfoNCE": ("in-phô en-xi-i", "Info Noise-Contrastive Estimation", "hàm mất mát đối sánh: kéo cặp đúng lại gần, đẩy các mẫu âm ra xa"),
    "batch": ("bát", "", "lô dữ liệu xử lý cùng lúc trong một bước (ở đây 512 câu)"),
    "L SMP": ("hàm mất mát SMP", "loss of Self-Masking Projection", "hàm MSE của LinCIR"),
    "tô": ("", "ký hiệu τ (tau), temperature", "nhiệt độ của InfoNCE, điều chỉnh độ “gắt” khi so sánh"),
    "baseline": ("bây-lai", "", "mốc so sánh: LinCIR gốc do nhóm tự huấn luyện cùng cấu hình"),
    "đen-ta": ("", "ký hiệu Δ (delta)", "vector từ tâm vùng văn bản tới tâm vùng ảnh"),
    "ép-xi-lon": ("", "ký hiệu ε (epsilon)", "nhiễu ngẫu nhiên theo phân phối chuẩn"),
    "transformers": ("tran-xpho-mơ", "", "thư viện mô hình học sâu mã nguồn mở của Hugging Face"),
    "tokenizer": ("tô-kần-nai-dơ", "", "bộ tách câu thành các token"),
    "Kaggle": ("ca-gồ", "", "nền tảng của Google cho chạy notebook với GPU miễn phí theo hạn mức"),
    "GPU": ("gi-pi-du", "Graphics Processing Unit", "bộ xử lý đồ họa, dùng để huấn luyện mô hình"),
    "NVIDIA T4": ("en-vi-đi-a ti-pho", "", "loại GPU 16 GB mà Kaggle cung cấp"),
    "CPU": ("xi-pi-du", "Central Processing Unit", "bộ xử lý trung tâm"),
    "fp16": ("ép-pi mười sáu", "floating point 16-bit", "số thực 16 bit, giúp huấn luyện nhanh và tốn ít bộ nhớ"),
    "AdamW": ("a-đam đáp-bờ-liu", "Adam with decoupled Weight decay", "thuật toán tối ưu dùng để cập nhật φ"),
    "weight decay": ("uết đi-cây", "", "phạt trọng số lớn để giảm quá khớp"),
    "run": ("ran", "", "một lần huấn luyện với một cấu hình và một seed"),
    "seed": ("xít", "random seed", "giá trị khởi tạo bộ sinh số ngẫu nhiên; chạy 3 seed để kiểm tra độ ổn định"),
    "checkpoint": ("chếch-poi", "", "trọng số mô hình được lưu tại một bước huấn luyện"),
    "LayerNorm": ("lay-ơ noóc", "Layer Normalization", "lớp chuẩn hóa giá trị trong mạng nơ-ron"),
    "prompt": ("prôm", "", "câu mô tả dùng để yêu cầu mô hình sinh ảnh"),
    "Midjourney": ("mít-giơ-ni", "", "dịch vụ sinh ảnh từ văn bản; mã nguồn dùng thêm các câu prompt của dịch vụ này"),
    "p": ("p (p-value)", "probability value", "xác suất thấy mức chênh này nếu cải tiến thật ra không có tác dụng; p < 0,05 là có ý nghĩa"),
    "khoảng tin cậy 95%": ("", "95% confidence interval", "khoảng chứa chênh lệch thật với độ tin cậy 95%; nằm hẳn dưới 0 nghĩa là chắc chắn kém hơn"),
    "âm tính giả": ("", "false negative", "ảnh đúng yêu cầu nhưng không được gán nhãn là đáp án"),
    "IDF": ("ai-đi-ép", "Inverse Document Frequency", "tần suất tài liệu nghịch đảo: từ càng hiếm, trọng số càng cao"),
    "lam-đa": ("", "ký hiệu λ (lambda)", "trọng số của InfoNCE trong cải tiến A"),
    "an-pha": ("", "ký hiệu α (alpha)", "hệ số của Δ trong cải tiến B"),
}

QA_ROUTE = ("Khi có câu hỏi: nghe hết câu hỏi, nhắc lại ngắn gọn, rồi trả lời hoặc mời người phụ trách. Phương pháp, cải tiến A, "
            "đường học: Trung. Tái hiện, bảng kết quả, kết luận: Tùng. Độ đo, kiểm định, cải tiến B, modality gap: Dũng. Bài toán, "
            "lý thuyết, ví dụ định tính: Nou. Mã nguồn, Kaggle, thiết lập thực nghiệm: Tâm. Danh sách câu hỏi dự kiến: "
            "slides/QA_du_kien.md và mục 6 trong tài liệu học của từng người.")

KAGGLE = [
    ("Phần cứng", "2 × NVIDIA T4 16 GB, 4 vCPU; Python 3.13, PyTorch 2.11"),
    ("Hạn mức Kaggle", "30 giờ GPU mỗi tuần; tối đa 12 giờ mỗi phiên"),
    ("Đã dùng", "22 giờ 52 phút / 30 giờ (đến khi xong phiên đánh giá cuối, 14:02 thứ Sáu 09/10/2026, giờ Hà Nội)"),
    ("Cấu hình huấn luyện", "CLIP ViT-L/14; batch 512; fp16; AdamW, tốc độ học 1e-4, weight decay 0,01; dropout của φ 0,5; "
                            "tốc độ học cố định; 5.000 bước; lưu checkpoint mỗi 500 bước (để vẽ đường học); dùng checkpoint bước cuối"),
    ("Bộ nhớ GPU", "tối đa 11,4 GB / 15 GB cho một run"),
    ("Số run", "12 run = 4 biến thể (baseline, A, B, A+B) × 3 seed (12345, 2024, 7), cộng đánh giá checkpoint chính thức"),
    ("Thời gian mỗi run", "trước tối ưu: 4,5 giây/bước, 6,2 giờ/run (2 run song song); sau tối ưu: 1,45 giây/bước, khoảng 2,0 giờ/run "
                          "(B seed 7: 1,91 giờ; A+B seed 7: 2,11 giờ)"),
    ("Vì sao 5.000 bước", "20.000 bước như bài báo mất khoảng 13 giờ/run trên T4, vượt giới hạn 12 giờ/phiên; mọi biến thể dùng cùng số bước"),
    ("Tối ưu nạp dữ liệu", "spaCy xử lý theo lô, bỏ NER và lemmatizer: nhanh gấp 3,1 lần; từ khóa trích ra giống hệt (kiểm tra 3.000 câu thật)"),
    ("Các phiên đã chạy", "chạy thử dữ liệu giả (06/10); chuẩn bị dữ liệu đánh giá và đánh giá checkpoint chính thức (07/10); huấn luyện 1: "
                          "baseline, A seed 12345 (08/10); huấn luyện 2: 8 run (08–09/10); huấn luyện cuối: B, A+B seed 7 (09/10); "
                          "đánh giá toàn bộ 12 run (09/10)"),
    ("Dữ liệu đánh giá", "FashionIQ val: 15.415 ảnh, 3 nhóm sản phẩm; CIRCO val: 220 truy vấn trên 123.403 ảnh COCO; "
                         "Δ tính trên 5.000 cặp COCO val2017"),
]


def annotate(text, seen):
    """split text into (segment, is_note) pieces; add a note after the first occurrence of each term in the document"""
    keys = sorted(TERMS, key=len, reverse=True)
    pat = re.compile("|".join(r"(?<![\w@/-])" + re.escape(k) + r"(?![\w@/-])" for k in keys))
    out, pos = [], 0
    for m in pat.finditer(text):
        k = m.group(0)
        if k in seen:
            continue
        seen.add(k)
        out.append((text[pos:m.end()], False))
        read, abbr, mean = TERMS[k]
        bits = [f"đọc “{read}”" if read else "", abbr, mean]
        out.append((" [" + "; ".join(b for b in bits if b) + "]", True))
        pos = m.end()
    out.append((text[pos:], False))
    return out


def add_annotated(doc, text, seen, indent=True, italic=False, color=None):
    q = doc.add_paragraph()
    if indent:
        q.paragraph_format.first_line_indent = Cm(0.8)
        q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for seg, note in annotate(text, seen):
        if not seg:
            continue
        r = q.add_run(seg)
        if note:
            r.font.size = Pt(10)
            r.font.color.rgb = MUTED
        else:
            r.italic = italic
            if color is not None:
                r.font.color.rgb = color
    return q


def syllables(t):
    return len(t.split())


def mmss(sec):
    sec = int(round(sec / 5.0) * 5)
    return f"{sec // 60}:{sec % 60:02d}"


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def table(doc, header, rows, widths):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for j, h in enumerate(header):
        c = t.rows[0].cells[j]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(c, "1E6FE8")
    for row in rows:
        cells = t.add_row().cells
        for j, v in enumerate(row):
            cells[j].text = str(v)
    for row in t.rows:
        for j, w in enumerate(widths):
            row.cells[j].width = Cm(w)
    doc.add_paragraph()
    return t


def main():
    prs = Presentation(DECK)
    titles = [next((sh.text_frame.text for sh in s.shapes if sh.name == "!!title"), "").replace("\n", " ") for s in prs.slides]
    titles[0] = "Bìa"
    n = len(titles)
    missing = [i for i in range(1, n + 1) if i not in SPEECH]
    if missing or len(SPEECH) != n:
        sys.exit(f"Kịch bản không khớp deck ({n} slide); thiếu: {missing}")

    doc = docx.Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    st.font.size = Pt(13)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.3
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.2)
        s.top_margin = s.bottom_margin = Cm(2.0)
    for name in ("Heading 1", "Heading 2"):
        doc.styles[name].font.name = "Times New Roman"
        doc.styles[name].font.color.rgb = ACCENT

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("KỊCH BẢN THUYẾT TRÌNH")
    r.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = ACCENT
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Nhóm 8 · Tái hiện và cải tiến LinCIR (CVPR 2024) · Người trình bày: Đào Văn Tâm")
    r.italic = True

    times = [syllables(" ".join(SPEECH[i][0]) + " " + SPEECH[i][1]) / PACE * 60 for i in range(1, n + 1)]
    total = sum(times)
    doc.add_heading("Cách dùng", level=1)
    for t in [f"Kịch bản khớp từng trang của {DECK.name} ({n} slide). Mỗi mục gồm lời nói và câu chuyển sang slide sau (in nghiêng).",
              f"Thời lượng ước tính theo tốc độ nói khoảng {PACE} tiếng/phút: tổng khoảng {mmss(total)}. Đọc thành tiếng 2–3 lần, "
              "bấm giờ; nếu dài hơn 16 phút, rút gọn đoạn thứ ba của slide 11 (chi tiết Kaggle) và giữ các con số chính.",
              "Một số chi tiết không có trên slide nhưng có trong lời nói (cấu hình và số giờ chạy Kaggle ở slide 11, ví dụ câu ở slide 3 và 7). "
              "Bảng số liệu Kaggle đầy đủ ở Phụ lục A; thuật ngữ, tên riêng, viết tắt ở Phụ lục B; ký hiệu ở Phụ lục C.",
              "Chữ xám nhỏ trong ngoặc vuông là chú thích (cách đọc, viết tắt của gì, nghĩa) ở lần đầu một thuật ngữ xuất hiện; "
              "không đọc phần này thành tiếng."]:
        doc.add_paragraph(t, style="List Bullet")
    acc = 0
    rows = []
    for i in range(1, n + 1):
        acc += times[i - 1]
        rows.append([i, titles[i - 1], mmss(times[i - 1]), mmss(acc)])
    table(doc, ["Slide", "Tiêu đề", "Thời lượng", "Mốc"], rows, [1.4, 11.0, 2.0, 1.8])

    doc.add_heading("Lời trình bày theo từng slide", level=1)
    seen = set()
    acc = 0
    for i in range(1, n + 1):
        acc += times[i - 1]
        doc.add_heading(f"Slide {i}. {titles[i - 1]}", level=2)
        meta = doc.add_paragraph()
        rr = meta.add_run(f"Khoảng {mmss(times[i - 1])} · đến mốc {mmss(acc)}")
        rr.font.size = Pt(11)
        rr.font.color.rgb = MUTED
        for para in SPEECH[i][0]:
            add_annotated(doc, para, seen)
        if SPEECH[i][1]:
            add_annotated(doc, "Chuyển: " + SPEECH[i][1], seen, indent=False, italic=True, color=ACCENT)
        if i == n:
            q = doc.add_paragraph()
            rr = q.add_run("Điều phối hỏi đáp: ")
            rr.bold = True
            q.add_run(QA_ROUTE)

    doc.add_heading("Phụ lục A. Thực nghiệm trên Kaggle: số liệu chi tiết", level=1)
    doc.add_paragraph("Dùng khi được hỏi về hạ tầng, cấu hình và thời gian chạy. Nguồn: nhật ký dự án (.claude/skills/roadmap/checklist.md), "
                      "docs/decisions.md, configs/EXP-001-baseline.yaml.")
    table(doc, ["Hạng mục", "Số liệu"], KAGGLE, [4.0, 12.2])
    doc.add_heading("Phụ lục B. Thuật ngữ, tên riêng và viết tắt", level=1)
    table(doc, ["Thuật ngữ", "Cách đọc", "Viết tắt của", "Nghĩa"],
          [[k, *TERMS[k]] for k in sorted(TERMS, key=str.lower)], [3.0, 3.4, 4.4, 5.4])
    doc.add_heading("Phụ lục C. Cách đọc ký hiệu trên slide", level=1)
    table(doc, ["Ký hiệu", "Đọc là", "Nghĩa"], [list(s) for s in SYMBOLS], [2.6, 4.6, 9.0])
    doc.save(OUT)
    print(OUT.name, f"{n} slide, tổng khoảng {mmss(total)}")


if __name__ == "__main__":
    main()
