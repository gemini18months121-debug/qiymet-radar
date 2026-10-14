import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

for site in ['https://epin.az', 'https://dolphgame.com']:
    try:
        req = urllib.request.Request(site, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read().decode('utf-8', errors='ignore')
            forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\']', body, re.I)
            inputs = re.findall(r'<input[^>]*name=["\']([^"\']*)["\']', body, re.I)
            print(f'{site} forms: {forms}, inputs: {inputs}')
    except Exception as e:
        print(f'{site} -> {e}')
