#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==========================================================
PDF TOOL
Python : 3.12+
Library: pypdf 6.x

Features
---------
✓ Split PDF
✓ Merge PDF
✓ Info PDF

Planned
-------
- Delete pages
- Rotate pages
- Watermark
- Compress
- Encrypt / Decrypt
==========================================================
"""

# ==========================================================
# Imports
# ==========================================================
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader, PdfWriter

# ==========================================================
# Constants
# ==========================================================
APP_NAME = "PDF Tool"
VERSION = "1.0.0"
TIME_FORMAT = "%Y%m%d_%H%M%S"
PAGE_PADDING = 3
MERGE_SUFFIX = "_merged"

# ==========================================================
# Utilities
# ==========================================================
def banner():
    """Hiển thị banner."""

    print()
    print("=" * 60)
    print(f"{APP_NAME} {VERSION}")
    print("=" * 60)
    print()

def interactive_menu():
    banner()

    while True:
        print("Select an option:\n")
        print("  1. Split toàn bộ")
        print("  2. Split theo trang")
        print("  3. Merge nhiều file")
        print("  4. Merge thư mục")
        print("  5. Merge đệ quy")
        print("  6. Info")
        print("  0. Exit")
        print()

        choice = input("Choice > ").strip()

        # --------------------------------------------------
        # 1. Split toàn bộ
        # --------------------------------------------------
        if choice == "1":
            pdf = input("\nInput PDF > ").strip()
            split_pdf(pdf)

        # --------------------------------------------------
        # 2. Split theo trang
        # --------------------------------------------------
        elif choice == "2":
            pdf = input("\nInput PDF > ").strip()

            pages = input(
                'Pages (Ví dụ: 1-3,5,8-10) > '
            ).strip()

            split_pdf(pdf, pages)

        # --------------------------------------------------
        # 3. Merge nhiều file
        # --------------------------------------------------
        elif choice == "3":
            raw = input(
                "\nInput PDF files (cách nhau bởi khoảng trắng) > "
            ).strip()

            merge_pdf(raw.split())

        # --------------------------------------------------
        # 4. Merge thư mục
        # --------------------------------------------------
        elif choice == "4":
            folder = input("\nInput Folder > ").strip()
            merge_pdf([folder])

        # --------------------------------------------------
        # 5. Merge đệ quy
        # --------------------------------------------------
        elif choice == "5":
            folder = input("\nInput Folder > ").strip()

            merge_pdf(
                [folder],
                recursive=True
            )

        # --------------------------------------------------
        # 6. Info
        # --------------------------------------------------
        elif choice == "6":
            pdf = input("\nInput PDF > ").strip()
            info_pdf(pdf)

        # --------------------------------------------------
        # Exit
        # --------------------------------------------------
        elif choice == "0":
            return

        else:
            print_error("Invalid option.")
        
        if choice != "0":
            input("\nPress Enter to continue...")

        print()

def ensure_pdf(path: str | Path) -> Path:
    # Kiểm tra file tồn tại và là PDF.
    if isinstance(path, str):
        path = path.strip().strip("'\"")

    path = Path(path).expanduser()

    if not path.exists():
        print(f"❌ Không tìm thấy file:\n{path}")
        sys.exit(1)

    if path.suffix.lower() != ".pdf":
        print(f"❌ Không phải file PDF:\n{path}")
        sys.exit(1)

    return path

def timestamp() -> str:
    # Trả về thời gian hiện tại.
    return datetime.now().strftime(TIME_FORMAT)

def page_name(page: int) -> str:
    # page_001.pdf
    return f"page_{page:0{PAGE_PADDING}d}.pdf"

def pages_name(start: int, end: int) -> str:
    # pages_001-005.pdf
    return (
        f"pages_"
        f"{start:0{PAGE_PADDING}d}"
        f"-"
        f"{end:0{PAGE_PADDING}d}.pdf"
    )

def merge_output_name(first_pdf: Path) -> Path:
    # Tự sinh tên file merge: report.pdf → report_merged_20260626_201530.pdf
    return (
        first_pdf.parent
        / f"{first_pdf.stem}"
        f"{MERGE_SUFFIX}"
        f"_{timestamp()}.pdf"
    )

# ----------------------------------------------------------
# Natural Sort
# ----------------------------------------------------------
def natural_key(path):
    """
    Sort giống Finder.
    page2.pdf
    page10.pdf
    """

    text = Path(path).name.lower()

    return [
        int(x) if x.isdigit() else x
        for x in re.split(r"([0-9]+)", text)
    ]

# ----------------------------------------------------------
# Parse pages
# ----------------------------------------------------------
def parse_ranges(expr: str):
    # Chuyển: 1,2,5-7 thành [(1,1), (2,2), (5,7)]
    expr = expr.replace(" ", "")

    if expr == "":
        raise ValueError("Biểu thức trang rỗng.")

    result = []

    for item in expr.split(","):
        if "-" in item:
            start, end = item.split("-")

            start = int(start)
            end = int(end)

            if start > end:
                start, end = end, start

            result.append((start, end))
        else:
            page = int(item)
            result.append((page, page))
    return result

# ----------------------------------------------------------
# Pretty Print
# ----------------------------------------------------------
def print_header(title: str):
    print()
    print("-" * 60)
    print(title)
    print("-" * 60)

def print_success(path: Path):
    print(f"✔ {path.name}")

def print_warning(msg: str):
    print(f"⚠ {msg}")

def print_error(msg: str):
    print(f"❌ {msg}")

def print_done(path: Path):
    print()
    print(f"📂 Output : {path}")
    print()
    
# ==========================================================
# Split
# ==========================================================
def split_pdf(input_pdf: str, expr: str | None = None):
    # Split PDF
    pdf = ensure_pdf(input_pdf)

    print_header("Split PDF")

    reader = PdfReader(pdf)
    total_pages = len(reader.pages)

    print(f"Input      : {pdf}")
    print(f"Pages      : {total_pages}")

    # Nếu không truyền pages: pdf split file.pdf -> split toàn bộ từng trang
    if expr is None or expr.strip() == "":
        groups = [
            (page, page)
            for page in range(1, total_pages + 1)
        ]

        print("Mode       : Split every page")

    # pdf split file.pdf "1,3-5,8"  -> Split theo nhóm trang.
    else:
        groups = parse_ranges(expr)

        print(f"Selection  : {expr}")

    # ------------------------------------------------------
    # Output folder
    # ------------------------------------------------------
    output_dir = pdf.parent / f"split_output_{timestamp()}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output Dir : {output_dir}")
    print()

    exported = 0

    for index, (start, end) in enumerate(groups, start=1):
        if start < 1 or end > total_pages:
            print_warning(
                f"Skip {start}-{end} (PDF chỉ có {total_pages} trang)"
            )

            continue

        writer = PdfWriter()

        for page in range(start - 1, end):
            writer.add_page(reader.pages[page])

        # --------------------------------------------------
        # Output filename
        # --------------------------------------------------
        if start == end:
            filename = page_name(start)
        else:
            filename = pages_name(start, end)

        output = output_dir / filename

        with open(output, "wb") as f:
            writer.write(f)

        exported += 1

        print(
            f"[{index:03d}/{len(groups):03d}] "
            f"{output.name}"
        )

    print()
    print(f"Exported   : {exported}")
    print_done(output_dir)
    
# ==========================================================
# Merge
# ==========================================================
def merge_pdf(inputs, recursive=False):
    """
    Merge nhiều file PDF.
    Hỗ trợ:
        pdf merge a.pdf b.pdf
        pdf merge *.pdf
        pdf merge .
        pdf merge folder
        pdf merge folder1 folder2 a.pdf
        pdf merge -r folder

    Notes
    -----
    - Folder sẽ tự tìm *.pdf
    - -r sẽ tìm cả thư mục con
    - Luôn Natural Sort trước khi merge
    - Output được tạo cùng thư mục với file đầu tiên
    """

    print_header("Merge PDF")
    # Nếu người dùng chỉ truyền đúng 1 thư mục
    single_input_dir = None

    if (
        len(inputs) == 1
        and Path(inputs[0]).expanduser().is_dir()
    ):
        single_input_dir = Path(inputs[0]).expanduser()

    pdf_files = []

    # ------------------------------------------------------
    # Expand inputs
    # ------------------------------------------------------
    for item in inputs:
        if isinstance(item, str):
            item = item.strip().strip("'\"")
        
        path = Path(item).expanduser()

        if not path.exists():
            print_warning(f"Không tồn tại: {path}")
            continue

        # --------------------------------------------------
        # Folder
        # --------------------------------------------------
        if path.is_dir():
            if recursive:
                files = path.rglob("*.pdf")
            else:
                files = path.glob("*.pdf")

            pdf_files.extend(files)

        # --------------------------------------------------
        # File
        # --------------------------------------------------
        else:
            ensure_pdf(path)
            pdf_files.append(path)

    # ------------------------------------------------------
    # Remove duplicate
    # ------------------------------------------------------
    pdf_files = list(dict.fromkeys(pdf_files))

    # ------------------------------------------------------
    # Không có file
    # ------------------------------------------------------
    if len(pdf_files) == 0:
        print_error("Không tìm thấy file PDF.")
        return

    # ------------------------------------------------------
    # Natural Sort
    # ------------------------------------------------------
    pdf_files = sorted(pdf_files, key=natural_key)

    # ------------------------------------------------------
    # Output
    # ------------------------------------------------------
    # Nếu chỉ merge 1 thư mục
    if single_input_dir is not None:
        output = (
            single_input_dir
            / f"merged_{timestamp()}.pdf"
        )
    # Các trường hợp còn lại
    else:
        output = merge_output_name(pdf_files[0])

    # ------------------------------------------------------
    # Không merge chính output
    # ------------------------------------------------------
    pdf_files = [
        pdf
        for pdf in pdf_files
        if pdf.resolve() != output.resolve()
    ]

    if len(pdf_files) < 2:
        print_error("Cần ít nhất 2 file PDF để merge.")
        return

    print(f"Recursive   : {recursive}")
    print(f"Input Files : {len(pdf_files)}")
    print(f"Output      : {output}")

    print()

    writer = PdfWriter()

    # ------------------------------------------------------
    # Merge
    # ------------------------------------------------------
    total = len(pdf_files)

    for index, pdf in enumerate(pdf_files, start=1):
        print(
            f"[{index:03d}/{total:03d}] "
            f"{pdf.name}"
        )
        writer.append(str(pdf))
    with open(output, "wb") as f:
        writer.write(f)

    writer.close()
    print_done(output)

# ==========================================================
# Info
# ==========================================================
def info_pdf(input_pdf):
    # Hiển thị thông tin PDF.
    pdf = ensure_pdf(input_pdf)

    print_header("PDF Information")

    reader = PdfReader(pdf)

    print(f"File       : {pdf}")
    print(f"Pages      : {len(reader.pages)}")

    metadata = reader.metadata

    if metadata:
        print()
        print("Metadata")
        print("-" * 60)

        for key, value in metadata.items():

            print(f"{key:20} {value}")
    else:
        print()
        print("Không có Metadata.")

# ==========================================================
# CLI
# ==========================================================
def build_parser():
    # Khởi tạo Command Line Interface.
    parser = argparse.ArgumentParser(
        prog=Path(sys.argv[0]).name,
        description=(
            "PDF Tool\n\n"
            "Examples:\n"
            "  pdf_tool.py split report.pdf\n"
            '  pdf_tool.py split report.pdf "1-3,5,8-10"\n'
            "  pdf_tool.py merge *.pdf\n"
            "  pdf_tool.py merge split_output_20260626_210512\n"
            "  pdf_tool.py merge -r Documents\n"
            "  pdf_tool.py info report.pdf"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    sub = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ======================================================
    # split
    # ======================================================
    split = sub.add_parser(
        "split",
        help="Split PDF",
        description=(
            "Split PDF\n\n"
            "Examples:\n"
            "  pdf_tool.py split report.pdf\n"
            '  pdf_tool.py split report.pdf "1-3,5,8-10"'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    split.add_argument(
        "pdf",
        help="Input PDF"
    )

    split.add_argument(
        "pages",
        nargs="?",
        default=None,
        help=(
            'Ví dụ: "1-3,5,8-10"\n'
            'Bỏ trống để tách toàn bộ từng trang.'
        )
    )

    # ======================================================
    # merge
    # ======================================================
    merge = sub.add_parser(
        "merge",
        help="Merge PDFs",
        description=(
            "Merge PDFs\n\n"
            "Examples:\n"
            "  pdf_tool.py merge *.pdf\n"
            "  pdf_tool.py merge split_output_20260626_210512\n"
            "  pdf_tool.py merge -r Documents"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    merge.add_argument(
        "files",
        nargs="+",
        help="Danh sách PDF hoặc thư mục."
    )

    merge.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Tìm PDF trong tất cả thư mục con."
    )

    # ======================================================
    # info
    # ======================================================
    info = sub.add_parser(
        "info",
        help="Hiển thị thông tin PDF"
    )

    info.add_argument(
        "pdf",
        help="Input PDF"
    )

    return parser

# ==========================================================
# Main
# ==========================================================
def main():
    # Không truyền tham số
    if len(sys.argv) == 1:
        interactive_menu()
        return

    # Có tham số -> dùng argparse
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "split":
        split_pdf(
            args.pdf,
            args.pages
        )
    elif args.command == "merge":
        merge_pdf(
            args.files,
            recursive=args.recursive
        )
    elif args.command == "info":
        info_pdf(
            args.pdf
        )

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)

    except Exception as e:
        print_error(str(e))
        sys.exit(1)
