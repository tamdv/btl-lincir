# BTL Nhóm 8 — LinCIR

Tái hiện, cải tiến và đánh giá **LinCIR** (*Language-only Efficient Training of Zero-shot Composed Image Retrieval*, Gu et al., CVPR 2024) cho môn Tìm kiếm và Truy xuất thông tin.

- **Lớp:** M25CQHT02-B · **Giảng viên:** TS. Đào Thị Thuý Quỳnh
- **Thành viên:** Đào Văn Tâm B25CHHT112 (trưởng nhóm) · Lâm Thành Trung B25CHHT117 · Nguyễn Xuân Tùng B25CHHT119 · Trần Quang Đức Dũng B25CHHT088 · Mekdala Nounou B25CHHT124
- **Quy tắc làm việc, bản đồ code, lệnh chạy:** [CLAUDE.md](CLAUDE.md)

## Truy cập nhanh

| Tài liệu | File |
|---|---|
| Báo cáo (30 trang) | [BaoCao_Nhom8_LinCIR.pdf](report/BaoCao_Nhom8_LinCIR.pdf) · [.docx](report/BaoCao_Nhom8_LinCIR.docx) |
| Slides thuyết trình (17 slide, có ghi chú người nói) | [Slides_Nhom8_LinCIR.pdf](slides/Slides_Nhom8_LinCIR.pdf) · [.pptx](slides/Slides_Nhom8_LinCIR.pptx) |
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

## Thứ tự thuyết trình (khoảng 15 phút)

| Slide | Nội dung (tiêu đề trên slide) | Người trình bày | Thời gian |
|---|---|---|---|
| 1 | Bìa, giới thiệu nhóm | Tâm | 0:20 |
| 2 | Truy vấn gồm một ảnh tham chiếu và một câu mô tả thay đổi | Nou | 1:00 |
| 3 | Dữ liệu bộ ba đắt và nhỏ nên cần CIR không cần mẫu | Nou | 0:45 |
| 4 | CIR là truy xuất có xếp hạng, đo bằng R@K và mAP@K | Nou | 1:00 |
| 5 | Ảnh được biến thành một "từ giả" [$] trong câu truy vấn | Trung | 1:00 |
| 6 | Pic2Word và SEARLE học với câu mẫu cố định và cần ảnh | Trung | 0:40 |
| 7 | LinCIR học từ giả chỉ bằng văn bản nhờ Self-Masking Projection | Trung | 1:30 |
| 8 | Nhiễu giúp φ dùng được vector ảnh dù hai miền lệch nhau | Trung | 0:45 |
| 9 | Mã nguồn chạy trên môi trường mới với sai lệch bằng 0 | Tâm | 1:00 |
| 10 | Checkpoint chính thức tái hiện khớp bài báo, lệch tối đa 0,77 điểm | Tùng | 0:45 |
| 11 | Cải tiến A: thêm InfoNCE để từ giả phân biệt được các câu | Trung | 1:00 |
| 12 | Cải tiến B: dịch nhiễu theo hướng của modality gap | Dũng | 0:45 |
| 13 | Mọi biến thể dùng cùng cấu hình, 3 seed và kiểm định theo truy vấn | Tâm | 0:45 |
| 14 | Nhiễu có hướng (B) tốt hơn LinCIR, InfoNCE (A) làm giảm hiệu năng | Dũng | 1:30 |
| 15 | Vì sao: B làm φ nhất quán hơn giữa ảnh và văn bản, A làm ngược lại | Dũng | 1:30 |
| 16 | Kết luận: tính nhất quán qua modality gap quyết định chất lượng | Tùng | 0:45 |
| 17 | Cảm ơn, hỏi đáp | Cả nhóm | — |

Lời nói cho từng slide nằm trong phần ghi chú (Notes) của file .pptx, mỗi đoạn có tên người nói ở đầu.

## Phân công: mỗi người cần đọc hiểu gì để trình bày

