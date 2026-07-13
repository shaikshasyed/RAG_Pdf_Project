import fitz
from app.rag.text_cleaner import clean_text


def load_pdf(pdf_path):

    pdf = fitz.open(pdf_path)
    pages = []

    for page_number, page in enumerate(pdf):
        text = page.get_text()
        text = clean_text(text)
        
        pages.append({
            "page": page_number + 1,
            "text": text,
        })

    pdf.close()

    return pages