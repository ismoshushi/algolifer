#!/usr/bin/env python3
"""Build index.html landing + reading page for GitHub Pages.

Web-only layout (PDF/EPUB builds in build.py are untouched):
sidebar TOC on the left (collapsible), anchor links to every chapter,
responsive drawer on small screens.
"""
import os
import re
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
html { scroll-behavior: smooth; }
body { font-family: "Noto Serif CJK SC","Songti SC","SimSun",serif;
       background: var(--paper); color: var(--ink);
       margin: 0; line-height: 1.95; font-size: 17px; }
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
.layout { display: flex; gap: 2.5em; max-width: 78em; margin: 0 auto;
          padding: 0 1.2em; align-items: flex-start; }
.toc { flex: 0 0 270px; position: sticky; top: 1em; max-height: calc(100vh - 2em);
       overflow-y: auto; background: #fff6; border: 1px solid #d8cdb4;
       border-radius: 8px; padding: 1em 1.1em; }
.toc-head { display: flex; justify-content: space-between; align-items: center;
            margin-bottom: .6em; }
.toc-head span { font-weight: bold; font-size: 1.05em; }
.toc-head button { background: none; border: 1px solid #d8cdb4; border-radius: 999px;
                   padding: .2em .8em; cursor: pointer; color: var(--muted); }
.toc ol { margin: 0; padding-left: 1.4em; }
.toc li { margin: .55em 0; line-height: 1.7; font-size: .93em; }
.toc a { color: var(--ink); text-decoration: none; }
.toc a:hover { color: var(--accent); }
.toc a.active { color: var(--accent); font-weight: bold; }
.toc-top { display: block; margin-top: 1em; padding-top: .8em;
           border-top: 1px dashed #d8cdb4; color: var(--muted);
           text-decoration: none; font-size: .9em; }
.book { flex: 1; min-width: 0; max-width: 46em; padding: 2em 0 3em; }
.book h2 { font-size: 1.4em; margin: 2.2em 0 .9em; scroll-margin-top: 1em;
           border-bottom: 1px solid #d8cdb4; padding-bottom: .4em; }
.book h3 { font-size: 1.12em; margin: 1.8em 0 .7em; scroll-margin-top: 1em; }
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
#toc-open { display: none; position: fixed; z-index: 40; padding: .55em 1em;
            border-radius: 999px; border: 1px solid var(--accent);
            background: var(--accent); color: #fff; cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,.2); }
body.toc-collapsed #toc-open { display: block; left: 1em; top: 1em; }
#toc-backdrop { display: none; }
@media (max-width: 960px) {
  .layout { display: block; }
  .toc { position: fixed; left: 0; top: 0; bottom: 0; z-index: 50; width: 280px;
         max-height: none; border-radius: 0; transform: translateX(-105%);
         transition: transform .25s ease; }
  body.toc-open .toc { transform: translateX(0); }
  #toc-open { display: block; right: 1em; bottom: 1em; left: auto; top: auto; }
  body.toc-open #toc-backdrop { display: block; position: fixed; inset: 0;
         background: rgba(0,0,0,.35); z-index: 45; }
  .hero h1 { font-size: 1.7em; }
}
"""

JS = """
(function(){
  var body = document.body;
  var openBtn = document.getElementById('toc-open');
  var closeBtn = document.getElementById('toc-close');
  var backdrop = document.getElementById('toc-backdrop');
  function setOpen(open){
    if (window.innerWidth >= 960) {
      body.classList.toggle('toc-collapsed', !open);
      try { localStorage.setItem('algolifer-toc', open ? 'open' : 'closed'); } catch(e) {}
    } else {
      body.classList.toggle('toc-open', open);
    }
  }
  try {
    if (window.innerWidth >= 960 && localStorage.getItem('algolifer-toc') === 'closed') {
      body.classList.add('toc-collapsed');
    }
  } catch(e) {}
  openBtn.addEventListener('click', function(){ setOpen(true); });
  closeBtn.addEventListener('click', function(){ setOpen(false); });
  backdrop.addEventListener('click', function(){ setOpen(false); });
  document.querySelectorAll('#toc a[href^="#sec-"]').forEach(function(a){
    a.addEventListener('click', function(){ if (window.innerWidth < 960) setOpen(false); });
  });
  var links = {};
  document.querySelectorAll('#toc a[href^="#sec-"]').forEach(function(a){
    links[a.getAttribute('href').slice(1)] = a;
  });
  var obs = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if (en.isIntersecting) {
        document.querySelectorAll('#toc a.active').forEach(function(x){ x.classList.remove('active'); });
        var a = links[en.target.id]; if (a) a.classList.add('active');
      }
    });
  }, { rootMargin: '-15% 0px -75% 0px' });
  document.querySelectorAll('.book h2[id]').forEach(function(h){ obs.observe(h); });
})();
"""


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def add_heading_ids(html):
    """Inject id="sec-N" into every <h2> in order; return (html, labels)."""
    labels = []

    def repl(m):
        inner = m.group(1)
        labels.append(strip_tags(inner))
        return f'<h2 id="sec-{len(labels)}">{inner}</h2>'

    return re.sub(r"<h2>(.*?)</h2>", repl, html), labels


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    blocks = md_to_blocks(text)
    body_html = blocks_to_html(blocks, chapter_class=False)
    # drop the auto title headers (hero covers them)
    body_html = body_html.replace("<h1>《算法长工自我修养》</h1>", "", 1)
    body_html = body_html.replace("<h2>第一册·X创作者篇</h2>", "", 1)
    body_html = body_html.replace("<h2>——X创作者计划：从入门到精通</h2>", "", 1)
    body_html, labels = add_heading_ids(body_html)

    toc_items = "".join(
        f'<li><a href="#sec-{i}">{label}</a></li>'
        for i, label in enumerate(labels, 1))
    toc = (f'<aside class="toc" id="toc">'
           f'<div class="toc-head"><span>目录</span>'
           f'<button id="toc-close" aria-label="收起目录">⟨ 收起</button></div>'
           f'<ol>{toc_items}</ol>'
           f'<a class="toc-top" href="#top">↑ 回到顶部</a></aside>')

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
<header class="hero" id="top">
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
<div class="layout" id="read">
{toc}
<main class="book">
{body_html}
</main>
</div>
<button id="toc-open" aria-label="打开目录">☰ 目录</button>
<div id="toc-backdrop"></div>
<footer class="site">
<div class="wrap">
<p>《算法长工自我修养》第一册·X创作者篇 ｜ {AUTHOR}（X {AUTHOR_X}）｜ {PUBLISHER}</p>
<p>开源地址：<a href="{REPO}">{REPO}</a></p>
<p>本书部分内容来源于网络公开资料的收集整理，仅供学习交流。如有侵权请联系作者（X {AUTHOR_X}），核实后及时删除。</p>
</div>
</footer>
<script>{JS}</script>
</body>
</html>"""
    out = os.path.join(_BASE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("SITE:", out, len(html), "headings:", len(labels))


if __name__ == "__main__":
    main()
