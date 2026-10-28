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
const warnGroups = new Map();
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
      else {
        warnings++;
        for (const n of v.nodes) {            // group identical findings across pages: rule + element
          const key = v.id + ' | ' + n.target.join(' ');
          const d = (n.any && n.any[0] && n.any[0].data) || {};
          const g = warnGroups.get(key) || { rule: v.id, target: n.target.join(' '), pages: [], data: d, html: (n.html || '').slice(0, 140) };
          g.pages.push(path || '/'); warnGroups.set(key, g);
        }
      }
    }
  } catch (e) { console.log(`ERROR ${path}: ${e.message}`); blocking++; }
  await page.close();
}
await browser.close();
summary.push('', '### Warnings grouped by element (same element on several pages = one fix)', '');
for (const g of [...warnGroups.values()].sort((x, y) => y.pages.length - x.pages.length)) {
  const c = g.data && g.data.contrastRatio ? ` — ${g.data.fgColor} on ${g.data.bgColor}, ratio ${g.data.contrastRatio} (needs ${g.data.expectedContrastRatio})` : '';
  summary.push(`- **${g.rule}** \`${g.target}\` on ${g.pages.length} page(s)${c}`);
  summary.push(`  - e.g. ${g.pages.slice(0, 3).join(', ')}  \n  - \`${g.html.replace(/`/g, "'")}\``);
}
summary.push('', `**${urls.length} pages checked: ${blocking} blocking, ${warnings} warnings.**`);
if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, summary.join('\n') + '\n');
fs.writeFileSync('a11y-report.md', summary.join('\n') + '\n');
console.log(`\n${urls.length} pages: ${blocking} blocking, ${warnings} warnings`);
if (process.env.GITHUB_ACTIONS) console.log(`::notice title=axe result::${base} - ${urls.length} pages: ${blocking} blocking, ${warnings} warnings`);
process.exit(blocking ? 1 : 0);
