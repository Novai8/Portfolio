/* Minimal zero-dependency static server for the 5Star Auto demo site.
   Usage: node server.js [port]   →   serves ./site with clean URLs. */
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "site");
const PORT = Number(process.argv[2] || process.env.PORT || 3000);

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
};

function send(res, code, body, type) {
  res.writeHead(code, {
    "Content-Type": type || "text/plain; charset=utf-8",
    "Cache-Control": "no-cache",
    "X-Frame-Options": "ALLOWALL",
  });
  res.end(body);
}

http
  .createServer((req, res) => {
    let p = decodeURIComponent(req.url.split("?")[0]);
    if (p.endsWith("/")) p += "index.html";
    let file = path.join(ROOT, path.normalize(p));
    if (!file.startsWith(ROOT)) return send(res, 403, "Forbidden");

    fs.stat(file, (err, st) => {
      if (!err && st.isDirectory()) file = path.join(file, "index.html");
      else if (err && !path.extname(file)) file = path.join(file, "index.html"); // clean URLs
      fs.readFile(file, (e, buf) => {
        if (e) {
          return fs.readFile(path.join(ROOT, "index.html"), (e2, home) =>
            e2 ? send(res, 404, "Not found") : send(res, 404, home, TYPES[".html"])
          );
        }
        send(res, 200, buf, TYPES[path.extname(file).toLowerCase()] || "application/octet-stream");
      });
    });
  })
  .listen(PORT, "0.0.0.0", () => console.log("5Star Auto demo running on http://0.0.0.0:" + PORT));
