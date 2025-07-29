# Expo 2025 Pavilion Wait Time Scraper

パビリオンの待ち時間を1時間ごとに取得し、CSVに保存します。

## 実行方法

```bash
uv venv
uv pip sync
python scrape_wait_times.py
```

## 依存ライブラリ
- requests
- beautifulsoup4

以下に、これまでの内容を **エンジニア向けの詳細な技術指示書** としてまとめました。
プロジェクトの概要からファイル構成、開発環境、GitHub Actions による定期実行まで、すべて網羅しています。

---

# 📄 Expo 2025 パビリオン待ち時間 スクレイピングシステム仕様書

## ✅ 概要

Expo 2025 大阪・関西万博の「パビリオン待ち時間」情報を、Web上から1時間ごとに自動取得し、CSVファイルに追記して保存するシステムです。GitHub Actions を利用して定期実行され、取得したCSVはGitHub上でバージョン管理されます。

---

## 🏗️ 技術スタック・構成方針

| 項目      | 内容                                                                      |
| ------- | ----------------------------------------------------------------------- |
| 言語      | Python 3.11以上                                                           |
| パッケージ管理 | [`uv`](https://astral.sh/blog/uv-python-package-manager/)（Poetry風の高速代替） |
| 仮想環境    | `uv venv` によるローカル環境構築                                                   |
| ソース管理   | Git + GitHub                                                            |
| 定期実行    | GitHub Actions（無料枠 2000分/月）                                             |
| データ保存   | CSVファイル（リポジトリ直下でGitにコミット）                                               |

---

## 📁 ディレクトリ構成

```
expo-wait-scraper/
├── scrape_wait_times.py        # スクレイピング本体
├── wait_times.csv              # 出力ファイル（毎回追記）
├── pyproject.toml              # Python依存定義（uv用）
├── uv.lock                     # lockファイル（自動生成）
├── .github/
│   └── workflows/
│       └── scrape.yml          # GitHub Actions 設定
├── .gitignore
└── README.md
```

---

## 🧑‍💻 スクレイピングスクリプト（`scrape_wait_times.py`）

```python
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv

URL = "https://expo2025.fun/%E3%83%91%E3%83%93%E3%83%AA%E3%82%AA%E3%83%B3%E5%BE%85%E3%81%A1%E6%99%82%E9%96%93/"
CSV_FILE = "wait_times.csv"

def scrape_wait_times():
    response = requests.get(URL)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []
    for row in soup.select("div.table-responsive tbody tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            name = cols[0].text.strip()
            wait_time = cols[1].text.strip()
            now = datetime.now().isoformat()
            rows.append([now, name, wait_time])

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

if __name__ == "__main__":
    scrape_wait_times()
```

---

## ⚙️ `pyproject.toml`

```toml
[project]
name = "expo-wait-scraper"
version = "0.1.0"
description = "Scrapes Expo 2025 pavilion wait times"
requires-python = ">=3.10"

dependencies = [
    "requests",
    "beautifulsoup4"
]
```

---

## 📌 `.gitignore`

```gitignore
__pycache__/
*.pyc
.venv/
```

※ `wait_times.csv` はGitHubで管理するため除外しない

---

## ⏰ GitHub Actions の設定（`.github/workflows/scrape.yml`）

```yaml
name: Scrape Wait Times

on:
  schedule:
    - cron: '0 * * * *'  # 毎時00分（UTC）
  workflow_dispatch:     # 手動実行も可能

jobs:
  run-scraper:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests beautifulsoup4

      - name: Run scraper
        run: python scrape_wait_times.py

      - name: Commit and push CSV
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add wait_times.csv
          git commit -m "Update wait_times.csv ($(date -u))" || echo "No changes to commit"
          git push
```

---

## 🚀 初回セットアップ手順（エンジニア向け）

### 1. uv のインストール（まだなら）

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
```

### 2. 仮想環境作成と依存インストール

```bash
uv venv
source .venv/bin/activate
uv pip install requests beautifulsoup4
```

### 3. GitHub リポジトリ作成と push

```bash
git init
gh auth login                      # GitHub CLIが必要
gh repo create expo-wait-scraper --public --source=. --push
```

---

## 📦 GitHub Actions 実行後の成果物

* `wait_times.csv` が1時間ごとに追記され、GitHubに自動コミット・プッシュされます
* 手動での実行テストも「Actions」タブ → `Run workflow` から可能です

---

## 🧩 拡張の余地（必要に応じて）

* 月単位でファイルを分割：`wait_times_YYYY-MM.csv`
* Google Drive や S3 にバックアップ
* GitHub Pages や Superset などでの可視化
* HTML構造変更への耐性強化（パビリオン名や構造に応じた対応）

---

必要があれば、この内容を **Markdownファイル（READMEや開発用ドキュメント）として出力**することも可能です。ご希望があればお知らせください。
