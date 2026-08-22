/* ============================================================
   wenjie-academy-battle.js · 战斗回放动画
   ============================================================ */
(function () {
  'use strict';

  // 5 个战场的怪兽 + 颜色
  const BATTLES = [
    {
      arena: 'math',
      monster: '👹',
      monsterName: '加法怪兽',
      arenaName: '数学',
      defeated: __MATH_DEFEATED__  // 1 = 今天打败了, 0 = 没打败
    },
    {
      arena: 'english',
      monster: '🐙',
      monsterName: '拼写怪兽',
      arenaName: '英文',
      defeated: __ENGLISH_DEFEATED__
    },
    {
      arena: 'chinese',
      monster: '🦂',
      monsterName: '识字怪兽',
      arenaName: '中文',
      defeated: __CHINESE_DEFEATED__
    },
    {
      arena: 'piano',
      monster: '👾',
      monsterName: '节拍怪兽',
      arenaName: '钢琴',
      defeated: __PIANO_DEFEATED__
    },
    {
      arena: 'reading',
      monster: '🐲',
      monsterName: '故事怪兽',
      arenaName: '阅读',
      defeated: __READING_DEFEATED__
    }
  ];

  // 微型奥特曼（简化版头部 + 上半身）
  function ultramanSVG(animated) {
    const enterClass = animated ? 'anim-ultraman' : '';
    const punchClass = animated ? 'anim-punch' : '';
    const victoryClass = animated ? 'anim-victory' : '';
    return `
      <g transform="translate(0, 0)">
        <g class="${enterClass}">
          <g class="${punchClass}">
            <g class="${victoryClass}">
              <!-- 头冠 -->
              <path d="M 60 30 L 56 50 Q 55 53 57 54 L 63 54 Q 65 53 64 50 Z"
                    fill="#cc2020" stroke="#500000" stroke-width="0.5"/>
              <!-- 头盔 -->
              <ellipse cx="60" cy="60" rx="22" ry="25" fill="#dcdcdc" stroke="#202020" stroke-width="1"/>
              <!-- 大眼睛 -->
              <ellipse cx="51" cy="60" rx="7" ry="10" fill="#a0e0ff" stroke="#101010" stroke-width="0.8"/>
              <ellipse cx="69" cy="60" rx="7" ry="10" fill="#a0e0ff" stroke="#101010" stroke-width="0.8"/>
              <ellipse cx="52" cy="56" rx="2" ry="3" fill="#ffffff"/>
              <ellipse cx="70" cy="56" rx="2" ry="3" fill="#ffffff"/>
              <!-- 嘴 -->
              <path d="M 56 76 Q 60 79 64 76" stroke="#202020" stroke-width="1" fill="none"/>
              <!-- 脖子 -->
              <rect x="55" y="84" width="10" height="4" fill="#c0c0c0" stroke="#202020" stroke-width="0.5"/>
              <!-- 上身 -->
              <path d="M 35 130 L 35 95 Q 38 88 45 86 L 75 86 Q 82 88 85 95 L 85 130 Z"
                    fill="#c0c0c0" stroke="#202020" stroke-width="0.8"/>
              <!-- 紫色护甲 -->
              <path d="M 50 88 L 60 86 L 70 88 L 70 105 L 60 100 L 50 105 Z"
                    fill="#8040c0" stroke="#301050" stroke-width="0.5" opacity="0.85"/>
              <!-- 红色条纹 -->
              <rect x="37" y="95" width="3" height="35" fill="#cc2020"/>
              <rect x="80" y="95" width="3" height="35" fill="#cc2020"/>
              <!-- 浅蓝计时器 -->
              <circle cx="60" cy="98" r="6" fill="#202020"/>
              <circle cx="60" cy="98" r="4.5" fill="#40c0e0"/>
              <circle cx="60" cy="98" r="3" fill="#a0e0ff"/>
              <!-- 出拳的手臂 -->
              <ellipse cx="90" cy="105" rx="10" ry="4" fill="#c0c0c0" stroke="#202020" stroke-width="0.8"/>
            </g>
          </g>
        </g>
      </g>
    `;
  }

  function monsterSVG(monster, animated) {
    const enterClass = animated ? 'anim-monster' : '';
    const hitClass = animated ? 'anim-monster-hit' : '';
    return `
      <g transform="translate(0, 0)">
        <g class="${enterClass}">
          <g class="${hitClass}">
            <!-- 怪兽身体（粗壮 + 凶） -->
            <ellipse cx="180" cy="100" rx="30" ry="35" fill="#7a2828" stroke="#3a0808" stroke-width="1"/>
            <!-- 怪兽头 -->
            <circle cx="180" cy="80" r="22" fill="#9a3838" stroke="#3a0808" stroke-width="1"/>
            <!-- 怪兽眼睛（凶） -->
            <ellipse cx="172" cy="78" rx="4" ry="6" fill="#ffff00"/>
            <ellipse cx="188" cy="78" rx="4" ry="6" fill="#ffff00"/>
            <circle cx="172" cy="78" r="2" fill="#000"/>
            <circle cx="188" cy="78" r="2" fill="#000"/>
            <!-- 怪兽嘴 + 牙 -->
            <path d="M 168 90 L 192 90" stroke="#000" stroke-width="1.5"/>
            <path d="M 170 90 L 172 94 L 174 90 Z" fill="#fff"/>
            <path d="M 176 90 L 178 94 L 180 90 Z" fill="#fff"/>
            <path d="M 182 90 L 184 94 L 186 90 Z" fill="#fff"/>
            <!-- 怪兽 emoji 装饰 -->
            <text x="180" y="115" font-size="20" text-anchor="middle">${monster}</text>
            <!-- 怪兽脚 -->
            <rect x="165" y="130" width="8" height="15" fill="#5a1818" rx="2"/>
            <rect x="187" y="130" width="8" height="15" fill="#5a1818" rx="2"/>
          </g>
        </g>
      </g>
    `;
  }

  // 爆炸效果
  function boomSVG() {
    return `
      <g class="anim-boom">
        <circle cx="180" cy="100" r="20" fill="#ffd700" opacity="0.9"/>
        <circle cx="180" cy="100" r="15" fill="#ff6b35" opacity="0.95"/>
        <circle cx="180" cy="100" r="10" fill="#fff" opacity="0.9"/>
        <text x="180" y="105" font-size="20" text-anchor="middle">💥</text>
      </g>
    `;
  }

  // 胜利光晕
  function victoryGlow() {
    return `
      <g class="anim-glow">
        <circle cx="60" cy="100" r="40" fill="none" stroke="#ffd700" stroke-width="3" opacity="0.8"/>
        <circle cx="60" cy="100" r="50" fill="none" stroke="#ffd700" stroke-width="1" opacity="0.5"/>
        <text x="60" y="50" font-size="22" text-anchor="middle">✨</text>
      </g>
    `;
  }

  // 渲染单个战斗卡片
  function renderBattle(battle) {
    const statusText = battle.defeated
      ? '✅ 已打败！'
      : '🎯 还没打败，继续努力！';
    const statusColor = battle.defeated ? '#87ceeb' : '#ffd700';

    return `
      <div class="replay-card">
        <div class="replay-card-title">
          ⚔️ 文杰奥特曼 VS ${battle.monsterName}
        </div>
        <svg class="replay-svg" viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg">
          <!-- 背景 -->
          <rect width="240" height="150" fill="#0a0e27"/>
          <!-- 地面 -->
          <line x1="0" y1="135" x2="240" y2="135" stroke="#ffd700" stroke-width="1" opacity="0.3"/>
          <!-- 奥特曼 -->
          ${ultramanSVG(true)}
          <!-- 怪兽 -->
          ${monsterSVG(battle.monster, true)}
          <!-- 爆炸（隐藏） -->
          ${boomSVG()}
          <!-- 胜利光晕（隐藏） -->
          ${victoryGlow()}
        </svg>
        <div class="replay-card-status" style="color: ${statusColor};">
          ${statusText}
        </div>
      </div>
    `;
  }

  // 初始化
  function init() {
    const grid = document.getElementById('replay-grid');
    if (!grid) return;
    grid.innerHTML = BATTLES.map(renderBattle).join('');
  }

  // 等待 DOM 就绪
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();