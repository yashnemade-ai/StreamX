from flask import Flask, request, Response, stream_with_context
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Connection": "keep-alive"
    }

    # ✅ Forward Range header (IMPORTANT for ExoPlayer)
    range_header = request.headers.get("Range")
    if range_header:
        headers["Range"] = range_header

    # ✅ Auto headers
    if "sunnxt" in url:
        headers["Referer"] = "https://www.sunnxt.com/"
        headers["Origin"] = "https://www.sunnxt.com"
    elif "hotstar" in url:
        headers["Referer"] = "https://www.hotstar.com/"
    elif "hubstream" in url:
        headers["Referer"] = "https://hubstream.art/"

    try:
        r = requests.get(url, headers=headers, stream=True, timeout=15)

        def generate():
            for chunk in r.iter_content(chunk_size=1024*32):
                if chunk:
                    yield chunk

        resp = Response(stream_with_context(generate()), status=r.status_code)

        # ✅ CORS
        resp.headers["Access-Control-Allow-Origin"] = "*"

        # ✅ IMPORTANT for ExoPlayer
        resp.headers["Content-Type"] = r.headers.get("Content-Type", "application/octet-stream")
        resp.headers["Accept-Ranges"] = "bytes"

        if "Content-Range" in r.headers:
            resp.headers["Content-Range"] = r.headers["Content-Range"]

        if "Content-Length" in r.headers:
            resp.headers["Content-Length"] = r.headers["Content-Length"]

        return resp

    except Exception as e:
        return str(e), 500
