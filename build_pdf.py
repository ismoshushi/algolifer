#!/usr/bin/env python3
"""Build PDF via fpdf2. Run: python3 build_pdf.py"""
import re, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import md_to_blocks, inline, COPYRIGHT_HTML, BOOK_TITLE, SUBTITLE, AUTHOR, AUTHOR_X, PUBLISHER, YEAR, LICENSE_URL, LICENSE_NAME

from fpdf import FPDF

SRC = os.path.expanduser("~/workspace/x-book/algolifer/算法长工自我修养.md")
OUTDIR = os.path.expanduser("~/workspace/x-book/algolifer/dist")
COVER = os.path.expanduser("~/workspace/x-book/cover/cover-D-chiptian.png")
BASENAME = "算法长工自我修养-第一册-X创作者篇"
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

class BookPDF(FPDF):
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-12)
        self.set_font("NotoSerif", "", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, f"{BOOK_TITLE} ｜ {AUTHOR} ｜ {LICENSE_NAME}", align="C")

pdf = BookPDF(format="A5")
pdf.set_auto_page_break(True, margin=16)
pdf.add_font("NotoSerif", "", os.path.join(FONT_DIR, "NotoSerifSC-Regular.otf"))
pdf.add_font("NotoSerif", "B", os.path.join(FONT_DIR, "NotoSerifSC-Bold.otf"))
pdf.set_margins(16, 16, 16)

# Cover page
pdf.add_page()
pdf.image(COVER, x=0, y=0, w=148)
pdf.set_xy(pdf.l_margin, pdf.t_margin)  # image() leaves cursor x stale

# Copyright page: strip tags from COPYRIGHT_HTML into lines
pdf.add_page()
pdf.set_font("NotoSerif", "", 15)
pdf.cell(0, 10, "版权信息", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("NotoSerif", "", 10)
lines = [
    f"{BOOK_TITLE} {SUBTITLE}",
    f"作者：{AUTHOR}（X {AUTHOR_X}）",
    PUBLISHER,
    f"© {YEAR} {AUTHOR}。保留部分权利。",
    "",
    f"本作品采用 {LICENSE_NAME}（{LICENSE_URL}）国际许可协议进行许可。",
    "",
    "您可以免费复制、发行、展览和通过信息网络传播本作品，也可以改编、",
    "翻译或以本作品为基础进行创作，但必须遵守以下条件：",
    "· 署名——注明原作者（魔术士 Sahm）、原作出处及是否修改；",
    "· 非商业性使用——不得以商业目的使用本作品；",
    "· 相同方式共享——改编作品须以相同的许可协议发布。",
]
for ln in lines:
    pdf.multi_cell(0, 6.5, ln, new_x="LMARGIN", new_y="NEXT")

def html_inline(s):
    # reuse inline() then convert <strong>/<em>/<code> to fpdf2 write_html tags
    h = inline(s)
    h = h.replace("<strong>", "<b>").replace("</strong>", "</b>")
    h = re.sub(r"</?em>", "", h)
    h = re.sub(r"</?i>", "", h)
    h = re.sub(r"<code>(.*?)</code>", r"<font face=\"courier\">\1</font>", h)
    h = re.sub(r'<a href="([^"]+)">([^<]+)</a>', r'<a href="\1">\2</a>', h)
    return h

with open(SRC, encoding="utf-8") as f:
    blocks = md_to_blocks(f.read())

def para(h, size=10.5, bold=False, align="J", lh=6.8):
    pdf.set_font("NotoSerif", "B" if bold else "", size)
    pdf.write_html(f'<p align="{align}"><font size="{size}">{h}</font></p>')
    pdf.set_x(pdf.l_margin)

for kind, payload in blocks:
    if kind == "h1":
        pdf.add_page()
        pdf.ln(30)
        para(html_inline(payload), size=20, bold=True, align="C", lh=10)
    elif kind == "h2":
        pdf.add_page()
        pdf.ln(6)
        para(html_inline(payload), size=15, bold=True, lh=8.5)
        pdf.ln(2)
    elif kind == "h3":
        pdf.ln(3)
        para(html_inline(payload), size=12, bold=True, lh=7.5)
    elif kind == "quote":
        pdf.set_text_color(90, 90, 90)
        for q in payload:
            para("▍ " + html_inline(q), size=10, lh=6.5)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)
    elif kind == "hr":
        pdf.ln(4)
        x = pdf.l_margin + 30
        pdf.line(x, pdf.get_y(), 148 - 16 - 30, pdf.get_y())
        pdf.ln(4)
    elif kind == "ol":
        for n, item in enumerate(payload, 1):
            para(f"{n}. {html_inline(item)}", lh=6.8)
        pdf.ln(1)
    elif kind == "ul":
        for item in payload:
            para(f"· {html_inline(item)}", lh=6.8)
        pdf.ln(1)
    elif kind == "p":
        para(html_inline(payload), lh=6.8)

out = os.path.join(OUTDIR, BASENAME + ".pdf")
pdf.output(out)
print("PDF:", out, os.path.getsize(out))
