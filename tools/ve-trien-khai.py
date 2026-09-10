#!/usr/bin/env python3
"""Clip thử: KÉO THẢ MỘT FILE HTML VÀO VIBE HOSTING RỒI TRANG CHẠY.

Dựng lại giao diện THẬT, không phỏng đoán. Bản trước tôi tự nghĩ ra một
dashboard chung chung; bản này đọc từ ảnh chụp sản phẩm trong dự án:

    public/image/triển khai website.png   ← màn "Đưa website lên mạng"
    public/image/trang chủ.png            ← bộ nhận diện, thanh bên, thẻ gói
    public/image/database khởi tạo.png    ← giao diện lúc ĐANG chạy tiến trình

Màu lấy bằng cách đọc thẳng pixel của mấy ảnh đó (xem khối MÀU), không ước
bằng mắt.

Kịch bản (15 giây, không lời):

  Cảnh 1 (5,0)  Màn "Đưa website lên mạng", bước 1 "Mã nguồn". Con trỏ kéo
                `ttindex.html` thả vào thẻ "Tải file" — thẻ sáng viền cam.
  Cảnh 2 (4,2)  Bước nhảy sang 3 "Đưa lên mạng". Thẻ tiến trình chạy từng
                bước. Tới bước cấp SSL thì thẻ SSL bật ra GIỮA KHUNG HÌNH.
  Cảnh 3 (2,8)  CAMERA ZOOM vào thẻ tiến trình. Database bật đèn xanh.
  Cảnh 4 (3,0)  Camera lùi ra, trang AIRTEX bật ra giữa khung.

HỆ TOẠ ĐỘ — cùng kỷ luật với `ve-s02.py`:
  · Không có số rời rạc; mọi vị trí suy từ khối HÌNH HỌC.
  · `kiem_trong()` chặn thành phần thò ra ngoài khung hoặc ngoài khối cha.
  · `kiem_dong()` chặn các dòng xếp chồng dọc cấn nhau.
  · `kiem_camera()` chặn khung ngắm zoom lọt ra ngoài mép clip.
  · `kiem_sao()` chặn cặp `*…*` bắc qua dấu `|` (xem chú thích ở hàm đó).

BA CHỖ CỦA ĐỊNH DẠNG PHẢI BIẾT TRƯỚC:
  1. Phần tử thuộc về MỘT cảnh; sang cảnh khác là mất. Khung ứng dụng phải
     khai lại ở cả bốn cảnh — viết thành hàm gọi bốn lần.
  2. `at` tính từ ĐẦU CẢNH.
  3. Con trỏ chuột nằm NGOÀI `#cam` nên camera không phóng nó theo. Chỉ dùng
     ở cảnh không zoom.
"""
import json
import math
import pathlib
import sys

W, H = 1280, 720
GOC = pathlib.Path('/home/coder/workspace/projects/clipVibehost/hosting-animatic-production')
OUT = GOC / 'scenes' / 'thu-trien-khai-html.json'
KIEM = pathlib.Path(__file__).parent / f'kiem-{OUT.stem}.json'

# ══ MÀU — đọc pixel từ chính ảnh chụp sản phẩm ═════════════════════════════
NEN_APP  = '#212230'   # nền trang + thanh bên
MUC_SANG = '#383945'   # mục menu đang chọn
GOI_NEN  = '#2a2b38'   # thẻ gói dưới chân thanh bên
GOI_HUY  = '#40414c'   # huy hiệu "Gói Vibe Host Pro"
CAM      = '#fd7401'   # cam thương hiệu (ô logo)
CAM_CHU  = '#fd5d01'   # chữ "Hosting"
CAM_BUOC = '#e77442'   # vòng tròn bước đang ở
CAM_NUT  = '#eea17f'   # nút "Tiếp tục"
CAM_MO   = '#fdf5f2'   # nền thẻ đang chọn
GIAY     = '#ffffff'
VIEN     = '#e7e9ee'
VIEN_MO  = '#f1f3f6'
NEN_NHAT = '#f7f8fa'
MUC      = '#1b2334'   # chữ tối trên nền trắng
MO       = '#6f7789'
NHAT     = '#9aa1b0'
NAV_CHU  = '#b6bac6'   # chữ menu thường
NAV_SANG = '#ffffff'
LUC      = '#1aa053'
LUC_MO   = '#e4f6ec'
CHO      = '#c8cedb'
TIM      = '#2b1b46'   # nền trang AIRTEX
VANG     = '#f2c45a'

# ══ HÌNH HỌC ═══════════════════════════════════════════════════════════════
SW = 190                      # bề rộng thanh bên
MX, MY = 198, 10              # góc trái trên thẻ trắng vùng chính
MW, MH = W - MX - 8, H - 20    # 1074 × 700
THANH_H = 56                  # dải tài khoản trên cùng

LE = 34                       # lề trong vùng chính
BODY_Y = MY + 160             # mép trên hai cột nội dung
BODY_H = 400
COT_W = 690                   # bề rộng thẻ nội dung
COT_X = MX + LE               # 232
PHAI_X = COT_X + COT_W + 22   # 944
PHAI_W = MX + MW - LE / 2 - PHAI_X   # tới mép phải trừ lề

MENU = ['Trang chủ', 'Triển khai website', 'Triển khai từ mẫu',
        'Tạo database', 'Sao lưu', 'Kết nối AI Agent']
MENU_SANG = 1
MENU_Y0, MENU_BUOC = 88, 31
GOI_HANG = [('Dịch vụ', '0/10'), ('CPU', '0/4 core'), ('RAM', '0/8 GB')]

