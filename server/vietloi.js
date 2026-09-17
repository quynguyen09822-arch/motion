/**
 * AI VIẾT LỜI ĐỌC cho một clip đã dựng xong.
 *
 * Đây KHÔNG phải "viết quảng cáo theo brief". Clip đã có sẵn: bao nhiêu cảnh,
 * mỗi cảnh dài mấy giây, trên hình đang hiện chữ gì. Việc của AI là viết lời
 * KHỚP với cái đã có — nói đúng lúc hình đang nói, và dừng đúng lúc hình dừng.
 *
 * VÌ SAO PHẢI ĐƯA THỜI LƯỢNG TỪNG CẢNH VÀO LỜI NHẮC
 *   Không đưa thì AI viết một đoạn hay ho dài 40 giây cho một clip 24 giây.
 *   Người dùng đọc thấy hay, bấm đọc, rồi mới phát hiện lời tràn quá phim — lúc
 *   đó đã tiêu ký tự rồi. Nên đưa số giây và nói thẳng nhịp nói tiếng Việt.
 *
 * NHỊP NÓI: tiếng Việt đọc thong thả khoảng 2,2 tiếng/giây, đọc nhanh 2,8.
 *   Lấy 2,3 làm chuẩn cho lời quảng cáo — đọc nhanh hơn thì nghe như đuổi.
 */
import { khoaGoogle } from './giong.js';

/**
 * CHUỖI MODEL DỰ PHÒNG — xếp theo SỐ ĐO, không theo số hiệu phiên bản.
 *
 * Đo ngày 17/09/2026 bằng cùng một lời nhắc:
 *   gemini-3.8-flash        503 — và mất 63,8 GIÂY mới chịu báo 503
 *   gemini-3.5-flash        503 — sau 31,8 giây
 *   gemini-2.5-flash        404 — API có liệt kê, nhưng khoá này gọi không được
 *   gemini-3.6-flash        200 — 4,9 giây
 *   gemini-3-flash-preview  200 — 1,56 giây
 *   gemini-3.1-flash-lite   200 — 2,08 giây
 *
 * Ba điều rút ra:
 *   1. Model MỚI NHẤT không phải model tốt nhất để đặt đầu bảng. Nó hay quá tải,
 *      và tệ hơn là mất cả phút mới chịu nói mình quá tải.
 *   2. Danh sách model do API trả về CÓ NÓI DỐI: `gemini-2.5-flash` nằm trong
 *      danh sách kèm `generateContent`, gọi vào thì 404. Nên 404 cũng phải tụt
 *      sang model kế, không được coi là lỗi chết.
 *   3. Phải có HẠN GIỜ cho từng lượt. Không có thì một cái 503 chậm khoá cả
 *      chuỗi, và người dùng ngồi nhìn "AI đang viết…" gần một phút.
 *
 * Với một bài lời đọc sáu dòng thì chênh lệch chất lượng giữa các model flash là
 * không đáng kể, còn chênh lệch 1,5 giây với 64 giây thì rất đáng kể.
 */
const CHUOI_MODEL = ['gemini-3.6-flash', 'gemini-3-flash-preview', 'gemini-3.1-flash-lite', 'gemini-3.8-flash'];
/* 12 giây, không phải 20. Model chạy được trả lời trong 1,5–5 giây, nên 12 đã là
   gấp đôi khoảng rộng rãi. Để 20 thì mỗi lần tụt model tốn thêm 20 giây chờ vô
   ích, và tổng thời gian vọt lên hơn nửa phút — người dùng bỏ đi trước khi xong. */
const HAN_GIAY = 12;
export const TIENG_MOI_GIAY = 2.3;

/** Rút nội dung thật của clip: cảnh nào dài bao lâu, trên hình có chữ gì. */
export function tomTatClip(doc) {
  const canh = [];
  for (const c of doc?.scenes || []) {
    const chu = [];
    const di = (ds) => {
      for (const e of ds || []) {
        if (e.kind === 'text' && e.text) {
          chu.push(String(e.text).replace(/\s*\|\s*/g, ' ').replace(/\*/g, '').trim());
          if (e.sub) chu.push(String(e.sub).replace(/\*/g, '').trim());
        } else if (e.kind === 'nut' && e.label) chu.push(`[nút] ${String(e.label).trim()}`);
        else if (e.kind === 'browser' && e.url) chu.push(`[trình duyệt] ${e.url}`);
        if (e.children) di(e.children);
      }
    };
    di(c.elements);
    canh.push({ id: c.id, giay: c.duration || 0, chu: chu.filter(Boolean) });
  }
  return { ten: doc?.meta?.name || '', canh, giay: canh.reduce((t, c) => t + c.giay, 0) };
}

