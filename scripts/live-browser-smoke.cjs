const { chromium } = require('playwright');
const base = (process.env.SITE_URL || 'https://voltride-4qj.pages.dev').replace(/\/$/, '');
const paths = ['/', '/blog', '/about', '/contact', '/ride-match', '/article-7', '/en/article-7', '/fr/article-7', '/privacy'];
(async () => {
  const browser = await chromium.launch({ headless: true });
  const failures = [];
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(20000);
    page.on('pageerror', e => failures.push('JS page error: ' + e.message));
    for (const path of paths) {
      const url = base + path;
      try {
        const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        const status = response ? response.status() : 0;
        const title = await page.title();
        const bodyText = await page.locator('body').innerText({ timeout: 10000 }).catch(() => '');
        console.log(path, 'HTTP', status, 'title:', title.slice(0, 100), 'body chars:', bodyText.length);
        if (status !== 200) failures.push(path + ' returned HTTP ' + status);
        if (!title.trim()) failures.push(path + ' has an empty document title');
        if (bodyText.trim().length < 30) failures.push(path + ' rendered almost no visible text');
      } catch (e) { failures.push(path + ' navigation failed: ' + e.message); }
    }
  } finally { await browser.close(); }
  if (failures.length) { console.error('BROWSER AUDIT FAIL'); failures.forEach(x => console.error('-', x)); process.exit(1); }
  console.log('BROWSER AUDIT PASS');
})().catch(e => { console.error(e); process.exit(1); });
