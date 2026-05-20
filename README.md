# 个人技术分享博客

这是一个适合部署到 GitHub Pages 的静态博客。它不需要 Python、Java、Node 后台；线上只依赖 HTML、CSS、JavaScript、`posts.json` 和 Markdown 文章文件。

## 为什么不用 Python 或 Java 后台

GitHub Pages 只能托管静态文件，不会运行服务器程序。所以：

- `server.py` 不会在线上执行
- Java 后台也不会在线上执行
- 最合适的方案是静态前端读取 `posts.json` 和 `posts/*.md`

本地预览时可以用一个小静态服务，线上 GitHub Pages 会直接托管这些文件。

## 本地预览

在项目目录运行：

```powershell
node dev-server.mjs
```

然后访问：

```text
http://localhost:8000
```

## 写一篇新文章

1. 在 `posts` 文件夹中新建一个 Markdown 文件，例如：

```text
posts/2026-05-20-react-notes.md
```

2. 写文章内容：

```md
# React 状态管理笔记

## 背景

今天学习了 React 状态管理。

## 收获

- 状态要尽量靠近使用它的组件
- 复杂状态可以考虑 reducer
```

3. 在 `posts.json` 里新增文章信息：

```json
{
  "slug": "2026-05-20-react-notes",
  "title": "React 状态管理笔记",
  "date": "2026-05-20",
  "summary": "记录今天对 React 状态管理的一些理解。",
  "tags": ["React", "前端", "日记"],
  "file": "posts/2026-05-20-react-notes.md"
}
```

## 发布

```powershell
git add .
git commit -m "Add new post"
git push
```

推送后 GitHub Actions 会自动部署到 GitHub Pages。
