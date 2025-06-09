from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
import re
import tempfile
import weasyprint

app = FastAPI()

class FillTemplateRequest(BaseModel):
    data: Dict[str, Any]
    optionalBlocks: Dict[str, Dict[str, str]] = {}

def inject_margin_reset(html: str) -> str:
    style_tag = """
    <style>
        @page { margin: 20px; }
        body { margin: 0px; font-family: Arial, sans-serif; }
        td.left-align { text-align: left; }
        td.right-align { text-align: right; }
        td.center-align { text-align: center; }
    </style>
    """
    return re.sub(r"(<head.*?>)", r"\1" + style_tag, html, flags=re.IGNORECASE)


def fill_placeholders(html: str, data: Dict[str, Any], optional_blocks: Dict[str, Dict[str, str]]) -> str:
    for key, value in data.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))

    def replace_optional(match):
        block_key = match.group(1)
        block_data = optional_blocks.get(block_key)
        if block_data:
            label = block_data.get("label", block_key)
            value = block_data.get("value", "")
            return f"<tr><td class='left-align'>&nbsp;{label}</td><td class='right-align'>{value}&nbsp;</td></tr>"
        return ""

    html = re.sub(r"{(\w+)}", replace_optional, html)
    return html

@app.post("/fill-template", response_class=FileResponse)
async def fill_template(request: FillTemplateRequest):
    try:
        with open("templates\retail_topup_transaction_slip.html", "r", encoding="utf-8") as file:
            template_html = file.read()

        # Process HTML
        html = inject_margin_reset(template_html)
        filled_html = fill_placeholders(html, request.data, request.optionalBlocks)

        # Generate PDF
        pdf_bytes = weasyprint.HTML(string=filled_html).write_pdf()

        # Save as temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name

        return FileResponse(
            temp_pdf_path,
            media_type="application/pdf",
            filename="invoice.pdf"
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))