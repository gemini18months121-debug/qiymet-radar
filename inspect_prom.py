import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
r = requests.get('https://prom.az/?s=capcut', headers=headers, timeout=8)
soup = BeautifulSoup(r.text, 'html.parser')

for a in soup.find_all('a'):
    if 'capcut' in a.get_text().lower():
        parent = a.find_parent(['div', 'li', 'article'])
        if parent:
            p_text = parent.get_text(" ", strip=True)
            # Find any numbers with ₼ or AZN
            prices = re.findall(r'(\d+[\.,]?\d*)\s*(?:₼|AZN|azn|manat)', p_text)
            print("TITLE:", a.get_text(strip=True), "| PRICES FOUND:", prices, "| PARENT SNIPPET:", p_text[:100])
