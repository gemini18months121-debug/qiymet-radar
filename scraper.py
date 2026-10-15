import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'az,tr,en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
}

def parse_duration(text):
    """Extracts duration like 1 Ay, 3 Ay, 1 İl, Ömürlük, 7 Gün."""
    t = text.replace('İ', 'i').replace('I', 'ı').lower()
    if any(k in t for k in ['ömürlük', 'omurluk', 'limitsiz', 'lifetime', 'ömürluk']):
        return 'Ömürlük'
    m = re.search(r'(\d+)\s*(?:il|illik|year)', t)
    if m:
        return f"{m.group(1)} İl"
    m = re.search(r'(\d+)\s*(?:ay|aylıq|month)', t)
    if m:
        return f"{m.group(1)} Ay"
    m = re.search(r'(\d+)\s*(?:gün|gun|günlük|gunluk|day)', t)
    if m:
        return f"{m.group(1)} Gün"
    return '1 Ay'

def clean_title(title):
    """Clean up repeated prefixes and suffixes from scraped titles."""
    t = re.sub(r'Ətraflı\s*→?', '', title, flags=re.I).strip()
    t = re.sub(r'Stokda\s*var.*', '', t, flags=re.I).strip()
    t = re.sub(r'-\d+%.*', '', t).strip()
    # Remove repeated consecutive identical words
    words = t.split()
    if len(words) > 4:
        half = len(words) // 2
        if " ".join(words[:half]).lower() == " ".join(words[half:half*2]).lower():
            t = " ".join(words[:half])
    return t[:55]

def extract_prices(text):
    matches = re.findall(r'(\d+(?:[\.,]\d{1,2})?)\s*(?:₼|AZN|azn|manat)', text)
    prices = []
    for m in matches:
        try:
            val = float(m.replace(',', '.'))
            if 0.5 <= val <= 2500:
                prices.append(val)
        except ValueError:
            continue
    return prices

def scrape_ucuzhesablar_com(query):
    """Scrapes the user's own store (ucuzhesablar.com)."""
    results = []
    url = "https://ucuzhesablar.com"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'li', 'article', 'a']):
                txt = item.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('azn' in txt.lower() or '₼' in txt):
                    if 15 < len(txt) < 180:
                        m = re.search(r'(\d+(?:[\.,]\d{1,2})?)\s*(?:AZN|₼)', txt, re.I)
                        if m:
                            price = float(m.group(1).replace(',', '.'))
                            link_el = item.find('a') if item.name != 'a' else item
                            link = link_el.get('href') if link_el else url
                            if link and not link.startswith('http'):
                                link = 'https://ucuzhesablar.com/' + link.lstrip('/')
                            
                            duration = parse_duration(txt)
                            title = clean_title(txt)
                            results.append({
                                'site': 'ucuzhesablar.com',
                                'title': title,
                                'duration': duration,
                                'price': price,
                                'url': link,
                                'is_owner': True
                            })
    except Exception:
        pass
    
    # deduplicate by price
    seen = set()
    cleaned = []
    for it in results:
        if it['price'] not in seen:
            seen.add(it['price'])
            cleaned.append(it)
    return cleaned[:3]

