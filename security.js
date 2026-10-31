/* Browser-side deterrents and visible ownership watermark.
   Important: client-side code cannot prevent screenshots or guarantee copy protection. */
(() => {
  "use strict";

  const isImageTarget = (target) =>
    target instanceof Element && Boolean(target.closest("img, picture, .lecture-image"));

  // Discourage common browser actions on displayed images.
  document.addEventListener("contextmenu", (event) => {
    if (isImageTarget(event.target)) event.preventDefault();
  });

  document.addEventListener("dragstart", (event) => {
    if (isImageTarget(event.target)) event.preventDefault();
  });

  document.addEventListener("copy", (event) => {
    if (isImageTarget(window.getSelection()?.anchorNode?.parentElement || event.target)) {
      event.preventDefault();
    }
  });

  // Prevent image selection while keeping normal text and form fields usable.
  const style = document.createElement("style");
  style.textContent = `
    img, picture, .lecture-image {
      -webkit-user-drag: none !important;
      user-drag: none !important;
      -webkit-touch-callout: none;
    }
    img::selection { background: transparent; }
    body::after {
      content: "DENTALSOLVE  ·  자료 무단 복제 금지";
      position: fixed;
      inset: 0;
      z-index: 9998;
      pointer-events: none;
      display: grid;
      place-items: center;
      color: rgba(20, 38, 63, .055);
      font: 800 clamp(18px, 2.2vw, 30px)/1.4 'Pretendard Variable', sans-serif;
      letter-spacing: .12em;
      transform: rotate(-24deg);
      text-align: center;
      white-space: nowrap;
      text-shadow: 0 0 1px rgba(255,255,255,.08);
    }
    @media print {
      body::after {
        content: "DENTALSOLVE · 무단 복제 금지";
        color: rgba(20, 38, 63, .16);
      }
    }
  `;
  document.head.appendChild(style);
})();