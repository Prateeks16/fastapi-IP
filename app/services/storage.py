import os, uuid

UPLOAD_DIR = "uploads"

def save_upload_file(file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())
    return filepath
