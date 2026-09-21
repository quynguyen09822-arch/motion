# Cấu trúc cơ sở dữ liệu — Motion

> Soạn 21/09/2026 theo yêu cầu của Quý: một cấu trúc CSDL hoàn chỉnh để trình bày
> và bảo vệ dự án.
>
> **Đây là THIẾT KẾ, app hiện chưa dùng CSDL.** Mọi thứ đang nằm ở file. Phần
> cuối nói rõ cái giá của việc chuyển, và vì sao có chỗ **không nên** chuyển.

---

## 0. Hiện trạng: app đang lưu ở đâu

| Thứ | Đang nằm ở | Mất khi dựng lại container? |
|---|---|---|
| Kịch bản clip | `scenes/<slug>.json` | **có**, nếu không gắn ổ lưu |
| Kho riêng từng người | `kho/<mã>/scenes/` | **có** |
| Bản nháp tự lưu | `.drafts/` | **có** |
| Kho sao lưu | `.hub-video-backups/` | **có** |
| Nhật ký lượt dùng | `.nhat-ky/dung.jsonl` | **có** |
| Hạn mức chi tiêu ngày | **chỉ trong bộ nhớ** (`new Map()`) | **có, mỗi lần restart** |
| Tài khoản + mật khẩu | biến môi trường | không |
| Video đã xuất | `out/*.mp4` | **có** |
| Giọng đọc AI | `public/voice/` | **có** |

Hai dòng đáng chú ý:

- **Hạn mức chi tiêu nằm trong RAM.** Restart là bộ đếm về 0 — ai cũng được cấp
  lại 300 lượt AI và 20.000 ký tự đọc. Đây là lỗ thật về chi phí, và là lý do
  mạnh nhất để có CSDL.
- **Tài khoản khai bằng biến môi trường.** Thêm một người là phải sửa cấu hình
  rồi triển khai lại. Không có "quên mật khẩu", không có phân quyền.

---

## 1. Nguyên tắc: cái gì vào CSDL, cái gì KHÔNG

Đây là phần quan trọng nhất của thiết kế, và cũng là chỗ dễ làm sai nhất.

**Vào CSDL** — thứ cần hỏi, đếm, lọc, hoặc phải đúng khi nhiều người cùng ghi:
tài khoản, dự án, phiên bản, nhật ký, hạn mức, hàng đợi việc.

**KHÔNG vào CSDL** — file nhị phân lớn: video xuất ra, ảnh, file giọng đọc.
Chúng đi vào **ổ lưu hoặc kho đối tượng**, CSDL chỉ giữ đường dẫn. Nhét video
30 MB vào một cột `bytea` là biến bản sao lưu CSDL thành hàng chục GB, và mọi
truy vấn chậm theo.

**Kịch bản clip dùng `JSONB`, KHÔNG băm nhỏ thành bảng.** Một cảnh có cây thành
phần lồng nhau nhiều tầng, mỗi loại trong 25 loại lại có bộ trường riêng. Băm ra
thành `element` / `element_prop` là tự tạo cho mình một bộ ORM để rồi ghép lại
y như cũ mỗi lần đọc — chậm hơn, và **`validateScene` vẫn là thẩm quyền quyết
định hợp lệ**, không phải ràng buộc của bảng. PostgreSQL đánh chỉ mục được vào
trong JSONB khi cần lọc.

---

## 2. Sơ đồ quan hệ

```
nguoi_dung ──< kho ──< du_an ──< ban_luu
     │                   │
     │                   ├──< ban_nhap   (0..1 mỗi dự án)
     │                   ├──< viec       (xuất video, kiểm bố cục)
     │                   └──< tep        (video, giọng đọc, ảnh)
     │
     ├──< nhat_ky_dung
     ├──< han_muc_ngay
     └──< phien
```

---

## 3. Bảng

### 3.1 `nguoi_dung` — tài khoản

