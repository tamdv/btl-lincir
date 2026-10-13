# BTL Nhóm 8 — LinCIR

Tái hiện, cải tiến và đánh giá **LinCIR** (*Language-only Efficient Training of Zero-shot Composed Image Retrieval*, Gu et al., CVPR 2024) cho môn Tìm kiếm và Truy xuất thông tin.

- **Lớp:** M25CQHT02-B · **Giảng viên:** TS. Đào Thị Thuý Quỳnh
- **Thành viên:** Đào Văn Tâm B25CHHT112 (trưởng nhóm) · Lâm Thành Trung B25CHHT117 · Nguyễn Xuân Tùng B25CHHT119 · Trần Quang Đức Dũng B25CHHT088 · Mekdala Nounou B25CHHT124
- **Quy tắc làm việc, bản đồ code, lệnh chạy:** [CLAUDE.md](CLAUDE.md)

## Tóm tắt dễ hiểu

### Bài báo nói về điều gì

**Bài toán.** Bạn đang xem ảnh một chiếc váy hoa màu xanh trên trang bán hàng. Bạn muốn tìm một chiếc gần giống nhưng có thêm vài thay đổi, và gõ: "màu bạc, bóng hơn, tay ngắn hơn". Hệ thống phải tìm trong hàng chục nghìn ảnh ra chiếc váy vừa giữ kiểu dáng của ảnh ban đầu, vừa có đúng các thay đổi đó. Bài toán tìm kiếm bằng một ảnh kèm một câu mô tả thay đổi như vậy gọi là **truy xuất ảnh kết hợp**.

Bài toán này khó vì câu "màu bạc, tay ngắn hơn" không tự mô tả được chiếc váy cần tìm. Nó chỉ có nghĩa khi đặt cạnh ảnh ban đầu. Hệ thống phải hiểu cả ảnh lẫn câu cùng lúc.

**Cách làm cũ và chỗ tốn kém.** Cách đơn giản là thuê người tạo dữ liệu mẫu: mỗi mẫu gồm ảnh ban đầu, câu mô tả thay đổi và ảnh đúng cần tìm. Việc này rất tốn công, nên bộ dữ liệu lớn nhất cũng chỉ có khoảng 46 nghìn mẫu. Mô hình học từ dữ liệu thời trang thì cũng chỉ dùng tốt cho thời trang.

Một số phương pháp gần đây tránh được việc thuê người gán nhãn. Ý tưởng chung là đổi ảnh ban đầu thành một "từ đặc biệt", rồi ghép từ đó vào câu tìm kiếm, ví dụ: "ảnh của [từ đặc biệt], màu bạc, tay ngắn hơn". Một mô hình có sẵn tên CLIP, vốn đã được huấn luyện trên hàng trăm triệu cặp ảnh và câu, sẽ biến câu này thành con số rồi so với từng ảnh trong kho. Chỉ cần dạy một mạng nhỏ (gọi là φ) cách đổi ảnh thành từ đặc biệt.

Tuy vậy, các phương pháp trước vẫn dùng ảnh khi dạy mạng φ. Việc này nặng: bộ ảnh huấn luyện chiếm khoảng 430 GB, trong khi phần chữ đi kèm chỉ 125 MB. Chúng cũng chỉ học với một mẫu câu cố định.

**Ý tưởng của LinCIR.** Tác giả (công ty NAVER, Hàn Quốc, công bố năm 2024) đề xuất dạy mạng φ **chỉ bằng chữ, không cần ảnh**. Cách làm:

1. Lấy một câu, ví dụ "con mèo xám ngủ trên gối".
2. Che các từ quan trọng, câu thành "[…] ngủ trên […]".
3. Cho mạng φ đọc câu gốc rồi tạo ra một từ đặc biệt điền vào chỗ trống.
4. Yêu cầu câu đã điền phải mang nghĩa giống câu gốc.

Muốn làm được, mạng φ phải học cách gói nội dung chính của cả câu vào một từ. Khi dùng thật, đưa ảnh vào thay cho câu, mạng φ tạo ra từ đặc biệt đại diện cho ảnh.

