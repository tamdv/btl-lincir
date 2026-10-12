# BTL Nhóm 8 — LinCIR (Tìm kiếm và Truy xuất thông tin)

Bài tập lớn: đọc hiểu, tái hiện, cải tiến và chứng minh cải tiến cho bài báo
*Language-only Efficient Training of Zero-shot Composed Image Retrieval* (Gu et al., CVPR 2024),
sau đó viết báo cáo và slides.

- Thành viên: Đào Văn Tâm B25CHHT112 (trưởng nhóm), Lâm Thành Trung B25CHHT117, Nguyễn Xuân Tùng B25CHHT119, Trần Quang Đức Dũng B25CHHT088, Mekdala Nounou B25CHHT124. Giảng viên: TS. Đào Thị Thuý Quỳnh.
- Kế hoạch + checklist dùng chung: https://claude.ai/artifact/Jons1Eq7odXT2kWWt4iYwj (task id dạng `p2-3`).
- **Lộ trình chi tiết, ai làm gì, việc nào phụ thuộc việc nào:** `.claude/skills/roadmap/checklist.md` (skill `roadmap`). Đọc file này trước khi bắt đầu hoặc khi được hỏi tiến độ.
- Ngôn ngữ: tài liệu, báo cáo, slides, ghi chú viết **tiếng Việt**; code, tên biến, commit message viết tiếng Anh.

## Cấu trúc thư mục

| Thư mục | Nội dung |
|---|---|
| `code/` | Code LinCIR gốc (upstream commit trong `code/UPSTREAM_COMMIT`) + sửa đổi của nhóm |
| `configs/` | Mỗi thí nghiệm một file `EXP-xxx.yaml` (tham số dòng lệnh) |
| `experiments/registry.csv` | Sổ đăng ký mọi lần chạy, một dòng một run |
| `experiments/runs/<run_id>/` | `config.yaml`, `train.log`, `metrics.json`, `per_query_<dataset>.csv` |
| `results/` | Bảng và hình **đã đóng băng** dùng cho báo cáo/slides |
| `scripts/` | Script phụ: đánh giá per-query, kiểm định thống kê, modality gap, vẽ bảng |
| `data/` | Dữ liệu benchmark (không commit) — xem `data/README.md` |
| `papers/` | PDF bài báo LinCIR, SEARLE |
| `docs/notes/` | Tóm tắt, ghi chú đọc hiểu của từng người |
| `docs/meetings/` | Biên bản họp `YYYY-MM-DD.md` |
| `docs/decisions.md` | Nhật ký quyết định (chọn cải tiến, đổi siêu tham số, lý do) |
| `report/`, `slides/` | Báo cáo và slides |

## Bản đồ code (`code/`)

- `train_phi.py` — vòng huấn luyện module chiếu φ (Phi).
  - Dòng ~230: thêm nhiễu `rand(B,1) * randn(B,d)` → chỗ sửa cho **cải tiến B** (nhiễu có hướng).
  - Dòng ~241: `F.mse_loss(...)` → chỗ sửa cho **cải tiến A** (thêm InfoNCE).
  - Dòng ~303: chọn `phi_best.pt` theo CIRR dev R@1.
- `loader.py` — `build_loader` (dòng ~208) tải 3 bộ caption từ HuggingFace; `extract_keywords_spacy` (dòng ~53) và `CaptionDataset` thay từ khóa bằng `[$]` → chỗ sửa cho **cải tiến C** (IDF).
- `models.py` — `build_text_encoder`: `large`=openai/clip-vit-large-patch14, `huge`, `giga`; class `Phi` (MLP 3 lớp).
- `validate.py` — đánh giá CIRR dev, FashionIQ (in R@K, chưa xuất per-query).
- `generate_test_submission.py` — file nộp CIRR test / CIRCO (chấm trên server ngoài).

## Lệnh chuẩn

```bash
pip install -r requirements.txt && python -m spacy download en_core_web_sm
python scripts/check_encoder_equivalence.py          # phải in 4 dòng True/0.00e+00 trước khi train

cd code
# Huấn luyện (Kaggle, ViT-L). Checkpoint ghi vào <output_dir>/checkpoints/{phi_best,phi_latest}.pt,
# thời gian + lịch sử validate vào <output_dir>/train_metrics.json
python train_phi.py --batch_size 512 --clip_model_name large --mixed_precision fp16 --num_workers 4 \
  --output_dir ../experiments/runs/<run_id> --cirr_dataset_path ../data/CIRR \
  --validation_steps 1000 --checkpointing_steps 1000 --seed <seed> \
  --lr_scheduler constant_with_warmup --lr_warmup_steps 0 --max_train_steps 20000
cd ..

# Đánh giá per-query (metrics.json + per_query_*.csv) — thay cho code/validate.py
python scripts/eval_per_query.py --phi experiments/runs/<run_id>/checkpoints/phi_latest.pt \
  --clip_model_name large --fiq data/FashionIQ --circo data/CIRCO --out_dir experiments/runs/<run_id>
# --phi official-large = checkpoint chính thức; thêm --cirr data/CIRR khi có
```