BUOC_TEN = ['Mã nguồn', 'Chuẩn bị', 'Đưa lên mạng']
BUOC_X = [960, 1090, 1220]
BUOC_Y = MY + 96

# Khung ngắm khi zoom: camera đặt điểm (mx,my) vào giữa khung, độc lập với mức
# phóng. Ngắm sao cho thẻ tiến trình (232…922 ngang, 170…570 dọc) lọt TRỌN vào
# khung — cắt ngang mép thẻ thì nhìn như lỗi chứ không như cố ý. Mép trái khung
# cũng phải qua khỏi thanh bên (kết thúc ở x=190), không thì lòi ra một dải tối.
ZOOM = 1.5
ZOOM_X, ZOOM_Y = 620, 400

HE_SO_RONG = 0.62
BU_RONG = 6


def rong_chu(s, size):
    return max(len(d) for d in s.split('|')) * size * HE_SO_RONG + BU_RONG


def cao_chu(s, size):
    return len(s.split('|')) * size * 1.12


# ══ DỰNG PHẦN TỬ ═══════════════════════════════════════════════════════════
canhs, els = [], None
hop, trong, dong_bang = {}, {}, []


def mo_canh(id, giay, camera=None, camera_muot=None):
    global els
    els = []
    c = {'id': id, 'duration': giay, 'stagger': 0,
         'camera': camera or {'x': 0, 'y': 0, 'scale': 1}, 'elements': els}
    if camera_muot is not None:
        c['cameraMove'] = camera_muot
    canhs.append(c)


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


