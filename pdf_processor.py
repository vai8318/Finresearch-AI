
from pathlib import Path

import pymupdf


PDF_PATH = Path(r"D:\AMDT\corrective-agent\Data\dabur-india-annual-report-2024-25.pdf")


def inspect_pdf(pdf_path: Path = PDF_PATH) -> None:
    """Display basic metadata and a sample of extracted text."""

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path.resolve()}"
        )

    with pymupdf.open(pdf_path) as document:
        print(f"File: {pdf_path}")
        print(f"Total pages: {document.page_count}")
        print(f"Metadata: {document.metadata}")

        for page_index in range(min(5, document.page_count)):
            page = document[page_index]
            text = page.get_text("text")

            print(f"\n{'=' * 20} PDF PAGE {page_index + 1} {'=' * 20}")
            print(f"Extracted characters: {len(text)}")
            print(text[:1500] if text.strip() else "[No extractable text]")


def inspect_all_pages(pdf_path: Path = PDF_PATH) -> None:
    """Summarize text extraction quality across the PDF."""

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path.resolve()}")

    empty_pages = []
    short_pages = []
    total_characters = 0

    with pymupdf.open(pdf_path) as document:
        for page_index, page in enumerate(document):
            text = page.get_text("text")
            character_count = len(text.strip())
            total_characters += character_count

            if character_count == 0:
                empty_pages.append(page_index + 1)
            elif character_count < 100:
                short_pages.append((page_index + 1, character_count))

        print("Total PDF pages:", document.page_count)
        print("Total extracted characters:", total_characters)
        print("Pages with no extracted text:", len(empty_pages))
        print("Empty page numbers:", empty_pages)
        print("Pages with fewer than 100 characters:", short_pages)


# if __name__ == "__main__":
#     inspect_all_pages()


def inspect_low_text_pages(pdf_path: Path = PDF_PATH) -> None:
    """Diagnose pages where text extraction returned very little text."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path.resolve()}")

    candidate_pages = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 27,
        41, 51, 55, 63, 77, 95, 121, 129, 130
    ]

    with pymupdf.open(pdf_path) as document:
        for page_number in candidate_pages:
            page = document[page_number - 1]
            text = page.get_text("text").strip()
            images = page.get_images(full=True)

            print(f"\n{'=' * 15} PDF PAGE {page_number} {'=' * 15}")
            print(f"Extracted characters: {len(text)}")
            print(f"Embedded images: {len(images)}")
            print(f"Drawings/vector elements: {len(page.get_drawings())}")
            print("Extracted text:")
            print(text[:500] if text else "[No extractable text]")


# if __name__ == "__main__":
#     inspect_low_text_pages()


def extract_pages(pdf_path: Path = PDF_PATH) -> list[dict]:
    """Extract searchable text while preserving original PDF page numbers."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path.resolve()}")

    page_records = []
    empty_pages = []
    low_text_pages = []

    with pymupdf.open(pdf_path) as document:
        total_pages = document.page_count

        for page_index, page in enumerate(document):
            text = page.get_text("text", sort=True).strip()
            pdf_page_number = page_index + 1

            if not text:
                empty_pages.append(pdf_page_number)
                continue

            if len(text) < 100:
                low_text_pages.append(pdf_page_number)

            page_records.append({
                "pdf_page": pdf_page_number,
                "text": text,
            })

    # The PDF is closed here, so use the saved total_pages variable.
    print(f"Total PDF pages: {total_pages}")
    print(f"Pages extracted with text: {len(page_records)}")
    print(f"Pages skipped because they contain no extractable text: {len(empty_pages)}")
    print(f"Pages with fewer than 100 characters: {len(low_text_pages)}")
    print(f"Empty PDF page numbers: {empty_pages}")

    return page_records


# if __name__ == "__main__":
#     records = extract_pages()
#     print(f"Total extracted page records: {len(records)}")


def inspect_extracted_pages(
    records: list[dict],
    page_numbers: list[int],
    preview_chars: int = 2500,
) -> None:
    """Preview extracted text from selected PDF pages."""
    records_by_page = {
        record["pdf_page"]: record["text"]
        for record in records
    }

    for page_number in page_numbers:
        print(f"\n{'=' * 20} PDF PAGE {page_number} {'=' * 20}")

        text = records_by_page.get(page_number)

        if text is None:
            print("[No extractable text]")
            continue

        print(text[:preview_chars])


if __name__ == "__main__":
    records = extract_pages()

    inspect_extracted_pages(
        records,
        page_numbers=[4, 10, 100, 200, 300, 400, 500, 544],
    )


def chunk_pages(
    records: list[dict],
    chunk_size: int = 1200,
    overlap: int = 200,
    newline_threshold: float = 0.8,
) -> list[dict]:
    """Create overlapping text chunks while preferring nearby newlines."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

    if not 0 < newline_threshold <= 1:
        raise ValueError("newline_threshold must be > 0 and <= 1.")

    chunks = []

    for record in records:
        text = record["text"].strip()
        page_number = record["pdf_page"]

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))

            if end < len(text):
                newline_position = text.rfind("\n", start, end)
                minimum_end = start + int(
                    (end - start) * newline_threshold
                )

                # Prefer a newline only if it is close enough
                # to the intended chunk boundary.
                if newline_position >= minimum_end:
                    end = newline_position

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "pdf_page": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                })
                chunk_index += 1

            if end >= len(text):
                break

            start = end - overlap

    return chunks
if __name__ == "__main__":
    records = extract_pages()
    chunks = chunk_pages(records)

    print(f"Total extracted page records: {len(records)}")
    print(f"Total chunks created: {len(chunks)}")

    if chunks:
        print("\nSample chunk:")
        print(f"PDF page: {chunks[0]['pdf_page']}")
        print(f"Chunk index: {chunks[0]['chunk_index']}")
        print(chunks[0]["text"][:500])