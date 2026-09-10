#!/usr/bin/env python3
"""Clip thử nghiệm: KÉO THẢ MỘT FILE HTML VÀO DASHBOARD RỒI NÓ CHẠY.

Kịch bản (13,6 giây, không lời):

  Cảnh 1 (0 → 5,4)   Dashboard Vibe Host hiện ra. Con trỏ nhặt tệp
                     `ttindex.html` ở góc trên rồi thả vào vùng nhận tệp.
  Cảnh 2 (5,4 → 9,8) Thanh tiến trình chạy, các bước lần lượt xong. Tới bước
                     cấp SSL thì một thẻ SSL bật ra GIỮA KHUNG HÌNH.
  Cảnh 3 (9,8 → 13,6) CAMERA ZOOM vào dashboard. Đèn database chuyển xanh,
                     rồi CDN. Trang đã chạy.

HỆ TOẠ ĐỘ — cùng kỷ luật với `ve-s02.py`:

  · Không có số rời rạc; mọi vị trí suy từ khối HÌNH HỌC.
  · Toạ độ bên trong dashboard là toạ độ TƯƠNG ĐỐI, `M()` cộng gốc vào.
  · `kiem_trong()` chặn thành phần thò ra ngoài khung hoặc ngoài khối cha.
  · `kiem_camera()` chặn khung ngắm zoom ra ngoài mép clip — lỗi này không
    báo gì, chỉ lòi nền trống ra ở rìa video.

BA CHỖ CỦA ĐỊNH DẠNG PHẢI BIẾT TRƯỚC, không thì dựng sai mà không hiểu vì sao:

  1. Phần tử THUỘC VỀ MỘT CẢNH. Sang cảnh khác là biến mất. Muốn dashboard
     đứng yên suốt ba cảnh thì phải KHAI LẠI ở từng cảnh — nên nó được viết
     thành hàm `dashboard()` gọi ba lần.
  2. `at` tính từ ĐẦU CẢNH, không phải từ đầu clip.
  3. Con trỏ chuột nằm NGOÀI `#cam` nên không bị camera phóng theo. Chỉ dùng
     nó ở cảnh không zoom.
"""
import json
import pathlib
import sys

W, H = 1280, 720
GOC = pathlib.Path('/home/coder/workspace/projects/clipVibehost/hosting-animatic-production')
OUT = GOC / 'scenes' / 'thu-trien-khai-html.json'
KIEM = pathlib.Path(__file__).parent / f'kiem-{OUT.stem}.json'

# ══ MÀU ════════════════════════════════════════════════════════════════════
NEN      = '#eef1f6'
NAV      = '#252b38'
NAV_SANG = '#333c4e'
GOI_NEN  = '#2f3849'
GIAY     = '#ffffff'
VIEN     = '#e3e7ee'
CAM      = '#ed7225'
CAM_MO   = '#fdece0'
XAM_NEN  = '#f2f4f8'
MUC      = '#1e2430'
MUC_NAV  = '#e9ecf3'
MUC_GOI  = '#aeb8ca'
MO       = '#8a93a6'
LUC      = '#1aa053'      # xanh lá "xong"
LUC_MO   = '#e4f6ec'
CHO      = '#c8cedb'      # xám "chưa tới"
TIM      = '#2b1b46'      # nền trang AIRTEX (đọc từ chính trang đó)
VANG     = '#f2c45a'      # vàng mặt trăng của trang AIRTEX

# ══ HÌNH HỌC ═══════════════════════════════════════════════════════════════
DX, DY = 48, 48                 # góc trái trên dashboard
DW, DH = W - 2 * DX, H - 2 * DY  # 1184 × 624
SW = 196                        # bề rộng thanh bên
MX = DX + SW                    # mép trái vùng chính (tuyệt đối)
MW = DW - SW                    # bề rộng vùng chính = 988
DAU_H = 84                      # chiều cao dải đầu vùng chính

LE_TRONG = 32                   # lề trong vùng chính
COT_TRAI_W = 520
COT_PHAI_W = 320
NOI_DUNG_Y = DAU_H + 36         # mép trên hai cột (tương đối dashboard)
NOI_DUNG_H = 400

# tuyệt đối
TX = MX + LE_TRONG                        # 276 — mép trái cột trái
PX = TX + COT_TRAI_W + 36                 # 832 — mép trái cột phải
NY = DY + NOI_DUNG_Y                      # 216

# Khung ngắm khi zoom. Camera đặt điểm (mx,my) vào giữa khung, độc lập với
# mức phóng: x = mx - W/2, y = my - H/2.
ZOOM = 1.38
# Mép trái khung ngắm phải nằm TRƯỚC chữ "Triển khai website" (ở x=276): ngắm
# lệch phải thì nó cắt mất chữ đầu, nhìn như lỗi chứ không như cố ý.
ZOOM_X = 730
# Mép trên khung ngắm đặt đúng mép trên dashboard: ngắm cao hơn thì tiêu đề
# "Triển khai website" bị cắt ngang mặt chữ.
ZOOM_Y = DY + H / 2 / ZOOM

MENU = ['Trang chủ', 'Triển khai website', 'Triển khai từ mẫu',
        'Tạo database', 'Sao lưu', 'SSL & bảo mật']
MENU_SANG = 1
MENU_Y0, MENU_BUOC = 100, 34
GOI_H = 104
GOI_HANG = [('Dịch vụ', '5/10'), ('CPU', '1.4/4 core'), ('RAM', '0.9/8 GB')]

HE_SO_RONG = 0.62
BU_RONG = 6


def rong_chu(s, size):
    return max(len(d) for d in s.split('|')) * size * HE_SO_RONG + BU_RONG


def cao_chu(s, size):
    return len(s.split('|')) * size * 1.12


