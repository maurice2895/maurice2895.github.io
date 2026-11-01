/* 덴탈솔브 홈페이지 동작 스크립트
   - 인라인 스크립트를 이 파일로 옮겨 Content-Security-Policy(script-src 'self')를 적용할 수 있게 했습니다.
   - 'js' 클래스가 붙은 경우에만 등장 애니메이션용으로 문장을 숨기므로,
     스크립트가 실행되지 않는 환경(일부 검색 수집기 등)에서도 문장이 그대로 보입니다. */
(() => {
  "use strict";
  const root = document.documentElement;
  root.classList.add("js");

  const init = () => {
    /* 1) 브랜드 문장(#brand-statement) 등장 효과 */
    const statement = document.querySelector("#brand-statement");
    if (statement) {
      if (!("IntersectionObserver" in window)) {
        statement.classList.add("is-visible");
      } else {
        const io = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              statement.classList.add("is-visible");
              io.unobserve(statement);
            }
          });
        }, { threshold: 0.28 });
        io.observe(statement);
      }
    }

    /* 2) 상단 메뉴: 현재 보고 있는 섹션 표시 (같은 페이지 안의 #링크만) */
    const links = [...document.querySelectorAll(".header .nav-item")];
    const targets = links
      .map((link) => {
        const href = link.getAttribute("href") || "";
        if (!href.startsWith("#")) return null;
        const section = document.querySelector(href);
        return section ? { link, section } : null;
      })
      .filter(Boolean);
    if (targets.length && "IntersectionObserver" in window) {
      const navIo = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          targets.forEach(({ link, section }) => {
            if (section === entry.target) link.setAttribute("aria-current", "location");
            else link.removeAttribute("aria-current");
          });
        });
      }, { rootMargin: "-24% 0px -62% 0px", threshold: 0 });
      targets.forEach(({ section }) => navIo.observe(section));
    }
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
