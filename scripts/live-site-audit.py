#!/usr/bin/env python3
"""Read-only live HTTP, sitemap, canonical and security-header audit."""
import os, sys, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from urllib.parse import urlparse

BASE = os.environ.get("SITE_URL", "https://voltride-4qj.pages.dev").rstrip("/")
TIMEOUT = 25
class Meta(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonicals=[]; self.title=False; self.title_text=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag.lower()=="link" and a.get("rel","").lower()=="canonical" and a.get("href"): self.canonicals.append(a["href"])
        if tag.lower()=="title": self.title=True
    def handle_endtag(self, tag):
        if tag.lower()=="title": self.title=False
    def handle_data(self, data):
        if self.title: self.title_text.append(data)

def request(url):
    req=urllib.request.Request(url, headers={"User-Agent":"VoltRide-Live-Audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body=r.read(2_000_000)
            return {"url":url,"status":r.status,"final":r.geturl(),"headers":{k.lower():v for k,v in r.headers.items()},"body":body,"error":None}
    except urllib.error.HTTPError as e:
        return {"url":url,"status":e.code,"final":e.geturl(),"headers":{k.lower():v for k,v in e.headers.items()},"body":b"","error":str(e)}
    except Exception as e:
        return {"url":url,"status":0,"final":url,"headers":{},"body":b"","error":str(e)}

def main():
    print("VoltRide live audit:", BASE)
    root=request(BASE+"/sitemap.xml")
    if root["status"] != 200: print("FAIL sitemap.xml",root["status"],root["error"]); return 1
    try: xml=ET.fromstring(root["body"])
    except Exception as e: print("FAIL sitemap XML:",e); return 1
    locs=[loc.text.strip() for entry in xml if entry.tag.endswith("}url") for loc in entry if loc.tag.endswith("}loc") and loc.text]
    if not locs: print("FAIL sitemap has no URLs"); return 1
    host=urlparse(BASE).netloc
    external=[u for u in locs if urlparse(u).netloc != host]
    if external: print("FAIL external sitemap URLs:",external[:5])
    print("Sitemap URLs:",len(locs),"unique:",len(set(locs)))
    duplicates=[(u,n) for u,n in Counter(locs).items() if n>1]
    if duplicates:
        print("FAIL duplicate sitemap URLs:")
        for url,count in duplicates: print("DUPLICATE",count,"x",url)
    results=[]
    with ThreadPoolExecutor(max_workers=12) as pool:
        fs=[pool.submit(request,u) for u in locs]
        for f in as_completed(fs): results.append(f.result())
    results.sort(key=lambda x:x["url"])
    bad=[x for x in results if x["status"] != 200]
    for x in bad: print("PAGE FAIL",x["status"],x["url"],x["error"] or "")
    html_pages=0; canonical_missing=[]; canonical_offhost=[]
    for x in results:
        if x["status"] != 200: continue
        ct=x["headers"].get("content-type","")
        if "html" not in ct and not x["body"].lstrip().lower().startswith((b"<!doctype html",b"<html")): continue
        html_pages+=1; p=Meta()
        try: p.feed(x["body"].decode("utf-8","replace"))
        except Exception: pass
        if not p.canonicals: canonical_missing.append(x["url"])
        for c in p.canonicals:
            if urlparse(c).netloc and urlparse(c).netloc != host: canonical_offhost.append((x["url"],c))
    home=request(BASE+"/")
    required=["x-content-type-options","referrer-policy","content-security-policy"]
    missing=[h for h in required if h not in home["headers"]]
    print("HTML pages inspected:",html_pages)
    print("Canonical missing:",len(canonical_missing))
    if canonical_missing: print("Canonical missing sample:",canonical_missing[:10])
    print("Canonical off-host:",len(canonical_offhost))
    sec=["strict-transport-security","x-content-type-options","x-frame-options","referrer-policy","content-security-policy","permissions-policy"]
    print("Homepage security headers:",", ".join(h+("=present" if h in home["headers"] else "=MISSING") for h in sec))
    print("robots.txt:",request(BASE+"/robots.txt")["status"],"sitemap.xml:",root["status"])
    failures=[]
    if bad: failures.append(f"{len(bad)} sitemap URLs did not return HTTP 200")
    if external: failures.append("sitemap contains off-host URLs")
    if len(set(locs)) != len(locs): failures.append("duplicate sitemap URLs")
    if missing: failures.append("missing baseline security headers: "+", ".join(missing))
    if canonical_offhost: failures.append("canonical URLs point off-host")
    # Missing canonicals are reported for review, not hard-failed: some routes may intentionally omit them.
    if home["status"] != 200: failures.append("homepage did not return HTTP 200")
    if failures:
        print("AUDIT RESULT: FAIL"); [print("-",x) for x in failures]; return 1
    print("AUDIT RESULT: PASS (canonical omissions are informational)")
    return 0
if __name__=="__main__": sys.exit(main())
