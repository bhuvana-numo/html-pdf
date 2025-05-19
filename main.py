from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import weasyprint
import re

app = FastAPI()

class HTMLContent(BaseModel):
    html_content: str

def inject_margin_reset(html: str) -> str:
    normalize_css = """
    <style>
        @page { margin: 0; }
        body {
            margin: 0;
            padding: 0;
            font-family: sans-serif;
            font-size: 12px; /* Adjust this default if needed */
        }
        html {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
    </style>
    """
    if "<head>" in html:
        return re.sub(r"<head>", f"<head>{normalize_css}", html, count=1, flags=re.IGNORECASE)
    elif "<html>" in html:
        return re.sub(r"<html>", f"<html><head>{normalize_css}</head>", html, count=1, flags=re.IGNORECASE)
    else:
        return f"<head>{normalize_css}</head>{html}"


@app.post("/generate-pdf")
async def generate_pdf(data: HTMLContent):
    try:
        html_with_margins = inject_margin_reset(data.html_content)
        pdf = weasyprint.HTML(string=html_with_margins).write_pdf()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf)
            temp_pdf_path = temp_pdf.name

        return FileResponse(temp_pdf_path, media_type="application/pdf", filename="invoiceTwo.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
