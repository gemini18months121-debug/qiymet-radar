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

STOP_WORDS = {
    'pro', 'key', 'hesab', 'hesabi', 'hesabı', 'ay', 'ayliq', 'aylıq', 
    'gun', 'gün', 'gunluk', 'günlük', 'il', 'illik', 'premium', 'azn', 
    'retial', 'retail', 'oem', 'digital', 'lisenziya', 'limitsiz', 
    'full', 'paket', 'şəxsi', 'sexsi', 'ortaq', 'hazır', 'hazir', 
    'sərfəli', 'super', 'plus', 'plan', 'al', 'sat', 'satin'
}

def normalize_token(w):
    w = w.lower().strip()
    if w.startswith('window'):
        return 'window'
    if w.startswith('spotify'):
        return 'spotify'
    if w.startswith('capcut'):
        return 'capcut'
    if w.startswith('netflix'):
        return 'netflix'
    if w.startswith('canva'):
        return 'canva'
    if w.startswith('chatgpt') or w.startswith('openai'):
        return 'chatgpt'
    if w.startswith('office') or w.startswith('microsoft'):
        return 'office'
    return w

def is_relevant_product(query, title):
    """
    Strict relevancy filter.
    Extracts core keywords from query (excluding generic words like pro, key, ay).
    Every core keyword MUST be present in the product title!
    """
    raw_q_words = re.findall(r'[A-Za-z0-9]+', query)
    core_q = [normalize_token(w) for w in raw_q_words if w.lower() not in STOP_WORDS]
    if not core_q:
        core_q = [normalize_token(w) for w in raw_q_words]

    t_words = [normalize_token(w) for w in re.findall(r'[A-Za-z0-9]+', title)]
    t_text = " ".join(t_words)

    for q in core_q:
        # Check if q is a standalone token or substring in title
        if not any(q == t or q in t for t in t_words):
            return False
            
    # Extra check for version numbers (e.g. windows 10 vs windows 11)
    if '11' in raw_q_words and '11' not in title:
        return False
    if '10' in raw_q_words and '10' not in title and '11' in title:
        return False

    return True

def parse_duration_info(text):
    """
    Returns (duration_display_str, duration_in_months)
    Used to calculate unit price per month for fair comparison.
    """
    t = text.replace('İ', 'i').replace('I', 'ı').lower()
    
    if any(k in t for k in ['ömürlük', 'omurluk', 'limitsiz', 'lifetime', 'ömürluk']):
        # Lifetime treated as at least 12 months for equivalent comparison
        return 'Ömürlük', 12.0
        
    m = re.search(r'(\d+)\s*(?:il|illik|year)', t)
    if m:
        val = float(m.group(1))
        return f"{int(val)} İl", val * 12.0
        
    m = re.search(r'(\d+)\s*(?:ay|aylıq|month)', t)
    if m:
        val = float(m.group(1))
        return f"{int(val)} Ay", val
        
    m = re.search(r'(\d+)\s*(?:gün|gun|günlük|gunluk|day)', t)
    if m:
        val = float(m.group(1))
        return f"{int(val)} Gün", max(0.25, val / 30.0)
        
    return '1 Ay', 1.0

