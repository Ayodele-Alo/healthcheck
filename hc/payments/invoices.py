# coding: utf-8

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


W, H = A4


def f(dt):
    return dt.strftime("%b. %-d, %Y")


class PdfInvoice(canvas.Canvas):
    def __init__(self, fileobj):
        super(PdfInvoice, self).__init__(fileobj, pagesize=A4,
                                         pageCompression=0)
        self.head_y = H - inch * 0.5

    def linefeed(self):
        self.head_y -= inch / 8

    def print(self, s, align="left", size=10, bold=False):
        self.head_y -= inch / 24
        self.linefeed()
        self.setFont("Helvetica-Bold" if bold else "Helvetica", size)

        if align == "left":
            self.drawString(inch * 0.5, self.head_y, s)
        elif align == "right":
            self.drawRightString(W - inch * 0.5, self.head_y, s)
        elif align == "center":
            self.drawCentredString(W / 2, self.head_y, s)

        self.head_y -= inch / 24

    def hr(self):
        self.setLineWidth(inch / 72 / 8)
        self.line(inch * 0.5, self.head_y, W - inch * 0.5, self.head_y)

    def print_row(self, items, align="left", bold=False, size=10):
        self.head_y -= inch / 8
        self.linefeed()

        self.setFont("Helvetica-Bold" if bold else "Helvetica", size)

        self.drawString(inch * 0.5, self.head_y, items[0])
        self.drawString(inch * 3.5, self.head_y, items[1])
        self.drawString(inch * 5.5, self.head_y, items[2])
        self.drawRightString(W - inch * 0.5, self.head_y, items[3])

        self.head_y -= inch / 8

    def render(self, tx, bill_to):
        width, height = A4
        invoice_id = "MS-HC-%s" % tx.id.upper()
        self.setTitle(invoice_id)

        self.print("SIA Monkey See Monkey Do", size=16)
        self.linefeed()
        self.print("Gaujas iela 4-2")
        self.print("Valmiera, LV-4201, Latvia")
        self.print("VAT: LV44103100701")
        self.linefeed()

        created = f(tx.created_at)
        self.print("Date Issued: %s" % created, align="right")
        self.print("Invoice Id: %s" % invoice_id, align="right")
        self.linefeed()

        self.hr()
        self.print_row(["Description", "Start", "End", tx.currency_iso_code],
                       bold=True)
        self.hr()
        start = f(tx.subscription_details.billing_period_start_date)
        end = f(tx.subscription_details.billing_period_end_date)
        if tx.currency_iso_code == "USD":
            amount = "$%s" % tx.amount
        elif tx.currency_iso_code == "EUR":
            amount = "€%s" % tx.amount
        else:
            amount = "%s %s" % (tx.currency_iso_code, tx.amount)

        self.print_row(["healthchecks.io paid plan", start, end, amount])

        self.hr()
        self.print_row(["", "", "", "Total: %s" % amount], bold=True)
        self.linefeed()

        self.print("Bill to:", bold=True)
        for s in bill_to.split("\n"):
            self.print(s.strip())

        self.linefeed()
        self.print("If you have a credit card on file it will be "
                   "automatically charged within 24 hours.", align="center")

        self.showPage()
        self.save()