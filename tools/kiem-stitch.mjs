#!/usr/bin/env node
/**
 * KIỂM ĐƯỜNG "TẢ BẰNG LỜI → STITCH VẼ GIAO DIỆN → DỰNG THÀNH CẢNH".
 *
 * PHẦN LỚN BÀI NÀY CHẠY KHÔNG CẦN STITCH, và đó là chủ ý.
 *   Một lượt gọi Stitch thật mất khoảng 90 giây và tốn hạn mức. Bài kiểm nào
 *   cũng gọi thật thì `npm run kiem` dài thêm một phút rưỡi mỗi lần chạy, và
 *   đỏ mỗi khi Google bận — mà một bài kiểm đỏ vu vơ thì người ta bắt đầu bỏ
 *   qua mọi màu đỏ.
 *
 *   Nên: mọi CỬA CHẶN kiểm offline; lượt gọi thật chỉ chạy khi được bảo
 *   (`STITCH_THAT=1`), và kể cả lúc đó, Stitch bận thì BỎ QUA chứ không tính
 *   là hỏng.
 *
 * CỬA ĐÁNG CANH NHẤT: soát lời tả phải xảy ra TRƯỚC khi trừ hạn mức.
 *   Phép kiểm ấy từng nằm trong phần chạy nền, nên đường HTTP trả `ok: true`
 *   cho một lời tả hai chữ, hạn mức bị trừ mất một lượt, và người dùng chỉ biết
 *   mình gõ thiếu sau khi hỏi lại. Bắt người ta trả tiền cho cú gõ thiếu của
 *   chính họ là kiểu hỏng không được phép có.
 *
 *   node tools/kiem-stitch.mjs [http://127.0.0.1:7803]
 */
import path from 'node:path';

const GOC = process.env.MOTION_GOC || process.argv[2] || 'http://127.0.0.1:7803';
const M = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const THAT = process.env.STITCH_THAT === '1';

let hong = 0;
const dat = (ten, ok, them = '') => {
  console.log(`${ok ? '  ✓' : '  ✗'} ${ten}${them ? ` — ${them}` : ''}`);
  if (!ok) hong++;
};
const goi = async (duong, than, cach = 'POST') => {
  const r = await fetch(`${GOC}${duong}`, {
    method: cach, headers: { 'Content-Type': 'application/json' },
    body: than ? JSON.stringify(than) : undefined,
  });
  return { ma: r.status, ...(await r.json().catch(() => ({}))) };
};

/* ---------- 1. soát lời tả — hàm thuần ---------- */
console.log('\n1. Soát lời tả (hàm thuần, chạy đồng bộ)');
const { soatLoiTa } = await import(path.join(M, 'server', 'stitch.js'));

dat('lời tả rỗng thì chặn', soatLoiTa('').ok === false);
dat('dưới mười chữ thì chặn', soatLoiTa('hosting').ok === false,
  soatLoiTa('hosting').cau);
dat('dài quá 4000 chữ thì chặn', soatLoiTa('a'.repeat(4001)).ok === false);
dat('lời tả bình thường thì qua',
  soatLoiTa('Man hinh bang gia ba goi hosting, nen trang').ok === true);
/* Khoảng trắng hai đầu không được tính là nội dung — nếu không thì mười dấu
   cách cũng lọt qua cửa, và Stitch nhận một lời tả rỗng. */
dat('mười dấu cách KHÔNG được tính là đủ chữ', soatLoiTa('          ').ok === false);
dat('trả về lời tả đã cắt hai đầu',
  soatLoiTa('   mot man hinh gioi thieu   ').loi === 'mot man hinh gioi thieu');

/* ---------- 2. cửa chặn của máy chủ ---------- */
console.log('\n2. Máy chủ chặn trước khi tiêu tiền');
/* HỎI MÁY CHỦ, đừng hỏi tiến trình của chính mình. `coKhoa()` gọi ở đây đọc
   biến môi trường của BÀI KIỂM, mà bài kiểm và máy chủ là hai tiến trình khác
   nhau — lần đầu viết đã sai đúng chỗ này, và nó báo "chưa khai khoá" trong khi
   máy chủ khai đủ. */
const toiLaAi = await goi('/api/toi-la-ai', null, 'GET');
const daKhai = toiLaAi.coStitch === true;
console.log(`  · máy chủ ${daKhai ? 'CÓ' : 'CHƯA'} khai khoá Stitch.`);

