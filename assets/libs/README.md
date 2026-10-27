# Locally hosted dependencies

These are the same library versions and font families previously loaded from public CDNs. Keeping them on the site removes extra connections during the initial page load.

- jQuery 3.6.0: https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js
- MDB FREE 4.20.0: https://cdn.jsdelivr.net/npm/mdbootstrap@4.20.0/
- medium-zoom 1.1.0: https://cdn.jsdelivr.net/npm/medium-zoom@1.1.0/dist/medium-zoom.min.js
- Google Fonts: Roboto (300, 400, 500, 700), Roboto Slab (100, 300, 400, 500, 700), and Material Icons, with `font-display: swap` and all original Unicode subsets.

Original license files and copyright notices are retained. The font stylesheet changes only the font URLs to local copies. Script and MDB stylesheet bytes remain unchanged so their existing Subresource Integrity hashes stay valid.

When updating a library, use a new versioned directory and update its URL and integrity hash in `_config.yml`. `bin/check-responsive-images.py` checks local library hashes and font/image URLs in the built site before deployment. These files are excluded from automatic minification to preserve their published integrity hashes.
