console.log("🔥 app.js loaded successfully");

const backendUrl = "http://127.0.0.1:8000";

// FIXES SILENT WORKER ENGINE CRASHES IN MODERN BROWSERS
if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
} else {
    console.error("CRITICAL: pdfjsLib is missing. Verify your HTML script tags.");
}

const pdfContainer = document.getElementById("pdfContainer");
const pdfCanvas = document.getElementById("pdfCanvas");
const ctx = pdfCanvas.getContext("2d");
const textLayer = document.getElementById("textLayer");

let currentPdfPath = null;
let textObjects = [];
let editedObjects = [];
const scale = 1.2; // Match your text coordinate scaling factor

// ------------------------------
// 1. Render PDF safely with explicit dimensions
// ------------------------------
async function renderPDF(file) {
    try {
        console.log("🔄 Starting PDF render engine sequence...");
        const arrayBuffer = await file.arrayBuffer();
        const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
        
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(1);
        const viewport = page.getViewport({ scale: scale });

        // FORCE fixed dimensions explicitly on elements to guarantee layout visibility
        pdfCanvas.width = viewport.width;
        pdfCanvas.height = viewport.height;
        pdfCanvas.style.width = viewport.width + "px";
        pdfCanvas.style.height = viewport.height + "px";

        pdfContainer.style.width = viewport.width + "px";
        pdfContainer.style.height = viewport.height + "px";

        textLayer.style.width = viewport.width + "px";
        textLayer.style.height = viewport.height + "px";

        const renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };

        await page.render(renderContext).promise;
        console.log("✅ PDF successfully drawn onto canvas framework.");
    } catch (error) {
        console.error("❌ Rendering chain break:", error);
        alert("Failed to render PDF framework: " + error.message);
    }
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

        // Coordinates and Dimensions
        div.style.left = (obj.x * scale) + "px";
        div.style.top = (obj.y * scale) + "px";
        div.style.width = (obj.width * scale) + "px";
        div.style.height = (obj.height * scale) + "px";
        
        // DYNAMIC FONT SCALING (Prevents text overlapping)
        div.style.fontSize = (obj.size * scale) + "px";
        div.style.lineHeight = "1";

        div.oninput = () => {
            editedObjects[index] = {
                page: obj.page,
                x: obj.x,
                y: obj.y,
                text: div.innerText // Keeps object mapping clean for backend
            };
        };

        textLayer.appendChild(div);
    });

    console.log("Overlay rendered safely:", textObjects.length);
}

// ------------------------------
// 3. Upload Event Listener
// ------------------------------
document.getElementById("pdfUpload").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    console.log("📂 File target selected:", file.name);

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`${backendUrl}/upload`, {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            throw new Error(`Server responded with status ${res.status}`);
        }

        const data = await res.json();
        currentPdfPath = data.file_path;
        textObjects = data.text_objects;
        editedObjects = new Array(textObjects.length).fill(null);

        console.log("📦 Payload metadata loaded:", data);

        // Run rendering safely
        await renderPDF(file);
        renderTextObjects();

    } catch (err) {
        console.error("❌ Processing pipeline broke:", err);
        alert("Upload processing exception: " + err.message);
    }
});

// ------------------------------
// 4. Save edits
// ------------------------------
document.getElementById("saveEdits").addEventListener("click", async () => {
    if (!currentPdfPath) {
        alert("Please upload a PDF file first.");
        return;
    }

    const cleanEdits = editedObjects.filter(item => item !== null);

    const payload = {
        file_path: currentPdfPath,
        edits: cleanEdits
    };

    try {
        const res = await fetch(`${backendUrl}/edit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Server rejected save operation layout metadata.");

        const data = await res.json();
        window.editedPdfPath = data.edited_pdf_path;
        alert("Edits saved successfully!");
    } catch (err) {
        alert("Error saving modifications: " + err.message);
    }
});

// ------------------------------
// 5. Download edited PDF
// ------------------------------
document.getElementById("downloadPdf").addEventListener("click", () => {
    if (!window.editedPdfPath) {
        alert("Please save layout edits before downloading.");
        return;
    }
    window.location.href = `${backendUrl}/export?path=${encodeURIComponent(window.editedPdfPath)}`;
});