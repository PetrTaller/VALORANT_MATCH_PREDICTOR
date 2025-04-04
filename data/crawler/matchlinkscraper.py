import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

CSV_FILE = "matches.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_match_links(base_url):
    match_links = set()
    page = 1

    try:
        while True:
            url = f"{base_url}/?page={page}"
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}, stopping.")
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            matches = soup.select("a.match-item[href^='/']")  # Correct selector

            if not matches:
                print(f"No matches found on page {page}, stopping.")
                break

            for match in matches:
                link = "https://www.vlr.gg" + match["href"]
                if link.count("/") == 4:  # Ensuring the format is "https://www.vlr.gg/xxxxxx/"
                    match_links.add(link)

            print(f"Scraped Page {page}: {len(match_links)} total links found.")
            page += 1
            time.sleep(2)  # Avoid rate-limiting

    except KeyboardInterrupt:
        print("\n[!] Keyboard Interrupt detected. Saving links...")
        save_links(match_links, CSV_FILE)

    return match_links

def save_links(links, filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            existing_links = set(pd.read_csv(filename, header=None)[0].tolist())
        except pd.errors.EmptyDataError:
            existing_links = set()
    else:
        existing_links = set()

    new_links = links - existing_links  # Remove duplicates
    if new_links:
        df = pd.DataFrame(new_links)
        df.to_csv(filename, mode='a', header=False, index=False)
        print(f"\n[✔] Saved {len(new_links)} new links to {filename}")
    else:
        print("\n[!] No new links to save.")

def main():
    base_url = "https://www.vlr.gg/matches/results"
    get_match_links(base_url)

if __name__ == "__main__":
    main()
