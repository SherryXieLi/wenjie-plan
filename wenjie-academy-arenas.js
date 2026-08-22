/* ============================================================
   wenjie-academy-arenas.js · 怪兽战场 modal
   娃版：极简（emoji + 短词）
   家长版：详细（任务详情 + 里程碑 + 奖励）
   ============================================================ */
(function () {
  'use strict';

  // 5 大战场数据
  const ARENA_DATA = {
    math: {
      emoji: '🔴',
      boss: '加法怪兽',
      boss_lv: 6,
      progress: '__MATH_PROGRESS__',
      // 娃版：短词 + emoji
      kidMissions: [
        { icon: '🔢', text: '珠算 10 题' },
        { icon: '⚡', text: '心算 7 题' },
        { icon: '📖', text: '做练习册' },
        { icon: '🔄', text: '复盘错题' },
      ],
      kidRewards: ['⭐ +15 智力', '⚡ +15 速度'],
      kidGoal: '算术全做完',
      // 家长版：详细
      missions: [
        '每天 19:15-19:25 做 10 道珠算（< 10 分钟）',
        '每天 19:25-19:35 做 7 道心算（< 3 分钟）',
        '每天 19:40-19:55 做 Intensive Maths 4-6 页',
        '每周日复盘本周错题怪兽',
      ],
      milestones: [
        { text: 'K2 末 · 心算 6 级 90%+', status: 'active' },
        { text: 'P1 · 珠算 8 级 · 加减法精通', status: 'future' },
        { text: 'P2 · 乘法口诀 + 简单应用题', status: 'future' },
        { text: 'P3 · 3-4 位加减法 + 应用题', status: 'future' },
      ],
      rewards: [
        { stat: '🧠 INTEL', value: '+15 / 天' },
        { stat: '⚡ SPEED', value: '+15 / 天' },
      ],
      weakness: '⚡ 闪电拳 · 集中力'
    },
    english: {
      emoji: '🔵',
      boss: '拼写怪兽',
      boss_lv: 4,
      progress: '__ENGLISH_PROGRESS__',
      kidMissions: [
        { icon: '📚', text: 'KAK 10 min' },
        { icon: '📝', text: 'One-stop 15 min' },
        { icon: '📖', text: '牛津树 3 本' },
        { icon: '🎧', text: '复习课' },
      ],
      kidRewards: ['⭐ +15 智力'],
      kidGoal: 'KAK Grade 2 完成',
      missions: [
        '每天 19:25-19:35 KAK Vowel Sounds（10 min）',
        '每天 19:40-19:55 One-stop English P1（15 min）',
        '每周读 3 本牛津树故事书（Level 1-3）',
        '每周日听 KAK 复习课',
      ],
      milestones: [
        { text: 'K2 末 · KAK Grade 1 完成', status: 'active' },
        { text: 'P1 · KAK Grade 2 + 词汇 500', status: 'future' },
        { text: 'P2 · KAK Grade 3 + 简单阅读', status: 'future' },
        { text: 'P3 · KAK Grade 4 + 流利阅读', status: 'future' },
      ],
      rewards: [
        { stat: '🧠 INTEL', value: '+15 / 天' },
        { stat: '⚡ SPEED', value: '+5 / 天' },
      ],
      weakness: '📚 词汇书 · 多读'
    },
    chinese: {
      emoji: '🟠',
      boss: '识字怪兽',
      boss_lv: 5,
      progress: '__CHINESE_PROGRESS__',
      kidMissions: [
        { icon: '✍️', text: '写 1 个字' },
        { icon: '📗', text: '快乐练习 2.0' },
        { icon: '📚', text: '亲子共读' },
        { icon: '📝', text: '练新字' },
      ],
      kidRewards: ['⭐ +10 智力', '💪 +5 力量'],
      kidGoal: '识字 500 字',
      missions: [
        '每天 8:15-8:30 写汉字 1 个（奶奶）',
        '每天 20:00-20:15 快乐练习 2.0（15 min）',
        '每天 20:40-21:00 亲子共读 20 min（妈妈）',
        '每周日练新字 5 个 + 复习 10 个',
      ],
      milestones: [
        { text: 'K2 末 · 识字 200 字', status: 'active' },
        { text: 'P1 · 识字 500 + 拼音基础', status: 'future' },
        { text: 'P2 · 识字 1000 + 自主阅读', status: 'future' },
        { text: 'P3 · 识字 1500 + 看图写话', status: 'future' },
      ],
      rewards: [
        { stat: '🧠 INTEL', value: '+10 / 天' },
        { stat: '💪 POWER', value: '+5 / 天' },
      ],
      weakness: '🖌️ 毛笔 · 描红'
    },
    piano: {
      emoji: '🟡',
      boss: '节拍怪兽',
      boss_lv: 3,
      progress: '__PIANO_PROGRESS__',
      kidMissions: [
        { icon: '🎹', text: '练琴 20 min' },
        { icon: '👨‍🏫', text: '钢琴课' },
        { icon: '🎵', text: '复习 Trinity 1' },
        { icon: '🎶', text: '练 Trinity 3' },
      ],
      kidRewards: ['💪 +5 力量', '⭐ +10 智力'],
      kidGoal: 'Trinity 3 通过',
      missions: [
        '每天 17:15-17:35 练琴 20 分钟',
        '每周 1 次钢琴课（45 min）',
        '每天复习 Trinity 1 曲库 4 首',
        '每天练 Trinity 3 备考曲 4 首（Ballade, Rain, Between the Fingers, Wild）',
      ],
      milestones: [
        { text: 'K2 · Trinity 1 ✅ Distinct', status: 'done' },
        { text: 'P1 · Trinity 2 跳过 → Trinity 3 准备', status: 'active' },
        { text: 'P2 · Trinity 3 + SPAF 1', status: 'future' },
        { text: 'P3 · Trinity 4 + SPAF 2', status: 'future' },
        { text: 'P6 · Trinity 7 + DSA 申请', status: 'future' },
      ],
      rewards: [
        { stat: '💪 POWER', value: '+5 / 天' },
        { stat: '🧠 INTEL', value: '+10 / 天' },
      ],
      weakness: '🎵 音符 · 节拍器'
    },
    reading: {
      emoji: '🟢',
      boss: '故事怪兽',
      boss_lv: 4,
      progress: '__READING_PROGRESS__',
      kidMissions: [
        { icon: '📚', text: '亲子共读 20 min' },
        { icon: '🐂', text: '牛津树 3 本' },
        { icon: '🗣', text: '讲给奶奶听' },
        { icon: '📕', text: '新章节书' },
      ],
      kidRewards: ['⭐ +10 智力', '💪 +5 力量'],
      kidGoal: '独立阅读 Level 3',
      missions: [
        '每天 20:40-21:00 亲子共读 20 min',
        '每周 3 本牛津树故事',
        '每周 1 次复述故事（讲给奶奶听）',
        '每月 1 本新的章节书',
      ],
      milestones: [
        { text: 'K2 末 · 看图讲故事 5 min', status: 'active' },
        { text: 'P1 · 独立阅读 Level 3', status: 'future' },
        { text: 'P2 · 章节书入门（Roald Dahl）', status: 'future' },
        { text: 'P3 · 阅读速度 200 wpm', status: 'future' },
      ],
      rewards: [
        { stat: '🧠 INTEL', value: '+10 / 天' },
        { stat: '💪 POWER', value: '+5 / 天' },
      ],
      weakness: '📖 故事书 · 想象力'
    }
  };

  // 打开 modal
  function openArenaModal(arenaKey) {
    const arena = ARENA_DATA[arenaKey];
    if (!arena) return;

    const modal = document.getElementById('arena-modal');
    const content = document.getElementById('arena-modal-content');

    // 检查当前模式
    const isParentMode = document.body.classList.contains('parent-mode');

    if (isParentMode) {
      // ===== 家长版（详细） =====
      const milestonesHtml = arena.milestones.map(m => {
        const icon = m.status === 'done' ? '✅' : m.status === 'active' ? '🔄' : '⏳';
        return `<li class="${m.status}">${icon} ${m.text}</li>`;
      }).join('');

      const missionsHtml = arena.missions.map(m => `<li>${m}</li>`).join('');

      const rewardsHtml = arena.rewards.map(r =>
        `<div class="arena-modal-stat"><span class="label">${r.stat}</span><span class="value">${r.value}</span></div>`
      ).join('');

      content.innerHTML = `
        <button class="arena-modal-close" aria-label="关闭">✕</button>
        <div style="font-size: 48px; text-align: center; margin-bottom: 8px;">${arena.emoji}</div>
        <h2 class="arena-modal-title">${arena.boss}</h2>
        <div class="arena-modal-boss">Lv ${arena.boss_lv} · ${arena.progress}</div>

        <div class="arena-section">
          <h3>⚔️ 今日任务 · Today's Missions</h3>
          <ul class="mission-list">${missionsHtml}</ul>
        </div>

        <div class="arena-section">
          <h3>🏆 击败奖励 · Power Up Rewards</h3>
          ${rewardsHtml}
          <div style="margin-top: 8px; padding: 8px; background: rgba(255,215,0,0.1); border-radius: 6px; font-size: 12px;">
            <strong style="color: #ffd700;">弱点 Weakness：</strong> ${arena.weakness}
          </div>
        </div>

        <div class="arena-section">
          <h3>📜 等级里程碑 · Level Milestones</h3>
          <ul class="milestone-list">${milestonesHtml}</ul>
        </div>
      `;
    } else {
      // ===== 娃版（极简） =====
      const missionsHtml = arena.kidMissions.map(m =>
        `<div class="kid-mission-item">
          <span class="kid-mission-icon">${m.icon}</span>
          <span class="kid-mission-text">${m.text}</span>
        </div>`
      ).join('');

      const rewardsHtml = arena.kidRewards.map(r =>
        `<div class="kid-reward">${r}</div>`
      ).join('');

      content.innerHTML = `
        <button class="arena-modal-close" aria-label="关闭">✕</button>
        <div style="font-size: 80px; text-align: center; margin: 8px 0 4px;">${arena.emoji}</div>
        <h2 class="arena-modal-title" style="font-size: 28px; margin-bottom: 4px;">${arena.boss}</h2>

        <div class="kid-goal">
          🎯 ${arena.kidGoal}
        </div>

        <div class="arena-section" style="margin-top: 16px;">
          <div style="font-size: 13px; color: #ffd700; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace;">
            ⚔️ 每天做
          </div>
          <div class="kid-mission-list">${missionsHtml}</div>
        </div>

        <div class="arena-section">
          <div style="font-size: 13px; color: #ffd700; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace;">
            🏆 打败后得到
          </div>
          <div class="kid-reward-list">${rewardsHtml}</div>
        </div>
      `;
    }

    modal.classList.add('open');

    // 绑定关闭
    const closeBtn = content.querySelector('.arena-modal-close');
    const bg = modal.querySelector('.arena-modal-bg');
    if (closeBtn) closeBtn.onclick = () => modal.classList.remove('open');
    if (bg) bg.onclick = () => modal.classList.remove('open');
  }

  // 绑定 arena card 点击
  document.addEventListener('click', function (e) {
    const card = e.target.closest('.arena-card');
    if (!card) return;
    const arena = card.getAttribute('data-arena');
    if (arena) {
      openArenaModal(arena);
    }
  });

  // ESC 关闭
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      const modal = document.getElementById('arena-modal');
      if (modal) modal.classList.remove('open');
    }
  });
})();