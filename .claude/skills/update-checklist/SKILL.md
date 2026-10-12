---
name: update-checklist
description: Đánh dấu xong hoặc bỏ đánh dấu việc trong checklist dùng chung của Nhóm 8 (artifact trên claude.ai). Dùng khi một việc trong kế hoạch đã hoàn thành hoặc người dùng hỏi tiến độ nhóm.
---

# Cập nhật checklist nhóm

Checklist: https://claude.ai/artifact/Jons1Eq7odXT2kWWt4iYwj

- Dữ liệu nằm trong database của artifact, collection `tasks`, mỗi document id là task id (`p1-1` … `p6-3`).
- Document: `{"done": true|false, "by": null, "at": "<ISO 8601>"}`. Thiếu document nghĩa là chưa xong.

## Đọc tiến độ

Dùng tool `ArtifactData` với `action: "list"`, `collection: "tasks"`. Đối chiếu id với danh sách việc trong trang (đọc trang bằng `Artifact` `action: "read"` nếu cần tên việc).

## Đánh dấu xong

1. `ArtifactData` `get` document đó để lấy `version` (nếu đã tồn tại).
2. `set` với `{"done": true, "by": null, "at": "<giờ hiện tại>"}` và `if_version` nếu document đã có. Nhiều việc thì dùng `batch`.
3. Báo lại cho người dùng những id đã đổi.

Chỉ đánh dấu khi người dùng xác nhận việc đã xong hoặc có bằng chứng rõ (ví dụ run `done` trong registry ứng với việc đó). Không tự bỏ đánh dấu việc người khác đã tick.
