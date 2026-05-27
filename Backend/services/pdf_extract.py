import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def extract_text_objects(pdf_path):
    doc = fitz.open(pdf_path)
    text_objects = []

    for page_number in range(len(doc)):
        page = doc[page_number]

        # ----------------------------------------------------
        # 1. TRY NORMAL TEXT EXTRACTION (PyMuPDF structured)
        # ----------------------------------------------------
        blocks = page.get_text("dict")["blocks"]
        normal_text_found = False

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                if "spans" not in line:
                    continue

                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    if not text:
                        continue  # skip empty spans

                    x0, y0, x1, y1 = span["bbox"]

                    text_objects.append({
                        "page": page_number + 1,
                        "text": text,
                        "x": float(x0),
                        "y": float(y0),
                        "width": float(x1 - x0),
                        "height": float(y1 - y0)
                    })

                    normal_text_found = True

        # If real text was found → skip OCR
        if normal_text_found:
            continue

        # ----------------------------------------------------
        # 2. OCR FALLBACK (for scanned PDFs)
        # ----------------------------------------------------
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        for i in range(len(ocr_data["text"])):
            text = ocr_data["text"][i].strip()
            if not text:
                continue

            x = ocr_data["left"][i]
            y = ocr_data["top"][i]
            w = ocr_data["width"][i]
            h = ocr_data["height"][i]

            text_objects.append({
                "page": page_number + 1,
                "text": text,
                "x": float(x),
                "y": float(y),
                "width": float(w),
                "height": float(h)
            })

    doc.close()
    return text_objects