Có một trở ngại: trong CLIP, con số biểu diễn ảnh và con số biểu diễn chữ nằm ở hai vùng khác nhau, dù cùng nói về một thứ. Mạng φ học trên chữ nhưng lại phải xử lý ảnh. Tác giả giải quyết bằng cách thêm nhiễu ngẫu nhiên vào đầu vào khi huấn luyện, để mạng quen với những đầu vào lệch khỏi vùng chữ.

**Kết quả bài báo.** LinCIR đạt kết quả tốt nhất trên bốn bộ đánh giá, huấn luyện nhanh hơn các phương pháp trước 6 đến 8 lần, và trên bộ thời trang còn vượt một phương pháp phải dùng dữ liệu do người gán nhãn.

### Nhóm 8 đã làm gì

**1. Dựng lại và kiểm tra.** Mã nguồn của tác giả viết cho phiên bản thư viện cũ, không chạy được trên máy hiện nay. Nhóm viết lại phần bị hỏng, sửa 4 lỗi, rồi kiểm tra: phần viết lại cho ra con số giống hệt bản gốc. Sau đó nhóm chạy lại mô hình tác giả công bố bằng mã của nhóm. Kết quả khớp bài báo, lệch không quá 0,77 điểm. Như vậy cách đánh giá của nhóm đáng tin.

**2. Đặt câu hỏi.** LinCIR có hai thành phần chính: cách chấm điểm khi dạy mạng φ, và phần nhiễu. Nhóm hỏi: sửa một trong hai thành phần này thì kết quả có tốt hơn không?

**3. Hai cải tiến.**

- **Cải tiến A (sửa cách chấm điểm).** Cách chấm gốc chỉ yêu cầu câu đã điền giống câu gốc. Nó không phạt trường hợp câu đã điền cũng giống nhiều câu khác. Nhóm thêm một yêu cầu: câu đã điền phải giống câu gốc **hơn** 511 câu khác đang xét cùng lúc. Kỳ vọng là mạng φ phân biệt rõ hơn, nên tìm kiếm chính xác hơn.
- **Cải tiến B (sửa phần nhiễu).** Nhiễu gốc lệch ngẫu nhiên theo mọi hướng. Nhóm đo hướng từ vùng chữ sang vùng ảnh, rồi cho nhiễu lệch có chủ đích về phía vùng ảnh. Khi đó mạng φ được luyện với đầu vào gần với ảnh thật mà nó sẽ gặp khi dùng.
- **Kết hợp A+B** để xem hai cải tiến có cộng thêm cho nhau không.

**4. Thử nghiệm công bằng.** Nhóm chạy cả bốn phiên bản (bản gốc, A, B, A+B) với cùng điều kiện, mỗi phiên bản 3 lần với khởi tạo ngẫu nhiên khác nhau, tổng cộng 12 lần. Thực nghiệm chạy trên máy chủ GPU miễn phí của Kaggle, dùng gần 23 trên 30 giờ được phép mỗi tuần. Kết quả được đánh giá trên hai bộ dữ liệu: thời trang (FashionIQ) và ảnh đời thực (CIRCO). Mọi chênh lệch đều được kiểm định thống kê để chắc rằng không do ngẫu nhiên.

### Kết quả

- **Cải tiến B tốt hơn bản gốc, và có ý nghĩa thống kê.** Trên bộ thời trang, cứ 1.000 lượt tìm kiếm thì B tìm đúng thêm khoảng 6 lượt trong 10 kết quả đầu. B chỉ huấn luyện bằng một phần tư thời gian nhưng vẫn vượt cả mô hình tác giả công bố.
- **Cải tiến A làm kết quả kém đi,** rõ nhất trên ảnh đời thực (điểm giảm từ 10,47 xuống 8,02). A+B cũng kém.

**Vì sao.** Nhóm đưa cùng một cặp ảnh và câu mô tả vào mạng φ, rồi đo hai đầu ra giống nhau đến mức nào:

- Với B, hai đầu ra giống nhau nhất: mạng xử lý ảnh nhất quán với cách nó xử lý chữ.
- Với A, độ giống giảm mạnh. Yêu cầu "phân biệt với 511 câu khác" khiến mạng học những chi tiết chỉ có ở chữ, mà ảnh không có.

**Kết luận của nhóm.** Với LinCIR, điều quan trọng nhất là mạng φ xử lý ảnh nhất quán với chữ. Làm cho mạng phân biệt các câu tốt hơn thì không giúp ích. Kết luận này có số đo trực tiếp và kiểm định thống kê làm căn cứ, không phải phỏng đoán.