const ngan = await goi('/api/stitch', { y: 'hosting' });
if (daKhai) {
  /* ĐÂY LÀ MỤC QUAN TRỌNG NHẤT CỦA CẢ BÀI. Trả 202 cho lời tả hai chữ nghĩa là
     việc đã mở, hạn mức đã trừ, và người dùng phải đợi rồi mới biết mình gõ
     thiếu. */
  dat('lời tả quá ngắn bị chặn NGAY, không mở việc nào',
    ngan.ma === 400 && ngan.ok !== true, `mã ${ngan.ma}`);
} else {
  dat('chưa khai khoá thì nói thẳng, không mở việc', ngan.ma === 503, `mã ${ngan.ma}`);
}

const khongCo = await goi('/api/stitch/khong-he-co', null, 'GET');
dat('hỏi một lượt không có thì báo rõ, không sập',
  khongCo.ma === 404 && khongCo.ok === false, khongCo.loi);

/* ---------- 3. lượt gọi thật ---------- */
console.log('\n3. Gọi Stitch thật');
if (!THAT) {
  console.log('  — bỏ qua (một lượt mất ~90 giây và tốn hạn mức).');
  console.log('    Chạy STITCH_THAT=1 node tools/kiem-stitch.mjs để kiểm cả đường này.');
} else if (!daKhai) {
  console.log('  — bỏ qua: máy chủ chưa khai MOTION_STITCH_KEY.');
} else {
  const t0 = Date.now();
  const bd = await goi('/api/stitch', {
    y: 'Man hinh gioi thieu dich vu hosting cua Mat Bao. Nen trang, mau nhan xanh la. '
      + 'Mot tieu de lon, mot dong phu, mot nut Kham pha ngay.',
    kieuMay: 'DESKTOP',
  });
  dat('mở được lượt vẽ', bd.ma === 202 && Boolean(bd.id), bd.id || bd.loi);

  if (bd.id) {
    let d = null;
    for (let i = 0; i < 90; i++) {
      d = await goi(`/api/stitch/${bd.id}`, null, 'GET');
      if (d.trangThai === 'xong' || d.trangThai === 'loi') break;
      await new Promise((r) => setTimeout(r, 4000));
    }
    const giay = Math.round((Date.now() - t0) / 1000);

    if (d?.trangThai === 'loi' && /bận|quota|429|RESOURCE/i.test(d.loi || '')) {
      console.log(`  — bỏ qua: Stitch đang bận (${d.loi?.slice(0, 80)}).`);
    } else {
      dat('vẽ xong trong hạn', d?.trangThai === 'xong', `${giay}s · ${d?.loi || d?.tieuDe || ''}`);

      if (d?.trangThai === 'xong') {
        /* Hỏi lần thường KHÔNG được kèm mã HTML: nó cỡ 24 KB, mà trình duyệt
           hỏi vài giây một lần suốt một phút rưỡi. */
        dat('lượt hỏi thường không kèm mã HTML', d.html === undefined,
          `chỉ báo cỡ: ${d.soByte} byte`);
        dat('có tiêu đề và ảnh xem trước', Boolean(d.tieuDe) && Boolean(d.anhXem), d.tieuDe);

        const full = await goi(`/api/stitch/${bd.id}?html=1`, null, 'GET');
        dat('hỏi kèm `?html=1` thì có mã thật',
          typeof full.html === 'string' && /<html|<body/i.test(full.html),
          `${Math.round((full.html?.length || 0) / 1024)} KB`);

        /* CHỐT CUỐI: mã ấy phải dựng được thành cảnh HỢP LỆ. Vẽ ra một trang
           đẹp mà `/api/tu-html` không nuốt nổi thì tính năng này vô dụng. */
        const canh = await goi('/api/tu-html', {
          slug: 'cta', html: full.html, y: 'Dung lai man hinh nay thanh mot canh clip',
        });
        if (/đều không dùng được lúc này|đang bận/.test(canh.loi || canh.cau || '')) {
          console.log('  — bỏ qua bước dựng cảnh: chuỗi model của Google đang bận.');
        } else {
          dat('mã Stitch dựng được thành cảnh HỢP LỆ',
            canh.ok === true && Boolean(canh.canh), canh.loi || canh.cau || `${canh.model}`);
          if (canh.canh) {
            const mon = [];
            const di = (ds) => { for (const e of ds || []) { mon.push(e); di(e.children); } };
            di(canh.canh.elements);
            dat('cảnh có món, và qua được bộ soát của nút Lưu',
              mon.length > 0 && (canh.vanDe || []).length === 0,
              `${mon.length} món · ${(canh.vanDe || []).slice(0, 2).join(' · ') || 'sạch'}`);
          }
        }
      }
    }
  }
}

console.log(hong ? `\n❌ ${hong} mục không đạt.\n` : '\n✅ Đường Stitch → Motion đạt hết.\n');
process.exit(hong ? 1 : 0);
