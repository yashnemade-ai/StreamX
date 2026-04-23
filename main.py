from flask import Flask, request, Response, stream_with_context
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

@app.route('/')
def home():
    return "StreamX Proxy is Live", 200

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "URL Missing", 400

    # 1. Parse URL and Headers
    target_url = url
    custom_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    if "|" in url:
        parts = url.split("|")
        target_url = parts[0]
        if len(parts) > 1:
            params = parts[1].split("&")
            for p in params:
                if "=" in p:
                    k, v = p.split("=", 1)
                    custom_headers[k.strip()] = v.strip()

    # 2. Add Cricbuzz/Hotstar specific headers if detected
    if "cricbuzz" in target_url or "akamaihd" in target_url:
        custom_headers["Referer"] = "https://www.cricbuzz.com/"
        custom_headers["Origin"] = "https://www.cricbuzz.com"

    if "Range" in request.headers:
        custom_headers["Range"] = request.headers["Range"]

    try:
        # 3. Fetch data with stream=True
        r = requests.get(target_url, headers=custom_headers, stream=True, timeout=15, verify=False)
        
        def generate():
            for chunk in r.iter_content(chunk_size=1024*128): # Small chunks to prevent crash
                yield chunk

        # Build Response
        resp = Response(stream_with_context(generate()), status=r.status_code)
        
        # 4. Critical CORS Headers
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        
        if 'Content-Type' in r.headers:
            resp.headers['Content-Type'] = r.headers['Content-Type']
        if 'Content-Range' in r.headers:
            resp.headers['Content-Range'] = r.headers['Content-Range']
            
        return resp

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
