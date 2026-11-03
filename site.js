/* 덴탈솔브 홈페이지 동작 스크립트 (모든 페이지 공용)
   1) 모바일 메뉴 열기·닫기
   2) 스크롤하면 머리글 테두리 표시, 휴대폰 하단 상담 버튼 표시
   3) 스크롤 등장 효과(.reveal) — 스크립트가 실행되지 않으면 내용이 그대로 보입니다.
   4) 바닥글 연도 자동 표시 */
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

    /* 2) 스크롤 상태 */
    const sticky = document.querySelector(".sticky-cta");
    const contact = document.querySelector(".contact");
    let ticking = false;
    const onScroll = () => {
      ticking = false;
      const y = window.scrollY || 0;
      if (header) header.classList.toggle("is-scrolled", y > 8);
      if (sticky) {
        let show = y > 420;
        if (show && contact) {
          const rect = contact.getBoundingClientRect();
          if (rect.top < window.innerHeight && rect.bottom > 0) show = false;
        }
        sticky.classList.toggle("is-shown", show);
      }
    };
    window.addEventListener("scroll", () => {
      if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
    }, { passive: true });
    onScroll();

    /* 3) 등장 효과 — 화면 아래에 있는 요소에만 적용해 첫 화면이 깜빡이지 않게 합니다. */
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const groups = ".bento, .criteria, .process, .lectures, .cred, .card-grid, .steps, .signal-grid, .check-list, .faq";
    const singles = ".sec-head, .page-sec h2, .page-sec .kicker, .contact-in, .cta-strip, .profile-grid > div:first-child";
    if (!reduce && "IntersectionObserver" in window) {
      const below = (el) => el.getBoundingClientRect().top > window.innerHeight * 0.92;
      const targets = [];
      document.querySelectorAll(groups).forEach((group) => {
        Array.from(group.children).forEach((child, i) => {
          if (below(child)) {
            child.classList.add("reveal");
            child.style.transitionDelay = `${Math.min(i, 4) * 90}ms`;
            targets.push(child);
          }
        });
      });
      document.querySelectorAll(singles).forEach((el) => {
        if (!el.classList.contains("reveal") && below(el)) {
          el.classList.add("reveal");
          targets.push(el);
        }
      });
      document.querySelectorAll(".reveal").forEach((el) => {
        if (!targets.includes(el)) targets.push(el);
      });
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
      targets.forEach((el) => io.observe(el));
    } else {
      document.querySelectorAll(".reveal").forEach((el) => el.classList.add("is-visible"));
    }

    /* 4) 연도 */
    document.querySelectorAll("[data-year]").forEach((el) => {
      el.textContent = String(new Date().getFullYear());
    });
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