# ══ DỰNG PHẦN TỬ ═══════════════════════════════════════════════════════════
canhs = []          # [{id, duration, camera, elements}]
els = None          # danh sách của cảnh đang mở
hop = {}            # (canh, id) → (x, y, w, h)
trong = {}          # id → id khối cha
dem_id = {}         # để id không trùng khi khai lại dashboard ở nhiều cảnh
dong_bang = []      # (cảnh, tên dòng, y trên, y dưới) — các dòng XẾP CHỒNG DỌC
                    # trong bảng triển khai. Khai ra để `kiem_dong()` canh:
                    # chúng đều là con của `db` nên phép kiểm con-trong-cha
                    # không thấy gì, mà chồng nhau thì mất chữ.


def mo_canh(id, giay, camera=None, camera_muot=None):
    global els
    els = []
    c = {'id': id, 'duration': giay, 'stagger': 0,
         'camera': camera or {'x': 0, 'y': 0, 'scale': 1}, 'elements': els}
    if camera_muot is not None:
        c['cameraMove'] = camera_muot
    canhs.append(c)
    return c


def E(id, kind, x, y, w, h, *, chua=None, **kw):
    d = {'id': id, 'kind': kind, 'x': round(x), 'y': round(y)}
    if w is not None:
        d['w'] = round(w)
    if h is not None:
        d['h'] = round(h)
    d.update(kw)
    els.append(d)
    hop[(canhs[-1]['id'], id)] = (round(x), round(y), round(w or 0), round(h or 0))
    if chua:
        trong[id] = chua
    return d


def khoi(id, x, y, w, h, fill, *, r=10, at=None, vao='rise', dai=.45, xoay=None,
         song=None, chua=None, **kw):
    d = {'fill': fill, 'radius': r}
    if at is not None:
        d['in'] = {'kind': vao, 'ease': 'out', 'dur': dai}
        d['at'] = round(at, 2)
    if song is not None:
        d['for'] = round(song, 2)
    if xoay is not None:
        d['rotate'] = round(xoay, 2)
    d.update(kw)
    E(id, 'panel', x, y, w, h, chua=chua, **d)


def chu(id, x, y, text, size=12, *, w=None, at=None, mau=None, align='left',
        vao='rise', dai=.45, song=None, chua=None, **kw):
    if w is None:
        w = rong_chu(text, size)
    d = {'text': text, 'size': size, 'align': align}
    if at is not None:
        d['in'] = {'kind': vao, 'ease': 'out', 'dur': dai}
        d['at'] = round(at, 2)
    if song is not None:
        d['for'] = round(song, 2)
    if mau:
        d['ink'] = mau
    d.update(kw)
    E(id, 'text', x, y, w, cao_chu(text, size), chua=chua, **d)


def M(rx, ry):
    """Toạ độ tương đối dashboard → tuyệt đối."""
    return DX + rx, DY + ry


def dau_tick(id, cx, cy, R, mau, at, *, chua=None, day=None):
    """Dấu tick vẽ bằng HAI THANH XOAY, không dùng ký tự.

    Ký tự ✓ phụ thuộc phông máy đang chạy — máy này đã ra ô vuông với `＋` và
    `⧉` rồi. Hai hình chữ nhật bo tròn xoay 45° thì máy nào cũng ra như nhau.
    """
    T = day or max(3, R * 0.19)
    # A→B (xuống phải), B→C (lên phải). Toạ độ theo phần của R.
    for i, (ax, ay, bx, by) in enumerate([(-.42, .02, -.10, .32), (-.10, .32, .44, -.30)]):
        import math
        x1, y1, x2, y2 = ax * R, ay * R, bx * R, by * R
        dai_thanh = math.hypot(x2 - x1, y2 - y1) + T * .3
        goc = math.degrees(math.atan2(y2 - y1, x2 - x1))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        khoi(f'{id}-t{i}', cx + mx - dai_thanh / 2, cy + my - T / 2,
             dai_thanh, T, mau, r=T / 2, at=at, vao='fade', dai=.25,
             xoay=goc, chua=chua)


def bieu_tuong_db(id, x, y, w, h, mau, at, *, chua=None):
    """Hình trụ database: nắp bo tròn + thân + đáy bo tròn."""
    nap = max(6, h * 0.28)
    khoi(f'{id}-than', x, y + nap / 2, w, h - nap, mau, r=2, at=at, vao='fade', chua=chua)
    khoi(f'{id}-nap', x, y, w, nap, mau, r=nap / 2, at=at, vao='fade', chua=chua)
    khoi(f'{id}-day', x, y + h - nap, w, nap, mau, r=nap / 2, at=at, vao='fade', chua=chua)


