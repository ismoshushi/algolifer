#!/usr/bin/env python3
"""Build single-file HTML / EPUB / PDF for 《算法长工自我修养》第一册.
Stdlib only. Run: python3 build.py  (then chromium for PDF)
"""
import re, html as ihtml, zipfile, os, sys, shutil

_BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_BASE, "算法长工自我修养.md")
OUTDIR = os.path.join(_BASE, "dist")
_COVER_CANDIDATES = [
    os.path.join(_BASE, "cover", "cover-D-chiptian.png"),
    os.path.expanduser("~/workspace/x-book/cover/cover-D-chiptian.png"),
]
COVER = next((p for p in _COVER_CANDIDATES if os.path.exists(p)), None)
BASENAME = "算法长工自我修养-第一册-X创作者篇"

BOOK_TITLE = "《算法长工自我修养》"
SUBTITLE = "第一册·X创作者篇 ——X创作者计划：从入门到精通"
AUTHOR = "魔术士 Sahm"
AUTHOR_X = "@idsahm"
PUBLISHER = "三千星火营出版"
YEAR = "2026"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
LICENSE_NAME = "CC BY-NC-SA 4.0"

COPYRIGHT_HTML = f"""<section class="copyright-page">
<h2>版权信息</h2>
<p>{BOOK_TITLE} {SUBTITLE}</p>
<p>作者：{AUTHOR}（X {AUTHOR_X}）</p>
<p>{PUBLISHER}</p>
<p>© {YEAR} {AUTHOR}。保留部分权利。</p>
<p>本作品采用 <a href="{LICENSE_URL}">{LICENSE_NAME}</a> 国际许可协议进行许可。</p>
<p>您可以免费复制、发行、展览和通过信息网络传播本作品，也可以改编、翻译或以本作品为基础进行创作，但必须遵守以下条件：</p>
<ul>
<li><strong>署名</strong>——注明原作者（{AUTHOR}）、原作出处及是否修改；</li>
<li><strong>非商业性使用</strong>——不得以商业目的使用本作品；</li>
<li><strong>相同方式共享</strong>——改编作品须以相同的许可协议发布。</li>
</ul>
<h2>内容来源与权利声明</h2>
<p>1. 本书引用的 X 网友观点（如 @HanZhang415188 对 X 开源算法的分析、@isnail、@lixinbao_X 的实战分享）均已注明出处，引用目的为介绍与评论，符合《中华人民共和国著作权法》第二十四条关于合理使用的规定。</p>
<p>2. 本书对斯坦尼斯拉夫斯基先生及其《演员的自我修养》的引用为致敬式戏仿；腰封所引语录系为本书创作的戏仿文字，并非其本人原话。</p>
<p>3. 本书部分案例与数据来源于网络公开资料的收集整理，仅供学习交流。</p>
<p>4. 如您认为本书内容侵犯了您的合法权益，请联系作者（X @idsahm），我们将在核实后及时删除相关内容。</p>
</section>"""

CSS = """
body { font-family: "Noto Serif CJK SC", "Songti SC", serif; line-height: 1.9;
       color: #222; max-width: 42em; margin: 0 auto; padding: 2em 1.2em; }
h1 { text-align: center; font-size: 1.9em; margin: 1.2em 0 0.3em; }
h2 { font-size: 1.35em; margin: 2em 0 0.8em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
h3 { font-size: 1.12em; margin: 1.6em 0 0.6em; }
p { text-align: justify; margin: 0.9em 0; }
blockquote { border-left: 3px solid #b00; margin: 1em 0; padding: 0.2em 0 0.2em 1em; color: #555; }
blockquote p { margin: 0.4em 0; }
hr { border: none; border-top: 1px solid #ddd; margin: 2.2em auto; width: 40%; }
ul, ol { margin: 0.9em 0; padding-left: 1.6em; }
li { margin: 0.4em 0; }
.copyright-page { background: #f8f6f1; border: 1px solid #ddd; padding: 1.2em 1.5em;
                  margin: 2em 0; font-size: 0.92em; }
.cover { text-align: center; margin: 1em 0 2em; }
.cover img { max-width: 320px; width: 60%; }
.attrib-foot { margin-top: 3em; padding-top: 1em; border-top: 1px solid #ccc;
               font-size: 0.85em; color: #666; }
@media print {
  body { max-width: none; padding: 0; }
  h2 { page-break-before: auto; }
  .chapter { page-break-before: always; }
  .copyright-page { break-inside: avoid; }
}
@page { size: A5; margin: 18mm 14mm; }
"""

