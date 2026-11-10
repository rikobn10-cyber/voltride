import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const html = readFileSync("ride-match.html", "utf8");
const indexHtml = readFileSync("index.html", "utf8");
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/i);
assert.ok(scriptMatch, "Ride Match inline application script must exist");

const context = {
  document: { documentElement: { lang: "ar", dir: "rtl" }, title: "", querySelectorAll: () => [], getElementById: () => ({ addEventListener: () => {}, style: { display: "none" } }) },
  localStorage: { getItem: () => JSON.stringify("fr"), setItem: () => {} },
  setTimeout: () => 0,
  console
};
vm.createContext(context);
vm.runInContext(scriptMatch[1], context);
const evaluate = expression => vm.runInContext(expression, context);

assert.equal(evaluate("scooters.length"), 35, "duplicate model records should be removed");
assert.equal(evaluate("uniqueScooters.length"), 35, "all unique models should remain");
assert.equal(evaluate("new Set(uniqueScooters.map(s => s.id)).size"), 35, "model IDs must be unique");

assert.doesNotMatch(html, /budgetTitle|budgetNote|budgetOptions|budget_range|parseBudgetRange|getBudgetScore|\\bMAD\\b|درهم/);
assert.doesNotMatch(html, /"price":\\d+/);
assert.match(html, /data-action="buy"/);
assert.doesNotMatch(html, /indexOf\\('اشترِ الآن'\\)/);

for (const preference of ["speed", "range", "commuter", "performance"]) {
  evaluate('"answers = { distance: "20-40", preference: "' + preference + '" }');
  const ids = JSON.parse(evaluate("JSON.stringify(getRecommendations().map(r => r.s.id))"));
  assert.equal(ids.length, 3, preference + ": should return three recommendations");
  assert.equal(new Set(ids).size, 3, preference + ": recommendations must be unique");
}

assert.match(html, /بعض روابط الشراء روابط إحالة/);
assert.equal(evaluate("rideMatchLang"), "fr", "Ride Match should inherit the saved site language");
assert.equal(evaluate('rideMatchT("speed")'), "Vitesse");
assert.equal(evaluate('rideMatchT("resultsTitle")'), "🎯 Nos recommandations");
evaluate('setRideMatchLanguage("en")');
assert.equal(evaluate("document.documentElement.lang"), "en");
assert.equal(evaluate("document.documentElement.dir"), "ltr");
assert.equal(evaluate('rideMatchT("buy")'), "Buy now ←");
evaluate('setRideMatchLanguage("ar")');
assert.equal(evaluate("document.documentElement.dir"), "rtl");
assert.match(html, /table-layout:fixed/);
assert.match(html, /color:var\(--cyan\)/);
assert.doesNotMatch(html, /border-collapse:;/);
assert.match(indexHtml, /specSpeed:"Vitesse"/);
assert.match(indexHtml, /specSpeed:"Speed"/);
assert.match(indexHtml, /t\("specSpeed"\)/);
assert.match(indexHtml, /t\("compareSpeed"\)/);
assert.match(indexHtml, /class="table-wrap"/);
assert.match(indexHtml, /\.table-wrap\{width:100%/);
assert.match(html, /data-value="commuter"/);
assert.match(html, /data-value="performance"/);
assert.doesNotMatch(html, /data-value="comfort"|data-value="weight"/);
console.log("Ride Match tests passed: unique models, global budget-neutral recommendations, supported preferences, and affiliate disclosure.");
