# pdf_utils.py
import fitz  # PyMuPDF

def extract_pdf_pages(path):
    doc = fitz.open(path)
    pages = []

    max_pages = min(len(doc), 40)  # ✅ 最多处理前40页

    for i in range(max_pages):
        page = doc[i]
        text = page.get_text()
        if text.strip():
            pages.append({'type': 'text', 'content': text})
        else:
            pix = page.get_pixmap()
            img_bytes = pix.tobytes('png')
            pages.append({'type': 'image', 'content': img_bytes})

    return pages
