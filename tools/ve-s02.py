#!/usr/bin/env python3
"""Vẽ lại màn hình S02 "Một đường link" bằng CODE, từ tấm storyboard.

Vì sao viết bộ sinh chứ không gõ tay JSON: màn này ~60 thành phần, toạ độ suy
từ nhau (mỗi tin nhắn cách nhau đúng một bước). Gõ tay thì sửa một con số phải
dò lại chục chỗ; ở đây đổi một biến là cả cột dịch theo.

Sinh ra `scenes/thu-ve-lai-s02.json` — FILE MỚI, không đụng clip nào của đội.
"""
import json, pathlib

W, H = 1280, 720
OUT = pathlib.Path('/home/coder/workspace/projects/clipVibehost/hosting-animatic-production/scenes/thu-ve-lai-s02.json')

# Màu đọc từ chính tấm ảnh
NAV   = '#252b38'   # thanh bên tối
GIAY   = '#ffffff'
VIEN   = '#e6e9ef'
CAM    = '#ed7225'
CAM_MO = '#fdece0'
XAM    = '#8a93a6'
MUC    = '#1e2430'
LUC    = '#1f8a4c'

els = []
def E(id, kind, x, y, **kw):
    els.append({'id': id, 'kind': kind, 'x': round(x), 'y': round(y), **kw})
    return els[-1]

def chu(id, x, y, text, size=13, mau=None, at=0, w=None, **kw):
    d = {'text': text, 'size': size, 'align': 'left'}
    if w: d['w'] = round(w)
    if at: d['at'] = round(at, 2)
    d.update(kw)
    E(id, 'text', x, y, **d)

def khoi(id, x, y, w, h, fill, r=10, at=0, **kw):
    d = {'w': round(w), 'h': round(h), 'fill': fill, 'radius': r}
    if at: d['at'] = round(at, 2)
    d.update(kw)
    E(id, 'panel', x, y, **d)

# ── nền ────────────────────────────────────────────────────────────────────
khoi('nen', 0, 0, W, H, '#f2f4f7', r=0, **{'in': {'kind': 'none', 'dur': 0.001}})

# ── tiêu đề ────────────────────────────────────────────────────────────────
chu('tieu-de', 30, 22, '*S02* · Một đường link', size=30, at=0.0)

# ── hai cửa sổ ─────────────────────────────────────────────────────────────
CX = [24, 654]                 # x của cửa sổ trái / phải
CY, CW, CH = 86, 602, 500      # y, rộng, cao
SW = 152                       # bề rộng thanh bên

NHAN = [('Trang chủ', True), ('Triển khai website', False), ('Triển khai từ mẫu', False),
        ('Tạo database', False), ('Sao lưu', False), ('Kết nối AI Agent', False)]
GOI = [('Dịch vụ', '4/10'), ('CPU', '1.2/4 core'), ('RAM', '0.5/8 GB')]


