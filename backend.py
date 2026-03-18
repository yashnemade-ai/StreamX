from flask import Flask, request, Response
import requests
from urllib.parse import urljoin

app = Flask(__name__)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url
    }

    try:
        r = requests.get(url, headers=headers, stream=True)

        content_type = r.headers.get('Content-Type', '')

        # 🔥 If playlist (m3u8), fix relative paths
        if 'application/vnd.apple.mpegurl' in content_type or '.m3u8' in url:
            text = r.text
            base = url

            new_lines = []
            for line in text.split('\n'):
                if line.startswith('#') or line.strip() == '':
                    new_lines.append(line)
                else:
                    absolute = urljoin(base, line)
                    proxied = '/proxy?url=' + absolute
                    new_lines.append(proxied)

            return Response('\n'.join(new_lines),
                            content_type='application/vnd.apple.mpegurl',
                            headers={"Access-Control-Allow-Origin": "*"})

        # 🔥 For video segments / mp4 / ts / mpd
        def generate():
            for chunk in r.iter_content(1024):
                if chunk:
                    yield chunk

        return Response(generate(),
                        content_type=content_type,
                        headers={"Access-Control-Allow-Origin": "*"})

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