def scrape_prom_az(query):
    results = []
    url = f"https://prom.az/?s={urllib.parse.quote(query)}&post_type=product"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.select('.product'):
                title_el = item.select_one('.woocommerce-loop-product__title, h2, h3, a')
                price_el = item.select_one('.price')
                if title_el and price_el:
                    title = title_el.get_text(strip=True)
                    if any(w in title.lower() for w in query.lower().split()):
                        prices = extract_prices(price_el.get_text(' ', strip=True))
                        if prices:
                            sale_price = min(prices)
                            link_el = item.select_one('a')
                            link = link_el.get('href') if link_el else url
                            duration = parse_duration(title)
                            results.append({
                                'site': 'prom.az',
                                'title': clean_title(title),
                                'duration': duration,
                                'price': sale_price,
                                'url': link,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:3]

def scrape_based_az(query):
    results = []
    url = f"https://based.az/?s={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for card in soup.find_all(['div', 'article']):
                txt = card.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('₼' in txt or 'azn' in txt.lower()):
                    if 15 < len(txt) < 180:
                        prices = extract_prices(txt)
                        if prices:
                            sale_price = min(prices)
                            title_m = re.search(r'(?:indi al|bax|al|kredit ilə)?\s*([A-Za-z0-9\s\+\-\(\)\.]{4,60})', txt, re.I)
                            title = title_m.group(1).strip() if title_m else txt[:45]
                            duration = parse_duration(txt)
                            results.append({
                                'site': 'based.az',
                                'title': clean_title(title),
                                'duration': duration,
                                'price': sale_price,
                                'url': url,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:3]

def scrape_appbazar_az(query):
    results = []
    url = f"https://appbazar.az/?s={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'article', 'li']):
                txt = item.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('₼' in txt or 'azn' in txt.lower()):
                    if 15 < len(txt) < 160:
                        prices = extract_prices(txt)
                        if prices:
                            sale_price = min(prices)
                            link_el = item.find('a')
                            link = link_el.get('href') if link_el else url
                            duration = parse_duration(txt)
                            results.append({
                                'site': 'appbazar.az',
                                'title': clean_title(txt),
                                'duration': duration,
                                'price': sale_price,
                                'url': link,
                                'is_owner': False
                            })
    except Exception:
        pass
    seen = set()
    unique = []
    for r in results:
        if r['price'] not in seen:
            seen.add(r['price'])
            unique.append(r)
    return unique[:3]

def scrape_elnur_store(query):
    results = []
    url = f"https://elnur.store/search?q={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'li', 'p']):
                txt = item.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('₼' in txt or 'azn' in txt.lower()):
                    if 15 < len(txt) < 150:
                        prices = extract_prices(txt)
                        if prices:
                            duration = parse_duration(txt)
                            results.append({
                                'site': 'elnur.store',
                                'title': clean_title(txt),
                                'duration': duration,
                                'price': min(prices),
                                'url': url,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:2]

def scrape_tenebris_az(query):
    results = []
    url = f"https://tenebris.az/search?q={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'article', 'a']):
                txt = item.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('₼' in txt or 'azn' in txt.lower()):
                    if 15 < len(txt) < 140:
                        prices = extract_prices(txt)
                        if prices:
                            duration = parse_duration(txt)
                            results.append({
                                'site': 'tenebris.az',
                                'title': clean_title(txt),
                                'duration': duration,
                                'price': min(prices),
                                'url': url,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:2]

def scrape_hesablar_az(query):
    results = []
    url = f"https://hesablar.az/search?q={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'article', 'li']):
                txt = item.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('₼' in txt or 'azn' in txt.lower()):
                    if 15 < len(txt) < 140:
                        prices = extract_prices(txt)
                        if prices:
                            duration = parse_duration(txt)
                            results.append({
                                'site': 'hesablar.az',
                                'title': clean_title(txt),
                                'duration': duration,
                                'price': min(prices),
                                'url': url,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:2]

def scrape_itemhesab_az(query):
    results = []
    url = f"https://www.itemhesab.az/search?s={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.select('.product-miniature, .product-description, [class*="product-"]'):
                t = item.select_one('h2, h3, .product-title')
                pr = item.select_one('.price, .current-price')
                if t and pr:
                    title = t.get_text(strip=True)
                    if any(w in title.lower() for w in query.lower().split()):
                        prices = extract_prices(pr.get_text(strip=True))
                        if prices:
                            link_el = item.select_one('a')
                            link = link_el.get('href') if link_el else url
                            duration = parse_duration(title)
                            results.append({
                                'site': 'itemhesab.az',
                                'title': clean_title(title),
                                'duration': duration,
                                'price': min(prices),
                                'url': link,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:2]

def scrape_epin_az(query):
    results = []
    url = f"https://epin.az/?s={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'li', 'a']):
                txt = item.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('₼' in txt or 'azn' in txt.lower()):
                    if 15 < len(txt) < 120:
                        prices = extract_prices(txt)
                        if prices:
                            duration = parse_duration(txt)
                            results.append({
                                'site': 'epin.az',
                                'title': clean_title(txt),
                                'duration': duration,
                                'price': min(prices),
                                'url': url,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:2]

def scrape_dolphgame_com(query):
    results = []
    url = f"https://dolphgame.com/?s={urllib.parse.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'li', 'a']):
                txt = item.get_text(' ', strip=True)
                if any(w in txt.lower() for w in query.lower().split()) and ('₼' in txt or 'azn' in txt.lower()):
                    if 15 < len(txt) < 120:
                        prices = extract_prices(txt)
                        if prices:
                            duration = parse_duration(txt)
                            results.append({
                                'site': 'dolphgame.com',
                                'title': clean_title(txt),
                                'duration': duration,
                                'price': min(prices),
                                'url': url,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:2]

def search_all_sites(query):
    """
    Scrapes all 10 sites (including ucuzhesablar.com) in parallel threads.
    """
    scrapers = [
        scrape_ucuzhesablar_com,
        scrape_prom_az,
        scrape_based_az,
        scrape_appbazar_az,
        scrape_elnur_store,
        scrape_tenebris_az,
        scrape_hesablar_az,
        scrape_itemhesab_az,
        scrape_epin_az,
        scrape_dolphgame_com
    ]
    
    all_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fn, query) for fn in scrapers]
        for f in as_completed(futures):
            try:
                res = f.result()
                if res:
                    all_results.extend(res)
            except Exception:
                pass

    # Deduplicate per site and round prices
    cleaned = []
    seen = set()
    for item in all_results:
        item['price'] = round(item['price'], 2)
        key = (item['site'], item['price'], item['duration'])
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    # Sort ascending by price
    cleaned.sort(key=lambda x: x['price'])
    
    lowest = cleaned[0]['price'] if cleaned else None
    cheapest_site = cleaned[0]['site'] if cleaned else None
    
    # Check user's own store status
    owner_items = [i for i in cleaned if i.get('is_owner')]
    owner_lowest = owner_items[0]['price'] if owner_items else None
    is_owner_cheapest = (lowest is not None and owner_lowest is not None and owner_lowest <= lowest)

    # Calculate recommended competitive sale price (if user's store not already cheapest)
    rec_price = None
    if lowest:
        if lowest <= 5:
            rec_price = round(max(0.5, lowest - 0.50), 2)
        elif lowest <= 15:
            rec_price = round(max(1.0, lowest - 1.00), 2)
        else:
            rec_price = round(lowest * 0.9, 2)

    return {
        'query': query,
        'total_found': len(cleaned),
        'lowest_price': lowest,
        'cheapest_site': cheapest_site,
        'owner_lowest': owner_lowest,
        'is_owner_cheapest': is_owner_cheapest,
        'recommended_price': rec_price,
        'items': cleaned
    }

if __name__ == '__main__':
    res = search_all_sites("capcut")
    print(f"Total: {res['total_found']}, Lowest: {res['lowest_price']} ₼ on {res['cheapest_site']}")
    print(f"Is Ucuzhesablar.com cheapest? {res['is_owner_cheapest']}")
    for it in res['items']:
        tag = " [👑 BİZİM SAYT]" if it['is_owner'] else ""
        print(f"  {it['site']}{tag} | {it['duration']} | {it['price']} ₼ -> {it['title']}")
