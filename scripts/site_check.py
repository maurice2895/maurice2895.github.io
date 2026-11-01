#!/usr/bin/env python3
"""Static quality checks for the DentalSolve GitHub Pages site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://maurice2895.github.io/"
ERRORS = []

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_open = False
        self.title = []
        self.description = ""
        self.canonical = ""
        self.refs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.title_open = True
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "").strip()
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonical = attrs.get("href", "").strip()
        for key in ("href", "src"):
            value = attrs.get(key, "").strip()
            if value:
                self.refs.append(value)

    def handle_endtag(self, tag):
        if tag == "title":
            self.title_open = False

    def handle_data(self, data):
        if self.title_open:
            self.title.append(data)

def fail(message):
    ERRORS.append(message)
    print("ERROR:", message)

html_files = sorted(\n    file for file in ROOT.rglob("*.html")\n    if not file.name.startswith("google")\n)
if not html_files:
    fail("No HTML files were found.")

for file in html_files:
    rel = file.relative_to(ROOT).as_posix()
    parser = PageParser()
    try:
        parser.feed(file.read_text(encoding="utf-8"))
        parser.close()
    except Exception as exc:
        fail(f"{rel}: HTML parsing failed: {exc}")
        continue

    if not "".join(parser.title).strip():
        fail(f"{rel}: missing page title")
    if not parser.description:
        fail(f"{rel}: missing meta description")
    if not parser.canonical:
        fail(f"{rel}: missing canonical URL")

    page_url = urljoin(BASE, rel)
    for ref in parser.refs:
        if ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        target_url = urljoin(page_url, ref)
        parsed = urlparse(target_url)
        if parsed.scheme not in ("http", "https") or parsed.netloc != "maurice2895.github.io":
            continue
        path = unquote(parsed.path).lstrip("/")
        target = ROOT / path
        if not path:
            target = ROOT / "index.html"
        elif target.is_dir() or parsed.path.endswith("/"):
            target = target / "index.html"
        if not target.is_file():
            fail(f"{rel}: internal reference not found: {ref}")

robots = ROOT / "robots.txt"
if not robots.is_file():
    fail("robots.txt is missing")
else:
    robots_text = robots.read_text(encoding="utf-8")
    if "User-agent:" not in robots_text:
        fail("robots.txt has no User-agent directive")
    if "sitemap.xml" not in robots_text:
        fail("robots.txt does not reference sitemap.xml")

sitemap = ROOT / "sitemap.xml"
if not sitemap.is_file():
    fail("sitemap.xml is missing")
else:
    try:
        tree = ET.parse(sitemap)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [node.text.strip() for node in tree.findall(".//sm:loc", ns) if node.text]
        if not urls:
            fail("sitemap.xml contains no URLs")
        for url in urls:
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "maurice2895.github.io":
                fail(f"sitemap contains an unexpected URL: {url}")
                continue
            path = unquote(parsed.path).lstrip("/")
            target = ROOT / path if path else ROOT / "index.html"
            if target.is_dir() or parsed.path.endswith("/"):
                target = target / "index.html"
            if not target.is_file():
                fail(f"sitemap URL does not map to a file: {url}")
    except ET.ParseError as exc:
        fail(f"sitemap.xml is not valid XML: {exc}")

if ERRORS:
    print(f"\nSite check failed: {len(ERRORS)} error(s).")
    sys.exit(1)

print(f"Site check passed: {len(html_files)} HTML files checked; sitemap and internal references are valid.")
