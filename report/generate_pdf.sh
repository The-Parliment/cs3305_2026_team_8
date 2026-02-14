#!/bin/bash

SCRIPTS="scripts"

pandoc meta.yaml report.md -o report.pdf \
  --pdf-engine=xelatex \
  --include-in-header=$SCRIPTS/table-preamble.tex \
  --include-in-header=$SCRIPTS/code-fancy.tex \
  --lua-filter=$SCRIPTS/mermaid.lua \
  --lua-filter=$SCRIPTS/mermaid-scale.lua \
  --lua-filter=$SCRIPTS/tabwidths.lua \
  --highlight-style=kate \
  -V monofont="Noto Sans Mono" \
