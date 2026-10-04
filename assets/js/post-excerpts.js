/* Keep article description visible on home banner + JS-rendered archives. */
(() => {
  const syncHomeCenterDesc = () => {
    const container = document.getElementById("home_center");
    if (!container) return;
    const descEl = container.querySelector(".home-center-title-desc");
    if (!descEl) return;
    const active = container.querySelector(".home-center-banner-item.active");
    const text = active?.dataset?.desc?.trim() || "";
    descEl.textContent = text;
    descEl.hidden = !text;
  };

  let homeObserver;

  const bind = () => {
    syncHomeCenterDesc();

    const home = document.getElementById("home_center");
    if (home) {
      homeObserver?.disconnect();
      homeObserver = new MutationObserver(syncHomeCenterDesc);
      home
        .querySelectorAll(".home-center-banner-item")
        .forEach((node) =>
          homeObserver.observe(node, {
            attributes: true,
            attributeFilter: ["class"],
          })
        );
    }
  };

  bind();
  document.addEventListener("pjax:complete", bind);
})();
