#!/usr/bin/env node
/* Run inside the configured WeWe RSS container, where got and cheerio are present. */

const fs = require("fs");
const got = require("got").default;
const { load } = require("cheerio");

const inputPath = process.argv[2];
const outputPath = process.argv[3];
if (!inputPath || !outputPath) {
  console.error("Usage: node fetch_wechat_fulltext.js INPUT_JSON OUTPUT_JSON");
  process.exit(2);
}

const payload = JSON.parse(fs.readFileSync(inputPath, "utf8"));
const entries = Array.isArray(payload) ? payload : (payload.entries || []);
const targets = entries.filter((item) => item.platform === "公众号");
const headers = {
  accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "accept-language": "zh-CN,zh;q=0.9,en;q=0.7",
  "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

(async () => {
  const output = [];
  for (const item of targets) {
    const id = item.external_id || "";
    const url = item.link || `https://mp.weixin.qq.com/s/${id}`;
    try {
      const page = await got(url, { headers, timeout: { request: 15000 }, retry: { limit: 2 } }).text();
      const $ = load(page);
      const root = $(".rich_media_content");
      root.find("br,p,section,li,h1,h2,h3,h4").each((_, element) => $(element).append("\n"));
      const text = root.text()
        .replace(/\u00a0/g, " ")
        .replace(/[ \t]+/g, " ")
        .replace(/\n\s*\n+/g, "\n")
        .trim();
      const title = $("#activity-name").text().trim() || $("title").text().trim();
      const source = $("#js_name").text().trim();
      if (!text) throw new Error("empty article body");
      output.push({ id, url, title, source, text });
      console.log(`${id}\t${text.length}`);
    } catch (error) {
      output.push({ id, url, error: error.message });
      console.error(`${id}\tERROR\t${error.message}`);
    }
    await sleep(250);
  }
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
