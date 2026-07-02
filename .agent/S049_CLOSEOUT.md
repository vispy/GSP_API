# S049 Closeout - GSP White Paper Draft

## Result

Prepared a first serious 2026 GSP white paper draft for review by Nicolas Rougier and Cyrille
Rossant.

## Produced

- `whitepaper/gsp-whitepaper.tex`
- `whitepaper/gsp-whitepaper.pdf`
- `whitepaper/references.bib`
- `whitepaper/README.md`
- `whitepaper/NOTES_FOR_NICOLAS.md`
- `whitepaper/figures/`
- `whitepaper/capability_matrix_s030.md`

## Draft Scope

The draft is a narrative technical white paper aimed at scientific visualization library developers.
It positions GSP as a semantic graphics server protocol below plotting APIs and above concrete
renderers, not as API reference.

Main concepts covered:

- motivation and primitive decomposition;
- what GSP is not;
- session/protocol boundary;
- control plane and data plane;
- transport independence;
- semantic visual families;
- capabilities and explicit adaptation;
- query/readback;
- illustrative protocol/code snippets;
- Matplotlib, Datoviz, and VisPy2 roles;
- conformance fixtures and review packs;
- extensions, large data, and remote rendering;
- current implementation status and open work;
- relation to adjacent systems and community shape.

## Validation

- Built the PDF with:

```bash
cd whitepaper
latexmk -pdf -interaction=nonstopmode -halt-on-error gsp-whitepaper.tex
```

- Rendered pages to PNG with Poppler:

```bash
cd whitepaper
pdftoppm -png -r 120 gsp-whitepaper.pdf ../tmp/pdfs/gsp-whitepaper-page
```

- Visually inspected representative rendered pages: title, decomposition figure, architecture
  figure, conformance montage, and final references.
- Checked LaTeX log for warnings/overfull/underfull/undefined issues.
- Checked text files for non-ASCII characters.

## Notes

- The draft uses a small BibTeX reference set; citations are improved but still not exhaustive.
- The paper is not ready for public release without author review.
- `NOTES_FOR_NICOLAS.md` identifies the main feedback points for Nicolas.
