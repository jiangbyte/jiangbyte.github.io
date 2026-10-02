(() => {
  const KEY = "solitude-toc-collapsed";
  const FLOATING_MQ = "(max-width: 1200px)";

  const isFloating = () => window.matchMedia(FLOATING_MQ).matches;

  const sync = (card, btn, collapsed) => {
    card.classList.toggle("is-collapsed", collapsed);
    if (btn) btn.setAttribute("aria-expanded", collapsed ? "false" : "true");
  };

  const sizeToc = () => {
    const card = document.getElementById("card-toc");
    const content = document.getElementById("toc-content");
    const btn = document.getElementById("toc-toggle");
    if (!card || !content) return;

    // Mobile floating overlay: always keep list visible while open
    if (isFloating()) {
      if (card.classList.contains("is-collapsed")) {
        sync(card, btn, false);
      }
      if (!card.classList.contains("open")) {
        content.style.maxHeight = "";
        return;
      }
      const headerH = btn ? btn.getBoundingClientRect().height : 48;
      const available = Math.floor(window.innerHeight - 60 - headerH - 24);
      content.style.maxHeight = `${Math.max(160, available)}px`;
      return;
    }

    if (card.classList.contains("is-collapsed")) {
      content.style.maxHeight = "0px";
      return;
    }

    const top = card.getBoundingClientRect().top;
    const headerH = btn ? btn.getBoundingClientRect().height : 48;
    const available = Math.floor(window.innerHeight - top - headerH - 12);
    content.style.maxHeight = `${Math.max(120, available)}px`;
  };

  const bind = () => {
    const card = document.getElementById("card-toc");
    const btn = document.getElementById("toc-toggle");
    if (!card || !btn) return;

    if (btn.dataset.tocBound !== "1") {
      btn.dataset.tocBound = "1";

      // Desktop restores collapse preference; mobile overlay starts expanded
      const collapsed = !isFloating() && localStorage.getItem(KEY) === "1";
      sync(card, btn, collapsed);

      btn.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        // Floating TOC is a temporary overlay — don't collapse the list
        if (isFloating()) {
          if (!card.classList.contains("open")) {
            card.classList.add("open");
          }
          sync(card, btn, false);
          sizeToc();
          return;
        }
        const next = !card.classList.contains("is-collapsed");
        sync(card, btn, next);
        localStorage.setItem(KEY, next ? "1" : "0");
        sizeToc();
      });

      // Recalculate when rightside toggles #card-toc.open
      const mo = new MutationObserver(() => sizeToc());
      mo.observe(card, { attributes: true, attributeFilter: ["class"] });
    }

    sizeToc();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
  document.addEventListener("pjax:complete", bind);
  window.addEventListener("resize", sizeToc, { passive: true });
  window.addEventListener("scroll", sizeToc, { passive: true });
})();
