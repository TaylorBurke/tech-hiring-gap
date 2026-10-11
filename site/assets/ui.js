/* Page chrome: hero sparkline, scroll progress, theme toggle, section reveal. No data logic here. */
(function () {
  const root = document.documentElement;
  const KEY = "thg-theme";
  const css = (n) => getComputedStyle(root).getPropertyValue(n).trim();

  /* theme toggle: remembered per viewer; falls back to the system setting */
  try { const t = localStorage.getItem(KEY); if (t) root.dataset.theme = t; } catch (e) {}
  const btn = document.getElementById("theme");
  if (btn) btn.addEventListener("click", () => {
    const dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem(KEY, root.dataset.theme); } catch (e) {}
    if (window.__rerender) window.__rerender();
    spark();
  });

  /* hero sparkline of software postings, peak and latest marked */
  function spark() {
    const host = document.getElementById("hero-spark");
    if (!host || !window.STORY) return;
    const data = window.STORY.series.indeed_software.monthly.filter((p) => p[0] >= "2020-01");
    const W = 900, H = 150, pad = 8, ymax = 240;
    const x = (i) => pad + (i / (data.length - 1)) * (W - 2 * pad - 70);
    const y = (v) => H - pad - (v / ymax) * (H - 2 * pad);
    const pts = data.map((p, i) => [x(i), y(p[1])]);
    const line = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join("");
    const pk = data.reduce((a, p, i) => (p[1] > data[a][1] ? i : a), 0);
    const last = data.length - 1, base = y(100);
    const dot = (i) => `<circle cx="${pts[i][0]}" cy="${pts[i][1]}" r="5" fill="${css("--s1")}" stroke="${css("--page")}" stroke-width="2"/>`;
    host.innerHTML = `<svg viewBox="0 0 ${W} ${H}" aria-hidden="true">
      <defs><linearGradient id="sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${css("--s1")}" stop-opacity=".28"/><stop offset="1" stop-color="${css("--s1")}" stop-opacity="0"/></linearGradient></defs>
      <line x1="${pad}" x2="${W - 62}" y1="${base}" y2="${base}" stroke="${css("--axis")}" stroke-dasharray="3 4"/>
      <text x="${pad}" y="${base - 6}" fill="${css("--muted")}" font-size="11">Feb 2020 level</text>
      <path d="${line}L${pts[last][0]} ${H - pad}L${pts[0][0]} ${H - pad}Z" fill="url(#sg)"/>
      <path d="${line}" fill="none" stroke="${css("--s1")}" stroke-width="2.5" stroke-linejoin="round"/>
      ${dot(pk)}${dot(last)}
      <text x="${pts[pk][0]}" y="${pts[pk][1] - 12}" text-anchor="middle" fill="${css("--ink")}" font-size="12.5" font-weight="600">${Math.round(data[pk][1])}</text>
      <text x="${pts[last][0] + 12}" y="${pts[last][1] + 4}" fill="${css("--ink")}" font-size="12.5" font-weight="600">${Math.round(data[last][1])}</text>
    </svg>`;
  }
  spark();
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", spark);

  /* reading progress on the nav, and the current chapter */
  const bar = document.getElementById("nav-bar");
  const links = [...document.querySelectorAll(".nav-links a[href^='#']")];
  const secs = links.map((a) => document.querySelector(a.getAttribute("href")));
  function onScroll() {
    const h = document.documentElement;
    if (bar) bar.style.transform = `scaleX(${Math.min(1, h.scrollTop / Math.max(1, h.scrollHeight - innerHeight))})`;
    let cur = -1;
    secs.forEach((s, i) => { if (s && s.getBoundingClientRect().top < innerHeight * 0.35) cur = i; });
    links.forEach((a, i) => a.classList.toggle("on", i === cur));
  }
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* gentle fade-up as sections enter; content stays visible without JS or with reduced motion */
  if (!matchMedia("(prefers-reduced-motion: reduce)").matches && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll("figure, .kpis, .prose > p, .table-wrap, .loops, .chapter > h2").forEach((el) => { el.classList.add("rv"); io.observe(el); });
  }
})();
