import io
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps
from PIL import UnidentifiedImageError
import pytesseract



def get_file_extension(file: UploadFile) -> str:
    if file.filename is None:
        raise ValueError("Uploaded file has no filename")

    return Path(file.filename).suffix.lstrip(".")

def valid_type_document(file: UploadFile) -> bool:
    ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
    "image/tiff",
    }
    return file.content_type in ALLOWED_CONTENT_TYPES

def extract_text_from_pdf(file_stream) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(file_stream.read()))

    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    return "\n".join(pages)


def extract_text_from_doc(file_stream) -> str:
    from docx import Document

    doc = Document(io.BytesIO(file_stream))

    text = [para.text for para in doc.paragraphs]
    full_text = "\n".join(text)

    return full_text


def extract_text_from_image(file_stream) -> str:
    try:
        image = Image.open(io.BytesIO(file_stream))
        image = ImageOps.exif_transpose(image)
        image = ImageOps.grayscale(image)
        print("image", image)
        return pytesseract.image_to_string(image)

    except UnidentifiedImageError:
        raise ValueError("Invalid image file")