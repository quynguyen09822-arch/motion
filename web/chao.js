/**
 * TRANG CHÀO — giới thiệu công cụ, và kho dự án của người đang đăng nhập.
 *
 * Trang này KHÔNG biết gì về kịch bản. Nó chỉ hỏi máy chủ hai câu — "kho của
 * tôi ra sao" và "trong kho có gì" — rồi bày ra. Mọi việc đụng tới nội dung
 * clip đều nằm ở trình sửa. Giữ ranh giới đó thì trang chào không bao giờ là
 * chỗ thứ hai có thể làm hỏng một kịch bản.
 *
 * MỌI ĐƯỜNG ĐI ĐỀU LÀ ĐƯỜNG DẪN THẬT. Thẻ dự án là `<a href="/sua?clip=…">`
 * chứ không phải `<div onclick>`: mở tab mới được, rê chuột thấy đường dẫn,
 * gửi link cho đồng nghiệp được. Ba thứ đó mất sạch nếu dựng bằng ô bấm giả.
 */
import { ganTen } from '/tenfile.js';

const $ = (id) => document.getElementById(id);

const luoi = $('luoi');
const luoiCu = $('luoi-cu');
const oTao = $('o-tao');
const oTen = $('ten');
const oMau = $('mau');
const loiTao = $('loi-tao');

let duAn = [];          // dự án đời mới trong kho của tôi
let khoHinh = [];       // khổ dựng sẵn, máy chủ khai

/* ---------- lời nhắc ---------- */
let hen;
function bao(cau, xau = false) {
  const b = $('bao');
  b.textContent = cau;
  b.classList.toggle('xau', xau);
  b.classList.remove('an');
  clearTimeout(hen);
  hen = setTimeout(() => b.classList.add('an'), xau ? 6000 : 3200);
}

/* ---------- chữ ---------- */
const giay1 = (g) => String(Math.round((g ?? 0) * 10) / 10).replace('.', ',');

/**
 * "3 phút trước", "hôm qua", "12/09".
 *
 * Mốc tuyệt đối từ 7 ngày trở đi: "11 ngày trước" bắt người đọc tự trừ ra ngày
 * nào, mà đó đúng là thứ họ muốn biết khi tìm lại một dự án cũ.
 */
