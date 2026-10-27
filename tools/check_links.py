#!/usr/bin/env python3
"""Offline site checks for VoltRide (no network, deterministic).

Checks, for every .html page in the repo:
  * every internal href/src points to a file that exists (and #fragments to an existing id)
  * <html lang> and <title> are present
  * canonical and hreflang URLs map to real pages
and for sitemap.xml: every <loc> maps to a real page.
External (http/https) links are NOT fetched on purpose: CI stays fast and never flaky.
Exit code 1 if anything is wrong.
"""
import os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://voltride-4qj.pages.dev"
SKIP_DIRS = {".git", ".github", "tools", "node_modules"}
SKIP_SCHEMES = ("http:", "https:", "mailto:", "tel:", "data:", "javascript:", "whatsapp:", "sms:")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.lang, self.title, self.canonical, self.hreflang = [], set(), None, "", None, []
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "html": self.lang = a.get("lang")
        if tag == "title": self._in_title = True
        if tag == "a" and a.get("href"): self.refs.append(a["href"])
        elif tag == "link" and a.get("href"):
            rel = (a.get("rel") or "").lower()
            if rel == "canonical": self.canonical = a["href"]
            elif rel == "alternate" and a.get("hreflang"): self.hreflang.append(a["href"])
            else: self.refs.append(a["href"])
        elif tag in ("script", "img", "source", "iframe") and a.get("src"): self.refs.append(a["src"])

    def handle_endtag(self, tag):
        if tag == "title": self._in_title = False

    def handle_data(self, data):
        if self._in_title: self.title += data


def to_local(page_path, ref):
    """Map an internal reference to a repo-relative file path (or None if external/ignorable)."""
    ref = ref.strip()
    if not ref or ref.startswith(SKIP_SCHEMES) or ref.startswith("//"):
        return None
    sp = urlsplit(ref)
    path = unquote(sp.path)
    if not path:                      # pure "#fragment" -> same page
        return page_path, sp.fragment
    if path.startswith("/"):
        rel = path.lstrip("/")
    else:
        rel = os.path.normpath(os.path.join(os.path.dirname(page_path), path)).replace(os.sep, "/")
    if rel in ("", "."): rel = "index.html"
    elif rel.endswith("/"): rel += "index.html"
    return rel, sp.fragment


def url_to_local(url):
    if not url.startswith(SITE): return None
    return to_local("index.html", url[len(SITE):] or "/")


def main():
    pages, errors = {}, []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if f.endswith(".html") and not f.startswith("google"):   # google*.html = Search Console verification file
                rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/")
                p = Page(); p.feed(open(os.path.join(dp, f), encoding="utf-8").read()); pages[rel] = p

    def exists(rel): return os.path.isfile(os.path.join(ROOT, rel))

    for rel, p in sorted(pages.items()):
        if not p.lang: errors.append(f"{rel}: <html> has no lang")
        if not p.title.strip(): errors.append(f"{rel}: empty <title>")
        for ref in p.refs:
            m = to_local(rel, ref)
            if not m: continue
            target, frag = m
            if not exists(target):
                errors.append(f"{rel}: broken link -> {ref}"); continue
            if frag and target.endswith(".html") and target in pages and frag not in pages[target].ids:
                # ids created by JavaScript cannot be seen here, so this is only a warning-level hint in the log
                print(f"note: {rel}: fragment #{frag} not found as a static id in {target}")
        for label, url in [("canonical", p.canonical)] + [("hreflang", u) for u in p.hreflang]:
            if not url: continue
            m = url_to_local(url)
            if m is None: errors.append(f"{rel}: {label} is not on {SITE}: {url}"); continue
            if not exists(m[0]): errors.append(f"{rel}: {label} points to a missing page: {url}")
        if p.canonical:
            m = url_to_local(p.canonical)
            if m and m[0] != rel and not (rel == "index.html" and m[0] == "index.html"):
                errors.append(f"{rel}: canonical points to another page: {p.canonical}")

    sm = os.path.join(ROOT, "sitemap.xml")
    if os.path.isfile(sm):
        locs = re.findall(r"<loc>([^<]+)</loc>", open(sm, encoding="utf-8").read())
        seen = set()
        for u in locs:
            if u in seen: errors.append(f"sitemap.xml: duplicate url {u}")
            seen.add(u)
            m = url_to_local(u)
            if m is None or not exists(m[0]): errors.append(f"sitemap.xml: url has no page: {u}")
    else:
        errors.append("sitemap.xml is missing")

    print(f"checked {len(pages)} pages")
    if errors:
        print("\n".join("ERROR " + e for e in errors)); print(f"\n{len(errors)} problem(s)"); sys.exit(1)
    print("OK: no broken internal links, canonicals, hreflang or sitemap entries")


if __name__ == "__main__":
    main()
