/* Windborne 宣传站脚本 — 零依赖 */
(function () {
  "use strict";

  var LANG_KEY = "ww-site-lang";
  var docEl = document.documentElement;

  /* ---------- language ---------- */
  function setLang(lang) {
    docEl.setAttribute("lang", lang);
    try {
      localStorage.setItem(LANG_KEY, lang);
    } catch (e) {}
    var btn = document.getElementById("langToggle");
    if (btn) btn.textContent = lang === "zh" ? "EN / 中" : "中 / EN";
  }
  (function initLang() {
    var saved = null;
    try {
      saved = localStorage.getItem(LANG_KEY);
    } catch (e) {}
    if (!saved) {
      saved = (navigator.language || "zh").toLowerCase().indexOf("zh") === 0 ? "zh" : "en";
    }
    setLang(saved);
  })();
  var langBtn = document.getElementById("langToggle");
  if (langBtn) {
    langBtn.addEventListener("click", function () {
      setLang(docEl.getAttribute("lang") === "zh" ? "en" : "zh");
    });
  }

  /* ---------- year ---------- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ---------- reveal on scroll ---------- */
  var revealEls = [].slice.call(document.querySelectorAll(".reveal"));
  if ("IntersectionObserver" in window && revealEls.length) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add("in");
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach(function (el) {
      io.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add("in");
    });
  }

  /* ---------- optional generated art injection ---------- */
  function imageExists(url, onOk) {
    var img = new Image();
    img.onload = function () {
      if (img.naturalWidth > 0) onOk(url);
    };
    img.src = url;
  }

  function injectHeroArt(url) {
    var frame = document.getElementById("heroFrame");
    if (!frame) return;
    frame.innerHTML = "";
    var img = new Image();
    img.src = url;
    img.alt = "Windborne";
    frame.appendChild(img);
  }

  function injectMedia(containerId, url, alt) {
    var el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = "";
    var img = new Image();
    img.src = url;
    img.alt = alt || "";
    img.loading = "lazy";
    el.appendChild(img);
  }

  /* ---------- visitor gallery ---------- */
  var RARITY = {
    common: { zh: "普通", en: "Common", dot: "dot-common" },
    rare: { zh: "稀有", en: "Rare", dot: "dot-rare" },
    epic: { zh: "极品", en: "Epic", dot: "dot-epic" }
  };
  var showcaseVisitors = [];
  var currentFilter = "all";

  function cardHTML(v) {
    var r = RARITY[v.rarity] || RARITY.common;
    var art = v.art
      ? '<img src="' + v.art + '" alt="" loading="lazy" />'
      : '<span style="font-size:34px">✦</span>';
    return (
      '<article class="visitor-card ' +
      v.rarity +
      '" data-rarity="' +
      v.rarity +
      '">' +
      '<div class="art">' +
      art +
      "</div>" +
      '<div class="name" title="' +
      v.label +
      " / " +
      v.labelEn +
      '">' +
      '<span data-lang-zh>' +
      v.label +
      "</span><span data-lang-en>" +
      v.labelEn +
      "</span></div>" +
      '<div class="tier"><span class="dot ' +
      r.dot +
      '"></span>' +
      '<span data-lang-zh>' +
      r.zh +
      "</span><span data-lang-en>" +
      r.en +
      "</span></div>" +
      "</article>"
    );
  }

  function renderGallery() {
    var grid = document.getElementById("visitorGrid");
    if (!grid) return;
    var list = showcaseVisitors.filter(function (v) {
      return currentFilter === "all" || v.rarity === currentFilter;
    });
    grid.innerHTML = list.map(cardHTML).join("");
  }

  function wireControls() {
    var controls = document.getElementById("galleryControls");
    if (controls) {
      controls.addEventListener("click", function (e) {
        var btn = e.target.closest ? e.target.closest(".filter-btn") : null;
        if (!btn) return;
        currentFilter = btn.getAttribute("data-filter");
        [].forEach.call(controls.querySelectorAll(".filter-btn"), function (b) {
          b.setAttribute("aria-pressed", b === btn ? "true" : "false");
        });
        renderGallery();
      });
    }
  }

  function buildHeroCollage() {
    var host = document.getElementById("heroCollage");
    if (!host || !showcaseVisitors.length) return;
    // pick a spread of visually distinct visitors that have art
    var picks = ["aurora", "doublerainbow", "cloud", "sunbeam", "thundercloud", "birds", "halo22", "cirrus"];
    var byId = {};
    showcaseVisitors.forEach(function (v) {
      byId[v.id] = v;
    });
    var positions = [
      { top: "10%", left: "12%", w: 118, delay: 0 },
      { top: "16%", left: "58%", w: 150, delay: 1.2 },
      { top: "46%", left: "30%", w: 168, delay: 0.6 },
      { top: "58%", left: "66%", w: 104, delay: 2.1 },
      { top: "62%", left: "8%", w: 96, delay: 1.6 },
      { top: "30%", left: "78%", w: 84, delay: 0.9 },
      { top: "8%", left: "38%", w: 78, delay: 2.6 },
      { top: "40%", left: "50%", w: 92, delay: 1.9 }
    ];
    var html = "";
    picks.forEach(function (id, i) {
      var v = byId[id];
      var p = positions[i];
      if (!v || !v.art || !p) return;
      html +=
        '<img class="float" src="' +
        v.art +
        '" alt="" style="top:' +
        p.top +
        ";left:" +
        p.left +
        ";width:" +
        p.w +
        "px;animation-delay:" +
        p.delay +
        's" />';
    });
    host.innerHTML = html;
  }

  function loadVisitors() {
    fetch("data/visitors.json")
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        showcaseVisitors = data.visitors || [];
        // update counts
        var setTxt = function (id, n) {
          var el = document.getElementById(id);
          if (el) el.textContent = String(n);
        };
        var showcaseTotal = data.showcaseTotal || showcaseVisitors.length;
        setTxt("cnt-all", showcaseTotal);
        setTxt("cnt-all-en", showcaseTotal);
        renderGallery();
        buildHeroCollage();
      })
      .catch(function (err) {
        var grid = document.getElementById("visitorGrid");
        if (grid)
          grid.innerHTML =
            '<p style="grid-column:1/-1;text-align:center;color:var(--ink-soft)">visitors.json 未能加载 / could not load visitors.json</p>';
      });
  }

  /* ---------- boot ---------- */
  wireControls();
  loadVisitors();

  // swap in generated art if present (produced by tools/gen_all_art.py)
  imageExists("assets/art/hero.jpg", injectHeroArt);
  imageExists("assets/art/ranch.jpg", function (u) {
    injectMedia("ranchMedia", u, "小牧场 / Ranch");
  });
})();