Phần kỹ thuật chi tiết (số liệu, kiểm định, thuật ngữ) ở các mục bên dưới, trong [báo cáo](report/BaoCao_Nhom8_LinCIR.pdf) và [kịch bản thuyết trình](slides/KichBan_ThuyetTrinh_Tam.pdf).

## Truy cập nhanh

| Tài liệu | File |
|---|---|
| Báo cáo (30 trang) | [BaoCao_Nhom8_LinCIR.pdf](report/BaoCao_Nhom8_LinCIR.pdf) · [.docx](report/BaoCao_Nhom8_LinCIR.docx) |
| Slides thuyết trình (16 slide, Tâm trình bày, có ghi chú lời nói) | [Slides_Nhom8_LinCIR.pdf](slides/Slides_Nhom8_LinCIR.pdf) · [.pptx](slides/Slides_Nhom8_LinCIR.pptx) |
| Kịch bản thuyết trình của Tâm (lời nói từng slide, số liệu Kaggle) | [KichBan_ThuyetTrinh_Tam.pdf](slides/KichBan_ThuyetTrinh_Tam.pdf) · [.docx](slides/KichBan_ThuyetTrinh_Tam.docx) |
| Câu hỏi phản biện dự kiến | [slides/QA_du_kien.md](slides/QA_du_kien.md) |
| Khung nội dung slides | [slides/khung_slides.md](slides/khung_slides.md) |
| Tài liệu học riêng từng người | [Tâm](docs/study/HuongDan_Tam.pdf) · [Trung](docs/study/HuongDan_Trung.pdf) · [Tùng](docs/study/HuongDan_Tung.pdf) · [Dũng](docs/study/HuongDan_Dung.pdf) · [Nou](docs/study/HuongDan_Nou.pdf) (bản .docx cùng thư mục [docs/study/](docs/study/)) |
| Bài báo gốc | [papers/LinCIR_CVPR2024.pdf](papers/LinCIR_CVPR2024.pdf) · tham khảo [SEARLE_ICCV2023.pdf](papers/SEARLE_ICCV2023.pdf) |
| Số liệu đã chốt (chỉ lấy số từ đây) | [results/FROZEN.md](results/FROZEN.md) · [bảng kết quả chính](results/tables/main_results.md) · [kiểm định](results/tables/significance.md) · [ablation](results/tables/ablation.md) |
| Hình kết quả | [modality_gap.png](results/figures/modality_gap.png) · [learning_curve.png](results/figures/learning_curve.png) · [qualitative_fiq_1.png](results/figures/qualitative_fiq_1.png) |
| Nhật ký quyết định | [docs/decisions.md](docs/decisions.md) |
| Bài giảng chương I | [Chapter_I.pdf](../Chapter_I.pdf) |

## Kết quả cần nhớ (cả nhóm)

Trung bình 3 seed (12345, 2024, 7), 5.000 bước, cùng cấu hình cho mọi biến thể.

| Biến thể | FashionIQ R@10 | FashionIQ R@50 | CIRCO mAP@5 |
|---|---|---|---|
| Baseline (LinCIR nhóm tự huấn luyện) | 25,90 | 45,53 | 10,47 |
| A: thêm InfoNCE | 25,54 | 45,16 | 8,02 |
| **B: nhiễu có hướng theo modality gap** | **26,50** | **46,79** | **10,94** |
| A + B | 25,44 | 45,36 | 7,81 |
| Checkpoint chính thức (20.000 bước) | 26,35 | 46,12 | 10,50 |

- **B tốt hơn baseline có ý nghĩa thống kê:** FashionIQ R@10 +0,60 (p = 0,006), R@50 +1,27 (p < 0,001), CIRCO mAP@25 và mAP@50 tăng (p = 0,028 và 0,017).
- **A làm giảm hiệu năng:** CIRCO mAP@5 giảm 2,45 điểm, KTC 95% [−3,95; −1,07] nằm hoàn toàn dưới 0. A+B giảm tương tự.
- **Giải thích:** cosine trung bình giữa φ(ảnh) và φ(văn bản) là B 0,84 > chính thức 0,81 > baseline 0,80 > A+B 0,69 > A 0,64. Thứ tự này trùng thứ tự CIRCO mAP@5.
- **Giả thuyết:** H2 (B tốt hơn) được ủng hộ; H1 (A tốt hơn) và H3 (A+B tốt nhất) bị bác bỏ.
- **Tái hiện:** checkpoint chính thức lệch bài báo tối đa 0,77 điểm; encoder viết lại lệch CLIP gốc 0,00.

