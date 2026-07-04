import os
import time
import requests
from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_BASE = "https://srtfile.github.io/vidnest/"
WAIT_SECONDS = 5


def build_api_url(path):
    # /movie/254  →  https://srtfile.github.io/vidnest/?r=%2Fmovie%2F254
    from urllib.parse import quote
    encoded = quote(path, safe='')
    return f"{API_BASE}?r={encoded}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch')
def fetch():
    path = "/movie/254"
    api_url = build_api_url(path)

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0 Safari/537.36'
        ),
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://srtfile.github.io/',
    }

    steps = [{'step': 1, 'msg': f'Requesting {api_url}', 'status': 'ok'}]

    try:
        resp = requests.get(api_url, headers=headers, timeout=20)
        resp.raise_for_status()
        steps.append({'step': 2, 'msg': f'Response received (HTTP {resp.status_code})', 'status': 'ok'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'steps': steps})

    steps.append({'step': 3, 'msg': f'Waiting {WAIT_SECONDS}s for dynamic content…', 'status': 'ok'})
    time.sleep(WAIT_SECONDS)
    steps.append({'step': 4, 'msg': 'Wait complete', 'status': 'ok'})

    try:
        data = resp.json()
    except Exception as e:
        return jsonify({'success': False, 'error': f'JSON parse failed: {e}', 'steps': steps})

    # Extract all stream URLs
    servers = data.get('servers', [])
    all_streams = []
    ok_count = 0
    error_count = 0

    for srv in servers:
        status = srv.get('status', 'error')
        if status == 'ok':
            ok_count += 1
        else:
            error_count += 1
        for stream in srv.get('streams', []):
            all_streams.append({
                'server': srv['server'],
                'url': stream['url'],
                'type': stream.get('type', 'unknown'),
                'status': status,
            })

    steps.append({'step': 5, 'msg': f'Found {len(all_streams)} stream URLs across {ok_count} working servers', 'status': 'ok'})

    return jsonify({
        'success': True,
        'api_url': api_url,
        'query': data.get('query', {}),
        'proxy': data.get('proxy', ''),
        'total_servers': len(servers),
        'ok_servers': ok_count,
        'error_servers': error_count,
        'total_streams': len(all_streams),
        'servers': servers,
        'all_streams': all_streams,
        'steps': steps,
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=False)