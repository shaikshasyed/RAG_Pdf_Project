import fitz
from app.rag.text_cleaner import clean_text
from app.rag.chunker import chunk_text
from app.rag.sentence_chunker import sentence_chunk


def load_pdf(pdf_path):

    pdf = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(pdf):

        text = page.get_text()
        text = clean_text(text)

        sentences = sentence_chunk(text)
        sentences_count = len(sentences)

        # word_count = len(text.split())
        # char_count = len(text)

        pages.append({
            "page": page_number + 1,
            "sentences_count": sentences_count,
            "sentences": sentences
        })

    pdf.close()

    return pages