## Thứ tự thuyết trình (Tâm trình bày, khoảng 15 phút, 16 slide)

**Tâm trình bày toàn bộ**; các thành viên khác hỗ trợ trả lời phản biện cho phần việc của mình. Mạch trình bày: phân công → bài toán và câu hỏi của nhóm → độ đo → ý tưởng token giả → tóm tắt bài báo → hai thành phần của LinCIR (SMP, nhiễu) → hai cải tiến kèm giả thuyết H1–H3 → dựng mã và thực nghiệm → tái hiện → kết quả, kiểm định → phân tích nguyên nhân → kết luận.

| Slide | Nội dung (tiêu đề trên slide) | Thời gian | Hỗ trợ trả lời |
|---|---|---|---|
| 1 | Bìa, giới thiệu nhóm | 0:20 | — |
| 2 | Phân công công việc của nhóm | 0:30 | — |
| 3 | Truy vấn gồm một ảnh tham chiếu và một câu mô tả thay đổi | 1:00 | Nou |
| 4 | CIR là truy xuất có xếp hạng, đo bằng R@K và mAP@K | 1:00 | Nou, Dũng |
| 5 | Ảnh được biến thành một "từ giả" [$] trong câu truy vấn | 0:50 | Nou |
| 6 | Bài báo LinCIR: huấn luyện truy xuất ảnh kết hợp chỉ bằng văn bản | 1:00 | Nou, Tùng |
| 7 | LinCIR học từ giả chỉ bằng văn bản nhờ Self-Masking Projection | 1:20 | Trung |
| 8 | Nhiễu giúp φ dùng được vector ảnh dù hai miền lệch nhau | 1:00 | Dũng |
| 9 | Cải tiến A: thêm InfoNCE để từ giả phân biệt được các câu | 1:00 | Trung |
| 10 | Cải tiến B: dịch nhiễu theo hướng của modality gap | 1:00 | Dũng |
| 11 | Dựng lại mã nguồn và chạy 4 biến thể × 3 seed trên Kaggle | 1:00 | Tâm |
| 12 | Checkpoint chính thức tái hiện khớp bài báo, lệch tối đa 0,77 điểm | 0:50 | Tùng |
| 13 | Nhiễu có hướng (B) tốt hơn LinCIR, InfoNCE (A) làm giảm hiệu năng | 1:30 | Tùng, Dũng |
| 14 | Vì sao: B làm φ nhất quán hơn giữa ảnh và văn bản, A làm ngược lại | 1:20 | Dũng, Trung |
| 15 | Kết luận: H2 được ủng hộ, H1 và H3 bị bác bỏ | 1:20 | Tùng, Nou |
| 16 | Cảm ơn, hỏi đáp (Tâm điều phối, mời thành viên phụ trách trả lời) | — | — |

Mời trả lời khi phản biện: phương pháp, cải tiến A, đường học → Trung; tái hiện, bảng kết quả, kết luận → Tùng; độ đo, kiểm định, cải tiến B, modality gap → Dũng; bài toán, lý thuyết, ví dụ định tính → Nou; mã nguồn, Kaggle → Tâm.

Lời nói cho từng slide nằm trong phần ghi chú (Notes) của file .pptx; kịch bản chi tiết trong [HuongDan_Tam.pdf](docs/study/HuongDan_Tam.pdf). Nội dung từng slide: [slides/khung_slides.md](slides/khung_slides.md).

## Phân công: mỗi người cần đọc hiểu gì để trình bày

Mỗi người đọc **tài liệu học riêng** (file PDF ở bảng Truy cập nhanh) trước. Tài liệu của Tâm có kịch bản cả 15 slide; tài liệu của các thành viên khác có các slide liên quan để hỗ trợ trả lời. Mỗi tài liệu có: lý thuyết, ý chính từng slide, thuật ngữ, câu hỏi phản biện kèm trả lời và danh sách tự kiểm tra. Phần dưới đây là tóm tắt để biết cần đọc gì và nắm chắc điều gì.

