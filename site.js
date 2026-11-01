/* 조재연 강사 홈페이지 동작 스크립트 (모든 페이지 공용)
   1) 모바일 메뉴 열기·닫기
   2) 스크롤 등장 효과(.reveal) — 스크립트가 실행되지 않는 환경에서는 내용이 그대로 보입니다.
   3) 푸터 연도 자동 표시 */
(() => {
  "use strict";
  document.documentElement.classList.add("js");

  const init = () => {
    /* 1) 모바일 메뉴 */
    const header = document.querySelector(".header");
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.getElementById("site-nav");
    if (header && toggle && nav) {
      const setOpen = (open) => {
        header.classList.toggle("is-open", open);
        toggle.setAttribute("aria-expanded", String(open));
        toggle.setAttribute("aria-label", open ? "메뉴 닫기" : "메뉴 열기");
      };
      toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
      nav.addEventListener("click", (event) => {
        if (event.target instanceof Element && event.target.closest("a")) setOpen(false);
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && header.classList.contains("is-open")) {
          setOpen(false);
          toggle.focus();
        }
      });
      document.addEventListener("click", (event) => {
        if (header.classList.contains("is-open") && event.target instanceof Node && !header.contains(event.target)) setOpen(false);
      });
      window.matchMedia("(min-width: 1081px)").addEventListener("change", (mq) => {
        if (mq.matches) setOpen(false);
      });
    }

    /* 2) 등장 효과 */
    const items = document.querySelectorAll(".reveal");
    if (items.length) {
      if (!("IntersectionObserver" in window)) {
        items.forEach((el) => el.classList.add("is-visible"));
      } else {
        const io = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              io.unobserve(entry.target);
            }
          });
        }, { threshold: 0.2 });
        items.forEach((el) => io.observe(el));
      }
    }

    /* 3) 연도 */
    document.querySelectorAll("[data-year]").forEach((el) => {
      el.textContent = String(new Date().getFullYear());
    });
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
