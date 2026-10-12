# Khung slides thuyết trình — Nhóm 8, LinCIR

Thời lượng mục tiêu: ~15 phút, tối đa 15 slide (14 slide nội dung + slide hỏi đáp). Số liệu chỉ lấy từ `results/` (đã đóng băng).
Hình dùng lại từ `report/figures/` và `results/figures/`.

| # | Tiêu đề | Nội dung chính | Hình/bảng | Người trình bày | Thời gian |
|---|---|---|---|---|---|
| 1 | Bìa | Đề tài, môn học, giảng viên TS. Đào Thị Thuý Quỳnh, Nhóm 8: Đào Văn Tâm, Lâm Thành Trung, Nguyễn Xuân Tùng, Trần Quang Đức Dũng, Mekdala Nounou | — | Tâm | 0:20 |
| 2 | Tóm tắt bài báo LinCIR | Vấn đề (bộ ba đắt; Pic2Word/SEARLE cần ảnh, câu mẫu cố định) · ý tưởng (SMP chỉ văn bản, nhiễu u·ε) · kết quả bài báo (tốt nhất 4 benchmark, nhanh hơn 6–8,4 lần) · Gu et al., NAVER, CVPR 2024 · dòng cuối: lộ trình của nhóm (dựng mã → tái hiện → baseline, A, B, A+B trên Kaggle → kiểm định → phân tích) | 3 thẻ | Tâm | 1:15 |
| 3 | Bài toán CIR | Nhu cầu thông tin kết hợp ảnh + văn bản; ví dụ váy FashionIQ; vì sao zero-shot: bộ ba đắt, nhỏ (46,6k, 28,8k) | `report/figures/cir_example.png` | Nou | 1:00 |
| 4 | Ý tưởng token giả | Ảnh → [$] trong không gian token; "a photo of [$] that …" | `report/figures/lincir_infer.png` | Nou | 1:00 |
| 5 | LinCIR: SMP | Chiếu z_c → ê_c, che từ khóa, MSE(z_c, ẑ_c); khác Pic2Word/SEARLE: không cần ảnh, không dùng câu mẫu cố định | `report/figures/lincir_train.png` | Trung | 1:30 |
| 6 | Cải tiến A: InfoNCE | Vì sao MSE chưa đủ cho xếp hạng; công thức; chi phí +2% | công thức | Trung | 1:00 |
| 7 | Nhiễu của LinCIR và cải tiến B | Modality gap; nhiễu u·ε của LinCIR; Δ = tâm ảnh − tâm văn bản; n = α·Δ + u·ε | sơ đồ | Dũng | 1:30 |
| 8 | Độ đo đánh giá (liên hệ môn học) | Mô hình tìm kiếm cổ điển; Precision/Recall → R@K, mAP@K; tìm kiếm vector vs chỉ mục ngược | công thức | Dũng | 1:00 |
| 9 | Dựng mã nguồn | Chuyển sang Python 3.13/transformers 5; sai lệch 0; 3 điểm lệch bài báo–code | bảng nhỏ | Tâm | 1:00 |
| 10 | Thiết lập thực nghiệm | Kaggle 2×T4, 3 seed, 5.000 bước, checkpoint cuối, FIQ + CIRCO | Bảng 5.1 | Tâm | 0:45 |
| 11 | Kết quả tái hiện | Checkpoint chính thức vs bài báo | Bảng 5.2 | Tùng | 0:45 |
| 12 | Kết quả chính + kiểm định | mean ± std; Δ, KTC 95%, p | Bảng 5.3, 5.4  | Tùng | 1:30 |
| 13 | Vì sao tốt hơn? | Modality gap/độ nhất quán φ; đường học; ví dụ top-5 | `results/figures/*`  | Dũng | 1:30 |
| 14 | Kết luận & hạn chế | Kết luận H1–H3; 5k bước, chưa quét λ/α, chưa có CIRR; hướng phát triển | — | Tùng | 0:45 |

Tổng ≈ 15 phút, 14 slide nội dung + slide hỏi đáp, mỗi người nói một khối liền: Tâm 1–2 (mở đầu, tóm tắt bài báo, lộ trình), Nou 3–4 (bài toán CIR, token giả), Trung 5–6 (SMP, cải tiến A), Dũng 7–8 (nhiễu và cải tiến B, độ đo), Tâm 9–10 (mã nguồn, thiết lập Kaggle), Tùng 11–12 (tái hiện, kết quả chính), Dũng 13 (vì sao), Tùng 14 (kết luận), Tâm điều phối hỏi đáp (15). Thời lượng: Dũng ≈ 4:00, Tâm ≈ 3:20, Tùng ≈ 3:00, Trung ≈ 2:30, Nou ≈ 2:00.

## Nguyên tắc
- Mỗi slide một ý; tối đa ~6 dòng chữ; số liệu phải có nguồn (bảng nào trong báo cáo).
- Slide 12–13 là trọng tâm "chứng minh": luôn nêu p-value và khoảng tin cậy, không chỉ nêu Δ.
- Kết quả không đạt (nếu có) trình bày trung thực + giải thích.
- Bộ slide thật làm sau khi đóng băng kết quả (A20).
