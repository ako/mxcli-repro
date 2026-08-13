#!/usr/bin/env python3
"""Open the grid page in a real browser and report what the client sees.

The third retrieval path in this reproduction: a data grid column bound to
`OrderView_SalesOrder/OrderNumber`, i.e. the client retrieving over the
association that the un-aliased ID column created. Prints console errors, failed
network responses, any Mendix error dialog, and the grid's rendered rows.

Usage: python3 repro/06-browse-page.py [url]
"""

import sys

from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8180/"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    page = browser.new_page()

    console, failures = [], []
    page.on("console", lambda m: console.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: console.append(f"[pageerror] {e}"))
    page.on(
        "response",
        lambda r: failures.append(f"{r.status} {r.url}") if r.status >= 400 else None,
    )

    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(4000)

    print("=== console errors/warnings ===")
    print("\n".join(console) or "(none)")

    print("\n=== HTTP >= 400 ===")
    print("\n".join(failures) or "(none)")

    print("\n=== visible text ===")
    body = page.inner_text("body")
    print(body[:2000] or "(empty)")

    page.screenshot(path="/tmp/claude-0/-home-user-mxcli-repro/f197c8e3-a078-59d8-8a57-d4f4e061119d/scratchpad/page.png", full_page=True)
    print("\nscreenshot: scratchpad/page.png")
    browser.close()
