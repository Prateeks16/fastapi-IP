from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
import io

def extract_text_from_file(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts).strip()

    else:
        # treat as plain text
        return data.decode("utf-8", errors="ignore").strip()
