from flask import Flask, request, Response, stream_with_context
import requests
from urllib.parse import urlparse

app = Flask(__name__)

@app.route('/')
def home():
    return "StreamX Universal Proxy is Running!"

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URL is missing", 400

    # 1. Extract manual headers from pipe format (|)
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    # Browser se aane wala 'Range' header copy karein (Seeking ke liye zaroori hai)
    if "Range" in request.headers:
        custom_headers["Range"] = request.headers["Range"]

    if "|" in target_url:
        parts = target_url.split("|")
        target_url = parts[0].trim()
        if len(parts) > 1:
            params = parts[1].split("&")
            for p in params:
                if "=" in p:
                    k, v = p.split("=", 1)
                    custom_headers[k.strip()] = v.strip()

    # 2. Domain specific auto-spoofing
    domain = urlparse(target_url).netloc
    if "cricbuzz.com" in domain or "willow" in domain:
        custom_headers["Referer"] = "https://www.cricbuzz.com/"
        custom_headers["Origin"] = "https://www.cricbuzz.com"
    elif "hotstar.com" in domain:
        custom_headers["Referer"] = "https://www.hotstar.com/"
        custom_headers["Origin"] = "https://www.hotstar.com"
    
    # Generic Referer fallback
    if "Referer" not in custom_headers:
        custom_headers["Referer"] = f"{urlparse(target_url).scheme}://{domain}/"

    try:
        # 3. Fetch the content (allow_redirects=True handle karega .php links ko)
        # verify=False use kiya hai kyunki IPTV links ke SSL aksar expired hote hain
        r = requests.get(target_url, headers=custom_headers, stream=True, timeout=20, verify=False, allow_redirects=True)

        def generate():
            # 128KB ke chunks mein data bhejenge (Smooth buffering ke liye)
            for chunk in r.iter_content(chunk_size=128*1024):
                yield chunk

        response = Response(stream_with_context(generate()), status=r.status_code)

        # 4. Mandatory CORS Headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'

        # 5. Pass-through zaroori video headers
        headers_to_copy = ['Content-Type', 'Content-Length', 'Content-Range', 'Accept-Ranges']
        for header in headers_to_copy:
            if header in r.headers:
                response.headers[header] = r.headers[header]

        return response

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    # Render automatically port provide karta hai
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
