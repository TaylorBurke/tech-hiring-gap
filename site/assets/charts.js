/* Chart kit for tech-hiring-gap. Plain SVG + d3 scales/shapes (vendored d3 v7).
   Specs follow the dataviz skill: 2px lines, >=8px end dots with a 2px surface ring,
   hairline solid grid, thin columns with 4px data-end radius, hover crosshair/tooltip,
   keyboard focus, and a table view for every chart. Text never wears the series color. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const parse = (ym) => new Date(+ym.slice(0, 4), +ym.slice(5, 7) - 1, 1);
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const fmtMonth = (ym) => `${MONTHS[+ym.slice(5, 7) - 1]} ${ym.slice(0, 4)}`;
  const fmtNum = (v, dec = 0) => d3.format(dec ? `,.${dec}f` : ",.0f")(v);

  /* ---------- shared pieces ---------- */
  function mount(host, spec) {
    host.textContent = "";
    const wrap = document.createElement("div");
    wrap.className = "chart";
    host.appendChild(wrap);
    if (spec.series && spec.series.length > 1 && !spec.noLegend) wrap.appendChild(legend(spec.series));
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", spec.label);
    svg.setAttribute("tabindex", "0");
    wrap.appendChild(svg);
    const tip = document.createElement("div");
    tip.className = "tip";
    tip.hidden = true;
    wrap.appendChild(tip);
    return { wrap, svg, tip };
  }

  function legend(series) {
    const ul = document.createElement("ul");
    ul.className = "legend";
    series.forEach((s) => {
      const li = document.createElement("li");
      const key = document.createElement("span");
      key.className = "key line";
      key.style.background = css(s.color);
      li.appendChild(key);
      li.appendChild(document.createTextNode(s.name));
      ul.appendChild(li);
    });
    return ul;
  }

  function tooltip(tip, wrap, x, y, title, rows) {
    tip.textContent = "";
    const h = document.createElement("div");
    h.className = "tip-title";
    h.textContent = title;
    tip.appendChild(h);
    rows.forEach((r) => {
      const row = document.createElement("div");
      row.className = "tip-row";
      if (r.color) {
        const k = document.createElement("span");
        k.className = "key line";
        k.style.background = css(r.color);
        row.appendChild(k);
      }
      const v = document.createElement("strong");
      v.textContent = r.value;
      row.appendChild(v);
      const n = document.createElement("span");
      n.className = "tip-name";
      n.textContent = r.name;
      row.appendChild(n);
      tip.appendChild(row);
    });
    tip.hidden = false;
    const w = wrap.clientWidth, tw = tip.offsetWidth;
    tip.style.left = Math.max(0, Math.min(w - tw, x + 14)) + "px";
    tip.style.top = Math.max(0, y - 10) + "px";
  }

  function axisX(g, x, h, w, years) {
    const per = w / Math.max(1, years[1] - years[0]);       // pixels per year
    const step = Math.max(1, Math.ceil(44 / per));          // thin the labels so they never collide
    const ticks = d3.range(years[0], years[1] + 1).filter((y) => (y - years[0]) % step === 0).map((y) => new Date(y, 0, 1));
    ticks.forEach((t) => {
      const px = x(t);
      if (px < -1 || px > w + 1) return;
      g.append("text").attr("x", px).attr("y", h + 18).attr("class", "tick").attr("text-anchor", "middle").text(t.getFullYear());
    });
  }

  function gridY(g, y, ticks, w, fmt, zeroLine) {
    ticks.forEach((t) => {
      g.append("line").attr("x1", 0).attr("x2", w).attr("y1", y(t)).attr("y2", y(t)).attr("class", t === zeroLine ? "axis-line" : "grid");
      g.append("text").attr("x", -8).attr("y", y(t) + 4).attr("class", "tick").attr("text-anchor", "end").text(fmt(t));
    });
  }

  function events(g, x, h, w, evs, narrow) {
    let k = 0;
    evs.forEach((e) => {
      const px = x(parse(e.at));
      g.append("line").attr("x1", px).attr("x2", px).attr("y1", 0).attr("y2", h).attr("class", "event");
      if (!e.text) return;
      if (narrow) {  // phones: numbered markers, text goes in a key under the legend
        g.append("text").attr("x", px).attr("y", -5 - (k % 2) * 14).attr("class", "event-label").attr("text-anchor", "middle").text(++k);
        return;
      }
      const right = e.side !== "left";
      g.append("text").attr("x", px + (right ? 6 : -6)).attr("y", -5 - (e.row || 0) * 14).attr("class", "event-label")
        .attr("text-anchor", right ? "start" : "end").text(e.text);
    });
  }

  /* ---------- line chart (one or more series on ONE axis) ---------- */
  function line(host, spec) {
    const { wrap, svg, tip } = mount(host, spec);
    const W = Math.max(320, host.clientWidth), H = spec.height || 300;
    const narrow = W < 560;
    const labelled = (spec.events || []).filter((e) => e.text);
    const evRows = narrow ? Math.min(2, labelled.length) : labelled.reduce((a, e) => Math.max(a, (e.row || 0) + 1), 0);
    const endLab = spec.endLabels && !narrow;                // narrow screens: legend + tooltip carry identity
    if (narrow && labelled.length) {
      const ol = document.createElement("ol");
      ol.className = "event-key";
      labelled.forEach((e) => { const li = document.createElement("li"); li.textContent = e.text; ol.appendChild(li); });
      wrap.insertBefore(ol, svg);
    }
    const m = { t: 10 + evRows * 14, r: endLab ? 168 : 24, b: 28, l: 52 };
    const w = W - m.l - m.r, h = H - m.t - m.b;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("width", W); svg.setAttribute("height", H);
    const g = d3.select(svg).append("g").attr("transform", `translate(${m.l},${m.t})`);
    const all = spec.series.flatMap((s) => s.data);
    const x = d3.scaleTime().domain(spec.xDomain.map(parse)).range([0, w]);
    const lo = spec.yMin !== undefined ? spec.yMin : Math.min(0, d3.min(all, (d) => d[1]));
    const hi = spec.yMax || d3.max(all, (d) => d[1]);
    const y = d3.scaleLinear().domain([lo, hi]).nice().range([h, 0]);
    gridY(g, y, y.ticks(spec.yTicks || 5), w, spec.yFormat || fmtNum, 0);
    axisX(g, x, h, w, [+spec.xDomain[0].slice(0, 4), +spec.xDomain[1].slice(0, 4)]);
    if (spec.ref) {
      g.append("line").attr("x1", 0).attr("x2", w).attr("y1", y(spec.ref.value)).attr("y2", y(spec.ref.value)).attr("class", "ref");
      g.append("text").attr("x", spec.ref.at ? x(parse(spec.ref.at)) : 4).attr("y", y(spec.ref.value) + (spec.ref.below ? 15 : -5)).attr("class", "event-label").text(spec.ref.label);
    }
    if (spec.events) events(g, x, h, w, spec.events, narrow);
    const ln = d3.line().x((d) => x(parse(d[0]))).y((d) => y(d[1])).curve(d3.curveLinear);
    spec.series.forEach((s) => {
      const solid = s.data.filter((d) => !s.prelim || d[0] < s.prelim);
      g.append("path").attr("d", ln(solid)).attr("fill", "none").attr("stroke", css(s.color)).attr("stroke-width", 2).attr("stroke-linejoin", "round").attr("stroke-linecap", "round");
      if (s.prelim && solid.length < s.data.length) {  // preliminary tail: same line, lighter + hollow end dot (no dashes: they read as projection)
        const tail = s.data.slice(solid.length - 1);
        g.append("path").attr("d", ln(tail)).attr("fill", "none").attr("stroke", css(s.color)).attr("stroke-width", 2).attr("stroke-opacity", 0.45);
      }
      const last = s.data[s.data.length - 1];
      const cx = x(parse(last[0])), cy = y(last[1]);
      g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", 6.5).attr("fill", css("--surface"));
      g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", 4.5)
        .attr("fill", s.prelim ? css("--surface") : css(s.color)).attr("stroke", css(s.color)).attr("stroke-width", s.prelim ? 2 : 0);
      if (endLab) {
        const lt = g.append("text").attr("x", cx + 12).attr("y", cy + 4 + (s.labelDy || 0)).attr("class", "end-label");
        lt.append("tspan").text(s.name);
        lt.append("tspan").attr("dx", 6).attr("class", "end-value").text((spec.valueFormat || fmtNum)(last[1]));
      }
    });
    interact(svg, g, wrap, tip, spec, x, y, m, w, h);
    table(host, spec);
  }

  function interact(svg, g, wrap, tip, spec, x, y, m, w, h) {
    const months = Array.from(new Set(spec.series.flatMap((s) => s.data.map((d) => d[0])))).sort();
    const cross = g.append("line").attr("y1", 0).attr("y2", h).attr("class", "cross").attr("opacity", 0);
    const dots = spec.series.map((s) => g.append("circle").attr("r", 4.5).attr("fill", css(s.color)).attr("stroke", css("--surface")).attr("stroke-width", 2).attr("opacity", 0));
    const show = (i, py) => {
      i = Math.max(0, Math.min(months.length - 1, i));
      const mo = months[i];
      const px = x(parse(mo));
      cross.attr("x1", px).attr("x2", px).attr("opacity", 1);
      const rows = [];
      spec.series.forEach((s, k) => {
        const d = s.data.find((q) => q[0] === mo);
        if (d) {
          dots[k].attr("cx", px).attr("cy", y(d[1])).attr("opacity", 1);
          rows.push({ color: s.color, name: s.name + (s.prelim && mo >= s.prelim ? " (preliminary)" : ""), value: (spec.valueFormat || fmtNum)(d[1]) });
        } else dots[k].attr("opacity", 0);
      });
      tooltip(tip, wrap, px + m.l, py === undefined ? m.t + 20 : py, fmtMonth(mo), rows);
      svg.__i = i;
    };
    const hide = () => { cross.attr("opacity", 0); dots.forEach((d) => d.attr("opacity", 0)); tip.hidden = true; };
    const idxAt = (clientX) => {
      const r = svg.getBoundingClientRect();
      const t = x.invert((clientX - r.left) * (svg.viewBox.baseVal.width / r.width) - m.l);
      let best = 0, bd = Infinity;
      months.forEach((mo, i) => { const dd = Math.abs(parse(mo) - t); if (dd < bd) { bd = dd; best = i; } });
      return best;
    };
    svg.addEventListener("pointermove", (e) => { const r = wrap.getBoundingClientRect(); show(idxAt(e.clientX), e.clientY - r.top); });
    svg.addEventListener("pointerleave", hide);
    svg.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault();
      show((svg.__i === undefined ? months.length - 1 : svg.__i) + (e.key === "ArrowRight" ? 1 : -1));
    });
    svg.addEventListener("focus", () => show(svg.__i === undefined ? months.length - 1 : svg.__i));
    svg.addEventListener("blur", hide);
  }

  /* ---------- column chart (single series, grows from the baseline) ---------- */
  function columns(host, spec) {
    const { wrap, svg, tip } = mount(host, spec);
    const W = Math.max(320, host.clientWidth), H = spec.height || 300;
    const m = { t: 10, r: 16, b: 28, l: 56 };
    const w = W - m.l - m.r, h = H - m.t - m.b;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.setAttribute("width", W); svg.setAttribute("height", H);
    const g = d3.select(svg).append("g").attr("transform", `translate(${m.l},${m.t})`);
    const s = spec.series[0];
    const x = d3.scaleBand().domain(s.data.map((d) => d[0])).range([0, w]).paddingInner(0).paddingOuter(0);
    const y = d3.scaleLinear().domain([0, d3.max(s.data, (d) => d[1])]).nice().range([h, 0]);
    gridY(g, y, y.ticks(spec.yTicks || 5), w, spec.yFormat || fmtNum, 0);
    const yrs = Array.from(new Set(s.data.map((d) => d[0].slice(0, 4)))).filter((yr) => s.data.some((d) => d[0] === yr + "-01"));
    if (s.data.length <= 12) {  // few bars: label every month, year on the first
      s.data.forEach((d, i) => {
        const lab = MONTHS[+d[0].slice(5, 7) - 1] + (i === 0 || d[0].slice(5, 7) === "01" ? " " + d[0].slice(0, 4) : "");
        g.append("text").attr("x", x(d[0]) + x.bandwidth() / 2).attr("y", h + 18).attr("class", "tick").attr("text-anchor", "middle").text(lab);
      });
    } else yrs.forEach((yr) => {
      g.append("text").attr("x", x(yr + "-01") + 2).attr("y", h + 18).attr("class", "tick").attr("text-anchor", "start").text(yr);
    });
    const bw = Math.min(24, Math.max(2, x.bandwidth() - 2));
    const r = Math.min(4, bw / 2);
    const bars = g.selectAll("path.bar").data(s.data).join("path").attr("class", "bar")
      .attr("d", (d) => {
        const bx = x(d[0]) + (x.bandwidth() - bw) / 2, top = y(d[1]), bh = h - top;
        const rr = Math.min(r, bh);
        return `M${bx},${h} L${bx},${top + rr} Q${bx},${top} ${bx + rr},${top} L${bx + bw - rr},${top} Q${bx + bw},${top} ${bx + bw},${top + rr} L${bx + bw},${h} Z`;
      })
      .attr("fill", css(s.color));
    // hit targets: full-height slots, bigger than the painted bar
    g.selectAll("rect.hit").data(s.data).join("rect").attr("class", "hit").attr("x", (d) => x(d[0])).attr("y", 0).attr("width", x.bandwidth()).attr("height", h).attr("fill", "transparent")
      .on("pointermove pointerenter", function (e, d) { show(d, e); })
      .on("pointerleave", hide);
    if (spec.events) {
      const xt = d3.scaleTime().domain([parse(s.data[0][0]), parse(s.data[s.data.length - 1][0])]).range([x.bandwidth() / 2, w - x.bandwidth() / 2]);
      events(g, xt, h, w, spec.events);
    }
    function show(d, e) {
      bars.attr("opacity", (q) => (q === d ? 1 : 0.55));
      const r0 = wrap.getBoundingClientRect();
      tooltip(tip, wrap, (e ? e.clientX - r0.left : x(d[0]) + m.l), (e ? e.clientY - r0.top : m.t + 20), fmtMonth(d[0]),
        [{ color: s.color, name: spec.tipName ? spec.tipName(d) : s.name, value: (spec.valueFormat || fmtNum)(d[1]) }]);
    }
    function hide() { bars.attr("opacity", 1); tip.hidden = true; }
    svg.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault();
      const i = svg.__i === undefined ? s.data.length - 1 : svg.__i;
      const j = Math.max(0, Math.min(s.data.length - 1, i + (e.key === "ArrowRight" ? 1 : -1)));
      svg.__i = j; show(s.data[j]);
    });
    svg.addEventListener("focus", () => { svg.__i = s.data.length - 1; show(s.data[s.data.length - 1]); });
    svg.addEventListener("blur", hide);
    table(host, spec);
  }

  /* ---------- small multiples: stacked panels sharing one time axis ---------- */
  function panels(host, spec) {
    host.textContent = "";
    const stack = document.createElement("div");
    stack.className = "panels";
    host.appendChild(stack);
    spec.panels.forEach((p, i) => {
      const cell = document.createElement("div");
      cell.className = "panel";
      const t = document.createElement("div");
      t.className = "panel-title";
      t.textContent = p.title;
      cell.appendChild(t);
      const inner = document.createElement("div");
      cell.appendChild(inner);
      stack.appendChild(cell);
      line(inner, Object.assign({ xDomain: spec.xDomain, endLabels: false, height: p.height || 150, label: p.title }, p,
        { noTable: true, events: i === 0 ? spec.events : spec.events.map((e) => ({ at: e.at, text: "" })) }));
    });
    table(host, { series: spec.panels.flatMap((p) => p.series), label: spec.label });
  }

  /* ---------- strip plot: every item as a dot on one axis, a few highlighted ---------- */
  function strip(host, spec) {
    const { wrap, svg, tip } = mount(host, { label: spec.label });
    svg.removeAttribute("tabindex");
    const W = Math.max(320, host.clientWidth), narrow = W < 560;
    const hl = spec.highlight;                                   // [{name, label}]
    const order = hl.map((q) => spec.items.find((i) => i.name === q.name)).sort((a, b) => b.v - a.v);
    const m = { t: 14 + order.length * 18, r: 22, b: 50, l: 22 };
    const r = narrow ? 3.6 : 5, step = 2 * r + 1, h = 8 * step + 6, H = m.t + h + m.b;
    const w = W - m.l - m.r;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("width", W); svg.setAttribute("height", H);
    const g = d3.select(svg).append("g").attr("transform", `translate(${m.l},${m.t})`);
    const x = d3.scaleLinear().domain(spec.domain).range([0, w]);
    d3.range(spec.domain[0], spec.domain[1] + 1).forEach((t) => {
      g.append("line").attr("x1", x(t)).attr("x2", x(t)).attr("y1", 0).attr("y2", h).attr("class", "grid");
      g.append("text").attr("x", x(t)).attr("y", h + 18).attr("class", "tick").attr("text-anchor", "middle").text(t + "%");
    });
    g.append("line").attr("x1", 0).attr("x2", w).attr("y1", h).attr("y2", h).attr("class", "axis-line");
    g.append("line").attr("x1", x(spec.median)).attr("x2", x(spec.median)).attr("y1", 0).attr("y2", h + 4).attr("class", "ref");
    g.append("text").attr("x", x(spec.median)).attr("y", h + 36).attr("class", "event-label").attr("text-anchor", "middle").text(`Median major ${spec.median.toFixed(1)}%`);
    const bins = {}, dots = [];
    spec.items.slice().sort((a, b) => a.v - b.v).forEach((it) => {
      const b = Math.round(it.v / 0.25), k = (bins[b] = (bins[b] || 0) + 1) - 1;
      dots.push({ it, cx: x(it.v), cy: h - r - 2 - k * step, hi: hl.some((q) => q.name === it.name) });
    });
    const hover = (e, d) => {
      const r0 = wrap.getBoundingClientRect();
      tooltip(tip, wrap, e.clientX - r0.left, e.clientY - r0.top, d.it.name,
        [{ value: d.it.v.toFixed(1) + "% unemployed", name: "", color: d.hi ? "--s1" : "--context" }, { value: d.it.u.toFixed(0) + "% underemployed", name: "" }]);
    };
    g.selectAll("circle.d").data(dots.filter((d) => !d.hi)).join("circle").attr("class", "d").attr("cx", (d) => d.cx).attr("cy", (d) => d.cy).attr("r", r)
      .attr("fill", css("--context")).attr("fill-opacity", 0.85).attr("stroke", css("--surface")).attr("stroke-width", 2);
    g.selectAll("circle.h").data(dots.filter((d) => d.hi)).join("circle").attr("class", "h").attr("cx", (d) => d.cx).attr("cy", (d) => d.cy).attr("r", r + 1.5)
      .attr("fill", css("--s1")).attr("stroke", css("--surface")).attr("stroke-width", 2);
    order.forEach((it, i) => {
      const d = dots.find((q) => q.it === it), ly = -8 - (order.length - 1 - i) * 18;
      g.append("line").attr("x1", d.cx).attr("x2", d.cx).attr("y1", ly + 3).attr("y2", d.cy - r - 3).attr("class", "event");
      const q = hl.find((z) => z.name === it.name);
      const t = g.append("text").attr("x", d.cx - 5).attr("y", ly).attr("class", "end-label").attr("text-anchor", "end");
      t.append("tspan").text(narrow ? q.short : q.label);
      t.append("tspan").attr("dx", 5).attr("class", "end-value").text(it.v.toFixed(1) + "%");
    });
    g.selectAll("circle.hit").data(dots).join("circle").attr("class", "hit").attr("cx", (d) => d.cx).attr("cy", (d) => d.cy).attr("r", 12).attr("fill", "transparent")
      .on("pointermove pointerenter", hover).on("pointerleave", () => { tip.hidden = true; });
    // table twin: all items, highest first
    const det = document.createElement("details");
    det.className = "table-view";
    det.innerHTML = "<summary>Table view</summary>";
    const sc = document.createElement("div"); sc.className = "table-scroll";
    const t = document.createElement("table");
    const hr = t.createTHead().insertRow();
    ["Major", "Unemployed (%)", "Underemployed (%)"].forEach((c) => { const th = document.createElement("th"); th.textContent = c; hr.appendChild(th); });
    const tb = t.createTBody();
    spec.items.slice().sort((a, b) => b.v - a.v).forEach((it) => {
      const tr = tb.insertRow();
      tr.insertCell().textContent = it.name;
      [it.v, it.u].forEach((v) => { const td = tr.insertCell(); td.textContent = v.toFixed(1); td.className = "num"; });
    });
    sc.appendChild(t); det.appendChild(sc); host.appendChild(det);
  }

  /* ---------- table view (the accessible twin) ---------- */
  function table(host, spec) {
    if (spec.noTable) return;
    const det = document.createElement("details");
    det.className = "table-view";
    const sum = document.createElement("summary");
    sum.textContent = "Table view";
    det.appendChild(sum);
    const months = Array.from(new Set(spec.series.flatMap((s) => s.data.map((d) => d[0])))).sort();
    const wrap = document.createElement("div");
    wrap.className = "table-scroll";
    const t = document.createElement("table");
    const head = t.createTHead().insertRow();
    ["Month"].concat(spec.series.map((s) => s.name)).forEach((c) => { const th = document.createElement("th"); th.textContent = c; head.appendChild(th); });
    const body = t.createTBody();
    months.forEach((mo) => {
      const tr = body.insertRow();
      tr.insertCell().textContent = fmtMonth(mo);
      spec.series.forEach((s) => {
        const d = s.data.find((q) => q[0] === mo);
        const td = tr.insertCell();
        td.textContent = d ? (spec.valueFormat || fmtNum)(d[1]) : "";
        td.className = "num";
      });
    });
    wrap.appendChild(t);
    det.appendChild(wrap);
    host.appendChild(det);
  }

  window.Charts = { line, columns, panels, strip, fmtNum, fmtMonth };
})();
