# PDF and print export

Use this when the user asks for a PDF, a print-ready page, a one-pager, a report, or a downloadable document. Design for print from the start; do not design for screen and then shrink it.

## Page contract

Before building, fix these in the page:

- Page size and orientation: A4 or Letter, portrait unless the content needs landscape.
- Margins: 15-20 mm for A4, 0.6-0.75 in for Letter.
- Page-count target: one page for a one-pager, otherwise let content decide.
- Color: required brand color, or grayscale-safe.
- Links: expanded as text when the PDF is read offline.

Read [adapt.md](adapt.md) for the screen-to-print content and layout changes.

## CSS

Put the print contract in the page, not in the exporter:

```css
@page {
  size: A4 portrait;
  margin: 18mm;
}

@media print {
  nav, .actions, button, [role="button"] { display: none !important; }
  a[href^="http"]::after { content: " (" attr(href) ")"; font-size: 0.85em; }
  .card, figure, table, pre { break-inside: avoid; }
  h1, h2, h3 { break-after: avoid; }
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
```

- Use one column. Expand content that was hidden behind tabs or accordions.
- Keep real text; never ship text as an image.
- Give charts print labels and a grayscale-safe palette.
- Avoid hover-only affordances, fixed headers, and viewport-height layouts.
- Verify the screen and print render at the target page size.

Chrome does not implement CSS paged-media margin boxes, so page numbers cannot be added reliably with `@bottom-center`. If the user needs page numbers, add them in the document structure or use a post-processing step; otherwise state the limitation.

## Export

```bash
skills/impeccable/scripts/pdf-export.sh <url-or-html-file> <output.pdf>
```

The helper resolves local files to `file://`, waits for fonts and scripts, and prints the page with headless Chrome/Chromium. Useful environment variables:

- `CHROME_BIN=/path/to/chrome` when the binary is not on `PATH`.
- `PDF_WAIT_MS=10000` for slow pages or remote fonts.
- `CHROME_NO_SANDBOX=1` only inside a container.

For a dev server, pass its URL and make sure it is running. For a local file, use the HTML path. The script prints the absolute PDF path and, when available, page count and page size.

## Verify

```bash
pdfinfo out.pdf | grep -E '^(Pages|Page size|File size):'
pdftotext out.pdf - | head -40
pdftoppm -f 1 -singlefile -png -r 96 out.pdf page1
```

Check:

- No clipped or overlapping content at page breaks.
- Text is selectable and copied correctly.
- Fonts embedded; no fallback boxes.
- Color survives grayscale if the document may be printed in black and white.
- Links and URLs are readable offline.
- The page count matches the contract.

Report the absolute path, page count, and any untested item. A PDF that was never opened and checked is a draft.

## Failure modes

- **Blank PDF:** wrong URL, a page behind auth, or scripts still loading. Increase `PDF_WAIT_MS`, check the URL, or export a static build.
- **Missing fonts:** wait longer, self-host the font, or replace it with a system font.
- **Break through a card:** add `break-inside: avoid`; split the card if it exceeds one page.
- **Missing background color:** set `print-color-adjust: exact` and test the printer's grayscale mode.
- **Chrome refuses to start:** in a container, set `CHROME_NO_SANDBOX=1`; on a desktop, do not disable the sandbox.
