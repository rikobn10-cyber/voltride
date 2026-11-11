import assert from "node:assert/strict";
import { chromium } from "playwright";

const base = (process.argv[2] || "https://voltride-4qj.pages.dev").replace(/\/$/, "");
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
const page = await context.newPage();
const pageErrors = [];
page.on("pageerror", error => pageErrors.push(error.message));

try {
  // Calculator: verify a real browser interaction produces numeric outputs.
  const home = await page.goto(base + "/", { waitUntil: "domcontentloaded", timeout: 30000 });
  assert.ok(home && home.ok(), "homepage must load successfully");
  // The test context is not a consenting visitor: explicitly decline analytics and keep GA traffic clean.
  const consentBanner = page.locator("#voltConsent");
  if (await consentBanner.count()) await consentBanner.locator("button.no").click();
  await page.locator("#calculateBtn").waitFor({ state: "visible", timeout: 15000 });
  await page.locator("#calculateBtn").click();
  await page.waitForFunction(() => {
    const value = document.querySelector("#rangeOut")?.textContent?.trim() || "";
    return value !== "" && value !== "—" && Number.isFinite(Number.parseFloat(value));
  }, { timeout: 10000 });
  const range = Number.parseFloat((await page.locator("#rangeOut").innerText()).replace(",", "."));
  const energy = Number.parseFloat((await page.locator("#energyOut").innerText()).replace(",", "."));
  assert.ok(range > 0, "calculator must return a positive range estimate");
  assert.ok(energy > 0, "calculator must return positive battery energy");

  // App settings: verify the primary app language selector updates document language and direction.
  await page.locator("#settingsBtn").click();
  await page.locator("#settings").waitFor({ state: "visible", timeout: 5000 });
  await page.locator("#languageSelect").selectOption("en");
  await page.waitForFunction(() => document.documentElement.lang === "en" && document.documentElement.dir === "ltr", { timeout: 5000 });

  // Catalog and comparison: select a verified market variant and compare its documented fields.
  await page.locator('button[data-screen="catalog"]').click();
  await page.locator("#catalog").waitFor({ state: "visible", timeout: 5000 });
  await page.locator("#catalogGrid article.scooter").first().waitFor({ state: "visible", timeout: 10000 });
  const variantSelectId = await page.locator('#catalogGrid select[data-catalog-variant]').evaluateAll(nodes => {
    const select = nodes.find(node => node.options.length > 1);
    return select ? select.id : null;
  });
  assert.ok(variantSelectId, "catalog must expose at least one documented market variant");
  const variantSelect = page.locator("#" + variantSelectId);
  const selectedVariantValue = await variantSelect.locator("option").nth(1).getAttribute("value");
  assert.ok(selectedVariantValue, "catalog variant option must have a stable value");
  await variantSelect.selectOption(selectedVariantValue);
  const scooterCard = variantSelect.locator("xpath=ancestor::article");
  const comparedModel = await scooterCard.locator(".scooter-name").innerText();
  await scooterCard.locator("[data-compare]").click();
  await page.locator("#compareFloatBtn").click();
  await page.locator("#compareModal.show").waitFor({ state: "visible", timeout: 5000 });
  const comparison = await page.locator("#compareBody").innerText();
  assert.ok(comparison.includes(comparedModel), "comparison must include the selected catalog model");
  assert.ok(comparison.includes("Wh"), "comparison must show the selected variant's battery energy");
  await page.locator("#closeCompare").click();

  // Generated model page: verify a representative V2-backed detail page and canonical URL.
  const modelPage = await page.goto(base + "/xiaomi-3-lite", { waitUntil: "domcontentloaded", timeout: 30000 });
  assert.ok(modelPage && modelPage.ok(), "generated model detail page must load successfully");
  assert.ok(await page.locator("h1").count() >= 1, "generated model page must expose a primary heading");
  const canonical = await page.locator('link[rel="canonical"]').getAttribute("href");
  assert.ok(canonical && canonical.includes("/xiaomi-3-lite"), "generated model page must declare its own canonical URL");

  // Ride Match: require an explicit market, complete both quiz steps and inspect recommendations.
  const ride = await page.goto(base + "/ride-match", { waitUntil: "domcontentloaded", timeout: 30000 });
  assert.ok(ride && ride.ok(), "Ride Match must load successfully");
  const market = page.locator("#rideMarket");
  await market.waitFor({ state: "visible", timeout: 15000 });
  await page.waitForFunction(() => {
    const select = document.querySelector("#rideMarket");
    return select && [...select.options].some(option => option.value === "EU");
  }, { timeout: 10000 });
  await market.selectOption("EU");
  await page.locator("#step1").waitFor({ state: "visible", timeout: 5000 });
  await page.locator('#distanceOptions button[data-value="20-40"]').click();
  await page.locator('#preferenceOptions button[data-value="range"]').click();
  await page.locator("#results").waitFor({ state: "visible", timeout: 5000 });

  const cards = page.locator("#recommendations .recommendation");
  const cardCount = await cards.count();
  assert.ok(cardCount >= 1 && cardCount <= 3, "Ride Match must render one to three recommendations");
  const rendered = await page.locator("#recommendations").innerText();
  assert.ok(rendered.includes("EU"), "recommendations must preserve the selected market");
  const buyLinks = page.locator('#recommendations a[data-action="buy"]');
  assert.ok(await buyLinks.count() >= 1, "recommendations must include a purchase/search action");
  const hrefs = await buyLinks.evaluateAll(links => links.map(link => link.href));
  assert.ok(hrefs.every(href => href.startsWith("https://www.aliexpress.com/wholesale?")), "unverified affiliate destinations must fall back to ordinary marketplace search");
  assert.ok(hrefs.every(href => !href.includes("s.click.aliexpress.com")), "unverified short affiliate links must not be rendered");

  // Language control should switch document direction without breaking the results.
  await page.locator("#rideMatchLanguage").selectOption("en");
  await page.waitForFunction(() => document.documentElement.lang === "en" && document.documentElement.dir === "ltr", { timeout: 5000 });
  assert.ok(await cards.count() >= 1, "language switching must preserve rendered recommendations");

  assert.deepEqual(pageErrors, [], "live pages must not throw uncaught browser errors");
  console.log(JSON.stringify({ status: "passed", calculator: { range, energy }, catalog: { comparedModel, selectedVariantValue }, generatedModelPage: { canonical }, rideMatch: { market: "EU", recommendations: cardCount, languageSwitch: "en" }, pageErrors }));
} finally {
  await context.close();
  await browser.close();
}
