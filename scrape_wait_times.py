import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

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

    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

if __name__ == "__main__":
    scrape_wait_times()
