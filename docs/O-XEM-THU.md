# Ô xem thử dùng chung — đề xuất API (chờ duyệt)

> Theo `BANG-CHINH-V2.md`, phần **Hạ tầng**: *"Trước khi code, cho anh xem API
> của thành phần này (nhận gì, trả gì)."* Đây là bản đó. **Chưa viết dòng mã
> nào.**

## Ba điều đã đo, quyết định cả thiết kế

**① Không phải đụng `scene-player.html`.** Tham số `?scene=` của bộ dựng nhận cả
**đường dẫn tuyệt đối**, không chỉ tên clip:

```js
const url = /^https?:|^\//.test(name) ? name : `scenes/${name}.json`;
```

Nên chỉ cần trỏ nó vào một đường sinh cảnh mẫu là xong. Bộ dựng của dự án chung
**giữ nguyên** — đúng ràng buộc trong tài liệu của anh.

**② Không phải phá luật "chỉ `player.js` được chạm `window.__clip`".**
`player.js` vốn đã xuất ra `taoPlayer(iframe)` — một nhà máy nhận iframe và trả
về `san() · nap() · tua() · chay() · dung() · giay · thoiLuong`. Ô xem thử gọi
đúng hàm đó cho iframe của mình. Không thêm một đường chạm `__clip` nào.

**③ Mở nhiều ô cùng lúc chịu được.** Đo thật trong Chromium, mỗi ô là một iframe
bộ dựng đầy đủ:

| Số ô | Nạp xong | Nhịp vẽ của trang cha |
|---|---|---|
| 1 | 348ms | 55,3 /giây |
| 4 | 179ms | 55,3 /giây |
| 10 | 328ms | **52,3 /giây** |
| 16 | 355ms | 50,7 /giây |

Mốc nghiệm thu "10 ô cùng lúc không giật" — đạt. **Nhưng đây là máy lúc rảnh.**
Máy đang xuất video thì chậm hơn nhiều, nên vẫn phải dừng ô khi nó ra khỏi tầm
nhìn, đúng như tài liệu yêu cầu.

## API đề xuất

```js
import { taoOXemThu } from './o-xem-thu.js';

const o = taoOXemThu({
  hop,                      // phần tử DOM để gắn ô vào
  mon: 'text',              // món mẫu: 'text' | 'anh' | 'nut' | 'huyhieu'
  nhan: 'Trượt lên nhẹ',    // chữ hiện trong món mẫu
  vao: 'truot-len',         // id một gói trong KHO_VAO — hoặc null
  ra: null,                 // id một gói trong KHO_RA — hoặc null
  hieuUng: { soft: 3 },     // các núm hiệu ứng đang đặt
  lap: true,                // diễn xong thì diễn lại
});
```

Trả về:

```js
o.phanTu        // phần tử gốc, để xếp vào lưới thẻ
o.dat({ hieuUng: { soft: 5 } })   // đổi giá trị rồi diễn lại (gộp nhịp ~150ms)
o.chay()        // diễn
o.dung()        // đứng
o.huy()         // gỡ iframe, ngắt theo dõi — BẮT BUỘC gọi khi đóng bảng
```

Tự lo ba việc, người gọi không phải nghĩ:

- **Chỉ dựng iframe khi ô lọt vào tầm nhìn**, và `dung()` khi ra khỏi. Mười thẻ
  trong dải cuộn thì chỉ mấy thẻ đang thấy là chạy.
- **Gộp nhịp `dat()`** khoảng 150ms — kéo thanh trượt bắn ra vài chục lần một
  giây, không gộp thì mỗi lần là một lượt nạp lại.
- **Diễn lặp** bằng `tua(0)` + `chay()`, nghỉ ~250ms giữa hai lượt cho mắt kịp.

## Cảnh mẫu lấy ở đâu

Thêm một đường đọc: `GET /api/canh-mau?mon=text&vao=truot-len&soft=3`, trả về
một kịch bản **một món** đúng định dạng.

Vì sao dựng ở máy chủ chứ không ở trình duyệt:

- **Dùng lại `validateScene`**, không chép nó ra bản thứ hai (luật 7 trong
  `CLAUDE.md`: mượn, không chép). Cảnh mẫu sai định dạng thì ô xem thử nói dối,
  mà nói dối thì tệ hơn không có.
- Bộ dựng chỉ `fetch` được **đường dẫn**. `blob:` và `data:` **không lọt** qua
  phép thử `/^https?:|^\//` của nó — đã đọc kỹ chỗ đó.
- Một chỗ duy nhất định nghĩa món mẫu, thay vì rải trong giao diện.

Đã cân nhắc và **bỏ**: ghi file cảnh mẫu vào `clip/scenes/`. Làm vậy thì chúng
hiện lên trong danh sách clip của người dùng như clip thật.

## Ba chỗ cần anh quyết

**① Món mẫu trông ra sao.** Em định: một thẻ chữ trên nền xám nhạt, chữ là tên
gói đang xem (vd "Trượt lên nhẹ"). Với hiệu ứng ảnh thì dùng một ô ảnh giả.
Anh muốn khác thì nói trước khi em code.

**② Diễn lặp liên tục hay rê chuột mới diễn.** Em đề nghị **lặp liên tục các ô
đang thấy** — số đo ở trên cho thấy chịu được, và "thấy trước khi chọn" thì phải
thấy mà không cần thao tác. Nếu anh thấy 10 thứ nhúc nhích cùng lúc là rối thì
đổi sang rê-chuột-mới-diễn, sửa một dòng.

**③ Ô xem thử có cần nghe được không.** Em định **không** — xem mặt chuyển động
thôi, không tiếng. Mở 10 ô mà mỗi ô một tiếng thì thành ồn.

## Hai chỗ trong `BANG-CHINH-V2.md` cần sửa lại cho khớp mã

Không phải lỗi lớn, nhưng để nguyên thì prompt giao cho người khác sẽ dẫn sai:

**① Tên mảng.** Tài liệu ghi *"mảng `VAO` và `RA` trong schema.js"* và prompt
Việc 2 ghi *"mỗi thẻ một gói trong mảng VAO"*. Tên thật là **`KHO_VAO`** và
**`KHO_RA`**. Không có mảng nào tên trần là `VAO`.

**② Việc 1 nhắc 4 hiệu ứng, thực tế có 5 cái kiểu `bac`.** Tài liệu liệt kê
`soft`, `softIn`, `shadow`, `maskSoft`. Còn một cái nữa cùng kiểu:

```js
{ id: 'push', nhan: 'Đẩy máy chậm', kieu: 'bac', bac: BAC_DAY },
```

`push` dùng thang `BAC_DAY` (5 nấc: Không…Rõ), khác ba cái kia (`BAC_NHOE`,
`BAC_BONG`, 6 nấc). Anh quyết: đổi nốt `push` sang thanh kéo cho đồng bộ, hay
cố ý để yên vì nó là *tốc độ đẩy máy* chứ không phải *độ đậm*?

## Việc sẽ làm sau khi anh duyệt

1. `server/canhmau.js` + đường `GET /api/canh-mau`, mượn `validateScene`
2. `web/inspector/o-xem-thu.js` theo đúng API trên
3. `tools/kiem-o-xem-thu.mjs` — ba mốc nghiệm thu trong `BANG-CHINH-V2.md`:
   cùng token thì ô xem thử và clip thật **trùng chuyển động**, 10 ô không giật,
   đổi giá trị thì ô đổi theo trong nửa giây
