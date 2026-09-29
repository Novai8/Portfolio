/* ==========================================================================
   5Star Auto — cinematic hero runtime
   Progressive enhancement only: every feature below is optional. If this file
   never runs, the hero is still a static, readable, fully navigable section.
   ========================================================================== */
(function () {
  "use strict";

  var docEl = document.documentElement;
  docEl.classList.remove("no-js");

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)");
  var desktop = window.matchMedia("(min-width: 861px)");
  var lowPower = (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2) ||
                 (navigator.deviceMemory && navigator.deviceMemory <= 2);

  function motionOK() { return !reduced.matches && !lowPower; }
  function pointerFX() { return motionOK() && fine.matches && desktop.matches; }

  /* ---------------------------------------------------------------- theme */
  var themeBtn = document.querySelector("[data-theme-toggle]");
  function applyTheme(t) {
    docEl.setAttribute("data-theme", t);
    try { localStorage.setItem("fsa-theme", t); } catch (e) {}
    if (themeBtn) themeBtn.setAttribute("aria-label", t === "dark" ? "Switch to light mode" : "Switch to dark mode");
  }
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      applyTheme(docEl.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  }

  /* ------------------------------------------------------------ film grain */
  // generated once, inlined as a data URI so there is no extra request
  (function grain() {
    try {
      var c = document.createElement("canvas");
      c.width = c.height = 120;
      var ctx = c.getContext("2d");
      var img = ctx.createImageData(120, 120);
      for (var i = 0; i < img.data.length; i += 4) {
        var v = 120 + Math.random() * 135;
        img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
        img.data[i + 3] = 18;
      }
      ctx.putImageData(img, 0, 0);
      docEl.style.setProperty("--grain", 'url("' + c.toDataURL("image/png") + '")');
    } catch (e) {}
  })();

  var hero = document.querySelector("[data-hero]");
  if (!hero) return;

  /* -------------------------------------------------- vehicle asset guard */
  var vehicleImgs = hero.querySelectorAll("[data-vehicle-img]");
  var failures = 0;
  Array.prototype.forEach.call(vehicleImgs, function (img) {
    img.addEventListener("error", function () {
      failures++;
      if (failures >= vehicleImgs.length) hero.classList.add("no-vehicle");
    });
  });

  /* ----------------------------------------------------- staged entrance */
  function reveal() { hero.classList.add("is-ready"); }
  if (document.readyState === "complete") { requestAnimationFrame(reveal); }
  else { window.addEventListener("load", function () { requestAnimationFrame(reveal); }); }
  // never let a slow image block the reveal
  setTimeout(reveal, 900);

  /* --------------------------------------------------- pointer + spotlight */
  var target = { x: 0, y: 0, mx: 0.5, my: 0.45 };
  var current = { x: 0, y: 0, mx: 0.5, my: 0.45 };
  var cur = { x: -100, y: -100 };
  var ring = { x: -100, y: -100 };
  var pointerRaw = { x: -100, y: -100 };
  var running = false;
  var cursorEls = null;

  function ensureCursor() {
    if (cursorEls || !pointerFX()) return;
    var dot = document.createElement("div");
    dot.className = "cursor";
    var r = document.createElement("div");
    r.className = "cursor-ring";
    document.body.appendChild(dot);
    document.body.appendChild(r);
    cursorEls = { dot: dot, ring: r };
    docEl.classList.add("cursor-active");
  }

  function lerp(a, b, t) { return a + (b - a) * t; }

  function frame() {
    current.x = lerp(current.x, target.x, 0.075);
    current.y = lerp(current.y, target.y, 0.075);
    current.mx = lerp(current.mx, target.mx, 0.11);
    current.my = lerp(current.my, target.my, 0.11);

    hero.style.setProperty("--px", current.x.toFixed(4));
    hero.style.setProperty("--py", current.y.toFixed(4));
    hero.style.setProperty("--mx", (current.mx * 100).toFixed(2) + "%");
    hero.style.setProperty("--my", (current.my * 100).toFixed(2) + "%");

    if (cursorEls) {
      cur.x = lerp(cur.x, pointerRaw.x, 0.32);
      cur.y = lerp(cur.y, pointerRaw.y, 0.32);
      ring.x = lerp(ring.x, pointerRaw.x, 0.15);
      ring.y = lerp(ring.y, pointerRaw.y, 0.15);
      cursorEls.dot.style.transform = "translate3d(" + cur.x + "px," + cur.y + "px,0)";
      cursorEls.ring.style.transform = "translate3d(" + ring.x + "px," + ring.y + "px,0)";
    }

    // magnetic primary CTA
    if (magnet.el) {
      magnet.cx = lerp(magnet.cx, magnet.tx, 0.14);
      magnet.cy = lerp(magnet.cy, magnet.ty, 0.14);
      magnet.el.style.transform = "translate3d(" + magnet.cx.toFixed(2) + "px," + magnet.cy.toFixed(2) + "px,0)";
      if (!magnet.active && Math.abs(magnet.cx) < 0.05 && Math.abs(magnet.cy) < 0.05) {
        magnet.el.style.transform = "";
        magnet.el = null;
      }
    }

    var settled = Math.abs(current.x - target.x) < 0.001 &&
                  Math.abs(current.y - target.y) < 0.001 &&
                  Math.abs(current.mx - target.mx) < 0.001 &&
                  Math.abs(current.my - target.my) < 0.001;

    var cursorSettled = !cursorEls ||
      (Math.abs(cur.x - pointerRaw.x) < 0.1 && Math.abs(cur.y - pointerRaw.y) < 0.1 &&
       Math.abs(ring.x - pointerRaw.x) < 0.1 && Math.abs(ring.y - pointerRaw.y) < 0.1);

    if (settled && cursorSettled && !magnet.el) { running = false; return; }
    requestAnimationFrame(frame);
  }
  function kick() { if (!running) { running = true; requestAnimationFrame(frame); } }

  var magnet = { el: null, tx: 0, ty: 0, cx: 0, cy: 0, active: false };

  if (pointerFX()) {
    ensureCursor();
    window.addEventListener("pointermove", function (e) {
      if (e.pointerType !== "mouse") return;
      pointerRaw.x = e.clientX;
      pointerRaw.y = e.clientY;

      var r = hero.getBoundingClientRect();
      var inside = e.clientY >= r.top && e.clientY <= r.bottom;
      if (inside) {
        target.x = ((e.clientX - r.left) / r.width) * 2 - 1;
        target.y = ((e.clientY - r.top) / r.height) * 2 - 1;
        target.mx = (e.clientX - r.left) / r.width;
        target.my = (e.clientY - r.top) / r.height;
        hero.classList.add("has-cursor");
      } else {
        hero.classList.remove("has-cursor");
        target.x = 0; target.y = 0;
      }
      kick();
    }, { passive: true });

    document.addEventListener("pointerleave", function () {
      hero.classList.remove("has-cursor");
      target.x = 0; target.y = 0; kick();
    });

    // cursor grows over interactive elements
    document.addEventListener("pointerover", function (e) {
      var t = e.target.closest ? e.target.closest("a,button,[data-hot]") : null;
      docEl.classList.toggle("cursor-hot", !!t);
    }, { passive: true });

    // magnetic pull on the primary CTA (3–5px, never chasing)
    var primary = hero.querySelector("[data-magnetic]");
    if (primary) {
      primary.addEventListener("pointermove", function (e) {
        var b = primary.getBoundingClientRect();
        var dx = (e.clientX - (b.left + b.width / 2)) / (b.width / 2);
        var dy = (e.clientY - (b.top + b.height / 2)) / (b.height / 2);
        magnet.el = primary;
        magnet.active = true;
        magnet.tx = Math.max(-1, Math.min(1, dx)) * 5;
        magnet.ty = Math.max(-1, Math.min(1, dy)) * 4;
        kick();
      }, { passive: true });
      primary.addEventListener("pointerleave", function () {
        magnet.active = false;
        magnet.tx = 0; magnet.ty = 0;
        kick();
      });
    }
  }

  /* ------------------------------------------------------ hotspots (touch) */
  var hotspots = hero.querySelectorAll("[data-hot]");
  Array.prototype.forEach.call(hotspots, function (h) {
    h.addEventListener("click", function (e) {
      e.preventDefault();
      var open = h.classList.contains("is-open");
      Array.prototype.forEach.call(hotspots, function (o) {
        o.classList.remove("is-open");
        o.setAttribute("aria-expanded", "false");
      });
      if (!open) { h.classList.add("is-open"); h.setAttribute("aria-expanded", "true"); }
    });
    h.addEventListener("blur", function () {
      h.classList.remove("is-open");
      h.setAttribute("aria-expanded", "false");
    });
  });

  /* --------------------------------------------------- scroll choreography */
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var h = hero.offsetHeight || 1;
      var p = Math.min(1, Math.max(0, window.pageYOffset / h));
      hero.style.setProperty("--sp", p.toFixed(4));
      var header = document.querySelector(".site-header");
      if (header) header.classList.toggle("is-stuck", window.pageYOffset > 40);
    });
  }
  if (motionOK() && desktop.matches) {
    window.addEventListener("scroll", onScroll, { passive: true });
  } else {
    window.addEventListener("scroll", function () {
      var header = document.querySelector(".site-header");
      if (header) header.classList.toggle("is-stuck", window.pageYOffset > 40);
    }, { passive: true });
  }
  onScroll();

  /* ---------------------------------------------------------- scroll cue */
  var cue = hero.querySelector("[data-scroll-cue]");
  if (cue) {
    cue.addEventListener("click", function () {
      var next = document.querySelector(cue.getAttribute("data-target") || "#why");
      if (!next) return;
      next.scrollIntoView({ behavior: reduced.matches ? "auto" : "smooth", block: "start" });
    });
  }

  /* -------------------------------------------------- section reveals */
  if ("IntersectionObserver" in window && motionOK()) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -12% 0px" });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ------------------------------------------ react to preference changes */
  function handlePrefChange() {
    if (!pointerFX() && cursorEls) {
      cursorEls.dot.remove(); cursorEls.ring.remove();
      cursorEls = null;
      docEl.classList.remove("cursor-active", "cursor-hot");
    } else { ensureCursor(); kick(); }
    if (!motionOK()) {
      hero.style.setProperty("--px", 0);
      hero.style.setProperty("--py", 0);
      hero.style.setProperty("--sp", 0);
    }
  }
  ["change"].forEach(function (ev) {
    if (reduced.addEventListener) {
      reduced.addEventListener(ev, handlePrefChange);
      fine.addEventListener(ev, handlePrefChange);
      desktop.addEventListener(ev, handlePrefChange);
    }
  });
})();
