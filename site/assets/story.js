/* Per-figure chart specs for chapters 1-4. Data arrives as window.STORY (data/derived/story.json). */
(function () {
  const S = window.STORY.series;
  const d = (k) => S[k].monthly;
  const PRELIM = window.STORY.latest_info_month;  // BLS flags only the newest JOLTS month as preliminary
  const two = (v) => Charts.fmtNum(v, 2);
  const k0 = (v) => (v === 0 ? "0" : Charts.fmtNum(v) + "k");
  const pct = (v) => (v >= 0 ? "+" : "") + Charts.fmtNum(v, 1) + "%";
  const X = ["2020-01", "2026-10"];

  const figs = {
    /* Chapter 1 */
    "fig-postings": () => Charts.line(document.getElementById("fig-postings"), {
      label: "Line chart of Indeed job postings indexed to February 2020: software development versus all postings",
      series: [
        { name: "Software development", color: "--s1", data: d("indeed_software") },
        { name: "All postings", color: "--context", data: d("indeed_all") },
      ],
      xDomain: X, endLabels: true, height: 320, ref: { value: 100, label: "Feb 2020 level", at: "2024-03", below: true },
      valueFormat: (v) => Charts.fmtNum(v),
    }),

    /* Chapter 2: small multiples on one shared time axis */
    "fig-turn": () => Charts.panels(document.getElementById("fig-turn"), {
      label: "Three stacked panels: interest rates, job postings, and employment, 2019 to 2026",
      xDomain: ["2019-01", "2026-10"],
      events: [
        { at: "2022-01", text: "Jan 2022: Sec. 174 amortization starts", side: "left", row: 0 },
        { at: "2022-03", text: "Mar 2022: first Fed rate rise", side: "right", row: 1 },
        { at: "2025-07", text: "Jul 2025: expensing restored", side: "left", row: 0 },
      ],
      panels: [
        { title: "Interest rates (percent)", height: 170, valueFormat: two, yMin: 0,
          series: [{ name: "Fed funds", color: "--s2", data: d("fedfunds") }, { name: "10-yr Treasury", color: "--context", data: d("treasury10") }] },
        { title: "Job postings on Indeed (Feb 2020 = 100)", height: 150, valueFormat: (v) => Charts.fmtNum(v),
          series: [{ name: "Software dev", color: "--s1", data: d("indeed_software") }, { name: "All postings", color: "--context", data: d("indeed_all") }] },
        { title: "Employment (percent change since Jan 2020)", height: 150, valueFormat: pct,
          series: [{ name: "Computer systems design", color: "--s1", data: d("emp_csd") }, { name: "All nonfarm jobs", color: "--context", data: d("emp_all") }] },
      ],
    }),

    /* Chapter 3 */
    "fig-cuts": () => Charts.columns(document.getElementById("fig-cuts"), {
      label: "Column chart of monthly announced job cuts, all industries, 2021 to 2026",
      series: [{ name: "Announced job cuts", color: "--s1", data: S.challenger_total.monthly.filter((p) => p[0] >= "2021-01") }],
      height: 300, yFormat: (v) => (v >= 1000 ? Charts.fmtNum(v / 1000) + "k" : v),
    }),
    "fig-layoffs": () => Charts.line(document.getElementById("fig-layoffs"), {
      label: "Line chart of monthly layoffs and discharges in the information sector, 3-month average",
      series: [{ name: "Layoffs and discharges, information sector (3-month avg)", color: "--s1", data: d("info_layoffs_3m"), prelim: PRELIM }],
      xDomain: ["2019-01", "2026-10"], height: 260, yMin: 0, valueFormat: (v) => Charts.fmtNum(v) + "k",
      yFormat: k0, ref: { value: window.STORY.facts.layoffs_2019, label: "2019 average", at: "2020-08" },
      events: [{ at: "2020-04", text: "Spring 2020: pandemic", side: "right", row: 0 }],
    }),
    "fig-ai": () => {
      const tot = Object.fromEntries(S.challenger_total.monthly);
      Charts.columns(document.getElementById("fig-ai"), {
        label: "Column chart of monthly announced job cuts citing AI, January to September 2026",
        series: [{ name: "Cuts citing AI", color: "--s1", data: S.challenger_ai.monthly }],
        height: 240, tipName: (p) => `cuts citing AI, ${Math.round((p[1] / tot[p[0]]) * 100)}% of ${Charts.fmtNum(tot[p[0]])} announced that month`,
        yFormat: (v) => (v >= 1000 ? Charts.fmtNum(v / 1000) + "k" : v),
      });
    },

    /* Chapter 5 */
    "fig-grads": () => Charts.line(document.getElementById("fig-grads"), {
      label: "Line chart of unemployment rates: recent college graduates versus all workers, 2019 to 2026",
      series: [
        { name: "Recent graduates (22-27)", color: "--s1", data: d("ny_recent") },
        { name: "All workers", color: "--context", data: d("ny_all") },
      ],
      xDomain: ["2019-01", "2026-10"], endLabels: true, height: 300, yMin: 0, valueFormat: (v) => v.toFixed(1) + "%", yFormat: (v) => v + "%",
      events: [{ at: "2025-10", text: "Oct 2025 estimated", side: "left", row: 0 }],
    }),
    "fig-majors": () => Charts.strip(document.getElementById("fig-majors"), {
      label: "Strip plot of unemployment rates for recent graduates in 74 college majors, with computer majors highlighted",
      items: window.STORY.majors.list.map((m) => ({ name: m.name, v: m.unemp, u: m.under })),
      domain: [0, 9], median: window.STORY.facts.major_median,
      highlight: [
        { name: "Computer Engineering", label: "Computer engineering", short: "Comp. eng." },
        { name: "Computer Science", label: "Computer science", short: "Comp. sci." },
        { name: "Information Systems & Management", label: "Information systems", short: "Info. sys." },
      ],
    }),
    "fig-broad": () => Charts.panels(document.getElementById("fig-broad"), {
      label: "Two stacked panels: headline and broader unemployment rates, and people outside the labor force who want a job",
      xDomain: ["2019-01", "2026-10"],
      events: [],
      panels: [
        { title: "Unemployment: headline (U-3) and broader (U-6), percent", height: 170, yMin: 0, valueFormat: (v) => v.toFixed(1) + "%", yFormat: (v) => v + "%",
          series: [{ name: "U-6 (adds discouraged, marginally attached, part-time for economic reasons)", color: "--s2", data: d("u6") }, { name: "U-3 (headline)", color: "--s1", data: d("u3") }] },
        { title: "Not in the labor force but want a job now, millions (12-month average)", height: 150, yMin: 0, valueFormat: (v) => (v / 1000).toFixed(1) + " million", yFormat: (v) => (v === 0 ? "0" : v / 1000 + "M"),
          ref: { value: window.STORY.facts.want_2019, label: "2019 average: " + (window.STORY.facts.want_2019 / 1000).toFixed(1) + " million", at: "2023-03", below: true },
          series: [{ name: "Want a job, not in labor force", color: "--s1", data: d("want_job_12m") }] },
      ],
    }),

    /* Chapter 6 */
    "fig-quits": () => Charts.line(document.getElementById("fig-quits"), {
      label: "Line chart of information-sector quits and hires, thousands per month, 3-month average",
      series: [
        { name: "Quits", color: "--s1", data: d("info_quits_3m"), prelim: PRELIM },
        { name: "Hires", color: "--s2", data: d("info_hires_3m"), prelim: PRELIM },
      ],
      xDomain: ["2019-01", "2026-10"], endLabels: true, height: 300, yMin: 0, valueFormat: (v) => Charts.fmtNum(v) + "k", yFormat: k0,
    }),

    /* Chapter 4 */
    "fig-gap-levels": () => Charts.line(document.getElementById("fig-gap-levels"), {
      label: "Line chart of information-sector job openings and hires, thousands per month, 3-month average",
      series: [
        { name: "Openings", color: "--s1", data: d("info_openings_3m"), prelim: PRELIM },
        { name: "Hires", color: "--s2", data: d("info_hires_3m"), prelim: PRELIM },
      ],
      xDomain: ["2019-01", "2026-10"], endLabels: true, height: 300, yMin: 0, valueFormat: (v) => Charts.fmtNum(v) + "k", yFormat: k0,
    }),
    "fig-gap-ratio": () => Charts.line(document.getElementById("fig-gap-ratio"), {
      label: "Line chart of job openings per hire: information sector versus the whole economy, 3-month average",
      series: [
        { name: "Information sector", color: "--s1", data: d("ratio_info"), prelim: PRELIM },
        { name: "Whole economy", color: "--context", data: d("ratio_all") },
      ],
      xDomain: ["2019-01", "2026-10"], endLabels: true, height: 300, yMin: 0, yMax: 3, yTicks: 6, valueFormat: two, yFormat: (v) => v.toFixed(1),
      ref: { value: 1, label: "1 opening per hire", at: "2023-09", below: true },
    }),
  };

  function render() { Object.keys(figs).forEach((k) => { if (document.getElementById(k)) figs[k](); }); }
  render();
  window.__rerender = render;
  let t;
  let lastW = innerWidth;
  addEventListener("resize", () => { if (innerWidth === lastW) return; lastW = innerWidth; clearTimeout(t); t = setTimeout(render, 150); });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
})();
