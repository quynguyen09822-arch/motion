# Đăng nhập và logo

## Đặt mật khẩu

```bash
npm run dat-mat-khau
```

Gõ mật khẩu hai lần (không hiện trên màn hình), nó cất **dạng băm** vào `.env`
của repo này. Khởi động lại là app bắt đầu hỏi mật khẩu.

Muốn bỏ: xoá dòng `MOTION_MAT_KHAU_HASH` trong `.env`.

> **`.env` đã được `.gitignore`.** Băm mật khẩu và khoá ký phiên tuyệt đối không
> được lên GitHub. Trước khi làm tính năng này, `.env` **chưa** bị bỏ qua — đã thêm.

## Không bao giờ khoá chính chủ ra ngoài

**Chưa đặt mật khẩu thì app chạy y như trước**, chỉ hiện một chip cảnh báo *"Chưa
đặt mật khẩu"* trên thanh trên.

Bắt đăng nhập ngay khi chưa ai kịp đặt mật khẩu là khoá chính chủ ra khỏi công cụ
của họ, và cách duy nhất để vào lại là sửa file trên máy chủ — thứ mà người dùng
của công cụ này không làm được.

## Cách làm, và vì sao

| | |
|---|---|
| **Băm** | `scrypt` + muối ngẫu nhiên. Cùng một mật khẩu, hai lần băm ra hai chuỗi khác nhau — không có muối thì một bảng tra sẵn là đủ để phá. |
| **So sánh** | `timingSafeEqual`, và **kiểm độ dài trước** — hàm đó ném lỗi nếu hai bên khác độ dài, tức là một mật khẩu dài bất thường làm sập máy chủ thay vì bị từ chối. |
| **Vé phiên** | chuỗi tự chứng thực `payload.chữ-ký`, ký bằng HMAC. Không lưu trong bộ nhớ → **khởi động lại máy chủ không đá ai ra**, mà công cụ này khởi động lại rất thường xuyên. |
| **Cookie** | `HttpOnly` (script lạ không đọc được vé) · `SameSite=Lax` · `Secure` **chỉ khi thật sự chạy https**. |
| **Đếm gõ sai** | sai 8 lần trong 15 phút là khoá theo địa chỉ máy. Đang khoá thì **gõ đúng cũng không vào được** — nếu không, bộ đếm chỉ là đồ trang trí. |
| **Khoá ký** | sinh một lần rồi cất vào `.env`. Sinh mới mỗi lần khởi động là mọi người bị đá ra sau mỗi lần khởi động lại. |

`Secure` bật bừa là một cái bẫy thật: trình duyệt sẽ không gửi cookie ở
`http://127.0.0.1`, và đăng nhập thành **vòng lặp không bao giờ vào được**.

## Đường nào mở khi chưa đăng nhập

Danh sách **trắng**, không phải đen:

```
/dang-nhap  /api/dang-nhap  /api/dang-xuat  /health  /api/health
/dang-nhap.css  /logo/motion-mark.png  /logo/motion-full.png  /logo/favicon.png
```

Mọi thứ khác — kể cả `/clip/*` (file của dự án clip) — đều qua cửa.

**Lời gọi API trả `401`, trang trả `302`.** Giao diện gọi `fetch` mà nhận về trang
HTML đăng nhập thì nó vỡ ở `JSON.parse`, và người dùng thấy một lỗi vô nghĩa.

Trang bị chặn thì `302` kèm `?tiep=…` để vào xong quay lại đúng chỗ đang định tới.

## Logo

File gốc anh gửi: `public/image.png` (1254×1254, **nền trắng**, 1,25 MB). Đặt thẳng
lên giao diện tối sẽ ra một ô trắng, nên đã xử lý:

| File | Dùng ở đâu |
|---|---|
| `web/logo/motion-mark.png` | dấu M, nền trong suốt, 242×128 — thanh trên + trang đăng nhập |
| `web/logo/motion-mark-64.png` | bản nhỏ |
| `web/logo/motion-full.png` | trọn bộ có chữ — **chỉ dùng trên nền sáng** |
| `web/logo/favicon.png` | biểu tượng tab |

Tách nền trắng bằng `colorkey=0xFFFFFF:0.18:0.06`. Đã thử ba mức (0.10 / 0.18 /
0.26) và **soi trên nền tối** để bắt viền trắng còn sót; mức giữa sạch nhất.

**Chữ "Motion" trên giao diện là CHỮ THẬT, không phải ảnh.** Hai lý do: chữ trong
file logo gốc là xanh navy đậm, đặt lên nền tối gần như mất hút; và chữ nhúng
trong ảnh thì mờ khi phóng to. Ảnh chỉ lo phần dấu M.

Ảnh cao 128px thu xuống 15px nên nét vẫn sắc trên màn hình 2× — **đừng thay bằng
bản nhỏ hơn**, bài kiểm có mục canh điều đó.

## Chạy kiểm

```bash
node tools/kiem-dang-nhap.mjs
```

38 mục. Nó **dựng máy chủ riêng trên cổng khác** và truyền mật khẩu bằng biến môi
trường — không đụng `.env` thật. Mục 8 canh đúng điều đó: chạy xong `.env` phải
không có dấu vết nào của bài kiểm.

> Một bài kiểm mà sửa cấu hình thật thì chạy xong người dùng bị khoá ra ngoài.
