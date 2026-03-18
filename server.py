import requests
from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
# Allow your Vercel frontend to access this backend
CORS(app)

# Standard High-Speed Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

@app.route('/')
def index():
    return "STREAMX Backend (Shaka Optimized) is Live!"

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URL Parameter is missing", 400

    # ✅ AUTO-INJECT HEADERS (Fixes SunNXT, Hotstar, Hubstream)
    req_headers = HEADERS.copy()
    if "sunnxt" in target_url:
        req_headers["Referer"] = "https://www.sunnxt.com/"
        req_headers["Origin"] = "https://www.sunnxt.com"
    elif "hotstar" in target_url:
        req_headers["Referer"] = "https://www.hotstar.com/"
    elif "hubstream" in target_url:
        req_headers["Referer"] = "https://hubstream.art/"

    try:
        # Stream the content to avoid high RAM usage
        r = requests.get(target_url, headers=req_headers, stream=True, timeout=15)
        
        def generate():
            for chunk in r.iter_content(chunk_size=1024*16):
                yield chunk

        # Build Response
        response = Response(stream_with_context(generate()), status=r.status_code)
        
        # ✅ FIX CORS: Essential for Shaka Player to load segments
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Content-Type"] = r.headers.get("Content-Type")
        
        return response

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Run on Port 5000 (Default for Flask)
    app.run(host='0.0.0.0', port=5000, threaded=True)
