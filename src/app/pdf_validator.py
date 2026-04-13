from pathlib import Path
from magic import magic
from PyPDF2 import PdfReader
from pathlib import Path
import pymupdf

class PdfValidator:
    @staticmethod
    def is_pdf(file_path: Path) -> bool:
        path_s = str(file_path)
        mime = magic.Magic(mime=True)

        # Check file extension
        if file_path.suffix.lower() != '.pdf':
            return False

        # Check PDF header
        try:
            with open(path_s, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False
        except Exception as e:
            return False

        # Check MIME type
        try:
            mime_type = mime.from_file(path_s)
            if mime_type != 'application/pdf':
                return False
        except Exception as e:
            return False

        # Check PyPDF2 parsing
        try:
            reader = PdfReader(path_s)
            _ = len(reader.pages)
        except Exception as e:
            return False

        return True
    
    @staticmethod
    def is_html(filepath : Path) -> bool:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(1000)
                return '<html' in content.lower() or '<body' in content.lower()
        except Exception:
            return False

    @staticmethod
    def check_pdf_integrity(file_path: Path) -> bool:
        try:
            doc = pymupdf.open(file_path)
            doc.close()
            return True
        except:
            return False