/* VoltRide — consent banner + consent-gated Google Analytics (shared by every page) */
(function () {
  "use strict";
  var GA_ID = "G-M4CWL77NBK";
  var KEY = "voltride_consent"; // "granted" | "denied"

  var T = {
    ar: {
      text: "نستعمل Google Analytics (كوكيز) لقياس الزيارات وتحسين VoltRide. لن يعمل إلا بعد موافقتك، ويمكنك التراجع في أي وقت من الإعدادات.",
      ok: "موافق", no: "رفض", more: "سياسة الخصوصية", dir: "rtl"
    },
    fr: {
      text: "Nous utilisons Google Analytics (cookies) pour mesurer l'audience et améliorer VoltRide. Il ne s'active qu'avec votre accord, modifiable à tout moment dans les réglages.",
      ok: "Accepter", no: "Refuser", more: "Confidentialité", dir: "ltr"
    },
    en: {
      text: "We use Google Analytics (cookies) to measure visits and improve VoltRide. It only runs with your consent, which you can change anytime in Settings.",
      ok: "Accept", no: "Decline", more: "Privacy policy", dir: "ltr"
    }
  };

  function lang() {
    try {
      var raw = localStorage.getItem("voltride_language");
      var l = raw ? JSON.parse(raw) : null;
      if (T[l]) return l;
    } catch (e) {}
    var d = (document.documentElement.lang || "ar").slice(0, 2);
    return T[d] ? d : "ar";
  }
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function loadGA() {
    if (window.__voltGA) return;
    window.__voltGA = true;
    window["ga-disable-" + GA_ID] = false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
    window.gtag("js", new Date());
    window.gtag("config", GA_ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
  }

  function disableGA() {
    window["ga-disable-" + GA_ID] = true;
    try {
      document.cookie.split(";").forEach(function (c) {
        var n = c.split("=")[0].trim();
        if (n.indexOf("_ga") === 0) {
          document.cookie = n + "=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
        }
      });
    } catch (e) {}
  }

  function injectStyle() {
    if (document.getElementById("voltConsentStyle")) return;
    var st = document.createElement("style");
    st.id = "voltConsentStyle";
    st.textContent =
      "#voltConsent{position:fixed;inset-inline:12px;bottom:12px;z-index:9999;max-width:560px;margin:auto;background:#111827;color:#f8fafc;border:1px solid rgba(0,242,254,.35);border-radius:16px;padding:14px 16px;box-shadow:0 16px 45px rgba(0,0,0,.45);font:13px/1.7 system-ui,-apple-system,'Segoe UI',Arial,sans-serif}" +
      "#voltConsent.has-nav{bottom:calc(84px + env(safe-area-inset-bottom))}" +
      "#voltConsent p{margin:0 0 10px;color:#cbd5e1}" +
      "#voltConsent .row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}" +
      "#voltConsent button{border:0;border-radius:10px;padding:9px 16px;font:inherit;font-weight:800;cursor:pointer}" +
      "#voltConsent .ok{background:linear-gradient(135deg,#00f2fe,#38bdf8);color:#001116}" +
      "#voltConsent .no{background:#1e293b;color:#f8fafc;border:1px solid rgba(148,163,184,.3)}" +
      "#voltConsent a{color:#00f2fe;font-size:12px;margin-inline-start:auto}";
    document.head.appendChild(st);
  }

  function hideBanner() {
    var el = document.getElementById("voltConsent");
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function showBanner() {
    hideBanner();
    injectStyle();
    var t = T[lang()];
    var el = document.createElement("div");
    el.id = "voltConsent";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-label", "Cookies");
    el.setAttribute("dir", t.dir);
    if (document.querySelector(".bottom-nav")) el.className = "has-nav";
    var p = document.createElement("p");
    p.textContent = t.text;
    var row = document.createElement("div");
    row.className = "row";
    var ok = document.createElement("button");
    ok.className = "ok"; ok.type = "button"; ok.textContent = t.ok;
    var no = document.createElement("button");
    no.className = "no"; no.type = "button"; no.textContent = t.no;
    var a = document.createElement("a");
    a.href = "privacy.html"; a.textContent = t.more;
    ok.onclick = function () { set("granted"); loadGA(); hideBanner(); };
    no.onclick = function () { set("denied"); disableGA(); hideBanner(); };
    row.appendChild(ok); row.appendChild(no); row.appendChild(a);
    el.appendChild(p); el.appendChild(row);
    document.body.appendChild(el);
  }

  window.VoltConsent = {
    open: showBanner,
    status: get,
    revoke: function () { set("denied"); disableGA(); }
  };

  function init() {
    var s = get();
    if (s === "granted") loadGA();
    else if (s !== "denied") showBanner();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("sw.js").catch(function () {});
    });
  }
})();
