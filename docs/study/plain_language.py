"""[NHOM8] Plain, precise wording for the talk (no analogies): tips, a glossary with short definitions and examples
taken from the project, and a simple script per slide. Used by build_guides.py and update_notes.py."""

TIPS = [
    "**Mở đầu bằng mạch chính trong 3 câu:** (1) Truy xuất ảnh kết hợp cần dữ liệu có nhãn rất tốn kém. (2) LinCIR huấn luyện chỉ bằng văn bản nên không cần dữ liệu đó. (3) Nhóm tái hiện LinCIR, thử hai cải tiến, chứng minh bằng kiểm định rằng một cải tiến tốt hơn và giải thích vì sao cải tiến còn lại kém hơn.",
    "**Mỗi slide theo trình tự:** nêu ý chính (tiêu đề) → nêu một con số → giải thích con số đó có nghĩa gì → nối sang slide sau. Không đọc toàn bộ bảng; chỉ nêu dòng hoặc cột cần thiết.",
    "**Diễn giải con số ngay khi nêu:** R@10 = 26 nghĩa là trong 26% số truy vấn, ảnh đúng nằm trong 10 kết quả đầu tiên; tăng 0,60 điểm R@10 tương đương thêm khoảng 6 truy vấn tìm đúng trên mỗi 1.000 truy vấn.",
    "**Thuật ngữ:** nêu tên tiếng Việt kèm tên tiếng Anh và định nghĩa một câu ở lần xuất hiện đầu tiên; các lần sau dùng đúng một tên đó.",
    "**Khi nói, làm tròn hợp lý** (“khoảng 26%”, “giảm khoảng 23%”); số chính xác đã có trên slide và trong báo cáo.",
    "**Ngắt nghỉ sau kết luận chính** (slide 12) trước khi chuyển sang phần giải thích nguyên nhân.",
    "**Trả lời câu hỏi:** câu đầu nêu thẳng kết luận, câu sau nêu căn cứ (số liệu, mục trong báo cáo).",
]

