import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join, relative, sep } from "node:path";

const sw = readFileSync("sw.js", "utf8");
const match = sw.match(/const PRECACHE = \[([\s\S]*?)\];/);
assert.ok(match, "service worker precache array must exist");
const precache = JSON.parse("[" + match[1] + "]");
assert.ok(precache.includes("ride-match.html"), "Ride Match must be available offline");
assert.ok(precache.includes("offline.html"), "offline fallback must be precached");
assert.equal(new Set(precache).size, precache.length, "precache entries must be unique");
assert.match(sw, /const VERSION = "voltride-v22";/, "cache version must change when the precache changes");

function collectHtml(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return collectHtml(path);
    return entry.isFile() && entry.name.endsWith(".html") ? [path] : [];
  });
}
for (const locale of ["en", "fr"]) {
  for (const file of collectHtml(locale)) {
    const precachePath = relative(".", file).split(sep).join("/");
    assert.ok(precache.includes(precachePath), locale + " page must be available offline: " + precachePath);
  }
}

assert.match(sw, /if \(req\.mode === "navigate"\)/, "navigation requests must use the offline-aware strategy");
assert.match(sw, /new URL\("offline\.html", self\.registration\.scope\)/, "offline fallback must use an absolute scope URL");
assert.match(sw, /self\.navigator\.onLine === false/, "resolved offline error responses must use the offline fallback");
assert.match(sw, /async function networkIsReachable\(\)/, "offline navigation must verify connectivity with a live resource probe");
assert.match(sw, /await networkIsReachable\(\)/, "HTTP error navigations must distinguish offline failures from real 404 responses");
assert.match(sw, /Response\.redirect\(page\.url, 302\)/, "cached clean URLs must redirect to their exact cached document URL");
assert.match(sw, /Response\.redirect\(offlineUrl, 302\)/, "uncached offline navigations must redirect to the cached offline page");
assert.match(sw, /new URL\(path, self\.registration\.scope\)/, "cache matching must resolve URLs against the service worker scope");
assert.doesNotMatch(sw, /DEBUG_CACHE|TEST_NAVIGATE/, "temporary PWA diagnostics must not ship in the service worker");
console.log("PWA tests passed: localized HTML precache coverage, Ride Match, offline fallback, unique entries and cache version.");
