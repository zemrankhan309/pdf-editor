import fitz  # PyMuPDF

def apply_edits(edits, pdf_path, output_path):
    doc = fitz.open(pdf_path)

    for edit in edits:
        page_index = edit["page"] - 1
        page = doc[page_index]

        x = edit["x"]
        y = edit["y"]
        text = edit["text"]

        # Remove old text by drawing a white rectangle
        rect = fitz.Rect(x, y, x + 200, y + 20)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        # Insert new text
        page.insert_text((x, y), text, fontsize=12, color=(0, 0, 0))

    doc.save(output_path)
    doc.close()