def cua_so(p, x, t0, nhan_pill, mau_pill, chu_pill, mau_chu_pill):
    """Dựng một cửa sổ. `p` là tiền tố id, `t0` là giây bắt đầu hiện."""
    # nhãn tròn phía trên
    khoi(f'{p}-pill', x + 232, CY - 46, 200, 34, mau_pill, r=17, at=t0)
    chu(f'{p}-pill-chu', x + 232, CY - 38, chu_pill, size=14, at=t0 + .05,
        w=200, align='center', **{'mau': mau_chu_pill} if False else {})

    # khung cửa sổ + thanh bên
    khoi(f'{p}-khung', x, CY, CW, CH, GIAY, r=12, at=t0 + .1)
    khoi(f'{p}-nav', x, CY, SW, CH, NAV, r=12, at=t0 + .12)

    # logo
    khoi(f'{p}-logo-cham', x + 16, CY + 20, 22, 22, CAM, r=11, at=t0 + .2)
    chu(f'{p}-logo', x + 44, CY + 22, 'Vibe Host', size=15, at=t0 + .2)
    chu(f'{p}-kglv', x + 16, CY + 62, 'KHÔNG GIAN LÀM VIỆC', size=9, at=t0 + .25)

    # mục menu
    for i, (ten, dang) in enumerate(NHAN):
        y = CY + 84 + i * 30
        if dang:
            khoi(f'{p}-nav-sang', x + 10, y - 5, SW - 20, 26, '#333b4d', r=7, at=t0 + .3)
        chu(f'{p}-nav-{i}', x + 24, y, ten, size=12, at=t0 + .3 + i * .04)

    # thẻ gói dưới chân
    gy = CY + CH - 116
    khoi(f'{p}-goi', x + 10, gy, SW - 20, 104, '#2f3646', r=9, at=t0 + .5)
    chu(f'{p}-goi-ten', x + 22, gy + 10, 'Gói Vibe Host Pro', size=11, at=t0 + .52)
    for i, (k, v) in enumerate(GOI):
        chu(f'{p}-goi-k{i}', x + 22, gy + 36 + i * 22, k, size=11, at=t0 + .55 + i * .04)
        chu(f'{p}-goi-v{i}', x + SW - 92, gy + 36 + i * 22, v, size=11, w=70,
            align='right', at=t0 + .55 + i * .04)

    # đầu khung chat
    hx = x + SW + 18
    khoi(f'{p}-ava-nhom', hx, CY + 18, 30, 30, '#eef1f6', r=15, at=t0 + .35)
    chu(f'{p}-nhom', hx + 40, CY + 18, 'Nhóm: Vận hành hệ thống', size=15, at=t0 + .35)
    chu(f'{p}-tv', hx + 40, CY + 40, '12 thành viên', size=11, at=t0 + .38)
    khoi(f'{p}-gach', x + SW, CY + 62, CW - SW, 1, VIEN, r=0, at=t0 + .4)

    # ô nhập tin nhắn
    khoi(f'{p}-o-nhap', hx, CY + CH - 52, CW - SW - 36, 38, '#f7f8fb', r=10, at=t0 + .6)
    chu(f'{p}-o-chu', hx + 14, CY + CH - 42, 'Nhập tin nhắn…', size=12, at=t0 + .62)
    khoi(f'{p}-gui', x + CW - 52, CY + CH - 44, 22, 22, CAM, r=11, at=t0 + .65)
    return hx


def tin(p, hx, i, ten, gio, loi, t, quan_tri=False, mau_ava='#f4ded0'):
    """Một tin nhắn: avatar + tên + giờ + bong bóng."""
    y = TIN_Y[i]
    khoi(f'{p}-av{i}', hx, y, 26, 26, mau_ava, r=13, at=t)
    chu(f'{p}-ten{i}', hx + 36, y + 1, ten, size=12, at=t)
    if quan_tri:
        khoi(f'{p}-qt{i}', hx + 36 + 52, y, 66, 17, '#eef1f6', r=8, at=t)
        chu(f'{p}-qtc{i}', hx + 36 + 58, y + 2, 'Quản trị viên', size=9, at=t)
    chu(f'{p}-gio{i}', hx + 36 + (128 if quan_tri else 54), y + 2, gio, size=10, at=t)
    khoi(f'{p}-bong{i}', hx + 36, y + 24, min(len(loi) * 6.6 + 26, 372), 34,
         '#f5f7fa', r=9, at=t + .08)
    chu(f'{p}-loi{i}', hx + 48, y + 32, loi, size=12, at=t + .1,
        w=min(len(loi) * 6.6 + 4, 350))