### Đào Văn Tâm — Chuyển đổi mã nguồn và vận hành thực nghiệm trên Kaggle

**Nhiệm vụ:** chuyển mã LinCIR sang môi trường mới và kiểm chứng tương đương với mô hình gốc; lập lịch chạy song song trên Kaggle trong hạn mức GPU, khắc phục nghẽn nạp dữ liệu. Trình bày toàn bộ buổi thuyết trình.

**Trình bày:** toàn bộ 16 slide và điều phối hỏi đáp · **Tài liệu học:** [HuongDan_Tam.pdf](docs/study/HuongDan_Tam.pdf)

**Cần đọc**
- Báo cáo: chương 1, mục 3.1, 3.5, 5.1, 5.3; [docs/decisions.md](docs/decisions.md)
- Bài báo LinCIR: Abstract, mục 1 (đóng góp, Hình 1), 3.1, 4.1; CLIP (Radford 2021): mục 2.3 (encoder văn bản)
- Code: [code/encode_with_pseudo_tokens.py](code/encode_with_pseudo_tokens.py), [code/compat.py](code/compat.py), [scripts/check_encoder_equivalence.py](scripts/check_encoder_equivalence.py), [code/loader.py](code/loader.py) (collate theo lô), [scripts/run_experiment.py](scripts/run_experiment.py), [scripts/kaggle_jobs.py](scripts/kaggle_jobs.py), [notebooks/kaggle_lincir.ipynb](notebooks/kaggle_lincir.ipynb)

**Phải nắm chắc**
- Mã gốc dùng API nội bộ của transformers 4.34, không chạy trên 5.x. Nhóm viết lại lượt truyền xuôi từ các mô-đun con; sai lệch với CLIP gốc là 0,00 trên ViT-B/32 và ViT-L/14.
- Luồng mã hóa: câu → token → nhúng → thay token [$] bằng φ(v) → Transformer nhân quả → vector tại EOS (lấy bằng argmax vì EOS = 49407 là mã lớn nhất) → chiếu.
- Tốc độ: 4,5 giây/bước → 1,45 giây/bước (khoảng 2 giờ/run) nhờ chạy spaCy theo lô và bỏ NER, lemmatizer. Từ khóa trích ra giống hệt mã cũ.
- Kaggle: 2 GPU T4, 30 giờ/tuần, phiên tối đa 12 giờ. Mỗi GPU chạy một run độc lập để giữ batch 512 cho mọi biến thể (quan trọng với InfoNCE).
- Vì sao 5.000 bước thay vì 20.000: 20.000 bước mất khoảng 13 giờ/run, vượt giới hạn phiên; mọi biến thể dùng cùng số bước nên so sánh vẫn công bằng.
- Tóm tắt bài báo (slide 6): Gu, Chun, Kim, Kang, Yun (NAVER), CVPR 2024. Vấn đề: bộ ba CIR gán nhãn tay đắt và nhỏ (46,6k, 28,8k); Pic2Word, SEARLE cần ảnh khi huấn luyện và chỉ học câu mẫu cố định. Ý tưởng: Self-Masking Projection học φ chỉ từ văn bản, thêm nhiễu u·ε để φ dùng được cho vector ảnh. Kết quả bài báo: tốt nhất trên 4 benchmark (CIRCO, GeneCIS, FashionIQ, CIRR), nhanh hơn Pic2Word 6,0 lần và SEARLE 8,4 lần với ViT-L, ViT-G huấn luyện 48 phút trên 8 A100, vượt cả phương pháp có giám sát trên FashionIQ.
- Câu hỏi của nhóm (slide 3): sửa hàm mất mát (A) hoặc sửa nhiễu (B) có giúp LinCIR tốt hơn không; giả thuyết H1–H3 ở slide 9–10. Nêu trước kết luận chính: B tốt hơn có ý nghĩa thống kê, A làm giảm hiệu năng. Nắm bảng "Kết quả cần nhớ" ở đầu file này.
- Điều phối hỏi đáp: nghe hết câu hỏi, chuyển cho đúng người theo danh sách ở phần Thứ tự thuyết trình.

### Lâm Thành Trung — Cải tiến A (InfoNCE) và đường học

**Nhiệm vụ:** đề xuất và cài đặt cải tiến A (thêm InfoNCE vào SMP); phân tích đường học theo số bước huấn luyện.