def chu(id, x, y, text, size=11, *, w=None, at=None, mau=None, align='left',
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


def the(id, x, y, w, h, at, *, nen=GIAY, vien=VIEN, r=12, vao='rise', dai=.45,
        chua=None, song=None):
    """Thẻ trắng có viền mảnh. Định dạng không có `border` nên viền là một khối
    lớn hơn 1px nằm dưới — trên nền trắng mà thiếu viền thì thẻ tan vào nền."""
    khoi(f'{id}-v', x - 1, y - 1, w + 2, h + 2, vien, r=r + 1, at=at, vao=vao,
         dai=dai, chua=chua, song=song)
    khoi(id, x, y, w, h, nen, r=r, at=at, vao=vao, dai=dai, chua=chua, song=song)


def dau_tick(id, cx, cy, R, mau, at, *, chua=None, day=None, vao='fade'):
    """Dấu tick vẽ bằng HAI THANH XOAY, không dùng ký tự — ký tự ✓ phụ thuộc
    phông máy đang chạy (máy này đã ra ô vuông với `＋` và `⧉`)."""
    T = day or max(2.4, R * 0.2)
    for i, (ax, ay, bx, by) in enumerate([(-.42, .02, -.10, .32), (-.10, .32, .44, -.30)]):
        x1, y1, x2, y2 = ax * R, ay * R, bx * R, by * R
        d = math.hypot(x2 - x1, y2 - y1) + T * .3
        goc = math.degrees(math.atan2(y2 - y1, x2 - x1))
        khoi(f'{id}-t{i}', cx + (x1 + x2) / 2 - d / 2, cy + (y1 + y2) / 2 - T / 2,
             d, T, mau, r=T / 2, at=at, vao=vao, dai=.25, xoay=goc, chua=chua)


def vien_dut(id, x, y, w, h, mau, at, *, day=2, net=13, khe=9, chua=None):
    """Viền nét đứt rải bằng vòng lặp — đổi kích thước vùng là viền tự chạy lại."""
    buoc = net + khe
    for i, cx in enumerate(range(0, int(w - net) + 1, buoc)):
        for cy, t in ((y, 'tr'), (y + h - day, 'du')):
            khoi(f'{id}-{t}{i}', x + cx, cy, net, day, mau, r=day / 2, at=at,
                 vao='fade', dai=.3, chua=chua)
    for i, cy in enumerate(range(buoc, int(h - net) + 1, buoc)):
        for cx, t in ((x, 'tra'), (x + w - day, 'ph')):
            khoi(f'{id}-{t}{i}', cx, y + cy, day, net, mau, r=day / 2, at=at,
                 vao='fade', dai=.3, chua=chua)


# ══ KHUNG ỨNG DỤNG — khai lại nguyên vẹn ở mỗi cảnh ════════════════════════
def khung_app(dong=False):
    """Thanh bên + thẻ trắng vùng chính + dải tài khoản.

    `dong=True` (cảnh 2, 3, 4): đứng sẵn từ giây 0, không diễn lại — để nó diễn
    lại thì mỗi lần chuyển cảnh cả ứng dụng nhấp nháy dựng từ đầu.
    """
    t = (lambda x: 0) if dong else (lambda x: x)
    v = (lambda x: 'none') if dong else (lambda x: x)

    khoi('nen', 0, 0, W, H, NEN_APP, r=0, **{'in': {'kind': 'none', 'dur': .001}})

    # ── thanh bên ─────────────────────────────────────────────────────────
    khoi('logo-o', 14, 16, 26, 26, CAM, r=8, at=t(.15), vao=v('pop'))
    chu('logo-ve', 14, 23, 'VE', size=11, w=26, align='center', at=t(.18),
        mau='#ffffff', vao=v('fade'))
    # `*Hosting*` lấy màu nhấn của clip — đúng cách trang thật tô chữ đó.
    chu('logo-ten', 48, 22, 'Vibe *Hosting*', size=14, at=t(.2), mau=NAV_SANG,
        vao=v('rise'))
    khoi('logo-gap', 152, 20, 15, 13, '#565a68', r=3, at=t(.24), vao=v('fade'))
    chu('kglv', 14, 62, 'KHÔNG GIAN LÀM VIỆC', size=8, at=t(.28), mau='#7c8598',
        vao=v('rise'))

    for i, ten in enumerate(MENU):
        y = MENU_Y0 + i * MENU_BUOC
        if i == MENU_SANG:
            khoi('menu-sang', 8, y - 6, SW - 16, 27, MUC_SANG, r=8, at=t(.32),
                 vao=v('fade'))
        khoi(f'menu-ic{i}', 20, y + 2, 13, 13, CAM if i == MENU_SANG else '#5e6373',
             r=3, at=t(.32 + i * .035), vao=v('fade'))
        chu(f'menu{i}', 42, y, ten, size=11, w=SW - 42 - 10,
            at=t(.32 + i * .035), mau=NAV_SANG if i == MENU_SANG else NAV_CHU,
            vao=v('rise'))

    gy = H - 116
    khoi('goi', 8, gy, SW - 16, 100, GOI_NEN, r=10, at=t(.56), vao=v('fade'))
    chu('goi-ten', 20, gy + 12, 'VAYS', size=11, at=t(.58), mau=NAV_SANG,
        vao=v('rise'), chua='goi')
    khoi('goi-huy', 76, gy + 10, 96, 17, GOI_HUY, r=8, at=t(.6), vao=v('fade'), chua='goi')
    chu('goi-huy-c', 76, gy + 14, 'Gói Vibe Host Pro', size=8, w=96, align='center',
        at=t(.62), mau='#d6d9e2', vao=v('fade'), chua='goi-huy')
    for i, (k, val) in enumerate(GOI_HANG):
        ry = gy + 42 + i * 20
        chu(f'goi-k{i}', 20, ry, k, size=9, w=70, at=t(.64 + i * .04), mau='#9aa0ae',
            vao=v('rise'), chua='goi')
        chu(f'goi-v{i}', SW - 20 - 62, ry, val, size=9, w=62, align='right',
            at=t(.64 + i * .04), mau='#dfe2ea', vao=v('rise'), chua='goi')

    # ── thẻ trắng vùng chính ──────────────────────────────────────────────
    khoi('app', MX, MY, MW, MH, GIAY, r=14, at=t(.12), vao=v('pop'))

    # dải tài khoản
    R = MX + MW
    khoi('tb-en', R - 238, MY + 18, 34, 24, NEN_NHAT, r=6, at=t(.42), vao=v('fade'), chua='app')
    chu('tb-en-c', R - 238, MY + 24, 'EN', size=9, w=34, align='center',
        at=t(.44), mau=MO, vao=v('fade'), chua='tb-en')
    khoi('tb-toi', R - 192, MY + 18, 24, 24, NEN_NHAT, r=12, at=t(.44), vao=v('fade'), chua='app')
    khoi('tb-toi-c', R - 186, MY + 24, 12, 12, '#8b93a3', r=6, at=t(.46), vao=v('fade'), chua='tb-toi')
    khoi('tb-vach', R - 160, MY + 20, 1, 20, VIEN, r=0, at=t(.46), vao=v('fade'), chua='app')
    khoi('tb-ava', R - 146, MY + 17, 26, 26, CAM, r=7, at=t(.48), vao=v('pop'), chua='app')
    chu('tb-ava-c', R - 146, MY + 24, 'VE', size=10, w=26, align='center',
        at=t(.5), mau='#ffffff', vao=v('fade'), chua='tb-ava')
    chu('tb-ten', R - 114, MY + 17, 'Nguyễn văn mười', size=10, w=100,
        at=t(.5), vao=v('rise'), chua='app')
    chu('tb-mail', R - 114, MY + 32, 'quynd@matbao.com', size=8, w=100,
        at=t(.52), mau=NHAT, vao=v('rise'), chua='app')
    khoi('tb-gach', MX, MY + THANH_H, MW, 1, VIEN_MO, r=0, at=t(.54), vao=v('fade'), chua='app')


def dai_buoc(dang, dong=False):
    """Dải ba bước ở góc phải trên. `dang` là chỉ số bước đang đứng (0-based);
    các bước trước nó hiện dấu tick."""
    t = (lambda x: 0) if dong else (lambda x: x)
    v = (lambda x: 'none') if dong else (lambda x: x)
    for i, ten in enumerate(BUOC_TEN):
        cx = BUOC_X[i]
        if i:
            khoi(f'bn{i}', BUOC_X[i - 1] + 15, BUOC_Y - 1, cx - BUOC_X[i - 1] - 30, 2,
                 CAM_BUOC if i <= dang else '#dfe6e6', r=1, at=t(.6), vao=v('fade'), chua='app')
        xong = i < dang
        khoi(f'bo{i}', cx - 13, BUOC_Y - 13, 26, 26,
             CAM_BUOC if i <= dang else '#edf1f1', r=13, at=t(.62 + i * .05),
             vao=v('pop'), chua='app')
        if xong:
            dau_tick(f'bt{i}', cx, BUOC_Y, 9, '#ffffff', t(.66 + i * .05), chua='app')
        else:
            chu(f'bs{i}', cx - 13, BUOC_Y - 6, str(i + 1), size=11, w=26, align='center',
                at=t(.66 + i * .05), mau='#ffffff' if i == dang else NHAT,
                vao=v('fade'), chua='app')
        chu(f'bl{i}', cx - 46, BUOC_Y + 20, ten, size=9, w=92, align='center',
            at=t(.68 + i * .05), mau=MUC if i <= dang else NHAT, vao=v('rise'), chua='app')


def cot_phai(tom_tat, at, *, hau='', dong=False):
    """Cột phải: Tóm tắt triển khai · Starter AI đề xuất · Lưu ý."""
    v = 'none' if dong else 'rise'
    x, w = PHAI_X, PHAI_W
    the(f'tt{hau}', x, BODY_Y, w, 138, at, vao='none' if dong else 'rise', chua='app')
    chu(f'tt{hau}-td', x + 22, BODY_Y + 20, 'Tóm tắt triển khai', size=13, at=at + .04,
        vao=v, chua=f'tt{hau}')
    for i, (k, val, mau) in enumerate(tom_tat):
        ry = BODY_Y + 54 + i * 26
        chu(f'tt{hau}-k{i}', x + 22, ry, k, size=10, w=110, at=at + .06 + i * .04,
            mau=MO, vao=v, chua=f'tt{hau}')
        chu(f'tt{hau}-v{i}', x + w - 22 - 150, ry, val, size=10, w=150, align='right',
            at=at + .06 + i * .04, mau=mau, vao=v, chua=f'tt{hau}')

    y2 = BODY_Y + 152
    the(f'ai{hau}', x, y2, w, 86, at + .1, nen=NEN_NHAT, vien=VIEN_MO,
        vao='none' if dong else 'rise', chua='app')
    khoi(f'ai{hau}-ic', x + 20, y2 + 18, 13, 13, CAM, r=3, at=at + .12, vao='fade', chua=f'ai{hau}')
    chu(f'ai{hau}-td', x + 40, y2 + 16, 'Starter — AI đề xuất', size=11, at=at + .12,
        vao=v, chua=f'ai{hau}')
    chu(f'ai{hau}-p', x + 40, y2 + 40, 'Phù hợp cho lần đưa website lên|mạng đầu tiên; đổi được sau.',
        size=9, w=w - 60, at=at + .14, mau=MO, vao=v, chua=f'ai{hau}')

    y3 = y2 + 100
    LUU_Y = ['Website được cấp SSL miễn phí.', 'Triển khai thường mất 1–3 phút.',
             'Nâng cấp tài nguyên bất kỳ lúc nào.']
    the(f'ly{hau}', x, y3, w, 110, at + .16, nen=NEN_NHAT, vien=VIEN_MO,
        vao='none' if dong else 'rise', chua='app')
    khoi(f'ly{hau}-ic', x + 20, y3 + 16, 13, 13, CAM, r=3, at=at + .18, vao='fade', chua=f'ly{hau}')
    chu(f'ly{hau}-td', x + 40, y3 + 14, 'Lưu ý', size=11, at=at + .18, vao=v, chua=f'ly{hau}')
    for i, d in enumerate(LUU_Y):
        ry = y3 + 40 + i * 22
        dau_tick(f'ly{hau}-t{i}', x + 27, ry + 6, 7, LUC, at + .2 + i * .04, chua=f'ly{hau}')
        chu(f'ly{hau}-d{i}', x + 40, ry, d, size=9, w=w - 60, at=at + .2 + i * .04,
            mau=MO, vao=v, chua=f'ly{hau}')


# ══════════════════════════════════════════════════════════════════════════
# CẢNH 1 — chọn nguồn, kéo thả tệp vào thẻ "Tải file"
# ══════════════════════════════════════════════════════════════════════════
C1 = 5.0
mo_canh('c1-keo-tha', C1)
khung_app()
dai_buoc(0)

chu('td', MX + LE, MY + 84, 'Đưa website lên mạng', size=23, at=.7, chua='app')
chu('td-phu', MX + LE, MY + 118,
    'Chọn mã nguồn, kiểm tra thông tin rồi để VAYS lo phần kỹ thuật',
    size=11, w=440, at=.74, mau=MO, chua='app')

the('nd', COT_X, BODY_Y, COT_W, BODY_H, .8, chua='app')
chu('nd-td', COT_X + 24, BODY_Y + 22, 'Chọn nguồn', size=15, at=.84, chua='nd')

# năm thẻ nguồn, đúng thứ tự và câu chữ của sản phẩm
NGUON = [
    ('Tải file', 'Kéo-thả hoặc chọn|file .zip, .html, .htm'),
    ('Dán HTML', 'Dán trực tiếp mã|HTML vào ô soạn thảo'),
    ('GitHub', 'Kết nối GitHub|(OAuth), tự deploy'),
    ('Git URL', 'Clone từ URL repo|công khai'),
    ('Vercel', 'Import từ Vercel|Project URL + Token'),
]
NG_X, NG_W, NG_H = COT_X + 24, (COT_W - 48 - 24) / 3, 62
NG_Y = [BODY_Y + 52, BODY_Y + 52 + NG_H + 12]
T_CHON = 2.75          # giây thẻ "Tải file" được chọn


def the_nguon(i, ten, phu, at):
    x = NG_X + (i % 3) * (NG_W + 12)
    y = NG_Y[i // 3]
    the(f'ng{i}', x, y, NG_W, NG_H, at, nen='#fcfcfd', vien='#eceff4', r=10, chua='nd')
    khoi(f'ng{i}-o', x + 12, y + 16, 30, 30, '#f2f4f8', r=8, at=at + .03, vao='pop', chua=f'ng{i}')
    chu(f'ng{i}-t', x + 50, y + 13, ten, size=11, w=NG_W - 60, at=at + .04, chua=f'ng{i}')
    chu(f'ng{i}-p', x + 50, y + 31, phu, size=8, w=NG_W - 60, at=at + .06, mau=MO, chua=f'ng{i}')
    return x, y


for i, (ten, phu) in enumerate(NGUON):
    the_nguon(i, ten, phu, .9 + i * .07)

# thẻ "Tải file" sáng viền cam khi tệp rơi vào
TF_X, TF_Y = NG_X, NG_Y[0]
khoi('ng0-vien', TF_X - 2, TF_Y - 2, NG_W + 4, NG_H + 4, CAM_BUOC, r=12,
     at=T_CHON, vao='fade', dai=.3, chua='nd')
khoi('ng0-nen', TF_X, TF_Y, NG_W, NG_H, CAM_MO, r=10, at=T_CHON, vao='fade', dai=.3, chua='nd')
khoi('ng0-o2', TF_X + 12, TF_Y + 16, 30, 30, '#fbe3d5', r=8, at=T_CHON + .04, vao='fade', chua='ng0-nen')
chu('ng0-t2', TF_X + 50, TF_Y + 13, 'Tải file', size=11, w=NG_W - 60, at=T_CHON + .04, chua='ng0-nen')
chu('ng0-p2', TF_X + 50, TF_Y + 31, 'ttindex.html  ·  68 KB', size=8, w=NG_W - 60,
    at=T_CHON + .06, mau=CAM_CHU, chua='ng0-nen')
khoi('ng0-dau', TF_X + NG_W - 22, TF_Y + 8, 15, 15, CAM_BUOC, r=8, at=T_CHON + .1,
     vao='pop', dai=.35, chua='ng0-nen')
dau_tick('ng0-tick', TF_X + NG_W - 14.5, TF_Y + 15.5, 5.5, '#ffffff', T_CHON + .16,
         chua='ng0-nen', day=1.8)

# ── khu "Tải file" bên dưới lưới nguồn ────────────────────────────────────
TAI_Y = NG_Y[1] + NG_H + 24
khoi('nd-gach', COT_X + 24, TAI_Y - 12, COT_W - 48, 1, VIEN_MO, r=0, at=1.3,
     vao='fade', chua='nd')
chu('tai-td', COT_X + 24, TAI_Y, 'Tải file', size=13, at=1.32, chua='nd')
THA_X, THA_Y = COT_X + 24, TAI_Y + 26
THA_W, THA_H = COT_W - 48, 104
khoi('tha', THA_X, THA_Y, THA_W, THA_H, '#fafbfc', r=10, at=1.36, vao='fade', chua='nd')
vien_dut('tha-v', THA_X, THA_Y, THA_W, THA_H, '#cfd6e3', 1.4, chua='nd')
khoi('tha-o', THA_X + THA_W / 2 - 19, THA_Y + 20, 38, 38, '#f2f4f8', r=10, at=1.44,
     vao='pop', song=T_CHON - 1.44 - .3, chua='nd', **{'out': {'kind': 'fade', 'dur': .2}})
chu('tha-c', THA_X, THA_Y + 68, 'Kéo-thả tệp .html vào đây', size=11, w=THA_W,
    align='center', at=1.5, mau=MO, song=T_CHON - 1.5 - .3, chua='nd',
    **{'out': {'kind': 'fade', 'dur': .2}})

# thẻ tệp: bản nổi ở góc trên, và bản rơi vào ô
def the_tep(id, x, y, at, *, vao='rise', song=None, chua=None):
    w, h = 232, 58
    the(id, x, y, w, h, at, vao=vao, r=10, song=song, chua=chua)
    khoi(f'{id}-o', x + 13, y + 13, 32, 32, CAM_MO, r=8, at=at + .03, vao='fade',
         song=song, chua=id)
    chu(f'{id}-ic', x + 13, y + 22, '< >', size=12, w=32, align='center', at=at + .05,
        mau=CAM_CHU, vao='fade', song=song, chua=f'{id}-o')
    chu(f'{id}-t', x + 56, y + 12, 'ttindex.html', size=12, at=at + .05, vao='fade',
        song=song, chua=id)
    chu(f'{id}-p', x + 56, y + 32, 'HTML  ·  68 KB', size=9, w=140, at=at + .07,
        mau=MO, vao='fade', song=song, chua=id)


the_tep('tep-a', MX + MW - 268, MY + 78, 1.25, song=1.45)
the_tep('tep-b', THA_X + (THA_W - 232) / 2, THA_Y + (THA_H - 58) / 2, T_CHON - .1,
        vao='fall', chua='nd')

# nút Tiếp tục
NUT_Y = BODY_Y + BODY_H - 52
khoi('nut', COT_X + COT_W - 24 - 118, NUT_Y, 118, 34, CAM_NUT, r=17, at=1.6, vao='fade', chua='nd')
chu('nut-c', COT_X + COT_W - 24 - 118, NUT_Y + 10, 'Tiếp tục  →', size=11, w=118,
    align='center', at=1.62, mau='#ffffff', chua='nut')

cot_phai([('Nguồn', 'Chưa chọn', NHAT), ('Tên website', 'Chưa đặt', NHAT),
          ('Địa chỉ', 'Chưa đặt', NHAT)], 1.0)
cot_phai([('Nguồn', 'Tải file', CAM_CHU), ('Tên website', 'airtex-trungthu', MUC),
          ('Địa chỉ', 'Chưa đặt', NHAT)], T_CHON + .25, hau='x')

# con trỏ: nhặt tệp ở góc trên phải, kéo xuống thả vào thẻ "Tải file"
els.append({
    'id': 'tro', 'kind': 'pointer', 'x': 0, 'y': 0,
    'path': [{'t': .95, 'x': W - 20, 'y': 40},
             {'t': 1.62, 'x': MX + MW - 160, 'y': MY + 106},
             {'t': 1.9, 'x': MX + MW - 160, 'y': MY + 106},
             {'t': 2.72, 'x': TF_X + NG_W / 2, 'y': TF_Y + NG_H / 2},
             {'t': 4.6, 'x': TF_X + NG_W / 2, 'y': TF_Y + NG_H / 2}],
    'clicks': [{'t': 1.75, 'x': MX + MW - 160, 'y': MY + 106},
               {'t': 2.78, 'x': TF_X + NG_W / 2, 'y': TF_Y + NG_H / 2}],
})


# ══════════════════════════════════════════════════════════════════════════
# THẺ TIẾN TRÌNH — dựng theo `public/image/database khởi tạo.png`
# ══════════════════════════════════════════════════════════════════════════
BUOC_CHAY = [
    ('Tải mã nguồn', 'Đang tải ttindex.html lên máy chủ…'),
    ('Cài đặt máy chủ', 'Dựng môi trường chạy web tĩnh…'),
    ('Cấp chứng chỉ SSL', 'Xin chứng chỉ Let\'s Encrypt…'),
    ('Kết nối database', 'Gắn cơ sở dữ liệu airtex_db…'),
]
HANG_Y0, HANG_BUOC = BODY_Y + 142, 44
VACH_N, VACH_KHE = 30, 3


def the_tien_trinh(moc, vach_da, vach_toi, *, hau='', t0=.15, buoc=.09, phan_tram=None):
    """`moc[i]`: None = chưa bắt đầu · 0 = xong sẵn · >0 = đánh dấu xong ở giây đó.
    Bước ngay sau bước xong cuối cùng được coi là ĐANG CHẠY."""
    the(f'tk{hau}', COT_X, BODY_Y, COT_W, BODY_H, 0, vao='none', chua='app')
    chu(f'tk{hau}-td', COT_X + 26, BODY_Y + 22, 'Đưa website lên mạng', size=15,
        at=0, vao='none', chua=f'tk{hau}')
    chu(f'tk{hau}-p', COT_X + 26, BODY_Y + 46, 'Hệ thống đang triển khai ttindex.html — 68 KB',
        size=10, at=0, vao='none', mau=MO, chua=f'tk{hau}')
    khoi(f'tk{hau}-g', COT_X + 26, BODY_Y + 74, COT_W - 52, 1, VIEN_MO, r=0,
         at=0, vao='none', chua=f'tk{hau}')
    chu(f'tk{hau}-td2', COT_X + 26, BODY_Y + 92, 'Đang đưa website lên mạng…', size=13,
        at=0, vao='none', chua=f'tk{hau}')
    chu(f'tk{hau}-p2', COT_X + 26, BODY_Y + 116,
        'Hệ thống đang xử lý — quá trình chạy nền, bạn có thể chờ tại đây.',
        size=10, w=COT_W - 60, at=0, vao='none', mau=MO, chua=f'tk{hau}')
    dong_bang.append((canhs[-1]['id'], 'phần đầu thẻ', BODY_Y + 92, BODY_Y + 130))

    xong_cuoi = max([i for i, m in enumerate(moc) if m is not None], default=-1)
    for i, (ten, phu) in enumerate(BUOC_CHAY):
        y = HANG_Y0 + i * HANG_BUOC
        dong_bang.append((canhs[-1]['id'], f'bước {i + 1} · {ten}', y, y + 34))
        m = moc[i]
        chay = m is None and i == xong_cuoi + 1
        if m is None:
            khoi(f'tk{hau}-o{i}', COT_X + 26, y + 1, 17, 17,
                 '#fdf0e9' if chay else '#f4f6f9', r=9, at=0, vao='none', chua=f'tk{hau}')
            khoi(f'tk{hau}-r{i}', COT_X + 30, y + 5, 9, 9,
                 CAM_BUOC if chay else '#dfe3ea', r=5, at=0, vao='none', chua=f'tk{hau}-o{i}')
        else:
            khoi(f'tk{hau}-o{i}', COT_X + 26, y + 1, 17, 17, LUC_MO, r=9,
                 at=m, vao='none' if m == 0 else 'pop', dai=.3, chua=f'tk{hau}')
            dau_tick(f'tk{hau}-k{i}', COT_X + 34.5, y + 9.5, 6, LUC, m + (0 if m == 0 else .05),
                     chua=f'tk{hau}', day=1.9)
        chu(f'tk{hau}-t{i}', COT_X + 54, y, ten, size=11.5, at=m or 0,
            vao='none' if (m is None or m == 0) else 'rise',
            mau=None if (m is not None or chay) else NHAT, chua=f'tk{hau}')
        if chay:
            bx = COT_X + 54 + rong_chu(ten, 11.5) + 8
            khoi(f'tk{hau}-b{i}', bx, y - 1, 58, 16, NEN_NHAT, r=8, at=0, vao='none', chua=f'tk{hau}')
            chu(f'tk{hau}-bc{i}', bx, y + 2, 'Đang chạy', size=8, w=58, align='center',
                at=0, vao='none', mau=MO, chua=f'tk{hau}-b{i}')
        chu(f'tk{hau}-s{i}', COT_X + 54, y + 18,
            phu if (m is not None or chay) else 'Chưa bắt đầu', size=9,
            w=COT_W - 90, at=m or 0, vao='none' if (m is None or m == 0) else 'rise',
            mau=MO if (m is not None or chay) else NHAT, chua=f'tk{hau}')

    # thanh tiến trình: nhiều vạch sáng dần — không đổi được bề rộng theo thời gian
    ty = BODY_Y + BODY_H - 78
    dong_bang.append((canhs[-1]['id'], 'thanh tiến trình', ty, ty + 6))
    tw = COT_W - 52
    vw = (tw - VACH_KHE * (VACH_N - 1)) / VACH_N
    for i in range(VACH_N):
        if i < vach_da:
            mau, at_, vao = CAM_BUOC, 0, 'none'
        elif i < vach_toi:
            mau, at_, vao = CAM_BUOC, round(t0 + (i - vach_da) * buoc, 2), 'pop'
        else:
            mau, at_, vao = '#eef1f4', 0, 'none'
        khoi(f'tk{hau}-v{i}', COT_X + 26 + i * (vw + VACH_KHE), ty, vw, 6, mau, r=3,
             at=at_, vao=vao, dai=.18, chua=f'tk{hau}')
    cy = ty + 18
    dong_bang.append((canhs[-1]['id'], 'dòng thời gian', cy, cy + 12))
    chu(f'tk{hau}-dc', COT_X + 26, cy, 'Đã chạy: 00:0' + str(len([m for m in moc if m is not None])),
        size=9, at=0, vao='none', mau=MO, chua=f'tk{hau}')
    chu(f'tk{hau}-pt', COT_X + COT_W - 26 - 60, cy, phan_tram or f'{round(vach_toi / VACH_N * 100)}%',
        size=9, w=60, align='right', at=0, vao='none', mau=MO, chua=f'tk{hau}')


TOM_TAT_XONG = [('Nguồn', 'Tải file', CAM_CHU),
                ('Tên website', 'airtex-trungthu', MUC),
                ('Địa chỉ', 'airtex-trungthu.vibehost.vn', MUC)]

# ══════════════════════════════════════════════════════════════════════════
# CẢNH 2 — đang đưa lên mạng, thẻ SSL bật ra giữa khung hình
# ══════════════════════════════════════════════════════════════════════════
C2 = 4.2
mo_canh('c2-trien-khai', C2)
khung_app(dong=True)
dai_buoc(2, dong=True)
chu('td', MX + LE, MY + 84, 'Đưa website lên mạng', size=23, at=0, vao='none', chua='app')
chu('td-phu', MX + LE, MY + 118, 'Chọn mã nguồn, kiểm tra thông tin rồi để VAYS lo phần kỹ thuật',
    size=11, w=440, at=0, vao='none', mau=MO, chua='app')
the_tien_trinh([.4, 1.1, 2.0, None], 0, 22, t0=.15, buoc=.09)
cot_phai(TOM_TAT_XONG, 0, dong=True)

# ── THẺ SSL BẬT RA GIỮA KHUNG HÌNH ────────────────────────────────────────
PW, PH = 420, 292
PPX, PPY = (W - PW) / 2, (H - PH) / 2
T_SSL, SONG_SSL = 2.05, 1.45
khoi('ssl-bong', PPX - 4, PPY - 4, PW + 8, PH + 8, '#00000018', r=26,
     at=T_SSL, vao='pop', dai=.5, song=SONG_SSL)
khoi('ssl', PPX, PPY, PW, PH, GIAY, r=22, at=T_SSL, vao='pop', dai=.5, song=SONG_SSL)
khoi('ssl-vong', PPX + PW / 2 - 52, PPY + 38, 104, 104, LUC_MO, r=52,
     at=T_SSL + .08, vao='pop', dai=.5, song=SONG_SSL - .08, chua='ssl')
khoi('ssl-tron', PPX + PW / 2 - 38, PPY + 52, 76, 76, LUC, r=38,
     at=T_SSL + .14, vao='pop', dai=.45, song=SONG_SSL - .14, chua='ssl')
dau_tick('ssl-dau', PPX + PW / 2, PPY + 90, 32, '#ffffff', T_SSL + .3, chua='ssl', day=7)
chu('ssl-td', PPX, PPY + 166, 'Đã cấp chứng chỉ SSL', size=21, w=PW, align='center',
    at=T_SSL + .34, song=SONG_SSL - .34, chua='ssl')
chu('ssl-phu', PPX, PPY + 200, 'Website đã được cấp SSL miễn phí', size=11, w=PW,
    align='center', at=T_SSL + .4, mau=MO, song=SONG_SSL - .4, chua='ssl')
khoi('ssl-nhan', PPX + PW / 2 - 64, PPY + 230, 128, 26, LUC_MO, r=13,
     at=T_SSL + .46, vao='pop', song=SONG_SSL - .46, chua='ssl')
chu('ssl-nhan-c', PPX + PW / 2 - 64, PPY + 236, 'HTTPS đang bật', size=11, w=128,
    align='center', at=T_SSL + .5, mau=LUC, song=SONG_SSL - .5, chua='ssl')


# ══════════════════════════════════════════════════════════════════════════
# CẢNH 3 — CAMERA ZOOM vào thẻ tiến trình, database bật đèn xanh
# ══════════════════════════════════════════════════════════════════════════
C3 = 2.8
T_DB = .85
mo_canh('c3-zoom', C3, camera={'x': ZOOM_X - W / 2, 'y': ZOOM_Y - H / 2, 'scale': ZOOM},
        camera_muot=1.0)
khung_app(dong=True)
dai_buoc(2, dong=True)
chu('td', MX + LE, MY + 84, 'Đưa website lên mạng', size=23, at=0, vao='none', chua='app')
chu('td-phu', MX + LE, MY + 118, 'Chọn mã nguồn, kiểm tra thông tin rồi để VAYS lo phần kỹ thuật',
    size=11, w=440, at=0, vao='none', mau=MO, chua='app')
the_tien_trinh([0, 0, 0, T_DB], 22, VACH_N, t0=.05, buoc=.06, phan_tram='100%')
cot_phai(TOM_TAT_XONG, 0, dong=True)

# đèn xanh database: chấm sáng nhấp ở hàng cuối
dbY = HANG_Y0 + 3 * HANG_BUOC
khoi('db-den-vong', COT_X + COT_W - 60, dbY + 2, 16, 16, LUC_MO, r=8,
     at=T_DB + .1, vao='pop', dai=.45, chua='tk')
khoi('db-den', COT_X + COT_W - 56, dbY + 6, 8, 8, LUC, r=4, at=T_DB + .16,
     vao='pop', dai=.4, chua='db-den-vong')
chu('db-xong', COT_X + COT_W - 60 - 96, dbY + 3, 'Đã kết nối', size=9, w=90,
    align='right', at=T_DB + .2, mau=LUC, chua='tk')


# ══════════════════════════════════════════════════════════════════════════
# CẢNH 4 — TRANG BẬT RA GIỮA KHUNG HÌNH
#
# Camera lùi về ×1 trong lúc cửa sổ trình duyệt nở ra ở giữa: cú lùi và cú nở
# đi ngược chiều nhau nên mắt bám vào trang, không bám vào dashboard.
# Màu lấy thẳng từ `public/html-foot/ttindex.html`.
# ══════════════════════════════════════════════════════════════════════════
C4 = 3.0
mo_canh('c4-bat-ra', C4, camera_muot=.85)
khung_app(dong=True)
dai_buoc(2, dong=True)
chu('td', MX + LE, MY + 84, 'Đưa website lên mạng', size=23, at=0, vao='none', chua='app')
chu('td-phu', MX + LE, MY + 118, 'Chọn mã nguồn, kiểm tra thông tin rồi để VAYS lo phần kỹ thuật',
    size=11, w=440, at=0, vao='none', mau=MO, chua='app')
the_tien_trinh([0, 0, 0, 0], VACH_N, VACH_N, phan_tram='100%')
cot_phai(TOM_TAT_XONG, 0, dong=True)

# ── cửa sổ trình duyệt ────────────────────────────────────────────────────
BW, BH = 760, 430
BX, BY = (W - BW) / 2, (H - BH) / 2          # 260, 145 — đúng tâm khung
THANH = 38                                    # dải điều khiển trên cùng
T_BAT = .5
khoi('br-bong', BX - 5, BY - 5, BW + 10, BH + 10, '#0000001c', r=15,
     at=T_BAT, vao='pop', dai=.55)
khoi('br', BX, BY, BW, BH, '#0b0f24', r=10, at=T_BAT, vao='pop', dai=.55)
# ── ruột trang: ẢNH CHỤP THẬT của `public/html-foot/ttindex.html` ────────
#
# Trước đây tôi vẽ tay lại trang bằng khối và chữ — nhìn hao hao nhưng không
# phải nó: sai phông, sai bố cục, thiếu mây, thiếu sao, thiếu ảnh áo. Vẽ tay
# một trang thật thì không bao giờ giống được.
#
# Ảnh chụp ở khổ 1520×784, đúng 2× vùng trang trong cửa sổ (760×392), nên
# không co giãn méo và vẫn nét khi xuất 1080p. Sinh lại bằng:
#     node tools/chup-ttindex.mjs
# Ảnh nằm ĐÚNG vùng trang (dưới dải điều khiển), khổ khớp đúng tỉ lệ ảnh chụp
# nên `cover` không cắt mất gì. Đặt phủ cả cửa sổ thì dải điều khiển che mất
# dải khuyến mãi và logo AIRTEX ở đầu trang — đã mắc một lần.
T_TR = T_BAT + .28
E('tr', 'image', BX, BY + THANH, BW, BH - THANH,
  src='public/image/ttindex-xem-truoc.png', radius=0, fit='cover',
  chua='br', **{'at': round(T_TR, 2), 'in': {'kind': 'fade', 'ease': 'out', 'dur': .5}})

# Dải điều khiển khai SAU ảnh để nằm trên nó.
khoi('br-thanh', BX, BY, BW, THANH, '#171c34', r=10, at=T_BAT + .04, vao='fade', chua='br')
for i, mau in enumerate(['#ff5f57', '#febc2e', '#28c840']):
    khoi(f'br-cham{i}', BX + 18 + i * 18, BY + 14, 10, 10, mau, r=5,
         at=T_BAT + .08 + i * .03, vao='pop', dai=.3, chua='br-thanh')
khoi('br-url', BX + 84, BY + 9, 320, 20, '#242a45', r=10, at=T_BAT + .14,
     vao='fade', chua='br-thanh')
khoi('br-khoa', BX + 94, BY + 14, 8, 10, LUC, r=2, at=T_BAT + .17, vao='pop',
     dai=.3, chua='br-url')
chu('br-diachi', BX + 108, BY + 13, 'airtex-trungthu.vibehost.vn', size=10,
    w=286, at=T_BAT + .18, mau='#c9d2ea', chua='br-url')

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
        if d and d[-1][3] > BODY_Y + BODY_H - 6:
            loi.append(f'[{c["id"]}] "{d[-1][1]}" xuống tới {d[-1][3]:.0f}, '
                       f'tràn khỏi thẻ kết thúc ở {BODY_Y + BODY_H}.')


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
    'meta': {'name': 'Kéo thả HTML → Vibe Hosting chạy ngay', 'width': W, 'height': H,
             'density': 1, 'bg': NEN_APP, 'accent': CAM_CHU, 'accent2': '#ff9a3c',
             'hot': CAM_CHU, 'hot2': '#e3272c', 'ink': MUC,
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
