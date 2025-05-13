from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import tempfile
import weasyprint

app = FastAPI()

class HTMLContent(BaseModel):
    html_content: str

@app.post("/generate-pdf")
async def generate_pdf(data: HTMLContent):
    try:
        pdf = weasyprint.HTML(string=data.html_content).write_pdf()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf)
            temp_pdf_path = temp_pdf.name

        return FileResponse(temp_pdf_path, media_type="application/pdf", filename="invoiceTwo.pdf")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))