/* Keep body[data-project] in sync after PJAX (#body-wrap is replaced; body attrs are not). */
(() => {
  const sync = () => {
    const wrap = document.getElementById("body-wrap");
    if (!wrap) return;
    if (wrap.hasAttribute("data-project")) {
      document.body.setAttribute("data-project", "true");
    } else {
      document.body.removeAttribute("data-project");
    }
  };
  sync();
  document.addEventListener("pjax:complete", sync);
})();
