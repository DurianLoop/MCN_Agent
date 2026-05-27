#!/usr/bin/env python3
"""Read-only Xiaohongshu research helper via Chrome DevTools Protocol.

Connects to a user-launched Chrome instance, navigates to search/profile URLs,
extracts visible text/links, and saves screenshots. It does not click like,
comment, follow, message, or publish.
"""

from __future__ import annotations

import argparse
import base64
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import websocket


def get_page_ws(endpoint: str) -> str:
    pages = json.loads(urllib.request.urlopen(f"{endpoint}/json/list", timeout=5).read().decode("utf-8"))
    page = next((item for item in pages if item.get("type") == "page"), pages[0])
    return page["webSocketDebuggerUrl"]


class CDP:
    def __init__(self, ws_url: str):
        self.ws = websocket.create_connection(ws_url, timeout=10, suppress_origin=True)
        self.next_id = 1

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        msg_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
        while True:
            payload = json.loads(self.ws.recv())
            if payload.get("id") == msg_id:
                if "error" in payload:
                    raise RuntimeError(f"{method}: {payload['error']}")
                return payload.get("result", {})

    def navigate(self, url: str, wait: float = 6.0) -> None:
        self.call("Page.enable")
        self.call("Runtime.enable")
        self.call("Page.navigate", {"url": url})
        time.sleep(wait)

    def eval(self, expression: str) -> Any:
        result = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
                "timeout": 5000,
            },
        )
        return result.get("result", {}).get("value")

    def screenshot(self, path: Path) -> None:
        data = self.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})["data"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(base64.b64decode(data))

    def close(self) -> None:
        self.ws.close()


EXTRACT_JS = r"""
(() => {
  const links = Array.from(document.querySelectorAll('a[href]')).slice(0, 120).map(a => ({
    text: (a.innerText || a.textContent || '').trim().slice(0, 120),
    href: a.href
  }));
  const cards = Array.from(document.querySelectorAll('section, article, [class*="note"], [class*="card"], [class*="feed"]'))
    .map(el => (el.innerText || el.textContent || '').trim())
    .filter(Boolean)
    .slice(0, 80);
  return {
    url: location.href,
    title: document.title,
    bodyText: document.body.innerText.slice(0, 8000),
    links,
    cards
  };
})()
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://127.0.0.1:9222")
    parser.add_argument("--query")
    parser.add_argument("--url")
    parser.add_argument("--out", type=Path, default=Path("references/xhs_live_capture.json"))
    parser.add_argument("--screenshot", type=Path, default=Path("references/screenshots/xhs_capture.png"))
    parser.add_argument("--wait", type=float, default=7.0)
    parser.add_argument("--scrolls", type=int, default=2)
    args = parser.parse_args()

    url = args.url
    if args.query:
        url = "https://www.xiaohongshu.com/search_result?keyword=" + urllib.parse.quote(args.query)
    if not url:
        raise SystemExit("Pass --query or --url")

    cdp = CDP(get_page_ws(args.endpoint))
    try:
        cdp.navigate(url, wait=args.wait)
        for _ in range(args.scrolls):
            cdp.eval("window.scrollBy(0, Math.round(window.innerHeight * 0.8)); true")
            time.sleep(1.5)
        data = cdp.eval(EXTRACT_JS)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        cdp.screenshot(args.screenshot)
        print(json.dumps({"out": str(args.out), "screenshot": str(args.screenshot), "title": data.get("title"), "url": data.get("url")}, ensure_ascii=True, indent=2))
    finally:
        cdp.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
