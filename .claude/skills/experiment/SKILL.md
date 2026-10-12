---
name: experiment
description: Đăng ký, chạy và ghi kết quả một thí nghiệm LinCIR (huấn luyện + đánh giá). Dùng khi cần train baseline hoặc biến thể cải tiến, chạy nhiều seed, hoặc đánh giá một checkpoint.
---

# Chạy thí nghiệm LinCIR

Mục tiêu: mọi run đều tái lập được và so sánh công bằng được.

## Cách nhanh (khuyến nghị)

`python scripts/run_experiment.py configs/<EXP>.yaml --seed <seed> --cirr <CIRR> --fiq <FIQ>` tự làm bước 3–7 bên dưới (đăng ký, thư mục run, train, đánh giá, cập nhật registry). Trên Kaggle dùng `notebooks/kaggle_lincir.ipynb`; kết quả chép về rồi chạy `scripts/rebuild_registry.py`. Các bước thủ công dưới đây dùng khi cần kiểm soát từng phần.

## Các bước

1. **Xác định thí nghiệm.** Tìm hoặc tạo `configs/EXP-<nnn>-<tên>.yaml` (copy từ `configs/EXP-001-baseline.yaml`). Chỉ đổi đúng các tham số mà biến thể cần đổi; mọi thứ khác giữ như baseline.
2. **Kiểm tra code.** `git status` phải sạch hoặc ghi rõ thay đổi chưa commit vào cột `notes`. Lấy `git rev-parse --short HEAD`.
3. **Đăng ký** một dòng cho mỗi seed vào `experiments/registry.csv` với `status=planned`. Run id: `EXP-<nnn>-<tên>-s<seed>`. Seed chuẩn: 12345, 2024, 7.
4. **Tạo thư mục** `experiments/runs/<run_id>/`, copy config vào đó.
5. **Chạy** (từ `code/`), ghi log:
   ```bash
   python train_phi.py <tham số từ config> --seed <seed> \
     --output_dir ../experiments/runs/<run_id> 2>&1 | tee ../experiments/runs/<run_id>/train.log
   ```
   Cập nhật `status=running`, `started`.
   Nếu không có GPU trên máy hiện tại: KHÔNG chạy. In lệnh đầy đủ để người dùng chạy trên máy GPU/Colab.
6. **Đánh giá** `checkpoints/phi_best.pt` trên CIRR dev và FashionIQ bằng `scripts/eval_per_query.py --out_dir experiments/runs/<run_id>` (lệnh đầy đủ trong `CLAUDE.md`). Lưu:
   - `metrics.json` (do script ghi) và `train_metrics.json` (do `train_phi.py` ghi: thời gian, thiết bị, bước tốt nhất)
   - `per_query_cirr.csv`, `per_query_fiq_<dress|shirt|toptee>.csv` (cột `query_id,target_rank,…`, rank bắt đầu từ 1)
7. **Cập nhật registry**: `status=done|failed`, `finished`, các cột chỉ số, `notes` (bất thường, OOM, lệch so với kỳ vọng).
8. Nếu run hoàn thành một việc trong checklist, dùng skill `update-checklist`.

## Quy tắc

- Không ghi đè thư mục run đã có. Chạy lại = run id mới (thêm hậu tố `-r2`).
- Run thất bại vẫn giữ, đánh dấu `failed` và ghi lý do.
- Khi so sánh với bài báo, dùng bảng số liệu tham chiếu trong `CLAUDE.md`; khi kết luận cải tiến, chỉ so với baseline do nhóm chạy (skill `compare-results`).
