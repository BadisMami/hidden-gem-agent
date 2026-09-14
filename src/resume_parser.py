from pypdf import PdfReader
import fitz
import easyocr
from PIL import Image


def extract_text(pdf_path):

    # =========================
    # Try normal PDF extraction first
    # =========================

    try:

        reader = PdfReader(pdf_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        if len(text.strip()) > 100:

            print(
                "Using standard PDF extraction..."
            )

            return text

    except Exception:

        pass

    # =========================
    # OCR Fallback
    # =========================

    print(
        "No text layer found. Using EasyOCR..."
    )

    reader = easyocr.Reader(
        ['en'],
        gpu=False
    )

    document = fitz.open(
        pdf_path
    )

    extracted_text = ""

    for page_number in range(
        len(document)
    ):

        page = document.load_page(
            page_number
        )

        pix = page.get_pixmap(
            matrix=fitz.Matrix(
                2,
                2
            )
        )

        image_path = (
            f"temp_page_{page_number}.png"
        )

        pix.save(
            image_path
        )

        results = reader.readtext(
            image_path,
            detail=0,
            paragraph=True
        )

        extracted_text += (
            "\n".join(results)
            + "\n"
        )

    return extracted_text


if __name__ == "__main__":

    resume_path = (
        "data/resumes/badis_resume.pdf"
    )

    text = extract_text(
        resume_path
    )

    print(text[:3000])