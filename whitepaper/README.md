# GSP White Paper Draft

This directory contains the 2026 draft of the GSP white paper.

The goal is a narrative technical paper for scientific visualization library developers. It is not
API reference and should not become a line-by-line restatement of the specs under `spec/`.

## Files

- `gsp-whitepaper.tex` - main LaTeX source.
- `gsp-whitepaper.pdf` - built PDF when available.
- `references.bib` - bibliography used by the paper.
- `NOTES_FOR_NICOLAS.md` - review packet and open questions.
- `figures/` - reusable explanatory figures plus current review-pack imagery.
- `capability_matrix_s030.md` - copied evidence used while drafting; not intended as a paper
  section.

## Build

```bash
cd whitepaper
latexmk -pdf -interaction=nonstopmode -halt-on-error gsp-whitepaper.tex
```

The draft uses ordinary `pdflatex` dependencies only.
