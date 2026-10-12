# Khung slides thuyết trình — Nhóm 8, LinCIR

Thời lượng mục tiêu: ~15 phút, 16 slide. Số liệu chỉ lấy từ `results/` (đã đóng băng). Ô `[CHỜ]` điền sau phiên U20.
Hình dùng lại từ `report/figures/` và `results/figures/`.

| # | Tiêu đề | Nội dung chính | Hình/bảng | Người trình bày | Thời gian |
|---|---|---|---|---|---|
| 1 | Bìa | Đề tài, môn học, giảng viên TS. Đào Thị Thuý Quỳnh, Nhóm 8: Đào Văn Tâm, Lâm Thành Trung, Nguyễn Xuân Tùng, Trần Quang Đức Dũng, Mekdala Nounou | — | Tâm | 0:20 |
| 2 | Bài toán CIR | Nhu cầu thông tin kết hợp ảnh + văn bản; ví dụ váy FashionIQ | `report/figures/cir_example.png` | Nou | 1:00 |
| 3 | Vì sao zero-shot? | Bộ ba ⟨ảnh, văn bản, ảnh đích⟩ đắt, nhỏ (28–46 nghìn) → ZS-CIR | sơ đồ nhỏ | Nou | 0:45 |
| 4 | Liên hệ môn học | Mô hình tìm kiếm cổ điển; Precision/Recall → R@K, mAP@K; tìm kiếm vector vs chỉ mục ngược | công thức | Nou | 1:00 |
| 5 | Ý tưởng token giả | Ảnh → [$] trong không gian token; "a photo of [$] that …" | `report/figures/lincir_infer.png` | Trung | 1:00 |
| 6 | Hạn chế Pic2Word/SEARLE | Câu mẫu cố định, cần bộ mã hóa ảnh khi train | — | Trung | 0:40 |
| 7 | LinCIR: SMP | Chiếu z_c → ê_c, che từ khóa, MSE(z_c, ẑ_c) | `report/figures/lincir_train.png` | Trung | 1:30 |
| 8 | Nhiễu & modality gap | U(0,1)·N(0,I); hai "hình nón" của CLIP | — | Trung | 0:45 |
| 9 | Dựng mã nguồn | Chuyển sang Python 3.13/transformers 5; sai lệch 0; 3 điểm lệch bài báo–code | bảng nhỏ | Tâm | 1:00 |
| 10 | Kết quả tái hiện | Checkpoint chính thức vs bài báo | Bảng 5.2 [CHỜ] | Tùng | 0:45 |
| 11 | Cải tiến A: InfoNCE | Vì sao MSE chưa đủ cho xếp hạng; công thức; chi phí +5% | công thức | Trung | 1:00 |
| 12 | Cải tiến B: nhiễu có hướng | Δ = tâm ảnh − tâm văn bản; n = α·Δ + u·ε | sơ đồ | Dũng | 0:45 |
| 13 | Thiết lập thực nghiệm | Kaggle 2×T4, 3 seed, 5.000 bước, checkpoint cuối, FIQ + CIRCO | Bảng 5.1 | Tâm | 0:45 |
| 14 | Kết quả chính + kiểm định | mean ± std; Δ, KTC 95%, p | Bảng 5.3, 5.4 [CHỜ] | Dũng | 1:30 |
| 15 | Vì sao tốt hơn? | Modality gap/độ nhất quán φ; đường học; ví dụ top-5 | `results/figures/*` [CHỜ] | Dũng | 1:30 |
| 16 | Kết luận & hạn chế | Kết luận H1–H3; 5k bước, chưa quét λ/α, chưa có CIRR; hướng phát triển | — | Tùng | 0:45 |

Tổng ≈ 15 phút. Người trình bày theo phân công trong phụ lục báo cáo: Nou (2–4, lý thuyết), Trung (5–8 phương pháp, 11 cải tiến A), Tâm (1, 9 mã nguồn, 13 thực nghiệm), Tùng (10 tái hiện, 16 kết luận), Dũng (12 cải tiến B, 14–15 kết quả và phân tích).

## Nguyên tắc
- Mỗi slide một ý; tối đa ~6 dòng chữ; số liệu phải có nguồn (bảng nào trong báo cáo).
- Slide 14–15 là trọng tâm "chứng minh": luôn nêu p-value và khoảng tin cậy, không chỉ nêu Δ.
- Kết quả không đạt (nếu có) trình bày trung thực + giải thích.
- Bộ slide thật làm sau khi đóng băng kết quả (A20).
