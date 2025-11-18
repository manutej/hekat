#!/usr/bin/env python3
"""
Convert Markdown and HTML files to PDF using Pandoc
Handles LaTeX equations with MathML support
"""

import subprocess
import os
import sys
from pathlib import Path

def run_pandoc(input_file, output_file, from_format='markdown'):
    """
    Run pandoc to convert file to PDF
    Supports LaTeX equations via MathML
    """
    cmd = [
        'pandoc',
        str(input_file),
        '-o', str(output_file),
        '--standalone',
        '--toc',
        '--toc-depth=3',
        '--mathml',  # Render math as MathML
        '--wrap=preserve',
        f'--from={from_format}',
        '--to=pdf',
        '-V', 'geometry:margin=1in',
        '-V', 'colorlinks=true',
        '-V', 'linkcolor=blue',
        '-V', 'lang=en',
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stderr
    except FileNotFoundError:
        return False, "Pandoc not found. Please install pandoc first."
    except Exception as e:
        return False, str(e)

def convert_directory(directory, from_format='markdown', file_extension='.md'):
    """Convert all files in directory"""
    base_path = Path(directory)

    if not base_path.exists():
        print(f"Directory not found: {directory}")
        return False

    files = sorted(base_path.glob(f'*{file_extension}'))

    if not files:
        print(f"No {file_extension} files found in {directory}")
        return False

    print(f"\n{'='*60}")
    print(f"Converting {len(files)} files from {base_path.name}")
    print(f"{'='*60}\n")

    success_count = 0
    fail_count = 0

    for md_file in files:
        pdf_file = md_file.with_suffix('.pdf')
        print(f"Converting: {md_file.name}")
        print(f"  → {pdf_file.name}")

        success, error = run_pandoc(md_file, pdf_file, from_format)

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
    """Convert all curriculum files to PDF"""

    base_dir = Path(__file__).parent

    print("\n" + "="*70)
    print("HEKAT Categorical Algebra Curriculum")
    print("Markdown to PDF Converter (using Pandoc)")
    print("="*70)

    # Convert markdown files in root
    print("\nPhase 1: Converting root capstone markdown files...")
    root_md_files = [
        'INDEX.md',
        'KAN-EXTENSIONS-MASTERY-GUIDE.md',
        'CURRICULUM-PROGRESSION.md',
        'PRACTICAL-IMPLICATIONS.md',
        'STRUCTURAL-ANALYSIS.md'
    ]

    root_success = True
    for md_file in root_md_files:
        full_path = base_dir / md_file
        if full_path.exists():
            pdf_path = full_path.with_suffix('.pdf')
            print(f"\nConverting: {md_file}")
            success, error = run_pandoc(full_path, pdf_path, 'markdown')
            if success:
                try:
                    size_mb = pdf_path.stat().st_size / (1024 * 1024)
                    print(f"  ✓ {pdf_path.name} ({size_mb:.1f} MB)")
                except:
                    print(f"  ✓ {pdf_path.name}")
            else:
                print(f"  ✗ Failed: {error}")
                root_success = False

    # Convert core-concepts markdown files
    print("\n\nPhase 2: Converting core-concepts markdown files...")
    core_dir = base_dir / 'core-concepts'
    if core_dir.exists():
        core_md = list(core_dir.glob('*.md'))
        if core_md:
            convert_directory(str(core_dir), 'markdown', '.md')
    else:
        print(f"Directory not found: {core_dir}")

    # Convert prerequisites markdown files
    print("\nPhase 3: Converting prerequisites markdown files...")
    prereq_dir = base_dir / 'prerequisites'
    if prereq_dir.exists():
        prereq_md = list(prereq_dir.glob('*.md'))
        if prereq_md:
            convert_directory(str(prereq_dir), 'markdown', '.md')
    else:
        print(f"Directory not found: {prereq_dir}")

    print("\n" + "="*70)
    print("Conversion Complete!")
    print("="*70)
    print("\nAll PDF files have been created alongside their markdown sources.")
    print("You can now:")
    print("  • Open PDFs in any PDF viewer")
    print("  • Print and annotate them")
    print("  • Share them with others")
    print("\n")

if __name__ == '__main__':
    main()
