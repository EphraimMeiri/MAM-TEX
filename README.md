# MAM-TEX

This Git repository converts [MAM (Miqra According to the Masorah)](https://en.wikisource.org/wiki/User:Dovi/Miqra_according_to_the_Masorah) from JSON to professionally typeset TEX/PDF files with full Hebrew cantillation marks and critical apparatus.

## Overview

The project uses the new parsed version of MAM from [bdenckla/MAM-parsed](https://github.com/bdenckla/MAM-parsed) and converts it to LaTeX format using the `reledmac` package for critical editions.

### Features

- ✅ **Full Hebrew Support**: Complete cantillation marks (te'amim) and vowel points (nikkud)
- ✅ **Configurable Output**: Generate with or without textual notes
- ✅ **Poetry Formatting**: Automatic column markers for Psalms, Job, and Proverbs
- ✅ **Critical Apparatus**: Ketiv/Qere variants and manuscript notes
- ✅ **Professional Typesetting**: Using the reledmac package for biblical editions

## Quick Start

### 1. Prerequisites

```bash
# Clone MAM data source
git clone https://github.com/bdenckla/MAM-parsed.git /tmp/MAM-parsed

# Install LaTeX (Ubuntu/Debian)
sudo apt-get install texlive-xetex texlive-humanities texlive-lang-other culmus

# Or on macOS
brew install --cask mactex
```

### 2. Generate TEX Files

```bash
# Edit configuration in to_TEX2.py (lines 17-18):
# using_ednotes = False    # Set True for notes
# use_column_markers = True  # Set True for poetry formatting

# Run conversion
python3 to_TEX2.py
```

### 3. Compile to PDF

```bash
# Option 1: Use provided script
./compile.sh

# Option 2: Manual compilation
cd out
xelatex -interaction=nonstopmode MAM-Ruth_noNotes.tex
xelatex -interaction=nonstopmode MAM-Ruth_noNotes.tex
xelatex -interaction=nonstopmode MAM-Ruth_noNotes.tex
```

## Configuration Settings

The conversion script (`to_TEX2.py`) has two main settings:

### Setting 1: Notes Control
```python
using_ednotes = False  # True = include textual apparatus notes
                       # False = clean text without notes
```

### Setting 2: Column Markers (Poetry)
```python
use_column_markers = True  # True = format songs using column layout
                           # False = standard paragraph layout
```

## Scripts

### `to_TEX2.py` - Main Conversion Script
Converts MAM JSON files to LaTeX TEX format with comprehensive template support.

**Supported Books**: All 24 books of the Hebrew Bible

**Output Files**:
- `MAM-{Book}.tex` - With notes and column markers
- `MAM-{Book}_noNotes.tex` - Without notes
- `MAM-{Book}_noColumns.tex` - Without column formatting
- `MAM-{Book}_noNotes_noColumns.tex` - Clean text only

### `to_TEX.py` - Legacy Script
Original conversion script (kept for reference).

### `to_html.py` - HTML Export
Creates HTML files of the nusach (textual) notes for each verse.

### `compile.sh` - Compilation Script
Automated script to compile all TEX files to PDF with proper multi-pass compilation.

## Documentation

- **[CONVERSION_UPDATES.md](CONVERSION_UPDATES.md)** - Details on the new format and updates
- **[COMPILATION_GUIDE.md](COMPILATION_GUIDE.md)** - Complete compilation instructions and troubleshooting

## Output Examples

Sample files are in the `out/` directory:
- `MAM-Ruth.tex` / `MAM-Ruth_noNotes.tex` - Book of Ruth
- `MAM-Psalms.tex` / `MAM-Psalms_noNotes.tex` - Book of Psalms
- Legacy TEX and PDF files from previous format

## Requirements

### LaTeX Packages
- `reledmac` - Critical apparatus (requires 3-pass compilation)
- `polyglossia` - Hebrew language support
- `xcolor` - Color support
- `titlesec`, `geometry`, `ragged2e` - Formatting

### Fonts
- **Taamey David (Taamey D)** - Main Hebrew font with te'amim
- **Aharoni** - Verse numbers (or substitute)

Install fonts: `sudo apt-get install culmus`

## Technical Details

### Template Support

The conversion now supports the new `stmpl` (structured template) format with handlers for:
- Ketiv/Qere variants (כו"ק, קו"כ)
- Special letters (large, small, pointed)
- Spacing markers (ר0, ר1, ר2, ר3)
- Layout elements (פסק, לגרמיה, מקף אפור)
- And 20+ more template types

### Validation

All generated TEX files are validated for:
- Balanced braces and brackets
- Proper LaTeX document structure
- Hebrew text encoding (UTF-8)
- Required package declarations

## Compilation Notes

**Important**: The `reledmac` package requires **3-5 compilation passes** for:
1. Basic text generation
2. Cross-reference processing
3. Apparatus and line number finalization

Use XeLaTeX (not pdfLaTeX) for proper Unicode and Hebrew support.

## Contributing

When adding support for new templates:
1. Add handler in `wtel_to_str()` function
2. Test with a sample book
3. Validate TEX output
4. Update documentation

## License

See [LICENSE.md](LICENSE.md) for details.

## References

- [MAM on Wikisource](https://en.wikisource.org/wiki/User:Dovi/Miqra_according_to_the_Masorah)
- [MAM-parsed Repository](https://github.com/bdenckla/MAM-parsed)
- [reledmac Package](https://ctan.org/pkg/reledmac)
