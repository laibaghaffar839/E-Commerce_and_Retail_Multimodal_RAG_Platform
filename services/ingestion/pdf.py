import pymupdf
import pymupdf4llm
import tempfile

from services.ingestion.image import extract_image


def extract_pdf(file_path: str) -> list[str]:
    """
    Extract text, tables, and embedded images from PDF.
    Returns a list of text strings.
    """

    extracted_text = []

    # Extract text and tables
    text = pymupdf4llm.to_markdown(file_path)

    if text.strip():
        extracted_text.append(text)

    # Open PDF
    document = pymupdf.open(file_path)

    # Extract embedded images
    for page in document:

        images = page.get_images(full=True)

        for image in images:

            xref = image[0]

            image_info = document.extract_image(xref)

            image_bytes = image_info["image"]
            image_ext = image_info["ext"]

            # Create temporary image file
            with tempfile.NamedTemporaryFile(
                suffix=f".{image_ext}"
            ) as temp_image:

                temp_image.write(image_bytes)
                temp_image.flush()

                # Call image.py
                image_text = extract_image(temp_image.name)

                extracted_text.extend(image_text)

    document.close()

    return extracted_text