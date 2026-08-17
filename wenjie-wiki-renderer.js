/* ============================================================
   wenjie-wiki-renderer.js · Wiki → HTML 渲染器
   妈妈改 Wiki (Markdown) → push → HTML 自动显示新内容

   用法：
   <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
   <script src="wenjie-wiki-renderer.js"></script>
   <script>WikiRenderer.init();</script>
   ============================================================ */
(function () {
  'use strict';

  const GH_BASE = 'https://raw.githubusercontent.com/SherryXieLi/wenjie-plan/main/';

  // ============================================================
  // 工具函数
  // ============================================================

  async function fetchMD(path) {
    const url = GH_BASE + path;
    const response = await fetch(url + '?_t=' + Date.now());  // cache buster
    if (!response.ok) throw new Error('Wiki not found: ' + path);
    return await response.text();
  }

  // 提取 ## 段落
  function extractSections(md) {
    const lines = md.split('\n');
    const titleLine = lines[0].startsWith('# ') ? lines[0].slice(2).trim() : '';
    const sections = [];
    let current = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.startsWith('## ')) {
        if (current) sections.push(current);
        current = { heading: line.slice(3).trim(), body: [] };
      } else if (current) {
        current.body.push(line);
      }
    }
    if (current) sections.push(current);
    return { title: titleLine, sections };
  }

  // 配置 marked
  if (typeof marked !== 'undefined') {
    marked.setOptions({
      gfm: true,
      breaks: false,
      headerIds: false,
      mangle: false
    });
  }

  function md(text) {
    if (typeof marked === 'undefined') return escapeHtml(text);
    return marked.parse(text);
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  // ============================================================
  // 渲染器：每日计划
  // ============================================================
  async function renderDailyPlan(date) {
    const mdText = await fetchMD(`wiki/plans/daily/${date}.md`);
    const { title, sections } = extractSections(mdText);

    let html = '';
    sections.forEach(sec => {
      const body = md(sec.body.join('\n'));
      html += `
        <section class="wiki-section">
          <h2>${escapeHtml(sec.heading)}</h2>
          <div class="wiki-body">${body}</div>
        </section>
      `;
    });

    return { title, html, raw: mdText };
  }

  // ============================================================
  // 渲染器：通用 Wiki（任意 .md 文件）
  // ============================================================
  async function renderWikiDoc(path) {
    const mdText = await fetchMD(path);
    const html = md(mdText);
    return { html, raw: mdText };
  }

  // ============================================================
  // 暴露 API
  // ============================================================
  window.WikiRenderer = {
    renderDailyPlan,
    renderWikiDoc,
    fetchMD,
    extractSections,
    md
  };
})();
