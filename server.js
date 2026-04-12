import express from "express";

const app = express();

app.get("/proxy", async (req, res) => {
    const url = req.query.url;

    const response = await fetch(url); // built-in fetch
    const data = await response.text();

    res.set("Access-Control-Allow-Origin", "*");
    res.send(data);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log("Server running on", PORT));
