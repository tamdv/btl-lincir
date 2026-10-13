"""[NHOM8] Study guides, one per member: what they did, the theory behind it, a talk script and expected questions.

  python docs/study/build_guides.py            # -> docs/study/HuongDan_<Ten>.docx
  ./docs/study/to_pdf.sh                        # -> .pdf via Microsoft Word (macOS)

Numbers marked [[...]] are placeholders filled after the evaluation sessions (yellow in the document).
"""
import re
import sys
from pathlib import Path

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
ACCENT = RGBColor(0x1F, 0x3A, 0x68)

# ---------------------------------------------------------------- shared content

OVERVIEW = [
    "**Bài toán.** Truy xuất ảnh kết hợp (Composed Image Retrieval – CIR): truy vấn gồm một ảnh tham chiếu và một câu mô tả thay đổi (“chiếc váy này nhưng màu bạc, tay ngắn hơn”); hệ thống trả về ảnh thỏa cả hai. Dữ liệu bộ ba ⟨ảnh, câu, ảnh đích⟩ đắt và nhỏ, nên hướng **zero-shot** huấn luyện không cần bộ ba.",
    "**Bài báo.** LinCIR (Gu và cộng sự, CVPR 2024) học một mạng chiếu φ (MLP 3 lớp) biến một vector thành “từ giả” [$] trong không gian token của CLIP, **chỉ bằng văn bản**: che các từ khóa của câu bằng [$] = φ(vector của câu + nhiễu) và ép câu đã che có cùng vector với câu gốc (Self-Masking Projection, mất mát MSE). Khi truy vấn, thay vector câu bằng vector ảnh: “a photo of [$] that {câu điều chỉnh}” → tìm ảnh theo cosine.",
    "**Nhóm đã làm.** (1) Chuyển mã nguồn chính thức sang Python 3.13 / transformers 5.x, kiểm chứng sai lệch 0 so với mô hình gốc. (2) Tái hiện: checkpoint chính thức đạt FashionIQ R@10 = 26,35 / R@50 = 46,12 (bài báo 26,28 / 46,49). (3) Hai cải tiến: **A** – thêm mất mát đối sánh InfoNCE; **B** – nhiễu có hướng theo modality gap. (4) Huấn luyện baseline, A, B, A+B trên Kaggle (2 × T4), mỗi biến thể 3 seed, 5.000 bước; đánh giá FashionIQ val + CIRCO val; kiểm định thống kê theo truy vấn.",
    "**Kết quả chính.** **B (nhiễu có hướng) tốt hơn baseline có ý nghĩa thống kê**: FashionIQ R@10 +0,60 (p = 0,006), R@50 +1,27 (p < 0,001), CIRCO mAP@25/50 tăng có ý nghĩa; B còn vượt checkpoint chính thức 20.000 bước. **A (InfoNCE) không tốt hơn** trên FashionIQ và **kém rõ trên CIRCO** (mAP@5 −2,45, KTC 95% nằm dưới 0); A+B tương tự A. Giải thích: độ nhất quán của φ giữa ảnh và văn bản (cosine) B 0,84 > baseline 0,80 > A 0,64 — cùng thứ tự với CIRCO. Kết luận: H2 được ủng hộ, H1 và H3 bị bác bỏ.",
]

KEY_NUMBERS = [
    ("Backbone", "CLIP ViT-L/14 (đóng băng); chỉ huấn luyện φ"),
    ("Huấn luyện", "AdamW, lr 1e-4, wd 0,01, batch 512, dropout 0,5, 5.000 bước (bài báo 20.000)"),
    ("Dữ liệu train", "Chỉ văn bản: chú thích CC3M + 2,47 triệu prompt Stable Diffusion + prompt Midjourney"),
    ("Đánh giá", "FashionIQ val (6.016 truy vấn, 3 nhóm, R@10/R@50); CIRCO val (220 truy vấn, 123.403 ảnh, mAP@K)"),
    ("Tái hiện", "Checkpoint chính thức: FIQ R@10 26,35 vs 26,28; R@50 46,12 vs 46,49 (lệch lớn nhất 0,77 điểm)"),
    ("Cải tiến A", "L = MSE + 0,5·InfoNCE (τ = 0,07, 511 mẫu âm trong batch)"),
    ("Cải tiến B", "n = 0,5·Δ + u·ε; Δ = tâm ảnh − tâm văn bản trên 5.000 cặp COCO (‖Δ‖ = 13,87)"),
    ("Giao thức", "3 seed (12345, 2024, 7), checkpoint bước cuối, paired bootstrap 10.000 lần + Wilcoxon, kết luận khi p < 0,05"),
    ("Tài nguyên", "Kaggle 2 × T4 16 GB, 30 giờ GPU/tuần, giới hạn 12 giờ/phiên; 1,45 s/bước, 2,0 giờ/run"),
    ("Kết quả (TB 3 seed)", "FIQ R@10: baseline 25,90 · A 25,54 · B 26,50 · A+B 25,44; CIRCO mAP@5: 10,47 · 8,02 · 10,94 · 7,81"),
]

# ---------------------------------------------------------------- per member

