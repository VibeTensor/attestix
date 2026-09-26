"""Post-build check for the static export in out/. Run after `npm run build`:

    python scripts/check_site.py

Asserts EU AI Act fine-calculator math (Art. 99 higher-of; Art. 99(6) SME
lower-of) and per-page <title>/canonical tags. Needs `pip install playwright`
and `playwright install chromium`.
"""
import functools
import http.server
import re
import threading
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

OUT = Path(__file__).resolve().parent.parent / "out"
EUR = "€"


def check_html():
    html = (OUT / "pricing.html").read_text(encoding="utf-8")
    title = re.search(r"<title>([^<]+)</title>", html).group(1)
    assert title == "Pricing | Attestix", title
    assert 'rel="canonical" href="https://attestix.io"' not in html, "homepage canonical leaked"
    cross = (OUT / "cross-post.html").read_text(encoding="utf-8")
    assert re.search(r'name="robots" content="noindex, ?nofollow"', cross), "cross-post not noindex"


def check_calculator(port):
    with sync_playwright() as pw:
        page = pw.chromium.launch().new_page()
        page.goto(f"http://127.0.0.1:{port}/demo/fine-calculator.html")
        def card(name):
            return page.get_by_role("heading", name=name).locator(
                "xpath=ancestor::div[contains(@class,'p-6')][1]"
            )

        tier1, tier2 = card("Tier 1"), card("Tier 2")
        box = page.get_by_label("Worldwide annual turnover in USD")
        box.fill("5400000")  # = EUR 5,000,000 at the page's 1.08 rate
        box.press("Enter")
        # large: higher-of everywhere
        expect(tier1).to_contain_text(f"{EUR}35,000,000")
        expect(tier2).to_contain_text(f"{EUR}15,000,000")
        # small mid-cap, Art. 99(6a): lower-of for tiers 2-3 only
        page.get_by_role("button", name="Small mid-cap").click()
        expect(tier1).to_contain_text(f"{EUR}35,000,000")
        expect(tier2).to_contain_text(f"{EUR}150,000")
        # SME, Art. 99(6): lower-of everywhere
        page.get_by_role("button", name="SME or start-up").click()
        expect(tier1).to_contain_text(f"{EUR}350,000")
        expect(tier2).to_contain_text(f"{EUR}150,000")

        phone = pw.chromium.launch().new_page(viewport={"width": 390, "height": 844})
        phone.goto(f"http://127.0.0.1:{port}/index.html")
        width = phone.evaluate("document.documentElement.scrollWidth")
        assert width <= 390, f"homepage scrolls sideways on phones: {width}px"


if __name__ == "__main__":
    check_html()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(OUT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        check_calculator(server.server_address[1])
    finally:
        server.shutdown()
    print("OK: fine calculator + page metadata")
