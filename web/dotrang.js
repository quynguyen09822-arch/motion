/**
 * ĐO TRANG NGAY TRONG TRÌNH DUYỆT NÀY — phần trình duyệt.
 *
 * Bản triển khai không có Chromium nên không tự đo được trang; trình duyệt người
 * dùng thì có (nó CHÍNH LÀ Chromium). Máy chủ cất trang lại, ta mở nó trong một
 * iframe ẩn đúng bằng khổ clip, trang tự đo bằng `web/dobocuc.js` rồi gửi bản đồ
 * ra đây. Toàn bộ lý do nằm ở đầu `server/dotrang.js`.
 *
 * IFRAME PHẢI ĐÚNG KHỔ CLIP. Đo một trang ở bề rộng 1600 rồi đem toạ độ đặt vào
 * clip 1280 là lệch hết. Đặt bề rộng iframe = bề rộng clip để trang TỰ DÀN LẠI
 * theo khổ thật, y như `doc-html.mjs` đặt cửa sổ Chromium.
 *
 * ĐẨY RA NGOÀI MÀN HÌNH, KHÔNG `display:none`. Phần tử `display:none` không có bố
 * cục — đo ra toàn số 0. `visibility:hidden` thì có bố cục nhưng trình duyệt có
 * thể không nạp phông cho chữ không hiện, và cỡ chữ đo được lại là cỡ của phông
 * dự phòng.
 */

/** Một trang Stitch nạp Tailwind + phông từ CDN rồi chờ thêm gần một giây. */
const HAN_MS = 60_000;

/**
 * @returns {Promise<object>} bản đồ bố cục, cùng khuôn với `tools/doc-html.mjs`
 * @throws  Error với câu tiếng Việt
 */
export async function doTrang({ html, url, rong, cao }) {
  const r = await fetch('/api/do-trang', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(url ? { url } : { html }),
  });
  const d = await r.json().catch(() => ({}));
  if (!d.ok) throw new Error(d.loi || d.cau || 'Máy chủ không cất được trang để đo.');

  const khung = document.createElement('iframe');
  /* `allow-scripts` và KHÔNG có `allow-same-origin`: trang lạ chạy ở origin rỗng,
     không đụng được trang sửa. Máy chủ cũng ép y như vậy bằng đầu đề CSP. */
  khung.setAttribute('sandbox', 'allow-scripts');
  khung.setAttribute('aria-hidden', 'true');
  khung.tabIndex = -1;
  Object.assign(khung.style, {
    position: 'fixed', left: '-100000px', top: '0',
    width: `${rong}px`, height: `${cao}px`,
    border: '0', pointerEvents: 'none',
  });

  try {
    return await new Promise((xong, hong) => {
      const hen = setTimeout(() => {
        removeEventListener('message', nghe);
        hong(new Error('Đo trang quá lâu (hơn 60 giây) — trang có thể đang chờ một thứ không tải được.'));
      }, HAN_MS);

      function nghe(ev) {
        /* Chỉ nhận tin từ ĐÚNG iframe này và ĐÚNG mã lượt đo này. Trang lạ nào
           khác trên máy cũng gửi được `postMessage` tới đây. */
        if (ev.source !== khung.contentWindow) return;
        if (!ev.data || ev.data.motionDoTrang !== d.id) return;
        clearTimeout(hen);
        removeEventListener('message', nghe);
        if (ev.data.loi) return hong(new Error(`Trang đo hỏng: ${ev.data.loi}`));
        if (!ev.data.banDo?.khoi) return hong(new Error('Trang đo không trả về bản đồ.'));
        xong(ev.data.banDo);
      }
      addEventListener('message', nghe);
      khung.src = `/do-trang/${d.id}`;
      document.body.appendChild(khung);
    });
  } finally {
    khung.remove();
  }
}
