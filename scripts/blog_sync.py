#!/usr/bin/env python3
"""네이버 블로그 최신 글 연동 스크립트

네이버 블로그(재연의 슬기로운 치과생활)의 공개 글 목록(RSS)을 읽어
홈페이지의 '최근 글' 칸에 제목·날짜·요약 한 줄·블로그 링크만 표시합니다.
글 전문은 홈페이지에 옮기지 않습니다.

- GitHub Actions(.github/workflows/blog-sync.yml)에서 매일 자동 실행됩니다.
- 직접 실행: python scripts/blog_sync.py
- 저장된 RSS 파일로 시험: python scripts/blog_sync.py --file 경로/feed.xml
"""
import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG_ID = "maurice2895"
FEED = f"https://rss.blog.naver.com/{BLOG_ID}.xml"
# 표시할 위치와 글 개수
TARGETS = [("index.html", 3), ("column/index.html", 9)]
SITEMAP_URLS = {"index.html": "https://dentalsolve.kr/", "column/index.html": "https://dentalsolve.kr/column/"}
START, END = "<!-- BLOG:START -->", "<!-- BLOG:END -->"
KST = timezone(timedelta(hours=9))
SUMMARY_LIMIT = 70


def read_feed(argv):
    if len(argv) == 3 and argv[1] == "--file":
        return Path(argv[2]).read_bytes()
    request = urllib.request.Request(FEED, headers={
        "User-Agent": "Mozilla/5.0 (compatible; dentalsolve-blog-sync/1.0; +https://dentalsolve.kr/)"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def clean_link(link):
    """추적용 꼬리표를 떼고 블로그 글 주소만 남깁니다."""
    link = link.strip().split("?")[0].split("#")[0]
    match = re.fullmatch(r"https?://(?:m\.)?blog\.naver\.com/([A-Za-z0-9_-]+)/(\d+)", link)
    if not match or match.group(1) != BLOG_ID:
        return None
    return f"https://blog.naver.com/{BLOG_ID}/{match.group(2)}"


def summary(description):
    text = re.sub(r"<[^>]+>", " ", html.unescape(description or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= SUMMARY_LIMIT else text[:SUMMARY_LIMIT].rstrip() + "…"


def posts(raw):
    result = []
    for item in ET.fromstring(raw).findall("./channel/item"):
        title = re.sub(r"\s+", " ", item.findtext("title") or "").strip()
        link = clean_link(item.findtext("link") or "")
        if not title or not link:
            continue
        try:
            date = parsedate_to_datetime(item.findtext("pubDate")).astimezone(KST).strftime("%Y.%m.%d")
        except (TypeError, ValueError):
            date = ""
        result.append((date, title, link, summary(item.findtext("description"))))
    return result


def card(date, title, link, text):
    esc = lambda value: html.escape(value, quote=True)
    meta = f"{date} · 네이버 블로그" if date else "네이버 블로그"
    body = f"<p>{esc(text)}</p>" if text else ""
    return (f'<a class="card" href="{esc(link)}" target="_blank" rel="noopener noreferrer">'
            f'<span class="card-no">{esc(meta)}</span><h3>{esc(title)}</h3>{body}'
            f'<span class="card-link">블로그에서 읽기 ↗<span class="sr-only">(새 창)</span></span></a>')


def touch_sitemap(urls):
    path = ROOT / "sitemap.xml"
    text = path.read_text(encoding="utf-8")
    today = datetime.now(KST).strftime("%Y-%m-%d")
    for url in urls:
        text = re.sub(rf"(<loc>{re.escape(url)}</loc>\s*<lastmod>)[0-9-]+(</lastmod>)", rf"\g<1>{today}\g<2>", text)
    path.write_text(text, encoding="utf-8")


def main(argv):
    try:
        items = posts(read_feed(argv))
    except Exception as exc:  # 네트워크·형식 오류: 기존 내용은 그대로 둡니다.
        print(f"::error::네이버 블로그 글 목록을 읽지 못했습니다: {exc}")
        return 1
    if not items:
        print("::error::네이버 블로그 글 목록이 비어 있습니다. 기존 내용을 그대로 둡니다.")
        return 1
    changed = []
    for rel, limit in TARGETS:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        start = text.index(START) + len(START)
        end = text.index(END)
        block = "".join(card(*item) for item in items[:limit])
        if text[start:end] != block:
            path.write_text(text[:start] + block + text[end:], encoding="utf-8")
            changed.append(rel)
    if changed:
        touch_sitemap([SITEMAP_URLS[rel] for rel in changed])
    print(f"블로그 글 {len(items)}개 확인 · 바뀐 파일: {', '.join(changed) if changed else '없음'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
