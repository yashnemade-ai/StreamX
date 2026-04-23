from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "StreamX Backend is Active!"

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "URL is missing", 400

    # Android code ki tarah headers spoofing
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.cricbuzz.com/",
        "Origin": "https://www.cricbuzz.com"
    }

    # Agar link mein manual headers bheje gaye hon (pipe format)
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
        # Stream the response back to browser
        req = requests.get(target_url, headers=headers, stream=True, timeout=10)
        
        def generate():
            for chunk in req.iter_content(chunk_size=4096):
                yield chunk

        resp = Response(generate(), status=req.status_code)
        
        # CORS allow karna taaki browser block na kare
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Content-Type'] = req.headers.get('Content-Type')
        return resp

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