function luc(ms) {
  if (!ms) return '';
  const p = Math.round((Date.now() - ms) / 60000);
  if (p < 1) return 'vừa xong';
  if (p < 60) return `${p} phút trước`;
  const g = Math.round(p / 60);
  if (g < 24) return `${g} giờ trước`;
  const n = Math.round(g / 24);
  if (n === 1) return 'hôm qua';
  if (n < 7) return `${n} ngày trước`;
  const d = new Date(ms);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}`;
}

/* ---------- thanh trên: ai đang đăng nhập ---------- */
async function veTaiKhoan() {
  let d;
  try { d = await (await fetch('/api/toi-la-ai')).json(); } catch { return; }
  const boc = $('o-tai-khoan');

  if (!d.coMatKhau) {
    /* Chưa đặt mật khẩu thì KHÔNG có kho riêng — mọi người dùng chung kho gốc.
       Nói thẳng ở đây, vì trang này vừa hứa "kho riêng của bạn". */
    const c = document.createElement('span');
    c.className = 'chip-canh-bao';
    c.textContent = 'Chưa đặt mật khẩu';
    c.title = 'Ai có đường dẫn cũng vào sửa được, và chưa chia kho theo tài khoản. '
      + 'Chạy `npm run dat-mat-khau` trên máy chủ để đặt.';
    boc.appendChild(c);
    return;
  }

  if (d.email) {
    const e = document.createElement('span');
    e.className = 'chip-ai';
    e.textContent = d.email.split('@')[0];
    e.title = `Đang đăng nhập: ${d.email}`;
    boc.appendChild(e);
  }

  const n = document.createElement('button');
  n.className = 'nut';
  n.type = 'button';
  n.textContent = 'Thoát';
  n.title = d.email ? `Đăng xuất ${d.email}` : 'Đăng xuất';
  n.onclick = async () => {
    await fetch('/api/dang-xuat', { method: 'POST' });
    location.href = '/dang-nhap';
  };
  boc.appendChild(n);
}

/* ---------- kho dự án ---------- */
function veThe(c) {
  const a = document.createElement('a');
  a.className = 'the' + (c.hong ? ' hong' : '');
  a.href = `/sua?clip=${encodeURIComponent(c.slug)}`;

  const ten = document.createElement('div');
  ten.className = 'the-ten';
  ten.textContent = c.ten || c.slug;
  a.appendChild(ten);

  const so = document.createElement('div');
  so.className = 'the-so';
  so.textContent = c.hong ? c.hong
    : c.doi === 2 ? `${c.soCanh} cảnh · ${giay1(c.giay)} giây`
      : 'clip đời cũ — chỉ xem';
  a.appendChild(so);

  const chan = document.createElement('div');
  chan.className = 'the-chan';
  if (c.doi === 2 && c.rong) {
    const k = document.createElement('span');
    k.className = 'hieu-kho';
    k.textContent = c.dung ? `Dọc ${c.rong}×${c.cao}` : `Ngang ${c.rong}×${c.cao}`;
    chan.appendChild(k);
  }
  const t = document.createElement('span');
  t.className = 'the-luc';
  t.textContent = luc(c.suaLuc);
  chan.appendChild(t);
  a.appendChild(chan);

  return a;
}

async function napKho() {
  const [k, ds] = await Promise.all([
    (await fetch('/api/kho')).json(),
    (await fetch('/api/clips')).json(),
  ]);
  if (!ds.ok) throw new Error(ds.loi || 'Không mở được kho dự án.');

  khoHinh = k.khoHinh || [];
  duAn = ds.clips.filter((c) => c.doi === 2);
  const doiCu = ds.clips.filter((c) => c.doi === 1);

  $('dang-nap').classList.add('an');
  $('dem-kho').textContent = duAn.length || '';
  $('ai-kho').textContent = k.laGoc
    ? 'kho gốc — chứa toàn bộ clip sẵn có của dự án'
    : `kho riêng của ${k.email || 'bạn'} — không ai khác nhìn thấy`;

  luoi.innerHTML = '';
  for (const c of duAn) luoi.appendChild(veThe(c));
  $('kho-trong').classList.toggle('an', duAn.length > 0);

  luoiCu.innerHTML = '';
  for (const c of doiCu) luoiCu.appendChild(veThe(c));
  $('boc-doi-cu').classList.toggle('an', doiCu.length === 0);
}

/* ---------- ô tạo dự án ---------- */
function dungPhieu() {
  const h = $('kho-hinh');
  h.innerHTML = '';
  khoHinh.forEach((k, i) => {
    const l = document.createElement('label');
    const r = document.createElement('input');
    r.type = 'radio'; r.name = 'kho'; r.value = k.v; r.checked = i === 0;
    /* Tên đọc lên phải là câu người đọc được, không phải `doc`/`ngang`. Chữ đã
       nằm trong `<label>` bọc ngoài, nhưng trình đọc màn hình thì tuỳ nơi lấy
       `value` làm tên — khai thẳng cho khỏi phải tin vào chuyện đó. */
    r.setAttribute('aria-label', k.nhan);
    l.appendChild(r);
    l.appendChild(document.createTextNode(k.nhan));
    h.appendChild(l);
  });

  oMau.innerHTML = '';
  const trang = document.createElement('option');
  trang.value = ''; trang.textContent = 'Trang trắng — một thẻ chữ ở giữa khung';
  oMau.appendChild(trang);
  for (const c of duAn) {
    if (c.hong) continue;   // không cho chép từ một dự án đang hỏng
    const o = document.createElement('option');
    o.value = c.slug;
    o.textContent = `Chép từ "${c.ten || c.slug}"`;
    oMau.appendChild(o);
  }
}

/* Chép từ dự án có sẵn thì khổ hình đi theo bản gốc — bày núm chọn khổ lúc đó
   là bày một núm chết, bấm vào thì không có gì đổi. */
function dongBoNum() {
  const chepMau = Boolean(oMau.value);
  $('kho-hinh').closest('.khokhung').classList.toggle('an', chepMau);
  $('xem-slug').textContent = ganTen(oTen.value) || '(sẽ tự đặt)';
}

function loi(cau, goiY = '') {
  loiTao.textContent = cau;
  loiTao.classList.remove('an');
  if (goiY) {
    /* Không tự đổi tên hộ. Hiện đúng tên còn trống và để người dùng bấm: họ có
       thể muốn một tên khác hẳn, và im lặng đổi tên là cách nhanh nhất làm
       người ta mất dấu dự án của chính mình. */
    const n = document.createElement('button');
    n.className = 'nut'; n.type = 'button';
    n.textContent = `Dùng "${goiY}"`;
    n.onclick = () => { taoThat(goiY); };
    loiTao.appendChild(n);
  }
}

async function taoThat(slugEp = '') {
  const ten = oTen.value.trim();
  if (!ten) { oTen.focus(); return loi('Chưa đặt tên cho dự án.'); }

  loiTao.classList.add('an');
  loiTao.textContent = '';
  $('lam').disabled = true;
  try {
    const than = {
      ten,
      slug: slugEp || ganTen(ten),
      kho: $('kho-hinh').querySelector('input:checked')?.value,
      mau: oMau.value || undefined,
    };
    const r = await fetch('/api/du-an', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(than),
    });
    const d = await r.json();
    if (!d.ok) return loi(d.loi || 'Không tạo được dự án.', d.goiY || '');
    /* Tạo xong đi thẳng vào trình sửa. Quay về danh sách rồi bắt bấm thêm một
       lần nữa là thêm một bước cho việc mà người ta vừa nói rõ là muốn làm. */
    location.href = `/sua?clip=${encodeURIComponent(d.slug)}`;
  } catch (e) {
    loi(`Không gọi được máy chủ — ${String(e.message || e).slice(0, 70)}`);
  } finally {
    $('lam').disabled = false;
  }
}

function moPhieu() {
  dungPhieu();
  oTen.value = '';
  loiTao.classList.add('an');
  loiTao.textContent = '';
  dongBoNum();
  oTao.showModal();
  oTen.focus();
}

/* ---------- nối dây ---------- */
$('nut-tao').onclick = moPhieu;
$('tao-dau').onclick = moPhieu;
$('thoi').onclick = () => oTao.close();
oTen.oninput = dongBoNum;
oMau.onchange = dongBoNum;
$('phieu').onsubmit = (ev) => { ev.preventDefault(); taoThat(); };

$('nut-kho').onclick = () => {
  $('kho').scrollIntoView({ behavior: 'smooth', block: 'start' });
};

/* ---------- chạy ---------- */
veTaiKhoan();
try {
  await napKho();
} catch (e) {
  $('dang-nap').textContent = e.message;
  bao(e.message, true);
}
