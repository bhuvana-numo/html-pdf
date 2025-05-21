from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import tempfile
import weasyprint
import re
import os

app = FastAPI()

HTML_FILE_PATH = "invoice-template.html"  

def inject_margin_reset(html: str) -> str:
    normalize_css = """
    <style>
        @page { margin: 0; }
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            font-size: 12px;
        }
        html {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        td.left-align {
            text-align: left;
        }
        td.right-align {
            text-align: right;
        }
    </style>
    """


    html = re.sub(r'\s*align="right"', ' class="right-align"', html, flags=re.IGNORECASE)
    html = re.sub(r'\s*align="left"', ' class="left-align"', html, flags=re.IGNORECASE)

    if "<head>" in html:
        return re.sub(r"<head>", f"<head>{normalize_css}", html, count=1, flags=re.IGNORECASE)
    elif "<html>" in html:
        return re.sub(r"<html>", f"<html><head>{normalize_css}</head>", html, count=1, flags=re.IGNORECASE)
    else:
        return f"<head>{normalize_css}</head>{html}"

@app.get("/generate-pdf")
async def generate_pdf():
    if not os.path.exists(HTML_FILE_PATH):
        raise HTTPException(status_code=404, detail="HTML template file not found.")

    try:
   
        with open(HTML_FILE_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()

        html_with_margins = inject_margin_reset(html_content)

        pdf = weasyprint.HTML(string=html_with_margins).write_pdf()


        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf)
            temp_pdf_path = temp_pdf.name

        return FileResponse(temp_pdf_path, media_type="application/pdf", filename="invoice.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
