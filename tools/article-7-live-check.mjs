import { chromium } from 'playwright';

const base = process.argv[2] || 'https://voltride-4qj.pages.dev';
const expected = [
  { path: '/article-7', date: '13 نوفمبر 2026', lang: 'ar' },
  { path: '/en/article-7', date: 'November 13, 2026', lang: 'en' },
  { path: '/fr/article-7', date: '13 novembre 2026', lang: 'fr' },
];
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const failures = [];
try {
  for (const item of expected) {
    const response = await page.goto(base + item.path, { waitUntil: 'domcontentloaded' });
    if (!response || response.status() !== 200) {
      failures.push(`${item.path}: HTTP ${response?.status() ?? 'no response'}`);
      continue;
    }
    const result = await page.evaluate(() => ({
      lang: document.documentElement.lang,
      visibleDate: document.querySelector('article .meta')?.innerText || '',
      modifiedMeta: document.querySelector('meta[property="article:modified_time"]')?.content || '',
      jsonLdDates: [...document.querySelectorAll('script[type="application/ld+json"]')].flatMap(s => {
        try { const data = JSON.parse(s.textContent); return data.dateModified ? [data.dateModified] : []; }
        catch { return []; }
      })
    }));
    if (result.lang !== item.lang) failures.push(`${item.path}: lang expected ${item.lang}, got ${result.lang}`);
    if (!result.visibleDate.includes(item.date)) failures.push(`${item.path}: visible date missing "${item.date}"; got "${result.visibleDate}"`);
    if (result.modifiedMeta !== '2026-11-13') failures.push(`${item.path}: article:modified_time is ${result.modifiedMeta}`);
    if (!result.jsonLdDates.includes('2026-11-13')) failures.push(`${item.path}: JSON-LD dateModified is not 2026-11-13`);
    console.log(`${failures.length ? 'CHECK' : 'PASS'} ${item.path}: ${JSON.stringify(result)}`);
  }
  const sitemapResponse = await page.request.get(base + '/sitemap.xml');
  if (!sitemapResponse || sitemapResponse.status() !== 200) failures.push(`/sitemap.xml: HTTP ${sitemapResponse?.status() ?? 'no response'}`);
  else {
    const xml = await sitemapResponse.text();
    for (const item of expected) {
      const loc = base + item.path;
      const entry = `<loc>${loc}</loc><lastmod>2026-11-13</lastmod>`;
      if (!xml.includes(entry)) failures.push(`sitemap: expected ${loc} with lastmod 2026-11-13`);
    }
  }
} finally {
  await browser.close();
}
if (failures.length) {
  console.error('Article 7 live validation failed:\\n- ' + failures.join('\\n- '));
  process.exit(1);
}
console.log('Article 7 live date + sitemap checks passed for AR/EN/FR.');
