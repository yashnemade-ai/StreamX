import express from "express";

const app = express();

// ✅ ROOT FIX (Cannot GET / solve)
app.get("/", (req, res) => {
    res.send("StreamX Proxy Running 🚀");
});

// ✅ FULL STREAMING PROXY
app.get("/proxy", async (req, res) => {
    const url = req.query.url;

    if (!url) return res.send("No URL");

    try {
        const response = await fetch(url);

        // content type detect karo
        const contentType = response.headers.get("content-type");

        // 🔥 Agar m3u8 hai → rewrite
        if (contentType && contentType.includes("application/vnd.apple.mpegurl")) {
            let data = await response.text();

            const base = url.substring(0, url.lastIndexOf("/") + 1);

            data = data.replace(/(?!#)([^\n]+)/g, (line) => {
                if (line.startsWith("http")) {
                    return `/proxy?url=${encodeURIComponent(line)}`;
                } else if (line.trim() !== "") {
                    return `/proxy?url=${encodeURIComponent(base + line)}`;
                }
                return line;
            });

            res.set("Content-Type", "application/vnd.apple.mpegurl");
            res.set("Access-Control-Allow-Origin", "*");
            return res.send(data);
        }

        // 🔥 Agar video segment (.ts, .mp4, etc.)
        const buffer = await response.arrayBuffer();
        res.set("Access-Control-Allow-Origin", "*");
        res.send(Buffer.from(buffer));

    } catch (err) {
        res.status(500).send("Error fetching stream");
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Server running on", PORT));
