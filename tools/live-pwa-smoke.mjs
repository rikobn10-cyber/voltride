import assert from "node:assert/strict";
import { chromium } from "playwright";

const base = (process.argv[2] || "https://voltride-4qj.pages.dev").replace(/\/$/, "");
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  serviceWorkers: "allow"
});
const page = await context.newPage();
const errors = [];
context.on("serviceworker", worker => {
  worker.on("console", message => console.log("SERVICE WORKER:", message.text()));
  worker.on("error", error => console.log("SERVICE WORKER ERROR:", error.message));
});
page.on("pageerror", error => errors.push(error.message));

try {
  const response = await page.goto(base + "/", { waitUntil: "load", timeout: 30000 });
  assert.ok(response?.ok(), "production homepage must load over HTTPS");
  assert.equal(new URL(base).protocol, "https:", "PWA production origin must use HTTPS");

  // This is a non-consenting test visitor. Never generate synthetic GA4 events.
  const consent = page.locator("#voltConsent");
  if (await consent.count()) await consent.locator("button.no").click();
  assert.equal(await page.evaluate(() => window.__voltGA === true), false,
    "declining consent must not initialize Google Analytics");

  const manifestHref = await page.locator('link[rel="manifest"]').getAttribute("href");
  assert.ok(manifestHref, "homepage must link to a web app manifest");
  const manifestUrl = new URL(manifestHref, base + "/").href;
  const manifestResponse = await page.request.get(manifestUrl);
  assert.ok(manifestResponse.ok(), "web app manifest must be reachable");
  const manifest = await manifestResponse.json();
  assert.equal(manifest.display, "standalone", "manifest must request standalone display");
  assert.ok(manifest.name && manifest.short_name, "manifest must declare app names");
  const startUrl = new URL(manifest.start_url, manifestUrl);
  const scopeUrl = new URL(manifest.scope || "./", manifestUrl);
  assert.equal(startUrl.origin, scopeUrl.origin, "PWA start URL must share the manifest scope origin");
  assert.ok(startUrl.pathname.startsWith(scopeUrl.pathname), "PWA start URL must be inside its declared scope");
  assert.ok(Array.isArray(manifest.icons) && manifest.icons.length >= 2, "manifest must declare app icons");
  for (const icon of manifest.icons) {
    const iconResponse = await page.request.get(new URL(icon.src, manifestUrl).href);
    assert.ok(iconResponse.ok(), "manifest icon must be reachable: " + icon.src);
  }

  // Wait for install + activation, then reload so this page is controlled by the worker.
  const workerInfo = await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    if (!registration.active) throw new Error("service worker has no active worker");
    const script = await fetch("/sw.js", { cache: "no-store" }).then(r => r.text());
    const version = script.match(/const VERSION = ["']([^"']+)["']/)?.[1];
    if (!version) throw new Error("service worker cache version is missing");
    const cache = await caches.open(version);
    const urls = (await cache.keys()).map(request => new URL(request.url).pathname);
    return {
      scope: registration.scope,
      activeState: registration.active.state,
      version,
      urls,
      controlled: Boolean(navigator.serviceWorker.controller)
    };
  });
  assert.equal(workerInfo.activeState, "activated", "service worker must be activated");
  assert.equal(workerInfo.version, "voltride-v21", "the new service worker version must be active");
  assert.ok(workerInfo.scope.startsWith(base + "/"), "service worker scope must match production origin");
  for (const path of ["/offline.html", "/ride-match.html", "/navee-g5.html"]) {
    assert.ok(workerInfo.urls.some(url => url.endsWith(path)), "precache must include " + path);
  }
  if (!workerInfo.controlled) {
    await page.reload({ waitUntil: "load" });
    await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller), { timeout: 10000 });
  }

  // Confirm the installed application can load precached clean URLs without network access.
  const cacheProbe = await page.evaluate(async () => {
    const registration = await navigator.serviceWorker.ready;
    const cache = await caches.open("voltride-v21");
    const offlineUrl = new URL("offline.html", registration.scope).href;
    return { offlineUrl, hasOfflineFallback: Boolean(await cache.match(offlineUrl)), controlled: Boolean(navigator.serviceWorker.controller), online: navigator.onLine, scope: registration.scope };
  });
  console.log("PWA cache probe", JSON.stringify(cacheProbe));
  assert.equal(cacheProbe.hasOfflineFallback, true, "offline fallback must exist in the active service worker cache");
  await context.setOffline(true);
  const ride = await page.goto(base + "/ride-match", { waitUntil: "domcontentloaded", timeout: 15000 });
  assert.ok(ride?.ok(), "cached Ride Match clean URL must load offline");
  await page.locator("#rideMarket").waitFor({ state: "visible", timeout: 5000 });

  const model = await page.goto(base + "/navee-g5", { waitUntil: "domcontentloaded", timeout: 15000 });
  assert.ok(model?.ok(), "cached model detail clean URL must load offline");
  assert.ok(await page.locator("h1").count(), "offline model page must retain its main heading");

  // An uncached route should return the designed offline fallback, not a browser network error.
  let fallback = null;
  let fallbackNavigationError = null;
  try {
    fallback = await page.goto(base + "/__voltride_offline_probe_20261111__/pwa-offline-test?probe=1", {
      waitUntil: "domcontentloaded",
      timeout: 15000
    });
  } catch (error) {
    fallbackNavigationError = error.message;
  }
  const fallbackDiagnostic = await page.evaluate(() => ({ url: location.href, title: document.title, online: navigator.onLine, controlled: Boolean(navigator.serviceWorker.controller), body: document.body.innerText.slice(0, 300) })).catch(error => ({ error: error.message }));
  console.log("PWA fallback diagnostic", JSON.stringify({ status: fallback?.status(), navigationError: fallbackNavigationError, diagnostic: fallbackDiagnostic }));
  await page.getByText("لا يوجد اتصال بالإنترنت").waitFor({ state: "visible", timeout: 5000 });
  assert.ok(fallback || fallbackNavigationError, "offline fallback navigation must be attempted");
  assert.deepEqual(errors, [], "PWA routes must not throw uncaught browser errors");

  console.log(JSON.stringify({
    status: "passed",
    manifest: { display: manifest.display, icons: manifest.icons.length, startUrl: manifest.start_url },
    serviceWorker: { version: workerInfo.version, active: workerInfo.activeState, precacheEntries: workerInfo.urls.length },
    offline: { rideMatch: "passed", modelPage: "passed", fallback: "passed" },
    analytics: "consent declined; no synthetic events sent",
    pageErrors: errors
  }));
} finally {
  await context.close();
  await browser.close();
}
