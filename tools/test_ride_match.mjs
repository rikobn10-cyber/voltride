import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const html = readFileSync("ride-match.html", "utf8");
const indexHtml = readFileSync("index.html", "utf8");
const v2 = JSON.parse(readFileSync("model_data_v2.json", "utf8"));
const scriptMatch = html.match(/<script>([\\s\\S]*?)<\\/script>\\s*<\\/body>/i);
assert.ok(scriptMatch, "Ride Match inline application script must exist");

const elements = new Map();
function element(id = "") {
  if (!elements.has(id)) {
    const listeners = {};
    const el = {
      id, value: "", textContent: "", innerHTML: "",
      style: { display: "none", width: "" },
      classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
      addEventListener(type, callback) { listeners[type] = callback; },
      appendChild(child) { (this.children ||= []).push(child); },
      children: [],
      listeners
    };
    elements.set(id, el);
  }
  return elements.get(id);
}
const context = {
  document: {
    documentElement: { lang: "ar", dir: "rtl" },
    title: "",
    querySelectorAll: () => [],
    getElementById: id => element(id),
    createElement: tag => element(tag + "-" + Math.random())
  },
  localStorage: { getItem: () => JSON.stringify("fr"), setItem: () => {} },
  setTimeout: () => 0,
  console
};
vm.createContext(context);
vm.runInContext(scriptMatch[1], context);
const evaluate = expression => vm.runInContext(expression, context);

const markets = JSON.parse(evaluate("JSON.stringify(RIDE_MATCH_MARKETS)"));
const models = JSON.parse(evaluate("JSON.stringify(RIDE_MATCH_MODELS)"));
assert.deepEqual(markets, [...new Set(markets)].sort(), "market list must be unique and sorted");
assert.ok(markets.includes("MA"), "Morocco market must be available when verified variants exist");
assert.equal(element("rideMarket").children.length, markets.length, "market selector must expose every generated market");
assert.equal(models.length, 19, "only model identities with projectable verified variants should be generated");
assert.ok(models.every(model => model.variants.length > 0));

for (const model of models) {
  assert.ok(model.variants.every(variant => markets.includes(variant.market)), model.id + ": each option must map to a generated market");
  assert.ok(model.variants.every(variant => variant.energyWh > 0 && variant.voltage > 0 && variant.ah > 0 && variant.motor > 0 && variant.speed > 0));
  assert.ok(model.variants.every(variant => variant.sourceUrl && variant.sourcePublisher));
}

for (const market of markets) {
  evaluate("answers = { market: " + JSON.stringify(market) + ', distance: "20-40", preference: "range" }');
  const eligible = JSON.parse(evaluate("JSON.stringify(getEligibleScooters())"));
  const recommendations = JSON.parse(evaluate("JSON.stringify(getRecommendations())"));
  assert.ok(eligible.length > 0, market + ": verified candidates should exist");
  assert.ok(eligible.every(model => model.market === market), market + ": candidates must match the selected market");
  assert.equal(new Set(eligible.map(model => model.id)).size, eligible.length, market + ": model candidates must be unique");
  assert.ok(recommendations.length > 0 && recommendations.length <= 3);
  assert.ok(recommendations.every(item => item.s.market === market));
  assert.ok(recommendations.every(item => Number.isFinite(item.range) && item.range > 0));
}

for (const preference of ["speed", "range", "commuter", "performance"]) {
  evaluate('answers = { market: "EU", distance: "20-40", preference: "' + preference + '" }');
  const recommendations = JSON.parse(evaluate("JSON.stringify(getRecommendations())"));
  assert.ok(recommendations.length > 0, preference + ": should return verified recommendations");
  assert.equal(new Set(recommendations.map(item => item.s.id)).size, recommendations.length, preference + ": recommendations must be unique");
}

evaluate('answers = { market: "MA", distance: "20-40", preference: "range" }');
const morocco = JSON.parse(evaluate("JSON.stringify(getEligibleScooters())"));
assert.ok(morocco.some(model => model.id === "ecoxtrem-bison-gt"));
assert.ok(morocco.some(model => model.id === "ecoxtrem-bison-m41"));
assert.ok(morocco.every(model => model.market === "MA"));
assert.ok(morocco.every(model => model.variantId && model.variantLabel));

evaluate('answers = { market: null, distance: "20-40", preference: "range" }');
assert.equal(evaluate("getRecommendations().length"), 0, "recommendations must be empty until a market is explicitly selected");

evaluate('answers = { market: "US", distance: "20-40", preference: "range" }');
evaluate("renderResults()");
const rendered = element("recommendations").innerHTML;
assert.match(rendered, /Battery energy|Énergie de la batterie|طاقة البطارية/);
assert.match(rendered, /Manufacturer source|Source du fabricant|مصدر الشركة المصنّعة/);
assert.match(rendered, /variantId|US|EU/);
assert.match(rendered, /aliexpress\\.com\\/wholesale/);
assert.doesNotMatch(rendered, /s\\.click\\.aliexpress/);
assert.doesNotMatch(rendered, /rel="noopener sponsored nofollow"/);

assert.doesNotMatch(html, /const uniqueScooters|uniqueScooters\\.slice/);
assert.doesNotMatch(html, /const scooters = \\[/);
assert.match(html, /\\/\\*RIDE_VARIANTS:START\\*\\/[\\s\\S]*?\\/\\*RIDE_VARIANTS:END\\*\\//);
assert.match(html, /if \\(!answers\\.market\\) return \\[\\];/);
assert.match(html, /RIDE_MATCH_MODELS\\.flatMap/);
assert.match(html, /answers\\.market = RIDE_MATCH_MARKETS\\.includes/);
assert.doesNotMatch(html, /s\\.voltage|s\\.ah|s\\.power/);
assert.doesNotMatch(html, /affiliateOnlyModels|iscooter-w9|iscooter-ix4|iscooter-w6/);
assert.doesNotMatch(html, /s\\.affiliateUrl/);
assert.match(html, /marketplace_search_click/);
assert.match(html, /data-action="buy"/);

const expectedVerifiedIds = v2.models
  .filter(model => model.variants.some(variant =>
    variant.verification?.status === "verified_variant" &&
    variant.verification?.confidence === "high"
  ))
  .map(model => model.id);
assert.deepEqual(models.map(model => model.id), expectedVerifiedIds, "Ride Match model identities must follow canonical V2 order and verification status");
assert.equal(models.reduce((n, model) => n + model.variants.length, 0), 22, "all verified market-specific choices must be generated");

assert.equal(evaluate("rideMatchLang"), "fr", "Ride Match should inherit the saved site language");
assert.equal(evaluate('rideMatchT("speed")'), "Vitesse");
evaluate('setRideMatchLanguage("en")');
assert.equal(evaluate("document.documentElement.lang"), "en");
assert.equal(evaluate("document.documentElement.dir"), "ltr");
assert.equal(evaluate('rideMatchT("buy")'), "Buy now ←");
evaluate('setRideMatchLanguage("ar")');
assert.equal(evaluate("document.documentElement.dir"), "rtl");
assert.match(html, /table-layout:fixed/);
assert.match(indexHtml, /specSpeed:"Vitesse"/);
assert.match(indexHtml, /specSpeed:"Speed"/);
console.log("Ride Match V2 tests passed: explicit market selection, verified variants, provenance, and safe marketplace fallback.");
