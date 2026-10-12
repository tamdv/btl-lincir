# Dữ liệu

Thư mục này không được commit (xem `.gitignore`). Mỗi người tự tải về máy có GPU.

## Dữ liệu huấn luyện (tự tải)

`code/loader.py` tự tải 3 bộ caption từ HuggingFace vào `code/datasets/` ở lần chạy đầu:
- `dangne/gcc_caption_only` (CC3M captions)
- `FredZhang7/stable-diffusion-prompts-2.47M`
- `Geonmo/midjourney-prompts-only` (bài báo không nhắc tới bộ này)

## Benchmark đánh giá

Làm theo hướng dẫn của SEARLE: https://github.com/miccunifi/SEARLE/tree/main#data-preparation

| Thư mục | Dữ liệu | Ghi chú |
|---|---|---|
| `data/CIRR/` | CIRR (ảnh NLVR2 + captions) | Ảnh NLVR2 cần **đăng ký** — làm ngay tuần 1 |
| `data/FashionIQ/` | FashionIQ (dress, shirt, toptee) | Nhiều link ảnh gốc đã hỏng, dùng bản tải theo hướng dẫn SEARLE |
| `data/CIRCO/` | CIRCO (ảnh COCO unlabeled2017, ~19GB) | Tùy chọn, chỉ khi đủ ổ đĩa; test chấm trên server |

Ghi lại ngày tải và nguồn vào bảng dưới khi tải xong.

| Dữ liệu | Người tải | Ngày | Nguồn | Ghi chú |
|---|---|---|---|---|
