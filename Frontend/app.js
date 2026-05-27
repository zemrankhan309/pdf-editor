console.log("CHECK:", document.getElementById("pdfUpload"));
console.log("🔥 app.js loaded");

const backendUrl = "http://127.0.0.1:8000";

const pdfCanvas = document.getElementById("pdfCanvas");
const ctx = pdfCanvas.getContext("2d");
const textLayer = document.getElementById("textLayer");

let currentPdfPath = null;
let textObjects = [];
let editedObjects = [];

// ------------------------------
// 1. Render PDF
// ------------------------------
async function renderPDF(file) {
    console.log("renderPDF() called");

    const arrayBuffer = await file.arrayBuffer();
    const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });

    loadingTask.onProgress = (p) => console.log("PDF loading:", p.loaded);

    const pdf = await loadingTask.promise;
    const page = await pdf.getPage(1);

    const scale = 1.2;
    const viewport = page.getViewport({ scale });

    pdfCanvas.width = viewport.width;
    pdfCanvas.height = viewport.height;

    await page.render({
        canvasContext: ctx,
        viewport: viewport
    }).promise;

    console.log("PDF rendered successfully");
}

// ------------------------------
// 2. Render editable overlay
// ------------------------------
function renderTextObjects() {
    textLayer.innerHTML = "";

    if (!textObjects || textObjects.length === 0) {
        console.warn("⚠ No text objects found.");
        return;
    }

    const scale = 1.2;

    textObjects.forEach((obj, index) => {
        const div = document.createElement("div");
        div.className = "text-item";
        div.contentEditable = true;
        div.innerText = obj.text;

        div.style.left = (obj.x * scale) + "px";
        div.style.top = (obj.y * scale) + "px";
        div.style.width = (obj.width * scale) + "px";
        div.style.height = (obj.height * scale) + "px";

        div.oninput = () => {
            editedObjects[index] = {
                page: obj.page,
                x: obj.x,
                y: obj.y,
                new_text: div.innerText
            };
        };

        textLayer.appendChild(div);
    });

    console.log("Overlay rendered:", textObjects.length);
}

// ------------------------------
// 3. Upload PDF
// ------------------------------
document.getElementById("pdfUpload").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    console.log("📂 Selected:", file.name);

    // Upload to backend
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${backendUrl}/upload`, {
        method: "POST",
        body: formData
    });

    const data = await res.json();
    currentPdfPath = data.file_path;
    textObjects = data.text_objects;

    console.log("BACKEND RESPONSE:", data);

    // Render PDF
    await renderPDF(file);

    // Render overlay
    renderTextObjects();
});

// ------------------------------
// 4. Save edits
// ------------------------------
document.getElementById("saveEdits").addEventListener("click", async () => {
    if (!currentPdfPath) {
        alert("Upload a PDF first.");
        return;
    }

    const payload = {
        file_path: currentPdfPath,
        edits: editedObjects
    };

    const res = await fetch(`${backendUrl}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();
    window.editedPdfPath = data.edited_pdf_path;

    alert("Edits saved!");
});

// ------------------------------
// 5. Download edited PDF
// ------------------------------
document.getElementById("downloadPdf").addEventListener("click", () => {
    if (!window.editedPdfPath) {
        alert("Save edits first.");
        return;
    }

    window.location.href = `${backendUrl}/export?path=${window.editedPdfPath}`;
});
