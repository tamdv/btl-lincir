# Kết quả đã chốt (đóng băng)

- **Chốt lúc:** 14:28 thứ Sáu 09/10/2026 (giờ Hà Nội) — Đào Văn Tâm duyệt (U13).
- **Quy tắc:** báo cáo, slides, tài liệu học, Q&A chỉ lấy số từ các file dưới đây. Mọi thay đổi sau thời điểm này phải ghi lý do trong `docs/decisions.md`.
- **Cấu hình:** CLIP ViT-L/14, 5.000 bước, batch 512, 3 seed (12345, 2024, 7), checkpoint bước cuối; FashionIQ val + CIRCO val; Kaggle 2 × T4.

## Run được dùng

| Run | FIQ TB R@10 | FIQ TB R@50 | CIRCO mAP@5 | CIRCO mAP@10 |
|---|---|---|---|---|
| EXP-000-official-s0 | 26.35 | 46.12 | 10.50 | 12.22 |
| EXP-001-baseline-s12345 | 25.96 | 45.79 | 10.50 | 11.81 |
| EXP-001-baseline-s2024 | 26.11 | 45.45 | 10.35 | 11.71 |
| EXP-001-baseline-s7 | 25.63 | 45.34 | 10.55 | 11.76 |
| EXP-002-infonce-s12345 | 25.65 | 45.37 | 7.54 | 9.33 |
| EXP-002-infonce-s2024 | 25.57 | 44.95 | 8.42 | 10.09 |
| EXP-002-infonce-s7 | 25.38 | 45.16 | 8.09 | 9.76 |
| EXP-003-gapnoise-s12345 | 26.54 | 46.86 | 11.15 | 12.48 |
| EXP-003-gapnoise-s2024 | 26.51 | 46.73 | 10.53 | 12.14 |
| EXP-003-gapnoise-s7 | 26.46 | 46.78 | 11.13 | 12.50 |
| EXP-004-infonce-gapnoise-s12345 | 25.59 | 45.39 | 7.75 | 9.19 |
| EXP-004-infonce-gapnoise-s2024 | 25.39 | 45.19 | 8.02 | 9.33 |
| EXP-004-infonce-gapnoise-s7 | 25.34 | 45.51 | 7.65 | 9.10 |

## Kết luận đã chốt

- **H2 được ủng hộ:** B (nhiễu có hướng) tốt hơn baseline có ý nghĩa thống kê — FashionIQ R@10 +0,60 (p = 0,006), R@50 +1,27 (p < 0,001), CIRCO mAP@25/50; vượt checkpoint chính thức 20.000 bước.
- **H1 bị bác bỏ:** A (InfoNCE) không tốt hơn trên FashionIQ, kém trên CIRCO (mAP@5 −2,45, KTC 95% [−3,95; −1,07]). Trình bày như kết quả âm có giải thích cơ chế.
- **H3 bị bác bỏ:** A+B kém baseline trên CIRCO (mAP@5 −2,66).
- **Cơ chế:** cosine φ(ảnh)–φ(văn bản) B 0,84 > chính thức 0,81 ≈ baseline 0,80 > A+B 0,69 > A 0,64, cùng thứ tự CIRCO mAP@5.

## Dấu vân tay file (SHA-256, 16 ký tự đầu)

| File | SHA-256 |
|---|---|
| `experiments/registry.csv` | `1f3dead48f4c2bd8` |
| `results/assets.json` | `86d4d0c72625b057` |
| `results/tables/main_results.md` | `32f8ecd0e0db25b7` |
| `results/tables/significance.md` | `6f1cc1013f4eb374` |
| `results/tables/ablation.md` | `84b0b2ffcc27bc8c` |
| `results/analysis_vi.json` | `ddaa5df63d6fdf77` |
| `results/figures/modality_gap.png` | `e2c70848fe885019` |
| `results/figures/learning_curve.png` | `029dc54fb546cc7e` |
| `results/figures/qualitative_fiq_1.png` | `f14ac7daa94cb5e8` |
| `report/BaoCao_Nhom8_LinCIR.docx` | `b6c33a3fe91515ed` |
| `slides/Slides_Nhom8_LinCIR.pptx` | `7cc22e1866ba7568` |

Ghi chú: `report/…docx` và `slides/…pptx` là bản Tâm sửa tay đã điền kết quả; chỉnh sửa trình bày sau khi chốt vẫn được phép nếu không đổi số liệu. 15:20 09/10/2026: chèn lại trường MỤC LỤC (bị mất từ bản 08/10), bỏ khoảng cách sau đoạn của style TOC 1/2 để mục lục vừa 1 trang; số liệu không đổi.

- 09/10/2026: slides chỉ đổi ghi chú người nói sang lời thường (không đổi số liệu) → SHA-256 mới của `slides/Slides_Nhom8_LinCIR.pptx`: `3aa5b74816a5fb99`.
- 09/10/2026: ghi chú người nói viết lại theo văn phong nghiêm túc, không ví von (không đổi số liệu) → SHA-256 mới: `2d94333bfb0c8c50`.
