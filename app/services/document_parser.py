from pathlib import Path

import fitz


ALLOWED_EXTENSIONS = {".pdf", ".txt"}


def validate_file_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only .pdf and .txt files are supported.")

    return extension


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def extract_text_from_pdf(file_path: str) -> str:
    text = []
    pdf_document = fitz.open(file_path)

    try:
        for page in pdf_document:
            page_text = page.get_text()
            if page_text:
                text.append(page_text)
    finally:
        pdf_document.close()

    return "\n".join(text)


def extract_text(file_path: str, file_extension: str) -> str:
    if file_extension == ".txt":
        text = extract_text_from_txt(file_path)
    elif file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        raise ValueError("Unsupported file type.")

    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("No text could be extracted from the file.")

    return cleaned_text