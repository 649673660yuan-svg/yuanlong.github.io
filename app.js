const state = {
  posts: [],
  activeTag: "全部",
  query: "",
  selectedSlug: "",
};

const postList = document.querySelector("#postList");
const tagFilter = document.querySelector("#tagFilter");
const searchInput = document.querySelector("#searchInput");
const reader = document.querySelector("#reader");

const escapeHtml = (value) =>
  value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const formatDate = (date) =>
  new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(`${date}T00:00:00`));

function parseInline(text) {
  return escapeHtml(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}

function markdownToHtml(markdown) {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  const html = [];
  let inCode = false;
  let inList = false;

  for (const line of lines) {
    if (line.startsWith("```")) {
      if (inCode) {
        html.push("</code></pre>");
        inCode = false;
      } else {
        html.push("<pre><code>");
        inCode = true;
      }
      continue;
    }

    if (inCode) {
      html.push(`${escapeHtml(line)}\n`);
      continue;
    }

    if (/^\s*-\s+/.test(line)) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${parseInline(line.replace(/^\s*-\s+/, ""))}</li>`);
      continue;
    }

    if (inList) {
      html.push("</ul>");
      inList = false;
    }

    if (line.startsWith("# ")) {
      html.push(`<h1>${parseInline(line.slice(2))}</h1>`);
    } else if (line.startsWith("## ")) {
      html.push(`<h2>${parseInline(line.slice(3))}</h2>`);
    } else if (line.startsWith("### ")) {
      html.push(`<h3>${parseInline(line.slice(4))}</h3>`);
    } else if (line.trim()) {
      html.push(`<p>${parseInline(line)}</p>`);
    }
  }

  if (inList) {
    html.push("</ul>");
  }

  return html.join("\n");
}

function getFilteredPosts() {
  const query = state.query.trim().toLowerCase();

  return state.posts.filter((post) => {
    const matchesTag = state.activeTag === "全部" || post.tags.includes(state.activeTag);
    const haystack = [post.title, post.summary, post.date, ...post.tags].join(" ").toLowerCase();
    const matchesQuery = !query || haystack.includes(query);
    return matchesTag && matchesQuery;
  });
}

function renderTags() {
  const tags = ["全部", ...new Set(state.posts.flatMap((post) => post.tags))];
  tagFilter.innerHTML = tags
    .map(
      (tag) =>
        `<button class="tag-button ${tag === state.activeTag ? "active" : ""}" data-tag="${tag}">${tag}</button>`,
    )
    .join("");
}

function renderPostList() {
  const posts = getFilteredPosts();

  if (!posts.length) {
    postList.innerHTML = '<div class="post-card"><h3>没有找到文章</h3><p>换个关键词或标签试试。</p></div>';
    return;
  }

  postList.innerHTML = posts
    .map(
      (post) => `
        <button class="post-card ${post.slug === state.selectedSlug ? "active" : ""}" data-slug="${post.slug}">
          <time>${formatDate(post.date)}</time>
          <h3>${post.title}</h3>
          <p>${post.summary}</p>
          <span class="tag-row">
            ${post.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}
          </span>
        </button>
      `,
    )
    .join("");
}

async function selectPost(slug) {
  const post = state.posts.find((item) => item.slug === slug);
  if (!post) return;

  state.selectedSlug = slug;
  renderPostList();

  reader.innerHTML = `
    <p class="eyebrow">Loading</p>
    <h3>正在加载文章...</h3>
  `;

  const response = await fetch(post.file);
  const markdown = await response.text();

  reader.innerHTML = `
    <p class="meta">${formatDate(post.date)} · ${post.tags.join(" / ")}</p>
    ${markdownToHtml(markdown)}
  `;
}

async function init() {
  const response = await fetch("posts.json");
  const posts = await response.json();
  state.posts = posts.sort((a, b) => b.date.localeCompare(a.date));

  renderTags();
  renderPostList();

  if (state.posts[0]) {
    selectPost(state.posts[0].slug);
  }
}

tagFilter.addEventListener("click", (event) => {
  const button = event.target.closest("[data-tag]");
  if (!button) return;

  state.activeTag = button.dataset.tag;
  renderTags();
  renderPostList();
});

postList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-slug]");
  if (!button) return;

  selectPost(button.dataset.slug);
});

searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  renderPostList();
});

init().catch((error) => {
  reader.innerHTML = `
    <div class="empty-state">
      <p class="eyebrow">Error</p>
      <h3>文章加载失败</h3>
      <p>${escapeHtml(error.message)}</p>
    </div>
  `;
});
