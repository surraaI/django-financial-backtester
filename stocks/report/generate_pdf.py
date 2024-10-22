import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_pdf_report(stock_symbol, metrics, image_base64):
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, f"Stock Price Report for {stock_symbol}")

        # Metrics
        c.setFont("Helvetica", 12)
        c.drawString(100, 700, f"Total Return: {metrics['total_return']}%")
        c.drawString(100, 680, f"Max Drawdown: {metrics['max_drawdown']}%")
        c.drawString(100, 660, f"Number of Trades: {metrics['number_of_trades']}")

        # Embed the image
        try:
            image_data = base64.b64decode(image_base64)
            image = ImageReader(io.BytesIO(image_data))
            c.drawImage(image, 100, 400, width=400, height=200)
        except Exception as image_error:
            print(f"Error embedding image: {str(image_error)}")
            raise image_error

        # Finalize the PDF
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise e
