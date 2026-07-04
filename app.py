import os
import time
import requests
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

app = Flask(__name__)
CORS(app)

TARGET_URL = "https://srtfile.github.io/vidnest/movie/254"
WAIT_SECONDS = 5


def extract_all_urls(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    urls = {}

    # Anchor tags
    for tag in soup.find_all('a', href=True):
        raw = tag['href'].strip()
        if raw and raw not in ('#', 'javascript:void(0)', 'javascript:;'):
            full = urljoin(base_url, raw)
            label = (tag.get_text(strip=True) or tag.get('title', '') or raw)[:80]
            urls[full] = {'url': full, 'label': label, 'type': 'anchor'}

    # Script src
    for tag in soup.find_all('script', src=True):
        raw = tag['src'].strip()
        if raw:
            full = urljoin(base_url, raw)
            urls[full] = {'url': full, 'label': raw[:80], 'type': 'script'}

    # Link href
    for tag in soup.find_all('link', href=True):
        raw = tag['href'].strip()
        if raw:
            full = urljoin(base_url, raw)
            rel = ' '.join(tag.get('rel', []))
            urls[full] = {'url': full, 'label': rel or raw[:80], 'type': 'link'}

    # Img src
    for tag in soup.find_all('img', src=True):
        raw = tag['src'].strip()
        if raw:
            full = urljoin(base_url, raw)
            alt = tag.get('alt', '')[:80] or raw[:80]
            urls[full] = {'url': full, 'label': alt, 'type': 'image'}

    # iframe src
    for tag in soup.find_all('iframe', src=True):
        raw = tag['src'].strip()
        if raw:
            full = urljoin(base_url, raw)
            urls[full] = {'url': full, 'label': raw[:80], 'type': 'iframe'}

    # source src (video/audio)
    for tag in soup.find_all('source', src=True):
        raw = tag['src'].strip()
        if raw:
            full = urljoin(base_url, raw)
            urls[full] = {'url': full, 'label': raw[:80], 'type': 'media-source'}

    # data-src (lazy-loaded)
    for tag in soup.find_all(attrs={'data-src': True}):
        raw = tag['data-src'].strip()
        if raw:
            full = urljoin(base_url, raw)
            urls[full] = {'url': full, 'label': raw[:80], 'type': 'lazy-src'}

    # Inline JS / raw URL regex
    inline_urls = re.findall(r'(?:https?://)[^\s\'"<>\)\]\}]+', html_content)
    for u in inline_urls:
        u = u.rstrip('.,;:')
        if u not in urls:
            urls[u] = {'url': u, 'label': u[:80], 'type': 'inline'}

    return list(urls.values())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch')
def fetch():
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    steps = [{'step': 1, 'msg': f'Navigating to {TARGET_URL}', 'status': 'ok'}]

    try:
        resp = requests.get(TARGET_URL, headers=headers, timeout=20)
        resp.raise_for_status()
        steps.append({'step': 2, 'msg': f'Page loaded (HTTP {resp.status_code})', 'status': 'ok'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'steps': steps})

    steps.append({'step': 3, 'msg': f'Waiting {WAIT_SECONDS}s for dynamic content…', 'status': 'ok'})
    time.sleep(WAIT_SECONDS)
    steps.append({'step': 4, 'msg': 'Wait complete', 'status': 'ok'})

    urls = extract_all_urls(resp.text, TARGET_URL)
    steps.append({'step': 5, 'msg': f'Extracted {len(urls)} unique URLs', 'status': 'ok'})

    by_type = {}
    for u in urls:
        by_type.setdefault(u['type'], []).append(u)

    soup = BeautifulSoup(resp.text, 'html.parser')
    page_title = soup.title.string if soup.title else 'N/A'

    return jsonify({
        'success': True,
        'target': TARGET_URL,
        'total': len(urls),
        'urls': urls,
        'by_type': by_type,
        'steps': steps,
        'page_title': page_title,
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=False)
