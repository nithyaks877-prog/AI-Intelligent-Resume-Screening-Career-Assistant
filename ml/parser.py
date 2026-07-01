import fitz  # PyMuPDF
from docx import Document
from io import BytesIO


def extract_text_from_pdf(file):
    """
    Extract text from PDF.
    Works for Streamlit UploadedFile and FastAPI UploadFile.
    """

    text = ""

    pdf = fitz.open(
        stream=file.read(),
        filetype="pdf"
    )

    for page in pdf:
        text += page.get_text()

    pdf.close()

    return text.strip()


def extract_text_from_docx(file):
    """
    Extract text from DOCX.
    Works for Streamlit UploadedFile and FastAPI UploadFile.
    """

    file.seek(0)

    doc = Document(BytesIO(file.read()))

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text.strip()


def extract_text(file):
    """
    Automatically detect PDF/DOCX.

    Supports:
    • Streamlit UploadedFile
    • FastAPI UploadFile
    """

    if file is None:
        return ""

    # Streamlit UploadedFile
    if hasattr(file, "name"):
        filename = file.name.lower()

    # FastAPI UploadFile
    elif hasattr(file, "filename"):
        filename = file.filename.lower()

        # FastAPI UploadFile stores the real file here
        file = file.file

    else:
        raise ValueError("Unknown file type.")

    file.seek(0)

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)

    elif filename.endswith(".docx"):
        return extract_text_from_docx(file)

    else:
        raise ValueError("Unsupported file format.")