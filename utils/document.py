from fastapi import UploadFile

def valid_type_document(file: UploadFile):
    if file.content_type == "application/pdf" or file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return True
    return False