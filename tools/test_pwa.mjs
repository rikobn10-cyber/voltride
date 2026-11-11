import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const sw = readFileSync("sw.js", "utf8");
const match = sw.match(/const PRECACHE = \[([\s\S]*?)\];/);
assert.ok(match, "service worker precache array must exist");
const precache = JSON.parse("[" + match[1] + "]");
assert.ok(precache.includes("ride-match.html"), "Ride Match must be available offline");
assert.ok(precache.includes("offline.html"), "offline fallback must be precached");
assert.equal(new Set(precache).size, precache.length, "precache entries must be unique");
assert.match(sw, /const VERSION = "voltride-v21";/, "cache version must change when the precache changes");
assert.match(sw, /if \(req\.mode === "navigate"\)/, "navigation requests must use the offline-aware strategy");
assert.match(sw, /new URL\("offline\.html", self\.registration\.scope\)/, "offline fallback must use an absolute scope URL");
assert.match(sw, /self\.navigator\.onLine === false/, "resolved offline error responses must use the offline fallback");
console.log("PWA tests passed: Ride Match precache, offline fallback, unique entries and cache version.");
