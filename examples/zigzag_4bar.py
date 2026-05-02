#!/usr/bin/env python3
"""4節平行リンク × 6 チェーン → ジグザグ機構"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter

r   = 35.65          # ギア半径
d   = r * np.sqrt(3) # ピッチ間隔（ジグザグ接触条件: d²+4R²=(2r)²）
R   = r / 2          # クランク腕長（= ジグザグ振幅）
N   = 6              # ギア数
N_PIV = N + 1        # 固定軸数（=7）

# ジグザグ時の接触距離確認: sqrt(d^2 + (2R)^2) == 2r
assert abs(np.hypot(d, 2*R) - 2*r) < 1e-6, "touching condition failed"

def unit_centers(theta_deg):
    """各ギア中心を返す（theta: 偶数ユニットのクランク角）"""
    th = np.radians(theta_deg)
    centers = []
    for k in range(N):
        sign = 1 if k % 2 == 0 else -1   # 隣同士は逆位相
        cx = (k + 0.5) * d + R * np.cos(sign * th)
        cy =              R * np.sin(sign * th)
        centers.append((cx, cy))
    return centers

def draw_frame(ax, theta_deg):
    ax.clear()
    th = np.radians(theta_deg)
    pivots = [(i * d, 0.0) for i in range(N_PIV)]  # 固定軸 7個
    centers = unit_centers(theta_deg)
    gear_colors = ['#3A7FC1', '#C0392B'] * 3

    # ---- クランク腕 と コネクティングロッド ----
    for k in range(N):
        sign = 1 if k % 2 == 0 else -1
        # 左固定軸 → 左クランク先端
        Lx, Ly = pivots[k]
        Rx_piv, Ry_piv = pivots[k + 1]
        # クランク先端（コネクティングロッドの両端）
        tip_Lx = Lx + R * np.cos(sign * th)
        tip_Ly =      R * np.sin(sign * th)
        tip_Rx = Rx_piv + R * np.cos(sign * th)
        tip_Ry =          R * np.sin(sign * th)
        # クランク（細い黒線）
        ax.plot([Lx, tip_Lx], [Ly, tip_Ly], 'k-', lw=2.5, zorder=2)
        ax.plot([Rx_piv, tip_Rx], [Ry_piv, tip_Ry], 'k-', lw=2.5, zorder=2)
        # コネクティングロッド（太い線 = 平行リンク）
        ax.plot([tip_Lx, tip_Rx], [tip_Ly, tip_Ry],
                '-', color='#666', lw=5, solid_capstyle='round', zorder=3)

    # ---- 固定軸 ----
    for px, py in pivots:
        ax.plot(px, py, 's', color='#222', markersize=9, zorder=5)
        ax.plot(px, py, 'w+', markersize=7, markeredgewidth=2, zorder=6)

    # ---- ギア（歯付き円） ----
    nt = 16
    for k, (cx, cy) in enumerate(centers):
        angles = np.linspace(0, 2*np.pi, nt, endpoint=False)
        ro, ri = r + 3.5, r
        pts_x, pts_y = [], []
        for a in angles:
            hw = np.pi / nt * 0.5
            for da, rr in [(-hw*1.3,ri),(-hw,ro),(hw,ro),(hw*1.3,ri)]:
                pts_x.append(cx + rr * np.cos(a + da))
                pts_y.append(cy + rr * np.sin(a + da))
        pts_x.append(pts_x[0]); pts_y.append(pts_y[0])
        ax.fill(pts_x, pts_y, color=gear_colors[k], alpha=0.70, zorder=4)
        ax.plot(pts_x, pts_y, 'k-', lw=1.2, zorder=4)
        # ピッチ円
        th2 = np.linspace(0, 2*np.pi, 120)
        ax.plot(cx + r*np.cos(th2), cy + r*np.sin(th2),
                '--', color='white', lw=0.8, alpha=0.7, zorder=5)
        ax.plot(cx, cy, 'k+', markersize=7, markeredgewidth=2, zorder=6)

    # ---- 寸法 ----
    h = abs(R * np.sin(th))
    if h > 2:
        last_cx = centers[-1][0]
        ax.annotate('', xy=(last_cx + r*1.5, R*np.sin(th)),
                    xytext=(last_cx + r*1.5, -R*np.sin(th)),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax.text(last_cx + r*1.7, 0, f'{2*h:.1f}mm\n(peak-to-peak)',
                va='center', fontsize=8.5, color='green', fontweight='bold')

    # 接触距離（ジグザグ時のみ）
    if theta_deg > 5:
        for k in range(N - 1):
            cx0, cy0 = centers[k]
            cx1, cy1 = centers[k + 1]
            dist = np.hypot(cx1-cx0, cy1-cy0)
            mx, my = (cx0+cx1)/2, (cy0+cy1)/2
            ax.text(mx, my, f'{dist:.0f}', ha='center', va='center',
                    fontsize=7, color='white', fontweight='bold',
                    bbox=dict(fc='#333',alpha=0.65,pad=1,boxstyle='round'))

    ax.set_xlim(-r*1.5, (N+0.5)*d + r*2.5)
    ax.set_ylim(-r*2.2, r*2.2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.25)
    ax.set_xlabel('x [mm]')
    ax.set_ylabel('y [mm]')
    ax.set_title(f'4-bar parallel link chain  theta={theta_deg:.0f}deg  '
                 f'peak-to-peak={2*h:.1f}mm  (max={2*R:.1f}mm when 90deg)',
                 fontsize=10)

    # フレーム（固定レール）
    ax.axhline(0, color='#aaa', lw=1.5, ls=':', zorder=1)

# ---- 静止4コマ ----
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
for ax, ang in zip(axes.flat, [0, 30, 60, 90]):
    draw_frame(ax, ang)
plt.suptitle(f'4-bar Parallel Link Chain × {N}  (r={r}mm, R={R:.1f}mm, d={d:.1f}mm)\n'
             f'straight(0deg) -> zigzag(90deg, touching {2*r:.1f}mm)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('zigzag_4bar_steps.png', dpi=110, bbox_inches='tight')
print("saved: zigzag_4bar_steps.png")
plt.close()

# ---- アニメーション ----
fig2, ax2 = plt.subplots(figsize=(14, 6))
angles = list(np.linspace(0, 90, 50)) + list(np.linspace(90, 0, 50))

def update(i):
    draw_frame(ax2, angles[i])

ani = FuncAnimation(fig2, update, frames=len(angles), interval=30)
writer = PillowWriter(fps=24)
ani.save('zigzag_4bar_animation.gif', writer=writer)
print("saved: zigzag_4bar_animation.gif")
print(f"\n設計値: r={r}mm  R={R:.2f}mm  d={d:.2f}mm")
print(f"ジグザグ時接触距離: {np.hypot(d,2*R):.2f}mm (=2r={2*r}mm)")
print(f"最大peak-to-peak: {2*R:.2f}mm")
