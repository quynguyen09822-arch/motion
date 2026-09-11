#!/usr/bin/env node
/**
 * KIỂM ẢNH NHỎ CỦA THÀNH PHẦN (bảng lớp kiểu Photoshop).
 *
 * Ảnh nhỏ dựng bằng cách nhân bản nút DOM từ trong iframe ra shadow root ở
 * trang cha. Hai lỗi đã vấp lúc dựng, và cả hai đều hỏng LẶNG LẼ — ra một ô
 * trông vẫn "có gì đó" nên rất dễ tưởng là xong:
 *
 *   1. Đường dẫn ảnh tương đối. Trong iframe gốc là `/clip/`, ở trang cha gốc
 *      là `/` — chép nguyên `src="public/a.png"` là ảnh vỡ hết.
 *   2. Đo ô khi ô còn `display:none`. Mọi phép đo ra 0, hệ số thu bị chặn ở
 *      mức tối đa, và món phóng to gấp bốn thay vì thu vừa ô.
 *
 *   node tools/kiem-anh-nho.mjs [http://127.0.0.1:7803]
 */
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const PROJ = process.env.PROJ_ROOT
  || '/home/coder/workspace/projects/clipVibehost/hosting-animatic-production';
const { chromium } = createRequire(path.join(PROJ, 'tools/'))('playwright');

const GOC = process.argv[2] || 'http://127.0.0.1:7803';
const M = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

let hong = 0;
const dat = (ten, ok, them = '') => {
  console.log(`${ok ? '  ✓' : '  ✗'} ${ten}${them ? ` — ${them}` : ''}`);
  if (!ok) hong++;
};

const trinh = await chromium.launch();
const trang = await trinh.newPage({ viewport: { width: 1700, height: 1000 } });
const loiJS = [];
trang.on('pageerror', (e) => loiJS.push(String(e)));

try {
  await trang.goto(GOC, { waitUntil: 'domcontentloaded' });
  await trang.waitForSelector('#app[data-trang-thai="san-sang"], #app[data-trang-thai="hong"]',
    { timeout: 40000 });
  await trang.selectOption('#chon-clip', 'cta');
  await trang.waitForSelector('#app[data-trang-thai="san-sang"]', { timeout: 30000 });
  await trang.waitForTimeout(1500);

  /* ---------- 1. có ảnh, và ảnh đúng loại món ---------- */
  console.log('\n1. Mỗi hàng có một ô ảnh dựng được');
  const o = await trang.evaluate(() => [...document.querySelectorAll('.lop-anh')].map((x) => ({
    mon: x.dataset.mon,
    loai: x.dataset.loai,
    trongO: x.shadowRoot?.querySelector('.el')?.className || null,
  })));
  dat('danh sách có ô ảnh', o.length > 3, `${o.length} ô`);
  dat('mọi ô đều dựng được nội dung', o.every((x) => x.trongO),
    `${o.filter((x) => x.trongO).length}/${o.length}`);
  dat('ô dựng ĐÚNG loại món của hàng đó',
    o.every((x) => !x.trongO || x.trongO.includes(`k-${x.loai}`)),
    o.find((x) => x.trongO && !x.trongO.includes(`k-${x.loai}`))?.mon || 'khớp hết');

  /* ---------- 2. ảnh trong ô phải tải được ---------- */
  console.log('\n2. Đường dẫn ảnh được đổi sang tuyệt đối');
  const anh = await trang.evaluate(async () => {
    const ra = [];
    for (const x of document.querySelectorAll('.lop-anh')) {
      for (const i of x.shadowRoot?.querySelectorAll('img') || []) {
        ra.push({ src: i.getAttribute('src'), rong: i.naturalWidth });
      }
    }
    return ra;
  });
  dat('có ảnh trong ô để kiểm', anh.length > 0, `${anh.length} ảnh`);
  dat('mọi src đều là đường dẫn tuyệt đối',
    anh.every((a) => /^https?:/.test(a.src || '')), anh.find((a) => !/^https?:/.test(a.src || ''))?.src || 'đúng hết');
  dat('mọi ảnh đều tải được (không vỡ)', anh.every((a) => a.rong > 0),
    `${anh.filter((a) => a.rong > 0).length}/${anh.length} tải được`);

  /* ---------- 3. ô xem lớn khi rê chuột ---------- */
  console.log('\n3. Ô xem lớn khi rê chuột');
  const hang = trang.locator('.lop-hang', { hasText: 'Quỹ đạo' }).first();
  await hang.hover();
  await trang.waitForTimeout(600);
  const lon = await trang.evaluate(() => {
    const x = document.querySelector('.lop-xem-lon');
    const e = x.shadowRoot?.querySelector('.el');
    const m = /scale\(([\d.]+)\)/.exec(e?.style.transform || '');
    return { hien: !x.classList.contains('an'), loai: e?.className || null,
      tiLe: m ? Number(m[1]) : null, rongMon: e?.offsetWidth || 0, oRong: x.offsetWidth };
  });
  dat('ô lớn hiện ra', lon.hien);
  dat('ô lớn dựng đúng món đang rê', /k-quydao/.test(lon.loai || ''), lon.loai);
  /*
   * Chốt chặn cho lỗi "đo khi còn ẩn": món rộng 662px thả vào ô 168px thì hệ số
   * phải NHỎ HƠN 1. Nếu ai đó lại vẽ trước khi hiện ô, hệ số sẽ vọt lên mức
   * tối đa và mục này bắt được ngay.
   */
  dat('món to hơn ô thì phải THU NHỎ, không phóng to',
    lon.rongMon > lon.oRong ? lon.tiLe < 1 : true,
    `món rộng ${lon.rongMon}px · ô ${lon.oRong}px · tỉ lệ ${lon.tiLe}`);
  dat('món vừa khít trong ô', lon.tiLe * lon.rongMon <= lon.oRong + 1,
    `${(lon.tiLe * lon.rongMon).toFixed(0)}px ≤ ${lon.oRong}px`);

  await trang.evaluate(() => document.querySelector('.lop-hang')?.dispatchEvent(
    new MouseEvent('mouseleave', { bubbles: true })));
  await trang.mouse.move(900, 500);
  await trang.waitForTimeout(400);

  /* ---------- 4. cảnh nặng thì dựng LƯỜI ---------- */
  console.log('\n4. Cảnh nhiều món thì chỉ dựng ô đang nhìn thấy');
  await trang.selectOption('#chon-clip', 'thu-trien-khai-html');
  await trang.waitForSelector('#app[data-trang-thai="san-sang"]', { timeout: 40000 });
  await trang.waitForTimeout(1800);
  const nang = await trang.evaluate(() => {
    const x = [...document.querySelectorAll('.lop-anh')];
    return { tong: x.length, daVe: x.filter((y) => y.dataset.veRoi).length };
  });
  dat('cảnh này thật sự nhiều món', nang.tong > 100, `${nang.tong} món`);
  dat('KHÔNG dựng hết một lượt', nang.daVe < nang.tong / 2,
    `mới dựng ${nang.daVe}/${nang.tong}`);

  console.log('\n5. Lỗi trên trang');
  dat('không có lỗi JS', loiJS.length === 0, loiJS.slice(0, 2).join(' | ') || 'sạch');
  await trang.screenshot({ path: path.join(M, '.kiem', 'anh-nho.png'), scale: 'css' });
} finally {
  await trinh.close();
}

console.log(hong === 0 ? '\n✅ Ảnh nhỏ thành phần: qua.\n' : `\n❌ ${hong} mục không đạt.\n`);
process.exit(hong === 0 ? 0 : 1);