GLOSSARY = [
    ("Truy xuất ảnh kết hợp (CIR)", "Tìm ảnh bằng truy vấn gồm một ảnh tham chiếu và một câu mô tả thay đổi", "Ảnh váy hoa xanh + “màu bạc, tay ngắn hơn” → tìm ảnh váy bạc tay ngắn"),
    ("Zero-shot", "Mô hình không được huấn luyện trên dữ liệu có nhãn của bài toán đích, được đánh giá trực tiếp", "LinCIR không dùng bộ ba nào của FashionIQ hay CIRCO khi huấn luyện"),
    ("Bộ ba có nhãn", "Ảnh tham chiếu – câu điều chỉnh – ảnh đích, do người gán thủ công", "FashionIQ có khoảng 46,6 nghìn bộ ba huấn luyện"),
    ("CLIP", "Mô hình gồm bộ mã hóa ảnh và bộ mã hóa văn bản, đưa ảnh và câu mô tả tương ứng về gần nhau", "Nhóm dùng CLIP ViT-L/14, giữ nguyên không huấn luyện lại"),
    ("Vector nhúng", "Dãy số (768 chiều với ViT-L) biểu diễn nội dung của một ảnh hoặc một câu", "Mỗi ảnh trong kho được mã hóa thành một vector"),
    ("Độ tương đồng cosine", "Mức độ cùng hướng của hai vector, càng gần 1 càng giống", "Kết quả truy xuất được xếp theo cosine giữa truy vấn và từng ảnh"),
    ("Token giả [$]", "Một vector đặt vào vị trí của một từ trong câu, đại diện cho ảnh tham chiếu", "Câu truy vấn: “a photo of [$] that is silver with shorter sleeves”"),
    ("Mạng chiếu φ", "Mạng nơ-ron nhỏ (3 lớp) biến vector thành token giả; là thành phần duy nhất được huấn luyện", "Cả 4 biến thể của nhóm chỉ khác nhau ở cách huấn luyện φ"),
    ("Self-Masking Projection (SMP)", "Che các cụm tính từ – danh từ của câu bằng [$] và huấn luyện φ để câu đã che giữ nguyên vector của câu gốc", "“gray cat sleeps on a pillow” → “[$] sleeps on [$]”"),
    ("Khoảng cách ảnh – văn bản (modality gap)", "Vector ảnh và vector văn bản của CLIP nằm ở hai vùng tách biệt", "Ảnh và chú thích của chính nó chỉ có cosine trung bình 0,26 (5.000 cặp COCO)"),
    ("Nhiễu khi huấn luyện", "Thành phần ngẫu nhiên cộng vào vector văn bản để φ chịu được khác biệt giữa ảnh và văn bản", "LinCIR dùng n = u·ε, u ~ U(0,1), ε ~ N(0, I)"),
    ("Cải tiến B – nhiễu có hướng", "Cộng thêm vector Δ (tâm vector ảnh trừ tâm vector văn bản) vào nhiễu, đẩy đầu vào của φ về phía vùng ảnh", "n = 0,5·Δ + u·ε, Δ tính trên 5.000 cặp COCO"),
    ("Cải tiến A – InfoNCE", "Hàm mất mát đối sánh: mỗi câu phải gần chính nó hơn 511 câu khác trong cùng batch", "L = MSE + 0,5·InfoNCE"),
    ("Baseline", "LinCIR gốc do nhóm tự huấn luyện, cùng cấu hình với các biến thể, dùng làm mốc so sánh", "5.000 bước, 3 seed"),
    ("Checkpoint", "Trọng số của mô hình được lưu tại một thời điểm huấn luyện", "Checkpoint chính thức của tác giả huấn luyện 20.000 bước"),
    ("Bước huấn luyện", "Một lần cập nhật trọng số trên một batch 512 câu", "5.000 bước mất khoảng 2 giờ trên GPU T4"),
    ("Seed", "Giá trị khởi tạo bộ sinh số ngẫu nhiên; khác seed thì thứ tự dữ liệu và nhiễu khác nhau", "Mỗi biến thể chạy với 3 seed: 12345, 2024, 7"),
    ("Độ lệch chuẩn (±)", "Mức dao động của kết quả giữa các lần chạy khác seed", "B: R@10 = 26,50 ± 0,04 — rất ổn định"),
    ("R@10, R@50 (Recall@K)", "Tỷ lệ truy vấn có ảnh đích nằm trong K kết quả đầu", "FashionIQ chỉ có một ảnh đúng cho mỗi truy vấn"),
    ("mAP@5", "Trung bình độ chính xác trên K = 5 kết quả đầu, dùng khi mỗi truy vấn có nhiều ảnh đúng", "CIRCO có trung bình 4,16 ảnh đúng mỗi truy vấn"),
    ("p-value", "Xác suất quan sát được mức chênh lệch như vậy nếu thực tế hai phương pháp ngang nhau", "B so với baseline, FashionIQ R@10: p = 0,006"),
    ("Khoảng tin cậy 95% (KTC)", "Khoảng giá trị của mức chênh lệch thật với độ tin cậy 95%; nếu toàn bộ khoảng lớn hơn 0 thì cải tiến tốt hơn", "B, R@50: Δ = +1,27, KTC [+0,81; +1,73]"),
    ("Paired bootstrap", "Lấy mẫu lại các truy vấn 10.000 lần, tính lại mức chênh mỗi lần để ước lượng p-value và KTC", "So từng truy vấn của B với cùng truy vấn đó của baseline"),
    ("Âm tính giả", "Ảnh thực tế thỏa truy vấn nhưng không được gán nhãn là đáp án", "Lý do bài báo khuyến nghị dùng mAP và K lớn thay vì R@1"),
    ("Ablation", "So sánh các biến thể bật/tắt từng thành phần để tách đóng góp của mỗi thành phần", "Baseline, A, B, A+B"),
]