Mỗi người đọc **tài liệu học riêng** (file PDF ở bảng Truy cập nhanh) trước. Tài liệu đó có: lý thuyết, lời nói từng slide, thuật ngữ, câu hỏi phản biện kèm trả lời và danh sách tự kiểm tra. Phần dưới đây là tóm tắt để biết cần đọc gì và nắm chắc điều gì.

### Đào Văn Tâm — Chuyển đổi mã nguồn và vận hành thực nghiệm trên Kaggle

**Nhiệm vụ:** chuyển mã LinCIR sang môi trường mới và kiểm chứng tương đương với mô hình gốc; lập lịch chạy song song trên Kaggle trong hạn mức GPU, khắc phục nghẽn nạp dữ liệu.

**Trình bày:** slide 1, 9, 13 · **Tài liệu học:** [HuongDan_Tam.pdf](docs/study/HuongDan_Tam.pdf)

**Cần đọc**
- Báo cáo: mục 3.5, 5.1, 5.3; [docs/decisions.md](docs/decisions.md)
- Bài báo LinCIR: mục 3.1, 4.1; CLIP (Radford 2021): mục 2.3 (encoder văn bản)
- Code: [code/encode_with_pseudo_tokens.py](code/encode_with_pseudo_tokens.py), [code/compat.py](code/compat.py), [scripts/check_encoder_equivalence.py](scripts/check_encoder_equivalence.py), [code/loader.py](code/loader.py) (collate theo lô), [scripts/run_experiment.py](scripts/run_experiment.py), [scripts/kaggle_jobs.py](scripts/kaggle_jobs.py), [notebooks/kaggle_lincir.ipynb](notebooks/kaggle_lincir.ipynb)

**Phải nắm chắc**
- Mã gốc dùng API nội bộ của transformers 4.34, không chạy trên 5.x. Nhóm viết lại lượt truyền xuôi từ các mô-đun con; sai lệch với CLIP gốc là 0,00 trên ViT-B/32 và ViT-L/14.
- Luồng mã hóa: câu → token → nhúng → thay token [$] bằng φ(v) → Transformer nhân quả → vector tại EOS (lấy bằng argmax vì EOS = 49407 là mã lớn nhất) → chiếu.
- Tốc độ: 4,5 giây/bước → 1,45 giây/bước (khoảng 2 giờ/run) nhờ chạy spaCy theo lô và bỏ NER, lemmatizer. Từ khóa trích ra giống hệt mã cũ.
- Kaggle: 2 GPU T4, 30 giờ/tuần, phiên tối đa 12 giờ. Mỗi GPU chạy một run độc lập để giữ batch 512 cho mọi biến thể (quan trọng với InfoNCE).
- Vì sao 5.000 bước thay vì 20.000: 20.000 bước mất khoảng 13 giờ/run, vượt giới hạn phiên; mọi biến thể dùng cùng số bước nên so sánh vẫn công bằng.

### Lâm Thành Trung — Cải tiến A (InfoNCE) và đường học

**Nhiệm vụ:** đề xuất và cài đặt cải tiến A (thêm InfoNCE vào SMP); phân tích đường học theo số bước huấn luyện. Đồng thời trình bày phương pháp LinCIR.

**Trình bày:** slide 5, 6, 7, 8, 11 · **Tài liệu học:** [HuongDan_Trung.pdf](docs/study/HuongDan_Trung.pdf)

**Cần đọc**
- Báo cáo: chương 3, mục 4.1–4.2, 5.7
- Bài báo LinCIR: mục 3.1–3.2, Bảng 8–9; van den Oord 2018 (InfoNCE): mục 2; Pic2Word, SEARLE: phần phương pháp
- Code: [code/train_phi.py](code/train_phi.py) (tìm `# [NHOM8] Improvement A`), [configs/EXP-002-infonce.yaml](configs/EXP-002-infonce.yaml); hình [learning_curve.png](results/figures/learning_curve.png)

