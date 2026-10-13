"""[NHOM8] Plain, precise wording for the talk (no analogies): tips, a glossary with short definitions and examples
taken from the project, and a simple script per slide. Used by build_guides.py and update_notes.py."""

TIPS = [
    "**Mở đầu bằng mạch chính trong 3 câu:** (1) Truy xuất ảnh kết hợp cần dữ liệu có nhãn rất tốn kém. (2) LinCIR huấn luyện chỉ bằng văn bản nên không cần dữ liệu đó. (3) Nhóm tái hiện LinCIR, thử hai cải tiến, chứng minh bằng kiểm định rằng một cải tiến tốt hơn và giải thích vì sao cải tiến còn lại kém hơn.",
    "**Mỗi slide theo trình tự:** nêu ý chính (tiêu đề) → nêu một con số → giải thích con số đó có nghĩa gì → nối sang slide sau. Không đọc toàn bộ bảng; chỉ nêu dòng hoặc cột cần thiết.",
    "**Diễn giải con số ngay khi nêu:** R@10 = 26 nghĩa là trong 26% số truy vấn, ảnh đúng nằm trong 10 kết quả đầu tiên; tăng 0,60 điểm R@10 tương đương thêm khoảng 6 truy vấn tìm đúng trên mỗi 1.000 truy vấn.",
    "**Thuật ngữ:** nêu tên tiếng Việt kèm tên tiếng Anh và định nghĩa một câu ở lần xuất hiện đầu tiên; các lần sau dùng đúng một tên đó.",
    "**Khi nói, làm tròn hợp lý** (“khoảng 26%”, “giảm khoảng 23%”); số chính xác đã có trên slide và trong báo cáo.",
    "**Ngắt nghỉ sau kết luận chính** (slide 13) trước khi chuyển sang phần giải thích nguyên nhân.",
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
    "1": ('Giới thiệu đề tài, giảng viên và 5 thành viên. Tâm trình bày, cả nhóm cùng trả lời câu hỏi.', '—'),
    "2": ("Phân công: Tâm chuyển đổi mã nguồn và chạy thực nghiệm trên Kaggle; Trung làm cải tiến A và đường học; Tùng tái hiện và đối chiếu bài báo – mã nguồn; Dũng làm giao thức đánh giá, kiểm định và cải tiến B; Nou làm tổng quan lý thuyết, phân tích định tính và thiết kế slides. Tâm trình bày, khi hỏi đáp thành viên phụ trách trả lời phần của mình.", "—"),
    "3": ('Truy vấn gồm một ảnh tham chiếu và một câu chỉ mô tả phần thay đổi; hệ thống phải tìm ảnh giữ đặc điểm của ảnh tham chiếu và áp dụng thay đổi. Bài báo LinCIR giải bài toán này mà không cần bộ ba gán nhãn. Câu hỏi của nhóm: sửa hàm mất mát (A) hoặc sửa nhiễu (B) có giúp LinCIR truy xuất tốt hơn không.', 'FashionIQ chỉ có 46,6 nghìn bộ ba gán nhãn, CIRR 28,8 nghìn'),
    "4": ('CIR vẫn là truy xuất có xếp hạng như chương I. R@K là tỉ lệ truy vấn có ảnh đích trong K kết quả đầu, dùng cho FashionIQ (1 ảnh đúng). AP@K lấy Precision tại các vị trí có ảnh đúng, chia cho min(K, số ảnh đúng); mAP@K là trung bình trên các truy vấn, dùng cho CIRCO (nhiều ảnh đúng). Khác chương I: so khớp vector bằng cosine thay vì khớp từ. Mọi so sánh được kiểm định bootstrap và Wilcoxon theo từng truy vấn.', 'R@10 = 26 nghĩa là 26% số truy vấn có ảnh đích trong 10 kết quả đầu'),
    "5": ('Ảnh tham chiếu qua bộ mã hóa ảnh rồi qua mạng chiếu φ thành một token giả [$], ghép vào câu “a photo of [$] that …”; bộ mã hóa văn bản tạo vector truy vấn để xếp hạng ảnh theo cosine. Chỉ cần học φ, CLIP giữ nguyên.', '—'),
    "6": ('Pic2Word và SEARLE học φ nhưng cần ảnh khi huấn luyện và chỉ học một câu mẫu cố định. LinCIR học φ chỉ từ văn bản bằng Self-Masking Projection và thêm nhiễu; bài báo đạt kết quả tốt nhất trên 4 bộ đánh giá, huấn luyện nhanh hơn và vượt cả phương pháp có giám sát trên FashionIQ.', 'Nhanh hơn Pic2Word 6 lần, SEARLE 8,4 lần với ViT-L'),
    "7": ('Che tính từ, danh từ trong câu bằng [$], thay [$] bằng token do φ tạo từ chính câu gốc, rồi yêu cầu câu đã che có cùng vector với câu gốc (MSE). Ví dụ “gray cat sleeps on a pillow” thành “[$] sleeps on [$]”. Nhờ vậy [$] học được bản tóm tắt một từ của câu.', '—'),
    "8": ('Vector ảnh và vector văn bản của CLIP nằm ở hai vùng tách biệt. φ học trên văn bản nhưng khi suy luận nhận vector ảnh, nên LinCIR thêm nhiễu u · ε khi huấn luyện để φ chịu được độ lệch này.', 'Tâm hai vùng cách nhau 0,82; ảnh và chú thích của chính nó chỉ có cosine 0,26'),
    "9": ('Cải tiến A sửa hàm mất mát: MSE chỉ kéo câu đã che về câu gốc, không phạt khi nó cũng gần các câu khác, trong khi đánh giá là xếp hạng. Thêm InfoNCE với 511 câu khác trong batch làm mẫu âm. Giả thuyết H1: A tăng R@K, mAP@K so với baseline.', 'Chi phí chỉ tăng 2% thời gian mỗi bước (1,474 so với 1,448 giây)'),
    "10": ('Cải tiến B sửa nhiễu: nhiễu của LinCIR đều theo mọi hướng, không dịch về phía vùng ảnh. B cộng thêm 0,5 · Δ, với Δ là hiệu giữa tâm vector ảnh và tâm vector văn bản, tính trên COCO val2017 khác tập đánh giá. Giả thuyết H2: φ nhất quán hơn giữa ảnh và văn bản nên R@K, mAP@K tăng. H3: A và B sửa hai thành phần khác nhau nên A+B có thể cộng hưởng.', 'Độ lớn của Δ là 13,87, tính trên 5.000 cặp ảnh – chú thích'),
    "11": ('Mã gốc không chạy với thư viện hiện tại; nhóm viết lại encoder văn bản, thay tokenizer, sửa 4 lỗi và kiểm chứng sai lệch bằng 0. Thực nghiệm: 4 biến thể × 3 seed, 5.000 bước, chỉ khác thành phần cải tiến, chạy trên 2 GPU T4 của Kaggle.', 'Sai lệch 0,00 so với CLIP gốc; nạp dữ liệu nhanh gấp 3,1 lần'),
    "12": ('Trước khi cải tiến, nhóm đánh giá lại checkpoint chính thức bằng mã đã chuyển đổi; kết quả khớp bài báo. Ba điểm bài báo khác mã nguồn; nhóm theo mã vì mã tạo ra số liệu công bố.', 'Lệch lớn nhất 0,77 điểm phần trăm'),
    "13": ('So với baseline nhóm tự huấn luyện. B cao nhất ở mọi cột và tốt hơn có ý nghĩa thống kê; B 5.000 bước vượt cả checkpoint chính thức 20.000 bước. A và A+B kém hơn trên CIRCO.', 'B tăng 0,60 điểm R@10 (thêm khoảng 6 truy vấn đúng trên 1.000), p = 0,006'),
    "14": ('Đo độ tương đồng giữa đầu ra của φ khi nhận ảnh và khi nhận văn bản của cùng một cặp; thứ tự trùng với thứ tự CIRCO mAP@5. InfoNCE buộc [$] mang đặc trưng phân biệt các câu, không chuyển được sang ảnh. A thấp hơn baseline ở mọi mốc huấn luyện.', 'B 0,84, baseline 0,80, A 0,64'),
    "15": ('Ví dụ: B xếp đúng ảnh đích ở hạng 1, baseline thì không. Kết luận: H2 được ủng hộ, H1 và H3 bị bác bỏ; chất lượng phụ thuộc chủ yếu vào việc φ xử lý ảnh nhất quán với văn bản. Hạn chế: 5.000 bước, chưa quét λ, α, chưa có CIRR.', 'CIRCO mAP@5: B 10,94, A 8,02'),
}
