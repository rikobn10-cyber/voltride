import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const html = readFileSync("ride-match.html", "utf8");
const indexHtml = readFileSync("index.html", "utf8");
const modelCatalog = JSON.parse(readFileSync("models.json", "utf8")).models;
const rideMatchData = JSON.parse(readFileSync("ride_match_data.json", "utf8"));
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
const rideModels = JSON.parse(evaluate("JSON.stringify(scooters)"));
for (const model of modelCatalog) {
  const rideModel = rideModels.find(item => item.id === model.id);
  assert.ok(rideModel, model.id + ": catalog model must appear in Ride Match");
  assert.equal(rideModel.name, model.name, model.id + ": name must match catalog");
  assert.equal(rideModel.speed, model.speed, model.id + ": speed must match catalog");
  assert.equal(rideModel.power, model.motor, model.id + ": motor power must match catalog");
  assert.equal(rideModel.voltage, model.voltage, model.id + ": voltage must match catalog");
  assert.equal(rideModel.ah, model.ah, model.id + ": battery capacity must match catalog");
  assert.equal(rideModel.cat, model.category, model.id + ": category must match catalog");
}

for (const model of rideMatchData.affiliateOnlyModels) {
  const rideModel = rideModels.find(item => item.id === model.id);
  assert.ok(rideModel, model.id + ": affiliate-only model must appear in Ride Match");
  for (const [field, value] of Object.entries(model)) {
    assert.equal(rideModel[field], value, model.id + ": " + field + " must match affiliate-only source");
  }
}
for (const id of rideMatchData.excludedModelIds) {
  const rideModel = rideModels.find(item => item.id === id);
  assert.ok(rideModel, id + ": excluded canonical model must exist");
  assert.equal(rideModel.eligible, false, id + ": configured exclusions must stay ineligible");
}
assert.match(html, /\/\*SCOOTERS:START\*\/[\s\S]*?\/\*SCOOTERS:END\*\//,
  "Ride Match scooter records must be generator-owned");


assert.doesNotMatch(html, /budgetTitle|budgetNote|budgetOptions|budget_range|parseBudgetRange|getBudgetScore|\bMAD\b|درهم/);
assert.doesNotMatch(html, /"price":\d+/);
const sourceVerifiedAffiliateModels = {
  "iscooter-w9": { speed: 45, power: 1000, voltage: 48, ah: 14 },
  "iscooter-ix4": { speed: 45, power: 800, voltage: 48, ah: 15 },
  "iscooter-w9air": { speed: 40, power: 800, voltage: 48, ah: 10 },
  "iscooter-ix5s": { speed: 45, power: 1000, voltage: 48, ah: 15 }
};
for (const [id, specs] of Object.entries(sourceVerifiedAffiliateModels)) {
  const model = rideModels.find(item => item.id === id);
  assert.ok(model, id + ": sourced affiliate model must remain in Ride Match");
  for (const [field, value] of Object.entries(specs)) assert.equal(model[field], value, id + ": " + field + " must match official manufacturer data");
}
const w6 = rideModels.find(item => item.id === "iscooter-w6");
assert.equal(w6.eligible, false, "W6 regional battery variants must not be recommended until the affiliate SKU is matched to a region");
assert.equal(evaluate('getRecommendations().some(r => r.s.id === "iscooter-w6")'), false, "region-ambiguous W6 must be excluded from recommendations");
for (const id of ["ecoxtrem-bison-gt", "ecoxtrem-bison-m41"]) {
  assert.equal(evaluate('getRecommendations().some(r => r.s.id === "' + id + '")'), false, id + ": unresolved regional/model variant must be excluded from recommendations");
}
assert.match(html, /data-action="buy"/);
assert.doesNotMatch(html, /indexOf\('اشترِ الآن'\)/);

for (const preference of ["speed", "range", "commuter", "performance"]) {
  evaluate('answers = { distance: "20-40", preference: "' + preference + '" }');
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