# ══ DASHBOARD — khai lại nguyên vẹn ở mỗi cảnh ═════════════════════════════
def dashboard(dong=False):
    """Vẽ khung dashboard + thanh bên + dải đầu.

    `dong=True` (cảnh 2, 3): mọi thứ đứng sẵn từ giây 0, không diễn lại. Nếu để
    nó diễn lại thì mỗi lần sang cảnh cả dashboard nhấp nháy dựng lại từ đầu.
    """
    def t(x):
        return 0 if dong else x

    def v(x):
        return 'none' if dong else x

    khoi('vien', DX - 2, DY - 2, DW + 4, DH + 4, '#dde2ea', r=20,
         at=t(.12), vao=v('pop'))
    khoi('db', DX, DY, DW, DH, GIAY, r=18, at=t(.15), vao=v('pop'))
    khoi('nav', DX, DY, SW, DH, NAV, r=18, at=t(.18), vao=v('fade'), chua='db')

    # logo
    khoi('logo-o', *M(22, 26), 26, 26, CAM, r=13, at=t(.25), vao=v('pop'), chua='db')
    chu('logo', *M(58, 28), 'Vibe Host', size=17, at=t(.27), mau=MUC_NAV, vao=v('rise'), chua='db')
    chu('kglv', *M(22, 72), 'KHÔNG GIAN LÀM VIỆC', size=9, at=t(.3), mau=MUC_GOI,
        vao=v('rise'), chua='db')

    for i, ten in enumerate(MENU):
        ry = MENU_Y0 + i * MENU_BUOC
        if i == MENU_SANG:
            khoi('menu-sang', *M(12, ry - 7), SW - 24, 30, NAV_SANG, r=8,
                 at=t(.34), vao=v('fade'), chua='db')
        khoi(f'menu-ic{i}', *M(28, ry + 3), 12, 12,
             CAM if i == MENU_SANG else '#5b6577', r=3,
             at=t(.34 + i * .035), vao=v('fade'), chua='db')
        chu(f'menu{i}', *M(50, ry), ten, size=11, w=SW - 50 - 12,
            at=t(.34 + i * .035), mau=MUC_NAV if i == MENU_SANG else MUC_GOI,
            vao=v('rise'), chua='db')

    gy = DH - GOI_H - 22
    khoi('goi', *M(12, gy), SW - 24, GOI_H, GOI_NEN, r=10, at=t(.56), vao=v('fade'), chua='db')
    chu('goi-ten', *M(24, gy + 11), 'Gói Vibe Host Pro', size=10, at=t(.58),
        mau=MUC_NAV, vao=v('rise'), chua='db')
    for i, (k, val) in enumerate(GOI_HANG):
        ry = gy + 38 + i * 21
        chu(f'goi-k{i}', *M(24, ry), k, size=10, w=64, at=t(.6 + i * .04),
            mau=MUC_GOI, vao=v('rise'), chua='db')
        chu(f'goi-v{i}', *M(SW - 24 - 76, ry), val, size=10, w=76, align='right',
            at=t(.6 + i * .04), mau=MUC_NAV, vao=v('rise'), chua='db')

    # dải đầu vùng chính
    chu('dau-ten', *M(SW + LE_TRONG, 28), 'Triển khai website', size=20,
        at=t(.4), vao=v('rise'), chua='db')
    chu('dau-phu', *M(SW + LE_TRONG, 57), 'airtex-trungthu.vibehost.vn', size=11,
        at=t(.44), mau=MO, vao=v('rise'), chua='db')
    khoi('dau-gach', *M(SW, DAU_H), MW, 1, VIEN, r=0, at=t(.46), vao=v('fade'), chua='db')
    for i in range(3):
        khoi(f'dau-ic{i}', *M(DW - 40 - i * 32, 34), 14, 14, '#c8cedb', r=4,
             at=t(.48 + i * .03), vao=v('fade'), chua='db')


# ══ CỘT PHẢI — ba hàng trạng thái ══════════════════════════════════════════
# (nhãn, y tương đối trong cột)
HANG = [('Chứng chỉ SSL', 0), ('Database', 100), ('CDN & bộ nhớ đệm', 200)]
HANG_H = 84


def the_trang_thai(i, ten, ry, mau_cham, phu, mau_phu, at, *, hau='', vao='rise',
                   nhuong=None):
    """Một thẻ trạng thái ở cột phải. `hau` cho phép khai lại cùng thẻ với id khác.

    `nhuong` là giây mà thẻ XANH sẽ đè lên thẻ này. Chữ và chấm của thẻ xám phải
    tan TRƯỚC mốc đó — nếu để chúng cùng mờ chuyển với thẻ xanh thì trong khoảng
    giao nhau hai lớp chữ hiện chồng lên nhau, đọc thành một đống nhoè.
    Riêng nền thẻ thì cứ chồng, đổi màu thôi nên không sao.
    """
    y = NY + ry
    idp = f'tt{i}{hau}'
    tan = {}
    if nhuong is not None:
        tan = {'song': max(.01, nhuong - .2), 'out': {'kind': 'fade', 'dur': .18}}
    khoi(idp, PX, y, COT_PHAI_W, HANG_H, XAM_NEN, r=12, at=at, vao=vao, chua='db')
    khoi(f'{idp}-cham', PX + 18, y + 18, 12, 12, mau_cham, r=6, at=at + .04,
         vao='pop', chua=idp, **tan)
    chu(f'{idp}-ten', PX + 42, y + 14, ten, size=13, at=at + .04, chua=idp, **tan)
    chu(f'{idp}-phu', PX + 42, y + 38, phu, size=11, at=at + .07, mau=mau_phu,
        chua=idp, **tan)
    return idp


def vien_dut(id, x, y, w, h, mau, at, *, day=2, net=14, khe=10, chua=None):
    """Viền nét đứt — định dạng không có `border`, nên rải từng vạch nhỏ.

    Vạch sinh bằng vòng lặp chứ không gõ tay: đổi kích thước vùng là viền tự
    chạy lại cho khít, không ai phải đếm.
    """
    n = 0
    buoc = net + khe
    for cx in range(0, int(w - net) + 1, buoc):
        for cy, ten in ((y, 'tr'), (y + h - day, 'du')):
            khoi(f'{id}-{ten}{n}', x + cx, cy, net, day, mau, r=day / 2,
                 at=at, vao='fade', dai=.3, chua=chua)
        n += 1
    n = 0
    for cy in range(buoc, int(h - net) + 1, buoc):
        for cx, ten in ((x, 'tra'), (x + w - day, 'ph')):
            khoi(f'{id}-{ten}{n}', cx, y + cy, day, net, mau, r=day / 2,
                 at=at, vao='fade', dai=.3, chua=chua)
        n += 1


def the_tep(id, x, y, at, *, vao='rise', dai=.45, song=None, chua=None):
    """Thẻ tệp `ttindex.html` — thứ được kéo thả."""
    w, h = 250, 64
    khoi(id, x, y, w, h, GIAY, r=12, at=at, vao=vao, dai=dai, song=song, chua=chua)
    khoi(f'{id}-o', x + 14, y + 14, 36, 36, CAM_MO, r=9, at=at + .03, vao='fade',
         song=song, chua=id)
    chu(f'{id}-ic', x + 14, y + 24, '< >', size=13, w=36, align='center',
        at=at + .05, mau=CAM, vao='fade', song=song, chua=id)
    chu(f'{id}-ten', x + 62, y + 14, 'ttindex.html', size=13, at=at + .05,
        vao='fade', song=song, chua=id)
    chu(f'{id}-phu', x + 62, y + 36, 'HTML  ·  68 KB', size=10, at=at + .07,
        mau=MO, vao='fade', song=song, chua=id)


