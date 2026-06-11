import io

from fastapi import UploadFile


def valid_type_document(file: UploadFile):
    if file.content_type == "application/pdf" or file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return True
    return False

def extract_text_from_pdf(file_stream):
    from pypdf import PdfReader
    
    pdf_bytes = io.BytesIO(file_stream.read())
    print("len: ", len(pdf_bytes.getvalue()))
    
    reader = PdfReader(stream=pdf_bytes)

    page = reader.pages[0]
    return page.extract_text()


def extract_text_from_doc(file_stream):
    from docx import Document

    doc = Document(io.BytesIO(file_stream))

    text = [para.text for para in doc.paragraphs]
    full_text = "\n".join(text)

    return full_text