# cách đọc ký hiệu trên slide: (ký hiệu, đọc là, nghĩa)
SYMBOLS = [
    ("φ", "“phi”", "Mạng chiếu 3 lớp, phần duy nhất được huấn luyện; biến một vector (ảnh hoặc câu) thành một token"),
    ("[$]", "“token giả” (hoặc “token đô-la”)", "Vị trí trong câu được thay bằng đầu ra của φ; “a photo of [$] that is blue” đọc là “a photo of token giả that is blue”"),
    ("Δ", "“đen-ta”", "Vector chênh lệch: tâm vector ảnh trừ tâm vector văn bản"),
    ("ε", "“ép-xi-lon”", "Nhiễu ngẫu nhiên theo phân phối chuẩn"),
    ("u · ε", "“u nhân ép-xi-lon”", "Nhiễu của LinCIR; u là hệ số ngẫu nhiên từ 0 đến 1"),
    ("α", "“an-pha”", "Hệ số của Δ trong cải tiến B (0,5)"),
    ("λ", "“lam-đa”", "Trọng số của InfoNCE trong cải tiến A (0,5)"),
    ("τ", "“tô”", "Nhiệt độ của InfoNCE (0,07)"),
    ("z_c", "“z c”", "Vector của câu gốc"),
    ("ẑ_c", "“z c mũ”", "Vector của câu đã che từ khóa bằng token giả"),
    ("L_SMP", "“hàm mất mát SMP”", "Hàm mất mát MSE của Self-Masking Projection"),
    ("R@K, R@10", "“Recall tại K”, “Recall tại 10”", "Tỉ lệ truy vấn có ảnh đích trong K kết quả đầu"),
    ("mAP@5", "“m-A-P tại 5”", "Độ chính xác trung bình trên 5 kết quả đầu"),
    ("±", "“cộng trừ”", "Độ lệch chuẩn qua 3 seed; “26,50 ± 0,04” đọc là “26,50 cộng trừ 0,04”"),
    ("p = 0,006", "“p bằng không phẩy không không sáu”", "Xác suất thấy mức chênh này nếu cải tiến thật ra không có tác dụng"),
    ("InfoNCE, CLIP", "“in-phô en-xi-i”, “clíp”", "Đọc thẳng tên tiếng Anh; tương tự baseline, seed, batch"),
]

