/**
 * DANH SÁCH THÀNH PHẦN — cây dựng TỪ KỊCH BẢN, không phải từ DOM.
 *
 * Đây là đường DUY NHẤT để chọn nền (`nen`) và vệt sáng (`sweep`): bộ dựng đặt
 * hai loại đó `pointer-events:none` nên bấm trên khung hình không bao giờ trúng.
 * Cũng là đường thoát khi một món bị món khác che kín.
 */
import { TEN_LOAI } from './inspector/schema.js';
import { tenMon } from './inspector/index.js';

const el = (the, lop, chu) => {
  const n = document.createElement(the);
  if (lop) n.className = lop;
  if (chu != null) n.textContent = chu;
  return n;
};

export function taoDanhSach(boc, { onChon, onRe, onThoiRe, anhNho }) {
  let chon = null;
  let canhDang = null;

  /*
   * Vẽ ảnh nhỏ LƯỜI: chỉ vẽ ô nào thật sự cuộn tới. Một cảnh của
   * `thu-trien-khai-html` có hơn 150 món; nhân bản hết một lượt là khựng cả
   * giao diện mỗi lần đổi lựa chọn, mà người dùng chỉ nhìn thấy chừng mười ô.
   */
  const doiNgo = new IntersectionObserver((muc) => {
    for (const m of muc) {
      if (!m.isIntersecting) continue;
      const o = m.target;
      doiNgo.unobserve(o);
      if (o.dataset.veRoi) continue;
      o.dataset.veRoi = '1';
      anhNho?.ve(canhDang, o.dataset.mon, o);
    }
  }, { root: boc, rootMargin: '80px' });

  /* Ô xem lớn khi rê chuột — như Photoshop bấm giữ vào ảnh nhỏ thì phóng ra. */
  const oLon = document.createElement('div');
  oLon.className = 'lop-xem-lon an';
  document.body.appendChild(oLon);
  let henLon = null;

  function hienLon(hang, monId) {
    clearTimeout(henLon);
    // Chờ một nhịp ngắn: lướt chuột qua cả danh sách mà ô nào cũng bật ra thì
    // rối mắt, và nhân bản liên tục cũng phí.
    henLon = setTimeout(() => {
      // Đặt chỗ và HIỆN RA TRƯỚC, vẽ sau: `anhNho.ve` phải đo được ô mới tính
      // đúng hệ số thu, mà ô đang `display:none` thì mọi phép đo ra 0.
      const r = hang.getBoundingClientRect();
      const cao = 168;
      oLon.style.left = `${r.right + 10}px`;
      oLon.style.top = `${Math.min(Math.max(8, r.top - cao / 2 + r.height / 2), innerHeight - cao - 8)}px`;
      oLon.classList.remove('an');
      if (!anhNho?.ve(canhDang, monId, oLon, 168)) oLon.classList.add('an');
    }, 220);
  }
  function anLon() {
    clearTimeout(henLon);
    oLon.classList.add('an');
  }

  function ve(doc, canhId) {
    boc.innerHTML = '';
    canhDang = canhId;
    doiNgo.disconnect();
    anLon();
    const canh = (doc?.scenes || []).find((s) => s.id === canhId);
    if (!canh) return;

    const dao = (els, sau) => {
      for (const e of els || []) {
        const hang = el('div', 'lop-hang');
        hang.style.paddingLeft = `${10 + sau * 14}px`;
        hang.dataset.mon = e.id;
        if (chon?.monId === e.id) hang.classList.add('dang');

        // Ô ảnh nhỏ thay cho chấm màu. Giữ `data-loai` để còn có màu viền khi
        // món không dựng được hình (nền, vệt sáng… vốn trong suốt).
        const o = el('div', 'lop-anh');
        o.dataset.loai = e.kind;
        o.dataset.mon = e.id;
        doiNgo.observe(o);
        hang.append(o, el('span', 'lop-ten', tenMon(e)));

        // Nền và vệt sáng bấm trên khung hình không trúng — đánh dấu để người
        // dùng biết vì sao chỉ chọn được từ đây.
        if (e.kind === 'nen' || e.kind === 'sweep') {
          hang.append(el('span', 'lop-dau', 'chỉ chọn ở đây'));
        }

        hang.onclick = () => onChon({ canhId, monId: e.id });
        hang.onmouseenter = () => { onRe({ canhId, monId: e.id }); hienLon(hang, e.id); };
        hang.onmouseleave = () => { onThoiRe(); anLon(); };
        boc.appendChild(hang);

        if (e.kind === 'group') dao(e.children, sau + 1);
      }
    };
    dao(canh.elements, 0);
  }

  return {
    ve,
    dat(c) { chon = c; },
    /** Kịch bản vừa đổi → vẽ lại những ô đang nhìn thấy. */
    veLaiAnh() {
      for (const o of boc.querySelectorAll('.lop-anh')) {
        delete o.dataset.veRoi;
        doiNgo.observe(o);
      }
    },
  };
}
