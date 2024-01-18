from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_pdf_report(file_path, report_content):
    # Create a PDF document
    pdf_canvas = canvas.Canvas(file_path, pagesize=letter)

    # Set font and size
    pdf_canvas.setFont("Helvetica", 12)

    # Add content to the PDF
    pdf_canvas.drawString(100, 700, "Report Title")
    pdf_canvas.drawString(100, 680, "Date: 2023-12-03")

    # Add dynamic content from your report
    y_position = 660
    for line in report_content:
        pdf_canvas.drawString(100, y_position, line)
        y_position -= 15

    # Save the PDF
    pdf_canvas.save()


# Example usage
report_content = [
    "This is a sample report.",
    "Line 2 of the report.",
    "Another line in the report.",
    "You can add more content as needed.",
]

generate_pdf_report("example_report.pdf", report_content)
