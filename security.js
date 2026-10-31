/* Lightweight browser-side image deterrents and subtle brand watermark.
   Screenshots and external capture cannot be fully blocked in a public website. */
(() => {
  "use strict";

  const isImageTarget = (target) =>
    target instanceof Element && Boolean(target.closest("img, picture, .lecture-image"));

  document.addEventListener("contextmenu", (event) => {
    if (isImageTarget(event.target)) event.preventDefault();
  });

  document.addEventListener("dragstart", (event) => {
    if (isImageTarget(event.target)) event.preventDefault();
  });

  document.addEventListener("copy", (event) => {
    const selectedElement = window.getSelection()?.anchorNode?.parentElement;
    if (isImageTarget(selectedElement || event.target)) event.preventDefault();
  });

  const style = document.createElement("style");
  style.textContent = `
    img, picture, .lecture-image {
      -webkit-user-drag: none !important;
      user-drag: none !important;
      -webkit-touch-callout: none;
    }
    img::selection { background: transparent; }
    body::after {
      content: "덴탈솔브";
      position: fixed;
      inset: 0;
      z-index: 9998;
      pointer-events: none;
      display: grid;
      place-items: center;
      color: rgba(20, 38, 63, .022);
      font: 850 clamp(48px, 8vw, 104px)/1.2 'Pretendard Variable', sans-serif;
      letter-spacing: .1em;
      transform: rotate(-24deg);
      text-align: center;
      white-space: nowrap;
    }
    @media print {
      body::after { color: rgba(20, 38, 63, .035); }
    }
  `;
  document.head.appendChild(style);
})();