import express from "express";
import fetch from "node-fetch";

const app = express();

app.get("/proxy", async (req, res) => {
    const url = req.query.url;

    const response = await fetch(url);
    const data = await response.text();

    res.set("Access-Control-Allow-Origin", "*");
    res.send(data);
});

app.listen(3000, () => console.log("Server running"));
