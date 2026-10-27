// Accessibility check with axe-core (WCAG 2.1 A/AA) on every page of sitemap.xml.
// Usage: node tools/a11y.mjs [baseUrl]   (default http://localhost:8080)
// BLOCKING rules fail the job; everything else is reported as a warning (so existing
// issues such as colour contrast don't keep the check permanently red).
import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';

const base = process.argv[2] || 'http://localhost:8080';
const SITE = 'https://voltride-4qj.pages.dev';
const BLOCKING = new Set([
  'label', 'select-name', 'button-name', 'link-name', 'image-alt', 'input-image-alt',
  'html-has-lang', 'html-lang-valid', 'valid-lang', 'document-title', 'meta-viewport',
  'aria-valid-attr', 'aria-valid-attr-value', 'aria-required-attr', 'aria-allowed-attr',
  'aria-roles', 'duplicate-id-aria', 'frame-title', 'bypass',
]);

const sitemap = fs.readFileSync('sitemap.xml', 'utf8');
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].replace(SITE, ''));
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 800 } });
let blocking = 0, warnings = 0;
const summary = ['## Accessibility (axe-core, WCAG 2.1 A/AA)', ''];

for (const path of urls) {
  const page = await ctx.newPage();
  try {
    const res = await page.goto(base + (path || '/'), { waitUntil: 'load' });
    if (!res || !res.ok()) { console.log(`ERROR ${path}: HTTP ${res && res.status()}`); blocking++; continue; }
    await page.waitForTimeout(300);
    const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze();
    for (const v of violations) {
      const isBlocking = BLOCKING.has(v.id) || v.impact === 'critical';
      const line = `${isBlocking ? 'ERROR' : 'warn '} ${path || '/'}: ${v.id} (${v.impact}) x${v.nodes.length} - ${v.help}`;
      console.log(line);
      if (isBlocking) { blocking++; summary.push(`- ❌ \`${path || '/'}\` **${v.id}** (${v.impact}) ×${v.nodes.length}: ${v.help}`);
        for (const n of v.nodes.slice(0, 3)) summary.push(`  - \`${n.target.join(' ')}\``); }
      else { warnings++; summary.push(`- ⚠️ \`${path || '/'}\` ${v.id} (${v.impact}) ×${v.nodes.length}`); }
    }
  } catch (e) { console.log(`ERROR ${path}: ${e.message}`); blocking++; }
  await page.close();
}
await browser.close();
summary.push('', `**${urls.length} pages checked: ${blocking} blocking, ${warnings} warnings.**`);
if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, summary.join('\n') + '\n');
console.log(`\n${urls.length} pages: ${blocking} blocking, ${warnings} warnings`);
process.exit(blocking ? 1 : 0);
