# Khung slides thuyết trình — Nhóm 8, LinCIR

Thời lượng mục tiêu: ~15 phút, 16 slide (bìa, phân công, 13 slide nội dung, hỏi đáp). Số liệu chỉ lấy từ `results/` (đã đóng băng).
Hình dùng lại từ `report/figures/` và `results/figures/`.

| # | Tiêu đề | Nội dung chính | Hình/bảng | Người trình bày | Thời gian |
|---|---|---|---|---|---|
| 1 | Bìa | Đề tài, giảng viên, 5 thành viên; lời nói: tóm tắt dễ hiểu khoảng 1 phút (ví dụ chiếc váy, LinCIR học chỉ bằng văn bản, B tốt hơn, A kém đi) | — | Tâm | 1:10 |
| 2 | Phân công công việc | Bảng 5 thành viên: công việc chính, slide hỗ trợ trả lời | bảng | Tâm | 0:30 |
| 3 | Bài toán CIR, câu hỏi của nhóm | Ví dụ chiếc váy; bài báo LinCIR giải bài toán chỉ bằng văn bản; câu hỏi: sửa hàm mất mát (A) hay sửa nhiễu (B) có giúp LinCIR tốt hơn | `report/figures/cir_example.png` | Tâm | 1:00 |
| 4 | Độ đo (liên hệ chương I) | R@K = số truy vấn có ảnh đích trong top-K / tổng số truy vấn; AP@K = Σ P@k·rel(k) / min(K, số ảnh đúng); giao thức FashionIQ val, CIRCO val, bootstrap + Wilcoxon | 3 thẻ | Tâm | 1:00 |
| 5 | Ý tưởng token giả | Ảnh → φ → [$] → "a photo of [$] that …" → vector truy vấn; chỉ học φ | `report/figures/lincir_infer.png` | Tâm | 0:50 |
| 6 | Tóm tắt bài báo LinCIR | Vấn đề của Pic2Word/SEARLE · ý tưởng LinCIR · kết quả bài báo (tốt nhất 4 bộ, nhanh hơn 6–8,4 lần) | 3 thẻ | Tâm | 1:00 |
| 7 | Self-Masking Projection | Sơ đồ phương pháp gốc (không có A, B): che từ khóa, MSE(z_c, ẑ_c) | `report/figures/lincir_train_base_slide.png` | Tâm | 1:20 |
| 8 | Nhiễu và modality gap | Hai vùng tách biệt (0,82; 0,26); nhiễu u·ε | 2 thẻ + 2 số | Tâm | 1:00 |
| 9 | Cải tiến A: InfoNCE | Vấn đề, giải pháp, chi phí +2%, giả thuyết H1 (chưa nêu kết quả) | 2 thẻ + 2 số | Tâm | 1:00 |
| 10 | Cải tiến B: nhiễu có hướng | Vấn đề, n = 0,5·Δ + u·ε, ‖Δ‖ = 13,87, giả thuyết H2 (H3 nói bằng lời) | 2 thẻ + 2 số | Tâm | 1:00 |
| 11 | Dựng mã nguồn, chạy trên Kaggle | Sai lệch 0,00, 4 lỗi đã sửa; 4 biến thể × 3 seed, 5.000 bước, 2 GPU T4 | 2 số + 2 thẻ | Tâm | 1:00 |
| 12 | Tái hiện | Bảng so với bài báo (lệch ≤ 0,77); 3 khác biệt bài báo – mã nguồn | Bảng 5.2 | Tâm | 0:50 |
| 13 | Kết quả chính, kiểm định | mean ± std, hàng checkpoint chính thức, B tô đậm; p-value, khoảng tin cậy | Bảng 5.3, 5.4 | Tâm | 1:30 |
| 14 | Vì sao | Độ nhất quán φ ảnh – văn bản; đường học; câu kết luận dưới hình | `results/figures/*_slide.png` | Tâm | 1:20 |
| 15 | Kết luận | Ví dụ truy xuất top-5; H1–H3; đóng góp; hạn chế | `results/figures/qualitative_fiq_1.png` | Tâm | 1:20 |
| 16 | Cảm ơn, hỏi đáp | Tâm điều phối, mời thành viên phụ trách trả lời | — | Tâm | — |

Tổng ≈ 15 phút. Tâm trình bày toàn bộ; khi hỏi đáp mời người phụ trách: phương pháp, cải tiến A → Trung; tái hiện, kết quả → Tùng; độ đo, kiểm định, cải tiến B → Dũng; bài toán, lý thuyết, ví dụ định tính → Nou; mã nguồn, Kaggle → Tâm.

## Nguyên tắc
- Mỗi slide một ý; tối đa ~6 dòng chữ; số liệu phải có nguồn (bảng nào trong báo cáo).
- Slide 13–14 là trọng tâm "chứng minh": luôn nêu p-value và khoảng tin cậy, không chỉ nêu Δ.
- Kết quả không đạt (nếu có) trình bày trung thực + giải thích.
- Bộ slide thật làm sau khi đóng băng kết quả (A20).
