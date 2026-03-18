let shakaPlayer;

async function openPlayer(url) {
    if (!url) return;

    const video = document.getElementById('v-player');
    document.getElementById('playerModal').style.display = 'flex';

    // Reset video
    video.pause();
    video.removeAttribute('src');
    video.load();

    // Destroy previous Shaka instance
    if (shakaPlayer) {
        await shakaPlayer.destroy();
        shakaPlayer = null;
    }

    try {
        // 🔥 MPD (DASH) → Shaka
        if (url.includes('.mpd')) {
            shakaPlayer = new shaka.Player(video);

            shakaPlayer.addEventListener('error', function (e) {
                console.error("Shaka error:", e);
            });

            await shakaPlayer.load(url);
            video.play();

        }
        // 🔥 M3U8 → HLS.js
        else if (url.includes('.m3u8')) {
            if (Hls.isSupported()) {
                const hls = new Hls();
                hls.loadSource(url);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function () {
                    video.play();
                });
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = url;
                video.play();
            }
        }
        // 🔥 MP4 direct
        else {
            video.src = url;
            video.play();
        }

    } catch (error) {
        console.error("Playback failed:", error);
        alert("Video play nahi ho rahi");
    }
}
