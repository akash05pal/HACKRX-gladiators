import os
import requests
from urllib.parse import urlparse

def download_document(doc_path_or_url, save_dir: str = "downloads"):
    print(f"Checking local file: {doc_path_or_url}")
    
    # Handle local file paths
    if os.path.isabs(doc_path_or_url):  # If absolute path
        abs_path = doc_path_or_url
    else:  # If relative path
        abs_path = os.path.abspath(os.path.join(save_dir, doc_path_or_url))
    
    print(f"Absolute path: {abs_path}")
    
    # Check if file exists locally
    if os.path.exists(abs_path):
        filetype = os.path.splitext(abs_path)[1].lower().lstrip('.')
        if filetype in ['pdf', 'docx']:
            return abs_path, filetype
        else:
            raise Exception(f"Unsupported file type: {filetype}")
            
    # Handle URLs
    elif doc_path_or_url.startswith(('http://', 'https://')):
        os.makedirs(save_dir, exist_ok=True)
        filename = os.path.basename(urlparse(doc_path_or_url).path)
        local_path = os.path.join(save_dir, filename)
        response = requests.get(doc_path_or_url)
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if ext in ['pdf', 'docx']:
                return local_path, ext
            else:
                raise Exception(f"Unsupported file type: {ext}")
        else:
            raise Exception(f"Failed to download document: {response.status_code}")
    else:
        raise Exception(f"File not found: {abs_path}")

def extract_text_pdf(pdf_path):
    import pdfplumber
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_docx(docx_path):
    from docx import Document
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def parse_document(file_path, filetype):
    if filetype == "pdf":
        return extract_text_pdf(file_path)
    elif filetype == "docx":
        return extract_text_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {filetype}")