def inline(s):
    s = ihtml.escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`(.+?)`', r'<code>\1</code>', s)
    s = re.sub(r'(https?://[^\s<>\)\]]+)', r'<a href="\1">\1</a>', s)
    return s

def md_to_blocks(md):
    """Return list of (kind, payload) blocks."""
    lines = md.split('\n')
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1; continue
        if re.match(r'^#{1,3}\s', s):
            level = len(re.match(r'^(#+)', s).group(1))
            blocks.append(('h%d' % level, s[level:].strip()))
            i += 1; continue
        if s.startswith('>'):
            qs = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                qs.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(('quote', qs)); continue
        if re.match(r'^(-{3,}|\*{3,})$', s):
            blocks.append(('hr', None)); i += 1; continue
        if re.match(r'^\d+\.\s', s):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i].strip()):
                items.append(re.sub(r'^\d+\.\s', '', lines[i].strip()))
                i += 1
            blocks.append(('ol', items)); continue
        if re.match(r'^[-*]\s', s):
            items = []
            while i < len(lines) and re.match(r'^[-*]\s', lines[i].strip()):
                items.append(re.sub(r'^[-*]\s', '', lines[i].strip()))
                i += 1
            blocks.append(('ul', items)); continue
        # paragraph: gather until blank
        ps = []
        while i < len(lines) and lines[i].strip():
            ps.append(lines[i].strip())
            i += 1
        blocks.append(('p', ' '.join(ps)))
    return blocks

def blocks_to_html(blocks, chapter_class=False):
    out = []
    for kind, payload in blocks:
        if kind in ('h1', 'h2', 'h3'):
            lvl = kind[1]
            cls = ' class="chapter"' if (kind == 'h2' and chapter_class) else ''
            out.append(f'<h{lvl}{cls}>{inline(payload)}</h{lvl}>')
        elif kind == 'quote':
            out.append('<blockquote>' + ''.join(f'<p>{inline(q)}</p>' for q in payload) + '</blockquote>')
        elif kind == 'hr':
            out.append('<hr/>')
        elif kind == 'ol':
            out.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in payload) + '</ol>')
        elif kind == 'ul':
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in payload) + '</ul>')
        elif kind == 'p':
            out.append(f'<p>{inline(payload)}</p>')
    return '\n'.join(out)

ATTRIB_FOOT = f"""<div class="attrib-foot">
<p>{BOOK_TITLE}{SUBTITLE} ｜ 作者：{AUTHOR}（X {AUTHOR_X}）｜ {PUBLISHER}</p>
<p>本作品采用 <a href="{LICENSE_URL}">{LICENSE_NAME}</a> 许可：免费分享、改编须署名、非商业性使用、相同方式共享。</p>
</div>"""