MEMBERS = {
"Tam": {
    "name": "Đào Văn Tâm", "id": "B25CHHT112",
    "role": "Trình bày toàn bộ 16 slide (khoảng 15 phút) và điều phối hỏi đáp. Phần việc riêng: chuyển đổi mã nguồn LinCIR sang môi trường mới, kiểm chứng tương đương với mô hình gốc; vận hành thực nghiệm trên Kaggle: lập lịch chạy song song trong hạn mức GPU, khắc phục nghẽn nạp dữ liệu.",
    "slides": [("1", "Bìa, giới thiệu nhóm", "0:20"), ("2", "Phân công công việc", "0:30"), ("3", "Bài toán CIR, câu hỏi của nhóm", "1:00"), ("4", "Độ đo R@K, mAP@K (liên hệ chương I)", "1:00"), ("5", "Ý tưởng token giả", "0:50"), ("6", "Tóm tắt bài báo LinCIR", "1:00"), ("7", "Self-Masking Projection", "1:20"), ("8", "Nhiễu và modality gap", "1:00"), ("9", "Cải tiến A: InfoNCE (H1)", "1:00"), ("10", "Cải tiến B: nhiễu có hướng (H2, H3)", "1:00"), ("11", "Dựng mã nguồn, chạy trên Kaggle", "1:00"), ("12", "Tái hiện, khác biệt bài báo – mã nguồn", "0:50"), ("13", "Kết quả chính, kiểm định", "1:30"), ("14", "Vì sao: độ nhất quán của φ", "1:20"), ("15", "Kết luận H1–H3, ví dụ truy xuất", "1:20"), ("16", "Hỏi đáp", "—")],
    "theory": [
        ("Bộ mã hóa văn bản của CLIP", [
            "Câu → tokenizer BPE → chuỗi mã token (tối đa 77, bắt đầu 49406, kết thúc EOS 49407) → lớp nhúng token + nhúng vị trí → 12 khối Transformer có **mặt nạ nhân quả** (mỗi token chỉ nhìn các token phía trước) → LayerNorm cuối → lấy vector tại vị trí EOS → phép chiếu tuyến tính → vector văn bản z_c (768 chiều với ViT-L).",
            "Vị trí EOS được tìm bằng argmax của mã token vì 49407 là mã lớn nhất trong câu. Do mặt nạ nhân quả, các token đệm phía sau EOS không ảnh hưởng tới kết quả.",
            "LinCIR chèn token giả bằng cách: ở mọi vị trí có mã 259 (ký tự “$”), thay vector nhúng token bằng ê = φ(·) trước khi đi qua các khối Transformer.",
        ]),
        ("Vì sao phải viết lại", [
            "Mã gốc gọi hàm nội bộ text_model.encoder(..., causal_attention_mask=...) của transformers 4.34; ở transformers 5.x tham số này không còn. Nhóm viết lại lượt truyền xuôi từ các mô-đun con có tên ổn định qua các phiên bản: layer_norm1, q/k/v/out_proj, layer_norm2, mlp, với scaled_dot_product_attention(is_causal=True).",
            "Gói clip của OpenAI (chỉ dùng clip.tokenize) khó cài trên Python ≥ 3.13 → thay bằng tokenizer CLIP của HuggingFace (cùng bảng từ vựng BPE, “$” vẫn là mã 259).",
        ]),
        ("Kiểm chứng tương đương (cách chứng minh “đúng”)", [
            "So vector của encoder viết lại với CLIPTextModelWithProjection gốc trên cùng câu (không có token giả): sai lệch tuyệt đối lớn nhất **0,00** trên ViT-B/32 (Mac) và ViT-L/14 (GPU Kaggle) — scripts/check_encoder_equivalence.py.",
            "Token “$” = 259 ở cả tokenizer đánh giá và tokenizer huấn luyện (“[$]” thêm vào tokenizer SDXL có mã 49408, được đổi thành 259).",
            "Checkpoint chính thức nạp khớp hoàn toàn (strict) và tái hiện FashionIQ lệch ≤ 0,77 điểm so với bài báo; chạy đánh giá hai lần cho thứ hạng từng truy vấn giống hệt.",
            "Các lỗi đã sửa trong mã gốc: gõ nhầm arg → args khi cắt gradient; truyền biến chưa định nghĩa khi đánh giá CIRCO; ép .half() gây lỗi trên CPU/MPS; ghi tham số list/None vào TensorBoard làm crash trên Kaggle.",
        ]),
        ("Vận hành trên Kaggle", [
            "Mỗi phiên tối đa 12 giờ, hạn mức 30 giờ GPU/tuần **tính theo giờ phiên** (đã kiểm chứng: 2:25 → 8:43 sau phiên 6,3 giờ dù dùng 2 GPU).",
            "Chạy 2 run song song, mỗi run 1 T4 với batch 512 (bộ nhớ đỉnh 11,4/15 GB). Không dùng 2 GPU cho 1 run vì khi đó InfoNCE chỉ thấy 256 mẫu âm mỗi GPU → khác cấu hình giữa các biến thể.",
            "Bộ lập lịch tự **ước lượng thời gian** run (học từ run đã xong) và không bắt đầu run mới nếu không kịp trước 11,3 giờ → không bao giờ bị Kaggle cắt giữa chừng và mất output. Mỗi phiên tự “mang theo” checkpoint, dữ liệu đánh giá của phiên trước (carry-forward).",
        ]),
        ("Khắc phục nghẽn nạp dữ liệu", [
            "Triệu chứng: chạy song song 4,5 giây/bước (dự kiến ~2,4) → 6,2 giờ/run. Đo trên caption thật: spaCy tốn 4,7 ms/câu, tokenizer 0,1 ms → GPU chờ CPU (Kaggle chỉ 4 vCPU cho 2 run).",
            "Giải pháp: spaCy xử lý theo lô (nlp.pipe) và bỏ thành phần NER, lemmatizer (không ảnh hưởng nhãn từ loại) → 1,51 ms/câu (nhanh ×3,1).",
            "Bằng chứng không đổi kết quả: từ khóa giống hệt trên 3.000 câu thật; DataLoader cùng seed cho các batch giống hệt từng token với mã cũ. Phương án bỏ cả parser bị loại vì làm khác kết quả ở 48/1.536 câu.",
            "Tốc độ sau tối ưu: **1,45 giây/bước khi 2 run song song** (2,0 giờ/run, trước đó 6,2 giờ) → 8 run trong một phiên thay vì 2.",
        ]),
    ],
    "files": ["code/encode_with_pseudo_tokens.py, code/compat.py — encoder viết lại, tokenizer thay thế",
              "scripts/check_encoder_equivalence.py — kiểm chứng sai lệch 0",
              "code/loader.py (CaptionDataset.collate) — spaCy theo lô",
              "scripts/run_experiment.py, scripts/kaggle_jobs.py, notebooks/kaggle_lincir.ipynb — chạy thí nghiệm, lập lịch, carry-forward",
              "docs/decisions.md — lý do của từng quyết định"],
    "script": [
        ("1", 'Giới thiệu đề tài, môn học, giảng viên và 5 thành viên; nói rõ Tâm trình bày, cả nhóm cùng trả lời câu hỏi.'),
        ("2", "Đọc bảng phân công: mỗi thành viên phụ trách một phần (Tâm: mã nguồn, Kaggle; Trung: cải tiến A, đường học; Tùng: tái hiện; Dũng: đánh giá, kiểm định, cải tiến B; Nou: lý thuyết, định tính, slides). Nói rõ khi hỏi đáp sẽ mời người phụ trách trả lời."),
        ("3", 'Bài toán CIR qua ví dụ chiếc váy: ảnh tham chiếu + câu “is shiny and silver with shorter sleeves” → ảnh đích; câu chỉ mô tả phần thay đổi. Bộ ba gán nhãn đắt và ít (46,6 nghìn, 28,8 nghìn) nên cần zero-shot. Bài báo LinCIR giải bài toán này chỉ bằng văn bản. Nêu câu hỏi của nhóm: sửa hàm mất mát (A) hay sửa nhiễu (B) có giúp LinCIR tốt hơn không.'),
        ("4", 'Liên hệ chương I: CIR vẫn là truy xuất có xếp hạng. R@K = tỉ lệ truy vấn có ảnh đích trong K kết quả đầu (FashionIQ, 1 ảnh đúng). AP@K = Σ P@k·rel(k) / min(K, số ảnh đúng), mAP@K = trung bình trên truy vấn (CIRCO, nhiều ảnh đúng). Khác chương I: so khớp vector bằng cosine thay vì khớp từ. Giao thức: FashionIQ val, CIRCO val, kiểm định bootstrap và Wilcoxon theo từng truy vấn.'),
        ("5", 'Ý tưởng chung của ZS-CIR dùng token giả: ảnh tham chiếu → bộ mã hóa ảnh → φ → token [$]; ghép vào “a photo of [$] that …” → bộ mã hóa văn bản → vector truy vấn → xếp hạng theo cosine. Chỉ học φ, CLIP giữ nguyên. Lần đầu nói: “ký hiệu đô-la trong ngoặc vuông là token giả”.'),
        ("6", 'Tóm tắt bài báo (Gu et al., NAVER, CVPR 2024). Vấn đề: Pic2Word, SEARLE cần ảnh khi huấn luyện, chỉ học câu mẫu cố định. Ý tưởng: Self-Masking Projection học φ chỉ từ văn bản, thêm nhiễu cho modality gap. Kết quả bài báo: tốt nhất 4 bộ đánh giá, nhanh hơn Pic2Word 6 lần, SEARLE 8,4 lần, vượt phương pháp có giám sát trên FashionIQ. Chuyển sang hai thành phần.'),
        ("7", 'SMP: câu x_c → z_c; φ(z_c) → token ê_c; che tính từ và danh từ bằng [$], thay [$] bằng ê_c, mã hóa lại được ẑ_c; huấn luyện φ để ẑ_c gần z_c (MSE). Ví dụ “gray cat sleeps on a pillow” → “[$] sleeps on [$]”: [$] học bản tóm tắt một từ của câu.'),
        ("8", 'Modality gap: tâm ảnh và tâm văn bản cách nhau 0,82; ảnh và chú thích của chính nó chỉ có cosine 0,26. φ học trên văn bản nhưng suy luận nhận vector ảnh, nên LinCIR thêm nhiễu u·ε, u ~ U(0,1), ε ~ N(0,I), để φ chịu được độ lệch. Đây là thành phần B sẽ sửa.'),
        ("9", 'Cải tiến A sửa hàm mất mát: MSE chỉ kéo câu đã che về câu gốc, không phạt khi nó cũng gần câu khác, trong khi đánh giá là xếp hạng. L = L_SMP + 0,5·InfoNCE, 511 mẫu âm trong batch, τ = 0,07; chi phí +2%/bước. Giả thuyết H1: A tăng R@K, mAP@K. Chưa nói kết quả.'),
        ("10", 'Cải tiến B sửa nhiễu: u·ε đều theo mọi hướng, không dịch về phía vùng ảnh. n = 0,5·Δ + u·ε, Δ = tâm ảnh − tâm văn bản trên 5.000 cặp COCO val2017 (‖Δ‖ = 13,87), khác tập đánh giá nên không rò rỉ. H2: φ nhất quán hơn giữa ảnh và văn bản nên R@K, mAP@K tăng. H3: A+B sửa hai thành phần khác nhau nên có thể cộng hưởng.'),
        ("11", 'Mã gốc viết cho transformers 4.34: viết lại encoder văn bản, thay tokenizer, sửa 4 lỗi; sai lệch 0,00 với CLIP gốc trên ViT-B/32 và ViT-L/14. Thực nghiệm: baseline, A, B, A+B × 3 seed, 5.000 bước, chỉ khác thành phần cải tiến; 2 GPU T4 trên Kaggle (12 giờ/phiên, 30 giờ/tuần); nạp dữ liệu nhanh gấp 3,1 lần, kết quả giống hệt.'),
        ("12", 'Đánh giá checkpoint chính thức bằng mã đã chuyển đổi: lệch tối đa 0,77 điểm, R@10 trung bình 26,35 so với 26,28 của bài báo. Ba khác biệt: φ không có LayerNorm, thêm prompt Midjourney, từ khóa gồm cả mạo từ; nhóm theo mã vì mã tạo ra số liệu công bố.'),
        ("13", 'So với baseline nhóm tự huấn luyện, không so với bài báo. B cao nhất ở mọi cột: R@10 +0,60 (p = 0,006), R@50 +1,27 (p < 0,001); B 5.000 bước vượt checkpoint chính thức 20.000 bước. A và A+B kém hơn trên CIRCO, khoảng tin cậy nằm dưới 0. Độ lệch chuẩn qua seed nhỏ (≤ 0,5).'),
        ("14", 'Cosine giữa φ(ảnh) và φ(văn bản) của cùng cặp: B 0,84 > chính thức 0,81 > baseline 0,80 > A+B 0,69 > A 0,64, trùng thứ tự CIRCO mAP@5. InfoNCE buộc [$] mang đặc trưng phân biệt câu văn bản, không chuyển được sang ảnh. Đường học: A thấp hơn baseline ở mọi mốc.'),
        ("15", 'Ví dụ FashionIQ: B xếp đúng ảnh đích hạng 1; nhiều ảnh trong top-5 đúng phần lớn yêu cầu nhưng không được gán nhãn (âm tính giả). Kết luận: H2 được ủng hộ, H1 và H3 bị bác bỏ. Đóng góp: dựng lại mã, tái hiện, hai cải tiến, kiểm định, phân tích cơ chế. Hạn chế: 5.000 bước, chưa quét λ, α, chưa có CIRR, CIRCO test; hướng C theo IDF.'),
        ("16", 'Mời câu hỏi; nghe hết câu hỏi rồi trả lời hoặc mời người phụ trách: phương pháp, cải tiến A → Trung; tái hiện, bảng kết quả → Tùng; độ đo, kiểm định, cải tiến B, cơ chế → Dũng; bài toán, lý thuyết, ví dụ định tính → Nou; mã nguồn, Kaggle → Tâm.'),
    ],
    "qa": [
        ("Làm sao chắc encoder viết lại cho kết quả giống bản gốc?", "So trực tiếp vector đầu ra với CLIPTextModelWithProjection gốc trên cùng đầu vào: sai lệch lớn nhất 0,00 trên cả ViT-B/32 và ViT-L/14. Thêm vào đó, checkpoint chính thức tái hiện khớp bài báo (lệch ≤ 0,77 điểm) và đánh giá lặp lại cho thứ hạng từng truy vấn giống hệt."),
        ("Vì sao lấy vector tại EOS bằng argmax?", "EOS có mã 49407, lớn nhất trong bảng từ, nên argmax của dãy mã chính là vị trí EOS. Mặt nạ nhân quả làm các token đệm sau EOS không ảnh hưởng."),
        ("Tại sao chỉ 5.000 bước, có làm sai lệch kết luận không?", "20.000 bước trên T4 ≈ 13 giờ/run, vượt giới hạn phiên 12 giờ và hạn mức tuần. Mọi biến thể cùng 5.000 bước nên so sánh vẫn công bằng; số tuyệt đối có thể thấp hơn checkpoint 20.000 bước. Đường học (slide 14, Trung phân tích): R@10 chỉ tăng 0,25 điểm từ 4.000 đến 5.000 bước; baseline 5.000 bước kém checkpoint 20.000 bước 0,45 điểm R@10 và gần bằng trên CIRCO (10,47 so với 10,50)."),
        ("Chạy 2 run song song có ảnh hưởng kết quả?", "Không: mỗi run một GPU riêng, cùng cấu hình; chỉ ảnh hưởng tốc độ. Kết quả phụ thuộc seed và dữ liệu, không phụ thuộc việc chạy cùng lúc."),
        ("Bỏ NER và lemmatizer có đổi dữ liệu huấn luyện không?", "Không. Hai thành phần này không ghi nhãn từ loại mà LinCIR dùng để chọn từ khóa. Đã kiểm tra từ khóa giống hệt trên 3.000 câu thật và batch giống hệt từng token với mã cũ. Riêng parser thì có ảnh hưởng nên được giữ lại."),
        ("Tại sao không dùng 2 GPU cho 1 run cho nhanh?", "Huấn luyện phân tán chia batch 512 thành 2 × 256; InfoNCE (cải tiến A) chỉ thấy mẫu âm trên GPU của mình → khác cấu hình với baseline. Chạy 2 run độc lập giữ batch 512 cho mọi biến thể."),
        ("fp16 có làm khác kết quả so với bài báo?", "Mã gốc cũng huấn luyện fp16. Khi đánh giá nhóm dùng fp32 như mã validate gốc; tái hiện khớp bài báo."),
    ],
    "check": ["Vẽ lại được luồng: câu → token → nhúng → (thay [$]) → Transformer nhân quả → EOS → chiếu.",
              "Giải thích vì sao sai lệch 0 là bằng chứng đủ mạnh, và còn những bằng chứng nào khác.",
              "Nói được tốc độ trước/sau tối ưu và vì sao kết quả không đổi.",
              "Giải thích cách tính hạn mức Kaggle và cơ chế không để phiên bị cắt."],
    "read": ["Báo cáo: toàn bộ chương 1–6 (trình bày tất cả các phần); docs/decisions.md", "Bài báo LinCIR: Tóm tắt (Abstract), mục 1 (đóng góp), 3.1, 4.1", "CLIP (Radford 2021): mục 2.3 (kiến trúc encoder văn bản)", "README.md: bảng kết quả cần nhớ (nắm chắc trước khi trình bày slide 13–15)"],
},
"Trung": {
    "name": "Lâm Thành Trung", "id": "B25CHHT117",
    "role": "Đề xuất và cài đặt cải tiến A (bổ sung InfoNCE vào SMP); phân tích đường học theo số bước huấn luyện.",
    "slides": [("7", "Self-Masking Projection", "Tâm trình bày"), ("9", "Cải tiến A: InfoNCE (H1)", "Tâm trình bày"), ("14", "Vì sao: độ nhất quán của φ", "Tâm trình bày")],
    "theory": [
        ("Token giả (textual inversion)", [
            "Biểu diễn một ảnh như một “từ” [$] trong không gian token của CLIP; ghép vào câu “a photo of [$] that {điều chỉnh}”, bộ mã hóa văn bản tự “hiểu” ảnh và phần thay đổi, tạo vector truy vấn để tìm ảnh. Cần học mạng chiếu φ: vector → token.",
            "Pic2Word học φ bằng cách đối sánh vector ảnh với vector của “a photo of [$]”; SEARLE tối ưu token cho từng ảnh rồi chưng cất. Hạn chế: chỉ thấy câu mẫu cố định → kém với câu điều chỉnh phức tạp, giảm khi backbone lớn; phải chạy bộ mã hóa ảnh khi train.",
        ]),
        ("Self-Masking Projection (SMP)", [
            "z_c = C(câu); ê = φ(z_c + n); che các cụm tính từ/danh từ bằng [$] → “[$] sleeps on [$]”; ẑ_c = C(câu đã che với [$] = ê); mất mát L_SMP = ‖z_c − ẑ_c‖².",
            "Trực giác: để câu đã che giữ nguyên nghĩa, [$] phải tóm tắt nội dung thiết yếu (“tóm tắt một từ”). Văn bản tự nhiên đa dạng → φ học được trong nhiều cấu trúc câu.",
            "Nhiễu n = u·ε, u ~ U(0,1), ε ~ N(0, I): chuẩn của nhiễu đa dạng (Gauss thuần trong 768 chiều có chuẩn gần như cố định ≈ 27,7). Mục đích: φ chịu được việc thay vector văn bản bằng vector ảnh khi suy luận (modality gap).",
        ]),
        ("Học đối sánh và InfoNCE", [
            "Với batch B câu, chuẩn hóa L2 ẑ và z; ma trận độ tương đồng S = ẑ zᵀ / τ (B × B). Đường chéo là cặp đúng, phần còn lại là mẫu âm.",
            "InfoNCE = entropy chéo của từng hàng với nhãn là đường chéo: −log( e^{S_ii} / Σ_j e^{S_ij} ). Bản đối xứng lấy trung bình theo hàng và theo cột.",
            "τ (nhiệt độ) điều khiển độ “sắc” của phân phối; τ = 0,07 là giá trị khởi tạo của chính CLIP. Batch 512 → mỗi câu có 511 mẫu âm.",
        ]),
        ("Cải tiến A — lập luận", [
            "MSE chỉ kéo ẑ về z của chính câu đó, không phạt ẑ gần vector các câu khác; bài toán đánh giá là **xếp hạng** (ảnh đích phải đứng trên mọi ảnh khác) → cần tính phân biệt.",
            "InfoNCE tối ưu theo cosine như khi truy xuất và đẩy các câu khác ra xa; giữ MSE để bảo toàn chuẩn và vị trí tuyệt đối của vector (InfoNCE chỉ quan tâm hướng).",
            "L = L_SMP + λ·L_NCE, λ = 0,5. Chi phí: ẑ, z đã có sẵn; phép nhân 512 × 512 nhỏ → thời gian/bước chỉ tăng ~2% khi huấn luyện thật (1,474 so với 1,448 giây).",
            "Hiện thực: code/train_phi.py, cờ --infonce_weight, --infonce_temp (mặc định 0 = LinCIR gốc).",
        ]),
        ("Đường học", [
            "Đánh giá các checkpoint 1.000–4.000 bước và bước cuối 5.000 của baseline và A (seed 12345) trên FashionIQ; vẽ R@10/R@50 theo số bước (results/figures/learning_curve.png).",
            "Đọc đồ thị: nếu đường còn tăng rõ ở 5.000 → chưa bão hòa, số tuyệt đối còn có thể cao hơn; nếu khoảng cách A − baseline ổn định theo số bước → cải tiến không phụ thuộc may rủi của điểm dừng. Kết quả: baseline tăng nhanh tới 2.000 bước rồi chậm lại (+0,25 điểm R@10 từ 4.000 đến 5.000); **A thấp hơn baseline trên R@10 ở mọi mốc** → A kém không phải do chọn điểm dừng.",
        ]),
    ],
    "files": ["code/train_phi.py — hàm mất mát (tìm comment # [NHOM8] Improvement A)", "configs/EXP-002-infonce.yaml", "results/figures/learning_curve.png (sau phiên eval)"],
    "script": [
        ("7", 'Mở đầu phần phương pháp: Pic2Word/SEARLE cần ảnh khi huấn luyện và chỉ học câu mẫu cố định (ảnh CC3M 430 GB, chú thích 125 MB). LinCIR thay ảnh bằng chính câu văn: che từ khóa bằng [$] = φ(z_c), ép ẑ_c ≈ z_c. Giải thích ví dụ “[$] sleeps on [$]” và vì sao [$] học được “tóm tắt một từ”.'),
        ("9", 'Cải tiến A sửa trực tiếp hàm mất mát vừa trình bày. Vấn đề: MSE không phân biệt, trong khi đánh giá là xếp hạng. Giải pháp: + λ·InfoNCE với 511 mẫu âm, τ = 0,07. Chi phí chỉ +2%/bước. Kết quả: A không tốt hơn trên FashionIQ (R@10 25,54 so với 25,90) và giảm CIRCO mAP@5 2,45 điểm — nói thẳng H1 bị bác bỏ; nguyên nhân ở slide 14 (Dũng hỗ trợ trả lời).'),
    ],
    "qa": [
        ("Kỳ vọng InfoNCE giúp xếp hạng, sao kết quả lại kém hơn?", "Kỳ vọng: InfoNCE tối ưu cosine với cặp đúng so với 511 câu khác, đúng thứ được đo khi truy xuất. Thực tế: độ nhất quán φ(ảnh)–φ(văn bản) giảm từ 0,80 xuống 0,64. InfoNCE buộc [$] mang đặc trưng giúp **phân biệt các câu văn bản**; đặc trưng này gắn với miền văn bản, không chuyển sang vector ảnh → φ khớp quá mức với văn bản, mất khả năng tổng quát qua modality gap. Ảnh hưởng nặng trên CIRCO (ảnh đời thực đa dạng) hơn FashionIQ."),
        ("Cải tiến của bạn thất bại, vậy đóng góp ở đâu?", "Đây là kết quả âm có kiểm định rõ (KTC 95% của CIRCO mAP@5 nằm hoàn toàn dưới 0) và có giải thích cơ chế. Nó cho thấy nút thắt của LinCIR là tính nhất quán qua modality gap, không phải tính phân biệt giữa các câu — chính phát hiện này dẫn tới kết luận chung của nhóm và giải thích vì sao B thành công. Hướng thử tiếp: λ nhỏ hơn, hoặc đối sánh có cả vector ảnh."),
        ("Sao không bỏ hẳn MSE?", "InfoNCE chỉ ràng buộc hướng (sau chuẩn hóa). MSE giữ chuẩn và vị trí tuyệt đối để [$] vẫn là một token “hợp lệ” cho bộ mã hóa; bỏ MSE có nguy cơ [$] trôi khỏi phân phối token thật."),
        ("τ = 0,07 và λ = 0,5 chọn thế nào?", "τ = 0,07 là nhiệt độ khởi tạo của CLIP; λ = 0,5 cân bằng hai số hạng ở cùng bậc độ lớn. Không quét vì giới hạn GPU — đã ghi là hạn chế."),
        ("Có mẫu âm giả (hai câu gần như giống nhau trong batch) không?", "Có thể nhưng hiếm với batch 512 lấy ngẫu nhiên từ hàng triệu câu; ảnh hưởng nhỏ. Đây cũng là hạn chế chung của InfoNCE trong batch."),
        ("Khác gì mất mát đối sánh của Pic2Word?", "Pic2Word đối sánh vector ảnh với vector câu mẫu “a photo of [$]”. Cải tiến A đối sánh câu đã che với câu gốc — hoàn toàn bằng văn bản, giữ ưu điểm của LinCIR."),
        ("Batch nhỏ hơn thì sao?", "Ít mẫu âm hơn → tín hiệu đối sánh yếu hơn. Vì vậy nhóm giữ batch 512 trên 1 GPU thay vì chia 2 GPU."),
        ("Đường học cho thấy gì về 5.000 bước?", "Hiệu năng tăng nhanh tới 2.000 bước rồi chậm lại (+0,25 điểm R@10 từ 4.000 đến 5.000); baseline 5.000 bước chỉ kém checkpoint 20.000 bước 0,45 điểm. A thấp hơn baseline ở mọi mốc R@10 nên kết luận về A không phụ thuộc điểm dừng."),
    ],
    "check": ["Viết được L_SMP và L_NCE, giải thích từng ký hiệu.", "Giải thích bằng lời vì sao MSE không đủ cho bài toán xếp hạng.",
              "Đọc được đồ thị đường học và kết luận về 5.000 bước.", "Trả lời câu hỏi về τ, λ, batch, mẫu âm."],
    "read": ["Báo cáo: mục 2.5, 3.2–3.4, 4.1–4.2, 5.7", "Bài báo LinCIR: mục 3.1–3.2, Bảng 8–9", "van den Oord 2018 (InfoNCE): mục 2", "Pic2Word (Saito 2023), SEARLE (Baldrati 2023): phần phương pháp"],
},
"Tung": {
    "name": "Nguyễn Xuân Tùng", "id": "B25CHHT119",
    "role": "Tái hiện: đánh giá checkpoint chính thức, đối chiếu với bài báo; phân tích khác biệt giữa bài báo và mã nguồn (cấu trúc φ, dữ liệu huấn luyện, trích từ khóa).",
    "slides": [("6", "Tóm tắt bài báo LinCIR", "Tâm trình bày"), ("12", "Tái hiện, khác biệt bài báo – mã nguồn", "Tâm trình bày"), ("13", "Kết quả chính, kiểm định", "Tâm trình bày"), ("15", "Kết luận H1–H3, ví dụ truy xuất", "Tâm trình bày")],
    "theory": [
        ("Giao thức đánh giá FashionIQ", [
            "Tập val: dress 2.017, shirt 2.038, toptee 1.961 truy vấn; kho ảnh tương ứng 3.817 / 6.346 / 5.373. Mỗi truy vấn có hai câu điều chỉnh, ghép “c1 and c2” và “c2 and c1”, mã hóa “a photo of [$] that …” cho cả hai thứ tự rồi lấy trung bình vector.",
            "Recall@K: tỷ lệ truy vấn có ảnh đích trong K kết quả đầu (K = 10, 50); báo cáo từng nhóm và trung bình (TB).",
        ]),
        ("Kết quả tái hiện (checkpoint chính thức, ViT-L)", [
            "Dress 21,32 / 42,19 (bài báo 20,92 / 42,44); Shirt 28,70 / 46,76 (29,10 / 46,81); Toptee 29,02 / 49,41 (28,81 / 50,18); TB 26,35 / 46,12 (26,28 / 46,49). Lệch lớn nhất 0,77 điểm.",
            "Nguyên nhân lệch nhỏ: khác phiên bản thư viện/tokenizer, số học dấu phẩy động, ảnh FashionIQ từ bản sao HuggingFace (đủ 15.415/15.415 ảnh cần thiết). Đánh giá hai lần cho thứ hạng từng truy vấn giống hệt → quy trình ổn định.",
            "CIRCO val: mAP@5 = 10,50, mAP@10 = 12,22. Bài báo chỉ công bố tập test (12,59 / 13,58) — tập test chấm trên máy chủ, đáp án không công khai → không so trực tiếp; số val dùng làm mốc cho các biến thể.",
        ]),
        ("Khác biệt bài báo – mã nguồn", [
            "**Cấu trúc φ:** bài báo ghi LN–Linear–GELU–Linear–GELU–Linear–LN, nhưng mã và checkpoint công bố **không có LayerNorm** (checkpoint nạp khớp tuyệt đối vào MLP không LN) → số liệu trong bài báo đến từ mô hình không LN.",
            "**Dữ liệu huấn luyện:** bài báo nêu CC3M + 2,47 triệu prompt Stable Diffusion; mã nạp thêm bộ prompt Midjourney.",
            "**Trích từ khóa:** mã giữ cả từ hạn định (DET, ví dụ “a”, “the”) trong cụm từ khóa.",
            "**Chọn checkpoint:** mã chọn theo R@1 trên CIRR dev; nhóm không có CIRR nên dùng checkpoint bước cuối cho mọi biến thể (không chọn trên tập báo cáo).",
            "Nhóm giữ hành vi của mã nguồn cho baseline vì đây là cấu hình sinh ra checkpoint công bố.",
        ]),
        ("Baseline nhóm tự chạy vs checkpoint chính thức", [
            "Baseline của nhóm: 5.000 bước (bài báo 20.000), checkpoint bước cuối. Khoảng cách với checkpoint chính thức: FashionIQ R@10 25,90 so với 26,35 (−0,45), CIRCO mAP@5 10,47 so với 10,50 — gần như bằng. Ý nghĩa: cho biết ảnh hưởng của việc rút ngắn huấn luyện; mọi so sánh cải tiến là với baseline cùng cấu hình, không với số của bài báo.",
        ]),
    ],
    "files": ["experiments/runs/EXP-000-official-s0/ — metrics.json, per_query_*.csv", "scripts/eval_per_query.py — đánh giá (FashionIQ, CIRCO)", "code/models.py (lớp Phi), code/loader.py (build_loader, extract_keywords_spacy)"],
    "script": [
        ("12", 'Trước khi cải tiến phải chắc đường ống đúng: đánh giá checkpoint chính thức bằng mã đã chuyển đổi. Bảng: lệch tối đa 0,77 điểm, TB R@10 +0,07. Nêu 3 khác biệt bài báo–mã nguồn và vì sao nhóm theo mã. CIRCO val là mốc tham chiếu.'),
        ("13", 'So với baseline nhóm tự chạy (không so với bài báo). Bảng kết quả (mean ± std, 3 seed) và bảng kiểm định (Δ, KTC 95%, p bootstrap, p Wilcoxon). Kết luận: B tốt hơn có ý nghĩa trên FashionIQ R@10 (+0,60, p = 0,006), R@50 (+1,27, p < 0,001) và CIRCO mAP@25/50; mAP@5/10 chưa đủ bằng chứng (chỉ 220 truy vấn). A và A+B kém trên CIRCO (KTC nằm dưới 0).'),
        ("15", 'Kết luận: H2 (B) được ủng hộ, H1 (A) và H3 (A+B) bị bác bỏ; tính nhất quán của φ qua modality gap quyết định chất lượng truy xuất. Hạn chế: 5.000 bước, không quét λ/α, không có CIRR, CIRCO chỉ val. Hướng phát triển: đủ 20.000 bước, quét tham số, CIRR + CIRCO test, hướng C (IDF).'),
    ],
    "qa": [
        ("Lệch 0,77 điểm có đáng lo không?", "Không: cùng bậc với nhiễu do khác phiên bản thư viện và ảnh bản sao; có nhóm lệch dương, nhóm lệch âm, trung bình R@10 chỉ +0,07. Quan trọng là đường ống tái lập được (chạy lại giống hệt) và khớp bài báo."),
        ("Ảnh FashionIQ lấy từ bản sao có đáng tin?", "Đủ 15.415/15.415 ảnh cần cho tập val, mã ảnh khớp danh sách chính thức, và kết quả tái hiện khớp bài báo — nếu ảnh sai, R@K sẽ lệch lớn."),
        ("Bài báo có LayerNorm mà code không — vậy tái hiện cái nào?", "Checkpoint công bố không có LN và cho đúng số trong bài báo → bài báo mô tả chưa chính xác. Nhóm tái hiện đúng mô hình đã tạo ra số liệu."),
        ("Vì sao không so CIRCO với bài báo?", "Bài báo báo cáo tập test (chấm trên máy chủ); nhóm chỉ có đáp án tập val. Hai tập khác truy vấn nên không so trực tiếp."),
        ("Baseline 5.000 bước thấp hơn checkpoint chính thức thì kết luận còn giá trị?", "Có, vì so sánh cải tiến luôn là cùng cấu hình (cùng 5.000 bước, cùng dữ liệu, cùng seed). Khoảng cách với checkpoint chính thức chỉ nói về số bước, không về cải tiến."),
        ("Bỏ CIRR có ảnh hưởng gì?", "Không ảnh hưởng tính hợp lệ: vẫn có hai bộ ở hai lĩnh vực (thời trang, ảnh đời thực); bài báo cũng nhận xét CIRR nhiều nhiễu. Hạn chế là không đối chiếu được Bảng 6 của bài báo."),
    ],
    "check": ["Nói được bảng tái hiện từ trí nhớ (ít nhất TB R@10, R@50 và mức lệch).", "Giải thích giao thức FashionIQ (hai câu, hai thứ tự).",
              "Nêu đủ 3 khác biệt bài báo–mã nguồn và hệ quả.", "Phân biệt so với bài báo (tái hiện) và so với baseline (cải tiến)."],
    "read": ["Báo cáo: mục 3.5, 5.2, 5.4, 5.5, 5.6, chương 6, Kết luận", "Bài báo LinCIR: Bảng 3, 5, 6 và mục 4.2", "FashionIQ (Wu 2021), CIRCO trong SEARLE (Baldrati 2023)", "results/tables/main_results.md, significance.md (hỏi Dũng cách đọc p-value, KTC)"],
},
"Dung": {
    "name": "Trần Quang Đức Dũng", "id": "B25CHHT088",
    "role": "Thiết kế giao thức đánh giá theo truy vấn (R@K, mAP@K) và kiểm định thống kê (paired bootstrap, Wilcoxon); cài đặt cải tiến B (nhiễu có hướng) và phân tích modality gap.",
    "slides": [("4", "Độ đo R@K, mAP@K (liên hệ chương I)", "Tâm trình bày"), ("8", "Nhiễu và modality gap", "Tâm trình bày"), ("10", "Cải tiến B: nhiễu có hướng (H2, H3)", "Tâm trình bày"), ("13", "Kết quả chính, kiểm định", "Tâm trình bày"), ("14", "Vì sao: độ nhất quán của φ", "Tâm trình bày")],
    "theory": [
        ("Độ đo", [
            "Recall@K (FashionIQ, 1 ảnh đúng/truy vấn): tỷ lệ truy vấn có ảnh đích trong top-K. Liên hệ chương I: Recall = |liên quan ∩ truy xuất| / |liên quan|, áp dụng cho K kết quả đầu.",
            "AP@K (CIRCO, nhiều ảnh đúng, TB 4,16/truy vấn): AP@K = (1 / min(K, |G|)) · Σ_{k≤K} P@k · rel(k); mAP@K = trung bình trên truy vấn. Thưởng cho việc đặt nhiều ảnh đúng ở vị trí cao; bài báo coi mAP CIRCO là độ đo đáng tin nhất vì R@1 bị “âm tính giả”.",
            "Nhóm lưu **thứ hạng từng truy vấn** (per_query_*.csv) thay vì chỉ số tổng — điều kiện để kiểm định ghép cặp. Script mới cho mAP CIRCO trùng tuyệt đối hàm gốc của tác giả.",
        ]),
        ("Kiểm định ghép cặp theo truy vấn", [
            "Thiết kế ghép cặp: cùng một truy vấn được trả lời bởi baseline và biến thể → so sánh trên hiệu số từng truy vấn, loại bỏ độ khó khác nhau giữa các truy vấn. Mỗi truy vấn lấy trung bình qua 3 seed.",
            "**Paired bootstrap:** lấy mẫu có hoàn lại N truy vấn (10.000 lần), tính trung bình hiệu số Δ* mỗi lần; p (một phía) = tỷ lệ Δ* ≤ 0; khoảng tin cậy 95% = phân vị 2,5% và 97,5% của Δ*.",
            "**Wilcoxon có dấu:** kiểm định phi tham số trên hiệu số từng truy vấn (bỏ hiệu bằng 0), không giả định phân phối chuẩn; dùng làm kiểm tra chéo.",
            "Kết luận “tốt hơn có ý nghĩa” khi Δ > 0 và p < 0,05; “chưa đủ bằng chứng” khi p ≥ 0,05; KTC 95% nằm hoàn toàn dưới 0 thì “kém hơn”.",
            "Vì sao không kiểm định trên 3 seed? Chỉ 3 điểm quá ít; ghép theo hàng nghìn truy vấn mạnh hơn nhiều. Độ lệch chuẩn qua seed vẫn được báo cáo để thấy độ ổn định.",
        ]),
        ("Modality gap và cải tiến B", [
            "Liang và cộng sự (2022): vector ảnh và văn bản của CLIP nằm ở hai “hình nón” tách biệt; đo bằng khoảng cách giữa tâm các vector đã chuẩn hóa. Trên 5.000 cặp COCO: khoảng cách tâm 0,821, cosine cặp ảnh–chú thích trung bình chỉ 0,256.",
            "Nhiễu LinCIR u·ε đẳng hướng: “làm mờ” vùng văn bản theo mọi hướng, không đưa đầu vào của φ về phía vùng ảnh. Cải tiến B: n = α·Δ + u·ε, Δ = tâm(vector ảnh) − tâm(vector văn bản) tính trên 5.000 cặp COCO val2017 (‖Δ‖ = 13,87), α = 0,5 — dịch phân phối đầu vào của φ về phía nơi nó sẽ gặp khi suy luận.",
            "COCO val2017 độc lập với tập đánh giá (CIRCO dùng COCO unlabeled2017) → không rò rỉ dữ liệu.",
            "Đo cơ chế: “độ nhất quán của φ” — mã hóa “a photo of [$]” với [$] = φ(vector văn bản) và [$] = φ(vector ảnh) của cùng cặp; cosine cao hơn / khoảng cách tâm nhỏ hơn nghĩa là φ xử lý ảnh giống như đã học với văn bản (results/figures/modality_gap.png). Kết quả: cosine B 0,84 > chính thức 0,81 ≈ baseline 0,80 > A+B 0,69 > A 0,64; khoảng cách tâm B 0,25 < baseline 0,29 < A 0,33 — **cùng thứ tự với CIRCO mAP@5**.",
        ]),
    ],
    "files": ["scripts/eval_per_query.py — thứ hạng từng truy vấn, mAP CIRCO", "scripts/stats_compare.py, scripts/make_report_assets.py — kiểm định, bảng, hình",
              "scripts/modality_gap.py — Δ, khoảng cách tâm, độ nhất quán φ", "code/train_phi.py (# [NHOM8] Improvement B), configs/EXP-003, EXP-004"],
    "script": [
        ("4", 'Liên hệ chương I: mô hình tìm kiếm cổ điển; Precision/Recall → R@K, mAP@K; tìm kiếm vector (xếp hạng theo cosine) khác mô hình Boolean khớp chính xác.'),
        ("10", 'Trước hết nhắc thành phần nhiễu của LinCIR: khi suy luận φ nhận vector ảnh, nhưng ảnh và văn bản của CLIP nằm ở hai vùng khác nhau (modality gap), nên LinCIR thêm nhiễu u·ε khi huấn luyện. Modality gap của CLIP: tâm ảnh và tâm văn bản cách nhau 0,82 (cosine cặp chỉ 0,26). Nhiễu của LinCIR đẳng hướng; B cộng thêm α·Δ để đưa đầu vào φ về phía vùng ảnh. Δ tính trên COCO độc lập với tập đánh giá.'),
        ("14", 'Vì sao: (1) độ nhất quán φ ảnh–văn bản theo biến thể; (2) đường học; (3) ví dụ top-5 thành công/thất bại (Nou chuẩn bị hình): độ nhất quán φ trùng thứ tự với CIRCO mAP@5; A thấp hơn baseline ở mọi mốc; ví dụ váy dài cúp ngực B xếp đúng hạng 1.'),
    ],
    "qa": [
        ("Vì sao dùng bootstrap thay vì t-test?", "Hiệu số theo truy vấn của Recall là 0/±1 (rời rạc), của AP lệch mạnh — không chuẩn. Bootstrap không giả định phân phối; Wilcoxon là kiểm tra chéo phi tham số."),
        ("p-value một phía có “dễ dãi” không?", "Giả thuyết có hướng (cải tiến tốt hơn) nên kiểm định một phía phù hợp; nhóm báo cáo thêm KTC 95% hai phía và Wilcoxon hai phía để người đọc tự đánh giá."),
        ("So nhiều chỉ số, nhiều biến thể — có vấn đề đa kiểm định?", "Có. Nhóm báo cáo đầy đủ mọi phép so sánh, không chọn lọc. Với 6 phép so sánh của B (ngưỡng 0,05/6 ≈ 0,0083), hai kết quả FashionIQ (p = 0,0055 và < 0,0001) vẫn có ý nghĩa; CIRCO mAP@25/50 (p = 0,028; 0,017) thì không. Nếu tính cả 18 phép (ngưỡng ≈ 0,0028), chỉ còn R@50."),
        ("Δ tính từ COCO, CIRCO cũng là COCO — có rò rỉ không?", "Không: Δ dùng COCO val2017 (có chú thích), CIRCO dùng COCO unlabeled2017 (tập ảnh khác). Δ chỉ là một vector hướng trung bình, không chứa thông tin truy vấn hay đáp án."),
        ("α = 0,5 chọn thế nào?", "Để phần dịch (‖0,5·Δ‖ ≈ 6,9) cùng bậc với độ lớn trung bình của nhiễu u·ε (≈ 13,9), tránh lấn át thành phần ngẫu nhiên. Không quét vì giới hạn GPU."),
        ("B chỉ tăng 0,6 điểm R@10 — có đáng kể không?", "Nhỏ về tuyệt đối nhưng rất ổn định (độ lệch chuẩn qua seed 0,04) và có ý nghĩa thống kê; R@50 tăng 1,27. B vượt cả checkpoint 20.000 bước chỉ với 5.000 bước và không tăng chi phí huấn luyện."),
        ("Có ý nghĩa thống kê nhưng Δ rất nhỏ thì sao?", "Phân biệt ý nghĩa thống kê và ý nghĩa thực tế: báo cáo cả độ lớn Δ, KTC 95% và so với độ lệch giữa các seed."),
    ],
    "check": ["Tự tay tính AP@5 cho một ví dụ nhỏ (3 ảnh đúng, danh sách 5 kết quả).", "Giải thích paired bootstrap bằng lời trong 30 giây.",
              "Đọc bảng kiểm định và nói kết luận cho từng biến thể.", "Giải thích Δ, α và vì sao không rò rỉ dữ liệu."],
    "read": ["Báo cáo: mục 2.1, 2.3, 3.3, 4.3, 5.3, 5.6, 5.7", "Liang 2022 (Mind the Gap): mục 2–3", "Efron & Tibshirani: chương về bootstrap; bài giảng chương I (Precision/Recall)"],
},
"Nou": {
    "name": "Mekdala Nounou", "id": "B25CHHT124",
    "role": "Tổng quan lý thuyết (CIR, ZS-CIR, CLIP, Pic2Word, SEARLE) và liên hệ với các độ đo IR; phân tích định tính; thiết kế slides thuyết trình.",
    "slides": [("3", "Bài toán CIR, câu hỏi của nhóm", "Tâm trình bày"), ("4", "Độ đo R@K, mAP@K (liên hệ chương I)", "Tâm trình bày"), ("5", "Ý tưởng token giả", "Tâm trình bày"), ("6", "Tóm tắt bài báo LinCIR", "Tâm trình bày"), ("15", "Kết luận H1–H3, ví dụ truy xuất", "Tâm trình bày")],
    "theory": [
        ("Truy xuất thông tin (chương I của môn học)", [
            "IR: tìm tài liệu (thường phi cấu trúc) thỏa nhu cầu thông tin từ bộ sưu tập lớn. Mô hình tìm kiếm cổ điển: nhiệm vụ → nhu cầu thông tin → truy vấn → máy tìm kiếm + bộ sưu tập → kết quả → tinh chỉnh truy vấn.",
            "Precision = tỷ lệ tài liệu truy xuất thực sự liên quan; Recall = tỷ lệ tài liệu liên quan đã được truy xuất. Với danh sách xếp hạng: Recall@K, Precision@K, AP/mAP.",
            "Mô hình Boolean + chỉ mục ngược: khớp chính xác, không xếp hạng. CLIP + tìm kiếm vector: mã hóa mọi ảnh thành vector, truy vấn thành vector, xếp hạng theo cosine — một mô hình truy xuất có xếp hạng.",
        ]),
        ("CIR và zero-shot CIR", [
            "CIR: truy vấn = ảnh tham chiếu + câu mô tả thay đổi; ví dụ FashionIQ: váy hoa xanh + “is shiny and silver with shorter sleeves”, “fit and flare” → váy bạc bóng.",
            "CIR có giám sát (TIRG, Combiner) học từ bộ ba có nhãn — đắt (FashionIQ ~46,6 nghìn, CIRR ~28,8 nghìn bộ ba), khó tổng quát. Zero-shot CIR không dùng bộ ba; huấn luyện trên dữ liệu sẵn có rồi đánh giá trực tiếp.",
        ]),
        ("CLIP, Pic2Word, SEARLE", [
            "CLIP: hai bộ mã hóa (ảnh, văn bản) học đối sánh trên 400 triệu cặp ảnh–văn bản → không gian chung; ảnh và câu mô tả của nó gần nhau.",
            "Pic2Word và SEARLE: học “từ giả” [$] đại diện cho ảnh, ghép vào câu; hạn chế là câu mẫu cố định và cần ảnh khi huấn luyện → LinCIR giải quyết bằng huấn luyện chỉ với văn bản (Trung trình bày tiếp).",
        ]),
        ("Phân tích định tính", [
            "Từ danh sách top-10 của từng truy vấn (topk_fiq_*.json), chọn ví dụ: (1) biến thể cải tiến đưa ảnh đích lên hạng 1 trong khi baseline không có trong top-5; (2) cả hai cùng thất bại.",
            "Đọc ví dụ: các ảnh xếp đầu có giữ đặc điểm của ảnh tham chiếu không, có áp dụng đúng thay đổi (màu, tay áo, kiểu dáng) không; thất bại thường do câu mơ hồ (“is the same”), thay đổi tinh tế, hoặc “âm tính giả” (ảnh đúng nhưng không được gán nhãn).",
            "Hình 5.3 (results/figures/qualitative_fiq_1.png): câu “is strapless with lighter colors” và “is lighter and blue and sleeveless”; B xếp đúng ảnh đích (váy dài cúp ngực, nền sáng) hạng 1, baseline trả về váy ngắn màu đậm, bỏ qua dáng váy và yêu cầu “sáng màu hơn”. Nhiều ảnh top-5 thỏa phần lớn điều kiện nhưng không phải ảnh đích được gán nhãn → âm tính giả.",
        ]),
        ("Thiết kế slides", [
            "16 slide, ~15 phút (slides/khung_slides.md). Mỗi slide một ý, ≤ 6 dòng; số liệu luôn có nguồn (bảng nào trong báo cáo); slide kết quả nêu cả p-value và KTC, không chỉ Δ.",
            "Dùng lại hình trong report/figures và results/figures; giữ một bảng màu, phông chữ thống nhất.",
        ]),
    ],
    "files": ["report/figures/cir_example.png — ví dụ CIR thật", "slides/khung_slides.md, slides/QA_du_kien.md", "results/figures/qualitative_fiq_*.png (sau phiên eval)", "Chapter_I.pdf (bài giảng): slide 6–8"],
    "script": [
        ("3", 'Kể ví dụ chiếc váy: ảnh tham chiếu + “màu bạc, tay ngắn hơn” → ảnh đích. Đây là truy xuất ảnh kết hợp, nhu cầu thông tin không diễn đạt trọn bằng chỉ chữ hay chỉ ảnh. Vì sao zero-shot: bộ ba phải gán nhãn tay, nhỏ (FashionIQ 46,6 nghìn, CIRR 28,8 nghìn) → mô hình có giám sát khó tổng quát → zero-shot không dùng bộ ba.'),
        ("5", 'Ý tưởng: ảnh → [$] trong không gian token; câu “a photo of [$] that …” → vector truy vấn → tìm ảnh. Chỉ cần học φ. Đây là ý tưởng chung của các phương pháp zero-shot.'),
    ],
    "qa": [
        ("CIR khác tìm ảnh bằng văn bản thế nào?", "Văn bản trong CIR chỉ mô tả phần thay đổi, không mô tả toàn bộ ảnh đích; hệ thống phải giữ đặc điểm của ảnh tham chiếu và áp dụng thay đổi."),
        ("Tại sao gọi là zero-shot?", "Không dùng bất kỳ bộ ba CIR có nhãn nào khi huấn luyện; mô hình được đánh giá trực tiếp trên FashionIQ, CIRCO."),
        ("Recall@K khác Precision thế nào, sao CIRCO dùng mAP?", "FashionIQ chỉ có 1 ảnh đúng → quan tâm ảnh đó có trong top-K (Recall@K). CIRCO có nhiều ảnh đúng → mAP@K đánh giá cả số lượng và vị trí của các ảnh đúng."),
        ("Tìm kiếm vector khác chỉ mục ngược thế nào?", "Chỉ mục ngược tra danh sách tài liệu chứa từ, khớp chính xác (Boolean). Tìm kiếm vector so độ tương đồng liên tục (cosine) giữa vector truy vấn và vector ảnh, cho danh sách có xếp hạng."),
        ("Ví dụ thất bại cho thấy điều gì?", "Trong Hình 5.3, top-5 có nhiều váy không dây tông xanh — đúng phần lớn yêu cầu nhưng không phải ảnh đích được gán nhãn: âm tính giả làm R@K đánh giá thấp chất lượng thực. Ngoài ra câu mơ hồ (“is the same”) hay thay đổi tinh tế cũng gây thất bại."),
        ("CLIP được huấn luyện thế nào?", "Đối sánh 400 triệu cặp ảnh–chú thích: kéo vector ảnh và chú thích của nó lại gần, đẩy xa các cặp khác trong batch."),
    ],
    "check": ["Giải thích CIR bằng ví dụ của chính mình trong 30 giây.", "Phân biệt Precision, Recall, Recall@K, mAP@K.",
              "Nói được 2 hạn chế của Pic2Word/SEARLE.", "Chọn và bình luận 2 ví dụ định tính."],
    "read": ["Báo cáo: chương 1–2, mục 5.8", "Bài giảng chương I: slide 6–8 (mô hình tìm kiếm, Precision/Recall)", "Bài báo LinCIR: mục 1–2; CLIP (Radford 2021): mục 1–2"],
},
}