# ══════════════════════════════════════════════════════════════════════════
# CẢNH 1 — dashboard hiện ra, kéo thả tệp vào
# ══════════════════════════════════════════════════════════════════════════
C1 = 4.8
mo_canh('c1-keo-tha', C1)
khoi('nen', 0, 0, W, H, NEN, r=0, **{'in': {'kind': 'none', 'dur': .001}})
dashboard()

# vùng nhận tệp
khoi('tha', TX, NY, COT_TRAI_W, NOI_DUNG_H, '#fafbfd', r=14, at=.8, vao='fade', chua='db')
vien_dut('tha-v', TX, NY, COT_TRAI_W, NOI_DUNG_H, '#cfd6e3', .84, chua='db')
T_THA = 2.8         # giây tệp chạm vùng nhận
khoi('tha-o', TX + COT_TRAI_W / 2 - 27, NY + 96, 54, 54, XAM_NEN, r=14, at=.95,
     vao='pop', song=T_THA - .95 - .45, chua='db',
     **{'out': {'kind': 'fade', 'dur': .25}})
khoi('tha-tep', TX + COT_TRAI_W / 2 - 13, NY + 108, 26, 30, '#b9c1d0', r=4, at=1.0,
     vao='pop', song=T_THA - 1.0 - .45, chua='db',
     **{'out': {'kind': 'fade', 'dur': .25}})
chu('tha-chu', TX, NY + 176, 'Kéo tệp .html vào đây', size=17, w=COT_TRAI_W,
    align='center', at=1.05, song=T_THA - 1.05 - .45, chua='db',
    **{'out': {'kind': 'fade', 'dur': .25}})
chu('tha-phu', TX, NY + 210, 'hoặc bấm để chọn từ máy', size=11, w=COT_TRAI_W,
    align='center', at=1.1, mau=MO, song=T_THA - 1.1 - .45, chua='db',
    **{'out': {'kind': 'fade', 'dur': .25}})

# ba thẻ trạng thái, đều đang xám
for i, (ten, ry) in enumerate(HANG):
    the_trang_thai(i, ten, ry, CHO, ['Chưa cấp', 'Chưa kết nối', 'Chưa bật'][i],
                   MO, 1.2 + i * .12)

# thẻ tệp nổi ở góc trên phải, rồi biến mất đúng lúc bản kia rơi xuống
the_tep('tep-a', 900, 96, 1.3, song=1.5)

# con trỏ: tới nhặt tệp, kéo xuống vùng nhận, thả
els.append({
    'id': 'tro', 'kind': 'pointer', 'x': 0, 'y': 0,
    'path': [{'t': 1.0, 'x': 1235, 'y': 46}, {'t': 1.7, 'x': 1004, 'y': 126},
             {'t': 1.95, 'x': 1004, 'y': 126}, {'t': 2.8, 'x': 545, 'y': 320},
             {'t': 4.4, 'x': 545, 'y': 320}],
    'clicks': [{'t': 1.8, 'x': 1004, 'y': 126}, {'t': 2.85, 'x': 545, 'y': 320}],
})

# tệp rơi vào ô, ô sáng lên màu cam
khoi('tha-sang', TX, NY, COT_TRAI_W, NOI_DUNG_H, '#fdf3ec', r=14, at=3.1,
     vao='fade', dai=.3, chua='db')
vien_dut('tha-vs', TX, NY, COT_TRAI_W, NOI_DUNG_H, CAM, 3.12, chua='db')
the_tep('tep-b', TX + (COT_TRAI_W - 250) / 2, NY + (NOI_DUNG_H - 64) / 2 - 20,
        2.85, vao='fall', **{'chua': 'db'})
chu('tha-nhan', TX, NY + NOI_DUNG_H / 2 + 44, 'Đã nhận tệp — sẵn sàng triển khai',
    size=12, w=COT_TRAI_W, align='center', at=3.5, mau=CAM, chua='db')


# ══════════════════════════════════════════════════════════════════════════
# BẢNG TRIỂN KHAI — dùng chung cảnh 2 và 3
# ══════════════════════════════════════════════════════════════════════════
BUOC = ['Tải tệp lên', 'Cài đặt máy chủ', 'Cấp chứng chỉ SSL', 'Kết nối database']
VACH_N = 26                      # số vạch của thanh tiến trình
VACH_KHE = 3
BUOC_BUOC = 46                   # khoảng cách dọc giữa hai bước


