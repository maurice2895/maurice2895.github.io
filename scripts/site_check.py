#!/usr/bin/env python3
"""Static quality checks for the DentalSolve GitHub Pages site."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from urllib.robotparser import RobotFileParser
import sys
import json
from collections import Counter
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://dentalsolve.kr/"
ERRORS = []

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_open = False
        self.title = []
        self.description = ""
        self.canonical = ""
        self.refs = []
        self.ids = []
        self.h1_count = 0
        self.meta = {}
        self.schema_blocks = []
        self.schema_open = False
        self.schema_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta":
            self.meta[attrs.get("name", attrs.get("property", ""))] = attrs.get("content", "")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.schema_open = True
            self.schema_text = []
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
        if tag == "script" and self.schema_open:
            self.schema_blocks.append("".join(self.schema_text))
            self.schema_open = False
        if tag == "title":
            self.title_open = False

    def handle_data(self, data):
        if self.schema_open:
            self.schema_text.append(data)
        if self.title_open:
            self.title.append(data)

def fail(message):
    ERRORS.append(message)
    print("ERROR:", message)

# Google/Naver verification files and the noindex 404 page are utility documents.
html_files = sorted(
    file for file in ROOT.rglob("*.html")
    if not file.name.startswith(("google", "naver"))
    and not {"_site", ".git"}.intersection(file.relative_to(ROOT).parts)
)
if not html_files:
    fail("No HTML files were found.")

pages = {}
public_urls = set()
titles = {}
descriptions = {}
for file in html_files:
    rel = file.relative_to(ROOT).as_posix()
    parser = PageParser()
    try:
        parser.feed(file.read_text(encoding="utf-8"))
        parser.close()
    except Exception as exc:
        fail(f"{rel}: HTML parsing failed: {exc}")
        continue

    pages[file.resolve()] = parser
    if parser.h1_count != 1:
        fail(f"{rel}: expected one h1, found {parser.h1_count}")
    for value, count in Counter(parser.ids).items():
        if count > 1:
            fail(f"{rel}: duplicate HTML id: {value}")

    if rel != "404.html":
        if not "".join(parser.title).strip():
            fail(f"{rel}: missing page title")
        if not parser.description:
            fail(f"{rel}: missing meta description")
        if not parser.canonical:
            fail(f"{rel}: missing canonical URL")
        expected_url = urljoin(BASE, rel.removesuffix("index.html"))
        if parser.canonical != expected_url:
            fail(f"{rel}: canonical must be {expected_url}")

    noindex = "noindex" in parser.meta.get("robots", "").lower()
    if rel == "404.html" or rel.startswith("members/"):
        if not noindex:
            fail(f"{rel}: utility/member page must remain noindex")
    elif noindex:
        fail(f"{rel}: public page is unexpectedly noindex")
    else:
        public_urls.add(parser.canonical)
        title = "".join(parser.title).strip()
        if title in titles:
            fail(f"{rel}: duplicate title with {titles[title]}")
        if parser.description in descriptions:
            fail(f"{rel}: duplicate description with {descriptions[parser.description]}")
        titles[title] = rel
        descriptions[parser.description] = rel
        for key, expected in (("og:url", parser.canonical), ("og:title", title),
                              ("twitter:title", title), ("og:description", parser.description),
                              ("twitter:description", parser.description)):
            if parser.meta.get(key) != expected:
                fail(f"{rel}: {key} does not match page metadata")
        if not parser.schema_blocks:
            fail(f"{rel}: structured data is missing")
        for block in parser.schema_blocks:
            try:
                data = json.loads(block)
                graph = data.get("@graph", [data])
                node_ids = {node.get("@id") for node in graph if node.get("@id")}
                if not any(node.get("url") == parser.canonical for node in graph):
                    fail(f"{rel}: structured data does not describe canonical page")
                for node in graph:
                    breadcrumb = node.get("breadcrumb", {}).get("@id")
                    if breadcrumb and breadcrumb not in node_ids:
                        fail(f"{rel}: unresolved breadcrumb mapping: {breadcrumb}")
                    if node.get("@type") == "BreadcrumbList":
                        items = node.get("itemListElement", [])
                        if not items or items[-1].get("item") != parser.canonical:
                            fail(f"{rel}: breadcrumb does not end at canonical page")
                        if [item.get("position") for item in items] != list(range(1, len(items)+1)):
                            fail(f"{rel}: invalid breadcrumb positions")
            except (ValueError, TypeError, AttributeError) as exc:
                fail(f"{rel}: invalid structured data: {exc}")

    page_url = urljoin(BASE, rel)
    for ref in parser.refs:
        if ref.startswith(("mailto:", "tel:", "javascript:", "data:")):
            continue
        target_url = urljoin(page_url, ref)
        parsed = urlparse(target_url)
        if parsed.scheme not in ("http", "https") or parsed.netloc != "dentalsolve.kr":
            continue
        path = unquote(parsed.path).lstrip("/")
        target = ROOT / path if path else ROOT / "index.html"
        if path and (target.is_dir() or parsed.path.endswith("/")):
            target = target / "index.html"
        if not target.is_file():
            fail(f"{rel}: internal reference not found: {ref}")

# Resolve fragment links after all target HTML IDs have been collected.
for file, parser in pages.items():
    for ref in parser.refs:
        parsed = urlparse(urljoin(urljoin(BASE, file.relative_to(ROOT).as_posix()), ref))
        if parsed.netloc != "dentalsolve.kr" or not parsed.fragment:
            continue
        path = unquote(parsed.path).lstrip("/")
        target = ROOT / path if path else ROOT / "index.html"
        if target.is_dir():
            target /= "index.html"
        target_parser = pages.get(target.resolve())
        if target_parser and unquote(parsed.fragment) not in target_parser.ids:
            fail(f"{file.relative_to(ROOT)}: fragment target not found: {ref}")

robots = ROOT / "robots.txt"
if not robots.is_file():
    fail("robots.txt is missing")
else:
    robots_text = robots.read_text(encoding="utf-8")
    if "User-agent:" not in robots_text:
        fail("robots.txt has no User-agent directive")
    if "sitemap.xml" not in robots_text:
        fail("robots.txt does not reference sitemap.xml")
    rules = RobotFileParser()
    rules.parse(robots_text.splitlines())
    for agent in ("Googlebot", "Yeti", "bingbot"):
        for url in public_urls | {urljoin(BASE, "site.css"), urljoin(BASE, "site.js")}:
            if not rules.can_fetch(agent, url):
                fail(f"robots.txt blocks {agent}: {url}")

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
        if len(urls) != len(set(urls)):
            fail("sitemap.xml contains duplicate URLs")
        if set(urls) != public_urls:
            fail(f"sitemap/public page mismatch: {sorted(set(urls) ^ public_urls)}")
        for url in urls:
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "dentalsolve.kr":
                fail(f"sitemap contains an unexpected URL: {url}")
                continue
            path = unquote(parsed.path).lstrip("/")
            target = ROOT / path if path else ROOT / "index.html"
            if path and (target.is_dir() or parsed.path.endswith("/")):
                target = target / "index.html"
            if not target.is_file():
                fail(f"sitemap URL does not map to a file: {url}")
    except ET.ParseError as exc:
        fail(f"sitemap.xml is not valid XML: {exc}")

try:
    rss = ET.parse(ROOT / "rss.xml")
    links = [node.text.strip() for node in rss.findall("./channel/item/link") if node.text]
    if len(links) != len(set(links)) or set(links) != public_urls - {BASE}:
        fail("RSS items must map to every public subpage exactly once")
    for item in rss.findall("./channel/item"):
        if item.findtext("guid") != item.findtext("link"):
            fail("RSS guid does not match its page link")
except (ET.ParseError, OSError) as exc:
    fail(f"rss.xml could not be read: {exc}")

if ERRORS:
    print(f"\nSite check failed: {len(ERRORS)} error(s).")
    sys.exit(1)

print(f"Site check passed: {len(html_files)} HTML files checked; sitemap and internal references are valid.")
