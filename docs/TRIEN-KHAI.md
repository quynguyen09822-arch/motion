# Triển khai lên Vibe Host

## Lỗi ban đầu và vì sao

Lần deploy đầu chết ở **`[01] Source Validation`**:

> Không nhận diện được ứng dụng ở gốc repo… chọn "Thư mục con" là một trong: `matbao-hub-video`.

Repo `quynguyen09822-arch/motion` trên GitHub chỉ có `README.md` + thư mục
`matbao-hub-video/`. Vibe Host quét gốc, không thấy `package.json`, nên dừng.

Repo ấy được tạo bằng **"Add files via upload"** (kéo thả trên web), không phải
`git push` — nên **48 commit ở máy chưa hề lên đó**.

## Lỗi thứ hai, chưa kịp hiện ra

Chỉnh "Thư mục con" chỉ đổi **chỗ chết**, không cứu được. Trình sửa là cửa sổ
nhìn vào dự án clip; `server/proj.js` kiểm 5 thứ lúc khởi động và ném lỗi nếu
thiếu. Repo không có `scenes/`, `scene-player.html`, `public/` — nên nó sẽ qua
được `[01]`–`[08]` rồi chết ở `[11] Health Check`.

## Cách sửa

**Đẩy repo ở máy lên** — repo ấy vốn đã có `package.json` **ở đúng gốc**, nên
không phải chọn thư mục con nữa, và 48 commit lên theo.

Kèm ba thứ mới:

1. **`clip/` — dữ liệu clip gói kèm, 2,3 MB.** Chỉ mang thứ 11 clip thật sự
   dùng. `public/` của dự án gốc nặng 147 MB, nhưng **đo ra thì các clip chỉ
   chạm tới 5 tệp, 1,6 MB** — phần còn lại là video nguồn chưa clip nào dùng.
2. **`Dockerfile`** — `node:22-alpine`, **không `npm install`** (ứng dụng không
   có gói phụ thuộc nào), chạy bằng người dùng `node`.
3. **`/health`** — nhịp tim rẻ cho bước `[11]`, không chạm đĩa.

## Bẫy đã vấp khi dựng ảnh Docker

Ảnh dựng xong, chạy lên là **chết ngay**:

```
Error: EACCES: permission denied, mkdir '/app/.hub-video-backups/_ban-goc-2026-09-16'
```

`COPY` tạo file thuộc quyền root, mà ta chạy bằng `node`. Ứng dụng **chụp một
bản gốc kịch bản ngay lúc khởi động** — đó là lưới an toàn của dữ liệu clip, và
một bản cho sửa được thì càng cần. Nên cách sửa đúng là **tạo sẵn hai thư mục
ghi được** (`.hub-video-backups/`, `.drafts/`) rồi `chown` cho `node`, chứ không
phải tắt phần sao lưu đi cho tiện.

## Đã kiểm tận nơi

| Việc | Kết quả |
|---|---|
| `docker build` | xong, ảnh **237 MB** |
| `docker run` + `HEALTHCHECK` | **healthy** |
| `/health` · `/api/clips` · `/` · bộ dựng · ảnh | **200** cả năm |
| Số clip đọc được | **11/11** |
| Mở bằng trình duyệt thật | clip hiện đúng, bảng lớp 9 dòng, **0 lỗi JS** |

## Giới hạn của bản triển khai

- **Không xuất được video** — cần `ffmpeg` + Chromium, cố ý không gói để ảnh nhẹ.
- **Không có 12 clip đời cũ** (`.html` rời) — không nằm trong repo.
- **Không thêm được nền video mới** — thư mục video nguồn không gói kèm.
- **Hai bản độc lập**: sửa trên mạng không về máy, sửa ở máy không lên mạng.

## Việc còn lại

Đẩy lên GitHub. Workspace **không có khoá GitHub** nên bước này cần người dùng —
xem lệnh trong phần bàn giao.
