# Nhật ký quyết định

Mỗi quyết định một mục, mới nhất ở trên. Ghi ngày tuyệt đối.

## 2026-10-09 — Kết luận thực nghiệm (Tâm đã chốt, xem results/FROZEN.md)
- **Kết quả:** B (nhiễu có hướng) là cải tiến của nhóm; A (InfoNCE) được báo cáo như kết quả âm có giải thích cơ chế, không bỏ khỏi báo cáo.
- **Lý do:** kiểm định theo truy vấn: B tốt hơn có ý nghĩa (FIQ R@10 p=0,006, R@50 p<0,001); A kém trên CIRCO (KTC 95% của Δ mAP@5 nằm dưới 0). Báo cáo trung thực cả kết quả âm theo quy tắc thí nghiệm.

## 2026-10-08 — Không đánh giá trên CIRR
- **Quyết định:** bỏ hẳn CIRR (U21). Đánh giá trên FashionIQ val và CIRCO val.
- **Lý do:** quyền tải ảnh NLVR2 dự kiến về sau hạn nộp báo cáo; hai bộ còn lại phủ hai lĩnh vực khác nhau, trong đó CIRCO là benchmark chính của bài báo; bài báo cũng nhận xét CIRR nhiều nhiễu. Không ảnh hưởng đường găng.
- **Người quyết định:** Tâm.

## 2026-10-08 — Tăng tốc nạp dữ liệu (không đổi kết quả)
- **Quyết định:** spaCy xử lý theo batch và bỏ NER/lemmatizer khi trích từ khóa. Kiểm chứng: từ khóa giống hệt trên 3.000 câu thật của 3 corpus; batch từ DataLoader giống hệt từng token với code cũ cùng seed. Không dùng phương án bỏ parser (khác kết quả ở 48/1.536 câu).
- **Lý do:** U18 chỉ xong 2/6 run vì nghẽn CPU (4,5 s/bước); tăng tốc ×3,1 phần CPU mà không ảnh hưởng tính công bằng với 2 run đã xong.

## 2026-10-08 — Định dạng báo cáo
- **Quyết định:** báo cáo .docx, 25–30 trang, theo mẫu `3.HĐHM/NOS – 2025-2 - Nhóm 10.docx` (cùng bìa, kiểu chữ, cấu trúc chương). Slides và Q&A làm sau bản nháp báo cáo.
- **Người quyết định:** Tâm.

## 2026-10-07 — Phương án nhanh (Tâm chốt)
- **Dữ liệu đánh giá:** FashionIQ val (ảnh từ bản sao HuggingFace `royokong/fashioniq_val_imgs`, chú thích từ repo chính thức, đủ 15.415/15.415 ảnh) và CIRCO val (220 truy vấn, ảnh COCO unlabeled2017). CIRR bổ sung khi NLVR2 duyệt.
- **Số bước:** K = 5.000 cho mọi biến thể (bài báo/code gốc: 20.000). Đo trên Kaggle T4: ~2,4 s/bước → 20.000 bước ≈ 13 giờ/run, vượt giới hạn 12 giờ/phiên và hạn mức ~30 giờ/tuần. Lưu checkpoint mỗi 500 bước để vẽ đường học, minh chứng K.
- **Chọn checkpoint:** dùng checkpoint bước cuối (phi_latest) cho mọi biến thể; không chọn theo FashionIQ/CIRCO để tránh chọn trên tập báo cáo.
- **Siêu tham số:** không quét; λ = 0,5 (A), α = 0,5 (B). Ghi là hạn chế.
- **Song song:** 2 run cùng lúc, mỗi run 1 T4, batch 512/run (InfoNCE đủ 512 negative).
- **Lý do:** có kết quả sau ~2 đêm train thay vì chờ NLVR2 (~1 tuần) và vượt hạn mức GPU.

## 2026-10-07 — Quy trình chọn siêu tham số và so sánh
- **Quyết định:** quét λ (A) và α (B) với 1 seed, chọn theo CIRR dev R@1 (giống tiêu chí chọn checkpoint của bài báo); FashionIQ val **không** dùng để chọn, coi là tập kiểm tra độc lập. Bản chính thức chạy 3 seed.
- **Quyết định:** mặc định train trên 1 card T4 với batch 512 (NPROC=1) để InfoNCE thấy đủ 512 negative; nếu hết bộ nhớ mới dùng 2 card và ghi rõ cho mọi biến thể.
- **Quyết định:** nếu thời gian 20.000 bước vượt hạn mức GPU, giảm `max_train_steps` **như nhau** cho mọi biến thể (`EXTRA_SET` trong notebook) và ghi vào báo cáo.
- **Lý do:** tránh chọn tham số trên chính tập báo cáo kết quả; giữ so sánh công bằng.

## 2026-10-06 — Khởi tạo dự án
- **Quyết định:** dùng CLIP ViT-L làm backbone chính; 3 seed 12345, 2024, 7; cải tiến chính A (InfoNCE), phụ B (nhiễu có hướng), dự phòng C (IDF).
- **Lý do:** vừa với 1 GPU; A và B nhắm đúng hai điểm yếu bài báo tự nêu (loss chỉ MSE, nhiễu đẳng hướng).
- **Người quyết định:** Tâm (đề xuất, chờ nhóm xác nhận ở buổi họp p3-1).
