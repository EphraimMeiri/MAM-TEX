#!/bin/bash
# MAM-TEX Compilation Script
# Compiles all generated TEX files to PDF using XeLaTeX

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OUTPUT_DIR="out"
COMPILE_PASSES=3

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}MAM-TEX Compilation Script${NC}"
echo -e "${BLUE}=====================================${NC}\n"

# Check for XeLaTeX
if ! command -v xelatex &> /dev/null; then
    echo -e "${RED}ERROR: xelatex not found${NC}"
    echo "Please install TeX Live with XeLaTeX support:"
    echo "  Ubuntu/Debian: sudo apt-get install texlive-xetex texlive-lang-other"
    echo "  macOS: brew install --cask mactex"
    echo "  Or download from: https://www.tug.org/texlive/"
    exit 1
fi

# Check for required packages
echo -e "${BLUE}Checking LaTeX packages...${NC}"
if ! kpsewhich reledmac.sty &> /dev/null; then
    echo -e "${YELLOW}WARNING: reledmac package not found${NC}"
    echo "Install with: sudo apt-get install texlive-humanities"
fi

if ! kpsewhich polyglossia.sty &> /dev/null; then
    echo -e "${YELLOW}WARNING: polyglossia package not found${NC}"
    echo "Install with: sudo apt-get install texlive-latex-extra"
fi

# Check for Hebrew fonts
echo -e "\n${BLUE}Checking Hebrew fonts...${NC}"
if fc-list | grep -qi "taamey"; then
    echo -e "${GREEN}✓ Taamey font found${NC}"
else
    echo -e "${YELLOW}WARNING: Taamey font not found${NC}"
    echo "Install with: sudo apt-get install culmus"
fi

# Change to output directory
cd "$OUTPUT_DIR" || exit 1

# Find all TEX files
TEX_FILES=($(ls MAM-*.tex 2>/dev/null))

if [ ${#TEX_FILES[@]} -eq 0 ]; then
    echo -e "${RED}No TEX files found in $OUTPUT_DIR${NC}"
    exit 1
fi

echo -e "\n${BLUE}Found ${#TEX_FILES[@]} TEX file(s) to compile${NC}\n"

# Compile each file
TOTAL_FILES=${#TEX_FILES[@]}
COMPILED=0
FAILED=0

for tex_file in "${TEX_FILES[@]}"; do
    echo -e "${BLUE}────────────────────────────────────${NC}"
    echo -e "${BLUE}Compiling: $tex_file${NC}"
    echo -e "${BLUE}────────────────────────────────────${NC}"

    basename="${tex_file%.tex}"

    # Compile multiple times for cross-references
    for pass in $(seq 1 $COMPILE_PASSES); do
        echo -e "Pass $pass/$COMPILE_PASSES..."

        if xelatex -interaction=nonstopmode "$tex_file" > "${basename}_pass${pass}.log" 2>&1; then
            # Check for errors in log
            if grep -qi "error" "${basename}_pass${pass}.log"; then
                echo -e "${RED}✗ Pass $pass completed with errors${NC}"
                FAILED=$((FAILED + 1))
                break
            else
                echo -e "${GREEN}✓ Pass $pass completed${NC}"
            fi
        else
            echo -e "${RED}✗ Pass $pass failed${NC}"
            FAILED=$((FAILED + 1))
            break
        fi
    done

    # Check if PDF was created
    if [ -f "${basename}.pdf" ]; then
        pdf_size=$(du -h "${basename}.pdf" | cut -f1)
        echo -e "${GREEN}✓ Generated: ${basename}.pdf (${pdf_size})${NC}"
        COMPILED=$((COMPILED + 1))
    else
        echo -e "${RED}✗ Failed to generate PDF${NC}"
        echo -e "Check ${basename}_pass*.log for errors"
        FAILED=$((FAILED + 1))
    fi

    echo ""
done

# Summary
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Compilation Summary${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "Total files:   $TOTAL_FILES"
echo -e "${GREEN}Compiled:      $COMPILED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed:        $FAILED${NC}"
fi
echo -e "${BLUE}=====================================${NC}"

# Clean up auxiliary files (optional)
read -p "Clean up auxiliary files (.aux, .log, etc.)? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}Cleaning up...${NC}"
    rm -f *.aux *.log *.out *.toc *.1 *.1R *.end *.eledsec* *_pass*.log
    echo -e "${GREEN}✓ Cleaned up auxiliary files${NC}"
fi

exit 0
