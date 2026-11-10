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
const enBlog = readFileSync("en/blog.html", "utf8");
const frBlog = readFileSync("fr/blog.html", "utf8");
const arAccessories = readFileSync("accessories.html", "utf8");
const enAccessories = readFileSync("en/accessories.html", "utf8");
const frAccessories = readFileSync("fr/accessories.html", "utf8");
const sitemap = readFileSync("sitemap.xml", "utf8");
assert.ok((enBlog.match(/class="article-card"/g) || []).length >= 10, "English blog should surface its translated articles");
assert.ok((frBlog.match(/class="article-card"/g) || []).length >= 6, "French blog should surface its translated articles");
assert.doesNotMatch(frBlog, /href="\/fr\/article-6"/, "French blog must not link to an untranslated article");
assert.doesNotMatch(arAccessories + enAccessories + frAccessories, /Tool Charger|Kids E-Moto/, "accessories pages must not promote unrelated products");
assert.match(enAccessories, /hreflang="fr"/);
assert.match(frAccessories, /hreflang="en"/);
assert.match(readFileSync("blog.html", "utf8"), /href="\/accessories"/, "Arabic blog should link to accessories");
assert.match(enBlog, /href="\/en\/accessories"/, "English blog should link to accessories");
assert.match(frBlog, /href="\/fr\/accessories"/, "French blog should link to accessories");

assert.match(sitemap, /<loc>https:\/\/voltride-4qj\.pages\.dev\/en\/accessories<\/loc>/);
assert.match(sitemap, /<loc>https:\/\/voltride-4qj\.pages\.dev\/fr\/accessories<\/loc>/);

const titleAuditFiles = [
  "article-7.html", "article-choosing-charger.html", "blog.html",
  "en/article-10.html", "en/article-4.html", "en/article-8.html",
  "en/blog/charger-safety.html", "en/blog/choosing-charger.html",
  "fr/article-10.html", "fr/article-11.html", "fr/article-7.html",
  "fr/article-8.html", "fr/comment-choisir-chargeur-trottinette.html",
  "en/article-7.html", "fr/about.html"
];
for (const path of titleAuditFiles) {
  const page = readFileSync(path, "utf8");
  const title = page.match(/<title>(.*?)<\/title>/i)?.[1] || "";
  const description = page.match(/<meta name="description" content="(.*?)">/i)?.[1] || "";
  assert.ok(title.length > 0 && title.length <= 60, path + ": title should be concise");
  assert.ok(description.length > 0 && description.length <= 160, path + ": meta description should be concise");
}
assert.doesNotMatch(readFileSync("blog.html", "utf8").match(/<title>(.*?)<\/title>/i)?.[1] || "", /المغرب/, "Arabic blog title should be global, not Morocco-specific");

for (const path of ["index.html", "blog.html", "about.html", "contact.html", "privacy.html", "accessories.html", "ride-match.html", "article-1.html", "article-3.html", "article-4.html", "article-9.html", "article-choosing-charger.html", "blog/charger-safety.html", "guides/not-charging.html"]) {
  assert.doesNotMatch(readFileSync(path, "utf8"), /<meta property="og:locale" content="ar_MA">/, path + ": global Arabic page must not claim a Morocco-only locale");
}
for (const path of ["article-2.html", "article-5.html", "article-6.html", "article-7.html", "article-8.html", "article-10.html"]) {
  assert.match(readFileSync(path, "utf8"), /<meta property="og:locale" content="ar_MA">/, path + ": Morocco-specific Arabic content should retain its regional locale");
}

const generatedModels = JSON.parse(readFileSync("models.json", "utf8")).models;
for (const model of generatedModels) {
  const modelPage = readFileSync(model.id + ".html", "utf8");
  const modelTitle = modelPage.match(/<title>(.*?)<\/title>/i)?.[1] || "";
  assert.ok(modelTitle.length > 0 && modelTitle.length <= 60, model.id + ": generated model title should be concise");
  const modelH1 = modelPage.match(/<h1>(.*?)<\/h1>/i)?.[1] || "";
  assert.equal(modelH1, modelTitle.replace(" | VoltRide", ""), model.id + ": H1 should match the generated title");
  assert.doesNotMatch(modelPage, /تقدير VoltRide للمغرب|الصحافة المغربية|هل يمكنني استعماله في طرق المغرب قانونياً|content="ar_MA"/, model.id + ": generated model page must not present Moroccan law as global");
  assert.match(modelPage, /سرعة مرجعية لا تتجاوز 25 كم\/س/, model.id + ": range benchmark must be explained as non-legal");
  assert.match(modelPage, /هل يمكنني استخدامه قانونياً على الطرق العامة/, model.id + ": legal FAQ must be jurisdiction-neutral");
  assert.match(modelPage, /الدليل القانوني الخاص بالمغرب/, model.id + ": Morocco-specific legal guidance must be clearly labelled");
  assert.ok(sitemap.includes("<loc>https://voltride-4qj.pages.dev/" + model.id + "</loc><lastmod>2026-11-10</lastmod>"), model.id + ": updated model page must have a current sitemap lastmod");

}


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
