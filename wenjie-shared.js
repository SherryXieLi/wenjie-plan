/* ============================================================
   wenjie-shared.js · 共享导航 + 页脚 + Last Updated
   自动从当前页面文件名推断页面 ID，无需手动配置
   ============================================================ */
(function () {
  'use strict';

  // ---- 页面配置（自动从 filename 推断）----
  const FILENAME = location.pathname.split('/').pop() || 'index.html';
  const PAGE_ID = FILENAME.replace('wenjie-', '').replace('.html', '');

  // ---- 全局导航 + 层级标记 ----
  const NAV_ITEMS = [
    { id: 'plan',     href: 'wenjie-plan.html',              label: '🗺 6年规划', layer: '战略层' },
    { id: 'progress', href: 'wenjie-progress.html',          label: '📊 进度 + CCA', layer: '评估层' },
    { id: 'daily',    href: 'wenjie-daily-plan.html',        label: '📅 每日计划', layer: '操作层' },
    { id: 'academy',  href: 'wenjie-growth-garden.html',     label: '🦸 英雄学院', layer: '娃看版' }
  ];

  // ---- 页面标题（top bar crumb）----
  const PAGE_TITLES = {
    'plan':              '文杰 · 6 年规划 + 入学评分',
    'progress':          '文杰 · 进度 + CCA',
    'daily-plan':        '文杰 · 每日学习内容',
    'growth-garden':     '文杰的英雄学院',
    '':                  '文杰学习计划'
  };

  const PAGE_PHASE = {
    'plan':              '6 年规划 · 2026-2032',
    'progress':          '进度追踪 + CCA',
    'daily-plan':        'Phase 1 · W01 · 8 月 · v6',
    'growth-garden':     '奥特曼英雄学院',
    '':                  ''
  };

  // ---- 渲染顶部导航 ----
  function renderTopBar() {
    const placeholders = document.querySelectorAll('[data-shared="top-bar"]');
    placeholders.forEach(function (el) {
      const navHTML = NAV_ITEMS.map(function (item) {
        const isCurrent = item.id === PAGE_ID;
        const cls = isCurrent ? 'current' : '';
        return '<a href="' + item.href + '" class="' + cls + '" data-layer="' + item.layer + '">' + item.label + '</a>';
      }).join('');

      el.innerHTML =
        '<div class="top-bar-inner">' +
          '<div class="crumb">' +
            '<span class="dot"></span>' +
            '<a href="index.html" style="color: var(--ink); text-decoration: none;"><strong>' + (PAGE_TITLES[PAGE_ID] || '文杰') + '</strong></a>' +
            (PAGE_PHASE[PAGE_ID] ? '<span>· ' + PAGE_PHASE[PAGE_ID] + '</span>' : '') +
            '<button class="hamburger" aria-label="菜单">☰ 导航</button>' +
          '</div>' +
          '<nav class="top-nav">' + navHTML + '</nav>' +
        '</div>';

      // 绑定汉堡菜单点击事件
      const hamburger = el.querySelector('.hamburger');
      const nav = el.querySelector('.top-nav');
      const inner = el.querySelector('.top-bar-inner');
      if (hamburger && nav) {
        hamburger.addEventListener('click', function (e) {
          e.stopPropagation();
          nav.classList.toggle('open');
          hamburger.classList.toggle('open');
          inner.classList.toggle('collapsed');
        });
      }
    });
  }

  // ---- 渲染面包屑 ----
  function renderBreadcrumb() {
    const placeholders = document.querySelectorAll('[data-shared="breadcrumb"]');
    placeholders.forEach(function (el) {
      const current = NAV_ITEMS.find(function (item) { return item.id === PAGE_ID; });
      if (!current) return;
      el.innerHTML =
        '<a href="index.html">文杰学习计划</a>' +
        '<span class="sep">›</span>' +
        '<span class="current">' + current.label + ' <small>· ' + current.layer + '</small></span>';
    });
  }

  // ---- 渲染页脚 ----
  function renderFooter() {
    const placeholders = document.querySelectorAll('[data-shared="footer"]');
    placeholders.forEach(function (el) {
      const lastUpdated = el.getAttribute('data-updated') || '2026-08-16';
      el.classList.add('shared-footer');
      el.innerHTML =
        '<div class="footer-inner">' +
          '<div class="meta">' +
            '<a href="https://github.com/SherryXieLi/wenjie-plan">📂 GitHub</a>' +
            '<a href="wiki/index.md">📚 Wiki</a>' +
            '<a href="https://github.com/SherryXieLi/wenjie-plan/blob/main/' + FILENAME + '">✏️ Edit on GitHub</a>' +
            '<a href="javascript:window.print()">🖨 打印 / PDF</a>' +
          '</div>' +
          '<div class="updated">' +
            'Last updated: <strong>' + lastUpdated + '</strong> · SherryXieLi · Singapore' +
          '</div>' +
        '</div>';
    });
  }

  // ---- 自动注入 fonts（避免每个页面重复）----
  function injectFonts() {
    if (document.querySelector('link[href*="fonts.googleapis"]')) return;
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;600;700&display=swap';
    document.head.appendChild(link);
  }

  // ---- 启动 ----
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      injectFonts();
      renderTopBar();
      renderBreadcrumb();
      renderFooter();
    });
  } else {
    injectFonts();
    renderTopBar();
    renderBreadcrumb();
    renderFooter();
  }
})();