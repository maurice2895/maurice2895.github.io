/* 조재연 강사 홈페이지 복사 방지 스크립트 (모든 페이지 공용)
   - 마우스 오른쪽 버튼, 글자 선택·복사·잘라내기, 이미지 끌어가기, 저장·소스보기·인쇄 단축키를 제한합니다.
   - 복사를 시도하면 클립보드에 내용 대신 저작권 안내 문구가 들어갑니다.
   - 참고: 공개 웹사이트는 화면 캡처, 브라우저 개발자 도구, 저장소(GitHub) 열람까지 완전히 막을 수 없습니다.
     이 스크립트는 일반 방문자의 손쉬운 복사를 줄이는 억제 장치입니다.
   - 검색엔진과 AI 검색 수집기는 HTML 원문을 읽으므로 검색 노출에는 영향을 주지 않습니다. */
(() => {
  "use strict";
  const NOTICE = "© 조재연 강사 (https://maurice2895.github.io/) — 이 사이트의 글·이미지·디자인은 무단 복제·배포를 금지합니다.";
  const root = document.documentElement;
  root.classList.add("protect");

  const isEditable = (target) =>
    target instanceof Element && Boolean(target.closest("input, textarea, select, [contenteditable='true']"));

  const block = (event) => {
    if (!isEditable(event.target)) event.preventDefault();
  };

  document.addEventListener("contextmenu", block);
  document.addEventListener("dragstart", block);
  document.addEventListener("selectstart", block);

  const onCopy = (event) => {
    if (isEditable(event.target)) return;
    event.preventDefault();
    if (event.clipboardData) event.clipboardData.setData("text/plain", NOTICE);
  };
  document.addEventListener("copy", onCopy);
  document.addEventListener("cut", onCopy);

  document.addEventListener("keydown", (event) => {
    const code = event.code || "";
    const mod = event.ctrlKey || event.metaKey;
    if (code === "F12") { event.preventDefault(); return; }
    /* 개발자 도구: Ctrl+Shift+I/J/C (Windows), Cmd+Option+I/J/C/U (Mac) */
    if (mod && (event.shiftKey || event.altKey) && ["KeyI", "KeyJ", "KeyC", "KeyU"].includes(code)) {
      event.preventDefault();
      return;
    }
    if (!mod) return;
    /* 저장(S)·소스 보기(U)·인쇄(P) */
    if (["KeyS", "KeyU", "KeyP"].includes(code)) { event.preventDefault(); return; }
    /* 전체 선택(A)·복사(C)·잘라내기(X) — 입력칸에서는 허용 */
    if (["KeyA", "KeyC", "KeyX"].includes(code) && !isEditable(event.target)) event.preventDefault();
  });
})();
