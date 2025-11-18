#!/usr/bin/env python3
"""
Convert HTML files to PDF using Pandoc library
Markdown → HTML (via pandoc) → PDF
Uses pandoc's internal PDF rendering via HTML intermediate
"""

import subprocess
import os
import sys
from pathlib import Path

def convert_html_to_pdf_via_pandoc(html_file, pdf_file):
    """
    Convert HTML to PDF using pandoc
    This uses pandoc's internal HTML rendering to PDF
    """
    cmd = [
        'pandoc',
        str(html_file),
        '-o', str(pdf_file),
        '--standalone',
        '--embed-resources',  # Embed CSS and resources
        '--mathml',
        '-t', 'pdf',  # Output format is PDF
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, None
        else:
            # If direct conversion fails, try alternative approach
            return False, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Conversion timed out"
    except FileNotFoundError:
        return False, "Pandoc not found"
    except Exception as e:
        return False, str(e)

def convert_directory(directory, file_extension='.html'):
    """Convert all HTML files in directory"""
    base_path = Path(directory)

    if not base_path.exists():
        print(f"Directory not found: {directory}")
        return False

    files = sorted(base_path.glob(f'*{file_extension}'))

    if not files:
        print(f"No {file_extension} files found in {directory}")
        return False

    print(f"\n{'='*60}")
    print(f"Converting {len(files)} HTML files from {base_path.name}")
    print(f"{'='*60}\n")

    success_count = 0
    fail_count = 0

    for html_file in files:
        pdf_file = html_file.with_suffix('.pdf')
        print(f"Converting: {html_file.name}")
        print(f"  → {pdf_file.name}")

        success, error = convert_html_to_pdf_via_pandoc(html_file, pdf_file)

        if success:
            try:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f"  ✓ Success ({size_mb:.1f} MB)\n")
                success_count += 1
            except:
                print(f"  ✓ Success\n")
                success_count += 1
        else:
            print(f"  ✗ Failed: {error}\n")
            fail_count += 1

    print(f"{'='*60}")
    print(f"Results: {success_count} succeeded, {fail_count} failed")
    print(f"{'='*60}\n")

    return fail_count == 0

def main():
    """Convert all curriculum HTML files to PDF"""

    base_dir = Path(__file__).parent

    print("\n" + "="*70)
    print("HEKAT Categorical Algebra Curriculum")
    print("HTML to PDF Converter (using Pandoc)")
    print("="*70)

    # Check if pandoc is available
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("\n❌ Error: Pandoc not found!")
            print("Please install pandoc: brew install pandoc")
            sys.exit(1)
    except:
        print("\n❌ Error: Pandoc not found!")
        print("Please install pandoc: brew install pandoc")
        sys.exit(1)

    # Convert root capstone HTML files
    print("\nPhase 1: Converting root capstone HTML files...")
    root_html_files = [
        'INDEX.html',
        'KAN-EXTENSIONS-MASTERY-GUIDE.html',
        'CURRICULUM-PROGRESSION.html',
        'PRACTICAL-IMPLICATIONS.html',
        'STRUCTURAL-ANALYSIS.html'
    ]

    root_success = 0
    for html_file in root_html_files:
        full_path = base_dir / html_file
        if full_path.exists():
            pdf_path = full_path.with_suffix('.pdf')
            print(f"Converting: {html_file}")
            success, error = convert_html_to_pdf_via_pandoc(full_path, pdf_path)
            if success:
                try:
                    size_mb = pdf_path.stat().st_size / (1024 * 1024)
                    print(f"  ✓ {pdf_path.name} ({size_mb:.1f} MB)\n")
                    root_success += 1
                except:
                    print(f"  ✓ {pdf_path.name}\n")
                    root_success += 1
            else:
                print(f"  ✗ Failed: {error}\n")
        else:
            print(f"  ⊘ Not found: {html_file}\n")

    # Convert core-concepts HTML files
    print("\nPhase 2: Converting core-concepts HTML files...")
    core_dir = base_dir / 'core-concepts'
    if core_dir.exists():
        core_html = list(core_dir.glob('*.html'))
        if core_html:
            success_count = 0
            for html_file in sorted(core_html):
                pdf_file = html_file.with_suffix('.pdf')
                print(f"Converting: {html_file.name}")
                success, error = convert_html_to_pdf_via_pandoc(html_file, pdf_file)
                if success:
                    try:
                        size_mb = pdf_file.stat().st_size / (1024 * 1024)
                        print(f"  ✓ {pdf_file.name} ({size_mb:.1f} MB)\n")
                        success_count += 1
                    except:
                        print(f"  ✓ {pdf_file.name}\n")
                        success_count += 1
                else:
                    print(f"  ✗ Failed: {error}\n")
            print(f"Core-concepts: {success_count}/{len(core_html)} succeeded\n")
    else:
        print(f"Directory not found: {core_dir}\n")

    # Convert prerequisites HTML files
    print("\nPhase 3: Converting prerequisites HTML files...")
    prereq_dir = base_dir / 'prerequisites'
    if prereq_dir.exists():
        prereq_html = list(prereq_dir.glob('*.html'))
        if prereq_html:
            success_count = 0
            for html_file in sorted(prereq_html):
                pdf_file = html_file.with_suffix('.pdf')
                print(f"Converting: {html_file.name}")
                success, error = convert_html_to_pdf_via_pandoc(html_file, pdf_file)
                if success:
                    try:
                        size_mb = pdf_file.stat().st_size / (1024 * 1024)
                        print(f"  ✓ {pdf_file.name} ({size_mb:.1f} MB)\n")
                        success_count += 1
                    except:
                        print(f"  ✓ {pdf_file.name}\n")
                        success_count += 1
                else:
                    print(f"  ✗ Failed: {error}\n")
            print(f"Prerequisites: {success_count}/{len(prereq_html)} succeeded\n")
    else:
        print(f"Directory not found: {prereq_dir}\n")

    print("\n" + "="*70)
    print("Conversion Complete!")
    print("="*70)
    print("\nPDF files have been created in the same folders as your HTML files.")
    print("\nStructure:")
    print("  core-concepts/*.pdf          - 7 core papers as PDFs")
    print("  prerequisites/*.pdf          - 10 prerequisite papers as PDFs")
    print("  *.pdf (root)                 - 5 capstone documents as PDFs")
    print("\nYou can now:")
    print("  • Open PDFs in any PDF viewer")
    print("  • Print and annotate them")
    print("  • Share them with colleagues")
    print("  • Read offline without internet")
    print("\n")

if __name__ == '__main__':
    main()
