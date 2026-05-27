const backendUrl = "http://127.0.0.1:8000";

const pdfCanvas = document.getElementById("pdfCanvas");
const ctx = pdfCanvas.getContext("2d");
const textLayer = document.getElementById("textLayer");

let currentPdfPath = null;
let textObjects = [];
let editedObjects = [];

// FIXED: Increased scale factor to 1.5 for ultra-crisp display quality
const GLOBAL_SCALE = 1.5;

async function renderPDF(file) {
    console.log("Rendering crisp PDF...");
    const arrayBuffer = await file.arrayBuffer();
    const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
    const pdf = await loadingTask.promise;
    const page = await pdf.getPage(1);

    const viewport = page.getViewport({ scale: GLOBAL_SCALE });
    pdfCanvas.width = viewport.width;
    pdfCanvas.height = viewport.height;

    await page.render({
        canvasContext: ctx,
        viewport: viewport
    }).promise;
}

function renderTextObjects() {
    textLayer.innerHTML = "";
    if (!textObjects || textObjects.length === 0) return;

    textObjects.forEach((obj, index) => {
        const div = document.createElement("div");
        div.className = "text-item";
        div.contentEditable = true;
        div.innerText = obj.text;

        // Position alignment mappings
        div.style.left = (obj.x * GLOBAL_SCALE) + "px";
        div.style.top = (obj.y * GLOBAL_SCALE) + "px";
        div.style.width = (obj.width * GLOBAL_SCALE) + "px";
        div.style.height = (obj.height * GLOBAL_SCALE) + "px";
        div.style.fontSize = ((obj.size || 11) * GLOBAL_SCALE) + "px";

        div.oninput = () => {
            div.classList.add("edited"); // Keep visible on screen after change
            editedObjects[index] = {
                page: obj.page,
                x: obj.x,
                y: obj.y,
                width: obj.width,
                height: obj.height,
                size: obj.size || 11,
                text: div.innerText
            };
        };

        textLayer.appendChild(div);
    });
}

document.getElementById("pdfUpload").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${backendUrl}/upload`, { method: "POST", body: formData });
    const data = await res.json();
    
    currentPdfPath = data.file_path;
    textObjects = data.text_objects;
    editedObjects = []; // Reset workspace tracking entries

    await renderPDF(file);
    renderTextObjects();
});

document.getElementById("saveEdits").addEventListener("click", async () => {
    if (!currentPdfPath) return alert("Upload a PDF first.");

    // Filter out blank array indexes before sending data to backend
    const cleanPayloadEdits = editedObjects.filter(item => item !== undefined && item !== null);

    const res = await fetch(`${backendUrl}/edit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: currentPdfPath, edits: cleanPayloadEdits })
    });

    const data = await res.json();
    window.editedPdfPath = data.edited_pdf_path;
    alert("Edits saved successfully!");
});

document.getElementById("downloadPdf").addEventListener("click", () => {
    if (!window.editedPdfPath) return alert("Save edits first.");
    window.location.href = `${backendUrl}/export?path=${window.editedPdfPath}`;
});