# per slide: (ý chính nói thành lời, một con số + ý nghĩa)
SLIDES = {
    "1": ("Giới thiệu đề tài, giảng viên và 5 thành viên. Đề tài: tái hiện và cải tiến phương pháp LinCIR, chứng minh cải tiến bằng kiểm định thống kê.", "—"),
    "2": ("Bài báo LinCIR (NAVER, CVPR 2024): bộ ba CIR gán nhãn tay đắt và nhỏ; Pic2Word, SEARLE cần ảnh khi huấn luyện và chỉ học câu mẫu cố định. LinCIR học mạng chiếu φ chỉ từ văn bản bằng Self-Masking Projection, thêm nhiễu để φ dùng được cho vector ảnh; tốt nhất trên 4 benchmark, huấn luyện nhanh hơn. Mã công khai nên nhóm dựng lại mã, tái hiện, chạy baseline, A, B, A+B trên Kaggle, kiểm định và phân tích. Nêu trước kết luận: B tốt hơn có ý nghĩa thống kê, A làm giảm hiệu năng.", "Nhanh hơn Pic2Word 6 lần, SEARLE 8,4 lần; kết quả nhóm: B tăng FashionIQ R@10 từ 25,90 lên 26,50, p = 0,006"),
    "3": ("Truy vấn gồm một ảnh tham chiếu và một câu mô tả thay đổi; hệ thống phải tìm ảnh giữ đặc điểm của ảnh tham chiếu và áp dụng thay đổi. Bộ ba (ảnh tham chiếu, câu, ảnh đích) phải gán nhãn tay nên đắt và nhỏ, vì vậy cần zero-shot: không dùng bộ ba nào khi huấn luyện.", "FashionIQ chỉ có 46,6 nghìn bộ ba, CIRR 28,8 nghìn"),
    "4": ("Ảnh tham chiếu được chuyển thành một token giả [$] và ghép vào câu “a photo of [$] that …”; bộ mã hóa văn bản tạo vector truy vấn để tìm ảnh. Chỉ cần huấn luyện mạng chiếu φ.", "—"),
    "5": ("Khác Pic2Word và SEARLE (cần ảnh, câu mẫu cố định), LinCIR huấn luyện φ chỉ bằng văn bản: che các từ khóa của câu bằng [$] và yêu cầu câu đã che có cùng vector với câu gốc.", "—"),
    "6": ("Cải tiến A sửa hàm mất mát vừa trình bày: thêm hàm mất mát đối sánh để mỗi câu phân biệt với 511 câu khác. Kết quả: không tốt hơn trên FashionIQ và kém hơn trên CIRCO; nguyên nhân trình bày ở slide 13.", "CIRCO mAP@5 giảm từ 10,47 xuống 8,02, tức giảm khoảng 23%"),
    "7": ("Vector ảnh và vector văn bản của CLIP nằm ở hai vùng tách biệt; LinCIR thêm nhiễu u·ε không có hướng để φ chịu được độ lệch này. Cải tiến B cộng vào nhiễu vector Δ chỉ từ vùng văn bản sang vùng ảnh, để φ được huấn luyện gần với điều kiện khi suy luận.", "Δ tính trên 5.000 cặp COCO, độc lập với dữ liệu đánh giá"),
    "8": ("Bài toán vẫn là truy xuất có xếp hạng như chương I. R@K là Recall tính trên K kết quả đầu; mAP@K dùng khi có nhiều ảnh đúng. Khác chương I ở chỗ so khớp bằng vector thay vì từ khóa.", "R@10 = 26 nghĩa là 26% số truy vấn có ảnh đúng trong 10 kết quả đầu"),
    "9": ("Mã nguồn gốc không chạy với thư viện hiện tại. Nhóm viết lại phần mã hóa văn bản, sửa 4 lỗi và kiểm chứng kết quả trùng khớp với mô hình gốc.", "Sai lệch 0,00 so với CLIP gốc"),
    "10": ("Mọi biến thể dùng cùng dữ liệu, cùng 5.000 bước, cùng siêu tham số và chạy 3 seed; chỉ khác đúng thành phần cải tiến. Nhóm khắc phục nghẽn nạp dữ liệu để kịp chạy trong hạn mức GPU.", "Tốc độ tăng 3,1 lần: 2,0 giờ mỗi lần chạy thay vì 6,2 giờ"),
    "11": ("Nhóm đánh giá lại checkpoint chính thức bằng mã đã chuyển đổi; kết quả khớp bài báo, xác nhận quy trình đánh giá đúng.", "Lệch lớn nhất 0,77 điểm phần trăm"),
    "12": ("B cao nhất ở mọi cột và tốt hơn baseline có ý nghĩa thống kê; A và A+B kém hơn trên CIRCO.", "B tăng 0,60 điểm R@10 (thêm khoảng 6 truy vấn đúng trên 1.000), p = 0,006"),
    "13": ("Đo độ tương đồng giữa đầu ra của φ khi nhận ảnh và khi nhận văn bản của cùng một cặp. Thứ tự độ tương đồng trùng với thứ tự kết quả CIRCO.", "B 0,84, baseline 0,80, A 0,64"),
    "14": ("Chất lượng truy xuất phụ thuộc chủ yếu vào việc φ xử lý ảnh nhất quán với văn bản. B cải thiện điều này nên tốt hơn; A làm giảm nên kém hơn. Hạn chế chính: huấn luyện 5.000 bước và chưa quét siêu tham số.", "B chỉ huấn luyện 5.000 bước nhưng vượt checkpoint chính thức 20.000 bước"),
}
