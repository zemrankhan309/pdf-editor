# 📄 Secure Local PDF Layout Editor

A powerful, privacy‑focused PDF text‑editing tool built with **Streamlit** and **PyMuPDF**.  
This app allows you to upload a PDF, extract all text spans, edit them in a clean table interface, and regenerate a modified PDF — all while preserving:

- Original text positions  
- Font size  
- Bold / italic styling  
- Page structure  
- Layout geometry  

Everything runs **locally** in memory. No files are uploaded to any server.

---

## 🚀 Features

- Upload any PDF and extract text with bounding‑box precision  
- Edit text directly using Streamlit’s Data Editor  
- Automatically detect bold/italic font styles  
- Preserve original typography and coordinates  
- Render page previews as images  
- Rebuild a new PDF with your modifications  
- 100% local processing — secure and private  

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit**
- **PyMuPDF (pymupdf)**
- **Pandas**
- **Pillow**

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/pdf-editor.git

cd pdf-editor

python -m venv .venv
.\.venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt


▶️ Run the App
.\.venv\Scripts\python.exe -m streamlit run app.py

This will Openup
http://localhost:8501

Project Structure
pdf-editor/
│
├── app.py
├── requirements.txt
├── README.md
└── CODE_EXPLANATION.md




📜 License
This project is open‑source under the MIT License.

Zemran Khan  
Resume Rewriter & PDF Tools Developer
GitHub: https://github.com/zemrankhan309 (github.com in Bing)