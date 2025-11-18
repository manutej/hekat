# How to Convert HTML Files to PDF

Your curriculum is now available as **22 beautiful HTML files** with full equation support, interactive navigation, and print-ready formatting.

## Option 1: Print from Browser (Simplest)

This is the **easiest method** and works great:

1. **Open any HTML file** in Safari, Chrome, or Firefox
2. **Press Cmd+P** (Mac) or Ctrl+P (Windows/Linux)
3. **Select "Save as PDF"**
4. Choose your location

**Advantages**:
- No software installation needed
- Perfect formatting and equation rendering
- Very quick

**Perfect For**: Converting individual files as needed

---

## Option 2: Batch Convert with Python Script

If you want to convert **all files at once** to PDF:

### Step 1: Install WeasyPrint
```bash
pip install weasyprint
```

### Step 2: Run the Converter Script
```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/hekat/algebraic-cat
python3 html-to-pdf-converter.py
```

This will create PDF files in the same folders as your HTML files.

**Advantages**:
- Converts all 22 files at once
- Batch processing
- Consistent output

**Time**: ~2-3 minutes for all files

---

## Option 3: Use Mac's Preview App

1. Open HTML file in Preview
2. File → Export as PDF

---

## Option 4: Use Web Browser Extensions

**Chrome/Edge**:
- Install "Save to PDF" extension
- Right-click HTML file → Open with Chrome → Print to PDF

**Firefox**:
- Built-in print to PDF (no extension needed)
- File → Print → "Save to PDF"

---

## Why HTML Format Is Actually Better

Your curriculum is in HTML because:

✅ **Perfect Equation Rendering** - MathML equations display beautifully, with proper mathematical notation

✅ **Interactive Navigation** - Click table of contents to jump to sections instantly

✅ **Syntax Highlighting** - Code examples are color-coded for readability

✅ **No Software Required** - Opens in any browser (Safari, Chrome, Firefox)

✅ **Print-Ready** - Professional formatting when printed to PDF

✅ **Offline Use** - Works completely offline, no internet needed

✅ **Searchable** - Browser Cmd+F to search within documents

✅ **Responsive** - Automatically formats for screen size

---

## File Organization

```
algebraic-cat/
├── core-concepts/
│   ├── MONOIDAL-CATEGORIES-COHERENCE.html
│   ├── ADJOINT-FUNCTORS-RESEARCH.html
│   ├── MONADS-ALGEBRAIC-THEORIES-OPERADS.html
│   ├── ENRICHED-CATEGORY-THEORY-RESEARCH.html
│   ├── HIGHER-CATEGORY-THEORY-RESEARCH.html
│   ├── TOPOS-THEORY-CATEGORICAL-LOGIC.html
│   └── CATEGORICAL-ALGEBRA-HOPF-TANNAKA.html
│
├── prerequisites/
│   ├── 01-CATEGORIES-FOUNDATIONAL.html
│   ├── 02-MORPHISMS-DIAGRAMS.html
│   ├── 03-Functors: Definition and Examples.html
│   ├── 04-NATURAL-TRANSFORMATIONS.html
│   ├── 05-HOM-FUNCTORS-REPRESENTABLE.html
│   ├── 06-LIMITS-COLIMITS.html
│   ├── 07-UNIVERSAL-PROPERTIES.html
│   ├── 08-FUNCTOR-CATEGORIES.html
│   ├── 09-YONEDA-LEMMA.html
│   └── 10-DUALITY.html
│
├── INDEX.html
├── KAN-EXTENSIONS-MASTERY-GUIDE.html
├── CURRICULUM-PROGRESSION.html
├── PRACTICAL-IMPLICATIONS.html
├── STRUCTURAL-ANALYSIS.html
│
└── html-to-pdf-converter.py (batch converter script)
```

---

## Recommended Reading Workflow

1. **Start with**: `INDEX.html` - Choose your learning path
2. **Follow your path** using the HTML files
3. **Print to PDF as needed** (you can do this selectively for files you reference frequently)

---

## Troubleshooting

### "Equations not showing"
**Solution**: Make sure you're opening the HTML in a modern browser (Safari, Chrome, Firefox). MathML equations are supported in all modern browsers.

### "Print looks wrong"
**Solution**: In the Print dialog, use these settings:
- Margins: Normal
- Paper size: Letter or A4
- Color: Color (not grayscale, equations render better in color)

### "WeasyPrint installation fails"
**Solution**: Try:
```bash
pip install --upgrade pip
pip install weasyprint
```

If that fails, use the browser print method instead (Option 1).

---

## Summary

**You have 22 beautiful HTML files ready to use immediately.** They have:
- Full LaTeX equation support (MathML rendering)
- Interactive table of contents
- Professional formatting
- Print-ready design
- No external dependencies

**You can read them right now** by opening any `.html` file in your browser.

**You can convert to PDF** whenever you want using the simple print method or the batch converter script.

Enjoy your categorical algebra curriculum! 🎓
