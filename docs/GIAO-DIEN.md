# Giao diện — dựng lại theo bản Stitch

Bản dựng gốc: `stitch_d_n_kh_i_nghi_p/` (`code.html` + `screen.png`).
Ảnh so sánh trước/sau nằm trong `.kiem/`.

## Ba điều làm nên cái nhìn đó

Cả ba đều nằm trong `:root` của [`web/app.css`](../web/app.css), không rải rác:

1. **Khối nổi trên nền đen.** Nền trang là đen tuyệt đối, mỗi cột là một khối
   xám bo góc nổi lên, cách nhau 8px. Trước đây các cột dán liền nhau và ngăn
   bằng một sợi chỉ 1px — mắt phải tự đi tìm ranh giới.
2. **Nhấn xanh lá, chữ đen trên nhấn.** Xanh dương cũ trùng với màu chữ liên kết
   *và* với chính màu thương hiệu trong nhiều clip, nên khung chọn lẫn vào nội
   dung. Xanh lá không xuất hiện trong clip nào.
3. **Xám trung tính, không ám xanh.** Bảng màu cũ ám xanh dương ở mọi cấp
   (`#0e1420`, `#263349`…). Vỏ phần mềm ám màu thì màu thật của clip bị đọc
   lệch — đúng thứ không được phép xảy ra ở công cụ chỉnh màu.

## Những thứ trong bản dựng KHÔNG được dựng

Bản Stitch vẽ ra một trình dựng phim đầy đủ. Ứng dụng này không có những thứ đó,
và **vẽ nút cho một tính năng không tồn tại còn tệ hơn không vẽ gì** — người dùng
bấm vào, không có gì xảy ra, và từ đó họ nghi ngờ cả những nút thật.

| Trong bản dựng | Vì sao không dựng |
|---|---|
| Timeline nhiều track, sóng âm | Ứng dụng **không có âm thanh**. Track hình thì có dữ liệu thật (cảnh + `at`/`for`) — xem "Còn lại" |
| Vòng màu Lift/Gamma/Gain, LUT, phơi sáng, bão hoà | Không có trong `schema.js`, bộ dựng không đọc |
| Khử ồn AI, âm lượng | Không có âm thanh |
| Đồng bộ Cloud | Không có |
| Badge "4K UHD", "60 FPS" | Clip thật là 1280×720 / 720×1280. Thay bằng **kích thước thật** đọc từ `meta` |
| Thư viện media 18 mục | Không có kho tài nguyên — cột trái là cảnh + thành phần |

## Những thứ đã dựng, và đều chạy bằng dữ liệu thật

- **Thanh trên**: ô hiệu MB · tên clip · viên "chưa lưu" (cam) · kích thước
  khung hình thật · hoàn tác/làm lại tròn · nút Lưu xanh lá.
- **Cột trái**: hai mục xếp chồng (Cảnh · Thành phần) — **không** đổi sang tab,
  vì giấu danh sách cảnh sau một tab là bước lùi. Thêm **ô lọc theo tên**: một
  cảnh có tới 156 thành phần, cuộn tay là hết ngày. Gõ không dấu cũng ra
  (`chu` → `Chữ`), và lọc trong cụm vẫn giữ cụm cha để còn thấy đường.
- **Khung hình**: khung chọn thêm **chấm kéo hai góc** — nói thẳng "cái này kéo
  được" thay vì để người dùng thử mới biết.
- **Thanh phát dưới cùng**: tên cảnh đang đứng, nút chạy tròn trắng, thanh tua,
  đồng hồ. Tách hẳn khỏi khung xem, nên lúc phóng to khung thì chỗ điều khiển
  vẫn đứng yên.
- **Cột phải**: tab nền xám chữ xanh, tiêu đề mục chữ trắng in hoa, ô nhập nền
  xám bo nhỏ, thanh trượt rãnh mảnh núm tròn.

## Hai bẫy đã vấp khi dựng

**1. Nút Chạy là hình vẽ, nhưng chữ vẫn phải có thật.**
Ghi `nutChay.textContent = '❚❚ Dừng'` là **xoá luôn cả hai hình SVG** bên trong.
Chữ "Chạy"/"Dừng" nay nằm trong một `<span class="chi-doc">` ẩn với mắt nhưng
đọc được với trình đọc màn hình — và `tools/kiem-chay-dung.mjs` vẫn đọc đúng chữ
đó để biết nút có kẹt nhãn không. Đừng đổi lại thành ghi thẳng vào nút.

**2. Lời nhắc đè lên thanh phát.**
`.bao` neo `bottom: 26px`, mà thanh phát mới cao 62px — lời nhắc rơi đúng lên nút
Chạy. Nay neo 82px (62 + 8 khe + 12 hở).

## Phông chữ

`Be Vietnam Pro` tải từ Google Fonts, **kèm đủ đường lùi hệ thống** trong
`--font`: mạng hỏng thì giao diện vẫn đúng, chỉ khác nét chữ.

Tuyệt đối **không** nạp phông này vào clip. Clip phải đo được cỡ chữ trên mọi
máy (`measureFit()` của bộ dựng); thêm một phông mạng vào đó là mở đường cho
lỗi "máy này chữ vừa, máy kia chữ tràn".

## Còn lại

**Timeline một track cho cảnh** — dữ liệu có thật (`scenes[].start/duration`, và
`at`/`for` của món đang chọn), nên dựng được mà không phải bịa. Đây là mảnh lớn
nhất của bản Stitch chưa làm.
