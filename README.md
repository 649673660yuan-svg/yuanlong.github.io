# 个人技术分享博客

这是一个可以直接部署到 GitHub Pages 的静态博客。文章使用 Markdown 编写，适合每天更新技术日记、复盘、源码阅读笔记和项目经验。

## 本地预览

因为浏览器直接打开本地文件时可能限制 `fetch` 读取文章，建议在项目目录运行：

```powershell
node dev-server.mjs
```

然后访问：

```text
http://localhost:8000
```

## Python 后端预览

你也可以使用 Python 启动一个本地后端服务器：

```powershell
python server.py
```

然后访问：

```text
http://localhost:8000
```

这个后端会提供：

- `/api/posts`：返回 `posts.json` 中的文章目录
- `/api/post/<slug>`：读取 Markdown 文件并返回渲染后的 HTML 内容

这样就把网站的数据后端改成了 Python 实现。
## 写一篇新文章

1. 在 `posts` 文件夹中新建一个 Markdown 文件，例如 `posts/2026-05-20-react-notes.md`。
2. 在 `posts.json` 中新增文章信息：

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

3. 提交并推送到 GitHub。

## 部署到 GitHub Pages

1. 在 GitHub 创建一个仓库，例如 `tech-blog`。
2. 把这些文件推送到仓库的 `main` 分支。
3. 打开仓库的 `Settings`。
4. 进入 `Pages`。
5. Source 选择 `Deploy from a branch`。
6. Branch 选择 `main`，目录选择 `/root`。
7. 保存后等待 GitHub 生成访问地址。

## 推荐文章结构

```md
# 标题

## 背景

## 问题

## 排查过程

## 解决方案

## 今天的收获
```