**Hỗ trợ phản biện:** slide 7 (SMP), 9 (cải tiến A), 14 (đường học) · **Tài liệu học:** [HuongDan_Trung.pdf](docs/study/HuongDan_Trung.pdf)

**Cần đọc**
- Báo cáo: mục 2.5, 3.2–3.4, 4.1–4.2, 5.7
- Bài báo LinCIR: mục 3.1–3.2, Bảng 8–9; van den Oord 2018 (InfoNCE): mục 2; Pic2Word, SEARLE: phần phương pháp
- Code: [code/train_phi.py](code/train_phi.py) (tìm `# [NHOM8] Improvement A`), [configs/EXP-002-infonce.yaml](configs/EXP-002-infonce.yaml); hình [learning_curve.png](results/figures/learning_curve.png)

**Phải nắm chắc**
- Self-Masking Projection: che từ khóa trong câu, thay bằng [$] = φ(z_c), huấn luyện bằng MSE giữa vector câu gốc z_c và vector câu đã che ẑ_c. Hoàn toàn không cần ảnh.
- Pic2Word, SEARLE (slide 6): cần chạy bộ mã hóa ảnh khi huấn luyện (ảnh CC3M khoảng 430 GB, chú thích chỉ 125 MB) và chỉ học câu mẫu cố định "a photo of [$]"; LinCIR bỏ cả hai hạn chế này.
- Cải tiến A: L = MSE + 0,5·InfoNCE, τ = 0,07, mẫu âm là 511 câu khác trong batch. Giữ MSE để [$] không trôi khỏi phân phối token thật.
- Kết quả âm: CIRCO mAP@5 giảm 2,45 điểm, cosine φ(ảnh)–φ(văn bản) giảm 0,80 → 0,64. Lý do: InfoNCE buộc [$] mang đặc trưng phân biệt các câu, các đặc trưng này gắn với miền văn bản.
- Đường học: R@10 chỉ tăng 0,25 điểm từ 4.000 đến 5.000 bước; A thấp hơn baseline ở mọi mốc, nên kết luận không phụ thuộc điểm dừng.

### Nguyễn Xuân Tùng — Tái hiện và khác biệt giữa bài báo và mã nguồn

**Nhiệm vụ:** đánh giá checkpoint chính thức, đối chiếu với bài báo; phân tích khác biệt giữa bài báo và mã nguồn.

**Hỗ trợ phản biện:** slide 6 (bài báo), 12 (tái hiện), 13 (kết quả), 15 (kết luận) · **Tài liệu học:** [HuongDan_Tung.pdf](docs/study/HuongDan_Tung.pdf)

**Cần đọc**
- Báo cáo: mục 3.5, 5.2, 5.4, 5.5, 5.6, chương 6, Kết luận
- Bài báo LinCIR: Bảng 3, 5, 6 và mục 4.2; FashionIQ (Wu 2021), CIRCO trong SEARLE
- Code và kết quả: [experiments/runs/EXP-000-official-s0/](experiments/runs/EXP-000-official-s0/), [scripts/eval_per_query.py](scripts/eval_per_query.py), [code/models.py](code/models.py) (lớp Phi), [code/loader.py](code/loader.py) (build_loader, extract_keywords_spacy)

**Phải nắm chắc**
- Bảng tái hiện: checkpoint chính thức đạt FashionIQ R@10 26,35, R@50 46,12 (bài báo 26,28 / 46,49), lệch tối đa 0,77 điểm ở từng nhóm sản phẩm.
- Dữ liệu: FashionIQ val đủ 15.415/15.415 ảnh (bản sao HuggingFace), CIRCO val 220 truy vấn trên 123.403 ảnh COCO. CIRR bị bỏ vì chưa được duyệt NLVR2.
- 3 khác biệt bài báo–mã nguồn: φ không có LayerNorm (checkpoint cũng không có); dữ liệu huấn luyện có thêm Midjourney prompts; cách trích từ khóa bằng spaCy. Nhóm tái hiện theo mã vì mã tạo ra số liệu của bài báo.
- Phân biệt hai loại so sánh: so với bài báo là kiểm tra tái hiện; so với baseline nhóm tự chạy là đánh giá cải tiến.
- Bảng kết quả chính (slide 13): so với baseline nhóm tự chạy, không so với bài báo. B tốt hơn có ý nghĩa ở FashionIQ R@10 (+0,60, p = 0,006) và R@50 (+1,27, p < 0,001); A và A+B có KTC 95% trên CIRCO nằm dưới 0. Đọc được mean ± std, Δ, KTC 95%, p (hỏi Dũng cách giải thích).
- Kết luận (slide 15): H2 được ủng hộ, H1 và H3 bị bác bỏ; chất lượng phụ thuộc vào việc φ xử lý ảnh nhất quán với văn bản; B chỉ 5.000 bước nhưng vượt checkpoint 20.000 bước.
- Hạn chế và hướng phát triển (chương 6): 5.000 bước, chưa quét λ và α, chỉ 220 truy vấn CIRCO, chưa có CIRR → đủ 20.000 bước, quét λ/α, CIRR và CIRCO test, hướng C theo IDF.

