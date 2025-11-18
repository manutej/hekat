#!/usr/bin/env python3
"""
Convert HTML files to PDF using weasyprint
Install with: pip install weasyprint
"""

import os
import sys
from pathlib import Path

def convert_html_to_pdf():
    """Convert all HTML files to PDF"""
    try:
        from weasyprint import HTML
    except ImportError:
        print("Error: weasyprint not installed")
        print("Install it with: pip install weasyprint")
        sys.exit(1)

    base_path = Path(__file__).parent

    # Find all HTML files
    html_files = list(base_path.glob("*.html")) + \
                 list(base_path.glob("core-concepts/*.html")) + \
                 list(base_path.glob("prerequisites/*.html"))

    print(f"Found {len(html_files)} HTML files to convert")
    print("")

    for html_file in sorted(html_files):
        pdf_file = html_file.with_suffix(".pdf")
        print(f"Converting: {html_file.name} → {pdf_file.name}")

        try:
            HTML(str(html_file)).write_pdf(str(pdf_file))
            size = pdf_file.stat().st_size / 1024 / 1024
            print(f"  ✓ Created ({size:.1f} MB)")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("")
    print("Conversion complete!")

if __name__ == "__main__":
    convert_html_to_pdf()