def bang_trien_khai(tieu_de, vach_da, vach_toi, moc, *, hau='', t0=.18, buoc=.1):
    """Bảng "đang triển khai": thanh vạch + bốn bước + (tuỳ chọn) thẻ xem trước.

    `vach_da` là số vạch ĐÃ sáng sẵn từ đầu cảnh, `vach_toi` là số vạch sáng khi
    cảnh kết thúc. Tách hai con số này ra vì cảnh 3 phải nối tiếp cảnh 2: để
    chung một tham số thì sang cảnh mới cả thanh chạy lại từ số không, nhìn như
    quay ngược.

    `moc[i]`: None = chưa tới · 0 = đã xong từ trước · >0 = đánh dấu ở giây đó.
    """
    khoi(f'bang{hau}', TX, NY, COT_TRAI_W, NOI_DUNG_H, '#fafbfd', r=14,
         at=0, vao='none', chua='db')
    chu(f'bang{hau}-td', TX + 28, NY + 26, tieu_de, size=16, at=0, vao='none', chua='db')
    chu(f'bang{hau}-phu', TX + 28, NY + 54, 'ttindex.html  ·  68 KB', size=11,
        at=0, vao='none', mau=MO, chua='db')

    # Thanh tiến trình là NHIỀU VẠCH sáng dần, không phải một khối phình ra —
    # định dạng không cho đổi bề rộng theo thời gian.
    tw = COT_TRAI_W - 56
    vw = (tw - VACH_KHE * (VACH_N - 1)) / VACH_N
    for i in range(VACH_N):
        if i < vach_da:
            mau, at_, vao = CAM, 0, 'none'
        elif i < vach_toi:
            mau, at_, vao = CAM, round(t0 + (i - vach_da) * buoc, 2), 'pop'
        else:
            mau, at_, vao = '#e6eaf1', 0, 'none'
        khoi(f'bang{hau}-v{i}', TX + 28 + i * (vw + VACH_KHE), NY + 92, vw, 8,
             mau, r=4, at=at_, vao=vao, dai=.2, chua='db')

    for i, ten in enumerate(BUOC):
        y = NY + 132 + i * BUOC_BUOC
        t = moc[i]
        tinh = t is None or t == 0
        khoi(f'bang{hau}-o{i}', TX + 28, y, 24, 24,
             '#eef1f6' if t is None else LUC_MO, r=12,
             at=t or 0, vao='none' if tinh else 'pop', dai=.3, chua='db')
        if t is None:
            khoi(f'bang{hau}-cho{i}', TX + 37, y + 9, 6, 6, CHO, r=3, at=0,
                 vao='none', chua='db')
        else:
            dau_tick(f'bang{hau}-tick{i}', TX + 40, y + 12, 11, LUC,
                     (t + .04) if t else 0, chua='db')
        chu(f'bang{hau}-b{i}', TX + 64, y + 4, ten, size=12, at=t or 0,
            vao='none' if tinh else 'rise', mau=MO if t is None else None, chua='db')

    dong_bang.append((canhs[-1]['id'], 'thanh tiến trình', NY + 92, NY + 100))
    for i in range(len(BUOC)):
        y = NY + 132 + i * BUOC_BUOC
        dong_bang.append((canhs[-1]['id'], f'bước {i + 1} · {BUOC[i]}', y, y + 26))
    return NY + 132 + len(BUOC) * BUOC_BUOC      # mép dưới của danh sách bước


# ══════════════════════════════════════════════════════════════════════════
# CẢNH 2 — đang triển khai, thẻ SSL bật ra giữa khung hình
# ══════════════════════════════════════════════════════════════════════════
C2 = 4.2
mo_canh('c2-trien-khai', C2)
khoi('nen', 0, 0, W, H, NEN, r=0, **{'in': {'kind': 'none', 'dur': .001}})
dashboard(dong=True)
bang_trien_khai('Đang triển khai…', 0, 20, [.45, 1.15, 2.05, None], t0=.18, buoc=.1)

# cột phải: SSL chuyển xanh đúng lúc bước SSL xong
the_trang_thai(0, 'Chứng chỉ SSL', HANG[0][1], CHO, 'Đang cấp…', MO, 0,
               vao='none', nhuong=2.05)
the_trang_thai(1, 'Database', HANG[1][1], CHO, 'Chưa kết nối', MO, 0, vao='none')
the_trang_thai(2, 'CDN & bộ nhớ đệm', HANG[2][1], CHO, 'Chưa bật', MO, 0, vao='none')
the_trang_thai(0, 'Chứng chỉ SSL', HANG[0][1], LUC, 'Đã cấp · Let\'s Encrypt',
               LUC, 2.05, hau='x', vao='fade')

# ── THẺ SSL BẬT RA GIỮA KHUNG HÌNH ────────────────────────────────────────
PW, PH = 420, 300
PPX, PPY = (W - PW) / 2, (H - PH) / 2        # đúng tâm khung: 430, 210
T_SSL, SONG_SSL = 2.1, 1.5
khoi('ssl-bong', PPX - 3, PPY - 3, PW + 6, PH + 6, '#00000014', r=27,
     at=T_SSL, vao='pop', dai=.5, song=SONG_SSL)
khoi('ssl', PPX, PPY, PW, PH, GIAY, r=24, at=T_SSL, vao='pop', dai=.5, song=SONG_SSL)
khoi('ssl-vong', PPX + PW / 2 - 54, PPY + 42, 108, 108, LUC_MO, r=54,
     at=T_SSL + .08, vao='pop', dai=.5, song=SONG_SSL - .08, chua='ssl')
khoi('ssl-tron', PPX + PW / 2 - 40, PPY + 56, 80, 80, LUC, r=40,
     at=T_SSL + .14, vao='pop', dai=.45, song=SONG_SSL - .14, chua='ssl')
dau_tick('ssl-dau', PPX + PW / 2, PPY + 96, 34, '#ffffff', T_SSL + .3, chua='ssl', day=7)
chu('ssl-td', PPX, PPY + 176, 'Đã cấp chứng chỉ SSL', size=22, w=PW,
    align='center', at=T_SSL + .34, song=SONG_SSL - .34, chua='ssl')
chu('ssl-phu', PPX, PPY + 212, 'Kết nối tới trang đã được mã hoá', size=12, w=PW,
    align='center', at=T_SSL + .4, mau=MO, song=SONG_SSL - .4, chua='ssl')
khoi('ssl-nhan', PPX + PW / 2 - 66, PPY + 244, 132, 26, LUC_MO, r=13,
     at=T_SSL + .46, vao='pop', song=SONG_SSL - .46, chua='ssl')
chu('ssl-nhan-c', PPX + PW / 2 - 66, PPY + 250, 'HTTPS đang bật', size=11, w=132,
    align='center', at=T_SSL + .5, mau=LUC, song=SONG_SSL - .5, chua='ssl')


# ══════════════════════════════════════════════════════════════════════════
# CẢNH 3 — CAMERA ZOOM vào dashboard, database bật đèn xanh
# ══════════════════════════════════════════════════════════════════════════
C3 = 2.8
mo_canh('c3-zoom', C3,
        camera={'x': ZOOM_X - W / 2, 'y': ZOOM_Y - H / 2, 'scale': ZOOM},
        camera_muot=1.1)
khoi('nen', 0, 0, W, H, NEN, r=0, **{'in': {'kind': 'none', 'dur': .001}})
dashboard(dong=True)
T_DB, T_CDN = .9, 1.7            # giây database và CDN bật đèn xanh
DAY_BUOC = bang_trien_khai('Đã triển khai xong', 20, VACH_N, [0, 0, 0, T_DB + .05],
                           t0=.08, buoc=.09)

