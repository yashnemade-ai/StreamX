from flask import Flask, request, Response, stream_with_context
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Default Browser Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

@app.route('/api/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URL missing", 400

    # Auto-detect Domain for Referer/Origin bypass
    req_headers = HEADERS.copy()
    if "sunnxt" in target_url:
        req_headers["Referer"] = "https://www.sunnxt.com/"
        req_headers["Origin"] = "https://www.sunnxt.com"
    elif "hotstar" in target_url:
        req_headers["Referer"] = "https://www.hotstar.com/"
    elif "hubstream" in target_url:
        req_headers["Referer"] = "https://hubstream.art/"

    try:
        # Fetching stream from target
        r = requests.get(target_url, headers=req_headers, stream=True, timeout=15)
        
        def generate():
            for chunk in r.iter_content(chunk_size=1024*16):
                yield chunk

        # Return the stream to Shaka Player
        response = Response(stream_with_context(generate()), status=r.status_code)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Content-Type"] = r.headers.get("Content-Type")
        return response
    except Exception as e:
        return str(e), 500

# Vercel handling
def handler(event, context):
    return app(event, context)
