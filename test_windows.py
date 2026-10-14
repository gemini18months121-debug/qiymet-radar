import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

def test_query(site, url, q):
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        print(f"\n--- {site} ({r.status_code}) ---")
        soup = BeautifulSoup(r.text, 'html.parser')
        cards = soup.find_all(['div', 'li', 'article', 'a'])
        found = 0
        for c in cards:
            txt = c.get_text(' ', strip=True)
            if q.lower() in txt.lower() and ('₼' in txt or 'azn' in txt.lower()):
                if len(txt) < 180:
                    print(f"[{site}] {txt}")
                    found += 1
                    if found >= 3:
                        break
        if not found:
            print(f"[{site}] No direct short cards found.")
    except Exception as e:
        print(f"[{site}] Error: {e}")

if __name__ == '__main__':
    test_query("itemhesab", "https://itemhesab.az/search?q=windows", "windows")
    test_query("epin", "https://epin.az/?s=windows", "windows")
    test_query("dolphgame", "https://dolphgame.com/?s=windows", "windows")
