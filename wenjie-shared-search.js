/* ============================================================
   wenjie-shared-search.js · Cmd+K 全站搜索
   索引 6 个页面 + Wiki 的关键词
   ============================================================ */
(function () {
  'use strict';

  // ---- 预定义搜索索引（关键词 → 目标页面）----
  const SEARCH_INDEX = [
    // 每日计划
    { kw: '每日计划|每天|今天|today|任务清单', page: 'wenjie-daily-plan.html', section: '#hero' },
    { kw: '5:2:1|节奏|周一|周二|周三|周四|周五|周末', page: 'wenjie-daily-plan.html' },
    { kw: '珠算|心算|6级', page: 'wenjie-daily-plan.html' },
    { kw: 'Phonics|KAK|Vowel|Long E|双元音', page: 'wenjie-daily-plan.html' },
    { kw: 'Intensive Maths|数学练习册', page: 'wenjie-daily-plan.html' },
    { kw: 'One-stop English|英文练习册', page: 'wenjie-daily-plan.html' },
    { kw: '快乐练习2.0|中文练习册|描红', page: 'wenjie-daily-plan.html' },
    { kw: '钢琴|练琴|17:15', page: 'wenjie-daily-plan.html' },
    { kw: '项目日|Timed Reading|WPM', page: 'wenjie-daily-plan.html' },

    // 6 年总览
    { kw: '6年|全景|P1|P2|P3|P4|P5|P6|PSLE', page: 'wenjie-master-overview.html' },
    { kw: 'RI|Hwa Chong|Hwa Chong Institution|华侨中学', page: 'wenjie-master-overview.html' },
    { kw: 'IP|A-Level|Junior College', page: 'wenjie-master-overview.html' },
    { kw: '时间轴|规划|roadmap', page: 'wenjie-master-overview.html' },
    { kw: '预算|费用|cost', page: 'wenjie-master-overview.html' },

    // 进度仪表盘
    { kw: '进度|追踪|dashboard|仪表盘', page: 'wenjie-progress-dashboard.html' },
    { kw: '错题|pattern|pattern-|mistakes', page: 'wenjie-progress-dashboard.html' },
    { kw: '完成率|正确率|分数', page: 'wenjie-progress-dashboard.html' },
    { kw: 'Wiki|log|日志', page: 'wenjie-progress-dashboard.html' },

    // 入学评分
    { kw: '入学|readiness|P1标准|学前', page: 'wenjie-school-readiness.html' },
    { kw: '12维度|评估|评分|5分制', page: 'wenjie-school-readiness.html' },
    { kw: 'gap|差距|action items|改进', page: 'wenjie-school-readiness.html' },

    // CCA
    { kw: 'CCA|课外活动|兴趣班', page: 'wenjie-cca-tracker.html' },
    { kw: '钢琴|钢琴课|Piano', page: 'wenjie-cca-tracker.html' },
    { kw: '游泳|Swim|跆拳道|Taekwondo', page: 'wenjie-cca-tracker.html' },
    { kw: 'DSA|特长入学', page: 'wenjie-cca-tracker.html' },

    // 成长花园
    { kw: '成长花园|garden|5座岛|可视化', page: 'wenjie-growth-garden.html' },

    // Wiki 相关
    { kw: 'profile|目标|goals', page: 'wiki/index.md' },
    { kw: 'resources|资源|bought|购买', page: 'wiki/resources/bought.md' },
    { kw: 'mastery|掌握度|进度', page: 'wiki/subjects/english/mastery.md' },
    { kw: 'plans|计划|quarterly|weekly|daily', page: 'wiki/plans/quarterly.md' }
  ];

  // ---- 渲染搜索按钮 + 快捷键 ----
  function initSearch() {
    // 创建搜索按钮（top-bar 右侧）
    const topbarInner = document.querySelector('.top-bar-inner');
    if (topbarInner) {
      const btn = document.createElement('button');
      btn.className = 'search-btn';
      btn.innerHTML = '🔍 <kbd>⌘K</kbd>';
      btn.setAttribute('aria-label', '搜索');
      topbarInner.appendChild(btn);

      btn.addEventListener('click', openSearch);
    }

    // Cmd+K / Ctrl+K 快捷键
    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        openSearch();
      }
      if (e.key === 'Escape') closeSearch();
    });
  }

  // ---- 打开搜索模态 ----
  function openSearch() {
    let modal = document.getElementById('search-modal');
    if (!modal) {
      modal = createModal();
      document.body.appendChild(modal);
    }
    modal.style.display = 'flex';
    const input = modal.querySelector('input');
    if (input) {
      input.value = '';
      input.focus();
      showResults('');
    }
  }

  function closeSearch() {
    const modal = document.getElementById('search-modal');
    if (modal) modal.style.display = 'none';
  }

  function createModal() {
    const modal = document.createElement('div');
    modal.id = 'search-modal';
    modal.className = 'search-modal';
    modal.innerHTML =
      '<div class="search-overlay" onclick="document.getElementById(\'search-modal\').style.display=\'none\'"></div>' +
      '<div class="search-panel">' +
        '<div class="search-input-wrap">' +
          '<input type="text" placeholder="搜索6 个页面 + Wiki ... (Cmd+K 打开 / Esc 关闭)" />' +
          '<span class="search-hint">⏎ 跳转</span>' +
        '</div>' +
        '<div class="search-results"></div>' +
        '<div class="search-footer">' +
          '<span>🔍 ' + SEARCH_INDEX.length + ' 索引词</span>' +
          '<span>📚 跨 6 页 + Wiki 搜索</span>' +
        '</div>' +
      '</div>';

    const input = modal.querySelector('input');
    input.addEventListener('input', function (e) {
      showResults(e.target.value);
    });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        const first = modal.querySelector('.search-result-item');
        if (first) first.click();
      }
    });
    return modal;
  }

  function showResults(query) {
    const modal = document.getElementById('search-modal');
    if (!modal) return;
    const container = modal.querySelector('.search-results');

    if (!query || !query.trim()) {
      container.innerHTML =
        '<div class="search-empty">' +
          '<div style="font-size: 48px; margin-bottom: 12px;">🔍</div>' +
          '<div>输入关键词搜索 · 例如：<code>钢琴</code> <code>5:2:1</code> <code>RI</code> <code>入学</code></div>' +
        '</div>';
      return;
    }

    const q = query.toLowerCase();
    const matches = SEARCH_INDEX.filter(function (item) {
      return item.kw.toLowerCase().includes(q);
    });

    if (matches.length === 0) {
      container.innerHTML = '<div class="search-empty">没找到匹配的关键词。试 <code>钢琴</code>、<code>5:2:1</code>、<code>RI</code></div>';
      return;
    }

    // 去重（同一页多条合并）
    const byPage = {};
    matches.forEach(function (m) {
      if (!byPage[m.page]) byPage[m.page] = [];
      byPage[m.page].push(m);
    });

    let html = '';
    Object.keys(byPage).forEach(function (page) {
      const pageName = page.replace('wenjie-', '').replace('.html', '');
      html += '<div class="search-group">' +
                '<div class="search-group-title">' + pageName + '</div>';
      byPage[page].forEach(function (m, i) {
        const highlight = highlightMatch(m.kw, query);
        html += '<a href="' + (m.page) + (m.section || '') + '" class="search-result-item" onclick="document.getElementById(\'search-modal\').style.display=\'none\'">' +
                  '<span class="dot"></span>' +
                  '<span class="match">' + highlight + '</span>' +
                '</a>';
      });
      html += '</div>';
    });

    container.innerHTML = html;
  }

  function highlightMatch(text, query) {
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return text;
    return text.substring(0, idx) +
           '<strong>' + text.substring(idx, idx + query.length) + '</strong>' +
           text.substring(idx + query.length);
  }

  // ---- 启动 ----
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
  } else {
    initSearch();
  }
})();