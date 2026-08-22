#!/usr/bin/env python3
"""Gera as propostas PDF a partir das fontes Markdown canônicas."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
BRAND = ROOT / "assets" / "brand"
GREEN = colors.HexColor("#123F34")
GREEN_DARK = colors.HexColor("#0C2F28")
YELLOW = colors.HexColor("#FCC931")
CREAM = colors.HexColor("#F4E8CF")
BLUE = colors.HexColor("#0F3C65")
INK = colors.HexColor("#172A25")
MUTED = colors.HexColor("#52625D")
RULE = colors.HexColor("#D8CCB5")


@dataclass(frozen=True)
class PdfSpec:
    source: Path
    output: Path
    subtitle: str
    title: str


class HorizontalRule(Flowable):
    def __init__(self, width: float, color=YELLOW, thickness: float = 2.0):
        super().__init__()
        self.width = width
        self.height = thickness + 5
        self.color = color
        self.thickness = thickness

    def draw(self) -> None:
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.height - 2, self.width, self.height - 2)


def register_fonts() -> None:
    fonts = {
        "LeagueSpartan": "LeagueSpartan-Regular.ttf",
        "LeagueSpartan-Medium": "LeagueSpartan-Medium.ttf",
        "LeagueSpartan-SemiBold": "LeagueSpartan-SemiBold.ttf",
        "LeagueSpartan-Bold": "LeagueSpartan-Bold.ttf",
    }
    for name, filename in fonts.items():
        pdfmetrics.registerFont(TTFont(name, str(BRAND / "fonts" / filename)))


def make_styles():
    sample = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "Body",
            parent=sample["BodyText"],
            fontName="LeagueSpartan",
            fontSize=9.4,
            leading=13.2,
            textColor=INK,
            spaceAfter=5,
            alignment=TA_LEFT,
        ),
        "h1": ParagraphStyle(
            "H1",
            fontName="LeagueSpartan-Bold",
            fontSize=20,
            leading=23,
            textColor=GREEN,
            spaceBefore=7,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="LeagueSpartan-Bold",
            fontSize=14.5,
            leading=18,
            textColor=GREEN,
            spaceBefore=11,
            spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="LeagueSpartan-SemiBold",
            fontSize=11.2,
            leading=14,
            textColor=BLUE,
            spaceBefore=7,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "Quote",
            fontName="LeagueSpartan-Medium",
            fontSize=9.3,
            leading=13,
            textColor=GREEN_DARK,
            leftIndent=7,
            rightIndent=7,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=7.4,
            leading=10,
            # Preformatted não pinta o backColor de forma confiável em todos os
            # renderizadores. Texto escuro preserva a legibilidade mesmo quando
            # o fundo do estilo não é desenhado.
            textColor=GREEN_DARK,
            backColor=colors.HexColor("#F6F0E3"),
            borderPadding=7,
            spaceBefore=4,
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small",
            fontName="LeagueSpartan",
            fontSize=7.8,
            leading=10.5,
            textColor=MUTED,
        ),
    }


def inline_markup(text: str) -> str:
    text = escape(text)
    text = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r'<link href="\2" color="#0F3C65">\1</link>', text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    return text


def paragraph(text: str, style) -> Paragraph:
    return Paragraph(inline_markup(text), style)


def parse_table(lines: list[str], styles, frame_width: float) -> Table:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        rows.pop(1)
    columns = max(len(row) for row in rows)
    for row in rows:
        row.extend([""] * (columns - len(row)))
    data = [
        [Paragraph(inline_markup(cell), styles["small"]) for cell in row]
        for row in rows
    ]
    widths = [frame_width / columns] * columns
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "LeagueSpartan-SemiBold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FBF7EE")),
                ("GRID", (0, 0), (-1, -1), 0.35, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def markdown_to_story(text: str, styles, frame_width: float) -> list:
    lines = text.splitlines()
    story: list = []
    paragraph_lines: list[str] = []
    list_lines: list[str] = []
    list_kind: str | None = None
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            story.append(paragraph(" ".join(line.strip() for line in paragraph_lines), styles["body"]))
            paragraph_lines.clear()

    def flush_list() -> None:
        nonlocal list_kind
        if not list_lines:
            return
        items = [ListItem(paragraph(item, styles["body"]), leftIndent=10) for item in list_lines]
        list_options = {
            "bulletType": "1" if list_kind == "number" else "bullet",
            "leftIndent": 16,
            "bulletFontName": "Helvetica-Bold",
            "bulletFontSize": 8.5,
            "bulletColor": GREEN,
            "spaceAfter": 7,
        }
        if list_kind == "number":
            list_options["start"] = "1"
        story.append(ListFlowable(items, **list_options))
        list_lines.clear()
        list_kind = None

    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["code"]))
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue

        if stripped.startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|"):
            flush_paragraph()
            flush_list()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            story.append(Spacer(1, 3))
            story.append(parse_table(table_lines, styles, frame_width))
            story.append(Spacer(1, 6))
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            if level == 1 and not story:
                index += 1
                continue
            if level == 2:
                story.append(HorizontalRule(min(frame_width, 46 * mm)))
            story.append(paragraph(heading.group(2), styles[f"h{level}"]))
            index += 1
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            flush_list()
            callout = Table(
                [[paragraph(stripped[2:], styles["quote"]) ]],
                colWidths=[frame_width],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
                        ("LINEBEFORE", (0, 0), (0, -1), 4, YELLOW),
                        ("BOX", (0, 0), (-1, -1), 0.35, RULE),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                ),
            )
            story.extend([callout, Spacer(1, 5)])
            index += 1
            continue

        bullet = re.match(r"^-\s+(.+)$", stripped)
        numbered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if bullet or numbered:
            flush_paragraph()
            kind = "number" if numbered else "bullet"
            if list_kind and list_kind != kind:
                flush_list()
            list_kind = kind
            list_lines.append((numbered or bullet).group(1))
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
        else:
            paragraph_lines.append(stripped)
        index += 1

    flush_paragraph()
    flush_list()
    if code_lines:
        story.append(Preformatted("\n".join(code_lines), styles["code"]))
    return story


def cover_callback(spec: PdfSpec):
    def draw(canvas, doc) -> None:
        width, height = A4
        canvas.saveState()
        canvas.setTitle(spec.title)
        canvas.setAuthor("Equipe AgroTurtles")
        canvas.setSubject("Proposta Maestro Agrícola — AI Glasses Brasil 2026")
        canvas.setFillColor(CREAM)
        canvas.rect(0, 0, width, height, stroke=0, fill=1)
        canvas.setFillColor(GREEN_DARK)
        canvas.rect(0, 0, width, height * 0.82, stroke=0, fill=1)
        canvas.setFillColor(YELLOW)
        canvas.rect(0, height * 0.82, width, 7 * mm, stroke=0, fill=1)

        canvas.setFillColor(YELLOW)
        canvas.setFont("LeagueSpartan-SemiBold", 11)
        canvas.drawString(28 * mm, height - 44 * mm, "PROPOSTA DE PROJETO")
        canvas.setFillColor(CREAM)
        canvas.setFont("LeagueSpartan-Bold", 36)
        canvas.drawString(28 * mm, height - 74 * mm, "MAESTRO")
        canvas.drawString(28 * mm, height - 91 * mm, "AGRÍCOLA")

        canvas.setFillColor(colors.white)
        canvas.setFont("LeagueSpartan-SemiBold", 17)
        canvas.drawString(28 * mm, height - 119 * mm, spec.subtitle.upper())
        canvas.setStrokeColor(YELLOW)
        canvas.setLineWidth(3)
        canvas.line(28 * mm, height - 128 * mm, 68 * mm, height - 128 * mm)

        canvas.setFont("LeagueSpartan", 12)
        canvas.setFillColor(CREAM)
        canvas.drawString(28 * mm, height - 145 * mm, "Equipe AgroTurtles")
        canvas.drawString(28 * mm, height - 154 * mm, "AI Glasses Brasil 2026")
        canvas.drawString(28 * mm, height - 163 * mm, "Revisão: 22 de agosto de 2026")

        logo_path = BRAND / "logo-horizontal.png"
        if logo_path.exists():
            logo = Image(str(logo_path), width=62 * mm, height=19.2 * mm)
            logo.drawOn(canvas, 28 * mm, 26 * mm)

        canvas.setFillColor(GREEN)
        canvas.setFont("LeagueSpartan-SemiBold", 8)
        canvas.drawRightString(width - 18 * mm, 13 * mm, "AGROTURTLES  ·  2026")
        canvas.restoreState()

    return draw


def body_callback(canvas, doc) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, height - 16 * mm, width - 18 * mm, height - 16 * mm)
    canvas.setFont("LeagueSpartan-SemiBold", 8)
    canvas.setFillColor(GREEN)
    canvas.drawString(18 * mm, height - 12 * mm, "MAESTRO AGRÍCOLA")
    canvas.setFont("LeagueSpartan", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 18 * mm, height - 12 * mm, "PROPOSTA · AGROTURTLES")
    canvas.setStrokeColor(YELLOW)
    canvas.setLineWidth(1.5)
    canvas.line(18 * mm, 14 * mm, 48 * mm, 14 * mm)
    canvas.setFont("LeagueSpartan-SemiBold", 8)
    canvas.setFillColor(GREEN)
    canvas.drawRightString(width - 18 * mm, 12 * mm, f"{doc.page:02d}")
    canvas.restoreState()


def build_pdf(spec: PdfSpec) -> None:
    styles = make_styles()
    width, height = A4
    left = right = 18 * mm
    top = 22 * mm
    bottom = 19 * mm
    frame_width = width - left - right
    frame = Frame(left, bottom, frame_width, height - top - bottom, id="body-frame")
    doc = BaseDocTemplate(
        str(spec.output),
        pagesize=A4,
        leftMargin=left,
        rightMargin=right,
        topMargin=top,
        bottomMargin=bottom,
        title=spec.title,
        author="Equipe AgroTurtles",
        subject="Proposta Maestro Agrícola — AI Glasses Brasil 2026",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[Frame(0, 0, width, height, id="cover-frame")], onPage=cover_callback(spec)),
            PageTemplate(id="body", frames=[frame], onPage=body_callback),
        ]
    )

    source_text = spec.source.read_text(encoding="utf-8")
    story = [NextPageTemplate("body"), PageBreak()]
    story.extend(markdown_to_story(source_text, styles, frame_width))
    doc.build(story)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    register_fonts()
    specs = [
        PdfSpec(
            source=Path(__file__).resolve().parent / "versao-resumida.md",
            output=args.output_dir / "Maestro-Agricola-Versao-Resumida-Revisada.pdf",
            subtitle="Versão resumida revisada",
            title="Maestro Agrícola — Versão Resumida Revisada",
        ),
        PdfSpec(
            source=Path(__file__).resolve().parent / "versao-tecnica.md",
            output=args.output_dir / "Maestro-Agricola-Versao-Tecnica-Revisada.pdf",
            subtitle="Versão técnica revisada",
            title="Maestro Agrícola — Versão Técnica Revisada",
        ),
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        build_pdf(spec)
        print(spec.output)


if __name__ == "__main__":
    main()
