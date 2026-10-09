"""Bounded PDF page rendering for optional native note attachments."""
import io
import math

MAX_PAGES = 32
MAX_RENDERED_BYTES = 64 * 1024 * 1024


def render_pdf_pages(data):
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise ValueError('PDF page mode needs pypdfium2: py -m pip install -r requirements-pdf.txt') from exc
    try:
        document = pdfium.PdfDocument(data)
    except pdfium.PdfiumError as exc:
        raise ValueError('PDF cannot be opened (invalid or password protected)') from exc
    pages, total = [], 0
    try:
        count = len(document)
        if not 1 <= count <= MAX_PAGES:
            raise ValueError('PDF page count must be between 1 and 32')
        for index in range(count):
            page = document[index]
            try:
                width, height = page.get_size()
                if not all(math.isfinite(v) and v > 0 for v in (width, height)):
                    raise ValueError('PDF page has invalid dimensions')
                # Up to 144 dpi, capped at 2400 pixels per side / 5.76 MP.
                scale = min(2.0, 2400 / max(width, height))
                bitmap = page.render(scale=scale)
                try:
                    image = bitmap.to_pil()
                    try:
                        stream = io.BytesIO()
                        image.save(stream, 'PNG')
                        png = stream.getvalue()
                    finally:
                        image.close()
                finally:
                    bitmap.close()
                total += len(png)
                if total > MAX_RENDERED_BYTES:
                    raise ValueError('Rendered PDF exceeds 64 MiB limit')
                pages.append(png)
            finally:
                page.close()
    except pdfium.PdfiumError as exc:
        raise ValueError('PDF page rendering failed') from exc
    finally:
        document.close()
    return pages
