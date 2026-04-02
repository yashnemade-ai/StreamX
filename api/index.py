from flask import Flask, request, Response, stream_with_context, send_from_directory
import requests
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="../public")
CORS(app)

# ✅ FRONTEND SERVE
@app.route("/")
def home():
    return send_from_directory("../public", "index.html")


# ✅ PROXY (ALL STREAM SUPPORT)
@app.route('/api/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Connection": "keep-alive"
    }

    # ✅ Range support (important for video players)
    range_header = request.headers.get("Range")
    if range_header:
        headers["Range"] = range_header

    # ✅ Smart referer/origin (auto detect)
    if "sunnxt" in url:
        headers["Referer"] = "https://www.sunnxt.com/"
        headers["Origin"] = "https://www.sunnxt.com"
    elif "hotstar" in url:
        headers["Referer"] = "https://www.hotstar.com/"
        headers["Origin"] = "https://www.hotstar.com"
    elif "jiocinema" in url:
        headers["Referer"] = "https://www.jiocinema.com/"
    elif "zee5" in url:
        headers["Referer"] = "https://www.zee5.com/"
    elif "sonyliv" in url:
        headers["Referer"] = "https://www.sonyliv.com/"
    elif "hubstream" in url:
        headers["Referer"] = "https://hubstream.art/"

    try:
        r = requests.get(url, headers=headers, stream=True, timeout=15)

        def generate():
            for chunk in r.iter_content(chunk_size=1024 * 64):
                if chunk:
                    yield chunk

        resp = Response(stream_with_context(generate()), status=r.status_code)

        # ✅ CORS
        resp.headers["Access-Control-Allow-Origin"] = "*"

        # ✅ Content headers
        resp.headers["Content-Type"] = r.headers.get("Content-Type", "application/octet-stream")
        resp.headers["Accept-Ranges"] = "bytes"

        if "Content-Range" in r.headers:
            resp.headers["Content-Range"] = r.headers["Content-Range"]

        if "Content-Length" in r.headers:
            resp.headers["Content-Length"] = r.headers["Content-Length"]

        return resp

    except Exception as e:
        return str(e), 500


# ✅ KEEP ALIVE ROUTE
@app.route("/ping")
def ping():
    return "OK"


# ✅ IMPORTANT: SERVER START (Render ke liye must)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
