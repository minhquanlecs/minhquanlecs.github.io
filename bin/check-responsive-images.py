"""Check responsive images and the integrity of locally hosted dependencies."""

import base64
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


class ResponsiveImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.integrity = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "link") and attrs.get("integrity"):
            url = attrs.get("src") or attrs.get("href", "")
            if url.startswith("/assets/libs/"):
                self.integrity.append((url, attrs["integrity"]))
        if tag == "source" and attrs.get("type") == "image/webp":
            self.urls.extend(
                item.strip().split()[0]
                for item in attrs.get("srcset", "").split(",")
                if item.strip()
            )


root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
images = set()
libraries = set()
for page in root.rglob("*.html"):
    parser = ResponsiveImages()
    parser.feed(page.read_text())
    libraries.update(parser.integrity)
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
for url, integrity in libraries:
    data = (root / urlsplit(url).path.lstrip("/")).read_bytes()
    algorithm, expected = integrity.split("-", 1)
    actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode()
    if actual != expected:
        raise SystemExit("Library integrity mismatch: " + url)
for css in (root / "assets/libs").rglob("*.css"):
    for url in re.findall(r"url\(([^)]+)\)", css.read_text()):
        url = url.strip("\"'")
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            continue
        target = root / parsed.path.lstrip("/") if parsed.path.startswith("/") else css.parent / parsed.path
        if not target.is_file():
            raise SystemExit("Missing dependency asset: " + str(target))
print(f"Verified {len(libraries)} local dependency integrity hashes and their font/image resources.")
