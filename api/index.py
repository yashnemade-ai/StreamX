from flask import Flask, request, Response, stream_with_context
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    url = request.args.get('url')
    if not url: return "Missing URL", 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Connection": "keep-alive"
    }

    # ✅ Auto Headers for unblocking
    if "sunnxt" in url:
        headers["Referer"] = "https://www.sunnxt.com/"
        headers["Origin"] = "https://www.sunnxt.com"
    elif "hotstar" in url:
        headers["Referer"] = "https://www.hotstar.com/"
    elif "hubstream" in target_url:
        req_headers["Referer"] = "https://hubstream.art/"

    try:
        # Vercel bypass for large chunks
        r = requests.get(url, headers=headers, stream=True, timeout=10)
        
        def generate():
            for chunk in r.iter_content(chunk_size=1024*16):
                yield chunk

        resp = Response(stream_with_context(generate()), status=r.status_code)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        # ✅ Video/Audio segments load hone ke liye zaroori header
        resp.headers["Content-Type"] = r.headers.get("Content-Type", "application/octet-stream")
        return resp
    except Exception as e:
        return str(e), 500
