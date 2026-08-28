/**
 * KHỞI ĐỘNG VÀ NỐI DÂY.
 *
 * Luồng dữ liệu, một chiều, không có ngoại lệ:
 *
 *   kho (kịch bản)  ──sửa──►  apDung()  ──►  player.nap()  ──►  khung xem
 *        ▲                                                          │
 *        └────────── bảng thuộc tính / kéo thả ◄── lớp bắt ◄────────┘
 *
 * Khung xem là CÁI ĐỂ NHÌN, không bao giờ là nguồn sự thật. Ta chỉ đọc hình học
 * từ nó (khung của món, hệ số phóng), ngoài ra không đọc gì.
 */
import { taoPlayer } from './player.js';
import { taoKho, timCanh, timMon } from './store.js';
import { taoDo } from './picker.js';
import { taoLopPhu } from './overlay.js';
import { taoDanhSach } from './layers.js';
import { taoBang, tenMon } from './inspector/index.js';
import { ganKeo } from './drag.js';

const $ = (id) => document.getElementById(id);
const chonClip = $('chon-clip'), dangClip = $('dang-clip'), dsCanhEl = $('ds-canh');
const bangDoiCu = $('bang-doi-cu'), bocKhung = $('boc-khung'), lopBat = $('lop-bat');
const nutChay = $('nut-chay'), thanhTua = $('thanh-tua'), dongHo = $('dong-ho'), baoEl = $('bao');
const nutLui = $('nut-lui'), nutToi = $('nut-toi'), nutLuu = $('nut-luu'), dauBan = $('dau-ban');

const player = taoPlayer($('khung'));
const kho = taoKho();
const doMon = taoDo(player);
const lopPhu = taoLopPhu($('lop-phu'), player);
const bang = taoBang($('bang-thuoc-tinh'), kho, player);
const dsLop = taoDanhSach($('ds-lop'), {
  onChon: (c) => datChon(c),
  onRe: (c) => lopPhu.veRe(c.canhId, c.monId),
  onThoiRe: () => lopPhu.xoaRe(),
});

let clips = [], clipDangMo = null, chon = null, dangKeoThanh = false;

/* ---------- lời nhắc ---------- */
let hen = null;
function bao(cau, hong = false) {
  baoEl.textContent = cau;
  baoEl.classList.toggle('hong', hong);
  baoEl.classList.remove('an');
  clearTimeout(hen);
  hen = setTimeout(() => baoEl.classList.add('an'), hong ? 8000 : 3400);
}
const giay1 = (n) => Number(n).toFixed(1).replace('.', ',');
const trangThai = (t) => { $('app').dataset.trangThai = t; };

/* ---------- áp kịch bản lên khung xem ---------- */
let henVe = null;
function apDung() {
  // Gộp nhiều lần sửa liên tiếp vào một nhịp vẽ: `nap()` là dựng lại cả cảnh,
  // gọi theo từng phím gõ thì giật.
  cancelAnimationFrame(henVe);
  henVe = requestAnimationFrame(() => {
    const doc = kho.doc();
    if (doc) player.nap(doc);   // nap() tự tua lại chỗ cũ — xem player.js
    veLopPhu();
  });
}

/* ---------- vẽ khung chọn ---------- */
function veLopPhu() {
  if (!chon?.monId) { lopPhu.xoa(); lopBat.classList.remove('keo-duoc'); return; }
  const t = timMon(kho.doc(), chon.canhId, chon.monId);
  if (!t) { lopPhu.xoa(); return; }
  const kieu = t.cha ? 'con' : t.el.place ? 'dat' : 'tu';
  lopPhu.veChon(chon.canhId, chon.monId, tenMon(t.el), kieu);
  lopBat.classList.toggle('keo-duoc', kieu === 'tu');
}

/* ---------- chọn ---------- */
function datChon(c) {
  chon = c;
  bang.dat(c);
  dsLop.dat(c);
  const doc = kho.doc();
  if (doc && c?.canhId) dsLop.ve(doc, c.canhId);
  veLopPhu();
  danhDauCanh();

  // Chọn một món chưa hiện ra thì tự tua tới lúc nó hiện — không thì người dùng
  // chọn xong nhìn khung hình trống, tưởng hỏng.
  if (!c?.monId) return;
  const t = timMon(doc, c.canhId, c.monId);
  const canh = player.dsCanh().find((x) => x.id === c.canhId);
  if (!t || !canh) return;
  const at = (t.el.at ?? 0) + (timCanh(doc, c.canhId)?.stagger ?? 0) * 0;
  const hienLuc = canh.start + at + (t.el.in?.dur ?? 0.55) + 0.05;
  const nay = player.giay();
  if (nay < canh.start || nay >= canh.start + canh.duration || nay < hienLuc - 0.02) {
    player.tua(Math.min(hienLuc, canh.start + canh.duration - 0.05));
    bao(`Đã nhảy tới giây ${giay1(player.giay())} để bạn nhìn thấy nó.`);
  }
}

