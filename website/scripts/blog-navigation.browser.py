"""Exercise a built Pages export with Playwright and a failed RSC transport.

Run against `wrangler pages dev out --ip 127.0.0.1 --port 8797` after
`npm run build`. Requires the Python Playwright package and Chromium.
No deployed site or cloud configuration is changed by this test.
"""

import argparse
import json
import re
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def run(base_url, executable=None):
    results = []
    aborted = []
    document_requests = []

    def record(value):
        results.append(value)
        print(json.dumps(value, ensure_ascii=True), flush=True)

    with sync_playwright() as playwright:
        options = {"headless": True}
        if executable:
            options["executable_path"] = executable
        browser = playwright.chromium.launch(**options)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.set_default_timeout(30000)
        page.on("request", lambda request: document_requests.append(
            (request.frame == page.main_frame, request.url))
                if request.resource_type == "document" else None)

        def fail_rsc_fetch(route):
            if route.request.resource_type == "document":
                route.continue_()
            else:
                aborted.append(urlsplit(route.request.url).path)
                route.abort("failed")

        context.route("**/blog/*.txt*", fail_rsc_fetch)
        context.route("**/blog.txt*", fail_rsc_fetch)

        def open_page(path):
            page.goto(base_url + path, wait_until="domcontentloaded", timeout=60000)
            page.locator("h1").wait_for()
            page.add_style_tag(content="* { animation: none !important; transition: none !important; scroll-behavior: auto !important; }")

        def article_passes(slug):
            page.locator("article").wait_for()
            assert urlsplit(page.url).path == "/blog/" + slug
            assert page.locator("h1").inner_text().strip()
            assert page.locator("article").inner_text().strip()

        def assert_document_navigation(path):
            assert any(is_main_frame and urlsplit(url).path == path
                       for is_main_frame, url in document_requests), document_requests
            assert not any(urlsplit(url).path.endswith(".txt")
                           for _, url in document_requests), document_requests

        def click_article(link, slug):
            document_requests.clear()
            link.click()
            article_passes(slug)
            assert_document_navigation("/blog/" + slug)

        open_page("/blog")
        slugs = sorted({
            link.get_attribute("href").removeprefix("/blog/")
            for link in page.locator('a[href^="/blog/"]').all()
            if re.fullmatch(r"/blog/[a-z0-9-]+", link.get_attribute("href") or "")
        })
        assert slugs, "The exported blog index must contain article links"

        for entry in ["/blog", "/research"]:
            for slug in slugs:
                selector = f'a[href="/blog/{slug}"]'
                try:
                    open_page(entry)
                    count = page.locator(selector).count()
                    assert count, "Article link is missing"
                except Exception as error:
                    record({"case": f"{entry} to {slug} setup", "passed": False,
                            "url": page.url, "error": str(error)[:300]})
                    continue
                for index in range(count):
                    label = f"{entry} to {slug} link {index + 1}"
                    try:
                        open_page(entry)
                        click_article(page.locator(selector).nth(index), slug)
                        record({"case": label, "passed": True})
                    except Exception as error:
                        record({"case": label, "passed": False, "url": page.url, "error": str(error)[:300]})

        for slug in slugs:
            try:
                redirect = context.request.get(base_url + f"/blog/{slug}.txt?ref=shared", max_redirects=0)
                assert redirect.status == 301
                assert urlsplit(redirect.headers["location"]).path == "/blog/" + slug
                open_page(f"/blog/{slug}.txt?ref=shared")
                article_passes(slug)
                assert "ref=shared" in page.url
                record({"case": "shared TXT " + slug, "passed": True, "redirect_status": redirect.status, "location": redirect.headers["location"]})
            except Exception as error:
                record({"case": "shared TXT " + slug, "passed": False, "url": page.url, "error": str(error)[:300]})

        try:
            open_page("/blog/" + slugs[0])
            related = [link.get_attribute("href") for link in page.locator('a[href^="/blog/"]').all()]
            for href in related:
                open_page("/blog/" + slugs[0])
                click_article(page.locator(f'a[href="{href}"]').first, href.removeprefix("/blog/"))
            open_page("/blog/" + slugs[0])
            document_requests.clear()
            page.locator('a[href="/blog"]').filter(has_text="All posts").click()
            page.locator("h1").wait_for()
            assert urlsplit(page.url).path == "/blog"
            assert_document_navigation("/blog")
            open_page("/blog.txt?ref=shared")
            assert urlsplit(page.url).path == "/blog"
            assert page.locator("h1").inner_text().strip()
            record({"case": "related articles and index recovery", "passed": True})
        except Exception as error:
            record({"case": "related articles and index recovery", "passed": False, "url": page.url, "error": str(error)[:300]})

        context.close()
        browser.close()

    return {"article_count": len(slugs), "results": results, "aborted_rsc_fetches": aborted}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url")
    parser.add_argument("--browser-executable")
    parser.add_argument("--report")
    arguments = parser.parse_args()
    result = run(arguments.base_url.rstrip("/"), arguments.browser_executable)
    if arguments.report:
        with open(arguments.report, "x", encoding="ascii") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=True)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    raise SystemExit(0 if all(case["passed"] for case in result["results"]) else 1)