### Trần Quang Đức Dũng — Giao thức đánh giá, kiểm định, cải tiến B

**Nhiệm vụ:** thiết kế đánh giá theo truy vấn (R@K, mAP@K) và kiểm định thống kê (paired bootstrap, Wilcoxon); cài đặt cải tiến B (nhiễu có hướng) và phân tích modality gap.

**Hỗ trợ phản biện:** slide 4 (độ đo), 8 (nhiễu), 10 (cải tiến B), 13 (kiểm định), 14 (cơ chế) · **Tài liệu học:** [HuongDan_Dung.pdf](docs/study/HuongDan_Dung.pdf)

**Cần đọc**
- Báo cáo: mục 2.1, 2.3, 3.3, 4.3, 5.3, 5.6, 5.7
- Bài báo LinCIR: mục 3.2 (nhiễu); Liang 2022 (Mind the Gap): mục 2–3; bootstrap (Efron & Tibshirani); bài giảng chương I (Precision/Recall)
- Code: [scripts/eval_per_query.py](scripts/eval_per_query.py), [scripts/stats_compare.py](scripts/stats_compare.py), [scripts/make_report_assets.py](scripts/make_report_assets.py), [scripts/modality_gap.py](scripts/modality_gap.py), [code/train_phi.py](code/train_phi.py) (`# [NHOM8] Improvement B`), [configs/EXP-003-gapnoise.yaml](configs/EXP-003-gapnoise.yaml), [configs/EXP-004-infonce-gapnoise.yaml](configs/EXP-004-infonce-gapnoise.yaml)
- Kết quả: [main_results.md](results/tables/main_results.md), [significance.md](results/tables/significance.md), [modality_gap.png](results/figures/modality_gap.png)

**Phải nắm chắc**
- Nhiễu và modality gap (slide 8): vector ảnh và văn bản của CLIP nằm ở hai vùng tách biệt (cosine ảnh–chú thích chỉ 0,26); LinCIR thêm nhiễu n = u·ε (u ~ U[0,1], ε ~ N(0,I)) để φ chịu được độ lệch này.
- Cải tiến B: n = 0,5·Δ + u·ε, với Δ = trung bình vector ảnh − trung bình vector văn bản trên 5.000 cặp COCO val2017 (‖Δ‖ = 13,87). COCO val2017 khác tập ảnh COCO unlabeled2017 của CIRCO, nên không rò rỉ dữ liệu.
- Tự tính được R@K (FashionIQ, 1 ảnh đúng) và AP@K (CIRCO, nhiều ảnh đúng) cho một ví dụ nhỏ.
- Paired bootstrap 10.000 lần trên hiệu số theo truy vấn, Wilcoxon kiểm tra chéo. Dùng bootstrap vì hiệu số Recall rời rạc, AP lệch, không chuẩn.
- Đọc bảng kiểm định: B tốt hơn ở FashionIQ R@10 (+0,60, p = 0,006), R@50 (+1,27, p < 0,001); vẫn có ý nghĩa sau hiệu chỉnh Bonferroni (ngưỡng 0,0083). A và A+B có KTC 95% trên CIRCO nằm dưới 0.
- Cơ chế: B tăng cosine φ(ảnh)–φ(văn bản) 0,80 → 0,84 và giảm khoảng cách tâm 0,29 → 0,25.

### Mekdala Nounou — Lý thuyết, phân tích định tính, slides

