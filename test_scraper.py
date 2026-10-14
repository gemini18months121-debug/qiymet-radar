import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'az,tr,en;q=0.9',
}

def extract_price(text):
    # Matches patterns like 4.99 ₼, 4,99 AZN, 12.00₼, 10 AZN, etc.
    m = re.search(r'(\d+[\.,]?\d*)\s*(?:₼|AZN|azn|manat)', text)
    if m:
        try:
            val = float(m.group(1).replace(',', '.'))
            return val
        except ValueError:
            pass
    return None

def test_scrape_site(name, url, query):
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200:
            print(f"[{name}] HTTP {r.status_code}")
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Generic heuristic: look for cards or links containing query
        products = []
        # Find elements that mention query
        for el in soup.find_all(['div', 'li', 'article', 'a']):
            el_text = el.get_text(" ", strip=True)
            if query.lower() in el_text.lower():
                price = extract_price(el_text)
                if price and 0.5 <= price <= 500:
                    # check if this is a relatively concise card
                    if len(el_text) < 250:
                        products.append((el_text[:80], price))
        
        # Deduplicate
        seen = set()
        unique = []
        for title, p in products:
            key = (round(p, 2))
            if key not in seen:
                seen.add(key)
                unique.append((title, p))
                
        print(f"[{name}] Found {len(unique)} items:")
        for t, p in unique[:3]:
            print(f"   -> {p:.2f} AZN | {t}")
    except Exception as e:
        print(f"[{name}] Error: {e}")

if __name__ == '__main__':
    q = "capcut"
    test_scrape_site("based.az", f"https://based.az/?s={q}", q)
    test_scrape_site("prom.az", f"https://prom.az/?s={q}", q)
    test_scrape_site("appbazar.az", f"https://appbazar.az/?s={q}", q)
    test_scrape_site("elnur.store", f"https://elnur.store/search?q={q}", q)
    test_scrape_site("tenebris.az", f"https://tenebris.az/search?q={q}", q)
    test_scrape_site("hesablar.az", f"https://hesablar.az/search?q={q}", q)
    test_scrape_site("itemhesab.az", f"https://itemhesab.az/search?q={q}", q)
    test_scrape_site("dolphgame.com", f"https://dolphgame.com/?s={q}", q)
