/**
 * KHỞI ĐỘNG VÀ NỐI DÂY.
 *
 * Bước M0: chọn clip → xem được → tua được. Chưa có đường ghi nào, và đó là cố ý.
 * Phép quy đổi toạ độ và luật bấm chọn là chỗ đẻ bug nhiều nhất; nên tìm ra chúng
 * lúc hậu quả tệ nhất chỉ là một hình chữ nhật vẽ lệch, chứ không phải lúc chúng
 * đã kịp ghi đè lên kịch bản thật.
 */
import { taoPlayer } from './player.js';

const $ = (id) => document.getElementById(id);
const chonClip = $('chon-clip');
const dangClip = $('dang-clip');
const dsCanhEl = $('ds-canh');
const bangDoiCu = $('bang-doi-cu');
const bocKhung = $('boc-khung');
const nutChay = $('nut-chay');
const thanhTua = $('thanh-tua');
const dongHo = $('dong-ho');
const baoEl = $('bao');

const player = taoPlayer($('khung'));

let clips = [];
let clipDangMo = null;
let dangKeoThanh = false;

/* ---------- lời nhắc ---------- */
let hen = null;
function bao(cau, hong = false) {
  baoEl.textContent = cau;
  baoEl.classList.toggle('hong', hong);
  baoEl.classList.remove('an');
  clearTimeout(hen);
  hen = setTimeout(() => baoEl.classList.add('an'), hong ? 8000 : 3200);
}

const giay1 = (n) => n.toFixed(1).replace('.', ',');

/* ---------- danh sách clip ---------- */
async function napDanhSach() {
  const r = await fetch('/api/clips');
  const d = await r.json();
  if (!d.ok) throw new Error(d.loi || 'Không lấy được danh sách clip.');
  clips = d.clips;

  chonClip.innerHTML = '';
  const nhomMoi = document.createElement('optgroup');
  nhomMoi.label = 'Sửa được';
  const nhomCu = document.createElement('optgroup');
  nhomCu.label = 'Clip đời cũ — chỉ xem';

  for (const c of clips) {
    const o = document.createElement('option');
    o.value = c.slug;
    o.textContent = c.hong
      ? `${c.ten} ⚠ hỏng`
      : c.doi === 2
        ? `${c.ten} · ${c.soCanh} cảnh · ${giay1(c.giay)}s`
        : c.ten;
    o.disabled = Boolean(c.hong);
    (c.doi === 2 ? nhomMoi : nhomCu).appendChild(o);
  }
  if (nhomMoi.children.length) chonClip.appendChild(nhomMoi);
  if (nhomCu.children.length) chonClip.appendChild(nhomCu);
}

/* ---------- mở một clip ---------- */
/* Trạng thái mở clip, gắn lên #app. Vừa để CSS bắt được lúc đang tải, vừa để
   máy kiểm chờ đúng lúc xong thay vì ngủ đại một quãng rồi đoán. */
const trangThai = (t) => { document.getElementById('app').dataset.trangThai = t; };

async function moClip(slug) {
  const c = clips.find((x) => x.slug === slug);
  if (!c) return;
  clipDangMo = c;
  trangThai('dang-mo');

  bangDoiCu.classList.toggle('an', c.doi !== 1);
  bocKhung.style.setProperty('--ti-le', c.doi === 2 && c.rong ? `${c.rong} / ${c.cao}` : '16 / 9');
  dangClip.textContent = c.doi === 2 ? `${c.rong}×${c.cao}` : 'đời cũ';
  dsCanhEl.innerHTML = '';

  try {
    await player.mo(c.xem, c.doi);
  } catch (e) {
    bao(e.message, true);
    trangThai('hong');
    return;
  }

  if (c.doi !== 2) {
    // Clip đời cũ: trang tự chạy lấy, ta không lái được. Khoá điều khiển của
    // mình lại thay vì để mấy cái nút nằm đó bấm không ăn — trông như hỏng.
    khoaDieuKhien(true);
    dsCanhEl.innerHTML = '<li class="khong-the">Clip đời cũ không tách được ra từng cảnh.</li>';
    bao(`Đã mở "${c.ten}" — chỉ xem.`);
    trangThai('san-sang');
    return;
  }

  khoaDieuKhien(false);
  // KHÔNG tự chạy. Khung hình đang chạy thì không bấm trúng gì cả — và bấm trúng
  // mới là việc chính của cái trình sửa này.
  const ds = player.dsCanh();
  veDanhSachCanh(ds);
  player.tua(ds.length ? ds[0].giua : 0);
  capNhat();
  bao(`Đã mở "${c.ten}".`);
  trangThai('san-sang');
}

function khoaDieuKhien(khoa) {
  nutChay.disabled = khoa;
  thanhTua.disabled = khoa;
  dongHo.textContent = khoa ? 'trang tự chạy' : '0,0 / 0,0 giây';
  if (khoa) nutChay.textContent = '▶ Chạy';
}

/* Danh sách cảnh. `giua` là lúc cảnh đã vào xong mà chưa bắt đầu ra — bộ dựng
   tính sẵn con số này, nhảy tới đó thì thấy cảnh ở dạng đại diện nhất. */
function veDanhSachCanh(ds) {
  dsCanhEl.innerHTML = '';
  ds.forEach((c, i) => {
    const li = document.createElement('li');
    li.dataset.canh = c.id;
    li.innerHTML = `<span>Cảnh ${i + 1} — ${c.id}</span><span class="giay-canh">${giay1(c.duration)}s</span>`;
    li.onclick = () => player.tua(c.giua);
    dsCanhEl.appendChild(li);
  });
}

/* ---------- đồng bộ thanh tua, đồng hồ, cảnh đang xem ---------- */
function capNhat() {
  if (!player.san()) return;
  const t = player.giay();
  const dai = player.thoiLuong();

  if (!dangKeoThanh) thanhTua.value = String(dai ? Math.round((t / dai) * 1000) : 0);
  dongHo.textContent = `${giay1(t)} / ${giay1(dai)} giây`;
  nutChay.textContent = player.dangChay() ? '❚❚ Dừng' : '▶ Chạy';

  const canh = player.canhHienTai();
  for (const li of dsCanhEl.children) {
    li.setAttribute('aria-current', String(li.dataset.canh === canh?.id));
  }
}
player.khiDoi(capNhat);

/* ---------- điều khiển ---------- */
nutChay.onclick = () => (player.dangChay() ? player.dung() : player.chay());

thanhTua.oninput = () => {
  dangKeoThanh = true;
  player.tua((Number(thanhTua.value) / 1000) * player.thoiLuong());
};
thanhTua.onchange = () => { dangKeoThanh = false; };

chonClip.onchange = () => moClip(chonClip.value);

document.addEventListener('keydown', (e) => {
  if (e.target.matches('input, select, textarea')) return;
  if (e.code === 'Space') { e.preventDefault(); nutChay.click(); }
  if (e.key === 'ArrowLeft') player.tua(player.giay() - (e.shiftKey ? 1 : 0.1));
  if (e.key === 'ArrowRight') player.tua(player.giay() + (e.shiftKey ? 1 : 0.1));
});

/* ---------- chạy ---------- */
try {
  await napDanhSach();
  const dau = clips.find((c) => c.doi === 2 && !c.hong);
  if (dau) {
    chonClip.value = dau.slug;
    await moClip(dau.slug);
  } else {
    bao('Không thấy clip nào sửa được trong thư mục scenes/.', true);
  }
} catch (e) {
  bao(e.message, true);
}
