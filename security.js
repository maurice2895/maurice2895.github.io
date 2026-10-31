/* Basic browser-side deterrents only; this is not access control. */
(() => {
  "use strict";

  // Discourage saving or dragging displayed images through the browser UI.
  document.addEventListener("contextmenu", (event) => {
    if (event.target instanceof Element && event.target.closest("img")) {
      event.preventDefault();
    }
  });

  document.addEventListener("dragstart", (event) => {
    if (event.target instanceof Element && event.target.closest("img")) {
      event.preventDefault();
    }
  });
})();
