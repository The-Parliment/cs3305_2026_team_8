#!/bin/bash
set -e

SCRIPTS="scripts"
TEMP_MD="temp-report.md"

# Keep only the main report body for pandoc
tail -n +47 REPORT.md > "$TEMP_MD"

pandoc meta.yaml "$TEMP_MD" -o REPORT.pdf \
  --pdf-engine=xelatex \
  --include-in-header="$SCRIPTS/table-preamble.tex" \
  --include-in-header="$SCRIPTS/code-fancy.tex" \
  --include-in-header="$SCRIPTS/spacing.tex" \
  --lua-filter="$SCRIPTS/mermaid.lua" \
  --lua-filter="$SCRIPTS/mermaid-scale.lua" \
  --lua-filter="$SCRIPTS/tabwidths.lua" \
  --highlight-style=kate \
  -V monofont="Noto Sans Mono"

rm -f "$TEMP_MD"
rm -f *.mmd
rm -f *.png