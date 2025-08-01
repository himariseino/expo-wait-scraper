import requests
import json
import re
from datetime import datetime
import csv
import os
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

SHEET_ID = "14R9px2COU6-9UIgib2xY7ICh5sI-FDzcfC14iQXFj3U"
CSV_FILE = "wait_times.csv"

def clean_text(text: str) -> str:
    return str(text).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()

def fetch_wait_times_from_sheet():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"
        response = requests.get(url)
        response.raise_for_status()

        # JSONP から中身を取り出す
        json_text = re.search(r"setResponse\((.*)\);", response.text, re.DOTALL).group(1)
        data = json.loads(json_text)

        rows = data["table"]["rows"]
        extracted_rows = []

        for row in rows:
            cells = [cell.get("v", "") if cell else "" for cell in row["c"]]
            if len(cells) >= 3:
                now = datetime.now().isoformat()
                name = clean_text(cells[0])
                wait_time = clean_text(cells[1])
                post_time = clean_text(cells[3]) if len(cells) > 3 else ""
                extracted_rows.append([now, name, wait_time, post_time])

        if extracted_rows:
            logger.info(f"{len(extracted_rows)} 件の待ち時間データを取得しました。")

            dir_name = os.path.dirname(CSV_FILE)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerows(extracted_rows)
        else:
            logger.warning("取得できたデータが空です。シートが空か構造が変わった可能性があります。")

    except Exception as e:
        logger.error(f"データ取得中にエラーが発生しました: {e}")

if __name__ == "__main__":
    fetch_wait_times_from_sheet()
