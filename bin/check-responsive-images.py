"""Fail deployment if a generated page references an absent responsive image."""

from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class ResponsiveImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "source" and attrs.get("type") == "image/webp":
            self.urls.extend(
                item.strip().split()[0]
                for item in attrs.get("srcset", "").split(",")
                if item.strip()
            )


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
images = set()
for page in root.rglob("*.html"):
    parser = ResponsiveImages()
    parser.feed(page.read_text())
    for url in parser.urls:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            continue
        path = unquote(parsed.path)
        images.add(root / path.lstrip("/") if path.startswith("/") else page.parent / path)

missing = sorted(str(image.relative_to(root)) for image in images if not image.is_file() or image.stat().st_size == 0)
if not images or missing:
    raise SystemExit("Missing responsive images: " + (", ".join(missing) or "no image sources generated"))
print(f"Verified {len(images)} responsive image files referenced by the built site.")
