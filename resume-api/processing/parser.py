import PyPDF2
from loguru import logger

class PDFParseError(Exception):
    pass

def extract_text_from_pdf(file_path: str) -> str:
    logger.info(f"[PARSER] Extracting text from: {file_path}")

    try:
        text_content = []
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)

            if len(reader.pages) == 0:
                raise PDFParseError("PDF has no pages")

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    logger.warning(
                        f"[PARSER] Page {page_num + 1} failed: {e}"
                    )
                    continue

            full_text = "\n".join(text_content)

            if not full_text.strip():
                raise PDFParseError(
                    "No text could be extracted. "
                    "PDF may be scanned or image-based."
                )

            logger.info(
                f"[PARSER] Extracted {len(full_text)} characters "
                f"from {len(reader.pages)} pages"
            )
            return full_text

    except PDFParseError:
        raise

    except FileNotFoundError:
        raise PDFParseError(f"File not found: {file_path}")

    except PyPDF2.errors.PdfReadError as e:
        raise PDFParseError(f"Corrupted or invalid PDF: {e}")

    except Exception as e:
        raise PDFParseError(f"Unexpected error reading PDF: {e}")

    
