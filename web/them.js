/**
 * THÊM · XOÁ · NHÂN BẢN — thành phần và cảnh.
 *
 * Mọi món mới sinh ra ở đây đều phải qua được `validateScene`, nên bắt buộc có:
 * `id` không trùng trong cảnh, `kind`, và `x`/`y` là SỐ (kể cả khi nằm trong cụm
 * và hai số đó vô nghĩa — bộ soát vẫn đòi). Thiếu một cái là kịch bản không lưu
 * được, mà lỗi thì hiện ra tận lúc bấm Lưu, rất khó lần.
 */
import { duyetMon, timCanh, timMon } from './store.js';

/** Món mới, kèm giá trị mặc định đủ đẹp để thả vào là thấy được ngay. */
/**
 * KHO THÀNH PHẦN — chia theo BỘ, giống kho hiệu ứng của mấy app dựng phim.
 *
 * Trước đây đây là một danh sách phẳng 13 món, trong khi bộ dựng vẽ được **25
 * loại**. Mười hai loại còn lại có thật, chạy được, mà không có đường nào thêm
 * vào — muốn dùng phải sửa tay file JSON. Đúng kiểu "năng lực bị giấu" mà
 * `tools/kiem-schema.mjs` sinh ra để chặn, chỉ khác là lần này nằm ở menu thêm
 * chứ không nằm ở bảng thuộc tính.
 *
 * `mau` phải ĐỦ ĐẸP ĐỂ THẢ VÀO LÀ THẤY NGAY. Một món mới ra khung hình trống
 * trơn thì người dùng tưởng bấm hỏng. Số mặc định dưới đây lấy từ chính các
 * clip thật đang chạy, không phải bịa.
 *
 * Mọi món mới đều phải qua `validateScene`, nên bắt buộc có `id`, `kind`, và
 * `x`/`y` là SỐ — kể cả khi nằm trong cụm và hai số đó vô nghĩa.
 */
export const BO_MON = [
  { id: 'chu',    ten: 'Chữ & nhãn',        mo: 'tiêu đề, nút bấm, nhãn số' },
  { id: 'khoi',   ten: 'Khối & bố cục',     mo: 'nền, thẻ, bảng, cụm' },
  { id: 'hinh',   ten: 'Hình & phim',       mo: 'ảnh, video, khung máy' },
  { id: 'sanpham',ten: 'Giao diện sản phẩm',mo: 'dựng lại màn hình app' },
  { id: 'trangtri',ten:'Trang trí',         mo: 'nền thương hiệu, hiệu ứng' },
];

