import fitz  # PyMuPDF

def apply_edits(edits, pdf_path, output_path):
    doc = fitz.open(pdf_path)

    for edit in edits:
        if not edit:
            continue
            
        page_index = edit["page"] - 1
        page = doc[page_index]

        x = edit["x"]
        y = edit["y"]
        text = edit["text"] # FIXED: Matches key defined in app.js
        w = edit.get("width", 100)
        h = edit.get("height", 12)

        # FIXED: Whitespace block covers old text using its exact original size
        rect = fitz.Rect(x, y, x + w, y + h)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        # Re-write the updated plain text string into document coordinate stream layer
        # Typos prevention calibration offset applied to baseline height y alignment (y + h - 2)
        page.insert_text((x, y + h - 2), text, fontsize=max(h * 0.9, 9), color=(0, 0, 0))

    doc.save(output_path)
    doc.close()