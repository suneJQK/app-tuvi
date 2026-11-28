#!/usr/bin/env python3
"""
Xuất toàn văn tài liệu đã biên tập (TAI_LIEU_BIEN_TAP_DAY_DU.md) ra tệp PDF
hỗ trợ đầy đủ tiếng Việt Unicode (DejaVu Serif / DejaVu Sans) và KẺ BẢNG CHUẨN
cho toàn bộ các bảng tra cứu bằng PyMuPDF Story.
"""

import html
import re
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
SRC_MD = ROOT / "TAI_LIEU_BIEN_TAP_DAY_DU.md"
OUT_PDF = ROOT / "TAI_LIEU_BIEN_TAP_DAY_DU.pdf"
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def md_inline_to_html(text: str) -> str:
    s = html.escape(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def render_html_table(table_lines: list[str]) -> str:
    """Chuyển khối bảng Markdown (| a | b |) thành HTML <table> kẻ ô chuẩn."""
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # Bỏ dòng phân cách | --- | --- |
        if all(re.fullmatch(r":?-{2,}:?", c) or c == "" for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""

    ncols = max(len(r) for r in rows)
    # Bảng nhiều cột dùng cỡ chữ nhỏ hơn để vừa khít khổ giấy A4
    tbl_class = "data-table wide-table" if ncols >= 10 else "data-table"

    html_parts = [f'<table class="{tbl_class}">']
    for r_idx, row in enumerate(rows):
        tag = "th" if r_idx == 0 else "td"
        row_cls = ' class="alt"' if (r_idx > 0 and r_idx % 2 == 0) else ""
        cells_html = "".join(f"<{tag}>{md_inline_to_html(c)}</{tag}>" for c in row)
        html_parts.append(f"<tr{row_cls}>{cells_html}</tr>")
    html_parts.append("</table>")
    return "\n".join(html_parts)


def md_to_html(md_text: str) -> str:
    parts = []
    quote_lines = []
    table_lines = []

    def flush_quote():
        nonlocal quote_lines
        if quote_lines:
            body = "<br/>".join(md_inline_to_html(l) for l in quote_lines)
            parts.append(f'<div class="note-box">{body}</div>')
            quote_lines = []

    def flush_table():
        nonlocal table_lines
        if table_lines:
            parts.append(render_html_table(table_lines))
            table_lines = []

    for raw_line in md_text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_quote()
            flush_table()
            continue
        if line.startswith("<!--") and line.endswith("-->"):
            continue
        if line == "---":
            flush_quote()
            flush_table()
            parts.append("<hr/>")
            continue
        if line.startswith("|") and line.endswith("|"):
            flush_quote()
            table_lines.append(line)
            continue
        else:
            flush_table()

        if line.startswith(">"):
            q = line.lstrip(">").strip()
            if q:
                quote_lines.append(q)
            continue
        else:
            flush_quote()

        if line.startswith("# "):
            parts.append(f"<h1>{md_inline_to_html(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            parts.append(f"<h2>{md_inline_to_html(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            parts.append(f"<h3>{md_inline_to_html(line[4:].strip())}</h3>")
        else:
            parts.append(f"<p>{md_inline_to_html(line)}</p>")

    flush_quote()
    flush_table()
    return "\n".join(parts)


CSS = """
@font-face {
    font-family: "DejaVuSerif";
    src: url("DejaVuSerif.ttf");
    font-weight: normal;
}
@font-face {
    font-family: "DejaVuSerif";
    src: url("DejaVuSerif-Bold.ttf");
    font-weight: bold;
}
@font-face {
    font-family: "DejaVuSans";
    src: url("DejaVuSans.ttf");
    font-weight: normal;
}
@font-face {
    font-family: "DejaVuSans";
    src: url("DejaVuSans-Bold.ttf");
    font-weight: bold;
}
body {
    font-family: "DejaVuSerif", serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1a1a1a;
}
h1 {
    font-family: "DejaVuSans", sans-serif;
    font-size: 16pt;
    color: #7a1c1c;
    margin-top: 14pt;
    margin-bottom: 8pt;
    page-break-before: always;
}
h1:first-of-type {
    page-break-before: avoid;
    text-align: center;
    font-size: 18pt;
}
h2 {
    font-family: "DejaVuSans", sans-serif;
    font-size: 13pt;
    color: #2c3e50;
    margin-top: 12pt;
    margin-bottom: 6pt;
}
h3 {
    font-family: "DejaVuSans", sans-serif;
    font-size: 11pt;
    color: #34495e;
    margin-top: 8pt;
    margin-bottom: 4pt;
}
p {
    margin-top: 0;
    margin-bottom: 5pt;
    text-align: justify;
}
code {
    font-family: "DejaVuSans", sans-serif;
    font-size: 9.5pt;
    background-color: #f3f4f6;
}
hr {
    border: none;
    border-top: 0.75pt solid #cccccc;
    margin: 10pt 0;
}
.note-box {
    font-family: "DejaVuSans", sans-serif;
    font-size: 9.5pt;
    line-height: 1.4;
    background-color: #fff8e6;
    border-left: 3pt solid #d97706;
    padding: 8pt 10pt;
    margin: 8pt 0 10pt 0;
    color: #3b2f1e;
}
table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 6pt 0 10pt 0;
    font-family: "DejaVuSans", sans-serif;
    font-size: 8.5pt;
    line-height: 1.25;
}
table.wide-table {
    font-size: 6.8pt;
    line-height: 1.2;
}
table.data-table th {
    background-color: #e8edf3;
    color: #1e293b;
    font-weight: bold;
    border: 0.6pt solid #94a3b8;
    padding: 3pt 4pt;
    text-align: center;
}
table.data-table td {
    border: 0.5pt solid #cbd5e1;
    padding: 2.5pt 3.5pt;
    text-align: center;
}
table.data-table tr.alt td {
    background-color: #f8fafc;
}
"""


def main():
    print(f"Đang đọc {SRC_MD.name}...")
    md_text = SRC_MD.read_text(encoding="utf-8")
    body_html = md_to_html(md_text)
    full_html = f"<html><body>{body_html}</body></html>"

    print("Đang dựng PDF có kẻ bảng chuẩn bằng PyMuPDF Story...")
    archive = pymupdf.Archive(FONT_DIR)
    story = pymupdf.Story(html=full_html, user_css=CSS, archive=archive)

    mediabox = pymupdf.paper_rect("a4")
    where = mediabox + (42, 48, -42, -48)

    writer = pymupdf.DocumentWriter(str(OUT_PDF))
    page_num = 0
    more = True
    while more:
        page_num += 1
        device = writer.begin_page(mediabox)
        more, _ = story.place(where)
        story.draw(device)
        writer.end_page()
    writer.close()

    # Đánh số trang chân trang
    doc = pymupdf.open(str(OUT_PDF))
    font_path = str(Path(FONT_DIR) / "DejaVuSans.ttf")
    for idx, page in enumerate(doc, 1):
        if idx == 1:
            continue
        rect = pymupdf.Rect(0, mediabox.height - 32, mediabox.width, mediabox.height - 14)
        page.insert_textbox(
            rect,
            f"- {idx} -",
            fontsize=8.5,
            fontname="dejavusans",
            fontfile=font_path,
            align=pymupdf.TEXT_ALIGN_CENTER,
            color=(0.4, 0.4, 0.4),
        )
    temp_out = ROOT / "TAI_LIEU_BIEN_TAP_DAY_DU_tmp.pdf"
    doc.save(str(temp_out), garbage=0, deflate=True)
    doc.close()
    temp_out.replace(OUT_PDF)

    print(f"Hoàn tất xuất PDF có bảng chuẩn: {OUT_PDF.name} — {page_num} trang, {OUT_PDF.stat().st_size / (1024*1024):.2f} MB")


if __name__ == "__main__":
    main()
