from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium


def main() -> None:
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG for visual QA.")
    parser.add_argument("pdf")
    parser.add_argument("out_dir")
    parser.add_argument("--scale", type=float, default=1.7)
    args = parser.parse_args()

    output = Path(args.out_dir)
    output.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(args.pdf)
    page_count = len(document)
    for index in range(page_count):
        page = document[index]
        image = page.render(scale=args.scale).to_pil()
        image.save(output / f"page-{index + 1}.png")
        page.close()
    document.close()
    print(f"Rendered {page_count} pages to {output}")


if __name__ == "__main__":
    main()
