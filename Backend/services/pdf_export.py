from fastapi.responses import FileResponse
import os

def export_pdf(path: str):
    if not os.path.exists(path):
        return {"error": "File not found"}

    filename = os.path.basename(path)

    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/pdf"
    )
