#!/usr/bin/env python3
"""Deployment matching permits the observed CDN beacon, not stale page content."""
import unittest
from indexnow import deployment_matches

URL = "https://dentalsolve.kr/"
PAGE = b'<html><head><meta name="robots" content="index"></head><body>Current</body></html>\n'
BEACON = b'<script type="module" src="https://static.cloudflareinsights.com/beacon.min.js/version" data-cf-beacon=\'{"r":1}\' crossorigin="anonymous"></script>\n'


class DeployMatchTests(unittest.TestCase):
    def test_unchanged_and_cdn_beacon(self):
        self.assertTrue(deployment_matches(URL, PAGE, PAGE))
        self.assertTrue(deployment_matches(URL, PAGE.replace(b"</body>", BEACON+b"</body>"), PAGE))

    def test_stale_text_and_noindex_are_rejected(self):
        for old, new in ((b"Current", b"Old"), (b'content="index"', b'content="noindex"')):
            with self.subTest(new=new):
                self.assertFalse(deployment_matches(URL, PAGE.replace(old, new), PAGE))

    def test_unrelated_scripts_are_rejected(self):
        for script in (b'<script src="https://example.com/beacon.min.js"></script>',
                       b'<script src="https://static.cloudflareinsights.com.evil.example/beacon.min.js"></script>',
                       b'<script src="https://static.cloudflareinsights.com/beacon.min.js">changed()</script>'):
            with self.subTest(script=script):
                self.assertFalse(deployment_matches(URL, PAGE.replace(b"</body>", script+b"</body>"), PAGE))

    def test_key_file_must_match(self):
        self.assertFalse(deployment_matches("https://dentalsolve.kr/key.txt", BEACON+b"key", b"key"))


if __name__ == "__main__":
    unittest.main()
