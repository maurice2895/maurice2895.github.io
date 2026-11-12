#!/usr/bin/env python3
"""Prove the deployment guard catches broken SEO and page mappings."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SiteGuardTests(unittest.TestCase):
    def check_copy(self, path=None, old=None, new=None):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory) / "site"
            shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns(".git", "_site", "__pycache__"))
            if path:
                file = site / path
                text = file.read_text(encoding="utf-8")
                self.assertIn(old, text)
                file.write_text(text.replace(old, new, 1), encoding="utf-8")
            return subprocess.run([sys.executable, str(site / "scripts/site_check.py")],
                                  capture_output=True, text=True)

    def test_valid_site(self):
        result = self.check_copy()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bad_mappings_are_rejected(self):
        cases = [
            ("index.html", 'content="https://dentalsolve.kr/og-image.png?v=20261104"',
             'content="https://dentalsolve.kr/missing-preview.png"', "internal reference not found"),
            ("site.css", "url(/images/icon-kakao.svg)", "url(/images/missing-icon.svg)",
             "CSS asset not found"),
            ("index.html", 'href="#main"', 'href="#missing-section"', "fragment target not found"),
            ("about/index.html", 'href="https://dentalsolve.kr/about/"',
             'href="https://dentalsolve.kr/"', "canonical must be"),
            ("members/index.html", "noindex,nofollow", "index,follow", "must remain noindex"),
            ("tools/card/index.html", "noindex,nofollow", "index,follow", "must remain noindex"),
            ("tools/insurance/index.html", "noindex,nofollow", "index,follow", "must remain noindex"),
            ("index.html", 'content="index, follow', 'content="noindex, follow', "unexpectedly noindex"),
            ("sitemap.xml", "https://dentalsolve.kr/about/", "https://dentalsolve.kr/members/",
             "sitemap/public page mismatch"),
            ("rss.xml", "https://dentalsolve.kr/consulting/", "https://dentalsolve.kr/members/",
             "RSS items must map"),
            ("index.html", '"@context":', '"@context" BROKEN:', "invalid structured data"),
            ("robots.txt", "Allow: /", "Disallow: /", "robots.txt blocks Googlebot"),
            ("index.html", 'alt="치과 전자차트 처치 버튼과 차팅 기록 화면 일러스트"',
             'data-removed-alt="description"', "image is missing alt attribute"),
            ("sitemap.xml", '<image:loc>https://dentalsolve.kr/images/dentalsolve-electronic-chart-consulting.svg</image:loc>',
             '<image:loc>https://dentalsolve.kr/members/private.webp</image:loc>',
             "sitemap images do not match visible content images"),
            ("robots.txt", "Allow: /", "Disallow: /images/", "robots.txt blocks image"),
        ]
        for path, old, new, message in cases:
            with self.subTest(path=path, message=message):
                result = self.check_copy(path, old, new)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout)


if __name__ == "__main__":
    unittest.main()