/* ---------- lớp bắt sự kiện ---------- */
lopBat.addEventListener('click', (ev) => {
  if (keo.dangKeo()) return;           // vừa kéo xong thì đừng đổi lựa chọn
  const { x, y } = player.quyDoi(ev.clientX, ev.clientY);
  const c = ev.altKey ? doMon.doNgoaiCung(x, y) : doMon.do(x, y, chon);
  datChon(c || { canhId: player.canhHienTai()?.id });
});

lopBat.addEventListener('mousemove', (ev) => {
  if (keo.dangKeo()) return;
  const { x, y } = player.quyDoi(ev.clientX, ev.clientY);
  const c = doMon.do(x, y, null);
  if (c) lopPhu.veRe(c.canhId, c.monId); else lopPhu.xoaRe();
});
lopBat.addEventListener('mouseleave', () => lopPhu.xoaRe());

const keo = ganKeo({
  lopBat, player, kho,
  layChon: () => chon,
  sauKhiKeo: () => bang.ve(),
  bao,
});

bang.khiChonKhac(datChon);

/* ---------- kho báo có thay đổi ---------- */
kho.khiDoi((viec) => {
  if (viec === 'sua') apDung();
  nutLui.disabled = !kho.nhanLui();
  nutToi.disabled = !kho.nhanToi();
  nutLui.title = kho.nhanLui() ? `Hoàn tác: ${kho.nhanLui()}` : 'Không có gì để hoàn tác';
  nutToi.title = kho.nhanToi() ? `Làm lại: ${kho.nhanToi()}` : 'Không có gì để làm lại';
  dauBan.classList.toggle('an', !kho.ban());
});

/* ---------- danh sách clip ---------- */
async function napDanhSach() {
  const d = await (await fetch('/api/clips')).json();
  if (!d.ok) throw new Error(d.loi || 'Không lấy được danh sách clip.');
  clips = d.clips;
  chonClip.innerHTML = '';
  const moi = document.createElement('optgroup'); moi.label = 'Sửa được';
  const cu = document.createElement('optgroup'); cu.label = 'Clip đời cũ — chỉ xem';
  for (const c of clips) {
    const o = document.createElement('option');
    o.value = c.slug;
    o.textContent = c.hong ? `${c.ten} ⚠ hỏng`
      : c.doi === 2 ? `${c.ten} · ${c.soCanh} cảnh · ${giay1(c.giay)}s` : c.ten;
    o.disabled = Boolean(c.hong);
    (c.doi === 2 ? moi : cu).appendChild(o);
  }
  if (moi.children.length) chonClip.appendChild(moi);
  if (cu.children.length) chonClip.appendChild(cu);
}

/* ---------- mở clip ---------- */
async function moClip(slug) {
  const c = clips.find((x) => x.slug === slug);
  if (!c) return;
  clipDangMo = c;
  trangThai('dang-mo');
  chon = null;
  bangDoiCu.classList.toggle('an', c.doi !== 1);
  bocKhung.style.setProperty('--ti-le', c.doi === 2 && c.rong ? `${c.rong} / ${c.cao}` : '16 / 9');
  dangClip.textContent = c.doi === 2 ? `${c.rong}×${c.cao}` : 'đời cũ';
  dsCanhEl.innerHTML = '';
  $('ds-lop').innerHTML = '';
  $('bang-thuoc-tinh').innerHTML = '';
  lopPhu.xoa();

  try {
    await player.mo(c.xem, c.doi);
  } catch (e) { bao(e.message, true); trangThai('hong'); return; }

  if (c.doi !== 2) {
    khoaDieuKhien(true);
    lopBat.style.display = 'none';
    dsCanhEl.innerHTML = '<li class="khong-the">Clip đời cũ không tách được ra từng cảnh.</li>';
    bao(`Đã mở "${c.ten}" — chỉ xem.`);
    trangThai('san-sang');
    return;
  }

  lopBat.style.display = '';
  khoaDieuKhien(false);

  const kq = await (await fetch(`/api/clip/${slug}`)).json();
  if (!kq.ok) { bao(kq.loi, true); trangThai('hong'); return; }

  // Nháp mới hơn file thật thì HỎI, tuyệt đối không tự áp.
  let doc = kq.doc;
  if (kq.nhap) {
    const luc = new Date(kq.nhap.luc).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    if (confirm(`Có bản đang sửa dở lúc ${luc} chưa lưu.\n\nOK = mở tiếp bản đó\nHuỷ = bỏ, dùng bản đã lưu`)) {
      doc = kq.nhap.doc;
    } else {
      fetch(`/api/draft/${slug}`, { method: 'DELETE' }).catch(() => {});
    }
  }

  kho.nap(slug, doc);
  const ds = player.dsCanh();
  veDanhSachCanh(ds);
  player.tua(ds.length ? ds[0].giua : 0);
  datChon({ canhId: ds[0]?.id });
  bang.dat(null);
  capNhat();
  bao(`Đã mở "${c.ten}". Bấm vào một thành phần trên khung hình để sửa.`);
  trangThai('san-sang');
}

