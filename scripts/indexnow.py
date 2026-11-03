#!/usr/bin/env python3
"""IndexNow 검색엔진 알림 스크립트

홈페이지가 바뀌면 sitemap.xml에 있는 주소를 IndexNow로 제출합니다.
IndexNow 규칙에 따라 한 곳(api.indexnow.org)에만 제출하면
참여 검색엔진(Bing, 네이버 등)에 자동으로 공유됩니다.

- GitHub Actions(.github/workflows/indexnow.yml)에서 자동 실행됩니다.
- 실제 사이트에 새 내용이 올라온 것을 확인한 뒤에 제출합니다.
- 직접 실행: python scripts/indexnow.py            (확인 후 제출)
            python scripts/indexnow.py --dry-run  (제출하지 않고 내용만 출력)
"""
import json
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = "dentalsolve.kr"
KEY = "254b7bd0955f7cd140d82f0f30a69fab"
ENDPOINT = "https://api.indexnow.org/indexnow"
WAIT_SECONDS = 600      # 배포 완료를 기다리는 최대 시간(10분)
POLL_INTERVAL = 20

RESULT_TEXT = {
    200: "제출 성공",
    202: "접수됨 (키 확인 대기 중 — 첫 제출에서는 정상입니다)",
    400: "형식 오류",
    403: "키가 올바르지 않음 (키 파일을 확인하세요)",
    422: "사이트 주소와 맞지 않는 URL 또는 키 형식 오류",
    429: "요청이 너무 잦음 — 10분 이상 지난 뒤 다시 시도하세요",
}


def sitemap_urls():
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(ROOT / "sitemap.xml")
    urls = [n.text.strip() for n in tree.findall(".//sm:loc", ns) if n.text]
    return [u for u in urls if u.startswith(f"https://{HOST}/")]


def local_file(url):
    path = url.split(HOST, 1)[1].lstrip("/")
    return ROOT / (path + "index.html" if (not path or path.endswith("/")) else path)


def fetch(url):
    req = urllib.request.Request(f"{url}?indexnow-check={int(time.time())}",
                                 headers={"Cache-Control": "no-cache", "User-Agent": "indexnow-check"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def wait_for_deploy(urls):
    """실제 사이트의 키 파일과 각 페이지가 저장소 내용과 같아질 때까지 기다립니다."""
    checks = [(f"https://{HOST}/{KEY}.txt", KEY.encode())]
    checks += [(u, local_file(u).read_bytes()) for u in urls if local_file(u).is_file()]
    deadline = time.time() + WAIT_SECONDS
    while True:
        pending = []
        for url, expected in checks:
            try:
                live = fetch(url)
                if live.strip() != expected.strip():
                    pending.append(url)
            except (urllib.error.URLError, TimeoutError):
                pending.append(url)
        if not pending:
            print(f"배포 확인 완료: 키 파일과 페이지 {len(checks) - 1}개가 최신 상태입니다.")
            return True
        if time.time() > deadline:
            print("경고: 10분 안에 배포 완료를 확인하지 못했습니다. 아직 바뀌지 않은 주소:", *pending, sep="\n  ")
            return False
        print(f"배포 대기 중... (남은 주소 {len(pending)}개)")
        time.sleep(POLL_INTERVAL)


def main():
    dry_run = "--dry-run" in sys.argv
    key_file = ROOT / f"{KEY}.txt"
    if not key_file.is_file() or key_file.read_text(encoding="utf-8").strip() != KEY:
        print(f"오류: 키 파일 {KEY}.txt 가 없거나 내용이 키와 다릅니다.")
        return 1

    urls = sitemap_urls()
    if not urls:
        print("오류: sitemap.xml 에서 제출할 주소를 찾지 못했습니다.")
        return 1
    payload = {"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": urls}
    print("제출할 주소:", *urls, sep="\n  ")
    if dry_run:
        print("\n[dry-run] 제출하지 않았습니다.\n" + json.dumps(payload, ensure_ascii=False, indent=1))
        return 0

    if not wait_for_deploy(urls):
        print("오류: 배포 확인에 실패하여 IndexNow 제출을 중단합니다. 배포 상태를 확인한 뒤 다시 실행하세요.")
        return 1

    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            status = res.status
    except urllib.error.HTTPError as err:
        status = err.code
    except urllib.error.URLError as err:
        print(f"오류: IndexNow 서버에 연결하지 못했습니다 ({err.reason}).")
        return 1

    print(f"\nIndexNow 응답: {status} — {RESULT_TEXT.get(status, '알 수 없는 응답')}")
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
