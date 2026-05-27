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

        # 1. Create a precise white masking box matching the text dimensions
        rect = fitz.Rect(x, y, x + w, y + h)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        # 2. Textbox insertion avoids baseline shifts and stops layout overlapping!
        page.insert_textbox(
            rect, 
            text, 
            fontsize=size, 
            fontname="helv", 
            color=(0, 0, 0), 
            align=0
        )

    doc.save(output_path)
    doc.close()