export const MAU_MON = [
  /* ---------- chữ & nhãn ---------- */
  { kind: 'text',     bo: 'chu',  ten: 'Chữ',          mo: 'dòng chữ, có thể tô màu nhấn',
    mau: { text: 'Dòng chữ mới', size: 48, align: 'center' } },
  { kind: 'nut',      bo: 'chu',  ten: 'Nút bấm',      mo: 'nút kêu gọi hành động',
    mau: { label: 'Bấm vào đây', size: 32 } },
  { kind: 'chip',     bo: 'chu',  ten: 'Nhãn số',      mo: 'một con số kèm nhãn',
    mau: { value: '99%', label: 'Nhãn' } },
  { kind: 'hangnhan', bo: 'chu',  ten: 'Hàng nhãn',    mo: 'vài nhãn ngắn xếp hàng',
    mau: { items: ['Ngắn gọn', 'Dễ nhớ', 'Nổi bật'] } },
  { kind: 'huyhieu',  bo: 'chu',  ten: 'Huy hiệu',     mo: 'biểu tượng tròn nổi bật',
    mau: { mark: 'cup', w: 96, h: 96 } },
  { kind: 'logo',     bo: 'chu',  ten: 'Logo',         mo: 'dấu hiệu + tên thương hiệu',
    mau: { name: 'Tên thương hiệu', mark: '◆', w: 260, size: 46 } },

  /* ---------- khối & bố cục ---------- */
  { kind: 'panel',    bo: 'khoi', ten: 'Khối màu',     mo: 'hình chữ nhật, hay dùng làm nền',
    mau: { w: 400, h: 220, radius: 16 } },
  { kind: 'card',     bo: 'khoi', ten: 'Thẻ',          mo: 'thẻ có tiêu đề và mấy dòng',
    mau: { title: 'Tiêu đề thẻ', rows: 3, w: 420 } },
  { kind: 'table',    bo: 'khoi', ten: 'Bảng',         mo: 'bảng danh sách',
    mau: { columns: ['Cột 1', 'Cột 2'], rows: 4, w: 520 } },
  { kind: 'group',    bo: 'khoi', ten: 'Cụm',          mo: 'gom nhiều món, xếp tự động',
    mau: { dir: 'doc', align: 'giua', justify: 'giua', gap: 4, children: [] } },
  { kind: 'timeline', bo: 'khoi', ten: 'Dòng thời gian', mo: 'các mốc rải đều trên một đường',
    mau: { labels: ['0s', '15s', '30s', '45s'], w: 1040, pad: 2 } },

  /* ---------- hình & phim ---------- */
  { kind: 'image',    bo: 'hinh', ten: 'Ảnh',          mo: 'một tấm ảnh',
    mau: { src: '', fit: 'contain', h: 120 } },
  /* Mặc định là NỀN ĐỘNG: kín khung, mờ sẵn, tối sẵn, lặp — thả vào là dùng
     được ngay cho việc hay làm nhất, khỏi phải vặn năm núm mới ra hình. */
  { kind: 'video',    bo: 'hinh', ten: 'Video',        mo: 'phim nền, mờ và tối sẵn',
    mau: { src: '', fit: 'cover', blur: 8, dim: 0.25, loop: true, place: 'day' } },
  { kind: 'phone',    bo: 'hinh', ten: 'Điện thoại',   mo: 'khung máy, thả ảnh/phim vào màn',
    mau: { src: '', w: 260, h: 540 } },
  { kind: 'browser',  bo: 'hinh', ten: 'Trình duyệt',  mo: 'cửa sổ web, thả ảnh/phim vào thân',
    mau: { url: 'ten-cua-ban.tinhgon.xyz', w: 560, h: 340 } },

  /* ---------- giao diện sản phẩm ---------- */
  { kind: 'form',     bo: 'sanpham', ten: 'Biểu mẫu',  mo: 'các ô nhập có nhãn và giá trị',
    mau: { title: 'Tạo mới', w: 380,
      fields: [{ label: 'Tên', value: 'du-an-moi' }, { label: 'Nguồn', value: 'Git URL' }] } },
  { kind: 'calendar', bo: 'sanpham', ten: 'Lịch',      mo: 'tháng có một ngày được đánh dấu',
    mau: { month: 'Tháng 12', cta: 'Chọn ngày', days: 28, highlight: 9, w: 380 } },
  { kind: 'upload',   bo: 'sanpham', ten: 'Ô kéo thả', mo: 'vùng kéo file vào',
    mau: { label: 'Kéo file vào đây', file: 'ten-file.zip', w: 446, h: 294 } },
  { kind: 'chat',     bo: 'sanpham', ten: 'Cửa sổ AI', mo: 'khung trò chuyện với trợ lý',
    mau: { title: 'Trợ lý AI', lines: ['Xin chào! Bạn muốn dựng gì?'],
      typing: 'Làm giúp tôi một trang bán hàng…', w: 446, h: 384 } },

  /* ---------- trang trí ---------- */
  { kind: 'nen',      bo: 'trangtri', ten: 'Nền thương hiệu', mo: 'bộ đồ nền phủ cả khung',
    mau: { place: 'day', parts: ['cham', 'net', 'khoi', 'song', 'duong'], draw: 1.3, waveLow: true } },
  { kind: 'quydao',   bo: 'trangtri', ten: 'Quỹ đạo',  mo: 'vòng tròn xoay quanh một tâm',
    mau: { core: 'tim', label: 'ten-mien.vn', warm: true, w: 662, h: 530 } },
  { kind: 'wheel',    bo: 'trangtri', ten: 'Vòng quay', mo: 'vòng quay may mắn',
    mau: { slices: 10, label: 'QUAY\nNGAY', spin: 18, w: 374, h: 374 } },
  { kind: 'shield',   bo: 'trangtri', ten: 'Khiên bảo mật', mo: 'khiên + mấy nhãn chứng nhận',
    mau: { mark: '🔒', badges: ['Chuẩn ngân hàng', 'Dữ liệu tại Việt Nam', 'SSL'], w: 563 } },
  { kind: 'sweep',    bo: 'trangtri', ten: 'Vệt sáng', mo: 'vệt sáng quét qua khung',
    mau: { w: 1280, h: 720, for: 0.5 } },
];


