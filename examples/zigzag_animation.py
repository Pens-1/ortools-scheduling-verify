#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter

r = 35.65
N = 6  # 円の数

def circle_positions(alpha_deg):
    """折り畳み角alpha[deg]での各円中心座標"""
    alpha = np.radians(alpha_deg)
    centers = []
    for k in range(N):
        x = k * 2 * r * np.cos(alpha)
        y = (k % 2) * 2 * r * np.sin(alpha)
        centers.append((x, y))
    return centers

def draw_frame(ax, alpha_deg, show_links=True):
    ax.clear()
    alpha = np.radians(alpha_deg)
    centers = circle_positions(alpha_deg)
    colors = ['#4A90D9', '#E74C3C'] * 3

    # リンク（中心間線）
    if show_links:
        for k in range(N - 1):
            x1, y1 = centers[k]
            x2, y2 = centers[k + 1]
            ax.plot([x1, x2], [y1, y2], 'k-', lw=2, alpha=0.5, zorder=1)
            # 距離ラベル
            d = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my+4, f'{d:.1f}', ha='center', va='bottom', fontsize=7, color='gray')

    # 円
    for k, (cx, cy) in enumerate(centers):
        circle = plt.Circle((cx, cy), r, color=colors[k], alpha=0.55,
                             linewidth=2, edgecolor='black', zorder=2)
        ax.add_patch(circle)
        ax.plot(cx, cy, 'k+', markersize=8, markeredgewidth=1.5, zorder=3)

    # ジグザグ高さ矢印
    h = 2 * r * np.sin(alpha)
    if h > 5:
        x_arr = centers[-1][0] + r * 1.3
        ax.annotate('', xy=(x_arr, h), xytext=(x_arr, 0),
                    arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax.text(x_arr + 5, h/2, f'{h:.1f}mm', va='center', fontsize=9,
                color='green', fontweight='bold')

    # 幅
    width = (N-1) * 2 * r * np.cos(alpha)
    ax.text(0.5, 0.02, f'width={width:.1f}mm', transform=ax.transAxes,
            ha='center', fontsize=9, color='navy')

    ax.set_xlim(-r*1.5, (N-1)*2*r + r*2.5)
    ax.set_ylim(-r*1.5, 2*r + r*1.8)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title(f'alpha={alpha_deg:.0f}deg  h={h:.1f}mm', fontsize=12)

# ---- 静止図（4ステップ） ----
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
for ax, a in zip(axes.flat, [0, 20, 40, 60]):
    draw_frame(ax, a)

plt.suptitle('Folding Chain: r=35.65mm  (straight -> hexagonal)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('zigzag_steps.png', dpi=110, bbox_inches='tight')
print("saved: zigzag_steps.png")

# ---- アニメーション ----
fig2, ax2 = plt.subplots(figsize=(12, 6))
alphas = list(np.linspace(0, 60, 45)) + list(np.linspace(60, 0, 45))

def update(frame):
    draw_frame(ax2, alphas[frame])

ani = FuncAnimation(fig2, update, frames=len(alphas), interval=40)
writer = PillowWriter(fps=20)
ani.save('zigzag_animation.gif', writer=writer)
print("saved: zigzag_animation.gif")
