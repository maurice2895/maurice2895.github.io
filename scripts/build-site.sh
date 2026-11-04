#!/usr/bin/env bash
# 공개할 파일만 배포합니다. 새 자료·소스·백업 파일은 자동 공개하지 않습니다.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="_site"
rm -rf "$OUT"
mkdir "$OUT"
PUBLIC_FILES=(index.html 404.html _headers _redirects robots.txt sitemap.xml rss.xml llms.txt
  security.js site.css site.js favicon.ico favicon.svg favicon-32.png apple-touch-icon.png og-image.png
  googlef97ab000014e40e4.html naver133c3117ea7348c1738597f91a5a3d64.html
  254b7bd0955f7cd140d82f0f30a69fab.txt)
PUBLIC_DIRS=(about consulting oneclick standardization ai-training emr-button-guide faq images)
for item in "${PUBLIC_FILES[@]}"; do
  test -f "$item" || { echo "필수 공개 파일 누락: $item" >&2; exit 1; }
  cp "$item" "$OUT/"
done
for dir in "${PUBLIC_DIRS[@]}"; do
  mkdir "$OUT/$dir"
  if [ "$dir" = images ]; then
    find "$dir" -maxdepth 1 -type f \( -name '*.svg' -o -name '*.webp' -o -name '*.png' -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.ico' \) -exec cp {} "$OUT/$dir/" \;
  else
    test -f "$dir/index.html" || { echo "페이지 누락: $dir/index.html" >&2; exit 1; }
    cp "$dir/index.html" "$OUT/$dir/"
  fi
done
echo "배포 파일 준비 완료: $(find "$OUT" -type f | wc -l)개"
