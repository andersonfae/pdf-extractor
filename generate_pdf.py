from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 12)
    text.textLine("Invoice Number: 123456")
    text.textLine("Date: 2023-03-15")
    text.textLine("Total: $1234.56")
    c.drawText(text)
    c.showPage()
    c.save()

if __name__ == "__main__":
    create_sample_pdf("sample_invoice.pdf")
    print("PDF 'sample_invoice.pdf' criado com sucesso!")