def clean_title(title):
    t = re.sub(r'Ətraflı\s*→?', '', title, flags=re.I).strip()
    t = re.sub(r'Stokda\s*var.*', '', t, flags=re.I).strip()
    t = re.sub(r'-\d+%.*', '', t).strip()
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
    """Scrapes user's own store (ucuzhesablar.com)."""
    results = []
    url = "https://ucuzhesablar.com"
    try:
        r = requests.get(url, headers=HEADERS, timeout=7)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for item in soup.find_all(['div', 'li', 'article', 'a']):
                txt = item.get_text(' ', strip=True)
                if ('azn' in txt.lower() or '₼' in txt) and 15 < len(txt) < 180:
                    if is_relevant_product(query, txt):
                        m = re.search(r'(\d+(?:[\.,]\d{1,2})?)\s*(?:AZN|₼)', txt, re.I)
                        if m:
                            price = float(m.group(1).replace(',', '.'))
                            link_el = item.find('a') if item.name != 'a' else item
                            link = link_el.get('href') if link_el else url
                            if link and not link.startswith('http'):
                                link = 'https://ucuzhesablar.com/' + link.lstrip('/')
                            
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'ucuzhesablar.com',
                                'title': clean_title(txt),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': price,
                                'monthly_price': round(price / duration_months, 2),
                                'url': link,
                                'is_owner': True
                            })
    except Exception:
        pass
    
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
                    if is_relevant_product(query, title):
                        prices = extract_prices(price_el.get_text(' ', strip=True))
                        if prices:
                            sale_price = min(prices)
                            link_el = item.select_one('a')
                            link = link_el.get('href') if link_el else url
                            duration_str, duration_months = parse_duration_info(title)
                            results.append({
                                'site': 'prom.az',
                                'title': clean_title(title),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': sale_price,
                                'monthly_price': round(sale_price / duration_months, 2),
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
                if ('₼' in txt or 'azn' in txt.lower()) and 15 < len(txt) < 180:
                    if is_relevant_product(query, txt):
                        prices = extract_prices(txt)
                        if prices:
                            sale_price = min(prices)
                            title_m = re.search(r'(?:indi al|bax|al|kredit ilə)?\s*([A-Za-z0-9\s\+\-\(\)\.]{4,60})', txt, re.I)
                            title = title_m.group(1).strip() if title_m else txt[:45]
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'based.az',
                                'title': clean_title(title),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': sale_price,
                                'monthly_price': round(sale_price / duration_months, 2),
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
                if ('₼' in txt or 'azn' in txt.lower()) and 15 < len(txt) < 160:
                    if is_relevant_product(query, txt):
                        prices = extract_prices(txt)
                        if prices:
                            sale_price = min(prices)
                            link_el = item.find('a')
                            link = link_el.get('href') if link_el else url
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'appbazar.az',
                                'title': clean_title(txt),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': sale_price,
                                'monthly_price': round(sale_price / duration_months, 2),
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
                if ('₼' in txt or 'azn' in txt.lower()) and 15 < len(txt) < 150:
                    if is_relevant_product(query, txt):
                        prices = extract_prices(txt)
                        if prices:
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'elnur.store',
                                'title': clean_title(txt),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': min(prices),
                                'monthly_price': round(min(prices) / duration_months, 2),
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
                if ('₼' in txt or 'azn' in txt.lower()) and 15 < len(txt) < 140:
                    if is_relevant_product(query, txt):
                        prices = extract_prices(txt)
                        if prices:
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'tenebris.az',
                                'title': clean_title(txt),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': min(prices),
                                'monthly_price': round(min(prices) / duration_months, 2),
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
                if ('₼' in txt or 'azn' in txt.lower()) and 15 < len(txt) < 140:
                    if is_relevant_product(query, txt):
                        prices = extract_prices(txt)
                        if prices:
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'hesablar.az',
                                'title': clean_title(txt),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': min(prices),
                                'monthly_price': round(min(prices) / duration_months, 2),
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
                    if is_relevant_product(query, title):
                        prices = extract_prices(pr.get_text(strip=True))
                        if prices:
                            link_el = item.select_one('a')
                            link = link_el.get('href') if link_el else url
                            duration_str, duration_months = parse_duration_info(title)
                            results.append({
                                'site': 'itemhesab.az',
                                'title': clean_title(title),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': min(prices),
                                'monthly_price': round(min(prices) / duration_months, 2),
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
                if ('₼' in txt or 'azn' in txt.lower()) and 15 < len(txt) < 120:
                    if is_relevant_product(query, txt):
                        prices = extract_prices(txt)
                        if prices:
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'epin.az',
                                'title': clean_title(txt),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': min(prices),
                                'monthly_price': round(min(prices) / duration_months, 2),
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
                if ('₼' in txt or 'azn' in txt.lower()) and 15 < len(txt) < 120:
                    if is_relevant_product(query, txt):
                        prices = extract_prices(txt)
                        if prices:
                            duration_str, duration_months = parse_duration_info(txt)
                            results.append({
                                'site': 'dolphgame.com',
                                'title': clean_title(txt),
                                'duration': duration_str,
                                'months': duration_months,
                                'price': min(prices),
                                'monthly_price': round(min(prices) / duration_months, 2),
                                'url': url,
                                'is_owner': False
                            })
    except Exception:
        pass
    return results[:2]

def search_all_sites(query):
    """
    Scrapes all 10 sites concurrently.
    Sorts by monthly_price (unit value per month) to fairly compare:
    e.g. 4 months for 6.20 AZN (1.55 AZN/month) beats 1 month for 5.99 AZN (5.99 AZN/month).
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

    # Deduplicate
    cleaned = []
    seen = set()
    for item in all_results:
        item['price'] = round(item['price'], 2)
        key = (item['site'], item['price'], item['duration'])
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    # Sort primarily by monthly_price (aylıq vahid qiymət), secondarily by total price
    cleaned.sort(key=lambda x: (x['monthly_price'], x['price']))
    
    lowest_monthly = cleaned[0]['monthly_price'] if cleaned else None
    cheapest_item = cleaned[0] if cleaned else None
    
    # Check user's own store status
    owner_items = [i for i in cleaned if i.get('is_owner')]
    owner_best = owner_items[0] if owner_items else None
    owner_product_url = owner_best['url'] if owner_best else "https://ucuzhesablar.com"
    
    is_owner_cheapest = False
    if cheapest_item and cheapest_item.get('is_owner'):
        is_owner_cheapest = True
    elif owner_best and lowest_monthly and owner_best['monthly_price'] <= lowest_monthly:
        is_owner_cheapest = True

    return {
        'query': query,
        'total_found': len(cleaned),
        'cheapest_item': cheapest_item,
        'lowest_price': cheapest_item['price'] if cheapest_item else None,
        'lowest_monthly': lowest_monthly,
        'cheapest_site': cheapest_item['site'] if cheapest_item else None,
        'owner_best': owner_best,
        'owner_product_url': owner_product_url,
        'is_owner_cheapest': is_owner_cheapest,
        'items': cleaned
    }

if __name__ == '__main__':
    for test_q in ["canva pro", "spotify", "windows 11", "capcut pro"]:
        res = search_all_sites(test_q)
        print(f"\n=== Axtarış: {test_q} (Tapıldı: {res['total_found']}) ===")
        print(f"Lider: {res['cheapest_site']} (Aylıq: {res['lowest_monthly']} ₼)")
        print(f"Ucuzhesablar link: {res['owner_product_url']}")
        for it in res['items'][:4]:
            tag = " [👑 BİZİM]" if it['is_owner'] else ""
            print(f"  {it['site']}{tag} | {it['duration']} | Cəmi: {it['price']} ₼ (Aylıq: {it['monthly_price']} ₼) -> {it['title']}")
