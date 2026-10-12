---
name: roadmap
description: Lộ trình và checklist toàn dự án LinCIR, phân rõ việc AI làm và việc người dùng/nhóm làm, kèm đầu vào–đầu ra của từng việc. Dùng khi người dùng hỏi tiến độ, hỏi "làm gì tiếp", báo đã xong một việc, hoặc trước khi bắt đầu một việc mới để kiểm tra điều kiện.
---

# Lộ trình dự án

Checklist nằm ở `checklist.md` cùng thư mục với file này. Mỗi việc có ID (`Axx` = AI làm, `Uxx` = người làm), người làm, đầu vào (**Cần**), đầu ra (**Ra**) và task id tương ứng trên checklist nhóm.

## Khi người dùng hỏi tiến độ hoặc "làm gì tiếp"

1. Đọc `checklist.md`.
2. Liệt kê các việc **sẵn sàng làm**: chưa xong và mọi việc trong cột **Cần** đã `[x]`. Tách làm hai nhóm:
   - **AI làm được ngay**: đề nghị bắt đầu luôn.
   - **Cần Bạn/Nhóm làm**: nói rõ làm gì, sản phẩm cần đưa lại cho AI là gì, và việc đó mở khóa việc nào.
3. Nêu việc đang chặn đường găng (xem cuối `checklist.md`), nếu có.

## Trước khi bắt đầu một việc

- Kiểm tra cột **Cần**. Nếu đầu vào chưa có, không làm giả: báo việc nào đang thiếu và ai cần làm. Ngoại lệ đã ghi trong bảng (ví dụ A08 được làm trước U04 rồi chỉnh sau).
- Đánh dấu `[~]` khi bắt đầu.

## Khi một việc xong

- Việc 🤖: chỉ đánh `[x]` khi sản phẩm ở cột **Ra** thực sự tồn tại và đã kiểm tra (file có, script chạy được, số liệu có nguồn).
- Việc 👤/👥: chỉ đánh `[x]` khi người dùng xác nhận, hoặc thấy sản phẩm của việc đó (ví dụ thư mục run có `per_query_*.csv`).
- Thêm một dòng vào mục **Nhật ký** cuối `checklist.md`: ngày tuyệt đối, ID, ghi chú ngắn.
- Nếu việc có task id trên checklist nhóm (cột **Nhóm**) và toàn bộ task đó đã xong, đề nghị tick bằng skill `update-checklist`.
- Cập nhật dòng "Cập nhật lần cuối".

## Khi kế hoạch thay đổi

Thêm, bỏ hoặc đổi việc trực tiếp trong `checklist.md`, giữ nguyên ID cũ (không đánh số lại), cập nhật sơ đồ phụ thuộc, và ghi lý do vào `docs/decisions.md`.

## Ranh giới

- AI không chạy train dài trên máy này (Apple M1, không có GPU NVIDIA). Mọi việc train/đánh giá thật là việc 👤 trên máy GPU; AI chuẩn bị lệnh, notebook và đọc kết quả.
- AI không tự commit, push, gửi gì ra ngoài khi chưa được đồng ý (A05 cần Bạn đồng ý).
- Không tick việc thay người khác khi chưa có xác nhận.
