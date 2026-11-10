import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const home = readFileSync("index.html", "utf8");
const frArticle = readFileSync("fr/article-10.html", "utf8");
const description = html => html.match(/<meta\s+name="description"\s+content="([^"]*)"\s*>/i)?.[1] || "";
const homeDescription = description(home);
const frDescription = description(frArticle);

assert.ok(homeDescription.length >= 80, "homepage must have a complete meta description");
assert.doesNotMatch(homeDescription, /Morocco|Maroc|المغرب|MAD|درهم/i, "homepage description should not target one country or currency");
assert.match(home, /<title>VoltRide.*مدى السكوتر الكهربائي/);
assert.equal((home.match(/<h1\b/gi) || []).length, 1, "homepage should have exactly one primary H1 heading");
assert.ok(frDescription.length >= 80, "French article 10 must have a valid meta description");
assert.match(frDescription, /Casque.*antivol.*éclairage/i);
const enContact = readFileSync("en/contact.html", "utf8");
const frContact = readFileSync("fr/contact.html", "utf8");
assert.notEqual(enContact.match(/<title>(.*?)<\/title>/i)?.[1], frContact.match(/<title>(.*?)<\/title>/i)?.[1], "localized contact pages should have distinct titles");
assert.doesNotMatch(frArticle, /<meta\s+name="description"\s+content">/i, "malformed description attribute must not return");

const schemaTag = '<script type="application/ld+json">';
const schemaStart = home.indexOf(schemaTag);
assert.notEqual(schemaStart, -1, "homepage structured data should exist");
const jsonStart = schemaStart + schemaTag.length;
const schemaEnd = home.indexOf("</script>", jsonStart);
assert.notEqual(schemaEnd, -1, "homepage structured data must close");
const jsonLd = JSON.parse(home.slice(jsonStart, schemaEnd));
assert.equal(jsonLd.isAccessibleForFree, true);
assert.ok(!jsonLd.offers, "avoid a country-specific MAD offer for a free global utility");

console.log("SEO metadata tests passed: global homepage description and valid French article metadata.");
