from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Try multiple methods to extract text from PDF and return best result."""
    text = ""

    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() or '' for p in pdf.pages]
            text_pdfplumber = '\n'.join(pages).strip()
            if len(text_pdfplumber) > len(text):
                text = text_pdfplumber
                logger.debug("Successfully extracted with pdfplumber")
    except Exception as e:
        logger.debug(f"pdfplumber extraction failed: {e}")

    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        pages = [page.get_text() for page in doc]
        text_fitz = '\n'.join(pages).strip()
        if len(text_fitz) > len(text):
            text = text_fitz
            logger.debug("Successfully extracted with PyMuPDF")
        doc.close()
    except Exception as e:
        logger.debug(f"PyMuPDF extraction failed: {e}")

    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or '')
            except Exception:
                pages.append('')
        text_pypdf2 = '\n'.join(pages).strip()
        if len(text_pypdf2) > len(text):
            text = text_pypdf2
            logger.debug("Successfully extracted with PyPDF2")
    except Exception as e:
        logger.debug(f"PyPDF2 extraction failed: {e}")

    if not text:
        logger.warning(f"Failed to extract text from {pdf_path.name}")

    return text