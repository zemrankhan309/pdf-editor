import fitz  # PyMuPDF

def apply_edits(edits, pdf_path, output_path):
    doc = fitz.open(pdf_path)

    for edit in edits:
        page_index = edit["page"] - 1
        page = doc[page_index]

        x = edit["x"]
        y = edit["y"]
        w = edit["width"]
        h = edit["height"]
        size = edit["size"]
        text = edit["text"]

        # 1. Create a white masking box over the old text (plus 1px margin padding)
        rect = fitz.Rect(x - 1, y - 1, x + w + 1, y + h + 1)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        # 2. Use insert_text with a baseline height shift.
        # This guarantees PyMuPDF will NEVER drop text due to bounding box constraints!
        baseline_y = y + h - (h * 0.15)
        
        page.insert_text(
            fitz.Point(x, baseline_y), 
            text, 
            fontsize=size, 
            fontname="helv", 
            color=(0, 0, 0)
        )

    # Force a clean structural save rewrite
    doc.save(output_path, garbage=3, deflate=True)
    doc.close()