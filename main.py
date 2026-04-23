from flask import Flask, request, Response, stream_with_context
import requests
import urllib3

# SSL Warning band karne ke liye
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/')
def home():
    return "StreamX Proxy is Running Smoothly!"

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URL is missing", 400

    # Loop Protection: Agar URL mein pehle se hamara proxy hai, toh use saaf karein
    if "onrender.com/proxy?url=" in target_url:
        target_url = target_url.split("url=")[-1]

    # Default Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.hotstar.com/",
        "Origin": "https://www.hotstar.com"
    }

    # Handle Pipe format
    if "|" in target_url:
        parts = target_url.split("|")
        target_url = parts[0]
        if len(parts) > 1:
            params = parts[1].split("&")
            for p in params:
                if "=" in p:
                    k, v = p.split("=", 1)
                    headers[k.strip()] = v.strip()

    try:
        # Stream=True use karna zaroori hai video segments ke liye
        r = requests.get(target_url, headers=headers, stream=True, timeout=15, verify=False)
        
        def generate():
            for chunk in r.iter_content(chunk_size=1024*256): # 256KB chunks
                yield chunk

        response = Response(stream_with_context(generate()), status=r.status_code)
        
        # Mandatory CORS Headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Content-Type'] = r.headers.get('Content-Type')
        
        return response

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
