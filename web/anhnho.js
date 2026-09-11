/**
 * ẢNH NHỎ CỦA TỪNG THÀNH PHẦN — như bảng lớp của Photoshop.
 *
 * Danh sách chỉ có chấm màu và tên thì nhìn không ra món nào là món nào: một
 * cảnh có sáu "Khối màu" và bốn "Chữ" thì cái tên chẳng giúp được gì. Có hình
 * thì nhận ra ngay.
 *
 * CÁCH LÀM: nhân bản chính nút DOM của món từ trong iframe ra, thả vào một
 * shadow root ở trang cha, kèm nguyên `<style>` của bộ dựng. Đọc được vì cùng
 * origin. Không đụng gì tới bên trong iframe — chỉ ĐỌC rồi chép ra.
 *
 * BA CÁI BẪY đã vấp khi dựng thử, đừng gỡ mấy đoạn xử lý bên dưới:
 *
 *  1. ĐƯỜNG DẪN ẢNH. Trong iframe, gốc là `/clip/`; ở trang cha, gốc là `/`.
 *     Chép nguyên `src="public/a.png"` ra là ảnh vỡ hết. Phải đổi thành đường
 *     dẫn tuyệt đối theo gốc CỦA IFRAME.
 *  2. MÀU NỀN. Màu chữ của clip (`--ink`) có khi là màu tối, vì clip nền sáng.
 *     Thả lên ô nền đen là chữ biến mất. Ô phải lấy đúng màu nền của clip.
 *  3. TRẠNG THÁI CHUYỂN ĐỘNG. Nút được nhân bản đang mang `opacity` và
 *     `transform` của đúng khoảnh khắc hiện tại — món chưa bay vào thì `opacity`
 *     bằng 0, chép ra được một ô trống trơn. Phải gỡ cả hai.
 */

const CO = 34;        // cạnh ô ảnh nhỏ trong danh sách, px

export function taoAnhNho(player) {
  let css = '';
  let bien = '';        // chuỗi khai lại mọi biến CSS của clip
  let nen = '#000';
  let goc = '';         // gốc đường dẫn của iframe

  /** Đọc lại CSS và bảng màu của clip. Gọi sau mỗi lần mở clip. */
  function napLai() {
    const d = player.tai();
    if (!d) { css = ''; return false; }
    goc = d.baseURI;
    css = [...d.querySelectorAll('style')].map((s) => s.textContent).join('\n');

    // Gom tên mọi biến CSS mà bộ dựng khai, rồi đọc giá trị đang áp trên body.
    const ten = new Set();
    for (const s of d.styleSheets) {
      try {
        for (const r of s.cssRules) {
          if (r.style) for (const k of r.style) if (k.startsWith('--')) ten.add(k);
        }
      } catch { /* bảng kiểu khác origin thì bỏ, ở đây không có */ }
    }
    const cs = d.defaultView.getComputedStyle(d.body);
    for (const k of d.body.style) if (k.startsWith('--')) ten.add(k);
    bien = [...ten].map((k) => `${k}:${cs.getPropertyValue(k)}`).join(';');
    nen = cs.getPropertyValue('--bg')?.trim() || cs.backgroundColor || '#000';
    return Boolean(css);
  }

  /** Đổi mọi đường dẫn tương đối trong bản sao sang tuyệt đối theo gốc iframe. */
  function suaDuongDan(node) {
    for (const n of [node, ...node.querySelectorAll('*')]) {
      for (const thuoc of ['src', 'href']) {
        const v = n.getAttribute?.(thuoc);
        if (v && !/^(https?:|data:|blob:|#)/.test(v)) {
          try { n.setAttribute(thuoc, new URL(v, goc).href); } catch { /* bỏ qua */ }
        }
      }
      // `mask-image`/`background-image` đặt thẳng vào style cũng chứa đường dẫn.
      const st = n.style;
      if (!st) continue;
      for (const k of ['maskImage', 'webkitMaskImage', 'backgroundImage']) {
        const v = st[k];
        if (!v || !v.includes('url(')) continue;
        st[k] = v.replace(/url\(["']?([^"')]+)["']?\)/g, (cu, u) => {
          if (/^(https?:|data:|blob:)/.test(u)) return cu;
          try { return `url("${new URL(u, goc).href}")`; } catch { return cu; }
        });
      }
    }
  }

  /**
   * Vẽ ảnh nhỏ của một món vào một ô.
   * @param monId id của món · @param canhId cảnh chứa nó
   * @param o     phần tử ô (đã có sẵn trong danh sách)
   * @param canh  cạnh ô, px
   */
  function ve(canhId, monId, o, canh = CO) {
    if (!css && !napLai()) return false;
    const gocNode = player.node(canhId, monId);
    if (!gocNode) return false;
    /*
     * Ô phải ĐANG HIỆN mới đo được. Vẽ vào một ô còn `display:none` thì mọi phép
     * đo ra 0, hệ số thu bị chặn ở mức tối đa và món phóng to gấp bốn thay vì
     * thu nhỏ vừa ô — nhìn ra một mảng trắng vô nghĩa. Đã mắc với ô xem lớn.
     */
    if (!o.offsetWidth || !o.offsetHeight) return false;

    o.textContent = '';
    const sh = o.shadowRoot || o.attachShadow({ mode: 'open' });
    sh.innerHTML = '';

    const st = document.createElement('style');
    st.textContent = `${css}
      :host{display:block;overflow:hidden}
      .khung{position:absolute;inset:0;background:${nen};${bien}}
      .giua{position:absolute;left:50%;top:50%}`;

    const khung = document.createElement('div');
    khung.className = 'khung';

    const ban = gocNode.cloneNode(true);
    suaDuongDan(ban);
    // Gỡ trạng thái của khoảnh khắc hiện tại — xem bẫy 3 ở đầu file.
    ban.style.opacity = '1';
    ban.style.transform = 'none';
    ban.style.animation = 'none';
    ban.classList.add('giua');

    khung.appendChild(ban);
    sh.append(st, khung);

    /*
     * Đo SAU khi đã gắn vào cây, và đo `offsetWidth` chứ không phải
     * `getBoundingClientRect` của bản gốc: bản gốc đang nằm dưới hai tầng phóng
     * của sân khấu và máy quay, lấy số đó là thu nhỏ hai lần.
     */
    const w = ban.offsetWidth || 1;
    const h = ban.offsetHeight || 1;
    const ti = Math.min((canh - 4) / w, (canh - 4) / h, 4);
    ban.style.transform = `translate(-50%,-50%) scale(${ti})`;
    return true;
  }

  return { ve, napLai, CO };
}
