# Technical Documentation: Secure Local PDF Layout Editor (`code_explanation.md`)

This file provides a comprehensive architectural and line-by-line technical explanation of the local, privacy-focused PDF layout editor application.

---

## 1. High-Level Architectural Overview

The core objective of this application is to allow complete in-memory textual modification of structural layers inside a PDF document without writing unencrypted intermediate scratch files to the local disk workspace. 

### Data Flow Pipeline
1. **Ingestion:** Raw bytes are buffered into memory via `st.file_uploader`.
2. **Structural Decomposition:** The layout topology is parsed hierarchically from **Pages -> Blocks -> Lines -> Spans** using PyMuPDF (`fitz`).
3. **State Retention:** Coordinate boundaries (`bbox`), typography flags, and textual content values are synchronized in persistent arrays utilizing `st.session_state`.
4. **Reactive Multi-Pane UI:** The DOM split renders an asynchronous 150 DPI raster image canvas on the left, side-by-side with a cellular text modification matrix (`st.data_editor`) on the right.
5. **Vector Reconstruction Engine:** Modified cells trigger a destructive localized vector layer masking pass (`draw_rect`) paired with clean coordinate-mapped text overwriting (`insert_text`) using core standard fallback tracking metrics.

---

## 2. Line-by-Line Code Decomposition

### App Layout & Memory Initialization
```python
st.set_page_config(
    page_title="Secure Local PDF Layout Editor",
    page_icon="📄",
    layout="wide"
)
```
* Configures the layout viewport parameters. The `layout="wide"` directive is mandatory to handle side-by-side positioning of full-scale page previews alongside an active text modifications grid without crushing visual fidelity.

```python
if "pdf_doc" not in st.session_state:
    st.session_state.pdf_doc = None
...
```
* Since Streamlit processes script evaluation imperatively from top-to-bottom on every single interactive element adjustment, initializing state arrays prevents runtime memory purges when switching pages or typing in text data editors.

---

### Text Extraction & Topology Mapping Engine
```python
if uploaded_file:
    if st.session_state.file_name != uploaded_file.name:
        file_bytes = uploaded_file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
```
* Restricts resource-heavy file reading loops. Raw bytes are handed over directly to PyMuPDF's in-memory byte streams via `stream=file_bytes` to protect high-confidentiality documents from being cached locally on storage drives.

```python
blocks = page.get_text("dict")["blocks"]
for block in blocks:
    if "lines" not in block: continue
    for line in block["lines"]:
        for span in line["spans"]:
```
* Navigates structural geometry layers. A **Span** represents a uniform grouping of continuous characters possessing identical styling metrics (exact size, specific color vectors, and individual font variations).

```python
font_name = span.get("font", "").lower()
flags = span.get("flags", 0)
is_bold = "bold" in font_name or "black" in font_name or "heavy" in font_name or bool(flags & 16)
is_italic = "italic" in font_name or "oblique" in font_name or bool(flags & 2)
```
* Inspects internal layout metadata definitions to determine visual typographic hierarchy. It checks for specific descriptive name tokens (`"bold"`, `"heavy"`) alongside low-level binary bitwise operations on font mask property flags (bit `16` marks boldface variants; bit `2` marks slant style adjustments).

---

### Synchronized Split Workspace Layout
```python
col_preview, col_editor = st.columns([1, 1.2])
```
* Divides the client screen into a dual-action interface pane environment.

```python
page_obj = st.session_state.pdf_doc[selected_page - 1]
pix = page_obj.get_pixmap(dpi=150)
img_data = pix.tobytes("png")
preview_image = Image.open(io.BytesIO(img_data))
st.image(preview_image, use_container_width=True)
```
* **Visualizing Node Positioning:** Creates a crisp 150 DPI pixelated snapshot array of the selected vector map target, allowing cross-comparisons against data cell modifications instantly.

```python
updated_grid_data = st.data_editor(
    current_page_df,
    hide_index=True,
    disabled=["ID", "Page", "Font Style", "Size (pt)"],
    use_container_width=True,
    key=f"grid_page_{selected_page}"
)
```
* **The Interface Mod Matrix:** Employs an interactive UI spreadsheet matrix. The structural control items (`ID`, `Page`, `Size`) are explicitly declared `disabled` to safeguard raw layout coordinates from unintended user structural deletions.

---

### Masking & Compilation Engine
```python
mask_rect = fitz.Rect(orig_item["x0"] - 0.5, orig_item["y0"] - 0.5, orig_item["x1"] + 0.5, orig_item["y1"] + 0.5)
target_page.draw_rect(mask_rect, color=(1, 1, 1), fill=(1, 1, 1))
```
* **The Visual Eraser Mask:** Native PDF formats do not have a standard "character delete" command mechanism. To clean historical character placements, a custom vector shape box is rendered precisely on top of the original element coordinates (`x0`, `y0`, `x1`, `y1`), filled completely with pure RGB white `(1, 1, 1)`.

```python
font_track = "Helvetica"
if orig_item["is_bold"] and orig_item["is_italic"]: font_track = "Helvetica-BoldOblique"
elif orig_item["is_bold"]: font_track = "Helvetica-Bold"
elif orig_item["is_italic"]: font_track = "Helvetica-Oblique"
```
* Maps unique internal system names back to universally recognized core standard PDF tracking names. This avoids font extraction failures and compilation crashes when exporting files.

```python
baseline_y = orig_item["y0"] + orig_item["height"] - (orig_item["height"] * 0.15)
```
* **Baseline Adjustment Alignment Logic:** Bounding boxes (`bbox`) track objects starting from their top-left boundary, but the system `insert_text` method writes data from the string's text baseline (the lower boundary line). Stripping `15%` off the calculated height prevents font vertical shifting and coordinate drift during processing.

```python
output_doc.save(pdf_output_buffer, garbage=3, deflate=True)
```
* Finalizes binary layout generation. Setting `garbage=3` strips out redundant structures, cleans unreferenced metadata layers, and applies standard file size deflation schemes before allowing user downloads via `st.download_button`.
```
```