```sql
CREATE TABLE nguoi_dung (
  id            BIGSERIAL PRIMARY KEY,
  email         CITEXT      NOT NULL UNIQUE,      -- không phân biệt hoa thường
  ten           TEXT        NOT NULL DEFAULT '',
  mat_khau_bam  TEXT,                             -- scrypt; NULL = chưa đặt
  vai           TEXT        NOT NULL DEFAULT 'nguoi_dung'
                CHECK (vai IN ('nguoi_dung', 'quan_tri')),
  dang_hoat_dong BOOLEAN    NOT NULL DEFAULT TRUE,
  tao_luc       TIMESTAMPTZ NOT NULL DEFAULT now(),
  vao_lan_cuoi  TIMESTAMPTZ
);
```

`CITEXT` chứ không phải `TEXT`: `Quy@matbao.com` và `quy@matbao.com` là **một
người**. Để `TEXT` thì hai bản ghi cùng tồn tại và kho bị tách làm đôi.

`mat_khau_bam` cho `NULL` để giữ đúng hành vi hiện tại — chưa đặt mật khẩu thì
không hỏi ai. Chuỗi rỗng khác `NULL`: rỗng nghĩa là "cố ý không có".

### 3.2 `kho` — kho dự án riêng

```sql
CREATE TABLE kho (
  id            BIGSERIAL PRIMARY KEY,
  chu_id        BIGINT      REFERENCES nguoi_dung(id) ON DELETE RESTRICT,
  ma            TEXT        NOT NULL UNIQUE,      -- 'goc' hoặc mã băm theo email
  la_goc        BOOLEAN     NOT NULL DEFAULT FALSE,
  tao_luc       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX kho_chi_mot_goc ON kho ((la_goc)) WHERE la_goc;
```

Chỉ được **một** kho gốc — chỉ mục riêng phần lo việc đó, không dựa vào kỷ luật
của người viết code.

`ON DELETE RESTRICT`: xoá người dùng **không** được kéo theo kho. Muốn xoá thì
phải xử lý kho trước, có chủ đích.

### 3.3 `du_an` — một clip

```sql
CREATE TABLE du_an (
  id            BIGSERIAL PRIMARY KEY,
  kho_id        BIGINT      NOT NULL REFERENCES kho(id) ON DELETE CASCADE,
  slug          TEXT        NOT NULL,
  ten           TEXT        NOT NULL,
  doc           JSONB       NOT NULL,             -- cả kịch bản: meta + scenes
  rong          INT         GENERATED ALWAYS AS ((doc->'meta'->>'width')::INT) STORED,
  cao           INT         GENERATED ALWAYS AS ((doc->'meta'->>'height')::INT) STORED,
  so_canh       INT         GENERATED ALWAYS AS (jsonb_array_length(doc->'scenes')) STORED,
  xoa_luc       TIMESTAMPTZ,                      -- xoá mềm, xem ghi chú dưới
  tao_luc       TIMESTAMPTZ NOT NULL DEFAULT now(),
  sua_luc       TIMESTAMPTZ NOT NULL DEFAULT now(),
  sua_boi       BIGINT      REFERENCES nguoi_dung(id),
  UNIQUE (kho_id, slug)
);
CREATE INDEX du_an_kho_moi ON du_an (kho_id, sua_luc DESC) WHERE xoa_luc IS NULL;
```

Ba điều cố ý:

- **`UNIQUE (kho_id, slug)`, không phải `UNIQUE (slug)`.** Hai người được có
  dự án cùng tên trong kho riêng của mỗi người. Khoá toàn cục là vô tình cho
  người vào trước chiếm mất cái tên.
- **Cột suy ra (`GENERATED … STORED`)** cho khổ hình và số cảnh: màn hình kho
  cần chúng để hiện thẻ, mà bóc JSONB mỗi lần thì chậm. Suy ra từ chính `doc`
  nên **không bao giờ lệch** — khác hẳn việc chép tay vào một cột riêng.
- **Xoá mềm (`xoa_luc`).** Tính năng xoá vừa làm đã cất bản lùi vào kho sao lưu;
  ở CSDL thì đánh dấu rẻ hơn và lùi được ngay. Dọn hẳn bằng một việc chạy định
  kỳ, sau 30 ngày.

