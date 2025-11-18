#!/usr/bin/env python3
"""
Convert HTML files to PDF using Google Chrome/Chromium in headless mode
No LaTeX or external dependencies required
"""

import subprocess
import os
import sys
from pathlib import Path

def convert_html_to_pdf_chrome(html_file, pdf_file):
    """
    Convert HTML to PDF using Chrome/Chromium in headless mode
    """
    # Expand user path to absolute path
    html_path = html_file.resolve()
    pdf_path = pdf_file.resolve()

    # Try different chrome executables
    chrome_executables = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        'google-chrome',
        'chromium-browser',
        'chrome',
    ]

    chrome_cmd = None
    for exe in chrome_executables:
        try:
            result = subprocess.run([exe, '--version'], capture_output=True, timeout=2)
            if result.returncode == 0:
                chrome_cmd = exe
                break
        except:
            continue

    if not chrome_cmd:
        return False, "Chrome/Chromium not found. Please install Google Chrome."

    cmd = [
        chrome_cmd,
        '--headless=new',  # Use new headless mode
        '--disable-gpu',
        '--no-sandbox',
        '--print-to-pdf=' + str(pdf_path),
        'file://' + str(html_path),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr if result.stderr else "Chrome returned error"
    except subprocess.TimeoutExpired:
        return False, "Conversion timed out (60s)"
    except Exception as e:
        return False, str(e)

def main():
    """Convert all HTML files to PDF using Chrome"""

    base_dir = Path(__file__).parent

    print("\n" + "="*70)
    print("HEKAT Categorical Algebra Curriculum")
    print("HTML to PDF Converter (using Chrome Headless)")
    print("="*70)

    # Find Chrome/Chromium
    chrome_executables = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        'google-chrome',
        'chromium-browser',
    ]

    chrome_found = False
    for exe in chrome_executables:
        try:
            result = subprocess.run([exe, '--version'], capture_output=True, timeout=2)
            if result.returncode == 0:
                chrome_found = True
                print(f"\n✓ Found: {result.stdout.decode().strip()}")
                break
        except:
            continue

    if not chrome_found:
        print("\n❌ Error: Google Chrome or Chromium not found!")
        print("Please install one of:")
        print("  • Google Chrome (recommended): https://www.google.com/chrome/")
        print("  • Chromium: brew install chromium")
        sys.exit(1)

    # Collect all HTML files
    html_files = []

    # Root files
    for html_file in sorted(base_dir.glob('*.html')):
        html_files.append(('Root', html_file))

    # Core-concepts
    core_dir = base_dir / 'core-concepts'
    if core_dir.exists():
        for html_file in sorted(core_dir.glob('*.html')):
            html_files.append(('Core-Concepts', html_file))

    # Prerequisites
    prereq_dir = base_dir / 'prerequisites'
    if prereq_dir.exists():
        for html_file in sorted(prereq_dir.glob('*.html')):
            html_files.append(('Prerequisites', html_file))

    total = len(html_files)
    print(f"\nFound {total} HTML files to convert")
    print("="*70 + "\n")

    success_count = 0
    fail_count = 0
    by_category = {}

    for category, html_file in html_files:
        pdf_file = html_file.with_suffix('.pdf')
        print(f"[{success_count + fail_count + 1}/{total}] Converting: {html_file.name}")

        success, error = convert_html_to_pdf_chrome(html_file, pdf_file)

        if success:
            try:
                size_mb = pdf_file.stat().st_size / (1024 * 1024)
                print(f"  ✓ Success ({size_mb:.1f} MB)\n")
                success_count += 1
                by_category[category] = by_category.get(category, 0) + 1
            except:
                print(f"  ✓ Success\n")
                success_count += 1
                by_category[category] = by_category.get(category, 0) + 1
        else:
            print(f"  ✗ Failed: {error}\n")
            fail_count += 1

    print("\n" + "="*70)
    print("Conversion Results")
    print("="*70)

    for category in ['Root', 'Core-Concepts', 'Prerequisites']:
        count = by_category.get(category, 0)
        if count > 0:
            print(f"{category}: {count} files")

    print(f"\nTotal: {success_count} succeeded, {fail_count} failed")
    print("="*70 + "\n")

    if fail_count == 0:
        print("✓ All conversions successful!")
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
    else:
        print(f"⚠ {fail_count} files failed to convert.")
        print("Please check Chrome installation and try again.")

    print()

if __name__ == '__main__':
    main()
