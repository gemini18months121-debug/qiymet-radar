import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
for u in [
    'https://www.itemhesab.az/axtaris?controller=search&s=windows',
    'https://www.itemhesab.az/search?controller=search&search_query=windows',
    'https://www.itemhesab.az/search?s=windows'
]:
    r = requests.get(u, headers=headers)
    print(f"{u} -> status {r.status_code}")
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.select('.product-miniature, .product-description, [class*="product-"]')
    print(f"Items found: {len(items)}")
    for item in items[:5]:
        t = item.select_one('h2, h3, .product-title')
        pr = item.select_one('.price, .current-price')
        if t and pr:
            print(" ->", t.get_text(strip=True), "|", pr.get_text(strip=True))
