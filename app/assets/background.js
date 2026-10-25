/* ReviewLens animated background.
   - 3 colour orbs + grid + soft spotlight in a fixed layer behind the app
   - palette shifts as you scroll (read from Streamlit's main scroll container)
   - layers tilt and drift with the cursor like a gyroscope (device tilt on phones)
   - respects prefers-reduced-motion; idempotent across Streamlit reruns/page changes */
(function () {
  var VERSION = "__RL_VERSION__";
  var W = window, D = document;
  if (W.__rlBg && W.__rlBg.v === VERSION && D.getElementById("rl-bg")) return;
  if (W.__rlBg && W.__rlBg.stop) W.__rlBg.stop();

  var layer = D.createElement("div");
  layer.id = "rl-bg";
  layer.setAttribute("aria-hidden", "true");
  layer.innerHTML = '<div class="rl-stage"><div class="rl-orb rl-o1"></div><div class="rl-orb rl-o2"></div>' +
    '<div class="rl-orb rl-o3"></div><div class="rl-grid"></div></div><div class="rl-spot"></div>';
  D.body.insertBefore(layer, D.body.firstChild);

  var STOPS = [
    [0.00, [[37, 99, 235], [124, 58, 237], [8, 145, 178]]],
    [0.35, [[67, 56, 202], [147, 51, 234], [14, 116, 144]]],
    [0.70, [[13, 148, 136], [37, 99, 235], [109, 40, 217]]],
    [1.00, [[30, 64, 175], [8, 145, 178], [91, 33, 182]]]
  ];
  function mix(a, b, t) { return a + (b - a) * t; }
  function palette(p) {
    var i = 0;
    while (i < STOPS.length - 2 && p > STOPS[i + 1][0]) i++;
    var a = STOPS[i], b = STOPS[i + 1];
    var t = Math.max(0, Math.min(1, (p - a[0]) / (b[0] - a[0])));
    t = t * t * (3 - 2 * t);
    return [0, 1, 2].map(function (k) {
      return "rgb(" + [0, 1, 2].map(function (c) { return Math.round(mix(a[1][k][c], b[1][k][c], t)); }).join(",") + ")";
    });
  }

  var reduce = W.matchMedia && W.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var tx = 0, ty = 0, cx = 0, cy = 0, tp = 0, cp = 0, raf = 0, stopped = false, last = "";

  function clamp(v) { return Math.max(-1, Math.min(1, v)); }
  function onMove(e) { tx = (e.clientX / W.innerWidth) * 2 - 1; ty = (e.clientY / W.innerHeight) * 2 - 1; }
  function onTilt(e) { if (e.gamma == null || e.beta == null) return; tx = clamp(e.gamma / 30); ty = clamp((e.beta - 45) / 30); }
  W.addEventListener("mousemove", onMove, { passive: true });
  W.addEventListener("deviceorientation", onTilt, { passive: true });

  function scroller() { return D.querySelector('[data-testid="stMain"]') || D.scrollingElement || D.documentElement; }

  function frame() {
    if (stopped) return;
    raf = W.requestAnimationFrame(frame);
    if (D.hidden) return;
    var s = scroller(), max = s.scrollHeight - s.clientHeight;
    tp = max > 40 ? Math.max(0, Math.min(1, s.scrollTop / max)) : 0;
    cp += (tp - cp) * (reduce ? 1 : 0.08);
    if (!reduce) { cx += (tx - cx) * 0.06; cy += (ty - cy) * 0.06; }
    var sig = cp.toFixed(3) + "|" + cx.toFixed(3) + "|" + cy.toFixed(3);
    if (sig === last) return;
    last = sig;
    var c = palette(cp), st = layer.style;
    st.setProperty("--mx", cx.toFixed(4));
    st.setProperty("--my", cy.toFixed(4));
    st.setProperty("--sp", cp.toFixed(4));
    st.setProperty("--sx", (((cx + 1) / 2) * 100).toFixed(2));
    st.setProperty("--sy", (((cy + 1) / 2) * 100).toFixed(2));
    st.setProperty("--c1", c[0]); st.setProperty("--c2", c[1]); st.setProperty("--c3", c[2]);
  }
  frame();

  W.__rlBg = {
    v: VERSION,
    stop: function () {
      stopped = true; W.cancelAnimationFrame(raf);
      W.removeEventListener("mousemove", onMove); W.removeEventListener("deviceorientation", onTilt);
      if (layer.parentNode) layer.parentNode.removeChild(layer);
    }
  };
})();