function khoaDieuKhien(khoa) {
  nutChay.disabled = khoa; thanhTua.disabled = khoa;
  nutLuu.disabled = khoa; nutLui.disabled = khoa; nutToi.disabled = khoa;
  dongHo.textContent = khoa ? 'trang tự chạy' : '0,0 / 0,0 giây';
  if (khoa) nutChay.textContent = '▶ Chạy';
}

function veDanhSachCanh(ds) {
  dsCanhEl.innerHTML = '';
  ds.forEach((c, i) => {
    const li = document.createElement('li');
    li.dataset.canh = c.id;
    li.innerHTML = `<span>Cảnh ${i + 1}</span><span class="giay-canh">${giay1(c.duration)}s</span>`;
    li.onclick = () => { player.tua(c.giua); datChon({ canhId: c.id }); };
    dsCanhEl.appendChild(li);
  });
}

function danhDauCanh() {
  const canh = chon?.canhId || player.canhHienTai()?.id;
  for (const li of dsCanhEl.children) {
    if (li.dataset) li.setAttribute('aria-current', String(li.dataset.canh === canh));
  }
}

/* ---------- đồng bộ thanh tua ---------- */
function capNhat() {
  if (!player.san()) return;
  const t = player.giay(), dai = player.thoiLuong();
  if (!dangKeoThanh) thanhTua.value = String(dai ? Math.round((t / dai) * 1000) : 0);
  dongHo.textContent = `${giay1(t)} / ${giay1(dai)} giây`;
  nutChay.textContent = player.dangChay() ? '❚❚ Dừng' : '▶ Chạy';
  veLopPhu();
}
player.khiDoi(capNhat);

/* ---------- lưu ---------- */
async function luu() {
  const kq = await kho.luu();
  if (kq.ok) {
    bao(kq.banCu ? 'Đã lưu. Bản cũ vẫn được cất lại phòng khi cần quay về.' : 'Đã lưu.');
  } else {
    bao(`Chưa lưu được — ${(kq.vanDe || [kq.loi]).join(' · ')}`, true);
  }
}

/* ---------- điều khiển ---------- */
nutChay.onclick = () => (player.dangChay() ? player.dung() : player.chay());
nutLuu.onclick = luu;
nutLui.onclick = () => { const n = kho.hoanTac(); if (n) { bang.ve(); bao(`Đã hoàn tác: ${n}`); } };
nutToi.onclick = () => { const n = kho.lamLai(); if (n) { bang.ve(); bao(`Đã làm lại: ${n}`); } };

thanhTua.oninput = () => { dangKeoThanh = true; player.tua((Number(thanhTua.value) / 1000) * player.thoiLuong()); };
thanhTua.onchange = () => { dangKeoThanh = false; };
chonClip.onchange = () => moClip(chonClip.value);

document.addEventListener('keydown', (e) => {
  const trongO = e.target.matches('input, select, textarea');
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') { e.preventDefault(); return luu(); }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
    e.preventDefault();
    return e.shiftKey ? nutToi.click() : nutLui.click();
  }
  if (trongO) return;
  if (e.code === 'Space') { e.preventDefault(); nutChay.click(); }
  if (e.key === 'ArrowLeft') player.tua(player.giay() - (e.shiftKey ? 1 : 0.1));
  if (e.key === 'ArrowRight') player.tua(player.giay() + (e.shiftKey ? 1 : 0.1));
  if (e.key === 'Escape') datChon({ canhId: chon?.canhId });
});

window.addEventListener('beforeunload', (e) => {
  if (kho.ban()) { e.preventDefault(); e.returnValue = ''; }
});

/* ---------- chạy ---------- */
try {
  await napDanhSach();
  const dau = clips.find((c) => c.doi === 2 && !c.hong);
  if (dau) { chonClip.value = dau.slug; await moClip(dau.slug); }
  else bao('Không thấy clip nào sửa được trong thư mục scenes/.', true);
} catch (e) { bao(e.message, true); }