# ── cột phải: SSL đã xanh sẵn; database và CDN bật lên trong cảnh này ──────
the_trang_thai(0, 'Chứng chỉ SSL', HANG[0][1], LUC, 'Đã cấp · Let\'s Encrypt',
               LUC, 0, vao='none')
the_trang_thai(1, 'Database', HANG[1][1], CHO, 'Đang kết nối…', MO, 0,
               vao='none', nhuong=T_DB)
the_trang_thai(2, 'CDN & bộ nhớ đệm', HANG[2][1], CHO, 'Chưa bật', MO, 0,
               vao='none', nhuong=T_CDN)

# ĐÈN XANH DATABASE — thẻ xanh chồng lên thẻ xám, kèm biểu tượng hình trụ
dbY = NY + HANG[1][1]
khoi('db-xanh', PX, dbY, COT_PHAI_W, HANG_H, LUC_MO, r=12, at=T_DB, vao='fade', dai=.35, chua='db')
bieu_tuong_db('db-hinh', PX + 18, dbY + 22, 22, 30, LUC, T_DB + .06, chua='db-xanh')
chu('db-ten', PX + 52, dbY + 18, 'Database', size=13, at=T_DB + .06, chua='db-xanh')
chu('db-phu', PX + 52, dbY + 42, 'Đã kết nối  ·  airtex_db', size=11, at=T_DB + .1,
    mau=LUC, chua='db-xanh')
khoi('db-den', PX + COT_PHAI_W - 34, dbY + HANG_H / 2 - 7, 14, 14, LUC, r=7,
     at=T_DB + .14, vao='pop', dai=.4, chua='db-xanh')

cdnY = NY + HANG[2][1]
khoi('cdn-xanh', PX, cdnY, COT_PHAI_W, HANG_H, LUC_MO, r=12, at=T_CDN, vao='fade',
     dai=.35, chua='db')
khoi('cdn-cham', PX + 18, cdnY + 26, 12, 12, LUC, r=6, at=T_CDN + .06, vao='pop', chua='cdn-xanh')
chu('cdn-ten', PX + 52, cdnY + 18, 'CDN & bộ nhớ đệm', size=13, at=T_CDN + .06, chua='cdn-xanh')
chu('cdn-phu', PX + 52, cdnY + 42, 'Đã bật  ·  12 điểm phát', size=11, at=T_CDN + .1,
    mau=LUC, chua='cdn-xanh')
khoi('cdn-den', PX + COT_PHAI_W - 34, cdnY + HANG_H / 2 - 7, 14, 14, LUC, r=7,
     at=T_CDN + .14, vao='pop', dai=.4, chua='cdn-xanh')


# ══════════════════════════════════════════════════════════════════════════
# CẢNH 4 — TRANG BẬT RA GIỮA KHUNG HÌNH
#
# Camera lùi về ×1 trong lúc cửa sổ trình duyệt nở ra ở giữa: cú lùi và cú nở
# đi ngược chiều nhau nên mắt bám vào trang, không bám vào dashboard.
# Màu lấy thẳng từ `public/html-foot/ttindex.html`.
# ══════════════════════════════════════════════════════════════════════════
C4 = 3.2
mo_canh('c4-bat-ra', C4, camera_muot=.85)
khoi('nen', 0, 0, W, H, NEN, r=0, **{'in': {'kind': 'none', 'dur': .001}})
dashboard(dong=True)
bang_trien_khai('Đã triển khai xong', VACH_N, VACH_N, [0, 0, 0, 0])
the_trang_thai(0, 'Chứng chỉ SSL', HANG[0][1], LUC, 'Đã cấp · Let\'s Encrypt', LUC, 0, vao='none')
the_trang_thai(1, 'Database', HANG[1][1], LUC, 'Đã kết nối · airtex_db', LUC, 0, vao='none')
the_trang_thai(2, 'CDN & bộ nhớ đệm', HANG[2][1], LUC, 'Đã bật · 12 điểm phát', LUC, 0, vao='none')

# ── cửa sổ trình duyệt ────────────────────────────────────────────────────
BW, BH = 760, 430
BX, BY = (W - BW) / 2, (H - BH) / 2          # 260, 145 — đúng tâm khung
THANH = 38                                    # dải điều khiển trên cùng
T_BAT = .5
khoi('br-bong', BX - 5, BY - 5, BW + 10, BH + 10, '#0000001c', r=21,
     at=T_BAT, vao='pop', dai=.55)
khoi('br', BX, BY, BW, BH, '#0b0f24', r=16, at=T_BAT, vao='pop', dai=.55)
khoi('br-thanh', BX, BY, BW, THANH, '#171c34', r=16, at=T_BAT + .04, vao='fade', chua='br')
for i, mau in enumerate(['#ff5f57', '#febc2e', '#28c840']):
    khoi(f'br-cham{i}', BX + 18 + i * 18, BY + 14, 10, 10, mau, r=5,
         at=T_BAT + .08 + i * .03, vao='pop', dai=.3, chua='br')
khoi('br-url', BX + 84, BY + 9, 320, 20, '#242a45', r=10, at=T_BAT + .14,
     vao='fade', chua='br')
khoi('br-khoa', BX + 94, BY + 14, 8, 10, LUC, r=2, at=T_BAT + .17, vao='pop',
     dai=.3, chua='br-url')
chu('br-diachi', BX + 108, BY + 13, 'airtex-trungthu.vibehost.vn', size=10,
    w=286, at=T_BAT + .18, mau='#c9d2ea', chua='br-url')

# ── ruột trang: toạ độ tương đối vùng trang ───────────────────────────────
PGX, PGY = BX, BY + THANH
PGW, PGH = BW, BH - THANH


def P(rx, ry):
    return PGX + rx, PGY + ry