# ══ CỬA SỔ TRÁI — "Trước đây: Gửi file" ══════════════════════════════════
hxT = cua_so('t', CX[0], 0.15, 'Trước đây', '#e9ecf1', 'Trước đây: Gửi file', XAM)
TIN_Y = [CY + 76, CY + 196, CY + 262, CY + 330]
tin('t', hxT, 0, 'Admin', '09:21', 'Team ơi, gửi file ca trực mới nhất nhé.', 1.4, True)
# thẻ file .xlsx
khoi('t-file', hxT + 36, CY + 138, 380, 46, GIAY, r=9, at=1.9)
khoi('t-file-ic', hxT + 48, CY + 148, 26, 26, LUC, r=6, at=1.95)
chu('t-file-ten', hxT + 84, CY + 146, 'dang-ky-ca-truc-FINAL-v7-sua-lan-cuoi.xlsx', size=11, at=1.95, w=300)
chu('t-file-cap', hxT + 84, CY + 164, 'XLSX · 25.6 KB', size=10, at=1.98, w=200)
tin('t', hxT, 1, 'Minh', '09:25', 'File này bản nào vậy anh?', 2.5, False, '#e2ddf5')
tin('t', hxT, 2, 'Huy', '09:25', 'Em mở bị lỗi, không tải được ạ.', 3.1, False, '#d9e6f7')
tin('t', hxT, 3, 'Admin', '09:28', 'À gửi nhầm bản cũ, để anh gửi lại nhé.', 3.7, True)

# ══ MŨI TÊN ══════════════════════════════════════════════════════════════
chu('mui-ten', 612, CY + 232, '*→*', size=42, at=4.4, w=40, align='center')

# ══ CỬA SỔ PHẢI — "Bây giờ: Gửi link" ════════════════════════════════════
hxP = cua_so('p', CX[1], 4.7, 'Bây giờ', CAM_MO, 'Bây giờ: Gửi link', CAM)
TIN_Y = [CY + 76, CY + 232, CY + 300, CY + 368]
tin('p', hxP, 0, 'Admin', '09:21', 'Team ơi, ca trực đã cập nhật tại đây nhé.', 5.9, True)
# thẻ LINK — nhân vật chính của cảnh
khoi('p-link', hxP + 36, CY + 138, 392, 58, GIAY, r=10, at=6.4)
khoi('p-link-ic', hxP + 48, CY + 152, 30, 30, CAM_MO, r=8, at=6.45)
chu('p-link-url', hxP + 90, CY + 148, '*https://internal.matbao.net/ca-truc*', size=12, at=6.5, w=300)
chu('p-link-phu', hxP + 90, CY + 168, 'Ca trực · Cập nhật 28/08/2026 09:15', size=10, at=6.55, w=300)
# thả tim
khoi('p-rc1', hxP + 36, CY + 204, 46, 22, '#eef1f6', r=11, at=7.0)
chu('p-rc1c', hxP + 46, CY + 208, '👍 2', size=11, at=7.05, w=36)
khoi('p-rc2', hxP + 90, CY + 204, 46, 22, '#fdeaea', r=11, at=7.15)
chu('p-rc2c', hxP + 100, CY + 208, '❤️ 1', size=11, at=7.2, w=36)
tin('p', hxP, 1, 'Minh', '09:23', 'Ok luôn anh, mở nhanh, xem dễ hơn nhiều!', 7.5, False, '#e2ddf5')
tin('p', hxP, 2, 'Huy', '09:24', 'Chuẩn rồi anh, không còn lỗi file nữa ạ.', 8.1, False, '#d9e6f7')
tin('p', hxP, 3, 'Lan', '09:24', 'Cảm ơn anh, tiện quá!', 8.7, False, '#d6efe0')

# ══ CÂU CHỐT ═════════════════════════════════════════════════════════════
chu('chot', 0, 626, 'Một đường link ·  cả phòng nhìn cùng một *bản*',
    size=26, at=9.6, w=W, align='center')
khoi('chot-gach', 540, 668, 200, 4, CAM, r=2, at=10.0)

doc = {
    'version': 1,
    'meta': {'name': 'thu-ve-lai-s02', 'width': W, 'height': H, 'density': 1,
             'bg': '#f2f4f7', 'accent': CAM, 'accent2': '#f4a261',
             'hot': CAM, 'hot2': '#e3272c', 'ink': MUC},
    'scenes': [{'id': 'canh-1', 'duration': 12.5, 'stagger': 0,
                'camera': {'x': 0, 'y': 0, 'scale': 1}, 'elements': els}],
}
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{OUT.name}: {len(els)} thành phần, {doc["scenes"][0]["duration"]}s')
