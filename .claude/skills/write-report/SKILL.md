---
name: write-report
description: Viết hoặc sửa các phần của báo cáo và slides BTL LinCIR bằng tiếng Việt, lấy số liệu từ results/ đã đóng băng. Dùng khi soạn báo cáo, slides, kịch bản thuyết trình hoặc câu hỏi Q&A.
---

# Viết báo cáo và slides

## Quy trình sinh báo cáo

```bash
python report/make_figures.py            # hình phương pháp (không phụ thuộc kết quả)
python scripts/make_report_assets.py     # bảng + hình kết quả từ experiments/runs → results/
python report/build_report.py            # → report/BaoCao_Nhom8_LinCIR.docx (theo mẫu NOS Nhóm 10)
```
Nội dung báo cáo nằm trong `report/build_report.py` (các hàm chapter1…chapter6). Sửa nội dung ở đó rồi chạy lại, không sửa tay file .docx (sẽ bị ghi đè). Sau khi mở trong Word: Cmd/Ctrl+A rồi F9 để cập nhật mục lục, danh mục hình/bảng. Giới hạn 25–30 trang.

## Lưu ý: báo cáo đã được sửa tay (2026-10-08)

`report/BaoCao_Nhom8_LinCIR.docx` là bản Tâm đã chỉnh tay. `build_report.py` phát hiện điều này và chỉ ghi `BaoCao_Nhom8_LinCIR_auto.docx`. Khi có kết quả: sinh bản `_auto` để lấy bảng/hình/đoạn mới, rồi chèn vào bản sửa tay (sửa XML theo skill docx hoặc hướng dẫn Tâm dán), không thay cả file. Tài liệu học từng người: `docs/study/build_guides.py` (cập nhật các ô [[...]] rồi chạy lại + `to_pdf.sh`).

## Điền kết quả vào bản sửa tay

1. `python scripts/make_report_assets.py` (bảng, hình, `results/assets.json`).
2. Viết `results/analysis_vi.json`: `main`, `sig`, `gap`, `curve`, `qual`, `conclusion`, `speed` (đoạn cho báo cáo); `title_14/15/16`, `slide_sig` [list], `slide_conclusion` [list] (cho slides). Mỗi khẳng định kèm số và p-value; kết quả âm viết trung thực.
3. `python report/fill_results.py` và `python slides/fill_results.py` (tự sao lưu), rồi `./report/update_fields.sh`, `./slides/to_pdf.sh` và xem lại PDF.

## Nguồn sự thật

- Số liệu: **chỉ** từ `results/tables/` và `results/FROZEN.md`. Không lấy số từ log rời hay trí nhớ. Nếu chưa đóng băng, ghi `[CHƯA CHỐT]` cạnh số.
- Nội dung bài báo: `papers/LinCIR_CVPR2024.pdf` (trích dẫn kèm số bảng/hình), `papers/SEARLE_ICCV2023.pdf`.
- Quyết định và lý do: `docs/decisions.md`. Thay đổi so với code gốc: tìm comment `# [NHOM8]` trong `code/`.

## Khung báo cáo (`report/`)

1. Giới thiệu — bài toán CIR, zero-shot CIR, động lực
2. Nghiên cứu liên quan — Pic2Word, SEARLE, CLIP, modality gap
3. Phương pháp LinCIR — SMP, nhiễu, suy luận
4. Đề xuất cải tiến — ý tưởng, công thức, giả thuyết
5. Thực nghiệm — dữ liệu, chỉ số, cài đặt, kết quả tái hiện
6. Kết quả và phân tích — bảng chính, kiểm định, ablation, cơ chế, định tính
7. Kết luận, hạn chế, hướng phát triển
Phụ lục — phân công, cấu hình, hướng dẫn chạy code

## Slides

`python slides/build_slides.py && ./slides/to_pdf.sh`. Quy chuẩn (Tâm): 16:9, trắng + xanh tươi, Morph mọi slide, chữ ≥ 20 pt, Helvetica, tiêu đề nêu thẳng ý chính, chân slide chỉ số trang, dùng sơ đồ `report/figures/*_slide.png`. **Slides đã được Tâm sửa tay (2026-10-09):** `build_slides.py` chỉ ghi `Slides_Nhom8_LinCIR_auto.pptx`; khi có kết quả, chèn số/hình vào bản sửa tay (sửa XML theo skill pptx, hoặc hướng dẫn Tâm), sửa tiêu đề slide 14–16 thành kết luận thật.

## Khung slides (`slides/`, 15–20 trang, ~15 phút)

Bài toán + ví dụ (1–2) → hạn chế phương pháp cũ (1) → LinCIR (3) → tái hiện (2) → cải tiến (2–3) → kết quả + kiểm định + ablation (3–4) → vì sao tốt hơn (2) → kết luận, Q&A (1).

## Văn phong

- Tiếng Việt học thuật, câu ngắn, chủ động. Thuật ngữ tiếng Anh để trong ngoặc ở lần đầu: "truy xuất ảnh kết hợp (Composed Image Retrieval, CIR)".
- Mỗi khẳng định về hiệu năng phải kèm số và nguồn (bảng nào, run nào, p-value).
- Kết quả không đạt cũng viết trung thực, kèm phân tích.
- Liên hệ kiến thức môn học khi phù hợp: Precision/Recall → R@K, mAP@K; TF-IDF; chỉ mục và tìm kiếm vector.
- Số liệu trong báo cáo và slides phải trùng khớp; trước khi giao bản cuối, đối chiếu lại từng con số với `results/`.
