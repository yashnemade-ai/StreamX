from flask import Flask, request, Response, stream_with_context
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

@app.route('/')
def home():
    return "StreamX Proxy Active"

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URL missing", 400

    # Clean the URL
    if "|" in target_url:
        parts = target_url.split("|")
        target_url = parts[0]
        # Baki headers aapka extension handle kar lega
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.hotstar.com/",
        "Origin": "https://www.hotstar.com"
    }

    # Video Seeking ke liye Range header copy karna ZAROORI hai
    if "Range" in request.headers:
        headers["Range"] = request.headers["Range"]

    try:
        # Stream=True use karke memory bachate hain
        r = requests.get(target_url, headers=headers, stream=True, timeout=10, verify=False)
        
        def generate():
            for chunk in r.iter_content(chunk_size=128*1024): # 128KB chunks for speed
                yield chunk

        # Response headers build karein
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(name, value) for (name, value) in r.raw.headers.items()
                        if name.lower() not in excluded_headers]
        
        # Add CORS
        resp_headers.append(('Access-Control-Allow-Origin', '*'))

        return Response(stream_with_context(generate()), status=r.status_code, headers=resp_headers)

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
