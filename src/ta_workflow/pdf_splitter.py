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


def get_input() -> tuple[str, list[tuple[int, int]]]:
    """Get user input for the file path and pages to split"""

    while True:
        input_path = input(
            "Enter the absolute path to a PDF file or directory containing PDF files: "
        )
        path = Path(input_path).expanduser().resolve()
        if not path.exists():
            print(f"File or directory not found: {input_path}")
        elif path.is_file() and path.suffix != ".pdf":
            print(f"Invalid file type: {input_path}")
        elif path.is_dir():
            pdf_files = sorted([f for f in path.glob("*.pdf")])
            if not pdf_files:
                print(f"No PDF files found in directory: {input_path}")
            else:
                print("Select a PDF file to split:")
                for i, pdf_file in enumerate(pdf_files):
                    print(f"{i+1}: {pdf_file}")
                selection = input("Enter the number of the PDF file to split: ")
                if not selection.isdigit() or not 1 <= int(selection) <= len(pdf_files):
                    print(f"Invalid selection: {selection}")
                else:
                    file_path = str(pdf_files[int(selection) - 1])
                    break
        elif path.is_file():
            file_path = input_path
            break
        else:
            print(f"Invalid file or directory: {input_path}")
            print(
                "Please enter the absolute path to a PDF file or directory containing PDF files."
            )

    pages = []
    while True:
        page_input = input(
            "Enter the page numbers to split, separated by a dash (or 'done' inputting is done): "
        )
        if page_input.lower() == "done":
            break
        page_numbers = page_input.split("-")
        if len(page_numbers) == 2:
            start_page = int(page_numbers[0])
            end_page = int(page_numbers[1])
            if end_page < start_page:
                print(
                    "Invalid input. The end page must be greater than or equal to the start page."
                )
            else:
                pages.append((start_page, end_page))
        else:
            print("Invalid input. Please enter two page numbers separated by a dash.")

    return file_path, pages
