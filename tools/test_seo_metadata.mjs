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


const hreflangClusters = [
  ["article-choosing-charger.html", "fr/comment-choisir-chargeur-trottinette.html", "en/blog/choosing-charger.html"],
  ["blog/charger-safety.html", "fr/blog/securite-chargeur-trottinette.html", "en/blog/charger-safety.html"]
];
const siteUrlFor = path => "https://voltride-4qj.pages.dev/" + path.replace(/\.html$/, "");
for (const cluster of hreflangClusters) {
  const expected = new Map([["ar", siteUrlFor(cluster[0])], ["fr", siteUrlFor(cluster[1])], ["en", siteUrlFor(cluster[2])]]);
  for (const path of cluster) {
    const html = readFileSync(path, "utf8");
    const alternates = [...html.matchAll(/<link\s+rel="alternate"\s+hreflang="(ar|fr|en)"\s+href="([^"]+)"/g)];
    const actual = new Map(alternates.map(match => [match[1], match[2]]));
    for (const [language, url] of expected) assert.equal(actual.get(language), url, path + ": reciprocal hreflang " + language);
    assert.equal(actual.size, 3, path + ": exactly three language alternates are required");
    assert.match(html, /hreflang="x-default"/, path + ": x-default is required");
  }
}
for (const path of ["article-choosing-charger.html", "fr/comment-choisir-chargeur-trottinette.html", "en/blog/choosing-charger.html"]) {
  const html = readFileSync(path, "utf8");
  assert.doesNotMatch(html, /For 42V batteries:.*48V DC|للبطاريات 42V:.*48V DC|Shachi 48V/i, path + ": incorrect charger voltage advice");
  assert.doesNotMatch(html, /s\.click\.aliexpress\.com/, path + ": unverified charger CTA must not be promoted");
}


const arabicRangeTips = readFileSync("article-1.html", "utf8");
const englishRangeTips = readFileSync("en/article-1.html", "utf8");
assert.doesNotMatch(arabicRangeTips, /السرعة القصوى المسموحة في المغرب 25 كم/س/, "avoid unsupported blanket Moroccan speed-limit claim");
assert.doesNotMatch(englishRangeTips, /maximum legal speed in Morocco is 25 km\/h/i, "avoid unsupported blanket English speed-limit claim");

const arabicCodes = readFileSync("article-3.html", "utf8");
const englishCodes = readFileSync("en/article-3.html", "utf8");
assert.match(englishCodes, /E14 \(Example\): Throttle Signal Issue/, "E14 label must match throttle description");
assert.doesNotMatch(englishCodes, /E14 \(Example\): Accelerometer Signal Issue/, "do not mislabel throttle as accelerometer");
assert.match(arabicCodes, /استعمل الشاحن الأصلي أو المعتمد/, "Arabic error guide must use correct charger spelling");
for (const html of [arabicCodes, englishCodes]) {
  assert.match(html, /If smoke or fire appears|إذا ظهر دخان أو اشتعال/, "battery incident advice must direct people away and to emergency services");
  assert.doesNotMatch(html, /move the scooter away from flammable items/, "do not advise moving a potentially failing battery");
}

const arabicAccessories = readFileSync("article-6.html", "utf8");
const englishAccessories = readFileSync("en/article-6.html", "utf8");
assert.doesNotMatch(arabicAccessories, /شعار معيار السلامة على الخوذة، مثل CE/, "CE alone must not be presented as a helmet safety standard");
assert.match(arabicAccessories, /EN 1078/, "Arabic helmet advice should name a relevant example standard");
assert.doesNotMatch(arabicAccessories, /إلزامي لسائق التروتينيت/, "avoid unsupported legal obligation claim in accessory article");
assert.doesNotMatch(englishAccessories, /mandatory according to law reports/i, "avoid unsupported legal obligation claim in English accessory article");

for (const path of ["article-1.html", "en/article-1.html", "article-3.html", "en/article-3.html", "article-6.html", "en/article-6.html", "guides/not-charging.html", "guides/error-codes.html"]) {
  const html = readFileSync(path, "utf8");
  assert.match(html, /2026-11-12/, path + ": modified date should be current");
  const slug = path.replace(/\.html$/, "");
  assert.ok(sitemap.includes("<loc>https://voltride-4qj.pages.dev/" + slug + "</loc><lastmod>2026-11-12</lastmod>"), path + ": sitemap lastmod should match");
}


