import requests
import json
import re
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 対象のスプレッドシートID（公開設定されている必要あり）
SHEET_ID = "14R9px2COU6-9UIgib2xY7ICh5sI-FDzcfC14iQXFj3U"

def fetch_column_headers():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"
        response = requests.get(url)
        response.raise_for_status()

        json_text = re.search(r"setResponse\((.*)\);", response.text, re.DOTALL).group(1)
        data = json.loads(json_text)

        columns = data["table"]["cols"]
        headers = [col.get("label", "") for col in columns]

        logger.info("取得したカラム名:")
        for idx, header in enumerate(headers):
            print(f"{idx}: {header}")

    except Exception as e:
        logger.error(f"カラム取得中にエラーが発生しました: {e}")

if __name__ == "__main__":
    fetch_column_headers()
