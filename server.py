from flask import Flask, jsonify
from pathlib import Path
import html
import json
import re

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent


def escape_html(value: str) -> str:
    return html.escape(str(value), quote=True)


def parse_inline(text: str) -> str:
    content = escape_html(text)
    content = re.sub(r"`([^`]+)`", r"<code>\1</code>", content)
    content = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", content)
    content = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',
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
            html_lines.append("</code></pre>" if in_code else "<pre><code>")
            in_code = not in_code
            continue

        if in_code:
            html_lines.append(f"{escape_html(line)}\n")
            continue

        if re.match(r"^\s*-\s+", line):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = re.sub(r"^\s*-\s+", "", line)
            html_lines.append(f"<li>{parse_inline(item)}</li>")
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
    posts = json.loads(posts_path.read_text(encoding="utf-8"))
    return sorted(posts, key=lambda item: item.get("date", ""), reverse=True)


def find_post(slug: str, posts: list):
    return next((post for post in posts if post.get("slug") == slug), None)


@app.route("/api/posts")
def api_posts():
    try:
        return jsonify(load_posts())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/post/<slug>")
def api_post(slug: str):
    try:
        posts = load_posts()
        post = find_post(slug, posts)
        if post is None:
            return jsonify({"error": "Post not found"}), 404

        relative_file = post.get("file", "")
        file_path = (ROOT / relative_file).resolve()
        if not str(file_path).startswith(str(ROOT)) or not file_path.is_file():
            return jsonify({"error": "Article file not found"}), 404

        markdown = file_path.read_text(encoding="utf-8")
        tags = " / ".join(escape_html(tag) for tag in post.get("tags", []))
        html_body = markdown_to_html(markdown)
        html_response = (
            f'<p class="meta">{escape_html(post.get("date", ""))} · {tags}</p>\n'
            f"{html_body}"
        )
        return html_response, 200, {"Content-Type": "text/html; charset=utf-8"}
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    file_name = "index.html" if path == "" else path
    file_path = (ROOT / file_name).resolve()

    if not str(file_path).startswith(str(ROOT)) or not file_path.is_file():
        return "Not found", 404

    mime_types = {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".md": "text/markdown; charset=utf-8",
    }
    mime_type = mime_types.get(file_path.suffix, "application/octet-stream")
    return file_path.read_bytes(), 200, {"Content-Type": mime_type}


if __name__ == "__main__":
    print("Python backend running at http://localhost:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)
