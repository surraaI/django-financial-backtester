import base64
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

def generate_pdf_report(stock_symbol, metrics, image_base64):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Title and metrics
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, f"Stock Price Report for {stock_symbol}")
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"Total Return: {metrics['total_return']}%")
    c.drawString(100, 680, f"Max Drawdown: {metrics['max_drawdown']}%")
    c.drawString(100, 660, f"Number of Trades: {metrics['number_of_trades']}")

    # Embed the plot image
    if image_base64:
        try:
            image_data = base64.b64decode(image_base64)
            image = ImageReader(io.BytesIO(image_data))
            c.drawImage(image, 100, 400, width=400, height=200)
        except Exception as e:
            print(f"Error embedding image: {e}")

    c.showPage()
    c.save()

    # Create FileResponse with the correct headers for PDF
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"{stock_symbol}_stock_report.pdf", content_type='application/pdf')