**Cách chạy chuẩn: một lệnh cho mỗi config × seed** (train → đánh giá per-query → ghi `experiments/registry.csv`):

```bash
python scripts/run_experiment.py configs/EXP-002-infonce.yaml --seed 12345 --cirr data/CIRR --fiq data/FashionIQ
# chạy lại: --suffix=-r2 ; ghi đè tham số: --set max_train_steps=5000 ; xem lệnh: --dry_run
```

**Phương án nhanh (đang dùng, xem `docs/decisions.md` 2026-10-07):** đánh giá trên FashionIQ val + CIRCO val (CIRR khi NLVR2 duyệt), K = 5.000 bước, checkpoint bước cuối, 2 run song song. Chuỗi phiên Kaggle: `prep_eval` → `train` (TRAIN_SET 1, 2) → `eval`; chi tiết trong ô đầu notebook. Dữ liệu: `scripts/prepare_eval_data.py --what fiq circo coco`.

Trên Kaggle: `./scripts/make_kaggle_bundle.sh` → upload `dist/btl-lincir-code.zip` thành Dataset riêng tư `btl-lincir-code` → mở `notebooks/kaggle_lincir.ipynb` (MODE `smoke` | `official` | `train`). Tải `results_*.zip` về, giải nén vào thư mục dự án, chạy `python scripts/rebuild_registry.py`.

Config: `EXP-000` checkpoint chính thức (chỉ đánh giá) · `001` baseline · `002` A · `003` B · `004` A+B · `005-*` quét λ · `006-*` quét α · `007` C · `900` chạy thử dữ liệu giả.

Cờ của nhóm trong `train_phi.py` (mặc định = LinCIR gốc):

| Cờ | Ý nghĩa |
|---|---|
| `--infonce_weight λ`, `--infonce_temp τ` | Cải tiến A: `L = MSE + λ·InfoNCE` (mặc định λ=0, τ=0.07) |
| `--gap_noise_alpha α`, `--gap_vector_path` | Cải tiến B: cộng `α·Δ` vào nhiễu; Δ từ `scripts/modality_gap.py --save_delta` |
| `--idf_path`, `--idf_keep_ratio r` | Cải tiến C: chỉ che `r` phần từ khóa IDF cao nhất; IDF từ `scripts/compute_idf.py` |
| `--caption_datasets`, `--train_captions_file`, `--max_captions` | Chọn/thu nhỏ dữ liệu train (tập con cố định, data seed 0) |
| `--cirr_dataset_path` | Giờ là tùy chọn: bỏ trống thì không validate, không có `phi_best.pt` |
| `--clip_model_name base` | CLIP ViT-B/32 cho chạy thử trên M1 |

Script trong `scripts/`:

| Script | Việc |
|---|---|
| `check_encoder_equivalence.py` | Kiểm tra encoder viết lại khớp HF CLIP, token `$` = 259 |
| `eval_per_query.py` | Đánh giá CIRR val / FashionIQ val, xuất thứ hạng từng truy vấn, cache đặc trưng ảnh |
| `stats_compare.py` | mean ± std qua seed, paired bootstrap, Wilcoxon |
| `modality_gap.py` | Đo modality gap CLIP, độ nhất quán của φ (ảnh vs văn bản), lưu Δ cho cải tiến B |
| `compute_idf.py` | IDF trên corpus caption cho cải tiến C |
| `make_toy_benchmarks.py` | Dữ liệu giả cấu trúc như CIRR/FashionIQ để chạy thử quy trình |
| `run_experiment.py` | Chạy một config × seed: train → đánh giá → ghi registry |
| `rebuild_registry.py` | Dựng lại registry từ các thư mục run (sau khi chép từ Kaggle về) |
| `make_kaggle_bundle.sh` | Đóng gói code thành `dist/btl-lincir-code.zip` để upload lên Kaggle |
| `prepare_eval_data.py` | Tải FashionIQ val (HF mirror), CIRCO val (COCO unlabeled2017, cache gallery 123k ảnh), COCO val2017 |
| `kaggle_jobs.py` | Chạy job song song trên 2 GPU, chặn trước giới hạn 12 giờ; tìm file trong Input |
| `make_report_assets.py` | Từ thư mục run → `results/tables/*.md`, `results/figures/*.png`, `results/assets.json` (dùng cho báo cáo) |

Chạy thử toàn bộ quy trình trên M1 (khoảng 10 phút, số liệu vô nghĩa): xem nhật ký A10 trong `.claude/skills/roadmap/checklist.md`.
Checkpoint chính thức ViT-L: https://huggingface.co/navervision/zeroshot-cir-models/blob/main/lincir_large.pt

