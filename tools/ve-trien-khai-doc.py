#!/usr/bin/env python3
"""Clip dọc 9:16 — kéo thả một file HTML vào Vibe Hosting rồi web chạy.

GIAO DIỆN LÀ PIXEL THẬT, KHÔNG PHẢI TÔI VẼ LẠI.

Học từ chính clip của đội (`vibe-host-map-domain.html`,
`vibe-host-trien-khai-web.html`): họ PHÁT bản ghi màn hình thật rồi zoom và vẽ
vòng cam lên trên. Định dạng kịch bản cảnh không có kiểu `video`, nhưng có kiểu
`image` — nên ở đây ta cắt đúng những khung cần từ chính bản ghi đó
(`tools/chup-man-vibe.mjs`) và để CAMERA làm phần zoom.

Ngữ pháp mượn nguyên của đội:
  · nền tối bao quanh, thanh trên có hiệu + địa chỉ + tên bài hướng dẫn
  · màn hình thật nằm trong một thẻ bo góc
  · VÒNG CAM khoanh đúng chỗ đang nói tới
  · viên thuốc thuyết minh ở đáy
  · dải bước của sản phẩm ở dưới cùng

MỘT CHỖ PHẢI CẨN THẬN: camera phóng MỌI THỨ trong `#cam`, kể cả viên thuốc
thuyết minh. Cảnh nào đẩy máy vào thì chữ phải đặt qua `neo_man()` và chia cỡ
cho mức phóng, không thì nó bị phóng theo rồi văng ra ngoài khung.

MỘT CHỖ CHƯA KHỚP, nói thẳng: bản ghi quay luồng **Git URL**, sản phẩm chưa có
bản ghi luồng **Tải file**. Nên ở nhịp kéo thả, khung ngắm chỉ lấy HÀNG TRÊN
của lưới nguồn — thẻ "Git URL" đang được chọn nằm ở hàng dưới, ngoài khung.
Muốn khớp tuyệt đối thì cần một bản ghi 30 giây luồng tải file.

Chạy: python3 tools/ve-trien-khai-doc.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import ve_chung as v                                          # noqa: E402
from ve_chung import chu, dau_tick, khoi, mo_canh, the        # noqa: E402

W, H = 720, 1280
v.dat_khung(W, H)
GOC = pathlib.Path('/home/coder/workspace/projects/clipVibehost/hosting-animatic-production')
OUT = GOC / 'scenes' / 'thu-trien-khai-doc.json'
KIEM = pathlib.Path(__file__).parent / f'kiem-{OUT.stem}.json'

# ══ MÀU — lấy từ `vibe-host-trien-khai-web.html` của đội ═══════════════════
NEN      = '#07130d'
NEN_2    = '#0d2118'
VIEN_MO  = 'rgba(255,255,255,.10)'
CAM      = '#ff671a'
CAM_2    = '#ffa24d'
LUC      = '#21c07a'
CHU      = '#eaf4ee'
CHU_MO   = '#8fae9c'
TOI      = '#0b1c13'
GIAY     = '#ffffff'
MUC      = '#0f172a'
MO       = '#64748b'
LUC_MO   = '#dcfce7'
CAM_MO   = '#fff1e9'

# ══ HÌNH HỌC ═══════════════════════════════════════════════════════════════
THANH_H = 88                                   # thanh trên
TD_Y = 140                                     # câu tiêu đề
MAN_CY = 560                                   # tâm dọc của ảnh màn hình
LOI_Y = 800                                    # dự phòng khi không truyền y
# Viên thuốc bám ngay dưới đáy ảnh chứ không đứng ở một y cố định: mỗi nhịp
# một khung cắt cao thấp khác nhau, neo cứng thì có nhịp hở cả trăm pixel.
LOI_HO = 44
RAY_Y = 900                                    # dải bước
CHAN_Y = 986

BUOC_TEN = ['Mã nguồn', 'Chuẩn bị', 'Đưa lên mạng']

# Mỗi nhịp một khung cắt riêng, kích thước thật lấy từ tools/chup-man-vibe.mjs.
# (tên tệp, rộng thật, cao thật, bề rộng trên sân khấu)
CAT = {
    'nguon':   ('vh-man-nguon.png',   1170, 258, 700),
    'taifile': ('vh-man-taifile.png',  396,  92, 660),
    'chay':    ('vh-man-chay.png',     810, 275, 690),
    'xong':    ('vh-man-xong.png',     470, 300, 620),
}

# ══ KHUNG BAO — thanh trên · thẻ màn hình · dải bước ═══════════════════════
def khung(khoa, buoc_dang, *, dong=False, cam=None):
    """Nền + thanh trên + ẢNH MÀN HÌNH THẬT + dải bước.

    `khoa` chọn một khung cắt trong `CAT`. Trả về hàm quy đổi toạ độ TRÊN ẢNH
    THẬT sang toạ độ sân khấu, để vẽ vòng cam đúng chỗ.
    """
    tep, rw, rh, sw = CAT[khoa]
    k = sw / rw
    sh = rh * k
    x, y = (W - sw) / 2, MAN_CY - sh / 2

    d = (lambda t: 0) if dong else (lambda t: t)
    va = (lambda t: 'none') if dong else (lambda t: t)
    khoi('nen', 0, 0, W, H, NEN, r=0, **{'in': {'kind': 'none', 'dur': .001}})
    khoi('man-v', x - 2, y - 2, sw + 4, sh + 4, 'rgba(255,255,255,.16)', r=14,
         at=d(.12), vao=va('pop'))
    v.anh('man', x, y, sw, sh, f'public/image/{tep}', radius=12,
          at=0 if dong else .14, vao='none' if dong else 'pop', dai=.5)
    _khung_chu(d, va, cam, buoc_dang)

    def R(rx, ry, rw2=0, rh2=0):
        return (x + rx * k, y + ry * k, rw2 * k, rh2 * k)
    R.day = y + sh                      # đáy ảnh, để neo viên thuốc
    return R


def _khung_chu(d, va, cam, buoc_dang):
    """Chữ quanh màn hình. Có `cam` thì neo theo màn hình và chia cỡ cho mức phóng."""
    s = 1 if cam is None else cam.get('scale', 1)

    def P(x, y):
        return (x, y) if cam is None else v.neo_man(x, y, cam)

    def C(n):
        return n / s

    # thanh trên
    khoi('tb', *P(0, 0), C(W), C(THANH_H), TOI, r=0, at=d(.05), vao=va('fade'))
    khoi('tb-cham', *P(28, 40), C(12), C(12), CAM, r=C(6), at=d(.08), vao=va('pop'), chua='tb')
    chu('tb-hieu', *P(50, 32), 'Vibe Host', size=C(22), at=d(.1), mau=CHU,
        vao=va('rise'), chua='tb')
    khoi('tb-dc', *P(184, 30), C(238), C(34), 'rgba(255,255,255,.06)', r=C(17),
         at=d(.12), vao=va('fade'), chua='tb')
    chu('tb-dc-c', *P(184, 39), 'vibehost.matbao.ai', size=C(15), w=C(238),
        align='center', at=d(.14), mau='#b9cfc2', vao=va('fade'), chua='tb-dc')
    chu('tb-bai', *P(W - 262, 36), 'Hướng dẫn · *Triển khai website*', size=C(15),
        w=C(238), align='right', at=d(.16), mau='#cfe3d6', vao=va('rise'), chua='tb')

    # dải bước của sản phẩm
    khoi('ray', *P(0, RAY_Y), C(W), C(64), TOI, r=0, at=d(.5), vao=va('fade'))
    x = 24
    for i, ten in enumerate(BUOC_TEN):
        w = v.rong_chu(ten, 16) + 46
        dang = i == buoc_dang
        khoi(f'ray{i}', *P(x, RAY_Y + 16), C(w), C(32),
             'rgba(255,103,26,.18)' if dang else 'rgba(255,255,255,.05)', r=C(16),
             at=d(.52 + i * .05), vao=va('fade'), chua='ray')
        khoi(f'ray{i}-c', *P(x + 14, RAY_Y + 27), C(10), C(10),
             CAM if dang else '#4d6b5b', r=C(5), at=d(.54 + i * .05),
             vao=va('pop'), chua=f'ray{i}')
        chu(f'ray{i}-t', *P(x + 30, RAY_Y + 23), ten, size=C(16), w=C(w - 44),
            at=d(.54 + i * .05), mau=CAM_2 if dang else CHU_MO, vao=va('rise'),
            chua=f'ray{i}')
        x += w + 10

    chu('chan', *P(24, CHAN_Y), 'airtex-trungthu.vibehost.vn', size=C(15),
        w=C(W - 48), align='center', at=d(.66), mau='#5f7f6e', vao=va('fade'))


def tieu_de(dong=False, cam=None, tan=None):
    """Câu tiêu đề phía trên màn hình."""
    d = (lambda x: 0) if dong else (lambda x: x)
    va = (lambda x: 'none') if dong else (lambda x: x)
    s = 1 if cam is None else cam.get('scale', 1)
    P = (lambda x, y: (x, y)) if cam is None else (lambda x, y: v.neo_man(x, y, cam))
    t = {} if tan is None else {'song': tan, 'out': {'kind': 'fade', 'dur': .3}}
    chu('td', *P(24, TD_Y), 'Kéo thả một file HTML,|*web chạy sau 3 phút*',
        size=44 / s, w=(W - 48) / s, at=d(.2), mau=CHU, vao=va('rise'), **t)


def loi_thoai(id, text, at, cam=None, song=None, day_san=None):
    """Viên thuốc thuyết minh — đúng kiểu clip hướng dẫn của đội."""
    s = 1 if cam is None else cam.get('scale', 1)
    w = min(v.rong_chu(text, 19) + 52, W - 40)
    x = (W - w) / 2
    # `day_san` là đáy ảnh trên SÂN KHẤU. Cảnh có zoom thì phải quy nó sang
    # toạ độ MÀN HÌNH trước — đưa thẳng số sân khấu vào `neo_man` là viên thuốc
    # leo lên đè đáy ảnh, đúng lỗi vừa mắc.
    if day_san is None:
        ly = LOI_Y
    elif cam is None:
        ly = day_san + LOI_HO
    else:
        ly = v.man_hinh(0, day_san, cam)[1] + LOI_HO
    ly = min(ly, RAY_Y - 76)
    px, py = (x, ly) if cam is None else v.neo_man(x, ly, cam)
    khoi(f'{id}-n', px, py, w / s, 54 / s, 'rgba(7,19,13,.92)', r=27 / s, at=at,
         vao='rise', dai=.4, song=song)
    chu(f'{id}-c', px, py + 16 / s, text, size=19 / s, w=w / s, align='center',
        at=at + .04, mau='#ffffff', vao='fade',
        song=None if song is None else song - .04, chua=f'{id}-n')


def vong(id, hop, at, *, song=None, mau=CAM, day=3):
    """Vòng cam khoanh một vùng trên ảnh màn hình — đúng thứ đội dùng để chỉ chỗ.
    `hop` là (x, y, rộng, cao) đã quy đổi sang sân khấu."""
    x, y, w, h = hop
    for i, (bx, by, bw, bh) in enumerate([
            (x - day, y - day, w + day * 2, day), (x - day, y + h, w + day * 2, day),
            (x - day, y, day, h), (x + w, y, day, h)]):
        khoi(f'{id}-{i}', bx, by, bw, bh, mau, r=day / 2, at=at, vao='fade',
             dai=.3, song=song)


def the_tep(id, x, y, at, *, vao='rise', song=None, ra=None):
    """Thẻ tệp `ttindex.html` — thứ được kéo thả. Vẽ đè lên màn hình thật."""
    w, h = 210, 58
    them = {'out': ra} if ra else {}
    the(id, x, y, w, h, at, vao=vao, r=11, song=song, vien='rgba(0,0,0,.10)')
    khoi(f'{id}-o', x + 12, y + 12, 34, 34, CAM_MO, r=9, at=at + .03, vao='fade',
         song=song, chua=id, **them)
    chu(f'{id}-ic', x + 12, y + 21, '< >', size=13, w=34, align='center',
        at=at + .05, mau=CAM, vao='fade', song=song, chua=f'{id}-o', **them)
    chu(f'{id}-t', x + 56, y + 12, 'ttindex.html', size=14, at=at + .05,
        vao='fade', song=song, chua=id, **them)
    chu(f'{id}-p', x + 56, y + 33, 'HTML · 68 KB', size=10.5, w=130, at=at + .07,
        mau=MO, vao='fade', song=song, chua=id, **them)


def the_ssl(cx, cy, rong, at, song):
    k = rong / 420.0
    cao = 292 * k
    x, y = cx - rong / 2, cy - cao / 2
    khoi('ssl-bong', x - 4 * k, y - 4 * k, rong + 8 * k, cao + 8 * k, 'rgba(0,0,0,.35)',
         r=26 * k, at=at, vao='pop', dai=.5, song=song)
    khoi('ssl', x, y, rong, cao, GIAY, r=22 * k, at=at, vao='pop', dai=.5, song=song)
    khoi('ssl-vong', cx - 52 * k, y + 38 * k, 104 * k, 104 * k, LUC_MO, r=52 * k,
         at=at + .08, vao='pop', dai=.5, song=song - .08, chua='ssl')
    khoi('ssl-tron', cx - 38 * k, y + 52 * k, 76 * k, 76 * k, LUC, r=38 * k,
         at=at + .14, vao='pop', dai=.45, song=song - .14, chua='ssl')
    dau_tick('ssl-dau', cx, y + 90 * k, 32 * k, '#ffffff', at + .3, chua='ssl',
             day=7 * k, song=song - .3)
    chu('ssl-td', x, y + 164 * k, 'Đã cấp chứng chỉ SSL', size=21 * k, w=rong,
        align='center', at=at + .34, song=song - .34, chua='ssl')
    chu('ssl-phu', x, y + 200 * k, 'Website đã được cấp SSL miễn phí', size=11 * k,
        w=rong, align='center', at=at + .4, mau=MO, song=song - .4, chua='ssl')
    khoi('ssl-nhan', cx - 64 * k, y + 230 * k, 128 * k, 26 * k, LUC_MO, r=13 * k,
         at=at + .46, vao='pop', song=song - .46, chua='ssl')
    chu('ssl-nhan-c', cx - 64 * k, y + 236 * k, 'HTTPS đang bật', size=11 * k,
        w=128 * k, align='center', at=at + .5, mau=LUC, song=song - .5, chua='ssl')


def cua_so_trang(cx, cy, rong, at):
    """Cửa sổ trình duyệt hiện ẢNH CHỤP THẬT của `ttindex.html`."""
    k = rong / 760.0
    cao, thanh = 430 * k, 38 * k
    x, y = cx - rong / 2, cy - cao / 2
    khoi('br-bong', x - 5 * k, y - 5 * k, rong + 10 * k, cao + 10 * k, 'rgba(0,0,0,.4)',
         r=15 * k, at=at, vao='pop', dai=.55)
    khoi('br', x, y, rong, cao, '#0b0f24', r=10 * k, at=at, vao='pop', dai=.55)
    v.anh('tr', x, y + thanh, rong, cao - thanh - 1,
          'public/image/ttindex-xem-truoc.png', radius=0, chua='br', at=at + .28)
    khoi('br-thanh', x, y, rong, thanh, '#171c34', r=10 * k, at=at + .04,
         vao='fade', chua='br')
    for i, mau in enumerate(['#ff5f57', '#febc2e', '#28c840']):
        khoi(f'br-cham{i}', x + (18 + i * 18) * k, y + 14 * k, 10 * k, 10 * k, mau,
             r=5 * k, at=at + .08 + i * .03, vao='pop', dai=.3, chua='br-thanh')
    khoi('br-url', x + 84 * k, y + 9 * k, 320 * k, 20 * k, '#242a45', r=10 * k,
         at=at + .14, vao='fade', chua='br-thanh')
    khoi('br-khoa', x + 94 * k, y + 14 * k, 8 * k, 10 * k, LUC, r=2 * k,
         at=at + .17, vao='pop', dai=.3, chua='br-url')
    chu('br-diachi', x + 108 * k, y + 13 * k, 'airtex-trungthu.vibehost.vn',
        size=10 * k, w=286 * k, at=at + .18, mau='#c9d2ea', chua='br-url')


# ══════════════════════════════════════════════════════════════════════════
# SÁU CẢNH, MỖI CẢNH MỘT CÚ MÁY
# ══════════════════════════════════════════════════════════════════════════

# ── C1: màn chọn nguồn thật ───────────────────────────────────────────────
mo_canh('c1-chon-nguon', 2.6)
R1 = khung('nguon', 0)
tieu_de()
loi_thoai('l1', 'Vibe Host nhận năm kiểu nguồn', .9, day_san=R1.day)

# ── C2: ĐẨY VÀO thẻ "Tải file" — kéo thả ──────────────────────────────────
cam2 = v.cam_ngam(W / 2, MAN_CY, 1.55)
mo_canh('c2-keo-tha', 3.8, camera=cam2, camera_muot=.9)
R2 = khung('taifile', 0, dong=True, cam=cam2)
T_CHON = 2.3
mx, my, mw, mh = R2(0, 0, *CAT['taifile'][1:3])
the_tep('tep-a', mx + mw - 210, my - 132, .5, song=1.4,
        ra={'kind': 'fade', 'dur': .2})
vong('vong0', (mx + 6, my + 6, mw - 12, mh - 12), T_CHON)
khoi('chon-nen', mx + 6, my + 6, mw - 12, mh - 12, 'rgba(255,103,26,.12)', r=8,
     at=T_CHON, vao='fade', dai=.3)
khoi('chon-dau', mx + mw - 44, my + 14, 26, 26, CAM, r=13, at=T_CHON + .12,
     vao='pop', dai=.35)
dau_tick('chon-tick', mx + mw - 31, my + 27, 9, '#ffffff', T_CHON + .18, day=3)
loi_thoai('l2', 'Kéo thẳng file .html vào ô này', .35, cam=cam2, song=1.65,
          day_san=R2.day)
loi_thoai('l2b', 'Xong — không cấu hình gì', T_CHON + .3, cam=cam2,
          day_san=R2.day)

tro_a = v.man_hinh(mx + mw - 105, my - 103, cam2)
tro_b = v.man_hinh(mx + mw / 2, my + mh / 2, cam2)
v.els.append({
    'id': 'tro', 'kind': 'pointer', 'x': 0, 'y': 0,
    'path': [{'t': .6, 'x': round(tro_a[0] + 180), 'y': round(tro_a[1] - 240)},
             {'t': 1.2, 'x': round(tro_a[0]), 'y': round(tro_a[1])},
             {'t': 1.45, 'x': round(tro_a[0]), 'y': round(tro_a[1])},
             {'t': 2.25, 'x': round(tro_b[0]), 'y': round(tro_b[1])},
             {'t': 3.6, 'x': round(tro_b[0]), 'y': round(tro_b[1])}],
    'clicks': [{'t': 1.28, 'x': round(tro_a[0]), 'y': round(tro_a[1])},
               {'t': 2.32, 'x': round(tro_b[0]), 'y': round(tro_b[1])}],
})

# ── C3: khối đang triển khai, đẩy nhẹ vào ─────────────────────────────────
cam3 = v.cam_ngam(W / 2, MAN_CY, 1.25)
mo_canh('c3-dang-chay', 2.8, camera=cam3, camera_muot=.8)
R3 = khung('chay', 2, dong=True, cam=cam3)
vong('vong3', R3(18, 152, 250, 34), 1.0, mau=CAM, day=2)
loi_thoai('l3', 'Hệ thống tự làm từng bước', .4, cam=cam3, song=2.2,
          day_san=R3.day)

# ── C4: LÙI RA — thẻ SSL bật ra giữa khung ────────────────────────────────
mo_canh('c4-ssl', 2.2, camera_muot=.75)
R4 = khung('chay', 2, dong=True)
the_ssl(W / 2, MAN_CY, 600, .3, 1.6)
loi_thoai('l4', 'SSL cấp tự động, miễn phí', .55, day_san=R4.day)

# ── C5: khối đã khởi chạy ─────────────────────────────────────────────────
cam5 = v.cam_ngam(W / 2, MAN_CY, 1.15)
mo_canh('c5-xong', 2.2, camera=cam5, camera_muot=.8)
R5 = khung('xong', 2, dong=True, cam=cam5)
vong('vong5', R5(16, 224, 130, 42), .6, mau=LUC, day=2)
loi_thoai('l5', 'Ứng dụng đã khởi chạy', .35, cam=cam5, day_san=R5.day)

# ── C6: LÙI RA — trang bật ra giữa khung ──────────────────────────────────
mo_canh('c6-bat-ra', 2.6, camera_muot=.8)
R6 = khung('xong', 2, dong=True)
cua_so_trang(W / 2, MAN_CY, 660, .35)
loi_thoai('l6', 'airtex-trungthu.vibehost.vn đã chạy', 1.0, day_san=R6.day)

v.chot(OUT, KIEM, {
    'name': 'Kéo thả HTML → Vibe Hosting (dọc 9:16)',
    'density': 1, 'bg': NEN, 'accent': CAM, 'accent2': CAM_2,
    'hot': CAM, 'hot2': '#e3272c', 'ink': CHU,
    'inkSoft': CHU_MO, 'inkFaint': '#5f7f6e',
})
