import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync("site.js", "utf8");
const storage = new Map();
const head = { children: [], appendChild(node) { node.parentNode = this; this.children.push(node); } };
const body = { children: [], appendChild(node) { node.parentNode = this; this.children.push(node); }, removeChild(node) { this.children = this.children.filter(item => item !== node); node.parentNode = null; } };
const document = {
  readyState: "complete",
  cookie: "",
  documentElement: { lang: "ar" },
  head, body,
  createElement(tag) { return { tagName: tag, children: [], setAttribute() {}, appendChild(node) { this.children.push(node); } }; },
  getElementById(id) { return [...head.children, ...body.children].find(node => node.id === id) || null; },
  querySelector() { return null; },
  querySelectorAll() { return []; }
};
const window = { location: { hostname: "voltride-4qj.pages.dev" }, addEventListener() {} };
const navigator = { serviceWorker: { register: () => Promise.resolve() } };
const localStorage = { getItem(key) { return storage.has(key) ? storage.get(key) : null; }, setItem(key, value) { storage.set(key, String(value)); } };
const context = { document, window, navigator, localStorage, console, Promise };
vm.createContext(context);
vm.runInContext(source, context);

const banner = () => body.children.find(node => node.id === "voltConsent");
const click = index => { const node = banner(); assert.ok(node, "consent banner should be visible"); node.children[1].children[index].onclick(); };
const gaScripts = () => head.children.filter(node => node.tagName === "script" && /googletagmanager/.test(node.src || ""));
assert.ok(banner(), "first visit should show the consent banner");
click(0);
assert.equal(storage.get("voltride_consent"), "granted");
assert.equal(gaScripts().length, 1, "accepting should load GA once");
const gaDisableKey = Object.keys(window).find(key => key.startsWith("ga-disable-"));
assert.ok(gaDisableKey, "GA disable flag should be initialized");
assert.equal(window[gaDisableKey], false);
window.VoltConsent.open();
click(1);
assert.equal(storage.get("voltride_consent"), "denied");
assert.equal(window[gaDisableKey], true, "rejecting should disable GA");
window.VoltConsent.open();
click(0);
assert.equal(storage.get("voltride_consent"), "granted");
assert.equal(window[gaDisableKey], false, "re-accepting must re-enable the already-loaded GA instance");
assert.equal(gaScripts().length, 1, "re-accepting must not inject a second GA script");

const previewStorage = new Map([["voltride_consent", "granted"]]);
const previewHead = { children: [], appendChild(node) { node.parentNode = this; this.children.push(node); } };
const previewBody = { children: [], appendChild(node) { node.parentNode = this; this.children.push(node); }, removeChild(node) { this.children = this.children.filter(item => item !== node); node.parentNode = null; } };
const previewDocument = {
  readyState: "complete", cookie: "", documentElement: { lang: "en" }, head: previewHead, body: previewBody,
  createElement(tag) { return { tagName: tag, children: [], setAttribute() {}, appendChild(node) { this.children.push(node); } }; },
  getElementById(id) { return [...previewHead.children, ...previewBody.children].find(node => node.id === id) || null; },
  querySelector() { return null; }, querySelectorAll() { return []; }
};
const previewWindow = { location: { hostname: "feature-branch.voltride-4qj.pages.dev" }, addEventListener() {} };
const previewContext = {
  document: previewDocument, window: previewWindow,
  navigator: { serviceWorker: { register: () => Promise.resolve() } },
  localStorage: { getItem(key) { return previewStorage.has(key) ? previewStorage.get(key) : null; }, setItem(key, value) { previewStorage.set(key, String(value)); } },
  console, Promise
};
vm.createContext(previewContext);
vm.runInContext(source, previewContext);
assert.equal(previewWindow.__voltGA, undefined, "preview hosts must not initialize GA");
assert.equal(previewHead.children.filter(node => node.tagName === "script" && /googletagmanager/.test(node.src || "")).length, 0, "preview hosts must not inject GA");
assert.equal(previewWindow.VoltAnalytics.track("ride_match_complete"), false, "preview hosts must not send product events");
assert.equal(previewBody.children.some(node => node.id === "voltConsent"), false, "preview hosts must not show the analytics consent banner");

console.log("Consent tests passed: production-only GA, accept/reject/re-accept, and preview exclusion.");
