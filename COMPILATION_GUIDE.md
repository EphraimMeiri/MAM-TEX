# MAM-TEX Compilation Guide

## Prerequisites

### Required Software

1. **XeLaTeX** (part of TeX Live or MiKTeX)
   - XeLaTeX is required (not pdfLaTeX) for Unicode and Hebrew support
   - Install TeX Live: `sudo apt-get install texlive-xetex texlive-lang-other`
   - Or download from: https://www.tug.org/texlive/

2. **LaTeX Packages**
   - `reledmac` - Critical apparatus and parallel texts
   - `polyglossia` - Multilingual support
   - `xcolor` - Color support
   - `titlesec` - Section formatting
   - `geometry` - Page layout
   - `ragged2e` - Text alignment

   Install with:
   ```bash
   sudo apt-get install texlive-humanities texlive-latex-extra
   ```

### Required Fonts

The TEX files require specific Hebrew fonts:

1. **Taamey David (Taamey D)**
   - Main Hebrew font with full cantillation marks (te'amim)
   - Download from: https://culmus.sourceforge.io/taamim/
   - Or: `sudo apt-get install culmus`

2. **Aharoni**
   - Used for verse numbers
   - Available in Windows as part of Hebrew fonts
   - Alternative: Use another Hebrew font like "David CLM" or "Frank Ruehl CLM"

### Installing Fonts

**On Linux:**
```bash
# Install Culmus fonts (includes Taamey David)
sudo apt-get install culmus fonts-culmus

# Or manually install fonts to:
mkdir -p ~/.local/share/fonts
cp *.ttf ~/.local/share/fonts/
fc-cache -fv
```

**On macOS:**
```bash
# Download and copy fonts to:
cp *.ttf ~/Library/Fonts/
```

**On Windows:**
- Right-click font files → Install
- Or copy to: `C:\Windows\Fonts\`

## Compilation Instructions

### Basic Compilation

To compile a TEX file to PDF:

```bash
cd out
xelatex -interaction=nonstopmode MAM-Ruth_noNotes.tex
xelatex -interaction=nonstopmode MAM-Ruth_noNotes.tex
xelatex -interaction=nonstopmode MAM-Ruth_noNotes.tex
```

**Important:** Run XeLaTeX **3-5 times** for proper cross-references and apparatus numbering.

### Why Multiple Passes?

The `reledmac` package requires multiple compilation passes:
1. **First pass**: Generates basic text and marks reference points
2. **Second pass**: Processes cross-references
3. **Third pass**: Finalizes apparatus and line numbers
4. **Fourth-fifth pass**: (Optional) For complex documents with many cross-references

### Compilation Flags

- `-interaction=nonstopmode`: Continue compilation even if errors occur
- `-shell-escape`: (If needed) Allow shell commands (not required for these files)
- `-output-directory=./`: Specify output directory

### Using the Automated Script

We provide a Python script that compiles multiple times automatically:

```bash
# In to_TEX2.py, use the tex_to_pdf() function:
python3 -c "
from to_TEX2 import tex_to_pdf
pdf_path = tex_to_pdf('out/MAM-Ruth_noNotes.tex')
print(f'Generated: {pdf_path}')
"
```

## File Organization

### Generated Files

After compilation, you'll have:
- `.tex` - Source TEX file
- `.pdf` - Final PDF output
- `.aux` - Auxiliary file with cross-references
- `.log` - Compilation log (check for errors/warnings)
- `.out` - Outline/bookmarks
- `.toc` - Table of contents
- `.1`, `.1R`, `.end`, `.eledsec1`, etc. - reledmac working files

### Cleaning Up

To remove auxiliary files:
```bash
rm *.aux *.log *.out *.toc *.1 *.1R *.end *.eledsec*
```

## Troubleshooting

### Common Errors

#### 1. Font Not Found
**Error:** `Font "Taamey D" not found`

**Solution:**
- Install Culmus fonts: `sudo apt-get install culmus`
- Or edit TEX file to use an alternative font:
  ```latex
  \newfontfamily\hebrewfont[Script=Hebrew]{David CLM}
  ```

#### 2. Package Not Found
**Error:** `File 'reledmac.sty' not found`

**Solution:**
```bash
sudo apt-get install texlive-humanities texlive-latex-extra
```

#### 3. Unicode/RTL Issues
**Error:** Hebrew text appears backwards or garbled

**Solution:**
- Ensure you're using XeLaTeX (not pdfLaTeX)
- Check that polyglossia is loaded
- Verify UTF-8 encoding: File should start with `\documentclass[12pt]{article}`

#### 4. Line Numbering Issues
**Symptom:** Line numbers don't appear or are incorrect

**Solution:**
- Run XeLaTeX at least 3 times
- Check that `\beginnumbering` and `\endnumbering` are present
- Verify `\pstart` and `\pend` are balanced

### Checking Compilation Logs

After compilation, check the `.log` file:

```bash
# Look for errors
grep -i "error" MAM-Ruth_noNotes.log

# Look for warnings
grep -i "warning" MAM-Ruth_noNotes.log

# Check for undefined references
grep -i "undefined" MAM-Ruth_noNotes.log
```

## Expected Output

### File Sizes (Approximate)

- **Ruth without notes**: ~14KB TEX → ~100-150KB PDF
- **Ruth with notes**: ~18KB TEX → ~150-200KB PDF
- **Psalms without notes**: ~264KB TEX → ~800KB-1MB PDF
- **Psalms with notes**: ~293KB TEX → ~1-1.5MB PDF

### Visual Features

The compiled PDFs should include:

1. **Hebrew Text**
   - Right-to-left text flow
   - Full cantillation marks (te'amim)
   - Proper vowel points (nikkud)

2. **Verse Numbers**
   - Superscript Hebrew numerals
   - Positioned before each verse

3. **Critical Apparatus** (with notes version only)
   - Footnotes with textual variants
   - Ketiv/Qere side notes
   - Manuscript references

4. **Formatting**
   - Proper paragraph spacing
   - Line numbers (for Psalms/Job/Proverbs)
   - Column layout for poetry (if enabled)

## Performance Tips

### Faster Compilation

1. **Use Draft Mode** (first runs):
   ```bash
   xelatex -interaction=nonstopmode -draftmode MAM-Ruth.tex
   ```

2. **Compile Only Changed Files**:
   ```bash
   # Only recompile if source is newer than PDF
   [ MAM-Ruth.tex -nt MAM-Ruth.pdf ] && xelatex MAM-Ruth.tex
   ```

3. **Parallel Compilation** (for multiple books):
   ```bash
   xelatex MAM-Ruth.tex & xelatex MAM-Psalms.tex & wait
   ```

### Memory Issues

For very large books (like Psalms), you may need to increase TeX memory:

Edit `texmf.cnf` or run with:
```bash
xelatex -extra-mem-top=100000000 MAM-Psalms.tex
```

## Batch Compilation

### Compile All Books

Create a shell script `compile_all.sh`:

```bash
#!/bin/bash
cd out

for book in Ruth Psalms; do
    for variant in "" "_noNotes"; do
        file="MAM-${book}${variant}.tex"
        if [ -f "$file" ]; then
            echo "Compiling $file..."
            for i in {1..3}; do
                xelatex -interaction=nonstopmode "$file" > /dev/null
            done
            echo "✓ Generated ${file%.tex}.pdf"
        fi
    done
done

echo "Compilation complete!"
```

Run with:
```bash
chmod +x compile_all.sh
./compile_all.sh
```

## Advanced Configuration

### Customizing Fonts

Edit the font definitions in the TEX files:

```latex
% Main Hebrew font
\newfontfamily\hebrewfont[Script=Hebrew]{Taamey D}

% Verse number font
\newfontfamily\locf[Script=Hebrew]{Aharoni}
```

Alternative fonts:
- **Taamey D** → `David CLM`, `Frank Ruehl CLM`, `Keter YG`
- **Aharoni** → `David CLM`, `Miriam CLM`

### Adjusting Page Layout

In the TEX file preamble:

```latex
\usepackage[
    paperwidth=5.5in,    % Change page width
    paperheight=8.5in,   % Change page height
    top=0.5in,           % Top margin
    bottom=.75in         % Bottom margin
]{geometry}
```

### Modifying Line Numbering

```latex
\firstlinenum{1}        % Start numbering at 1 (default: 2000)
\linenumincrement{1}    % Number every line (default: 2000)
\lineation{page}        % Reset per page (or 'section')
```

## Quality Assurance

### Pre-Compilation Checklist

- [ ] XeLaTeX installed
- [ ] Required packages installed
- [ ] Hebrew fonts installed and accessible
- [ ] TEX files validated (balanced braces, proper structure)
- [ ] Sufficient disk space (~50MB per large book)

### Post-Compilation Verification

- [ ] PDF opens without errors
- [ ] Hebrew text displays correctly (right-to-left)
- [ ] Cantillation marks (te'amim) are visible
- [ ] Verse numbers appear properly
- [ ] Notes/apparatus formatted correctly (if applicable)
- [ ] No font substitution warnings in log
- [ ] File size is reasonable

## Getting Help

If you encounter issues:

1. **Check the log file**: `*.log` contains detailed error information
2. **Verify fonts**: Run `fc-list | grep -i hebrew` to see installed fonts
3. **Test minimal example**: Create a simple TEX file to test font/package installation
4. **Stack Exchange**: Search on tex.stackexchange.com
5. **reledmac documentation**: `texdoc reledmac`

## References

- **reledmac Manual**: https://ctan.org/pkg/reledmac
- **Polyglossia Manual**: https://ctan.org/pkg/polyglossia
- **XeLaTeX Guide**: https://www.overleaf.com/learn/latex/XeLaTeX
- **Hebrew in LaTeX**: https://www.ctan.org/pkg/babel-hebrew
