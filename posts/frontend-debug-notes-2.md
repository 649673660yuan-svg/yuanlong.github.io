# 一次前端调试复盘 2

这篇是第二篇调试日记，用来确认静态博客在 GitHub Pages 上能正常读取文章列表、Markdown 文件和标签信息。

## 问题现象

页面提示文章加载失败，但首页样式能正常显示。说明 HTML、CSS 大概率已经加载，问题更可能出在 `posts.json` 或文章 Markdown 文件路径上。

## 排查路径

- 先检查 `posts.json` 是否是合法 JSON
- 再确认每篇文章的 `file` 路径是否真实存在
- 最后确认前端使用相对路径读取文件，而不是请求后端接口

## 解决方案

把博客改回最适合 GitHub Pages 的静态结构：前端直接读取 `posts.json`，再根据文章里的 `file` 字段读取 Markdown 文件。

```js
const response = await fetch("posts.json");
const posts = await response.json();
```

## 收获

GitHub Pages 适合静态博客。只要把文章索引和文章文件维护好，不需要额外后台，也能稳定发布和每日更新。
