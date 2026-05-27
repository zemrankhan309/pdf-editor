from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import tempfile

from services.pdf_extract import extract_text_objects
from services.pdf_edit import apply_edits

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
    apply_edits(edits, file_path, edited_pdf_path)
    
    return {"edited_pdf_path": edited_pdf_path}


# FIXED: Explicitly stream the edited file directly back to the user's browser
@app.get("/export")
def export(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Edited file not found.")
    return FileResponse(path, media_type="application/pdf", filename="edited_document.pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)