# ---------------------------------------------------------------- rendering


def rich(p, text, size=None):
    for part in re.split(r"(\*\*[^*]+\*\*|\[\[[^\]]+\]\])", text):
        if not part:
            continue
        if part.startswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("[["):
            r = p.add_run(f"[CHỜ KẾT QUẢ: {part[2:-2]}]")
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            r = p.add_run(part)
        if size:
            r.font.size = Pt(size)


def setup(doc):
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21), Cm(29.7)
    s.left_margin = s.right_margin = Cm(2.5)
    s.top_margin = s.bottom_margin = Cm(2.2)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    st.font.size = Pt(12)
    st.paragraph_format.line_spacing = 1.25
    st.paragraph_format.space_after = Pt(4)
    for name, size in (("Heading 1", 15), ("Heading 2", 13)):
        h = doc.styles[name]
        h.font.name = "Times New Roman"
        h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        h.font.size = Pt(size)
        h.font.color.rgb = ACCENT
        h.font.bold = True
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
    # page number footer
    p = s.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for kind, text in (("begin", None), (None, " PAGE "), ("end", None)):
        r = OxmlElement("w:r")
        if kind:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), kind)
            r.append(f)
        else:
            t = OxmlElement("w:instrText")
            t.text = text
            r.append(t)
        p._p.append(r)


