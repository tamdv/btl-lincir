---
name: compare-results
description: So sánh baseline và biến thể cải tiến bằng thống kê (mean ± std qua seed, paired bootstrap, Wilcoxon), lập bảng kết quả/ablation và đóng băng số liệu vào results/. Dùng khi cần kết luận một cải tiến có tốt hơn không.
---

# So sánh và chứng minh kết quả

## Đầu vào

Các run `done` trong `experiments/registry.csv`, mỗi run có `per_query_<dataset>.csv` (`query_id,target_rank`).

## Cách nhanh

`python scripts/make_report_assets.py` tạo toàn bộ bảng (chính, kiểm định, ablation) và hình (đường học, modality gap, ví dụ top-5) từ `experiments/runs/`. Các bước dưới đây để kiểm tra/giải thích từng phần.

## Các bước

1. **Kiểm tra tính công bằng** trước khi tính: cùng backbone, cùng dữ liệu, cùng `max_train_steps`, cùng tiêu chí chọn checkpoint, đủ 3 seed cho mỗi bên. Thiếu điều kiện nào thì dừng và báo.
2. **Tổng hợp theo seed**: mean ± std cho từng chỉ số (CIRR R@1/5/10/50, FashionIQ R@10/R@50 từng loại và trung bình).
3. **Kiểm định** bằng `scripts/stats_compare.py`:
   ```bash
   python scripts/stats_compare.py --base experiments/runs/EXP-001-baseline-s*/per_query_cirr.csv \
     --new experiments/runs/EXP-002-infonce-s*/per_query_cirr.csv --k 1 5 10 50
   ```
   Script ghép theo `query_id`, lấy trung bình qua seed, chạy paired bootstrap (10.000 lần) và Wilcoxon trên recall@K và reciprocal rank.
   CIRCO: `--base .../per_query_circo.csv --new ... --value_cols ap5 ap10 ap25 ap50` (kiểm định mAP@K). FashionIQ: chạy riêng cho `per_query_fiq_{dress,shirt,toptee}.csv`.
4. **Viết kết luận đúng mức**:
   - p < 0.05 và Δ > 0: "tốt hơn có ý nghĩa thống kê".
   - p ≥ 0.05: "chưa đủ bằng chứng", không viết "tốt hơn".
   - Δ < 0: ghi rõ là kém hơn, phân tích nguyên nhân.
5. **Lưu bảng** Markdown/CSV vào `results/tables/` (tên `main_results.md`, `ablation.md`, `significance.md`), hình vào `results/figures/`. Ghi run id nguồn ở chân mỗi bảng.
6. **Đóng băng** (chỉ khi người dùng yêu cầu): tạo `results/FROZEN.md` ghi ngày, commit, danh sách run id. Sau đó không sửa `results/` nữa trừ khi có quyết định ghi trong `docs/decisions.md`.

## Giải thích "tại sao tốt hơn"

Ngoài con số, đề xuất ít nhất một bằng chứng cơ chế: modality gap trước/sau (`scripts/modality_gap.py --phi baseline=... --phi A=...`), phân bố cosine cặp đúng/sai, kết quả theo nhóm truy vấn, ví dụ top-5 định tính.
