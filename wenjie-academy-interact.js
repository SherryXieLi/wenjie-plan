/* ============================================================
   wenjie-academy-interact.js · 任务完成互动
   ============================================================ */
(function () {
  'use strict';

  const STORAGE_KEY = 'wenjie-todays-tasks';

  function getTodayStr() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }

  function loadState() {
    try {
      const all = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      return all[getTodayStr()] || {};
    } catch (e) {
      return {};
    }
  }

  function saveState(state) {
    try {
      const all = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
      all[getTodayStr()] = state;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
    } catch (e) {}
  }

  function countTotal() {
    return document.querySelectorAll('.todays-task-card[data-task-id]').length;
  }

  function countDone(state) {
    return Object.values(state).filter(Boolean).length;
  }

  function updateUI() {
    const state = loadState();
    const total = countTotal();
    const done = countDone(state);

    // 更新每个按钮状态
    document.querySelectorAll('.task-done-btn').forEach((btn) => {
      const id = btn.getAttribute('data-task-id');
      if (state[id]) {
        btn.classList.add('checked');
        btn.textContent = '已打败';
      } else {
        btn.classList.remove('checked');
        btn.textContent = '⚔️ 打败它';
      }
      const card = btn.closest('.todays-task-card');
      if (card) {
        if (state[id]) card.classList.add('done');
        else card.classList.remove('done');
      }
    });

    // 显示/隐藏 "打败怪兽" 按钮
    const wrapper = document.getElementById('defeat-btn-wrapper');
    if (wrapper) {
      wrapper.style.display = (done === total && total > 0) ? 'block' : 'none';
    }
  }

  function showCelebration() {
    const overlay = document.getElementById('celebration-overlay');
    if (overlay) {
      overlay.classList.add('show');
      // 震动效果（如果支持）
      if (navigator.vibrate) {
        navigator.vibrate([100, 50, 100, 50, 200]);
      }
    }
  }

  function hideCelebration() {
    const overlay = document.getElementById('celebration-overlay');
    if (overlay) {
      overlay.classList.remove('show');
    }
  }

  // 初始化
  function init() {
    // 1. 给每个打败按钮加 click 事件
    document.querySelectorAll('.task-done-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const id = btn.getAttribute('data-task-id');
        const state = loadState();
        state[id] = !state[id];  // toggle
        saveState(state);
        updateUI();
      });
    });

    // 2. 打败怪兽按钮
    const defeatBtn = document.getElementById('defeat-monster-btn');
    if (defeatBtn) {
      defeatBtn.addEventListener('click', showCelebration);
    }

    // 3. 关闭按钮
    const closeBtn = document.getElementById('celebration-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', hideCelebration);
    }

    // 4. 点击覆盖层外部关闭
    const overlay = document.getElementById('celebration-overlay');
    if (overlay) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) hideCelebration();
      });
    }

    // 5. 恢复 UI 状态
    updateUI();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();