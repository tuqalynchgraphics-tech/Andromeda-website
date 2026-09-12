/* Andromeda (Sui-styled) — progressive enhancement only.
   The page is fully readable and navigable with JS disabled. */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- preloader: drop it once the intro animation has played ---- */
  var preloader = $("[data-preloader]");
  if (preloader) {
    var dropPreloader = function () {
      if (preloader && preloader.parentNode) preloader.parentNode.removeChild(preloader);
      preloader = null;
    };
    preloader.addEventListener("animationend", function (e) {
      if (e.animationName === "pre-out") dropPreloader();
    });
    setTimeout(dropPreloader, reduce ? 900 : 2200);   /* safety net */
  }

  /* ---- promo bar ---------------------------------------------------- */
  var promo = $("[data-promo]");
  var promoClose = $("[data-promo-close]");
  if (promo && promoClose) {
    try { if (sessionStorage.getItem("andromeda:promo") === "closed") promo.hidden = true; } catch (e) {}
    promoClose.addEventListener("click", function () {
      promo.hidden = true;
      try { sessionStorage.setItem("andromeda:promo", "closed"); } catch (e) {}
    });
  }

  /* ---- header scroll state --------------------------------------- */
  var header = $("[data-header]");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 24); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- overlay nav --------------------------------------------------- */
  var overlay = $("[data-overlay]");
  var openBtn = $("[data-menu-open]");
  var closeBtn = $("[data-menu-close]");
  if (overlay && openBtn) {
    overlay.hidden = false;
    var setInert = function (on) {
      if (on) { overlay.setAttribute("inert", ""); overlay.setAttribute("aria-hidden", "true"); }
      else { overlay.removeAttribute("inert"); overlay.removeAttribute("aria-hidden"); }
    };
    setInert(true);

    var open = function () {
      setInert(false);
      overlay.classList.add("is-open");
      document.body.classList.add("nav-open");
      openBtn.setAttribute("aria-expanded", "true");
      var first = $("a", overlay);
      if (first) first.focus();
    };
    var close = function () {
      overlay.classList.remove("is-open");
      document.body.classList.remove("nav-open");
      openBtn.setAttribute("aria-expanded", "false");
      setInert(true);
      openBtn.focus();
    };
    openBtn.addEventListener("click", open);
    if (closeBtn) closeBtn.addEventListener("click", close);
    $$("[data-menu-link]", overlay).forEach(function (a) {
      a.addEventListener("click", close);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && overlay.classList.contains("is-open")) close();
    });
    // rudimentary focus containment
    overlay.addEventListener("keydown", function (e) {
      if (e.key !== "Tab") return;
      var f = $$("a, button", overlay).filter(function (el) { return !el.disabled; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ---- header CTA: split label into per-char roll cells -------- */
  var ctaLabel = $("[data-stagger] .btn-cta__label");
  if (ctaLabel) {
    var chars = ctaLabel.textContent.split("");
    ctaLabel.textContent = "";
    chars.forEach(function (chr, i) {
      var isSpace = chr === " " || chr === " ";
      var cell = document.createElement("span");
      cell.className = "btn-cta__ch" + (isSpace ? " btn-cta__ch--space" : "");
      cell.style.setProperty("--i", i);
      var mover = document.createElement("span");
      var glyph = isSpace ? " " : chr;
      mover.textContent = glyph;
      mover.setAttribute("data-ch", glyph);
      cell.appendChild(mover);
      ctaLabel.appendChild(cell);
    });
  }

  /* ---- hero mark: turn with scroll position -------------------- */
  var heroMark = $(".hero__spin");
  if (heroMark && !reduce) {
    var spinQueued = false;
    var applySpin = function () {
      spinQueued = false;
      heroMark.style.rotate = ((window.scrollY || 0) * 0.1).toFixed(2) + "deg";
    };
    applySpin();
    window.addEventListener("scroll", function () {
      if (!spinQueued) { spinQueued = true; requestAnimationFrame(applySpin); }
    }, { passive: true });
  }

  /* ---- pixel dissolve between the hero and section 01 ----------
     A canvas grid of chunky squares covers the top of #difference in
     the hero's purple. Each cell has its own random scroll threshold,
     so as you scroll past the seam the curtain shatters away in a
     staggered, pixelated pattern and the section shows through. */
  var pxCanvas = $("[data-pixel-transition]");
  if (pxCanvas && !reduce && pxCanvas.getContext) {
    var PX = { size: 34, color: "#5d22d6", randomness: 0.4, start: 0.04, end: 0.42 };
    var pxCtx = pxCanvas.getContext("2d");
    var pxGrid = { cols: 0, rows: 0, w: 0, h: 0, dpr: 1 };
    var pxThresh = null;
    var pxLocal = 0, pxRaf = 0;

    var pxDraw = function () {
      if (!pxThresh) return;
      var g = pxGrid;
      var cw = (g.w / g.cols) * g.dpr;
      var ch = (g.h / g.rows) * g.dpr;
      pxCtx.clearRect(0, 0, pxCanvas.width, pxCanvas.height);
      pxCtx.fillStyle = PX.color;
      var span = Math.max(0.0001, PX.end - PX.start);
      var local = (pxLocal - PX.start) / span;
      local = local < 0 ? 0 : local > 1 ? 1 : local;
      for (var r = 0; r < g.rows; r++) {
        for (var c = 0; c < g.cols; c++) {
          if (local < pxThresh[r * g.cols + c]) {
            pxCtx.fillRect(c * cw, r * ch, Math.ceil(cw) + 1, Math.ceil(ch) + 1);
          }
        }
      }
    };

    var pxBuild = function () {
      var w = pxCanvas.clientWidth, h = pxCanvas.clientHeight;
      if (!w || !h) return;
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      pxCanvas.width = Math.max(1, Math.floor(w * dpr));
      pxCanvas.height = Math.max(1, Math.floor(h * dpr));
      var cols = Math.max(1, Math.ceil(w / PX.size));
      var rows = Math.max(1, Math.ceil(h / PX.size));
      var t = new Float32Array(cols * rows);
      for (var i = 0; i < t.length; i++) {
        // top rows dissolve first (base), plus jitter for an organic edge;
        // floor at 0.03 so the curtain starts fully opaque
        var v = i / t.length + (Math.random() - 0.5) * PX.randomness;
        t[i] = v < 0.03 ? 0.03 : v > 1 ? 1 : v;
      }
      pxThresh = t;
      pxGrid = { cols: cols, rows: rows, w: w, h: h, dpr: dpr };
      pxDraw();
    };

    var pxMeasure = function () {
      pxRaf = 0;
      var rect = pxCanvas.getBoundingClientRect();
      var vh = window.innerHeight || 1;
      // 0 as the seam enters at the viewport bottom, 1 as it leaves the top
      var raw = (vh - rect.top) / (vh + rect.height);
      pxLocal = raw < 0 ? 0 : raw > 1 ? 1 : raw;
      pxDraw();
    };
    var pxQueue = function () { if (!pxRaf) pxRaf = requestAnimationFrame(pxMeasure); };

    pxBuild();
    pxMeasure();
    window.addEventListener("scroll", pxQueue, { passive: true });
    window.addEventListener("resize", function () { pxBuild(); pxMeasure(); }, { passive: true });
    if (typeof ResizeObserver !== "undefined") {
      new ResizeObserver(function () { pxBuild(); }).observe(pxCanvas);
    }
  }

  /* ---- click effect: 4-way pixel burst -----------------------
     Each click sprays little pixels out of the point in four
     directions — fast, then fading as they travel. */
  (function () {
    if (reduce) return;

    var cv = document.createElement("canvas");
    cv.className = "click-fx";
    cv.setAttribute("aria-hidden", "true");
    cv.style.position = "fixed";
    cv.style.zIndex = "2000";
    document.body.appendChild(cv);
    var ctx = cv.getContext("2d");
    var dpr = Math.min(window.devicePixelRatio || 1, 2);

    function size() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = Math.max(window.innerWidth || 0, document.documentElement.clientWidth || 0) || 1;
      var h = Math.max(window.innerHeight || 0, document.documentElement.clientHeight || 0) || 1;
      cv.width = Math.round(w * dpr);
      cv.height = Math.round(h * dpr);
      cv.style.width = w + "px";
      cv.style.height = h + "px";
    }
    // allocate the full-viewport backing store lazily, on the first click
    addEventListener("resize", function () { if (cv.width > 2) size(); }, { passive: true });

    var REACH = 80;    // how far a pixel travels, CSS px
    var DUR = 480;     // lifetime, ms
    var PXS = 4;       // pixel square, CSS px

    function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

    // 8 pixels: a straddling pair travelling out along each of the 4 axes
    function burst(x, y) {
      var parts = [];
      for (var arm = 0; arm < 4; arm++) {
        var ang = arm * Math.PI / 2;   // E / S / W / N
        parts.push({ ang: ang, off: -1 });
        parts.push({ ang: ang, off: 1 });
      }
      return { x: x, y: y, t: performance.now(), parts: parts };
    }

    var hits = [], raf = 0;

    // black pixels on a light background, white on a dark one
    function inkAt(x, y) {
      var els = document.elementsFromPoint(x, y);
      for (var i = 0; i < els.length; i++) {
        if (els[i] === cv) continue;
        var m = getComputedStyle(els[i]).backgroundColor.match(/rgba?\(([^)]+)\)/);
        if (!m) continue;
        var c = m[1].split(",").map(parseFloat);
        if ((c[3] === undefined ? 1 : c[3]) < 0.5) continue;   // see-through, keep looking
        var lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
        return lum > 150 ? "#111111" : "#ffffff";
      }
      return "#ffffff";
    }

    function frame() {
      raf = 0;
      var now = performance.now();
      ctx.clearRect(0, 0, cv.width, cv.height);
      var s = PXS * dpr;
      hits = hits.filter(function (h) {
        var p = (now - h.t) / DUR;
        if (p >= 1) return false;
        // one opacity, shared by all 8 pixels
        ctx.globalAlpha = p < 0.62 ? 1 : Math.max(0, 1 - (p - 0.62) / 0.38);
        ctx.fillStyle = h.col;
        var cx = h.x * dpr, cy = h.y * dpr;
        var d = easeOutCubic(p) * REACH * dpr;
        for (var k = 0; k < h.parts.length; k++) {
          var pt = h.parts[k];
          var ox = Math.cos(pt.ang), oy = Math.sin(pt.ang);
          var bx = Math.round((cx + ox * d - oy * pt.off * s) / s) * s;
          var by = Math.round((cy + oy * d + ox * pt.off * s) / s) * s;
          ctx.fillRect(bx, by, s, s);
        }
        return true;
      });
      ctx.globalAlpha = 1;
      if (hits.length) raf = requestAnimationFrame(frame);
    }

    addEventListener("pointerdown", function (e) {
      if (e.pointerType === "touch" && e.isPrimary === false) return;
      if (cv.width < 2) size();
      var b = burst(e.clientX, e.clientY);
      b.col = inkAt(e.clientX, e.clientY);
      hits.push(b);
      if (hits.length > 6) hits.shift();
      if (!raf) raf = requestAnimationFrame(frame);
    }, { passive: true });
  })();

  /* ---- expertise accordion (#difference) ------------------------ */
  var accBtns = $$("[data-accordion] .acc-head button");
  accBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".acc-item");
      var willOpen = !item.classList.contains("is-open");
      $$("[data-accordion] .acc-item").forEach(function (it) {
        it.classList.remove("is-open");
        var b = $(".acc-head button", it);
        if (b) b.setAttribute("aria-expanded", "false");
      });
      if (willOpen) {
        item.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
      }
    });
  });

  /* ---- scroll reveal --------------------------------------------- */
  // self-contained mechanisms (own CSS keyed off .is-in) — just observe
  var special = $$(".display--reveal, .rule-lead");
  // generic fade-rise
  var generic = $$(".statement, .prose, .get-card, .acc-item, .carousel, .expect-row, .pull, .col, .about-visual, .form, .btn-sq--ghost, .display:not(.display--reveal)");

  if (reduce || !("IntersectionObserver" in window)) {
    special.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    generic.forEach(function (el, i) {
      el.classList.add("reveal");
      el.style.transitionDelay = (i % 3) * 55 + "ms";
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    generic.concat(special).forEach(function (el) { io.observe(el); });
  }

  /* ---- contact form (not wired to a backend) -------------------- */
  var form = $(".form");
  if (form) {
    var note = $("[data-form-status]", form);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = $("#cf-name", form), email = $("#cf-email", form);
      if (!name.value.trim() || !email.checkValidity()) {
        note.textContent = "Please add your name and a valid email address.";
        note.removeAttribute("data-ok");
        (name.value.trim() ? email : name).focus();
        return;
      }
      note.textContent = "Thanks, " + name.value.trim().split(" ")[0] +
        " — this is a design concept, so nothing was sent. Wire it to your CRM or an email endpoint to go live.";
      note.setAttribute("data-ok", "");
      form.reset();
    });
  }

  /* ---- "what we build" carousel -------------------------------- */
  $$("[data-carousel]").forEach(function (root) {
    var track = $("[data-carousel-track]", root);
    var cards = $$(".carousel__card", track);
    var dotsWrap = $("[data-carousel-dots]", root);
    var n = cards.length;
    if (!n) return;
    var i = 0, timer = null;

    cards.forEach(function (c, idx) {
      var d = document.createElement("button");
      d.type = "button";
      d.setAttribute("aria-label", "Show solution " + (idx + 1) + " of " + n);
      d.addEventListener("click", function () { go(idx); bump(); });
      dotsWrap.appendChild(d);
    });
    var dots = $$("button", dotsWrap);

    function render() {
      var gap = parseFloat(getComputedStyle(track).columnGap || getComputedStyle(track).gap) || 0;
      var step = cards[0].getBoundingClientRect().width + gap;
      track.style.transform = "translateX(" + (-i * step) + "px)";
      cards.forEach(function (c, idx) { c.classList.toggle("is-active", idx === i); });
      dots.forEach(function (d, idx) { d.classList.toggle("is-active", idx === i); });
    }
    function go(to) { i = (to % n + n) % n; render(); }
    function bump() { if (timer) { stop(); start(); } }
    function start() { if (reduce || timer) return; timer = setInterval(function () { go(i + 1); }, 5000); }
    function stop() { clearInterval(timer); timer = null; }

    $("[data-carousel-next]", root).addEventListener("click", function () { go(i + 1); bump(); });
    $("[data-carousel-prev]", root).addEventListener("click", function () { go(i - 1); bump(); });
    root.addEventListener("mouseenter", stop);
    root.addEventListener("mouseleave", start);
    root.addEventListener("focusin", stop);
    root.addEventListener("focusout", start);
    window.addEventListener("resize", render);

    render();
    start();
  });

  /* ---- footer "in action" cycling list ----------------------- */
  var footCycle = $("[data-foot-cycle]");
  if (footCycle && !reduce) {
    var items = $$("li", footCycle);
    if (items.length) {
      var fi = items.findIndex(function (el) { return el.classList.contains("is-active"); });
      if (fi < 0) fi = 0;
      setInterval(function () {
        items[fi].classList.remove("is-active");
        fi = (fi + 1) % items.length;
        items[fi].classList.add("is-active");
      }, 2200);
    }
  }
})();