const winterGuideAr = readFileSync("article-9.html", "utf8");
const winterGuideEn = readFileSync("en/article-9.html", "utf8");
assert.match(winterGuideAr, /لا تشحن أثناء النوم أو عند مغادرة المنزل/, "Arabic winter charging advice must require supervision");
assert.match(winterGuideEn, /never charge while asleep or away from home/i, "English winter charging advice must require supervision");
assert.match(winterGuideAr, /نطاق الحرارة المحدد في الدليل/, "Arabic cold-weather charging must defer to manufacturer temperature limits");
assert.match(winterGuideEn, /temperature range in its manual/i, "English cold-weather charging must defer to manufacturer temperature limits");

const accessoryGuideAr = readFileSync("article-10.html", "utf8");
const accessoryGuideEn = readFileSync("en/article-10.html", "utf8");
assert.doesNotMatch(accessoryGuideAr, /الخوذة المثبتة إلزامية بحسب المرسوم/, "avoid unsupported helmet mandate assertion in buying guide");
assert.doesNotMatch(accessoryGuideEn, /wearing a.*helmet is mandatory for scooter riders/i, "avoid unsupported English helmet mandate assertion");
assert.match(accessoryGuideAr, /EN 1078 مخصص لخوذات راكبي الدراجات وألواح التزلج والزلاجات ذات العجلات/, "Arabic guide must accurately describe EN 1078 scope");
assert.match(accessoryGuideEn, /EN 1078 is an example for bicycle, skateboard and roller-skate helmets/i, "English guide must accurately describe EN 1078 scope");
assert.match(accessoryGuideAr, /CE وحدها ليست معيار خوذة/, "CE marking must not be presented as a helmet standard");
assert.match(accessoryGuideEn, /CE marking alone is not a helmet safety standard/i, "CE marking must not be presented as a helmet standard");

const chargingCostAr = readFileSync("article-8.html", "utf8");
assert.match(chargingCostAr, /11% إلى 18%/, "charging efficiency conversion should use reciprocal range");
assert.doesNotMatch(chargingCostAr, /تضيف نحو 10–15%/, "avoid inaccurate direct loss percentage for 85-90% efficiency");

for (const path of ["article-8.html", "en/article-8.html", "article-9.html", "en/article-9.html", "article-10.html", "en/article-10.html"]) {
  const html = readFileSync(path, "utf8");
  assert.match(html, /2026-11-12/, path + ": modified date should be current");
  const slug = path.replace(/\.html$/, "");
  assert.ok(sitemap.includes("<loc>https://voltride-4qj.pages.dev/" + slug + "</loc><lastmod>2026-11-12</lastmod>"), path + ": sitemap lastmod should match");
}

assert.doesNotMatch(chargingCostAr, /<li>[^<]*<strong>الإعدادات[\\s\\S]*?<\\/a><\\/p>/, "charging cost list item must have valid list markup");


const winterGuideFr = readFileSync("fr/article-9.html", "utf8");
assert.match(winterGuideFr, /ne rechargez jamais pendant votre sommeil ni lorsque vous quittez votre domicile/i, "French winter charging advice must require supervision");
assert.match(winterGuideFr, /plage de température de charge indiquée dans le manuel/i, "French cold-weather charging must defer to manufacturer temperature limits");

const accessoryGuideFr = readFileSync("fr/article-10.html", "utf8");
assert.doesNotMatch(accessoryGuideFr, /est obligatoire pour le conducteur de trottinette/i, "avoid unsupported French helmet mandate assertion");
assert.match(accessoryGuideFr, /EN 1078 est un exemple pour les casques de cyclistes, de skateboard et de patins à roulettes/i, "French guide must accurately describe EN 1078 scope");
assert.match(accessoryGuideFr, /le marquage CE seul n'est pas une norme de sécurité pour casque/i, "French guide must not present CE marking as a helmet standard");
for (const path of ["fr/article-9.html", "fr/article-10.html"]) {
  const html = readFileSync(path, "utf8");
  assert.match(html, /2026-11-12/, path + ": modified date should be current");
  const slug = path.replace(/\.html$/, "");
  assert.ok(sitemap.includes("<loc>https://voltride-4qj.pages.dev/" + slug + "</loc><lastmod>2026-11-12</lastmod>"), path + ": sitemap lastmod should match");
}

console.log("SEO metadata tests passed: global homepage description and valid French article metadata.");
