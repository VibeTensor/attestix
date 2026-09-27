"""Audit every page of the static export in out/. Run after `npm run build`:

    python scripts/audit_pages.py [--shots]

Per page: title, description, canonical, h1 count, phone overflow, JS errors,
images without alt, broken internal links, and counts of legacy design
markers. Writes audit/report.json and prints problems. With --shots, also
saves a desktop first-screen screenshot per page and a contact sheet.
"""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT, AUDIT = ROOT / "out", ROOT / "audit"
SHOTS = "--shots" in sys.argv


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_head(self):  # serve /x as /x.html like Cloudflare Pages
        p = urlparse(self.path).path
        if "." not in p.rsplit("/", 1)[-1] and not p.endswith("/"):
            if (OUT / (p.lstrip("/") + ".html")).exists():
                self.path = p + ".html"
        return super().send_head()


def route_exists(path: str) -> bool:
    p = path.split("#")[0].split("?")[0].rstrip("/") or "/index"
    rel = p.lstrip("/")
    return any((OUT / c).exists() for c in (rel, rel + ".html", rel + "/index.html"))


PAGES = sorted(
    "/" + str(f.relative_to(OUT).with_suffix("")).replace("\\", "/")
    for f in OUT.rglob("*.html")
    if "_next" not in f.parts and f.name not in ("404.html", "_not-found.html")
)
PAGES = ["/" if p == "/index" else p.removesuffix("/index") for p in PAGES]

PROBE = """() => {
  const vw = document.documentElement.clientWidth;
  const meta = (n) => (document.querySelector(`meta[name="${n}"]`) || {}).content || null;
  return {
    title: document.title,
    description: meta('description'),
    canonical: (document.querySelector('link[rel=canonical]') || {}).href || null,
    robots: meta('robots'),
    h1: document.querySelectorAll('h1').length,
    imgNoAlt: [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length,
    links: [...new Set([...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')))],
    legacySerif: document.querySelectorAll('.font-serif').length,
    legacyMonoCaps: [...document.querySelectorAll('[class*=font-mono-atx][class*=uppercase]')].length,
    legacyWide: document.querySelectorAll('[class*="max-w-[1320px]"], [class*="max-w-[1400px]"]').length,
    height: document.body.scrollHeight,
  };
}"""


def main():
    AUDIT.mkdir(exist_ok=True)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(OUT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    report = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        desk = browser.new_page(viewport={"width": 1440, "height": 900})
        phone = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        desk.on("pageerror", lambda e: errors.append(str(e)[:160]))
        desk.on("console", lambda m: m.type == "error" and errors.append(m.text[:160]))
        for path in PAGES:
            errors.clear()
            desk.goto(base + path, wait_until="load")
            desk.wait_for_timeout(600)
            r = desk.evaluate(PROBE)
            r["jsErrors"] = list(errors)
            internal = [l for l in r.pop("links") if l.startswith("/") and not l.startswith("//")]
            r["brokenLinks"] = sorted({l for l in internal if not route_exists(l)})
            phone.goto(base + path, wait_until="load")
            phone.wait_for_timeout(300)
            r["phoneWidth"] = phone.evaluate("document.documentElement.scrollWidth")
            if SHOTS:
                (AUDIT / "shots").mkdir(exist_ok=True)
                desk.add_style_tag(content="[role=dialog],[class*=cookie i]{display:none!important}")
                desk.screenshot(path=str(AUDIT / "shots" / (path.strip("/").replace("/", "__") or "home")) + ".png")
            report[path] = r
    (AUDIT / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")

    titles = {}
    for p, r in report.items():
        titles.setdefault(r["title"], []).append(p)
    problems = 0
    for p, r in report.items():
        issues = []
        if r["phoneWidth"] > 390: issues.append(f"phone overflow {r['phoneWidth']}px")
        if r["h1"] != 1: issues.append(f"h1 x{r['h1']}")
        if not r["description"]: issues.append("no description")
        if r["canonical"] and r["canonical"].rstrip("/") != "https://attestix.io" + (p if p != "/" else ""):
            issues.append(f"canonical -> {r['canonical']}")
        if len(titles[r["title"]]) > 1: issues.append(f"duplicate title '{r['title'][:40]}'")
        if r["imgNoAlt"]: issues.append(f"{r['imgNoAlt']} img without alt")
        if r["brokenLinks"]: issues.append(f"broken links {r['brokenLinks'][:4]}")
        if r["jsErrors"]: issues.append(f"JS errors {r['jsErrors'][:2]}")
        legacy = r["legacySerif"] + r["legacyMonoCaps"] + r["legacyWide"]
        if issues or legacy:
            problems += bool(issues)
            print(f"{p:48} legacy={legacy:3} | " + "; ".join(issues))
    print(f"\n{len(report)} pages audited, {problems} with issues")


if __name__ == "__main__":
    main()