T_TR = T_BAT + .3
khoi('tr-nen', PGX, PGY, PGW, PGH, '#0a0d22', r=0, at=T_TR, vao='fade', dai=.4, chua='br')
khoi('tr-tim', PGX, PGY, PGW, PGH, '#2b1b46', r=0, at=T_TR, vao='fade', dai=.4, chua='br')

# dải khuyến mãi
khoi('tr-km', PGX, PGY, PGW, 26, '#3a2a5e', r=0, at=T_TR + .04, vao='fade', chua='br')
chu('tr-km-c', PGX, PGY + 7, 'Ưu đãi Trung Thu *giảm đến 42%*  ·  Miễn phí giao toàn quốc',
    size=10, w=PGW, align='center', at=T_TR + .06, mau='#e9ddff', chua='br')

# đầu trang
khoi('tr-logo', *P(24, 40), 16, 16, VANG, r=8, at=T_TR + .1, vao='pop', dai=.3, chua='br')
chu('tr-ten', *P(48, 40), 'AIRTEX', size=14, at=T_TR + .12, mau='#ffffff', chua='br')
# Ba mục thôi, không phải bốn: mục thứ tư chạy tới x=664, đúng chỗ mặt trăng.
for i, nv in enumerate(['Công nghệ vải', 'Bộ sưu tập', 'Combo ưu đãi']):
    chu(f'tr-nv{i}', *P(292 + i * 94, 43), nv, size=9, w=90, align='center',
        at=T_TR + .14 + i * .03, mau='#b9a9d4', chua='br')
khoi('tr-cta0', *P(PGW - 106, 34), 82, 26, VANG, r=13, at=T_TR + .18, vao='pop',
     dai=.35, chua='br')
chu('tr-cta0-c', *P(PGW - 106, 42), 'Đặt ngay', size=10, w=82, align='center',
    at=T_TR + .2, mau='#2b1b46', chua='br')

# mặt trăng + dây đèn lồng
# Mặt trăng nằm DƯỚI dải đầu trang (nó vẽ sau nên che nút "Đặt ngay" nếu đặt
# cao) và TRÊN thẻ sản phẩm (thẻ vẽ sau nên phủ mờ lên nó — đúng như trang gốc).
khoi('tr-trang', *P(PGW - 152, 78), 128, 128, VANG, r=64, at=T_TR + .22,
     vao='pop', dai=.55, chua='br')
khoi('tr-day', *P(0, 96), PGW, 1, '#6b5a92', r=0, at=T_TR + .26, vao='fade', chua='br')
for i, mau in enumerate(['#e0574f', '#f0a93c', '#e8564f', '#f2c45a', '#dd5a8e', '#e0574f']):
    khoi(f'tr-den{i}', *P(46 + i * 104, 96), 15, 21, mau, r=7,
         at=T_TR + .28 + i * .035, vao='fall', dai=.4, chua='br')

# câu tiêu đề
chu('tr-td', *P(24, 136), 'Mặc mát như *gió đêm rằm*,|công nghệ giấu|trong từng sợi vải',
    size=25, w=390, at=T_TR + .36, mau='#ffffff', chua='br')
chu('tr-phu', *P(24, 262), 'Bộ sưu tập áo thun AirCool 3.0 — hạ nhiệt tức thì|2.4°C, kháng khuẩn ion bạc Ag+, chống tia UV.',
    size=10, w=390, at=T_TR + .46, mau='#b9a9d4', chua='br')
khoi('tr-cta1', *P(24, 306), 168, 34, VANG, r=17, at=T_TR + .52, vao='pop', dai=.4, chua='br')
chu('tr-cta1-c', *P(24, 316), 'Xem combo Trung Thu →', size=11, w=168,
    align='center', at=T_TR + .54, mau='#2b1b46', chua='br')

# thẻ sản phẩm bên phải
khoi('tr-the', *P(430, 128), 306, 226, '#ffffff10', r=14, at=T_TR + .5, vao='pop',
     dai=.45, chua='br')
khoi('tr-nhan', *P(444, 118), 148, 22, '#dd5a8e', r=11, at=T_TR + .56, vao='pop',
     dai=.35, chua='br')
chu('tr-nhan-c', *P(444, 124), 'BÁN CHẠY NHẤT · -28%', size=9, w=148,
    align='center', at=T_TR + .58, mau='#ffffff', chua='br')
khoi('tr-ao', *P(548, 156), 70, 78, '#26407a', r=10, at=T_TR + .6, vao='pop',
     dai=.4, chua='tr-the')
khoi('tr-tay0', *P(528, 160), 26, 20, '#26407a', r=6, at=T_TR + .62, vao='fade',
     xoay=-16, chua='tr-the')
khoi('tr-tay1', *P(612, 160), 26, 20, '#26407a', r=6, at=T_TR + .62, vao='fade',
     xoay=16, chua='tr-the')
for i, mau in enumerate(['#3d63c4', '#1b1e2a', '#ece7dd', '#a63a4a', '#4c8464']):
    khoi(f'tr-mau{i}', *P(492 + i * 36, 250), 22, 22, mau, r=11,
         at=T_TR + .64 + i * .03, vao='pop', dai=.3, chua='tr-the')
chu('tr-sp', *P(446, 292), 'Áo thun AirCool Basic', size=11, w=180,
    at=T_TR + .7, mau='#ffffff', chua='tr-the')
chu('tr-gia', *P(446, 314), '359.000đ', size=19, w=180, at=T_TR + .74,
    mau=VANG, chua='tr-the')


# ══ KIỂM TRA TRƯỚC KHI GHI ═════════════════════════════════════════════════
loi = []


def kiem_trong():
    """Mọi thành phần trong khung hình; con nằm trong khối cha đã khai."""
    for (canh, id_), (x, y, w_, h_) in hop.items():
        if x < 0 or y < 0 or x + w_ > W or y + h_ > H:
            loi.append(f'[{canh}] `{id_}` thò ra ngoài khung hình: '
                       f'({x},{y}) {w_}×{h_} — khung {W}×{H}.')
        cha = trong.get(id_)
        if cha:
            c = hop.get((canh, cha))
            if c is None:
                loi.append(f'[{canh}] `{id_}` khai cha là `{cha}` nhưng cảnh này không có `{cha}`.')
                continue
            cx, cy, cw, ch = c
            if x < cx or y < cy or x + w_ > cx + cw or y + h_ > cy + ch:
                loi.append(f'[{canh}] `{id_}` thò ra ngoài `{cha}`: '
                           f'({x},{y}) {w_}×{h_} — cha ({cx},{cy}) {cw}×{ch}.')