## Môi trường

- **Kaggle Notebook** (train, đánh giá): GPU T4×2, 16GB/card, Python 3.13, torch 2.11+cu128, CUDA 13 driver, 20GB ở `/kaggle/working`. Dữ liệu gắn vào `/kaggle/input/` (chỉ đọc). Tắt phiên khi không dùng để không mất giờ GPU.
- **Mac mini M1, 16GB RAM** (code, chạy thử nhỏ, demo): không có GPU NVIDIA, dùng CPU/MPS, fp32. Không chạy train dài ở đây.
- Mac: môi trường ảo `.venv/` (Python 3.14, transformers 5.19). Chạy bằng `.venv/bin/python`.

## Lưu ý đã biết về code gốc

- Đã sửa (`# [NHOM8]`): `train_phi.py` gõ nhầm `arg.max_grad_norm`; `validate.py` gọi CIRCO với biến chưa định nghĩa; `utils.py` ép `.half()` làm hỏng CPU/MPS; `encode_with_pseudo_tokens.py` dùng API nội bộ transformers 4.34 (đã viết lại, kiểm tra khớp tuyệt đối); bỏ phụ thuộc gói `clip` của OpenAI (`code/compat.py`).
- Class `Phi` trong code **không có LayerNorm** đầu/cuối như bài báo mô tả (LN-Linear-…-Linear-LN) → thêm một điểm lệch giữa bài báo và code.
- `build_loader` dùng **3** bộ caption (CC3M, SD prompts 2.47M, **Midjourney prompts**), trong khi bài báo chỉ nêu CC3M + SD prompts. Ghi rõ điểm này khi so sánh tái hiện.
- Sau `max_train_steps` script gọi `exit()`; `phi_best.pt` chỉ được lưu khi có `--checkpointing_steps`.
- Không bật `--l2_normalize` khi train (bài báo: không hội tụ).
- Tokenizer lấy từ `stabilityai/stable-diffusion-xl-base-1.0` (cần tải lần đầu).

## Số liệu tham chiếu của bài báo (ViT-L)

| Benchmark | Chỉ số | LinCIR (paper) |
|---|---|---|
| CIRCO test | mAP@5 / @10 / @25 / @50 | 12.59 / 13.58 / 15.00 / 15.85 |
| CIRR test (full) | R@1 / R@5 / R@10 | 25.04 / 53.25 / 66.68 |
| CIRR dev | R@1 (Bảng 7, 8) | 25.66 |
| FashionIQ val | Avg R@10 / R@50 | 26.28 / 46.49 |
| GeneCIS | Avg R@1 / R@2 / R@3 | 12.19 / 22.76 / 32.38 |

Chỉ số chính theo bài báo: CIRCO mAP@5, CIRR full **R@10**, FashionIQ R@10/R@50. CIRR R@1 nhiễu (false negative) — chỉ dùng để chọn model.

## Quy tắc thí nghiệm (bắt buộc)

1. **Mọi run phải đăng ký** trong `experiments/registry.csv` trước khi chạy (dùng skill `experiment`).
2. **So sánh công bằng**: baseline là LinCIR do nhóm tự chạy, cùng backbone, cùng dữ liệu, cùng số bước, cùng tiêu chí chọn model. Không kết luận "tốt hơn" bằng cách so với số của bài báo.
3. **3 seed cố định**: `12345`, `2024`, `7`. Báo cáo trung bình ± độ lệch chuẩn.
4. **Kết luận chỉ khi có kiểm định** (paired bootstrap hoặc Wilcoxon, p < 0.05) — dùng skill `compare-results`.
5. Kết quả âm hoặc không đổi vẫn ghi lại đầy đủ; không xóa run thất bại, đánh dấu `status=failed`.
6. Sau mốc đóng băng (cuối tuần 6), báo cáo và slides **chỉ** lấy số từ `results/`.

## Quy ước

- **Thời gian: luôn dùng giờ Hà Nội (GMT+7).** Kaggle ghi giờ UTC (tên file `results_*_YYYYMMDD-HHMM`, cột started/finished do notebook ghi) → cộng 7 giờ khi báo cáo hoặc nhập vào registry (dòng đã chuyển có đuôi `[giờ HN]`).

- Run id: `EXP-<số 3 chữ số>-<tên ngắn>-s<seed>`, ví dụ `EXP-001-baseline-s12345`.
- Nhánh git: `feat/<tên>` cho cải tiến, `exp/<EXP-id>` khi cần; không push thẳng `main`.
- Mỗi thay đổi so với code gốc đánh dấu comment `# [NHOM8] <mô tả>` để dễ liệt kê trong báo cáo.
- Biên bản họp và quyết định ghi ngắn gọn, có ngày tuyệt đối.
