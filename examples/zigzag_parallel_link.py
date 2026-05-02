#!/usr/bin/env python3
"""別々の平行リンクをギアで噛み合わせたジグザグ機構"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# ---- パラメータ ----
N   = 6              # 平行リンクの数
L   = 50.0           # 各リンクの底辺長
h   = 35.65          # 側辺長（== ギア半径で噛み合い保つ）
g_r = h              # ギア半径

def units_state(alpha):
    """alpha=0: 折り畳み（一直線）、alpha=π/2: 矩形ジグザグ"""
    sa, ca = np.sin(alpha), np.cos(alpha)
    gap = np.sqrt(max(0, (2*g_r)**2 - (2*h*sa)**2))   # 隣接リンクの隙間
    units = []
    for k in range(N):
        sign = +1 if k % 2 == 0 else -1   # 偶数: 上向き、奇数: 下向き
        x = k * (L + gap)
        BL = (x,         0)
        BR = (x + L,     0)
        TL = (x + h*ca,         sign * h*sa)
        TR = (x + L + h*ca,     sign * h*sa)
        units.append(dict(BL=BL, BR=BR, TL=TL, TR=TR, sign=sign))
    return units, gap

def draw_gear(ax, cx, cy, color, alpha=0.7, n_teeth=14, tooth_h=2.5):
    angles = np.linspace(0, 2*np.pi, n_teeth, endpoint=False)
    ro, ri = g_r + tooth_h, g_r
    pts_x, pts_y = [], []
    for ang in angles:
        hw = np.pi/n_teeth*0.55
        for da, rr in [(-hw*1.3,ri),(-hw,ro),(hw,ro),(hw*1.3,ri)]:
            pts_x.append(cx + rr*np.cos(ang+da))
            pts_y.append(cy + rr*np.sin(ang+da))
    pts_x.append(pts_x[0]); pts_y.append(pts_y[0])
    ax.fill(pts_x, pts_y, color=color, alpha=alpha, zorder=5)
    ax.plot(pts_x, pts_y, 'k-', lw=0.7, zorder=6)
    ax.plot(cx, cy, 'k+', markersize=6, markeredgewidth=1.2, zorder=7)

def draw_frame(ax, alpha):
    ax.clear()
    units, gap = units_state(alpha)
    para_colors = ['#FFE9DC', '#DCEAFF'] * (N//2+1)

    # 平行リンクの4辺
    for k, u in enumerate(units):
        xs = [u['BL'][0], u['BR'][0], u['TR'][0], u['TL'][0], u['BL'][0]]
        ys = [u['BL'][1], u['BR'][1], u['TR'][1], u['TL'][1], u['BL'][1]]
        ax.fill(xs, ys, color=para_colors[k], alpha=0.55, zorder=1)
        ax.plot(xs, ys, '-', color='black', lw=2.5, zorder=4)
        # トップバー強調
        ax.plot([u['TL'][0], u['TR'][0]], [u['TL'][1], u['TR'][1]],
                '-', color='#C0392B', lw=4, zorder=5)
        # ボトムバー
        ax.plot([u['BL'][0], u['BR'][0]], [u['BL'][1], u['BR'][1]],
                '-', color='#2C3E50', lw=4, zorder=5)
        # ユニット番号
        cx = (u['BL'][0]+u['BR'][0])/2
        ax.text(cx, u['sign']*h*np.sin(alpha)/2 if alpha>0.05 else -8,
                f'{k}', ha='center', fontsize=10, fontweight='bold',
                color='gray', zorder=10)

    # 境界のギア対 (TR(k)↔TL(k+1)) と (BR(k)↔BL(k+1))
    for k in range(N-1):
        TR_k  = units[k]['TR']
        TL_k1 = units[k+1]['TL']
        # 上のギア対（オレンジ）
        draw_gear(ax, *TR_k, '#E67E22')
        draw_gear(ax, *TL_k1, '#E67E22')
        # 噛み合いライン
        ax.plot([TR_k[0], TL_k1[0]], [TR_k[1], TL_k1[1]],
                ':', color='green', lw=1, zorder=2)

        BR_k  = units[k]['BR']
        BL_k1 = units[k+1]['BL']
        # 下のギア対（青）
        draw_gear(ax, *BR_k, '#2980B9')
        draw_gear(ax, *BL_k1, '#2980B9')

    # 寸法
    sa = np.sin(alpha)
    ax.set_title(f'alpha={np.degrees(alpha):.0f}deg  '
                 f'top_height={h*sa:+.1f}/{-h*sa:+.1f}mm  '
                 f'gap={gap:.1f}mm',
                 fontsize=11)

    ax.set_xlim(-g_r*1.2, N*(L+2*g_r) + g_r*1.2)
    ax.set_ylim(-h - g_r*1.5, h + g_r*1.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('x [mm]'); ax.set_ylabel('y [mm]')

# ---- 静止4コマ ----
fig, axes = plt.subplots(2, 2, figsize=(18, 10))
for ax, ang_deg in zip(axes.flat, [0, 30, 60, 90]):
    draw_frame(ax, np.radians(ang_deg))
plt.suptitle(f'Separate parallel links coupled by gears at TR/TL & BR/BL\n'
             f'(N={N} units, L={L}mm, h=g_radius={h}mm)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('zigzag_parallel_link_steps.png', dpi=110, bbox_inches='tight')
print("saved: zigzag_parallel_link_steps.png")
plt.close()

# ---- アニメ ----
fig2, ax2 = plt.subplots(figsize=(16, 6))
angles = list(np.linspace(0, np.pi/2, 50)) + list(np.linspace(np.pi/2, 0, 50))
def update(i): draw_frame(ax2, angles[i])
ani = FuncAnimation(fig2, update, frames=len(angles), interval=40)
ani.save('zigzag_parallel_link_animation.gif', writer=PillowWriter(fps=22))
print("saved: zigzag_parallel_link_animation.gif")