def kiem_dong():
    """Các dòng trong bảng triển khai xếp chồng dọc — không dòng nào cấn dòng nào.

    Phép kiểm con-trong-cha không thấy lỗi này: mọi dòng đều là con của `db` và
    đều nằm gọn trong đó. Nhưng chúng chồng lên nhau thì thẻ xem trước đè mất
    bước "Kết nối database" — đã xảy ra đúng như vậy ở bản đầu.
    """
    for c in canhs:
        d = sorted([x for x in dong_bang if x[0] == c['id']], key=lambda x: x[2])
        for a, b in zip(d, d[1:]):
            if b[2] < a[3]:
                loi.append(f'[{c["id"]}] "{a[1]}" ({a[2]:.0f}–{a[3]:.0f}) '
                           f'cấn "{b[1]}" ({b[2]:.0f}–{b[3]:.0f}).')
        if d and d[-1][3] > NY + NOI_DUNG_H - 6:
            loi.append(f'[{c["id"]}] "{d[-1][1]}" xuống tới {d[-1][3]:.0f}, '
                       f'tràn khỏi bảng kết thúc ở {NY + NOI_DUNG_H}.')


def kiem_sao():
    """Dấu `*...*` không được bắc qua chỗ xuống dòng `|`.

    Trình dựng CẮT DÒNG TRƯỚC rồi mới dịch dấu sao trên từng dòng, nên một cặp
    sao nằm hai bên dấu `|` bị chẻ đôi: không dòng nào có đủ cặp, và ký tự `*`
    hiện nguyên ra màn hình. Không có lỗi nào báo — chỉ nhìn mới thấy.
    """
    for c in canhs:
        for e in c['elements']:
            for phan in ('text', 'sub'):
                v = e.get(phan)
                if not isinstance(v, str) or '|' not in v:
                    continue
                for dong in v.split('|'):
                    if dong.count('*') % 2:
                        loi.append(f'[{c["id"]}] `{e["id"]}`: cặp `*…*` bắc qua dấu `|` — '
                                   f'dòng "{dong.strip()}" lẻ dấu sao, sẽ hiện nguyên ký tự.')


def kiem_camera():
    """Khung ngắm khi zoom không được vượt mép clip.

    Vượt là lòi nền trống ra ở rìa video, và KHÔNG CÓ GÌ BÁO — chỉ khi xem lại
    mới thấy một dải xám bên cạnh. Camera đặt điểm (mx,my) vào giữa khung nên
    nửa bề rộng nhìn thấy là W/2 chia cho mức phóng.
    """
    for c in canhs:
        cam = c['camera']
        s = cam.get('scale', 1)
        if s <= 1:
            continue
        mx, my = cam['x'] + W / 2, cam['y'] + H / 2
        nx, ny = W / 2 / s, H / 2 / s
        if mx - nx < -0.5 or mx + nx > W + 0.5 or my - ny < -0.5 or my + ny > H + 0.5:
            loi.append(f'[{c["id"]}] khung ngắm zoom ×{s} quanh ({mx:.0f},{my:.0f}) '
                       f'lọt ra ngoài clip: x {mx - nx:.0f}…{mx + nx:.0f}, '
                       f'y {my - ny:.0f}…{my + ny:.0f} — clip {W}×{H}.')


def kiem_id():
    """Id không được trùng trong cùng một cảnh — `validateScene` cũng chặn,
    nhưng báo ở đây thì biết ngay id nào, không phải dò trong JSON."""
    for c in canhs:
        thay = set()
        for e in c['elements']:
            if e['id'] in thay:
                loi.append(f'[{c["id"]}] trùng id `{e["id"]}`.')
            thay.add(e['id'])


def kiem_moc():
    """Không phần tử nào được hẹn giờ sau lúc cảnh kết thúc."""
    for c in canhs:
        for e in c['elements']:
            if e.get('at', 0) >= c['duration']:
                loi.append(f'[{c["id"]}] `{e["id"]}` hiện ở giây {e["at"]} '
                           f'nhưng cảnh chỉ dài {c["duration"]}s.')


kiem_trong()
kiem_dong()
kiem_sao()
kiem_camera()
kiem_id()
kiem_moc()

if loi:
    print('✗ Bố cục sai — KHÔNG ghi file:', file=sys.stderr)
    for l in loi:
        print('   ·', l, file=sys.stderr)
    sys.exit(1)

doc = {
    'version': 1,
    'meta': {'name': 'Kéo thả HTML → chạy ngay', 'width': W, 'height': H,
             'density': 1, 'bg': NEN, 'accent': CAM, 'accent2': '#f4a261',
             'hot': CAM, 'hot2': '#e3272c', 'ink': MUC,
             'inkSoft': '#5d6678', 'inkFaint': '#98a1b2'},
    'scenes': canhs,
}
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')

moc, chay = [], 0.0
for c in canhs:
    chay += c['duration']
    moc.append({'id': c['id'], 'moc': round(chay - 0.15, 2)})
KIEM.write_text(json.dumps({'slug': OUT.stem, 'w': W, 'h': H, 'canh': moc,
                            'trong': trong}, ensure_ascii=False, indent=2),
                encoding='utf-8')

tong = sum(len(c['elements']) for c in canhs)
print(f'✓ {OUT.name}: {tong} thành phần, {len(canhs)} cảnh, {chay:.1f}s')
for c in canhs:
    print(f'   · {c["id"]:<16} {c["duration"]:>4.1f}s  ×{c["camera"].get("scale", 1)}  '
          f'{len(c["elements"])} thành phần')