**Phải nắm chắc**
- Self-Masking Projection: che từ khóa trong câu, thay bằng [$] = φ(z_c), huấn luyện bằng MSE giữa vector câu gốc z_c và vector câu đã che ẑ_c. Hoàn toàn không cần ảnh.
- Nhiễu n = u·ε (u ~ U[0,1], ε ~ N(0,I)) giúp φ chịu được độ lệch giữa vector ảnh và vector văn bản khi suy luận.
- Hạn chế của Pic2Word/SEARLE: cần ảnh khi huấn luyện, dùng câu mẫu cố định "a photo of [$]".
- Cải tiến A: L = MSE + 0,5·InfoNCE, τ = 0,07, mẫu âm là 511 câu khác trong batch. Giữ MSE để [$] không trôi khỏi phân phối token thật.
- Kết quả âm: CIRCO mAP@5 giảm 2,45 điểm, cosine φ(ảnh)–φ(văn bản) giảm 0,80 → 0,64. Lý do: InfoNCE buộc [$] mang đặc trưng phân biệt các câu, các đặc trưng này gắn với miền văn bản.
- Đường học: R@10 chỉ tăng 0,25 điểm từ 4.000 đến 5.000 bước; A thấp hơn baseline ở mọi mốc, nên kết luận không phụ thuộc điểm dừng.

### Nguyễn Xuân Tùng — Tái hiện và khác biệt giữa bài báo và mã nguồn

**Nhiệm vụ:** đánh giá checkpoint chính thức, đối chiếu với bài báo; phân tích khác biệt giữa bài báo và mã nguồn. Đồng thời trình bày kết luận.

**Trình bày:** slide 10, 16 · **Tài liệu học:** [HuongDan_Tung.pdf](docs/study/HuongDan_Tung.pdf)

**Cần đọc**
- Báo cáo: mục 3.5, 5.2, 5.4, chương 6, Kết luận
- Bài báo LinCIR: Bảng 3, 5, 6 và mục 4.2; FashionIQ (Wu 2021), CIRCO trong SEARLE
- Code và kết quả: [experiments/runs/EXP-000-official-s0/](experiments/runs/EXP-000-official-s0/), [scripts/eval_per_query.py](scripts/eval_per_query.py), [code/models.py](code/models.py) (lớp Phi), [code/loader.py](code/loader.py) (build_loader, extract_keywords_spacy)

**Phải nắm chắc**
- Bảng tái hiện: checkpoint chính thức đạt FashionIQ R@10 26,35, R@50 46,12 (bài báo 26,28 / 46,49), lệch tối đa 0,77 điểm ở từng nhóm sản phẩm.
- Dữ liệu: FashionIQ val đủ 15.415/15.415 ảnh (bản sao HuggingFace), CIRCO val 220 truy vấn trên 123.403 ảnh COCO. CIRR bị bỏ vì chưa được duyệt NLVR2.
- 3 khác biệt bài báo–mã nguồn: φ không có LayerNorm (checkpoint cũng không có); dữ liệu huấn luyện có thêm Midjourney prompts; cách trích từ khóa bằng spaCy. Nhóm tái hiện theo mã vì mã tạo ra số liệu của bài báo.
- Phân biệt hai loại so sánh: so với bài báo là kiểm tra tái hiện; so với baseline nhóm tự chạy là đánh giá cải tiến.
- Hạn chế (chương 6): 5.000 bước, chưa quét λ và α, chỉ 220 truy vấn CIRCO, chưa có CIRR.

### Trần Quang Đức Dũng — Giao thức đánh giá, kiểm định, cải tiến B

**Nhiệm vụ:** thiết kế đánh giá theo truy vấn (R@K, mAP@K) và kiểm định thống kê (paired bootstrap, Wilcoxon); cài đặt cải tiến B (nhiễu có hướng) và phân tích modality gap.

**Trình bày:** slide 12, 14, 15 · **Tài liệu học:** [HuongDan_Dung.pdf](docs/study/HuongDan_Dung.pdf)

