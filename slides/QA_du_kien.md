# Câu hỏi dự kiến và gợi ý trả lời — Nhóm 8, LinCIR

Gợi ý trả lời dựa trên bài báo [1] và việc nhóm đã làm. Ô `[CHỜ]` cập nhật sau khi có kết quả.

## Về bài toán và phương pháp
1. **CIR khác tìm kiếm ảnh bằng văn bản ở điểm nào?** Truy vấn gồm cả ảnh tham chiếu và văn bản mô tả *thay đổi*; kết quả phải giữ đặc điểm của ảnh và áp dụng thay đổi. Văn bản thường không mô tả đầy đủ ảnh đích.
2. **Vì sao gọi là zero-shot?** Không dùng bất kỳ bộ ba CIR có nhãn nào khi huấn luyện; mô hình được đánh giá trực tiếp trên FashionIQ/CIRCO.
3. **Làm sao huấn luyện cho truy xuất ảnh mà không cần ảnh?** SMP: chiếu vector câu thành token [$], thay các từ khóa bằng [$] và buộc câu đã che có cùng vector với câu gốc. Khi suy luận thay vector câu bằng vector ảnh — hợp lệ vì CLIP đặt ảnh và văn bản trong cùng không gian; nhiễu giúp thu hẹp modality gap.
4. **Modality gap là gì, đo thế nào?** Vector ảnh và văn bản của CLIP nằm ở hai vùng tách biệt; đo bằng khoảng cách giữa tâm các vector đã chuẩn hóa của hai miền [5].
5. **Vì sao nhiễu U(0,1)·N(0,I) tốt hơn Gauss?** Trong 768 chiều, nhiễu Gauss có chuẩn gần như cố định; nhân thêm hệ số đều ngẫu nhiên cho chuẩn đa dạng → phủ được nhiều "khoảng cách" tới vùng ảnh hơn.
6. **Liên hệ với môn học?** Mô hình tìm kiếm cổ điển (nhu cầu → truy vấn → xếp hạng); đánh giá bằng Precision/Recall mở rộng thành R@K, mAP@K; tìm kiếm vector là mô hình xếp hạng, khác mô hình Boolean khớp chính xác dựa trên chỉ mục ngược.

## Về tái hiện
7. **Vì sao chỉ 5.000 bước thay vì 20.000?** T4 ~2,4 s/bước → 20.000 bước ≈ 13 giờ/run, vượt giới hạn phiên 12 giờ và hạn mức ~30 giờ/tuần cho 12+ run. Mọi biến thể cùng 5.000 bước nên so sánh vẫn công bằng; đường học cho thấy [CHỜ: đã/ chưa bão hòa].
8. **Kết quả tái hiện có khớp bài báo không?** [CHỜ: EXP-000 vs Bảng 5 của bài báo]. CIRCO bài báo báo cáo trên test, nhóm đo trên val nên chỉ so tương đối.
9. **Làm sao chắc code đã sửa vẫn đúng?** So vector nhúng của encoder viết lại với CLIP gốc: sai lệch 0,00 trên ViT-B/32 và ViT-L/14; checkpoint chính thức nạp khớp hoàn toàn; mAP CIRCO của script mới trùng tuyệt đối hàm gốc.
10. **Bài báo và code khác nhau ở đâu?** φ không có LayerNorm; dữ liệu có thêm prompt Midjourney; cụm từ khóa giữ cả từ hạn định.
11. **Sao không dùng CIRR?** Ảnh CIRR (NLVR2) cần đăng ký, đang chờ duyệt; bổ sung khi có.

## Về cải tiến và chứng minh
12. **Vì sao InfoNCE giúp?** MSE chỉ kéo ẑ về z của chính câu đó, không đẩy xa câu khác; đánh giá là xếp hạng → cần tính phân biệt; InfoNCE dùng 511 mẫu âm trong batch và tối ưu theo cosine như lúc truy xuất.
13. **Sao giữ MSE?** Giữ chuẩn và vị trí tuyệt đối của vector (InfoNCE chỉ quan tâm hướng); bỏ hẳn có thể làm [$] lệch khỏi phân phối token thật.
14. **Δ tính từ đâu, có rò rỉ dữ liệu đánh giá không?** 5.000 cặp COCO val2017, độc lập với FashionIQ và CIRCO (CIRCO dùng COCO unlabeled, khác tập).
15. **Chọn λ = α = 0,5 thế nào?** Giá trị khởi điểm hợp lý, không quét vì giới hạn GPU; ghi là hạn chế. Quét trên tập dev riêng là hướng phát triển.
16. **"Tốt hơn" nghĩa là gì?** Δ > 0 và p < 0,05 theo paired bootstrap trên từng truy vấn (trung bình qua 3 seed), kèm Wilcoxon và khoảng tin cậy 95%. [CHỜ: kết quả]
17. **Tại sao không chọn checkpoint tốt nhất?** Chọn theo tập báo cáo sẽ làm kết quả lạc quan giả; dùng checkpoint cuối cho mọi biến thể là công bằng.
18. **Nếu cải tiến không tốt hơn thì sao?** Vẫn báo cáo trung thực; phân tích qua modality gap và đường học để giải thích. [CHỜ]
19. **Chi phí của cải tiến?** A: +~5% thời gian/bước; B: thêm một vector Δ tính một lần; suy luận không đổi.
20. **Nếu làm tiếp sẽ làm gì?** Đủ 20.000 bước, quét λ/α, CIRR + CIRCO test, hướng C (IDF), backbone lớn hơn.