def table(doc, header, rows, widths):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(11)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "DCE6F2")
        c._tc.get_or_add_tcPr().append(shd)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            rich(cells[i].paragraphs[0], v, size=11)
    for row in t.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Cm(w)
            for para in row.cells[i].paragraphs:
                para.paragraph_format.space_after = Pt(1)
                para.paragraph_format.line_spacing = 1.1
    doc.add_paragraph()


def bullets(doc, items):
    for it in items:
        rich(doc.add_paragraph(style="List Bullet"), it)


def build(key, m):
    doc = docx.Document()
    setup(doc)
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("TÀI LIỆU HỌC VÀ CHUẨN BỊ THUYẾT TRÌNH")
    r.bold = True
    r.font.size = Pt(16)
    r.font.color.rgb = ACCENT
    t2 = doc.add_paragraph()
    t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t2.add_run(f"{m['name']} ({m['id']}) · Nhóm 8 · Tìm kiếm và Truy xuất thông tin · Đề tài LinCIR")
    r.italic = True
    doc.add_heading("1. Vai trò của bạn", level=1)
    rich(doc.add_paragraph(), m["role"])
    solo = all(sl[2] != "Tâm trình bày" for sl in m["slides"])
    if not solo:
        rich(doc.add_paragraph(), "Tâm trình bày toàn bộ slide. Bạn **hỗ trợ trả lời phản biện** cho các slide liên quan đến phần việc của bạn dưới đây; "
             "khi Tâm mời, trả lời ngắn, nêu số liệu và nguồn (bảng nào trong báo cáo).")
    table(doc, ["Slide", "Nội dung", "Thời gian" if solo else "Người trình bày"], [list(s) for s in m["slides"]], [1.6, 11.0, 2.4])
    doc.add_heading("2. Bức tranh chung của đề tài (cả nhóm cần nắm)", level=1)
    for para in OVERVIEW:
        rich(doc.add_paragraph(), para)
    table(doc, ["Hạng mục", "Số liệu / cấu hình"], [list(k) for k in KEY_NUMBERS], [3.2, 11.8])
    from plain_language import GLOSSARY, SLIDES, SYMBOLS, TIPS
    doc.add_heading("3. Trình bày rõ ràng, dễ hiểu (đọc trước khi tập)", level=1)
    doc.add_heading("Mẹo thuyết trình", level=2)
    bullets(doc, TIPS)
    doc.add_heading("Slide của bạn: ý chính và con số cần nêu" if solo else "Slide liên quan: ý chính và con số cần nắm", level=2)
    table(doc, ["Slide", "Ý chính nói thành lời", "Một con số và ý nghĩa"],
          [[n, SLIDES[n][0], SLIDES[n][1]] for n, _, _ in m["slides"] if n in SLIDES], [1.2, 9.0, 4.8])
    doc.add_heading("Thuật ngữ: định nghĩa ngắn", level=2)
    table(doc, ["Thuật ngữ", "Định nghĩa", "Ví dụ trong đề tài"], [list(g) for g in GLOSSARY], [3.8, 6.2, 5.0])
    doc.add_heading("Cách đọc ký hiệu trên slide", level=2)
    doc.add_paragraph("Lần đầu gặp [$] trên slide, nói thêm: “ký hiệu đô-la trong ngoặc vuông là token giả”; các lần sau chỉ nói “token giả”. "
                      "Ví dụ câu nói: “Mạng phi biến ảnh tham chiếu thành một token giả, ghép vào câu mô tả thay đổi.”")
    table(doc, ["Ký hiệu", "Đọc là", "Nghĩa"], [list(g) for g in SYMBOLS], [2.6, 4.6, 7.8])
    doc.add_heading("4. Kiến thức và nội dung công việc", level=1)
    for title, items in m["theory"]:
        doc.add_heading(title, level=2)
        bullets(doc, items)
    doc.add_heading("Tệp liên quan trong dự án", level=2)
    bullets(doc, m["files"])
    doc.add_heading("5. Kịch bản trình bày chi tiết" if solo else "5. Ý chính phần của bạn (để hỗ trợ trả lời)", level=1)
    table(doc, ["Slide", "Ý chính cần nói" if solo else "Ý chính cần nắm"], [list(s) for s in m["script"]], [1.6, 13.4])
    doc.add_heading("6. Câu hỏi phản biện dự kiến", level=1)
    for i, (q, a) in enumerate(m["qa"], start=1):
        p = doc.add_paragraph()
        rr = p.add_run(f"H{i}. {q}")
        rr.bold = True
        p.paragraph_format.space_after = Pt(1)
        pa = doc.add_paragraph()
        pa.paragraph_format.left_indent = Cm(0.6)
        rich(pa, "→ " + a)
    doc.add_heading("7. Tự kiểm tra trước buổi thuyết trình", level=1)
    bullets(doc, ["☐ " + c for c in m["check"]])
    doc.add_heading("8. Đọc thêm", level=1)
    bullets(doc, m["read"])
    out = OUT / f"HuongDan_{key}.docx"
    doc.save(out)
    return out


if __name__ == "__main__":
    for k, m in MEMBERS.items():
        print(build(k, m).name)