def build_html(body_html, title):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="author" content="{AUTHOR}"/>
<meta name="dcterms.rights" content="{LICENSE_NAME} {LICENSE_URL}"/>
<title>{ihtml.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
{body_html}
{ATTRIB_FOOT}
</body>
</html>"""

def split_chapters(blocks):
    """Split blocks at h2 into chapters. Returns [(title, blocks)]."""
    chapters, cur, cur_title = [], [], "扉页"
    for kind, payload in blocks:
        if kind == 'h2':
            if cur:
                chapters.append((cur_title, cur))
            cur, cur_title = [], payload
        else:
            cur.append((kind, payload))
    if cur:
        chapters.append((cur_title, cur))
    return chapters

def build_epub(chapters, out_path):
    tmp = out_path + ".tmpdir"
    oebps = os.path.join(tmp, "OEBPS")
    metainf = os.path.join(tmp, "META-INF")
    os.makedirs(oebps, exist_ok=True)
    os.makedirs(metainf, exist_ok=True)
    has_cover = COVER is not None
    if has_cover:
        shutil.copy(COVER, os.path.join(oebps, "cover.png"))

    spine_items, manifest_items, nav_points = [], [], []
    for idx, (title, blks) in enumerate(chapters):
        fname = f"chapter-{idx:02d}.xhtml"
        is_title_page = (idx == 0)
        inner = blocks_to_html(blks, chapter_class=not is_title_page)
        if is_title_page:
            inner = COPYRIGHT_HTML + "\n" + inner
        xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN">
<head><title>{ihtml.escape(title)}</title><style>{CSS}</style></head>
<body>{inner}{ATTRIB_FOOT}</body>
</html>"""
        with open(os.path.join(oebps, fname), "w", encoding="utf-8") as f:
            f.write(xhtml)
        manifest_items.append(f'<item id="ch{idx}" href="{fname}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="ch{idx}"/>')
        nav_points.append(f'<li><a href="{fname}">{ihtml.escape(title)}</a></li>')

    if has_cover:
        manifest_items.append('<item id="cover" href="cover.png" media-type="image/png"/>')
    manifest_items.append('<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>目录</title></head>
<body><nav epub:type="toc"><h1>目录</h1><ol>{''.join(nav_points)}</ol></nav></body>
</html>"""
    with open(os.path.join(oebps, "nav.xhtml"), "w", encoding="utf-8") as f:
        f.write(nav)

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="3.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>{ihtml.escape(BOOK_TITLE + SUBTITLE)}</dc:title>
<dc:creator>{ihtml.escape(AUTHOR)}</dc:creator>
<dc:language>zh-CN</dc:language>
<dc:identifier id="bookid">urn:algolifer:changong-1</dc:identifier>
<dc:rights>本作品采用 {LICENSE_NAME}（{LICENSE_URL}）许可：署名、非商业性使用、相同方式共享。</dc:rights>
<meta property="dcterms:modified">2026-10-19T00:00:00Z</meta>
<meta name="cover" content="cover"/>
</metadata>
<manifest>{''.join(manifest_items)}</manifest>
<spine>{''.join(spine_items)}</spine>
</package>"""
    with open(os.path.join(oebps, "content.opf"), "w", encoding="utf-8") as f:
        f.write(opf)
    with open(os.path.join(metainf, "container.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')

    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        for root, _, files in os.walk(tmp):
            for fn in sorted(files):
                full = os.path.join(root, fn)
                arc = os.path.relpath(full, tmp)
                z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(tmp)

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    with open(SRC, encoding="utf-8") as f:
        md = f.read()
    blocks = md_to_blocks(md)
    chapters = split_chapters(blocks)

    # single-file HTML (copyright page right after the title h1)
    body_html = blocks_to_html(blocks, chapter_class=True)
    body_html = body_html.replace('</h1>', '</h1>\n' + COPYRIGHT_HTML, 1)
    html_doc = build_html(body_html, BOOK_TITLE + SUBTITLE)
    html_path = os.path.join(OUTDIR, BASENAME + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    print("HTML:", html_path, os.path.getsize(html_path))

    # EPUB
    epub_path = os.path.join(OUTDIR, BASENAME + ".epub")
    build_epub(chapters, epub_path)
    print("EPUB:", epub_path, os.path.getsize(epub_path))
    print("PDF: run chromium --headless --print-to-pdf on the HTML")

if __name__ == "__main__":
    main()
