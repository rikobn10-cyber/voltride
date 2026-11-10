import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const html = readFileSync("index.html", "utf8");
const start = html.indexOf("const CURRENCY_BY_REGION = {");
const end = html.indexOf("\nlet tariffs =", start);
assert.ok(start >= 0 && end > start, "currency region detection block must exist");
const detector = html.slice(start, end);

function detect(languages, timeZone = "UTC") {
  const context = {
    navigator: { languages, language: languages[0] || "" },
    Intl: { DateTimeFormat: () => ({ resolvedOptions: () => ({ timeZone }) }) }
  };
  return vm.runInNewContext(detector + "\ndetectDefaultCurrency();", context);
}

assert.equal(detect(["en-US"]), "USD", "US browser region should default to USD");
assert.equal(detect(["fr-FR"]), "EUR", "French language in France should default to EUR");
assert.equal(detect(["fr-CA"]), "USD", "French language in Canada must not imply EUR");
assert.equal(detect(["en-GB"]), "USD", "English language in the UK must not imply USD from language alone; unsupported region uses USD fallback");
assert.equal(detect(["ar-MA"]), "MAD", "Morocco browser region should default to MAD");
assert.equal(detect(["ar"], "Africa/Casablanca"), "MAD", "Morocco timezone should be a fallback when browser locale has no region");
assert.equal(detect(["en-CA", "fr-FR"]), "EUR", "first supported browser locale should determine the default");
assert.equal(detect(["de-CH"]), "USD", "unsupported region should use the documented USD fallback");
console.log("Currency locale tests passed");
