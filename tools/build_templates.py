"""Build the templates added after the original pack, in the pack's house style.

Usage:
    python tools/build_templates.py            # builds any that don't exist yet
    python tools/build_templates.py --force    # rebuilds all of them (overwrites hand edits)

The original 46 templates were made in Word and Excel. These ones are built
here so their layout matches: a logo and business block, a navy title, grey
label tables, navy-headed line tables, and a Setup sheet in each workbook.
Once built, a template can be edited by hand like any other; run
`python tools/describe_templates.py` afterwards to refresh its Structure.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
WORD = ROOT / "templates" / "word"
EXCEL = ROOT / "templates" / "excel"
NAVY, GREY, WHITE = "003366", "F5F5F5", "FFFFFF"
SIG = "____________________"


# ---------------------------------------------------------------- Word helpers

def _shade(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def _borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "BFBFBF")
        borders.append(el)
    tbl_pr.append(borders)


def _widths(table, cms: list[float]) -> None:
    """Fixed column widths: grid, table width and every cell, so all viewers agree."""
    table.autofit = False
    tbl = table._tbl
    for col, w in zip(tbl.tblGrid.findall(qn("w:gridCol")), cms):
        col.set(qn("w:w"), str(int(Cm(w).twips)))
    tbl_w = tbl.tblPr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl.tblPr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(Cm(sum(cms)).twips)))
    tbl_w.set(qn("w:type"), "dxa")
    for row in table.rows:
        for cell, w in zip(row.cells, cms):
            cell.width = Cm(w)


def _run(p, text: str, size: float = 10, bold: bool = False, font: str = "Calibri", color: str | None = None):
    r = p.add_run(text)
    r.font.size, r.font.bold, r.font.name = Pt(size), bold, font
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r


def _cell(cell, text: str, bold: bool = False, color: str | None = None, font: str = "Cambria", align=None) -> None:
    lines = text.split("\n")
    p = cell.paragraphs[0]
    for i, line in enumerate(lines):
        if i:
            p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        if align is not None:
            p.alignment = align
        _run(p, line, 10, bold, font if bold else "Calibri", color)


class Doc:
    def __init__(self, title: str, licence_label: str = "Licence"):
        self.d = Document()
        normal = self.d.styles["Normal"]
        normal.font.name, normal.font.size = "Calibri", Pt(10)
        normal.paragraph_format.space_after = Pt(4)
        sec = self.d.sections[0]
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, side, Cm(2.0))
        head = self.d.add_table(rows=1, cols=2)
        head.alignment = WD_TABLE_ALIGNMENT.CENTER
        _widths(head, [7.5, 9.5])
        _run(head.rows[0].cells[0].paragraphs[0], "[LOGO]")
        right = head.rows[0].cells[1]
        lines = [("[BUSINESS_NAME]", 11, True), ("ABN: [ABN]", 9, False),
                 (f"{licence_label}: [LICENCE_NUMBER]", 9, False), ("[PHONE] | [EMAIL]", 9, False)]
        for i, (text, size, bold) in enumerate(lines):
            p = right.paragraphs[0] if i == 0 else right.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p.paragraph_format.space_after = Pt(0)
            _run(p, text, size, bold, "Cambria" if bold else "Calibri")
        p = self.d.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _run(p, title, 14, True, "Cambria", NAVY)

    def heading(self, text: str) -> None:
        p = self.d.add_paragraph()
        _run(p, text, 11, True, "Cambria", NAVY)

    def para(self, text: str, bold: bool = False, italic: bool = False) -> None:
        p = self.d.add_paragraph()
        r = _run(p, text, 10, bold)
        r.font.italic = italic

    def info(self, pairs: list[tuple[str, str]], cols: int = 4) -> None:
        """Grey label table: label, value, label, value."""
        per_row = cols // 2
        rows = [pairs[i:i + per_row] for i in range(0, len(pairs), per_row)]
        t = self.d.add_table(rows=len(rows), cols=cols)
        _borders(t)
        _widths(t, [3.4, 5.1, 3.4, 5.1] if cols == 4 else [5, 12])
        for r, chunk in zip(t.rows, rows):
            for j, (label, value) in enumerate(chunk):
                _cell(r.cells[2 * j], label, bold=True)
                _shade(r.cells[2 * j], GREY)
                _cell(r.cells[2 * j + 1], value)
        self.d.add_paragraph()

    def lines(self, header: list[str], rows: list[list[str]], widths: list[float] | None = None) -> None:
        """Navy-headed line table. The widest column is the second unless widths are given."""
        t = self.d.add_table(rows=1 + len(rows), cols=len(header))
        _borders(t)
        n = len(header)
        if not widths:
            other = {2: 4.0, 3: 3.5, 4: 3.0, 5: 2.6}.get(n, 2.4)
            widths = [other] * n
            widths[1 if n > 2 else 0] = 17 - other * (n - 1)
        _widths(t, widths)
        for c, text in zip(t.rows[0].cells, header):
            _cell(c, text, bold=True, color=WHITE)
            _shade(c, NAVY)
        for r, values in zip(t.rows[1:], rows):
            for c, text in zip(r.cells, values):
                _cell(c, text)
        self.d.add_paragraph()

    def totals(self, labels: list[str], last_highlight: bool = True) -> None:
        t = self.d.add_table(rows=len(labels), cols=2)
        _borders(t)
        _widths(t, [11, 6])
        for i, (r, label) in enumerate(zip(t.rows, labels)):
            last = last_highlight and i == len(labels) - 1
            _cell(r.cells[0], label, bold=True, color=WHITE if last else None)
            _shade(r.cells[0], NAVY if last else GREY)
            _cell(r.cells[1], "$", bold=last, align=WD_ALIGN_PARAGRAPH.RIGHT)
        self.d.add_paragraph()

    def box(self, text: str) -> None:
        """A one-cell table for free text the filler replaces."""
        t = self.d.add_table(rows=1, cols=1)
        _borders(t)
        _widths(t, [17])
        _cell(t.rows[0].cells[0], text)
        self.d.add_paragraph()

    def signatures(self, who: list[str]) -> None:
        for name in who:
            self.heading(name)
            t = self.d.add_table(rows=2, cols=4)
            _borders(t)
            _widths(t, [2.6, 5.9, 2.6, 5.9])
            for r, (a, b) in zip(t.rows, [("Name:", "Date:"), ("Signature:", "Position:")]):
                _cell(r.cells[0], a, bold=True); _shade(r.cells[0], GREY)
                _cell(r.cells[1], SIG)
                _cell(r.cells[2], b, bold=True); _shade(r.cells[2], GREY)
                _cell(r.cells[3], SIG)
            self.d.add_paragraph()

    def save(self, path: Path) -> None:
        self.d.save(path)


# ------------------------------------------------------------- Word templates

def payment_claim() -> Doc:
    d = Doc("PAYMENT CLAIM")
    d.para("This is a payment claim made under the [SOPA_ACT].", bold=True)
    d.info([("Claim No:", "[CLAIM_NUMBER]"), ("Claim Date:", "[DATE]"),
            ("Claimant:", "[BUSINESS_NAME]"), ("Respondent:", "[CLIENT_NAME]"),
            ("Claimant Address:", "[BUSINESS_ADDRESS], [BUSINESS_ADDRESS_LINE_2]"), ("Respondent Address:", "[CLIENT_ADDRESS]"),
            ("Project:", "[PROJECT_ADDRESS]"), ("Contract No:", "[CONTRACT_NUMBER]"),
            ("Work Up To:", "[DD/MM/YYYY]"), ("Payment Due:", "[DD/MM/YYYY]")])
    d.heading("WORK CLAIMED")
    d.para("The construction work and related goods and services this claim covers:")
    d.lines(["Item", "Description of work", "Contract Value", "Complete to Date", "This Claim"],
            [["", "", "$", "$", "$"]] * 4)
    d.totals(["Total Completed to Date (excl. GST)", "Less: Previously Claimed", "Less: Retention (if applicable)",
              "Amount Claimed This Claim (excl. GST)", "GST (10%)", "AMOUNT CLAIMED (incl. GST)"])
    d.heading("PAYMENT DETAILS")
    d.info([("Account Name:", "[ACCOUNT_NAME]"), ("BSB:", "[BSB]"),
            ("Account Number:", "[ACCOUNT_NUMBER]"), ("Reference:", "[CONTRACT_NUMBER]-[CLAIM_NUMBER]")])
    d.heading("WHAT HAPPENS NEXT")
    d.box("[SELECT: If you do not intend to pay this claim in full, you must provide a payment schedule stating the amount you propose to pay and your reasons for paying less, within the time set by the security of payment act or the contract, whichever is earlier. / Delete this paragraph if your state's notice to a home owner is attached instead.]")
    d.para("Supporting documents attached: [SELECT: progress photos / site diary extracts / signed variations / inspection certificates / supporting statement (NSW head contractors)]")
    d.signatures(["CLAIMANT"])
    return d


def payment_schedule() -> Doc:
    d = Doc("PAYMENT SCHEDULE")
    d.para("This is a payment schedule given under the [SOPA_ACT] in response to the payment claim identified below.", bold=True)
    d.info([("Schedule Date:", "[DATE]"), ("Project:", "[PROJECT_ADDRESS]"),
            ("Respondent:", "[BUSINESS_NAME]"), ("Claimant:", "[SUBBIE_NAME]"),
            ("Claimant ABN:", "[SUBBIE_ABN]"), ("Contract / Order:", "[CONTRACT_NUMBER]"),
            ("Claim Reference:", "[CLAIM_REF]"), ("Claim Received:", "[DD/MM/YYYY]")])
    d.heading("SCHEDULED AMOUNT")
    d.lines(["Item", "Amount Claimed", "Amount Scheduled", "Difference", "Reason for paying less"], widths=[2.4, 2.8, 2.8, 2.6, 6.4], rows=
            [["", "$", "$", "$", ""]] * 4)
    d.totals(["Total Claimed (excl. GST)", "Total Scheduled (excl. GST)", "GST (10%) on Scheduled Amount",
              "SCHEDULED AMOUNT (incl. GST)"])
    d.heading("REASONS")
    d.para("Every reason for paying less than the amount claimed must be set out here. Reasons left out may not be "
           "able to be relied on later, so be complete.", italic=True)
    d.box("[Set out each reason for withholding payment, by item, with the contract clause, back charge notice or defect it relies on.]")
    d.para("The scheduled amount will be paid by [DD/MM/YYYY].")
    d.signatures(["RESPONDENT"])
    return d


def tax_invoice() -> Doc:
    d = Doc("TAX INVOICE")
    d.info([("Invoice No:", "[INVOICE_NUMBER]"), ("Invoice Date:", "[DATE]"),
            ("Bill To:", "[CLIENT_NAME]"), ("Due Date:", "[DD/MM/YYYY]"),
            ("Client Address:", "[CLIENT_ADDRESS]"), ("Job / Order No:", "[CONTRACT_NUMBER]"),
            ("Site:", "[PROJECT_ADDRESS]"), ("Quote Ref:", "[QUOTE_NUMBER]")])
    d.lines(["Description", "Qty", "Unit", "Rate (excl. GST)", "Amount (excl. GST)"], widths=[7.4, 1.6, 1.6, 3.2, 3.2], rows=
            [["", "", "", "$", "$"], ["", "", "", "$", "$"], ["", "", "", "$", "$"], ["", "", "", "$", "$"]])
    d.totals(["Subtotal (excl. GST)", "GST (10%)", "TOTAL (incl. GST)"])
    d.heading("PAYMENT DETAILS")
    d.info([("Account Name:", "[ACCOUNT_NAME]"), ("BSB:", "[BSB]"),
            ("Account Number:", "[ACCOUNT_NUMBER]"), ("Reference:", "[INVOICE_NUMBER]")])
    d.para("[SELECT: Payment terms: 7 / 14 / 30 days from the invoice date. / Payment is due as set out in our agreement.]")
    d.para("[SELECT: This is a payment claim made under the security of payment act (name the Act). / Delete this line if you are not claiming under the security of payment act.]")
    d.para("Thank you for your business.")
    return d


def trade_quote() -> Doc:
    d = Doc("QUOTATION")
    d.info([("Quote No:", "[QUOTE_NUMBER]"), ("Quote Date:", "[DATE]"),
            ("Prepared For:", "[CLIENT_NAME]"), ("Valid Until:", "[DD/MM/YYYY]"),
            ("Client Phone:", "[CLIENT_PHONE]"), ("Client Email:", "[CLIENT_EMAIL]"),
            ("Site:", "[PROJECT_ADDRESS]"), ("Trade:", "[TRADE]")])
    d.heading("SCOPE OF WORK")
    d.box("[Describe the work you will do, in the order you will do it, with brands, sizes and finishes where they matter.]")
    d.heading("PRICE")
    d.lines(["Item", "Description", "Amount (excl. GST)"],
            [["", "", "$"]] * 3)
    d.totals(["Subtotal (excl. GST)", "GST (10%)", "QUOTE TOTAL (incl. GST)"])
    d.heading("INCLUSIONS")
    d.box("[List what is included: materials, labour, waste removal, permits or certificates you will supply.]")
    d.heading("EXCLUSIONS")
    d.box("[List what is not included: for example making good by others, rock or hidden services, after-hours work, items the client supplies.]")
    d.heading("TERMS")
    d.para("Payment: [SELECT: deposit on acceptance, balance on completion / progress payments as listed above / full payment on completion]")
    d.para("Start: [SELECT: within 10 working days of acceptance / on a date agreed in writing]. Allow [NUMBER] working days on site, weather permitting.")
    d.para("Changes to the scope will be quoted and agreed in writing before the work is done. Prices are based on clear access "
           "and normal working hours. Check that this quote meets any state requirement for a written contract before work starts.")
    d.heading("ACCEPTANCE")
    d.para("I accept this quote and its terms, and authorise the work to proceed.")
    d.signatures(["CLIENT"])
    return d


def rfi() -> Doc:
    d = Doc("REQUEST FOR INFORMATION")
    d.info([("RFI No:", "[RFI_NUMBER]"), ("Date Raised:", "[DATE]"),
            ("Project:", "[PROJECT_ADDRESS]"), ("Contract No:", "[CONTRACT_NUMBER]"),
            ("To:", "[NAME]"), ("Response Needed By:", "[DD/MM/YYYY]"),
            ("Discipline:", "[SELECT: Architect / Engineer / Client / Certifier / Supplier]"), ("Raised By:", "[NAME]")])
    d.heading("QUESTION")
    d.box("[State the question clearly, one issue per RFI. Say what you have found on site or in the documents and what you need to know.]")
    d.heading("REFERENCES")
    d.lines(["Drawing / Document", "Revision", "Detail or Clause"], widths=[8, 3, 6], rows= [["", "", ""], ["", "", ""]])
    d.heading("BUILDER'S PROPOSED SOLUTION (OPTIONAL)")
    d.box("[If you have a suggested answer, describe it here so the designer can approve or reject it.]")
    d.heading("IMPACT IF NOT ANSWERED BY THE DATE ABOVE")
    d.para("☐ Delay to the program   ☐ Possible variation   ☐ Work on hold   ☐ No impact yet")
    d.heading("RESPONSE")
    d.box("[Response from the designer, engineer or client.]")
    d.para("A response that changes the scope, cost or time is a variation and will be confirmed in writing before the work proceeds.", italic=True)
    d.signatures(["RESPONDED BY"])
    return d


def meeting_minutes() -> Doc:
    d = Doc("MEETING MINUTES")
    d.info([("Meeting No:", "[MEETING_NUMBER]"), ("Date:", "[DATE]"),
            ("Project:", "[PROJECT_ADDRESS]"), ("Time:", "[TIME]"),
            ("Location:", "[LOCATION]"), ("Chaired By:", "[NAME]"),
            ("Meeting Type:", "[SELECT: Site meeting / Client meeting / Pre-start / Trade coordination / Handover]"), ("Contract No:", "[CONTRACT_NUMBER]")])
    d.heading("ATTENDEES")
    d.lines(["Name", "Company / Role", "Present / Apology"], widths=[5.5, 7.5, 4.0], rows= [["", "", ""], ["", "", ""], ["", "", ""]])
    d.heading("ITEMS DISCUSSED")
    d.lines(["Item", "Discussion", "Action", "Responsible", "Due"], widths=[1.4, 6.6, 4.0, 3.0, 2.0], rows=
            [["", "", "", "", ""]] * 3)
    d.heading("DECISIONS THAT AFFECT COST OR TIME")
    d.box("[List any decision that changes scope, cost or the program. Each one needs a variation or a delay notice in writing; these minutes are not a variation.]")
    d.heading("NEXT MEETING")
    d.info([("Date:", "[DD/MM/YYYY]"), ("Location:", "[LOCATION]")])
    d.para("Please advise any corrections to these minutes within [NUMBER] working days of issue, otherwise they will be taken as accurate.")
    return d


def suspension_notice() -> Doc:
    d = Doc("NOTICE OF INTENTION TO SUSPEND WORK")
    d.info([("Notice Date:", "[DATE]"), ("Project:", "[PROJECT_ADDRESS]"),
            ("To:", "[CLIENT_NAME]"), ("Contract No:", "[CONTRACT_NUMBER]"),
            ("Address:", "[CLIENT_ADDRESS]"), ("Delivered By:", "[SELECT: Hand / Post / Email, as the contract allows]")])
    d.para("Dear [CLIENT_NAME],")
    d.para("We give you notice that we intend to suspend work under the contract because the amount below has not been paid by its due date.")
    d.heading("AMOUNT UNPAID")
    d.lines(["Claim / Invoice", "Date Issued", "Due Date", "Amount (incl. GST)"], widths=[4.25] * 4, rows=
            [["[INVOICE_NUMBER]", "[DD/MM/YYYY]", "[DD/MM/YYYY]", "$"]])
    d.heading("BASIS FOR SUSPENSION")
    d.para("[SELECT: The contract / The security of payment act / Both the contract and the security of payment act]")
    d.para("Contract clause: [CONTRACT_CLAUSE]. Act: [SOPA_ACT].")
    d.heading("WHEN WORK WILL BE SUSPENDED")
    d.para("Unless the amount above is paid in full, we will suspend work at the end of [NUMBER] business days after this notice is given to you, on [DD/MM/YYYY].")
    d.para("If we suspend, we will claim the extra time and any costs the contract allows for the suspension and for re-starting. "
           "Work will resume within [NUMBER] business days of payment in full.")
    d.para("If you believe the amount is not owed, please contact us immediately so we can resolve this.")
    d.para("Get advice before sending this notice: the notice period, how it must be served and whether you can suspend at all depend on "
           "your contract and your state's law. Suspending without a right to do so can put you in breach.", italic=True)
    d.para("Yours faithfully,")
    d.signatures(["BUILDER"])
    return d


def breach_notice() -> Doc:
    d = Doc("NOTICE OF BREACH (NOTICE TO REMEDY)")
    d.info([("Notice Date:", "[DATE]"), ("Project:", "[PROJECT_ADDRESS]"),
            ("To:", "[CLIENT_NAME]"), ("Contract No:", "[CONTRACT_NUMBER]"),
            ("Address:", "[CLIENT_ADDRESS]"), ("Delivered By:", "[SELECT: Hand / Registered post / Email, as the contract requires]")])
    d.para("Dear [CLIENT_NAME],")
    d.para("We give you notice under clause [CONTRACT_CLAUSE] of the contract that you are in substantial breach of the contract.")
    d.heading("DETAILS OF THE BREACH")
    d.box("[Describe each breach precisely: what the contract requires, the clause, what has not been done, and the dates. For non-payment, list each claim, its date, due date and amount.]")
    d.heading("WHAT YOU MUST DO")
    d.box("[State exactly what must be done to remedy each breach, for example: pay $X (incl. GST) into the account below.]")
    d.para("You must remedy the breach within [NUMBER] [SELECT: working days / days] after you receive this notice, by [DD/MM/YYYY].")
    d.heading("IF THE BREACH IS NOT REMEDIED")
    d.para("If the breach is not remedied within that time, we may [SELECT: terminate the contract / suspend work / terminate the contract or suspend work] "
           "under clause [CONTRACT_CLAUSE], without further notice, and claim the amounts the contract allows.")
    d.para("This notice is a formal step under the contract. Check the contract's notice clause for the required period, wording and method "
           "of service, and get legal advice before sending it.", italic=True)
    d.para("Yours faithfully,")
    d.signatures(["BUILDER"])
    return d


def termination_notice() -> Doc:
    d = Doc("NOTICE OF TERMINATION")
    d.info([("Notice Date:", "[DATE]"), ("Project:", "[PROJECT_ADDRESS]"),
            ("To:", "[CLIENT_NAME]"), ("Contract No:", "[CONTRACT_NUMBER]"),
            ("Address:", "[CLIENT_ADDRESS]"), ("Delivered By:", "[SELECT: Hand / Registered post / Email, as the contract requires]")])
    d.para("Dear [CLIENT_NAME],")
    d.para("On [DD/MM/YYYY] we gave you a notice of breach under clause [CONTRACT_CLAUSE] of the contract. The breach has not been remedied "
           "within the time stated in that notice.")
    d.para("We therefore terminate the contract under clause [CONTRACT_CLAUSE], with effect from the date this notice is given to you.")
    d.heading("BREACH NOT REMEDIED")
    d.box("[Summarise the breach set out in the notice of breach and confirm it remains unremedied.]")
    d.heading("AMOUNTS WE CLAIM")
    d.lines(["Item", "Amount (incl. GST)"], widths=[11, 6], rows=
            [["Work done and not yet paid", "$"], ["Approved variations not yet paid", "$"],
             ["Other amounts the contract allows", "$"]])
    d.totals(["TOTAL CLAIMED (incl. GST)"])
    d.heading("SITE AND MATERIALS")
    d.box("[State the arrangements for securing the site, removing plant and dealing with unfixed materials, as the contract provides.]")
    d.para("Termination ends the contract and has serious legal and insurance consequences, including for home warranty cover. "
           "Do not send this notice without legal advice.", bold=True, italic=True)
    d.para("Yours faithfully,")
    d.signatures(["BUILDER"])
    return d


WORD_TEMPLATES = {
    "Payment_Claim_TEMPLATE.docx": payment_claim,
    "Payment_Schedule_TEMPLATE.docx": payment_schedule,
    "Tax_Invoice_TEMPLATE.docx": tax_invoice,
    "Trade_Quote_TEMPLATE.docx": trade_quote,
    "RFI_TEMPLATE.docx": rfi,
    "Meeting_Minutes_TEMPLATE.docx": meeting_minutes,
    "Suspension_Notice_TEMPLATE.docx": suspension_notice,
    "Breach_Notice_TEMPLATE.docx": breach_notice,
    "Termination_Notice_TEMPLATE.docx": termination_notice,
}


# ------------------------------------------------------------ Excel templates

def _font(size: float, bold: bool = True, color: str | None = None):
    from openpyxl.styles import Font
    return Font(name="Cambria", size=size, bold=bold, color=("FF" + color) if color else None)


def _xl_styles():
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    thin = Side(style="thin", color="BFBFBF")
    return {
        "title": (Font(name="Cambria", size=16, bold=True, color="FF" + WHITE), PatternFill("solid", fgColor="FF" + NAVY)),
        "head": (Font(name="Cambria", size=10, bold=True, color="FF" + WHITE), PatternFill("solid", fgColor="FF" + NAVY)),
        "label": (Font(name="Cambria", size=10, bold=True), PatternFill("solid", fgColor="FF" + GREY)),
        "border": Border(left=thin, right=thin, top=thin, bottom=thin),
        "wrap": Alignment(wrap_text=True, vertical="top"),
    }


def _setup(wb, labels: list[str]):
    st = _xl_styles()
    ws = wb.active
    ws.title = "Setup"
    ws["A1"] = "PROJECT SETUP"
    ws["A1"].font, ws["A1"].fill = _font(12, color=WHITE), st["title"][1]
    for i, label in enumerate(labels, start=3):
        c = ws.cell(row=i, column=1, value=label)
        c.font, c.fill, c.border = st["label"][0], st["label"][1], st["border"]
        ws.cell(row=i, column=2).border = st["border"]
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 24, 40
    return {label: f"Setup!$B${i}" for i, label in enumerate(labels, start=3)}


def _sheet_header(ws, title: str, info: list[tuple[str, str]], headers: list[str], widths: list[int], row: int = 4):
    st = _xl_styles()
    ws["A1"] = title
    ws["A1"].font, ws["A1"].fill = st["title"]
    for j, (label, ref) in enumerate(info):
        col = 1 + 3 * j
        ws.cell(row=2, column=col, value=label).font = st["label"][0]
        ws.cell(row=2, column=col + 1, value=f"={ref}")
    for j, (h, w) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(row=row, column=j, value=h)
        c.font, c.fill, c.border, c.alignment = st["head"][0], st["head"][1], st["border"], st["wrap"]
        ws.column_dimensions[c.column_letter].width = w
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def _instructions(wb, steps: list[str]):
    st = _xl_styles()
    ws = wb.create_sheet("Instructions")
    ws["A1"] = "HOW TO USE THIS WORKBOOK"
    ws["A1"].font, ws["A1"].fill = _font(12, color=WHITE), st["title"][1]
    for i, step in enumerate(steps, start=3):
        ws.cell(row=i, column=1, value=f"STEP {i - 2}:").font = _font(10, color=NAVY)
        ws.cell(row=i, column=2, value=step).alignment = st["wrap"]
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 12, 90


def construction_program(path: Path) -> None:
    import openpyxl
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import Alignment, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    st = _xl_styles()
    wb = openpyxl.Workbook()
    refs = _setup(wb, ["Business Name:", "Project Name:", "Project Address:", "Client Name:",
                       "Contract Number:", "Start Date:", "Completion Date:", "Site Supervisor:"])
    ws = wb.create_sheet("Program")
    weeks = 26
    headers = ["ID", "Task", "Trade", "Start", "Duration (working days)", "Finish", "Predecessor ID", "% Complete", "Notes"]
    _sheet_header(ws, "CONSTRUCTION PROGRAM",
                  [("Project:", refs["Project Name:"]), ("Contract completion:", refs["Completion Date:"])],
                  headers + [""] * weeks, [5, 32, 16, 12, 12, 12, 12, 10, 24] + [4] * weeks)
    # Week-commencing dates across the top of the bar chart.
    first_week = 10
    for w in range(weeks):
        col = first_week + w
        c = ws.cell(row=4, column=col)
        start = refs["Start Date:"]
        prev = ws.cell(row=4, column=col - 1).coordinate
        c.value = f'=IF({start}="","",{start}-WEEKDAY({start},3))' if w == 0 else f'=IF({prev}="","",{prev}+7)'
        c.number_format = "dd/mm"
        c.alignment = Alignment(text_rotation=90)
    tasks = ["Site establishment", "Set out and excavation", "Footings and slab", "Frame", "Roof cover",
             "Windows and external doors (lock-up)", "Rough-in: plumbing, electrical, mechanical", "Insulation",
             "Plasterboard", "Waterproofing", "Fix-out: joinery, doors, trims", "Tiling", "Painting",
             "Fit-off: plumbing, electrical", "External works and landscaping", "Final clean", "Practical completion inspection"]
    first, last = 5, 5 + 59
    for i in range(first, last + 1):
        n = i - first
        ws.cell(row=i, column=1, value=n + 1)
        if n < len(tasks):
            ws.cell(row=i, column=2, value=tasks[n])
        # Start: after the predecessor's finish if there is one, otherwise typed (or the job start for task 1).
        ws.cell(row=i, column=4, value=(
            f'=IF(G{i}<>"",WORKDAY(INDEX($F${first}:$F${last},MATCH(G{i},$A${first}:$A${last},0)),1,Holidays!$A$4:$A$60),'
            f'IF(A{i}=1,{refs["Start Date:"]},""))'))
        ws.cell(row=i, column=6, value=f'=IF(OR(D{i}="",E{i}=""),"",WORKDAY(D{i},E{i}-1,Holidays!$A$4:$A$60))')
        for col in (4, 6):
            ws.cell(row=i, column=col).number_format = "dd/mm/yyyy"
        ws.cell(row=i, column=8).number_format = "0%"
        for col in range(1, 10):
            ws.cell(row=i, column=col).border = st["border"]
        if n and n < len(tasks):
            ws.cell(row=i, column=7, value=n)  # each sample task follows the one before
    top_left = ws.cell(row=first, column=first_week).coordinate
    bar_range = f"{top_left}:{ws.cell(row=last, column=first_week + weeks - 1).coordinate}"
    col_letter = ws.cell(row=4, column=first_week).column_letter
    rule = f'AND($D{first}<>"",$F{first}<>"",{col_letter}$4+6>=$D{first},{col_letter}$4<=$F{first})'
    ws.conditional_formatting.add(bar_range, FormulaRule(formula=[rule], fill=PatternFill("solid", fgColor="FF" + NAVY)))
    dv = DataValidation(type="decimal", operator="between", formula1="0", formula2="1")
    ws.add_data_validation(dv)
    dv.add(f"H{first}:H{last}")

    hol = wb.create_sheet("Holidays")
    hol["A1"] = "NON-WORKING DAYS"
    hol["A1"].font, hol["A1"].fill = _font(12, color=WHITE), st["title"][1]
    hol["A3"], hol["B3"] = "Date", "Reason"
    for c in (hol["A3"], hol["B3"]):
        c.font, c.fill = st["label"]
    hol.column_dimensions["A"].width, hol.column_dimensions["B"].width = 14, 40
    for r in range(4, 61):
        hol.cell(row=r, column=1).number_format = "dd/mm/yyyy"

    _instructions(wb, [
        "Fill in Setup. The Start Date is the first day on site.",
        "On Holidays, list public holidays, the industry shutdown (RDOs if you take them) and any other non-working days for the job's state.",
        "On Program, list tasks in order. Give each a duration in working days. Put the ID of the task it follows in Predecessor ID and the start and finish dates calculate themselves; leave Predecessor ID blank and type a Start date for a task that doesn't follow another.",
        "The bars show each task against week-commencing dates. Update % Complete each week.",
        "If the program slips past the contract completion date, issue a Delay Notification for any delay you are entitled to an extension of time for.",
    ])
    wb.save(path)


def timesheet_docket(path: Path) -> None:
    import openpyxl
    from openpyxl.worksheet.datavalidation import DataValidation

    st = _xl_styles()
    wb = openpyxl.Workbook()
    refs = _setup(wb, ["Business Name:", "Project Name:", "Project Address:", "Client Name:",
                       "Contract Number:", "Default Labour Rate (excl GST):"])
    ws = wb.create_sheet("Dockets")
    headers = ["Date", "Docket No", "Worker", "Trade / Role", "Start", "Finish", "Break (min)", "Hours",
               "Rate (excl GST)", "Labour (excl GST)", "Materials / Plant (excl GST)", "Total (excl GST)",
               "Work Done", "Charge To (Contract / VAR No)", "Signed Off By"]
    _sheet_header(ws, "TIMESHEETS AND DAY WORK DOCKETS",
                  [("Project:", refs["Project Name:"]), ("Client:", refs["Client Name:"])],
                  headers, [12, 10, 18, 16, 8, 8, 9, 8, 11, 13, 13, 13, 36, 16, 16])
    first, last = 5, 204
    for i in range(first, last + 1):
        ws.cell(row=i, column=1).number_format = "dd/mm/yyyy"
        for col in (5, 6):
            ws.cell(row=i, column=col).number_format = "hh:mm"
        ws.cell(row=i, column=8, value=f'=IF(OR(E{i}="",F{i}=""),"",ROUND(MOD(F{i}-E{i},1)*24-N(G{i})/60,2))')
        ws.cell(row=i, column=9, value=f"={refs['Default Labour Rate (excl GST):']}")
        ws.cell(row=i, column=10, value=f'=IF(H{i}="","",ROUND(H{i}*I{i},2))')
        ws.cell(row=i, column=12, value=f'=IF(AND(J{i}="",K{i}=""),"",N(J{i})+N(K{i}))')
        for col in (9, 10, 11, 12):
            ws.cell(row=i, column=col).number_format = '"$"#,##0.00'
        for col in range(1, len(headers) + 1):
            ws.cell(row=i, column=col).border = st["border"]
    dv = DataValidation(type="time")
    ws.add_data_validation(dv)
    dv.add(f"E{first}:F{last}")

    summ = wb.create_sheet("Summary")
    summ["A1"] = "SUMMARY BY CHARGE"
    summ["A1"].font, summ["A1"].fill = _font(12, color=WHITE), st["title"][1]
    for j, h in enumerate(["Charge To", "Hours", "Labour (excl GST)", "Materials / Plant (excl GST)", "Total (excl GST)", "GST", "Total (incl GST)"], 1):
        c = summ.cell(row=3, column=j, value=h)
        c.font, c.fill, c.border = st["head"][0], st["head"][1], st["border"]
        summ.column_dimensions[c.column_letter].width = 18
    rng = lambda col: f"Dockets!${col}${first}:${col}${last}"
    for r in range(4, 24):
        summ.cell(row=r, column=2, value=f'=IF(A{r}="","",SUMIF({rng("N")},A{r},{rng("H")}))')
        summ.cell(row=r, column=3, value=f'=IF(A{r}="","",SUMIF({rng("N")},A{r},{rng("J")}))')
        summ.cell(row=r, column=4, value=f'=IF(A{r}="","",SUMIF({rng("N")},A{r},{rng("K")}))')
        summ.cell(row=r, column=5, value=f'=IF(A{r}="","",C{r}+D{r})')
        summ.cell(row=r, column=6, value=f'=IF(A{r}="","",ROUND(E{r}*0.1,2))')
        summ.cell(row=r, column=7, value=f'=IF(A{r}="","",E{r}+F{r})')
        for col in range(3, 8):
            summ.cell(row=r, column=col).number_format = '"$"#,##0.00'
        for col in range(1, 8):
            summ.cell(row=r, column=col).border = st["border"]
    summ.cell(row=25, column=1, value="All dockets").font = st["label"][0]
    summ.cell(row=25, column=2, value=f"=SUM({rng('H')})")
    summ.cell(row=25, column=3, value=f"=SUM({rng('J')})")
    summ.cell(row=25, column=4, value=f"=SUM({rng('K')})")
    summ.cell(row=25, column=5, value="=C25+D25")
    summ.cell(row=25, column=6, value="=ROUND(E25*0.1,2)")
    summ.cell(row=25, column=7, value="=E25+F25")
    for col in range(3, 8):
        summ.cell(row=25, column=col).number_format = '"$"#,##0.00'

    _instructions(wb, [
        "Fill in Setup, including your default labour rate (ex GST). Override the rate on any line by typing over it.",
        "Record one line per worker per day: start and finish times (hh:mm) and unpaid break minutes. Hours and labour calculate themselves.",
        "Add materials or plant used for day work, ex GST.",
        "In Charge To, put the contract number for contract work, or the variation number (VAR-001) for day work the client will pay for.",
        "Get the client or supervisor to sign off each day work docket the day it happens. Unsigned dockets are hard to get paid.",
        "On Summary, type each Charge To value once to total hours and cost; use the totals in your variation or invoice.",
    ])
    wb.save(path)


EXCEL_TEMPLATES = {
    "Construction_Program_TEMPLATE.xlsx": construction_program,
    "Timesheet_Docket_TEMPLATE.xlsx": timesheet_docket,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="rebuild templates that already exist")
    args = parser.parse_args()
    for name, build in WORD_TEMPLATES.items():
        path = WORD / name
        if path.exists() and not args.force:
            print(f"kept   {path.relative_to(ROOT)}")
            continue
        build().save(path)
        print(f"built  {path.relative_to(ROOT)}")
    for name, build in EXCEL_TEMPLATES.items():
        path = EXCEL / name
        if path.exists() and not args.force:
            print(f"kept   {path.relative_to(ROOT)}")
            continue
        build(path)
        print(f"built  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