/** Sinh id chưa trùng trong cảnh. */
function idMoi(canh, goc) {
  const dungRoi = new Set(duyetMon(canh.elements).map((x) => x.el.id));
  let i = 1;
  let t = `${goc}-${i}`;
  while (dungRoi.has(t)) t = `${goc}-${++i}`;
  return t;
}

/** Thêm một món vào cảnh, hoặc vào trong một cụm. Trả về id món mới. */
export function themMon(doc, canhId, kind, chaId = null) {
  const canh = timCanh(doc, canhId);
  if (!canh) return null;
  const mau = MAU_MON.find((m) => m.kind === kind);
  const el = { id: idMoi(canh, kind), kind, x: 0, y: 0, ...structuredClone(mau?.mau || {}) };

  // Món ngoài cùng thì cho vào giữa khung cho dễ thấy; món trong cụm thì để
  // flex lo, đặt `place` vào là thừa.
  // Mẫu nào tự khai `place` rồi thì tôn trọng — video mặc định phủ KÍN KHUNG vì
  // việc hay làm nhất với nó là làm nền động.
  if (!chaId && !el.place) el.place = 'giua';

  const cha = chaId ? timMon(doc, canhId, chaId)?.el : null;
  if (cha && cha.kind === 'group') (cha.children ||= []).push(el);
  else canh.elements.push(el);
  return el.id;
}

export function xoaMon(doc, canhId, monId) {
  const canh = timCanh(doc, canhId);
  if (!canh) return false;
  const boc = (ds) => {
    const i = (ds || []).findIndex((e) => e.id === monId);
    if (i >= 0) { ds.splice(i, 1); return true; }
    return (ds || []).some((e) => e.kind === 'group' && boc(e.children));
  };
  return boc(canh.elements);
}

/** Nhân bản một món. Con trong cụm cũng phải được đặt id mới, không thì trùng. */
export function nhanBanMon(doc, canhId, monId) {
  const canh = timCanh(doc, canhId);
  const t = timMon(doc, canhId, monId);
  if (!canh || !t) return null;

  const banSao = structuredClone(t.el);
  const datLaiId = (e) => {
    e.id = idMoi(canh, e.kind);
    if (e.kind === 'group') (e.children || []).forEach(datLaiId);
  };
  // Đặt id cho món ngoài trước rồi mới tới con, để `idMoi` thấy được cả những
  // id vừa cấp — nếu không hai anh em nhân bản cùng lúc sẽ trùng nhau.
  datLaiId(banSao);

  // Lệch đi một chút cho thấy là có hai cái, không phải một cái.
  if (!banSao.place) { banSao.x = (banSao.x || 0) + 24; banSao.y = (banSao.y || 0) + 24; }

  const ds = t.cha ? t.cha.children : canh.elements;
  ds.splice(ds.indexOf(t.el) + 1, 0, banSao);
  return banSao.id;
}

/* ---------- cảnh ---------- */

function idCanhMoi(doc, goc = 'canh') {
  const co = new Set((doc.scenes || []).map((s) => s.id));
  let i = doc.scenes.length + 1;
  let t = `${goc}-${i}`;
  while (co.has(t)) t = `${goc}-${++i}`;
  return t;
}

export function themCanh(doc, sauCanhId = null) {
  const canh = {
    id: idCanhMoi(doc),
    duration: 4,
    stagger: 0.16,           // giá trị cả bộ đang dùng — giữ cho đồng nhịp
    elements: [{ id: 'chu-1', kind: 'text', x: 0, y: 0, place: 'giua',
      text: 'Cảnh mới', size: 56, align: 'center' }],
  };
  const i = sauCanhId ? doc.scenes.findIndex((s) => s.id === sauCanhId) : -1;
  doc.scenes.splice(i >= 0 ? i + 1 : doc.scenes.length, 0, canh);
  return canh.id;
}

export function nhanBanCanh(doc, canhId) {
  const i = doc.scenes.findIndex((s) => s.id === canhId);
  if (i < 0) return null;
  const ban = structuredClone(doc.scenes[i]);
  ban.id = idCanhMoi(doc);
  doc.scenes.splice(i + 1, 0, ban);
  return ban.id;
}

export function xoaCanh(doc, canhId) {
  // Bộ soát đòi ít nhất một cảnh — xoá cái cuối cùng là kịch bản hỏng.
  if ((doc.scenes || []).length <= 1) return false;
  const i = doc.scenes.findIndex((s) => s.id === canhId);
  if (i < 0) return false;
  doc.scenes.splice(i, 1);
  return true;
}
