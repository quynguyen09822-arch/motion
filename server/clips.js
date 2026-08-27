/**
 * DANH SÁCH CLIP — đọc `scenes/*.json`, và nhận diện clip đời cũ.
 *
 * Trong dự án có hai đời clip. Đời mới là dữ liệu (`scenes/<tên>.json`), sửa
 * bằng chuột được. Đời cũ là code viết tay trong một file HTML — xem và xuất
 * video được, nhưng vị trí do code tính lúc chạy nên không sửa bằng chuột được.
 * Hàm ở đây trả về cả hai, có gắn nhãn `doi`, để giao diện nói thẳng với người
 * dùng thay vì để họ bấm mãi không được rồi tưởng hỏng.
 */
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import path from 'node:path';
import { PROJ, SCENES, tongThoiLuong } from './proj.js';

/** Đời cũ: mỗi clip là một file HTML tự chứa. Danh sách cứng — chúng không đẻ thêm. */
const DOI_CU = [
  { slug: 'marketer-52s', ten: 'Vibe Host — Marketer (52 giây, dọc)', file: 'vibe-host-marketer.html' },
  { slug: 'animatic-18s', ten: 'Vibe Hosting — bản 18 giây', file: 'vibe-hosting-animatic-18s.html' },
  { slug: 'animatic-90s', ten: 'Vibe Hosting — bản 90 giây', file: 'vibe-hosting-animatic-90s.html' },
];

/** Tên file chỉ được là chữ thường, số và gạch ngang — không dấu chấm, không gạch chéo. */
export function locSlug(raw) {
  if (typeof raw !== 'string') return null;
  const slug = raw.trim().toLowerCase();
  return /^[a-z0-9][a-z0-9-]{0,48}$/.test(slug) ? slug : null;
}

export function duongDanClip(slug) {
  return path.join(SCENES, `${slug}.json`);
}

export function docClip(slug) {
  const f = duongDanClip(slug);
  if (!existsSync(f)) return null;
  return { doc: JSON.parse(readFileSync(f, 'utf8')), suaLuc: statSync(f).mtimeMs };
}

/** Đường dẫn xem thử, tính theo đời clip. Luôn là đường dẫn tương đối của CHÍNH server này. */
export function duongDanXem(clip) {
  return clip.doi === 2
    ? `/clip/scene-player.html?scene=${clip.slug}`
    : `/clip/${clip.file}`;
}

export async function danhSachClip() {
  const ds = [];

  for (const ten of readdirSync(SCENES).sort()) {
    if (!ten.endsWith('.json')) continue;
    const slug = ten.replace(/\.json$/, '');
    const f = path.join(SCENES, ten);
    try {
      const doc = JSON.parse(readFileSync(f, 'utf8'));
      ds.push({
        slug,
        doi: 2,
        ten: doc?.meta?.name || slug,
        rong: doc?.meta?.width ?? null,
        cao: doc?.meta?.height ?? null,
        dung: doc?.meta?.height > doc?.meta?.width,
        soCanh: Array.isArray(doc?.scenes) ? doc.scenes.length : 0,
        giay: Math.round((await tongThoiLuong(doc)) * 10) / 10,
        file: `scenes/${ten}`,
        suaLuc: statSync(f).mtimeMs,
      });
    } catch (e) {
      // Một file hỏng không được làm chết cả danh sách — báo ra rồi đi tiếp.
      ds.push({ slug, doi: 2, ten: slug, hong: `Không đọc được: ${e.message}`, file: `scenes/${ten}` });
    }
  }

  for (const cu of DOI_CU) {
    const f = path.join(PROJ, cu.file);
    if (!existsSync(f)) continue;
    ds.push({ ...cu, doi: 1, suaLuc: statSync(f).mtimeMs });
  }

  return ds;
}
