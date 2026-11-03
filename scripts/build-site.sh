#!/usr/bin/env bash
# Cloudflare Pages 배포용 빌드 스크립트
# - 저장소에서 웹사이트에 필요한 파일만 _site 폴더로 복사합니다.
# - 저장소 관리용 파일(scripts, .github, README.md, CNAME 등)은 웹에 올라가지 않습니다.
# - Cloudflare Pages 설정: 빌드 명령 = bash scripts/build-site.sh, 빌드 출력 디렉터리 = _site
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="_site"
rm -rf "$OUT"
mkdir "$OUT"

shopt -s dotglob nullglob
for item in *; do
  case "$item" in
    .git|.github|.gitignore|.nojekyll|.DS_Store|scripts|README.md|CNAME|"$OUT") continue ;;
  esac
  cp -R "$item" "$OUT/"
done

# 필수 파일이 빠지면 배포를 멈춥니다.
for required in index.html 404.html _headers robots.txt sitemap.xml security.js site.css site.js; do
  if [ ! -f "$OUT/$required" ]; then
    echo "오류: $required 파일이 없어 배포를 중단합니다." >&2
    exit 1
  fi
done

echo "배포 파일 준비 완료: $(find "$OUT" -type f | wc -l)개"
