from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import tempfile

from services.pdf_extract import extract_text_objects
from services.pdf_edit import apply_edits
from services.pdf_export import export_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "pdf_editor_workspace")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            buffer.write(chunk)

    text_objects = extract_text_objects(file_path)
    return {"file_path": file_path, "text_objects": text_objects}


@app.post("/edit")
async def edit_pdf(payload: dict):
    file_path = payload["file_path"]
    edits = payload.get("edits", [])
    
    edited_pdf_path = file_path.replace(".pdf", "_edited.pdf")
    
    # FIXED: Arguments match pdf_edit.py parameter structure perfectly
    apply_edits(edits, file_path, edited_pdf_path)
    
    return {"edited_pdf_path": edited_pdf_path}


@app.get("/export")
def export(path: str):
    return export_pdf(path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)