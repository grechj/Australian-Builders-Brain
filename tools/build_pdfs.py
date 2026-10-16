"""Build the PDF checklists and handouts in templates/pdf from their brain pages.

Usage:
    python tools/build_pdfs.py            # rebuild every PDF
    python tools/build_pdfs.py --check    # exit 1 if any PDF is older than its page

The brain page is the source: any page with a `pdf:` key in its frontmatter
is rendered to that path. Edit the page, never the PDF, then rebuild. Pages
with `- [ ]` checklist items become tick-box checklists with a project/date
header; tables, notes (> quotes) and headings are kept.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parent.parent
BRAIN = ROOT / "brain"
INK, GREY, LINE, SHADE = colors.HexColor("#1a1a1a"), colors.HexColor("#555555"), colors.HexColor("#bbbbbb"), colors.HexColor("#f1f1ef")

ss = getSampleStyleSheet()
STYLES = {
    "title": ParagraphStyle("t", parent=ss["Title"], fontSize=17, leading=21, alignment=TA_LEFT, textColor=INK, spaceAfter=2 * mm),
    "sub": ParagraphStyle("s", parent=ss["Normal"], fontSize=9.5, leading=13, textColor=GREY, spaceAfter=4 * mm),
    "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11.5, leading=15, textColor=INK, spaceBefore=4 * mm, spaceAfter=1.5 * mm, keepWithNext=1),
    "body": ParagraphStyle("b", parent=ss["Normal"], fontSize=9.5, leading=13.5, textColor=INK, spaceAfter=2 * mm),
    "cell": ParagraphStyle("c", parent=ss["Normal"], fontSize=9, leading=12, textColor=INK),
    "note": ParagraphStyle("n", parent=ss["Normal"], fontSize=9, leading=12.5, textColor=GREY),
}


def inline(text: str) -> str:
    """Markdown inline to reportlab mini-HTML."""
    text = re.sub(r"<a id=\"[^\"]*\"></a>", "", text)
    text = re.sub(r"\[\^[^\]]+\]", "", text)                      # footnote markers
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)           # links -> text
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip()


def split_page(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    _, front, body = text.split("---\n", 2)
    body = re.sub(r"\n\[\^[^\]]+\]:.*", "", body)                  # footnote definitions
    return yaml.safe_load(front), body


def table_flowable(rows: list[list[str]]) -> Table:
    data = [[Paragraph(inline(c), STYLES["cell"]) for c in r] for r in rows]
    t = Table(data, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), SHADE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def checklist_flowable(items: list[str], width: float) -> Table:
    data = [[Paragraph("Item", STYLES["cell"]), Paragraph("Done", STYLES["cell"]), Paragraph("Notes", STYLES["cell"])]]
    data += [[Paragraph(inline(i), STYLES["cell"]), "☐", ""] for i in items]
    t = Table(data, colWidths=[width * 0.62, width * 0.08, width * 0.30], repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("BACKGROUND", (0, 0), (-1, 0), SHADE),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("FONTNAME", (1, 1), (1, -1), "DejaVu" if "DejaVu" in _fonts() else "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


_FONTS: set[str] = set()


def _fonts() -> set[str]:
    """Register a font with a ☐ glyph if one is available (Helvetica lacks it)."""
    if _FONTS:
        return _FONTS
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    for candidate in ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                      "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                      "/Library/Fonts/Arial Unicode.ttf"):
        if Path(candidate).exists():
            pdfmetrics.registerFont(TTFont("DejaVu", candidate))
            _FONTS.add("DejaVu")
            break
    _FONTS.add("Helvetica")
    return _FONTS


def render(page: Path, out: Path) -> None:
    meta, body = split_page(page)
    width = A4[0] - 36 * mm
    handout = "/handouts/" in str(page)
    story = [Paragraph(inline(meta["title"]), STYLES["title"])]
    if not handout:  # a handout's description is written for the builder, not the client
        story.append(Paragraph(inline(meta.get("description", "")), STYLES["sub"]))
    is_checklist = "- [ ]" in body or meta.get("type") == "Playbook"
    if is_checklist:
        story.append(table_flowable([["Project", "", "Date", ""], ["Completed by", "", "Signature", ""]]))
        story.append(Spacer(1, 3 * mm))

    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip() or line.startswith("<a id="):
            i += 1
            continue
        if line.startswith("#"):
            story.append(Paragraph(inline(line.lstrip("#").strip()), STYLES["h2"]))
            i += 1
        elif line.startswith("- [ ]"):
            items = []
            while i < len(lines) and lines[i].startswith("- [ ]"):
                items.append(lines[i][5:].strip())
                i += 1
            story.append(checklist_flowable(items, width))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            story.append(table_flowable(rows))
            story.append(Spacer(1, 2 * mm))
        elif line.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i].lstrip("> ").strip())
                i += 1
            if not handout:
                story.append(Paragraph(inline(" ".join(q for q in quote if q)), STYLES["note"]))
                story.append(Spacer(1, 2 * mm))
            # Handout pages keep builder-only notes (in quotes) out of the client PDF.
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(Paragraph("• " + inline(lines[i][2:]), STYLES["body"]))
                i += 1
            story.extend(items)
        else:
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"[#|>-]", lines[i]):
                para.append(lines[i].strip())
                i += 1
            story.append(Paragraph(inline(" ".join(para)), STYLES["body"]))

    footer_text = f"{meta['title']}  ·  General information only: check your contract and state requirements."

    def footer(canvas, doc):
        from reportlab.pdfbase.pdfmetrics import stringWidth
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GREY)
        text, room = footer_text, A4[0] - 36 * mm - 20 * mm
        while stringWidth(text, "Helvetica", 7.5) > room:
            text = text[:-2]
        canvas.drawString(18 * mm, 10 * mm, text if text == footer_text else text.rstrip() + "…")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm, title=meta["title"],
                            author="Australian Builder's Brain", subject=meta.get("description", ""))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def sources() -> list[tuple[Path, Path]]:
    pairs = []
    for page in sorted(BRAIN.rglob("*.md")):
        if page.name in ("index.md", "log.md"):
            continue
        text = page.read_text()
        m = re.search(r"^pdf: (.+)$", text.split("---", 2)[1] if text.startswith("---") else "", re.M)
        if m:
            pairs.append((page, ROOT / m.group(1).strip()))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if a PDF is missing or older than its page")
    args = parser.parse_args()
    _fonts()
    stale = []
    for page, out in sources():
        if args.check:
            if not out.exists() or out.stat().st_mtime < page.stat().st_mtime:
                stale.append(f"{out.relative_to(ROOT)} (from {page.relative_to(ROOT)})")
            continue
        render(page, out)
        print(f"built {out.relative_to(ROOT)} from {page.relative_to(ROOT)}")
    if stale:
        print("out of date:\n  " + "\n  ".join(stale))
        sys.exit(1)


if __name__ == "__main__":
    main()
