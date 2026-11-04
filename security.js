/* 공개 페이지의 간단한 복사를 억제합니다. 소스 열람·캡처·직접 요청을 완전히 막지는 못합니다.
   원문 HTML, 검색 로봇, 링크 이동, 입력 및 접근성 기능을 숨기거나 변경하지 않습니다. */
(() => {
  "use strict";
  const root = document.documentElement;
  if (root.dataset.contentGuard === "2026110415") return;
  root.dataset.contentGuard = "2026110415";
  root.classList.add("protect");
  const NOTICE = "© 덴탈솔브 · 조재연 (https://dentalsolve.kr/) — 글·이미지·디자인의 무단 복제·배포를 금지합니다.";
  const editable = (event) => {
    const path = typeof event.composedPath === "function" ? event.composedPath() : [event.target];
    return path.some(node => node instanceof Element &&
      (node.isContentEditable || Boolean(node.closest("input, textarea, select, [contenteditable]:not([contenteditable='false']), [data-allow-copy]"))));
  };
  const block = (event) => {
    if (!editable(event) && event.cancelable) event.preventDefault();
  };
  for (const name of ["contextmenu", "dragstart", "selectstart"]) {
    document.addEventListener(name, block, {capture: true, passive: false});
  }
  for (const name of ["copy", "cut"]) {
    document.addEventListener(name, event => {
      if (editable(event)) return;
      event.preventDefault();
      if (event.clipboardData) {
        event.clipboardData.clearData();
        event.clipboardData.setData("text/plain", NOTICE);
      }
    }, {capture: true});
  }
  document.addEventListener("keydown", event => {
    if (event.isComposing || editable(event)) return;
    const key = (event.key || "").toLowerCase();
    const code = event.code || "";
    const letter = code.startsWith("Key") ? code.slice(3).toLowerCase() : key;
    const mod = event.ctrlKey || event.metaKey;
    const inspection = mod && (event.shiftKey || event.altKey) && ["i", "j", "c", "u"].includes(letter);
    if (key === "f12" || code === "F12" || inspection ||
        (mod && ["s", "u", "p", "a", "c", "x"].includes(letter))) event.preventDefault();
  }, {capture: true});
  for (const image of document.images) image.draggable = false;
})();
