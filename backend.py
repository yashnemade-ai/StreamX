from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "No URL provided", 400

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, stream=True)

    def generate():
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                yield chunk

    return Response(generate(), content_type=r.headers.get('Content-Type'))

if __name__ == "__main__":
    app.run(debug=True)