**Nhiệm vụ:** tổng quan lý thuyết (CIR, ZS-CIR, CLIP, Pic2Word, SEARLE) và liên hệ với các độ đo IR; phân tích định tính; thiết kế slides.

**Hỗ trợ phản biện:** slide 3 (bài toán), 4 (liên hệ chương I), 5 (token giả), 6 (Pic2Word, SEARLE), 15 (ví dụ định tính) · **Tài liệu học:** [HuongDan_Nou.pdf](docs/study/HuongDan_Nou.pdf)

**Cần đọc**
- Báo cáo: chương 1–2, mục 5.8
- Bài giảng chương I ([Chapter_I.pdf](../Chapter_I.pdf)): slide 6–8 (mô hình tìm kiếm, Precision/Recall)
- Bài báo LinCIR: mục 1–2; CLIP (Radford 2021): mục 1–2; Pic2Word, SEARLE: phần phương pháp
- File: [report/figures/cir_example.png](report/figures/cir_example.png), [qualitative_fiq_1.png](results/figures/qualitative_fiq_1.png), [slides/khung_slides.md](slides/khung_slides.md), [slides/QA_du_kien.md](slides/QA_du_kien.md)

**Phải nắm chắc**
- Bài toán CIR (slide 3): truy vấn = ảnh tham chiếu + câu mô tả thay đổi; câu chỉ mô tả phần thay đổi, không mô tả toàn bộ ảnh đích.
- Zero-shot (slide 3): không dùng bộ ba (ảnh tham chiếu, câu, ảnh đích) có nhãn khi huấn luyện, vì loại dữ liệu này đắt và nhỏ.
- Token giả (slide 6): ảnh tham chiếu → φ → token [$], ghép vào câu "a photo of [$] that …", bộ mã hóa văn bản tạo vector truy vấn; chỉ cần học φ.
- Pic2Word, SEARLE: đã biểu diễn ảnh thành từ giả nhưng chỉ học với câu mẫu cố định và cần ảnh khi huấn luyện (slide 6).
- Độ đo Recall@K và mAP@K (slide 4, Nou cần hiểu để trả lời câu hỏi liên hệ môn học).
- Tìm kiếm vector (cosine, kết quả có xếp hạng) khác chỉ mục ngược (khớp từ chính xác).
- CLIP: học đối sánh trên 400 triệu cặp ảnh–chú thích, đưa ảnh và văn bản vào cùng không gian vector.
- Ví dụ định tính (Hình 5.3): B xếp đúng ảnh đích ở vị trí 1; nhiều ảnh trong top-5 đúng phần lớn yêu cầu nhưng không được gán nhãn (âm tính giả).

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| [code/](code/) | Mã LinCIR gốc và sửa đổi của nhóm (đánh dấu `# [NHOM8]`) |
| [configs/](configs/) | Mỗi thí nghiệm một file `EXP-xxx.yaml` |
| [experiments/](experiments/) | `registry.csv` và thư mục từng run (`metrics.json`, `per_query_*.csv`) |
| [results/](results/) | Bảng và hình đã đóng băng dùng cho báo cáo, slides |
| [scripts/](scripts/) | Đánh giá theo truy vấn, kiểm định, modality gap, chạy thí nghiệm |
| [notebooks/](notebooks/) | Notebook Kaggle và các file kết quả tải về |
| [report/](report/), [slides/](slides/) | Báo cáo, slides và script tạo chúng |
| [docs/](docs/) | Tài liệu học ([study/](docs/study/)), ghi chú ([notes/](docs/notes/)), nhật ký quyết định |
| [papers/](papers/) | PDF bài báo |

## Dùng với Claude Code

Mở Claude Code tại thư mục này. Các skill có sẵn trong `.claude/skills/`:

| Skill | Dùng khi |
|---|---|
| `/roadmap` | Xem tiến độ, việc tiếp theo, ai làm gì (checklist: `.claude/skills/roadmap/checklist.md`) |
| `/experiment` | Đăng ký, chạy, ghi kết quả một thí nghiệm |
| `/compare-results` | So sánh baseline và cải tiến, kiểm định thống kê, lập bảng |
| `/update-checklist` | Đánh dấu việc đã xong trong checklist nhóm |
| `/write-report` | Soạn báo cáo, slides, Q&A từ số liệu đã chốt |