function loiNhac(tom, brief) {
  const dong = tom.canh.map((c, i) =>
    `  Cảnh ${i + 1} — ${c.giay.toFixed(1)} giây — trên hình: ${c.chu.length ? c.chu.join(' / ') : '(không có chữ)'}`);
  const tong = tom.giay;
  const tieng = Math.floor(tong * TIENG_MOI_GIAY);
  return `Bạn viết lời đọc (voice-over) tiếng Việt cho một clip quảng cáo ĐÃ DỰNG XONG.

CLIP ĐANG CÓ
  Tên: ${tom.ten || '(chưa đặt)'}
  Tổng: ${tong.toFixed(1)} giây, ${tom.canh.length} cảnh
${dong.join('\n')}

Ý MUỐN CỦA NGƯỜI DỰNG
${String(brief || '(không ghi gì thêm — cứ bám theo chữ trên hình)').trim()}

LUẬT VIẾT
1. Lời phải VỪA thời lượng. Cả bài tối đa khoảng ${tieng} tiếng (tiếng Việt đọc
   khoảng ${TIENG_MOI_GIAY} tiếng mỗi giây). Thà ngắn hơn chứ đừng dài hơn.
2. Mỗi cảnh một dòng, theo đúng thứ tự. Dòng nào cũng phải đọc lọt trong số giây
   của cảnh đó. Cảnh ngắn dưới 2 giây thì viết vài tiếng thôi, hoặc để trống.
3. ĐỪNG đọc lại y nguyên chữ đang hiện trên hình. Chữ trên hình để MẮT đọc, lời
   để TAI nghe — nói lại y hệt là thừa. Hãy nói phần mà hình không nói được.
4. Văn nói, câu ngắn, không sáo rỗng. Không dùng "đột phá", "giải pháp toàn diện",
   "tối ưu hoá trải nghiệm". Xưng hô trung tính.
5. Không emoji, không dấu ngoặc chú thích, không ghi tên cảnh. Chỉ lời để đọc.
6. Trả về ĐÚNG ${tom.canh.length} dòng, mỗi dòng một cảnh, không đánh số, không
   thêm lời dẫn nào trước hay sau.`;
}

export async function vietLoi({ doc, brief }) {
  const kq = khoaGoogle();
  if (!kq.ok) return { ok: false, cau: kq.cau };
  const tom = tomTatClip(doc);
  if (!tom.canh.length) return { ok: false, cau: 'Clip này chưa có cảnh nào.' };

  const than = JSON.stringify({
    contents: [{ role: 'user', parts: [{ text: loiNhac(tom, brief) }] }],
    generationConfig: { temperature: 0.8, maxOutputTokens: 2048 },
  });

  let d = null, daDung = null;
  const vetXe = [];
  for (const m of CHUOI_MODEL) {
    const bo = new AbortController();
    const hen = setTimeout(() => bo.abort(), HAN_GIAY * 1000);
    try {
      const r = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent?key=${encodeURIComponent(kq.k)}`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: than, signal: bo.signal });
      if (r.ok) { d = await r.json(); daDung = m; break; }
      await r.text();
      /* 503 quá tải · 429 hết lượt · 404 model không gọi được bằng khoá này —
         cả ba đều đáng tụt sang model kế. Mã khác (400 lời gọi sai, 403 khoá
         hỏng) thì tụt cũng vô ích: dừng luôn và nói thật. */
      if (![503, 429, 404].includes(r.status)) {
        return { ok: false, cau: `Google AI trả ${r.status} với ${m}.` };
      }
      vetXe.push(`${m}:${r.status}`);
    } catch (e) {
      vetXe.push(`${m}:${e.name === 'AbortError' ? `quá ${HAN_GIAY}s` : 'vỡ'}`);
    } finally { clearTimeout(hen); }
  }
  if (!d) {
    return { ok: false, cau: `Cả ${CHUOI_MODEL.length} model của Google AI đều không dùng được lúc này `
      + `(${vetXe.join(' · ')}). Thử lại sau vài phút, hoặc tự gõ lời.` };
  }
  const chu = (d.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('').trim();
  if (!chu) return { ok: false, cau: 'AI không trả về lời nào. Thử viết brief rõ hơn.' };

  const dong = chu.split('\n').map((x) => x.replace(/^\s*(\d+[.)]|[-•])\s*/, '').trim()).filter(Boolean);
  const soTieng = chu.split(/\s+/).filter(Boolean).length;
  return {
    ok: true,
    loi: dong.join('\n'),
    soDong: dong.length,
    soCanh: tom.canh.length,
    soTieng,
    giayClip: tom.giay,
    // Ước thời gian đọc để giao diện cảnh báo TRƯỚC khi người dùng bấm đọc.
    giayDoc: Number((soTieng / TIENG_MOI_GIAY).toFixed(1)),
    model: daDung,
    // Nói ra khi phải tụt model — để biết model đầu bảng hỏng chốc lát hay dài ngày.
    tutModel: vetXe.length ? `${vetXe.join(' · ')} → dùng ${daDung}` : null,
  };
}