**Cần đọc**
- Báo cáo: mục 2.1, 2.3, 4.3, 5.3, 5.5, 5.6, 5.7
- Liang 2022 (Mind the Gap): mục 2–3; bootstrap (Efron & Tibshirani); bài giảng chương I (Precision/Recall)
- Code: [scripts/eval_per_query.py](scripts/eval_per_query.py), [scripts/stats_compare.py](scripts/stats_compare.py), [scripts/make_report_assets.py](scripts/make_report_assets.py), [scripts/modality_gap.py](scripts/modality_gap.py), [code/train_phi.py](code/train_phi.py) (`# [NHOM8] Improvement B`), [configs/EXP-003-gapnoise.yaml](configs/EXP-003-gapnoise.yaml), [configs/EXP-004-infonce-gapnoise.yaml](configs/EXP-004-infonce-gapnoise.yaml)
- Kết quả: [main_results.md](results/tables/main_results.md), [significance.md](results/tables/significance.md), [modality_gap.png](results/figures/modality_gap.png)

**Phải nắm chắc**
- Cải tiến B: n = 0,5·Δ + u·ε, với Δ = trung bình vector ảnh − trung bình vector văn bản trên 5.000 cặp COCO val2017 (‖Δ‖ = 13,87). COCO val2017 khác tập ảnh COCO unlabeled2017 của CIRCO, nên không rò rỉ dữ liệu.
- Tự tính được R@K (FashionIQ, 1 ảnh đúng) và AP@K (CIRCO, nhiều ảnh đúng) cho một ví dụ nhỏ.
- Paired bootstrap 10.000 lần trên hiệu số theo truy vấn, Wilcoxon kiểm tra chéo. Dùng bootstrap vì hiệu số Recall rời rạc, AP lệch, không chuẩn.
- Đọc bảng kiểm định: B tốt hơn ở FashionIQ R@10 (+0,60, p = 0,006), R@50 (+1,27, p < 0,001); vẫn có ý nghĩa sau hiệu chỉnh Bonferroni (ngưỡng 0,0083). A và A+B có KTC 95% trên CIRCO nằm dưới 0.
- Cơ chế: B tăng cosine φ(ảnh)–φ(văn bản) 0,80 → 0,84 và giảm khoảng cách tâm 0,29 → 0,25.

### Mekdala Nounou — Lý thuyết, phân tích định tính, slides

**Nhiệm vụ:** tổng quan lý thuyết (CIR, ZS-CIR, CLIP, Pic2Word, SEARLE) và liên hệ với các độ đo IR; phân tích định tính; thiết kế slides.

**Trình bày:** slide 2, 3, 4 · **Tài liệu học:** [HuongDan_Nou.pdf](docs/study/HuongDan_Nou.pdf)

**Cần đọc**
- Báo cáo: chương 1–2, mục 5.8
- Bài giảng chương I ([Chapter_I.pdf](../Chapter_I.pdf)): slide 6–8 (mô hình tìm kiếm, Precision/Recall)
- Bài báo LinCIR: mục 1–2; CLIP (Radford 2021): mục 1–2
- File: [report/figures/cir_example.png](report/figures/cir_example.png), [qualitative_fiq_1.png](results/figures/qualitative_fiq_1.png), [slides/khung_slides.md](slides/khung_slides.md), [slides/QA_du_kien.md](slides/QA_du_kien.md)

**Phải nắm chắc**
- CIR: truy vấn = ảnh tham chiếu + câu mô tả thay đổi; câu chỉ mô tả phần thay đổi, không mô tả toàn bộ ảnh đích.
- Zero-shot: không dùng bộ ba (ảnh tham chiếu, câu, ảnh đích) có nhãn khi huấn luyện, vì loại dữ liệu này đắt và nhỏ.
- Độ đo: Recall@K cho FashionIQ (1 ảnh đúng), mAP@K cho CIRCO (nhiều ảnh đúng, tính cả vị trí). Liên hệ Precision/Recall trong bài giảng.
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
