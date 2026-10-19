#!/usr/bin/env python3
"""Build index.html landing + reading page for GitHub Pages."""
import os
from build import (md_to_blocks, blocks_to_html, COPYRIGHT_HTML, BOOK_TITLE,
                   SUBTITLE, AUTHOR, AUTHOR_X, PUBLISHER, YEAR,
                   LICENSE_URL, LICENSE_NAME)

_BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_BASE, "算法长工自我修养.md")
REPO = "https://github.com/ismoshushi/algolifer"
REL = REPO + "/releases/download/v1"
PDF_URL = REL + "/algolifer-v1.pdf"
EPUB_URL = REL + "/algolifer-v1.epub"

CSS = """
:root { --paper:#f7f2e7; --ink:#2b2b2b; --accent:#b03a2e; --muted:#8a7f6a; }
* { box-sizing: border-box; }
body { font-family: "Noto Serif CJK SC","Songti SC","SimSun",serif;
       background: var(--paper); color: var(--ink);
       margin: 0; line-height: 1.9; }
.wrap { max-width: 44em; margin: 0 auto; padding: 0 1.2em; }
.hero { text-align: center; padding: 3.5em 1.2em 2.5em;
        border-bottom: 3px double var(--accent); }
.hero .kicker { color: var(--accent); letter-spacing: .35em; font-size: .85em;
                margin-bottom: 1em; }
.hero h1 { font-size: 2.2em; margin: .2em 0; letter-spacing: .08em; }
.hero .sub { color: var(--muted); margin: .5em 0 1.2em; }
.hero .slogan { font-size: 1.25em; font-weight: bold; color: var(--accent);
                margin: 1.2em 0; }
.hero .meta { color: var(--muted); font-size: .92em; margin-bottom: 1.6em; }
.hero img.cover { max-width: 240px; border: 1px solid #d8cdb4;
                  box-shadow: 0 4px 18px rgba(0,0,0,.18); margin-bottom: 1.2em; }
.btns { display: flex; flex-wrap: wrap; gap: .7em; justify-content: center;
        margin: 1.4em 0; }
.btn { display: inline-block; padding: .65em 1.4em; border-radius: 999px;
       text-decoration: none; font-size: 1em; border: 1px solid var(--accent); }
.btn.primary { background: var(--accent); color: #fff; }
.btn.ghost { color: var(--accent); background: transparent; }
.book { padding: 2em 0 3em; }
.book h2 { font-size: 1.4em; margin: 2.2em 0 .9em;
           border-bottom: 1px solid #d8cdb4; padding-bottom: .4em; }
.book h3 { font-size: 1.12em; margin: 1.8em 0 .7em; }
.book p { margin: .9em 0; text-align: justify; }
.book blockquote { border-left: 3px solid var(--accent); margin: 1.2em 0;
                   padding: .4em 1em; color: #555; background: #fff8; }
.book ul, .book ol { padding-left: 1.6em; }
.book li { margin: .45em 0; }
.book hr { border: none; border-top: 1px dashed #d8cdb4; margin: 2em 0; }
.copyright-page { background: #fff6; border: 1px solid #d8cdb4;
                  border-radius: 8px; padding: 1.2em 1.4em; margin: 1.5em 0; }
.copyright-page h2 { border: none; margin-top: 0; }
footer.site { border-top: 3px double var(--accent); padding: 2em 1.2em 3em;
              text-align: center; color: var(--muted); font-size: .9em; }
footer.site a { color: var(--accent); }
.toc { background: #fff6; border: 1px solid #d8cdb4; border-radius: 8px;
       padding: 1em 1.4em; margin: 1.5em 0; }
.toc h2 { margin-top: .4em; }
.toc ol { columns: 2; }
@media (max-width: 560px) { .toc ol { columns: 1; } .hero h1 { font-size: 1.7em; } }
"""

CHAPTERS = [
    ("前言", "本书写给谁"),
    ("第一章", "算法长工三问：你配吗"),
    ("第二章", "浏览量是唯一的真神"),
    ("第三章", "评论区：算法长工的工位"),
    ("第四章", "互关经济学与风控"),
    ("第五章", "内容炼金术：从20浏览到200浏览"),
    ("第六章", "十秒视频：算法长工的尊严"),
    ("第七章", "蓝V的自我修养"),
    ("第八章", "数据复盘：算法长工的体检表"),
    ("第九章", "心态管理：在自嘲中长期主义"),
    ("第十章", "从算法长工到监工：出师"),
    ("附录一", "算法长工黑话词典"),
    ("附录二", "算法长工90天路线图"),
    ("附录三", "算法长工工具箱"),
    ("后记", ""),
]

def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    blocks = md_to_blocks(text)
    body_html = blocks_to_html(blocks, chapter_class=False)
    # drop the auto title headers (hero covers them)
    body_html = body_html.replace("<h1>《算法长工自我修养》</h1>", "", 1)
    body_html = body_html.replace("<h2>第一册·X创作者篇</h2>", "", 1)
    body_html = body_html.replace("<h2>——X创作者计划：从入门到精通</h2>", "", 1)

    toc_items = "".join(
        f"<li>{a} {b}</li>" if b else f"<li>{a}</li>" for a, b in CHAPTERS)
    toc = f'<nav class="toc"><h2>目录</h2><ol>{toc_items}</ol></nav>'

    # insert TOC after 腰封 section (first <hr>)
    body_html = body_html.replace("<hr/>", "<hr/>" + toc, 1)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{BOOK_TITLE}{SUBTITLE}｜{AUTHOR}</title>
<meta name="description" content="《算法长工自我修养》第一册·X创作者篇——写给 X 中文创作者的讽刺生存手册，开源开放获取。"/>
<style>{CSS}</style>
</head>
<body>
<header class="hero">
<div class="wrap">
<div class="kicker">三千星火营出版</div>
<img class="cover" src="cover/cover-D-chiptian.png" alt="《算法长工自我修养》封面"
     onerror="this.style.display='none'"/>
<h1>{BOOK_TITLE}</h1>
<div class="sub">第一册·X创作者篇 ——X创作者计划：从入门到精通</div>
<div class="slogan">"没有小零工，只有大长工"</div>
<div class="meta">{AUTHOR}（X {AUTHOR_X}）著 ｜ {PUBLISHER} ｜ © {YEAR}</div>
<div class="btns">
<a class="btn primary" href="#read">📕 在线阅读</a>
<a class="btn ghost" href="{PDF_URL}">⬇ PDF</a>
<a class="btn ghost" href="{EPUB_URL}">⬇ EPUB</a>
<a class="btn ghost" href="{REPO}">⭐ GitHub 开源</a>
</div>
<div class="meta">本作品采用 <a href="{LICENSE_URL}">{LICENSE_NAME}</a> 许可：免费分享、改编须署名、非商业性使用、相同方式共享。</div>
</div>
</header>
<main class="wrap book" id="read">
{body_html}
</main>
<footer class="site">
<div class="wrap">
<p>《算法长工自我修养》第一册·X创作者篇 ｜ {AUTHOR}（X {AUTHOR_X}）｜ {PUBLISHER}</p>
<p>开源地址：<a href="{REPO}">{REPO}</a></p>
<p>本书部分内容来源于网络公开资料的收集整理，仅供学习交流。如有侵权请联系作者（X {AUTHOR_X}），核实后及时删除。</p>
</div>
</footer>
</body>
</html>"""
    out = os.path.join(_BASE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("SITE:", out, len(html))


if __name__ == "__main__":
    main()