### 3.4 `ban_luu` — lịch sử từng lần lưu

```sql
CREATE TABLE ban_luu (
  id            BIGSERIAL PRIMARY KEY,
  du_an_id      BIGINT      NOT NULL REFERENCES du_an(id) ON DELETE CASCADE,
  doc           JSONB       NOT NULL,
  nhan          TEXT,                             -- "kéo đổi chỗ", "AI dựng cảnh"
  luu_boi       BIGINT      REFERENCES nguoi_dung(id),
  luu_luc       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ban_luu_theo_du_an ON ban_luu (du_an_id, luu_luc DESC);
```

Thay đúng vai trò của `.hub-video-backups/`. `nhan` lấy từ `kho.sua(nhãn, việc)`
đang có sẵn trong `web/store.js` — nhãn tiếng Việt tả việc vừa làm, nên lịch sử
đọc được chứ không phải một dãy thời gian.

Dọn theo đúng luật đang chạy: giữ 50 bản gần nhất, cộng tất cả bản trong 7 ngày.

### 3.5 `ban_nhap` — nháp tự lưu

```sql
CREATE TABLE ban_nhap (
  du_an_id      BIGINT      PRIMARY KEY REFERENCES du_an(id) ON DELETE CASCADE,
  doc           JSONB       NOT NULL,
  sua_luc       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Khoá chính **chính là** `du_an_id`: mỗi dự án nhiều nhất một nháp. Đây là cách
ràng buộc "0..1" bằng cấu trúc thay vì bằng code.

### 3.6 `tep` — video, giọng đọc, ảnh

```sql
CREATE TABLE tep (
  id            BIGSERIAL PRIMARY KEY,
  du_an_id      BIGINT      REFERENCES du_an(id) ON DELETE SET NULL,
  loai          TEXT        NOT NULL
                CHECK (loai IN ('video_xuat', 'giong_doc', 'anh', 'nhac', 'tieng_dong')),
  duong_dan     TEXT        NOT NULL,             -- đường dẫn trên ổ lưu
  ten_hien      TEXT        NOT NULL,
  co_byte       BIGINT      NOT NULL,
  dinh_dang     TEXT,                             -- mp4 · webm · gif · mp3
  giay          NUMERIC(8,2),
  bam_noi_dung  TEXT,                             -- sha256, để khỏi lưu trùng
  tao_luc       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX tep_theo_du_an ON tep (du_an_id, tao_luc DESC);
```

**CSDL giữ đường dẫn, không giữ byte.** `ON DELETE SET NULL` chứ không `CASCADE`:
xoá dự án thì video đã xuất **vẫn còn** — người ta đã gửi nó cho khách rồi.

### 3.7 `viec` — hàng đợi việc nặng

```sql
CREATE TABLE viec (
  id            BIGSERIAL PRIMARY KEY,
  du_an_id      BIGINT      REFERENCES du_an(id) ON DELETE CASCADE,
  nguoi_id      BIGINT      REFERENCES nguoi_dung(id),
  loai          TEXT        NOT NULL CHECK (loai IN ('xuat', 'kiem', 'chuyen')),
  trang_thai    TEXT        NOT NULL DEFAULT 'dang_cho'
                CHECK (trang_thai IN ('dang_cho', 'dang_chay', 'xong', 'hong', 'huy')),
  tien_do       SMALLINT    NOT NULL DEFAULT 0 CHECK (tien_do BETWEEN 0 AND 100),
  doan_giay     NUMERIC(8,2),
  tham_so       JSONB       NOT NULL DEFAULT '{}',
  ket_qua_tep   BIGINT      REFERENCES tep(id),
  cau_loi       TEXT,
  bat_dau       TIMESTAMPTZ,
  ket_thuc      TIMESTAMPTZ,
  tao_luc       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX viec_dang_cho ON viec (tao_luc) WHERE trang_thai = 'dang_cho';
```

App đang giữ luật **một slot việc nặng, không bao giờ hai** (`jobs.js`) — vì bộ
xuất để khung hình tạm theo `cwd`, hai lệnh song song đẻ ra hai video hỏng trong
im lặng. Ở CSDL, luật đó giữ bằng:

```sql
CREATE UNIQUE INDEX viec_mot_slot ON viec ((1)) WHERE trang_thai = 'dang_chay';
```

Một chỉ mục thay cho một đoạn code mà ai cũng có thể quên.

### 3.8 `nhat_ky_dung` — ai dùng gì, lúc nào

```sql
CREATE TABLE nhat_ky_dung (
  id            BIGSERIAL PRIMARY KEY,
  luc           TIMESTAMPTZ NOT NULL DEFAULT now(),
  viec          TEXT        NOT NULL,             -- 'luu' · 'khoi-phuc' · 'xoa-du-an'
  nguoi_id      BIGINT      REFERENCES nguoi_dung(id) ON DELETE SET NULL,
  du_an_slug    TEXT,                             -- giữ CHUỖI, xem ghi chú
  so_canh       INT,
  them          JSONB
);
CREATE INDEX nhat_ky_theo_ngay ON nhat_ky_dung (luc DESC);
```

`du_an_slug` giữ **chuỗi** chứ không phải khoá ngoại: xoá dự án rồi thì con số
thống kê *"tháng trước sửa 47 clip"* vẫn phải đúng. Nhật ký là sổ ghi chép,
không phải bản sao của hiện trạng — và đây chính là lý do `nhatky.js` hiện tại
ghi append-only, không bao giờ sửa dòng cũ.

### 3.9 `han_muc_ngay` — trần chi tiêu

```sql
CREATE TABLE han_muc_ngay (
  ngay          DATE        NOT NULL,             -- theo múi giờ VN
  loai          TEXT        NOT NULL CHECK (loai IN ('goiAI', 'kyTu', 'xuat')),
  nguoi_id      BIGINT      NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
  da_dung       INT         NOT NULL DEFAULT 0,
  PRIMARY KEY (ngay, loai, nguoi_id)
);
```

**Đây là bảng đáng giá nhất trong cả thiết kế.** Hiện `hanmuc.js` đếm bằng
`new Map()` trong RAM, nên **mỗi lần restart là bộ đếm về 0** — ai cũng được cấp
lại 300 lượt gọi AI và 20.000 ký tự đọc. Đưa vào CSDL là bịt lỗ đó.

Tăng bằng một câu, an toàn khi nhiều người cùng gọi:

```sql
INSERT INTO han_muc_ngay (ngay, loai, nguoi_id, da_dung)
VALUES ($1, $2, $3, $4)
ON CONFLICT (ngay, loai, nguoi_id)
DO UPDATE SET da_dung = han_muc_ngay.da_dung + EXCLUDED.da_dung
RETURNING da_dung;
```

### 3.10 `phien` — vé đăng nhập

```sql
CREATE TABLE phien (
  id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  nguoi_id      BIGINT      NOT NULL REFERENCES nguoi_dung(id) ON DELETE CASCADE,
  het_han       TIMESTAMPTZ NOT NULL,
  tao_tu_ip     INET,
  tao_luc       TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX phien_don_dep ON phien (het_han);
```

Có bảng này mới **thu hồi** được vé. Cách hiện tại (vé ký HMAC, không lưu) sống
được qua restart nhưng **không đuổi ai ra giữa chừng được** — mất máy là vé còn
dùng tới lúc hết hạn.

### 3.11 `thanh_phan_luu` — kho thành phần người dùng tự lưu

```sql
CREATE TABLE thanh_phan_luu (
  id            BIGSERIAL PRIMARY KEY,
  kho_id        BIGINT      NOT NULL REFERENCES kho(id) ON DELETE CASCADE,
  ten           TEXT        NOT NULL,
  nhom          TEXT        NOT NULL DEFAULT 'khac',   -- 'nen' · 'cum' · 'chu'
  noi_dung      JSONB       NOT NULL,             -- một món, hoặc một cụm
  anh_nho       TEXT,                             -- đường dẫn ảnh xem trước
  dung_bao_lan  INT         NOT NULL DEFAULT 0,
  tao_luc       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (kho_id, ten)
);
```

Bảng cho đúng tính năng Quý nêu: *"lưu các thành phần mới như là nền các thứ"*.
`KIT` trong `web/them.js` hiện viết cứng; bảng này là phần **thêm vào**, không
thay thế — bộ dựng sẵn của nhà vẫn nằm trong mã.

---

## 4. Quyền xem: một người chỉ thấy kho của mình

Đừng dựa vào câu `WHERE kho_id = $1` rải khắp nơi — sót một chỗ là lộ dữ liệu.
PostgreSQL làm được ở tầng bảng:

```sql
ALTER TABLE du_an ENABLE ROW LEVEL SECURITY;

CREATE POLICY du_an_cua_toi ON du_an
  USING (kho_id IN (
    SELECT id FROM kho
    WHERE chu_id = current_setting('app.nguoi_id')::BIGINT
       OR la_goc AND current_setting('app.vai') = 'quan_tri'
  ));
```

Mỗi request đặt `SET LOCAL app.nguoi_id = …` sau khi xác thực. Từ đó **quên
`WHERE` cũng không lộ**.

---

## 5. Đường di trú — đi bốn bước, không đi một bước

| Bước | Làm gì | Lùi được không |
|---|---|---|
| 1 | Dựng bảng, **chưa đụng app**. Viết script đổ dữ liệu từ file vào. | có, xoá CSDL là xong |
| 2 | **Ghi hai nơi**: file vẫn là chính, CSDL ghi theo. Đối chiếu hằng ngày. | có |
| 3 | Đọc từ CSDL, file thành bản lùi. | có, lật một cờ |
| 4 | Bỏ đường ghi file. | khó — chỉ làm sau khi bước 3 chạy êm vài tuần |

Bước 2 là bước người ta hay bỏ qua, và là bước duy nhất cho biết cấu trúc mới có
giữ đúng dữ liệu cũ hay không **trước khi** phụ thuộc vào nó.

---

## 6. Cái giá phải nói thẳng

**Repo này có luật "không gói phụ thuộc, không bước dựng".** `package.json` không
có `dependencies` nào, và đó là chủ ý — `server/router.js` ghi rõ lý do: công cụ
mà người không rành kỹ thuật phải dựa vào thì không được có kiểu hỏng "cài gói
thất bại".

Thêm CSDL là **phá luật đó**: cần trình điều khiển `pg`, cần `node_modules`,
cần bước cài lúc dựng ảnh. Đây là quyết định kiến trúc, không phải một việc kỹ
thuật.

Nên nói cho công bằng — **hai đường**:

| | Gắn ổ lưu (volume) | Chuyển sang CSDL |
|---|---|---|
| Sửa mã | **không dòng nào** | đổi mọi đường đọc/ghi |
| Giữ được luật zero-dependency | **có** | không |
| Cứu được dữ liệu khi dựng lại | **có** | có |
| Sửa lỗi hạn mức đếm trong RAM | không | **có** |
| Nhiều người sửa cùng lúc | không | **có** |
| Hỏi/đếm/báo cáo | phải đọc cả thư mục | **một câu SQL** |

**Nếu mục tiêu chỉ là "clip không bay khi dựng lại" thì gắn ổ lưu là xong** —
`docker-compose.yml` đã khai sẵn bốn ổ, chỉ thiếu `motion-kho:/app/kho`.

**CSDL đáng làm khi** cần một trong ba thứ: nhiều người dùng thật, hạn mức chi
tiêu đếm đúng qua restart, hoặc báo cáo số liệu cho cấp trên.

---

## 7. Toàn bộ DDL

Chạy được nguyên khối trên PostgreSQL 14 trở lên:

```sql
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pgcrypto;   -- cho gen_random_uuid()
```

Rồi 11 bảng theo thứ tự mục 3.1 → 3.11 (thứ tự đó đã đúng chiều khoá ngoại,
chạy từ trên xuống không vướng).
