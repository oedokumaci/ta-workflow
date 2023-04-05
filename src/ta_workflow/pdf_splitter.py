from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter


def split_pdf(file_path_str: str, pages: list[tuple[int, int]]) -> None:
    """Split a PDF into multiple files based on the given page numbers"""

    file_path = Path(file_path_str)
    with file_path.open("rb") as f:
        reader = PdfReader(f)
        for i, page_range in enumerate(pages):
            start_page, end_page = page_range
            output = PdfWriter()
            for page in range(start_page - 1, end_page):
                output.add_page(reader.pages[page])
            new_file_path = file_path.with_name(f"{file_path.stem}_part{i+1}.pdf")
            with new_file_path.open("wb") as out_file:
                output.write(out_file)


if __name__ == "__main__":
    file_path = input("Enter the absolute path to the PDF file: ")
    pages = [
        (1, 5),
        (6, 8),
        (9, 12),
        (13, 22),
        (23, 28),
        (29, 31),
        (32, 34),
        (35, 37),
        (38, 41),
        (42, 44),
        (45, 48),
        (49, 50),
        (51, 54),
    ]
    split_pdf(file_path, pages)
