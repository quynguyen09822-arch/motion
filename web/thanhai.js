/**
 * NÚT AI Ở THANH DƯỚI, và thanh hỏi bật lên từ đó.
 *
 * VÌ SAO Ở DƯỚI CHỨ KHÔNG PHẢI CỘT PHẢI
 *   Cột phải là chỗ SỬA MỘT MÓN đang chọn — mọi thứ trong đó đều thuộc về một
 *   thành phần cụ thể. Hỏi AI thì không: câu hỏi thường về cả clip, và hỏi trong
 *   lúc đang xem chứ không phải đang chỉnh. Nhét vào cột phải là bắt người dùng
 *   rời khỏi việc đang làm để đi tìm chỗ hỏi.
 *
 * THANH NẰM NGANG, KHÔNG PHẢI KHUNG CHAT
 *   Không giữ lịch sử hội thoại. Một câu hỏi, một câu trả lời, xong. Giữ lịch sử
 *   thì phải có chỗ cuộn, có chỗ xoá, và người dùng bắt đầu chờ đợi nó nhớ được
 *   mọi thứ — mà nó thì không. Hứa ít, giữ đúng lời.
 *
 * BA CÂU GỢI Ý, và chúng là ba câu hỏi CÓ THẬT người dùng hay hỏi. Ô trống
 * không có gợi ý là ô trống người ta không biết gõ gì vào.
 */
const el = (the, lop, chu) => {
  const n = document.createElement(the);
  if (lop) n.className = lop;
  if (chu != null) n.textContent = chu;
  return n;
};

const GOI_Y = [
  'Clip này đang có vấn đề gì không?',
  'Nên thêm gì cho đỡ trống?',
  'Nhịp chuyển động đã ổn chưa?',
];

export function taoThanhAI({ nutBoc, laySlug, bao, moKhungAI }) {
  let mo = false, dangHoi = false;

  const nut = el('button', 'nut-ai');
  nut.type = 'button';
  nut.title = 'Hỏi AI về clip này';
  nut.setAttribute('aria-label', 'Hỏi AI về clip này');
  nut.setAttribute('aria-expanded', 'false');
  nut.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true">'
    + '<path d="M8 1.6l1.5 3.9 3.9 1.5-3.9 1.5L8 12.4 6.5 8.5 2.6 7l3.9-1.5z"/>'
    + '<path d="M12.6 10.6l.6 1.6 1.6.6-1.6.6-.6 1.6-.6-1.6-1.6-.6 1.6-.6z"/></svg>'
    + '<span class="nut-ai-chu">AI</span>';

  const thanh = el('div', 'thanh-ai an');
  thanh.setAttribute('role', 'dialog');
  thanh.setAttribute('aria-label', 'Hỏi AI về clip');

  const hangGoi = el('div', 'ai-goi-y');
  const o = el('input', 'o-nhap o-hoi');
  o.type = 'text';
  o.placeholder = 'Hỏi gì về clip này…';
  o.setAttribute('aria-label', 'Câu hỏi cho AI');

  const gui = el('button', 'nut chinh nut-gui', 'Hỏi');
  gui.type = 'button';
  const dong = el('button', 'nut-ti nut-dong-ai');
  dong.type = 'button';
  dong.title = 'Đóng (Esc)';
  dong.setAttribute('aria-label', 'Đóng thanh AI');
  dong.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg>';

  const tra = el('div', 'ai-tra an');

  const hang = el('div', 'ai-hang-hoi');
  hang.append(o, gui, dong);
  thanh.append(hangGoi, hang, tra);

  function veGoiY() {
    hangGoi.innerHTML = '';
    for (const g of GOI_Y) {
      const b = el('button', 'ai-chip', g);
      b.type = 'button';
      b.onclick = () => { o.value = g; hoi(); };
      hangGoi.appendChild(b);
    }
    const b2 = el('button', 'ai-chip nhan', 'Viết lời đọc…');
    b2.type = 'button';
    // Việc này đã có hẳn một khung riêng với brief, chọn giọng và nghe thử —
    // đưa người dùng sang đó thay vì trả lời nửa vời trong một thanh ngang.
    b2.onclick = () => { datMo(false); moKhungAI?.(); };
    hangGoi.appendChild(b2);
  }

  async function hoi() {
    const cau = o.value.trim();
    const slug = laySlug?.();
    if (!cau || dangHoi) return;
    if (!slug) return bao('Mở một clip trước đã.', true);
    dangHoi = true;
    gui.disabled = true; gui.textContent = 'Đang nghĩ…';
    tra.classList.remove('an', 'hong');
    tra.textContent = 'Đang đọc lại clip…';
    try {
      const r = await fetch('/api/hoi-ai', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slug, hoi: cau }),
      });
      const d = await r.json();
      if (!d.ok) { tra.classList.add('hong'); tra.textContent = d.loi || 'Hỏi AI hỏng.'; return; }
      tra.textContent = d.tra;
    } catch (e) {
      tra.classList.add('hong');
      tra.textContent = `Hỏi AI hỏng — ${String(e.message || e).slice(0, 80)}`;
    } finally { dangHoi = false; gui.disabled = false; gui.textContent = 'Hỏi'; }
  }

  gui.onclick = hoi;
  o.onkeydown = (ev) => {
    if (ev.key === 'Enter') { ev.preventDefault(); hoi(); }
    if (ev.key === 'Escape') { ev.preventDefault(); datMo(false); }
  };
  dong.onclick = () => datMo(false);

  function datMo(v) {
    mo = v;
    thanh.classList.toggle('an', !v);
    nut.classList.toggle('dang-mo', v);
    nut.setAttribute('aria-expanded', String(v));
    if (v) { veGoiY(); o.focus(); }
    else { tra.classList.add('an'); tra.textContent = ''; }
  }

  nut.onclick = () => datMo(!mo);
  /* Esc đóng thanh dù con trỏ đang ở đâu. Bắt ở cấp tài liệu vì người dùng hay
     bấm Esc trong lúc mắt nhìn khung hình, không phải trong lúc con trỏ ở ô gõ. */
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && mo) { ev.preventDefault(); datMo(false); }
  });

  nutBoc.appendChild(nut);
  document.body.appendChild(thanh);
  return { mo: () => datMo(true), dong: () => datMo(false) };
}
