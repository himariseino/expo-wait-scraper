import asyncio
from datetime import datetime
import csv
import os
import logging
import re

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

URL = "https://expo2025.fun/%E3%83%91%E3%83%93%E3%83%AA%E3%82%AA%E3%83%B3%E5%BE%85%E3%81%A1%E6%99%82%E9%96%93/"
CSV_FILE = "wait_times.csv"

def clean_text(text: str) -> str:
    text = re.sub(r'[\n\r\t]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

async def scrape_wait_times():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # GitHub Actions では xvfb 必須
            page = await browser.new_page()

            # イベントログ出力
            page.on("console", lambda msg: logger.info(f"[console] {msg.type}: {msg.text}"))
            page.on("requestfailed", lambda req: logger.warning(f"[request failed] {req.method} {req.url}"))
            page.on("pageerror", lambda exc: logger.error(f"[page error] {exc}"))

            await page.set_extra_http_headers({
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/115.0.0.0 Safari/537.36"
                )
            })

            # ページ遷移と描画待ち
            await page.goto(URL, wait_until="networkidle", timeout=60000)

            # HTML を保存（wait_for_selectorの前に）
            html = await page.content()
            with open("debug-dump.html", "w", encoding="utf-8") as f:
                f.write(html)

            # スクリーンショットも撮る（念のため）
            await page.screenshot(path="debug.png", full_page=True)

            # セレクタを待つ
            await page.wait_for_selector("table.table", timeout=30000)


            # HTMLが極端に短い場合
            if len(html) < 50000:
                logger.error(f"HTMLの長さが異常に短いです（{len(html)}文字）。ページの読み込みに失敗した可能性があります。")
                raise RuntimeError("HTML content too short — failed to load page properly.")

            # テーブル抽出
            rows = []
            for row in await page.query_selector_all("table.table tbody tr"):
                cols = await row.query_selector_all("td")
                if len(cols) >= 3:
                    name = clean_text(await cols[0].text_content())
                    wait_time = clean_text(await cols[1].text_content())
                    post = clean_text(await cols[2].text_content())
                    now = datetime.now().isoformat()
                    rows.append([now, name, wait_time, post])

            if rows:
                logger.info(f"{len(rows)} 件のデータを取得しました。")
                dir_name = os.path.dirname(CSV_FILE)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                    writer.writerows(rows)
            else:
                logger.warning("待ち時間データが取得できませんでした。HTML構造が変わった可能性があります。")

            await browser.close()

    except PlaywrightTimeoutError:
        logger.error("ページの読み込みまたは待機セレクタの検出でタイムアウトしました。")
    except Exception as e:
        logger.error(f"スクレイピング中に予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_wait_times())
