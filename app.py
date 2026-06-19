import streamlit as st
import pymupdf as fitz
import pandas as pd
from PIL import Image
import io

# App Layout Configuration
st.set_page_config(
    page_title="Secure Local PDF Layout Editor",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Secure Local PDF Layout Editor")
st.markdown("Modify document text layers seamlessly while safely preserving typography parameters and bold styling records.")

# Initialize global application session memory states
if "pdf_doc" not in st.session_state:
    st.session_state.pdf_doc = None
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
if "editor_df" not in st.session_state:
    st.session_state.editor_df = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None

# Integrated Secure File Uploader Stream (Processed entirely within local RAM)
uploaded_file = st.file_uploader("Upload target PDF document", type=["pdf"])

if uploaded_file:
    # Refresh data maps only if a brand new asset stream is provided
    if st.session_state.file_name != uploaded_file.name:
        st.session_state.file_name = uploaded_file.name
        file_bytes = uploaded_file.read()
        
        # Open PDF directly from byte cache strings safely
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        st.session_state.pdf_doc = doc
        
        all_pages_items = []
        flattened_table_rows = []
        global_item_idx = 0
        
        # Traverse layout dictionary objects across document streams
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_val = span.get("text", "")
                        if not text_val.strip():
                            continue
                        
                        # Extract structural boundary limits 
                        x0, y0, x1, y1 = span["bbox"]
                        font_name = span.get("font", "").lower()
                        flags = span.get("flags", 0)
                        
                        # Parse font properties to lock down headline hierarchy weights
                        is_bold = "bold" in font_name or "black" in font_name or "heavy" in font_name or bool(flags & 16)
                        is_italic = "italic" in font_name or "oblique" in font_name or bool(flags & 2)
                        
                        style_label = "Regular"
                        if is_bold and is_italic:
                            style_label = "Bold Italic"
                        elif is_bold:
                            style_label = "Bold"
                        elif is_italic:
                            style_label = "Italic"

                        item_meta = {
                            "global_idx": global_item_idx,
                            "page": page_num + 1,
                            "text": text_val,
                            "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                            "width": x1 - x0,
                            "height": y1 - y0,
                            "size": span.get("size", 11),
                            "is_bold": is_bold,
                            "is_italic": is_italic
                        }
                        all_pages_items.append(item_meta)
                        
                        # Build layout rows for the user-facing table view
                        flattened_table_rows.append({
                            "ID": global_item_idx,
                            "Page": page_num + 1,
                            "Font Style": style_label,
                            "Size (pt)": round(span.get("size", 11), 1),
                            "Editable Text Content": text_val
                        })
                        global_item_idx += 1
                        
        st.session_state.extracted_data = all_pages_items
        st.session_state.editor_df = pd.DataFrame(flattened_table_rows)

if st.session_state.pdf_doc is not None:
    # Build clean split workspace panes
    col_preview, col_editor = st.columns([1, 1.2])
    total_pages = len(st.session_state.pdf_doc)
    
    with col_preview:
        st.subheader("Visual Document Preview")
        selected_page = st.number_input(f"Navigate Pages (1 to {total_pages})", min_value=1, max_value=total_pages, value=1, step=1)
        
        # Render clean raster image of current selection
        page_obj = st.session_state.pdf_doc[selected_page - 1]
        pix = page_obj.get_pixmap(dpi=150)
        img_data = pix.tobytes("png")
        preview_image = Image.open(io.BytesIO(img_data))
        
        st.image(preview_image, use_container_width=True, caption=f"Page {selected_page} Target Canvas")

    with col_editor:
        st.subheader("Text Layer Modifications Matrix")
        st.caption("Double-click elements inside 'Editable Text Content' to rewrite text fields safely.")
        
        # Isolate text inputs matching current canvas scope context
        current_page_df = st.session_state.editor_df[st.session_state.editor_df["Page"] == selected_page]
        
        # Render a stable Data Editor to avoid cursor jumping bugs
        updated_grid_data = st.data_editor(
            current_page_df,
            hide_index=True,
            disabled=["ID", "Page", "Font Style", "Size (pt)"],
            use_container_width=True,
            key=f"grid_page_{selected_page}"
        )
        
        # Sync changes back to active state arrays instantly
        for _, row in updated_grid_data.iterrows():
            target_id = row["ID"]
            new_text_value = row["Editable Text Content"]
            st.session_state.editor_df.loc[st.session_state.editor_df["ID"] == target_id, "Editable Text Content"] = new_text_value

        st.markdown("---")
        
        # PDF compilation handler block
        if st.button("Apply Modifications & Compile PDF Document", type="primary"):
            with st.spinner("Writing text vectors into PDF stream layers..."):
                output_doc = fitz.open()
                output_doc.insert_pdf(st.session_state.pdf_doc)
                
                modifications_detected = 0
                
                for idx, orig_item in enumerate(st.session_state.extracted_data):
                    current_edited_val = st.session_state.editor_df.loc[st.session_state.editor_df["ID"] == idx, "Editable Text Content"].values[0]
                    
                    if current_edited_val != orig_item["text"]:
                        modifications_detected += 1
                        target_page = output_doc[orig_item["page"] - 1]
                        
                        # 1. Overlay crisp white vector mask over historical elements
                        mask_rect = fitz.Rect(
                            orig_item["x0"] - 0.5, 
                            orig_item["y0"] - 0.5, 
                            orig_item["x1"] + 0.5, 
                            orig_item["y1"] + 0.5
                        )
                        target_page.draw_rect(mask_rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        # FIXED: Use universal core Standard PDF font track names to avoid compilation errors
                        font_track = "Helvetica"
                        if orig_item["is_bold"] and orig_item["is_italic"]:
                            font_track = "Helvetica-BoldOblique"
                        elif orig_item["is_bold"]:
                            font_track = "Helvetica-Bold"
                        elif orig_item["is_italic"]:
                            font_track = "Helvetica-Oblique"
                            
                        # Compute base tracking alignment limits safely
                        baseline_y = orig_item["y0"] + orig_item["height"] - (orig_item["height"] * 0.15)
                        
                        # 3. Rewrite updated content securely using original style parameters
                        target_page.insert_text(
                            fitz.Point(orig_item["x0"], baseline_y),
                            current_edited_val,
                            fontsize=orig_item["size"],
                            fontname=font_track,
                            color=(0, 0, 0)
                        )
                
                if modifications_detected == 0:
                    st.warning("No modified layout properties detected.")
                else:
                    pdf_output_buffer = io.BytesIO()
                    output_doc.save(pdf_output_buffer, garbage=3, deflate=True)
                    output_doc.close()
                    
                    st.success(f"Successfully processed {modifications_detected} structural text revisions!")
                    
                    # Direct client data delivery stream download mechanism
                    st.download_button(
                        label="📥 Download Updated PDF File",
                        data=pdf_output_buffer.getvalue(),
                        file_name="modified_document.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )