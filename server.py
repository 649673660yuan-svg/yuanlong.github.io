from flask import Flask, jsonify
from pathlib import Path
import json
import re
import html
import os

app = Flask(__name__)
ROOT = Path(".").resolve()


def escape_html(value: str) -> str:
    return html.escape(value, quote=True)


def parse_inline(text: str) -> str:
    content = escape_html(text)
    content = re.sub(r"`([^`]+)`", r"<code>\1</code>", content)
    content = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", content)
    content = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r"<a href=\"\2\" target=\"_blank\" rel=\"noreferrer\">\1</a>",
        content,
    )
    return content


def markdown_to_html(markdown: str) -> str:
    lines = markdown.replace("\r\n", "\n").split("\n")
    html_lines = []
    in_code = False
    in_list = False

    for line in lines:
        if line.startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                html_lines.append("<pre><code>")
                in_code = True
            continue

        if in_code:
            html_lines.append(f"{escape_html(line)}\n")
            continue

        if re.match(r"^\s*-\s+", line):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{parse_inline(re.sub(r'^\s*-\s+', '', line))}</li>")
            continue

        if in_list:
            html_lines.append("</ul>")
            in_list = False

        if line.startswith("# "):
            html_lines.append(f"<h1>{parse_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{parse_inline(line[3:])}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{parse_inline(line[4:])}</h3>")
        elif line.strip():
            html_lines.append(f"<p>{parse_inline(line)}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def load_posts() -> list:
    posts_path = ROOT / "posts.json"
    if not posts_path.exists():
        raise FileNotFoundError("posts.json not found")
    posts = json.loads(posts_path.read_text(encoding="utf-8"))
    return sorted(posts, key=lambda item: item.get("date", ""), reverse=True)


def find_post(slug: str, posts: list):
    for post in posts:
        if post.get("slug") == slug:
            return post
    return None


@app.route("/api/posts")
def api_posts():
    try:
        posts = load_posts()
        return jsonify(posts)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/post/<slug>")
def api_post(slug: str):
    try:
        posts = load_posts()
        post = find_post(slug, posts)
        if post is None:
            return {"error": "Post not found"}, 404

        file_path = ROOT / post.get("file", "")
        if not file_path.exists() or not file_path.is_file():
            return {"error": "Article file not found"}, 404

        markdown = file_path.read_text(encoding="utf-8")
        html_body = markdown_to_html(markdown)
        html_response = f"<p class=\"meta\">{escape_html(post.get('date', ''))} · {' / '.join(escape_html(tag) for tag in post.get('tags', []))}</p>\n{html_body}"
        return html_response, 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as exc:
        return {"error": str(exc)}, 500


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    if path == "":
        file_name = "index.html"
    else:
        file_name = path

    file_path = ROOT / file_name

    if not file_path.exists() or not file_path.is_file():
        return "Not found", 404

    try:
        content = file_path.read_bytes()
        if file_name.endswith(".html"):
            mime_type = "text/html; charset=utf-8"
        elif file_name.endswith(".css"):
            mime_type = "text/css; charset=utf-8"
        elif file_name.endswith(".js"):
            mime_type = "text/javascript; charset=utf-8"
        elif file_name.endswith(".json"):
            mime_type = "application/json; charset=utf-8"
        elif file_name.endswith(".md"):
            mime_type = "text/markdown; charset=utf-8"
        else:
            mime_type = "application/octet-stream"

        return content, 200, {"Content-Type": mime_type}
    except Exception as exc:
        return f"Error: {exc}", 500


if __name__ == "__main__":
    print("Python backend running at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
