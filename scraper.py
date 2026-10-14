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

def extract_prices(text):
    """Extract all price values found with currency symbols (₼, AZN, manat)."""
    # Regex for prices like: 4.99 ₼, 4,99 AZN, 12 ₼, 25.00₼
    matches = re.findall(r'(\d+(?:[\.,]\d{1,2})?)\s*(?:₼|AZN|azn|manat)', text)
    prices = []
    for m in matches:
        try:
            val = float(m.replace(',', '.'))
            if 0.5 <= val <= 2000:
                prices.append(val)
        except ValueError:
            continue
    return prices

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
                            # lowest price in .price is the active sale price
                            sale_price = min(prices)
                            link_el = item.select_one('a')
                            link = link_el.get('href') if link_el else url
                            results.append({
                                'site': 'prom.az',
                                'title': title,
                                'price': sale_price,
                                'url': link
                            })
    except Exception:
        pass
    return results

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
                            # Extract clean title
                            title_m = re.search(r'(?:indi al|bax|al|kredit ilə)?\s*([A-Za-z0-9\s\+\-\(\)\.]{4,60})', txt, re.I)
                            title = title_m.group(1).strip() if title_m else txt[:45]
                            results.append({
                                'site': 'based.az',
                                'title': title,
                                'price': sale_price,
                                'url': url
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
                            results.append({
                                'site': 'appbazar.az',
                                'title': txt[:60],
                                'price': sale_price,
                                'url': link
                            })
    except Exception:
        pass
    # deduplicate by price
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
                            results.append({
                                'site': 'elnur.store',
                                'title': txt[:60],
                                'price': min(prices),
                                'url': url
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
                            results.append({
                                'site': 'tenebris.az',
                                'title': txt[:55],
                                'price': min(prices),
                                'url': url
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
                            results.append({
                                'site': 'hesablar.az',
                                'title': txt[:60],
                                'price': min(prices),
                                'url': url
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
                            results.append({
                                'site': 'itemhesab.az',
                                'title': title,
                                'price': min(prices),
                                'url': link
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
                            results.append({
                                'site': 'epin.az',
                                'title': txt[:50],
                                'price': min(prices),
                                'url': url
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
                            results.append({
                                'site': 'dolphgame.com',
                                'title': txt[:50],
                                'price': min(prices),
                                'url': url
                            })
    except Exception:
        pass
    return results[:2]

def search_all_sites(query):
    """
    Scrapes all 9 sites concurrently in parallel threads.
    Returns:
      {
        'query': query,
        'lowest_price': float,
        'recommended_price': float,
        'cheapest_site': str,
        'items': list of items sorted by price ascending
      }
    """
    scrapers = [
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
    with ThreadPoolExecutor(max_workers=9) as executor:
        futures = [executor.submit(fn, query) for fn in scrapers]
        for f in as_completed(futures):
            try:
                res = f.result()
                if res:
                    all_results.extend(res)
            except Exception:
                pass

    # Clean and filter duplicates per site
    cleaned = []
    seen = set()
    for item in all_results:
        # round price to 2 decimal places
        item['price'] = round(item['price'], 2)
        key = (item['site'], item['price'])
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    # Sort ascending by price
    cleaned.sort(key=lambda x: x['price'])
    
    lowest = cleaned[0]['price'] if cleaned else None
    cheapest_site = cleaned[0]['site'] if cleaned else None
    
    # Calculate recommended competitive sale price:
    # 5% to 10% lower, rounded nicely (e.g., .90 or .49 or minus 0.50)
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
        'recommended_price': rec_price,
        'cheapest_site': cheapest_site,
        'items': cleaned
    }

if __name__ == '__main__':
    import time
    start = time.time()
    res = search_all_sites("capcut")
    print(f"Elapsed: {time.time() - start:.2f}s")
    print(f"Lowest: {res['lowest_price']} AZN on {res['cheapest_site']}")
    print(f"Recommended Sale Price: {res['recommended_price']} AZN")
    print("Found items:")
    for it in res['items']:
        print(f"  [{it['site']}] {it['price']} ₼ -> {it['title']}")
