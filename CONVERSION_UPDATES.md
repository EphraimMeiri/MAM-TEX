# MAM to TEX Conversion Updates

## Summary of Changes

This document summarizes the updates made to the MAM→TEX conversion code to work with the new MAM-parsed data format and implement configurable settings.

## Key Improvements

### 1. Updated to New MAM Data Format
- **Source**: Now uses data from [MAM-parsed repository](https://github.com/bdenckla/MAM-parsed)
- **Format**: Updated from old format (`body`, `book_name`) to new format (`book39s`, `book24_name`)
- **File Mapping**: Added complete mapping from English book names to new file naming scheme
- **Path Detection**: Automatically detects MAM-parsed data in multiple locations

### 2. Configurable Settings (to_TEX2.py)

#### Setting 1: Notes Control
- **Variable**: `using_ednotes` (True/False)
- **Purpose**: Controls whether to include textual apparatus notes in the output
- **With Notes**: Generates `\edtext{}` commands with critical apparatus
- **Without Notes**: Generates clean text without notes

#### Setting 2: Column Markers for Poetic Books
- **Variable**: `use_column_markers` (True/False)
- **Purpose**: Applies special formatting for songs/poetry using column markers
- **Affects**: Psalms, Job, Proverbs
- **Functions**: `psalms_postprocess()`, `job_postprocessing()`, `emet_postprocess()`

### 3. Support for New Template Format (stmpl)

Added comprehensive support for the new `stmpl` (structured template) format used in MAM-parsed:

**Supported Templates:**
- `מ:קמץ` - Grammatical forms
- `ר0`, `ר1`, `ר2`, `ר3` - Spacing and layout markers
- `מ:לגרמיה`, `מ:לגרמיה-2` - Text spacing
- `כו"ק`, `קו"כ` - Ketiv/Qere variants
- `קרי ולא כתיב`, `כתיב ולא קרי` - Ketiv/Qere special cases
- `מ:אות-ג`, `מ:אות-ק` - Large and small letters
- `מ:אות מנוקדת` - Pointed letters
- `מ:מקף אפור` - Gray makaf
- `מ:דחי` - Dagesh/hiriq corrections
- `מ:צינור` - Vertical pipe
- `גלגל`, `גלגל-2` - Galgal te'amim
- And more...

### 4. Code Quality Improvements
- Fixed Python 2 to Python 3 compatibility (`has_key` → `in`)
- Added proper None handling to prevent concatenation errors
- Improved error messages and debugging output
- Better handling of missing templates

## Generated Files

The updated code successfully generates TEX files with different configurations:

### Test Outputs (validated):
1. **MAM-Ruth.tex** - With notes and column markers (18KB)
2. **MAM-Ruth_noNotes.tex** - Without notes (14KB)
3. **MAM-Psalms.tex** - With notes and column markers (293KB)
4. **MAM-Psalms_noNotes.tex** - Without notes (264KB)

All files validated for:
- ✓ Balanced braces
- ✓ Proper LaTeX document structure
- ✓ Hebrew text encoding
- ✓ Appropriate use of critical apparatus based on settings

## File Naming Convention

Output files use the following naming scheme:
- Base: `MAM-{BookName}.tex`
- Without notes: `MAM-{BookName}_noNotes.tex`
- Without column markers: `MAM-{BookName}_noColumns.tex`
- Both: `MAM-{BookName}_noNotes_noColumns.tex`

## Book Name Mappings

```python
'Genesis': 'A1-Genesis',
'Exodus': 'A2-Exodus',
'Leviticus': 'A3-Levit',
'Numbers': 'A4-Numbers',
'Deuteronomy': 'A5-Deuter',
'Joshua': 'B1-Joshua',
'Judges': 'B2-Judges',
'Samuel': 'BA-Samuel',
'Kings': 'BC-Kings',
'Isaiah': 'C1-Isaiah',
'Jeremiah': 'C2-Jeremiah',
'Ezekiel': 'C3-Ezekiel',
'The-12': 'CA-The-12-Minor-Prophets',
'Psalms': 'D1-Psalms',
'Proverbs': 'D2-Proverbs',
'Job': 'D3-Job',
'Song': 'E1-Song of Songs',
'Ruth': 'E2-Ruth',
'Lamentations': 'E3-Lamentations',
'Ecclesiastes': 'E4-Ecclesiastes',
'Esther': 'E5-Esther',
'Daniel': 'F1-Daniel',
'Ezra': 'FA-Ezra-Nexemiah',
'Chronicles': 'FC-Chronicles',
```

## Usage

### Prerequisites
1. Clone MAM-parsed data: `git clone https://github.com/bdenckla/MAM-parsed.git`
2. Install required packages: `reledmac`, `polyglossia`, Hebrew fonts (`Taamey D`, `Aharoni`)

### Running the Conversion

```python
# Edit to_TEX2.py to set your preferences:
using_ednotes = False      # Set to True for notes
use_column_markers = True  # Set to False to disable column formatting

# Then run:
python3 to_TEX2.py
```

### Compiling to PDF

```bash
cd out
xelatex -interaction=nonstopmode MAM-{BookName}.tex
# Run 3-5 times for proper cross-references
xelatex -interaction=nonstopmode MAM-{BookName}.tex
xelatex -interaction=nonstopmode MAM-{BookName}.tex
```

## Next Steps

1. **Compile PDFs**: Run XeLaTeX on generated files in an environment with LaTeX installed
2. **Review Output**: Check PDF output for formatting, Hebrew rendering, and notes placement
3. **Expand Coverage**: Generate TEX files for additional books beyond Ruth and Psalms
4. **Fine-tune Templates**: Add handlers for any remaining edge-case templates as needed

## Notes

- LaTeX compilation requires XeLaTeX (not pdfLaTeX) due to Hebrew and Unicode support
- The `reledmac` package requires multiple compilation passes (3-5) for proper cross-references
- Some warnings about unknown templates are expected and can be addressed incrementally
