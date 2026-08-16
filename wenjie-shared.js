/* ============================================================
   wenjie-shared.js · 共享导航 + 页脚 + Last Updated
   自动从当前页面文件名推断页面 ID，无需手动配置
   ============================================================ */
(function () {
  'use strict';

  // ---- 页面配置（自动从 filename 推断）----
  const FILENAME = location.pathname.split('/').pop() || 'index.html';
  const PAGE_ID = FILENAME.replace('wenjie-', '').replace('.html', '');

  // ---- 全局导航 ----
  const NAV_ITEMS = [
    { id: 'daily',     href: 'wenjie-daily-plan.html',        label: '📅 每日计划' },
    { id: 'garden',    href: 'wenjie-growth-garden.html',     label: '🌱 成长花园' },
    { id: 'overview',  href: 'wenjie-master-overview.html',   label: '🗺 6年总览' },
    { id: 'progress',  href: 'wenjie-progress-dashboard.html',label: '📊 进度' },
    { id: 'readiness', href: 'wenjie-school-readiness.html',  label: '🏫 入学' },
    { id: 'cca',       href: 'wenjie-cca-tracker.html',       label: '🎹 CCA' }
  ];

  // ---- 页面标题（top bar crumb）----
  const PAGE_TITLES = {
    'daily-plan':        '文杰 · 每日学习内容',
    'growth-garden':     '文杰的成长花园',
    'master-overview':   '文杰 · 6 年全景速览',
    'progress-dashboard':'文杰 · 学习进度仪表盘',
    'school-readiness':  '文杰 · 入学准备度',
    'cca-tracker':       '文杰 · CCA 进度追踪',
    '':                  '文杰学习计划'
  };

  const PAGE_PHASE = {
    'daily-plan':        'Phase 1 · W01 · 8 月 · v4.3',
    'master-overview':   '6 年规划 · 2026-2032',
    'progress-dashboard':'每周更新 · 数据驱动',
    'school-readiness':  'Phase 1 · W01 · 8 月',
    'cca-tracker':       '🏊 Swimming + 🎹 Piano · DSA 准备',
    'growth-garden':     '文杰的成长花园',
    '':                  ''
  };

  // ---- 渲染顶部导航 ----
  function renderTopBar() {
    const placeholders = document.querySelectorAll('[data-shared="top-bar"]');
    placeholders.forEach(function (el) {
      const navHTML = NAV_ITEMS.map(function (item) {
        const isCurrent = item.id === PAGE_ID;
        const cls = isCurrent ? 'current' : '';
        return '<a href="' + item.href + '" class="' + cls + '">' + item.label + '</a>';
      }).join('');

      el.innerHTML =
        '<div class="top-bar-inner">' +
          '<div class="crumb">' +
            '<span class="dot"></span>' +
            '<a href="index.html" style="color: var(--ink); text-decoration: none;"><strong>' + (PAGE_TITLES[PAGE_ID] || '文杰') + '</strong></a>' +
            (PAGE_PHASE[PAGE_ID] ? '<span>· ' + PAGE_PHASE[PAGE_ID] + '</span>' : '') +
          '</div>' +
          '<nav class="top-nav">' + navHTML + '</nav>' +
        '</div>';
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
      renderFooter();
    });
  } else {
    injectFonts();
    renderTopBar();
    renderFooter();
  }
})();