#!/usr/bin/env python3
"""全節水平固定 → 矛盾なし機構: ギア角度=バー角度、全噛み合い整合"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

R    = 35.65
N    = 6
g_r  = 9.0
b    = 2 * g_r

GEAR_LOCAL = {
    'TR': ( g_r,  b), 'TL': (-g_r,  b),
    'MR': ( g_r,  0), 'ML': (-g_r,  0),
    'BR': ( g_r, -b), 'BL': (-g_r, -b),
}

def chain_state(alpha_deg):
    """全節水平、中心は折り畳みチェーン位置"""
    a = np.radians(alpha_deg)
    centers = [(k * 2*R * np.cos(a), (k%2) * 2*R * np.sin(a)) for k in range(N)]
    rotations = [0.0] * N   # 全節水平
    return centers, rotations

def gear_positions(k, alpha_deg):
    centers, _ = chain_state(alpha_deg)
    cx, cy = centers[k]
    return {label: (cx + lx, cy + ly) for label, (lx, ly) in GEAR_LOCAL.items()}

def bar_angle(p1, p2):
    return np.arctan2(p2[1]-p1[1], p2[0]-p1[0])

def get_bar_angles(alpha_deg):
    """各バー(k→k+1)の角度 [rad]"""
    angles_top = []
    angles_bot = []
    for k in range(N-1):
        gk  = gear_positions(k,   alpha_deg)
        gk1 = gear_positions(k+1, alpha_deg)
        angles_top.append(bar_angle(gk['TR'], gk1['TL']))
        angles_bot.append(bar_angle(gk['BR'], gk1['BL']))
    return angles_top, angles_bot

def compute_gear_spins(alpha_deg):
    """全ギアの回転角[rad]、矛盾なし"""
    angles_top, angles_bot = get_bar_angles(alpha_deg)
    spins = {k: {} for k in range(N)}
    for k in range(N):
        # TR(k): 出方向バー（k→k+1）の角度
        if k < N - 1:
            spins[k]['TR'] = angles_top[k]
            spins[k]['BR'] = angles_bot[k]
        # TL(k): 入方向バー（k-1→k）の角度（バーの両端が同じ向き）
        if k > 0:
            spins[k]['TL'] = angles_top[k-1]
            spins[k]['BL'] = angles_bot[k-1]
        # 端の節: 反対側ギアは噛み合いから決まる
        if k == 0:
            spins[k]['TL'] = -spins[k]['TR']  # TR-TL mesh
            spins[k]['BL'] = -spins[k]['BR']
        if k == N-1:
            spins[k]['TR'] = -spins[k]['TL']
            spins[k]['BR'] = -spins[k]['BL']
        # 中央: TR-MR mesh, TL-ML mesh
        spins[k]['MR'] = -spins[k]['TR']
        spins[k]['ML'] = -spins[k]['TL']
    return spins

def check_consistency(alpha_deg):
    """節内噛み合い整合性チェック"""
    spins = compute_gear_spins(alpha_deg)
    errors = []
    for k in range(N):
        s = spins[k]
        # TR-TL mesh
        diff_tr_tl = (s['TR'] + s['TL']) % (2*np.pi)
        if min(diff_tr_tl, 2*np.pi - diff_tr_tl) > 0.01:
            errors.append(f"node{k} TR-TL: {np.degrees(s['TR']):.1f} vs -{np.degrees(s['TL']):.1f}")
        # BR-BL mesh
        diff_br_bl = (s['BR'] + s['BL']) % (2*np.pi)
        if min(diff_br_bl, 2*np.pi - diff_br_bl) > 0.01:
            errors.append(f"node{k} BR-BL: {np.degrees(s['BR']):.1f} vs -{np.degrees(s['BL']):.1f}")
        # TR-MR-BR chain (TR=BR)
        diff_tr_br = (s['TR'] - s['BR']) % (2*np.pi)
        if min(diff_tr_br, 2*np.pi - diff_tr_br) > 0.01:
            errors.append(f"node{k} TR-BR: {np.degrees(s['TR']):.1f} vs {np.degrees(s['BR']):.1f}")
    return errors

def draw_gear(ax, cx, cy, color, spin_rad=0, n_teeth=14, tooth_h=2.0,
              alpha=0.85, zorder=8):
    angles = np.linspace(0, 2*np.pi, n_teeth, endpoint=False) + spin_rad
    ro, ri = g_r + tooth_h, g_r
    pts_x, pts_y = [], []
    for ang in angles:
        hw = np.pi/n_teeth*0.55
        for da, rr in [(-hw*1.3,ri),(-hw,ro),(hw,ro),(hw*1.3,ri)]:
            pts_x.append(cx + rr*np.cos(ang+da))
            pts_y.append(cy + rr*np.sin(ang+da))
    pts_x.append(pts_x[0]); pts_y.append(pts_y[0])
    ax.fill(pts_x, pts_y, color=color, alpha=alpha, zorder=zorder)
    ax.plot(pts_x, pts_y, 'k-', lw=0.6, zorder=zorder+1)
    mx = cx + g_r * np.cos(spin_rad)
    my = cy + g_r * np.sin(spin_rad)
    ax.plot([cx, mx], [cy, my], '-', color='red', lw=2, zorder=zorder+2)
    ax.plot(cx, cy, 'k.', markersize=2, zorder=zorder+3)

def draw_bar_with_gears(ax, p1, p2, color, spin_rad):
    p1 = np.array(p1); p2 = np.array(p2)
    L = np.linalg.norm(p2 - p1)
    if L < 1e-3: return
    u = (p2 - p1) / L
    perp = np.array([-u[1], u[0]])
    half_w = g_r * 0.5
    corners = np.array([
        p1 + half_w*perp, p2 + half_w*perp,
        p2 - half_w*perp, p1 - half_w*perp,
        p1 + half_w*perp,
    ])
    ax.fill(corners[:,0], corners[:,1], color=color, alpha=0.7, zorder=7)
    ax.plot(corners[:,0], corners[:,1], '-', color='black', lw=0.8, zorder=7.5)
    draw_gear(ax, p1[0], p1[1], color, spin_rad, alpha=0.95, zorder=9)
    draw_gear(ax, p2[0], p2[1], color, spin_rad, alpha=0.95, zorder=9)

def draw_frame(ax, alpha_deg):
    ax.clear()
    centers, _ = chain_state(alpha_deg)
    spins = compute_gear_spins(alpha_deg)
    errors = check_consistency(alpha_deg)

    for k, (cx, cy) in enumerate(centers):
        col = '#FFEEDD' if k%2==0 else '#DDEEFF'
        c = plt.Circle((cx, cy), R, facecolor=col,
                       edgecolor='gray', lw=1.0, alpha=0.30, zorder=2)
        ax.add_patch(c)
        ax.plot(cx, cy, 'k+', markersize=8, markeredgewidth=1.5, zorder=10)
        ax.text(cx, cy + R*1.05, f'{k}', ha='center', fontsize=11,
                fontweight='bold', color='gray')

    # 中央ギア
    for k in range(N):
        gp = gear_positions(k, alpha_deg)
        for label in ['MR','ML']:
            gx, gy = gp[label]
            draw_gear(ax, gx, gy, '#9B59B6', spins[k][label], zorder=8)

    # 棒（一体）
    for k in range(N-1):
        gk  = gear_positions(k,   alpha_deg)
        gk1 = gear_positions(k+1, alpha_deg)
        ang_top = bar_angle(gk['TR'], gk1['TL'])
        ang_bot = bar_angle(gk['BR'], gk1['BL'])
        draw_bar_with_gears(ax, gk['TR'], gk1['TL'], '#D35400', ang_top)
        draw_bar_with_gears(ax, gk['BR'], gk1['BL'], '#1F618D', ang_bot)

    # 端のギア (節0のTL/BL, 節N-1のTR/BR)
    gp0 = gear_positions(0, alpha_deg)
    for label in ['TL','BL']:
        gx, gy = gp0[label]
        color = '#F39C12' if label[0]=='T' else '#3498DB'
        draw_gear(ax, gx, gy, color, spins[0][label], zorder=8)
    gpN = gear_positions(N-1, alpha_deg)
    for label in ['TR','BR']:
        gx, gy = gpN[label]
        color = '#F39C12' if label[0]=='T' else '#3498DB'
        draw_gear(ax, gx, gy, color, spins[N-1][label], zorder=8)

    cx0, cy0 = centers[0]
    ax.plot(cx0, cy0, '*', color='red', markersize=20,
            markeredgecolor='darkred', markeredgewidth=1.5, zorder=12)

    a = np.radians(alpha_deg)
    h = 2*R*np.sin(a)
    angles_top, angles_bot = get_bar_angles(alpha_deg)
    title = f'alpha={alpha_deg:.0f}deg  zigzag={h:.1f}mm  '
    if angles_top:
        title += f'bar0_top={np.degrees(angles_top[0]):.1f} bar0_bot={np.degrees(angles_bot[0]):.1f}'
    title += f'  consistency: {"OK" if not errors else "NG ("+str(len(errors))+")"}'
    ax.set_title(title, fontsize=10)

    ax.set_xlim(-R*1.4, (N-1)*2*R + R*1.4)
    ax.set_ylim(-R*1.5, 2*R + R*1.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.25)
    ax.set_xlabel('x [mm]'); ax.set_ylabel('y [mm]')

# 静止4コマ
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
for ax, ang in zip(axes.flat, [0, 20, 40, 60]):
    draw_frame(ax, ang)
plt.suptitle('All nodes horizontal → top & bottom bars parallel → no contradiction\n'
             'gear rotation = bar angle (rigid), all gear meshes consistent',
             fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('zigzag_4gear_steps.png', dpi=110, bbox_inches='tight')
print("saved")
plt.close()

# 整合性確認
for ang in [0, 20, 40, 60]:
    errors = check_consistency(ang)
    print(f"alpha={ang}deg: {'CONSISTENT' if not errors else 'INCONSISTENT '+str(errors)}")

fig2, ax2 = plt.subplots(figsize=(14, 6))
angles_anim = list(np.linspace(0, 60, 60)) + list(np.linspace(60, 0, 60))
def update(i): draw_frame(ax2, angles_anim[i])
ani = FuncAnimation(fig2, update, frames=len(angles_anim), interval=33)
ani.save('zigzag_4gear_animation.gif', writer=PillowWriter(fps=24))
print("saved gif")
