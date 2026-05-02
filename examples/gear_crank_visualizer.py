#!/usr/bin/env python3
"""
平行クランク機構 可視化プログラム
- 静止図 (gear_viz_static.png)
- アニメーション GIF (gear_viz_animation.gif)
- クリアランスマップ (gear_viz_clearance.png)

実行:
    python3 examples/gear_crank_visualizer.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Polygon, FancyArrowPatch
from matplotlib.collections import PatchCollection
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(os.path.dirname(__file__), "..")

# ═══════════════════════════════════════════════════════════
#  パラメータ  (gear_crank_optimizer.py の最適解)
# ═══════════════════════════════════════════════════════════
R_LARGE          = 35.65   # 大ギア半径 r [mm]
X_OPT, Y_OPT    = 13.9391, 15.2922   # 最適 x, y
L_OPT            = 8.9391  # 最適バー半幅 L
GEAR_TOL         = 5.0     # ギア公差 [mm]

r   = R_LARGE
s3  = np.sqrt(3) * r
x, y, L = X_OPT, Y_OPT, L_OPT

# ── ギア中心 ─────────────────────────────────────────────
O   = np.array([0.0,   0.0])
Op  = np.array([r,     s3])
O1  = np.array([2 * r, 0.0])
O1p = np.array([3 * r, s3])
GEAR_CENTERS = [O, Op, O1, O1p]
GEAR_LABELS  = ["O", "O'", "O₁", "O₁'"]

# ── クランク半径 & 初期角 ────────────────────────────────
R_cr = np.hypot(x, 2 * y - x)
a0   = np.arctan2(2 * y - x,  x)   # O  の P1  初期角
b0   = np.arctan2(2 * y - x, -x)   # O' の P1' 初期角 (= π - a0)
g0   = np.arctan2(2 * y - x,  x)   # O' の P2  初期角 (= a0)
d0   = np.arctan2(2 * y - x, -x)   # O1 の P2' 初期角 (= π - a0)


# ═══════════════════════════════════════════════════════════
#  ジオメトリ関数
# ═══════════════════════════════════════════════════════════
def crank_pin(center, offset_angle, alpha, cw=True):
    """ギアが alpha 回転したときのクランクピン位置"""
    sign = -1 if cw else +1
    phi  = offset_angle + sign * alpha
    return center + R_cr * np.array([np.cos(phi), np.sin(phi)])


def all_pins(alpha):
    """全クランクピン位置 (外部噛み合い: 隣接ギアは逆回転)"""
    P1  = crank_pin(O,  a0, alpha, cw=True)
    P1p = crank_pin(Op, b0, alpha, cw=False)
    P2  = crank_pin(Op, g0, alpha, cw=False)
    P2p = crank_pin(O1, d0, alpha, cw=True)
    return P1, P1p, P2, P2p


# ═══════════════════════════════════════════════════════════
#  描画ユーティリティ
# ═══════════════════════════════════════════════════════════
def bar_polygon(a, b, half_w):
    """バー中心線 a→b, 半幅 half_w の Polygon コーナー"""
    d    = b - a
    if np.linalg.norm(d) < 1e-9:
        return None
    dn   = d / np.linalg.norm(d)
    perp = np.array([-dn[1], dn[0]]) * half_w
    return np.array([a + perp, b + perp, b - perp, a - perp])


def add_bar(ax, a, b, half_w, fc, ec, alpha_val=0.45, lw=2):
    corners = bar_polygon(a, b, half_w)
    if corners is None:
        return
    poly = Polygon(corners, closed=True,
                   facecolor=fc, edgecolor=ec,
                   linewidth=lw, alpha=alpha_val, zorder=4)
    ax.add_patch(poly)


def add_gear(ax, center, r_pitch, r_eff=None, fc="#ddddff",
             ec="steelblue", lw=1.5, alpha_val=0.5):
    """ピッチ円 (+ 実効円) 描画"""
    ax.add_patch(Circle(center, r_pitch, facecolor=fc,
                        edgecolor=ec, linewidth=lw,
                        alpha=alpha_val, zorder=3))
    if r_eff is not None:
        ax.add_patch(Circle(center, r_eff, fill=False,
                            edgecolor=ec, linewidth=1,
                            linestyle="--", alpha=0.5, zorder=3))


def set_common_axes(ax, margin=0.4):
    ax.set_aspect("equal")
    ax.set_xlim(-r * margin, 4 * r + r * margin)
    ax.set_ylim(-r * margin, s3 + r * (1 + margin))
    ax.set_xlabel("x [mm]", fontsize=9)
    ax.set_ylabel("y [mm]", fontsize=9)
    ax.grid(True, alpha=0.2, zorder=0)


BLUE_FC  = "#aaccff"
BLUE_EC  = "#2255bb"
RED_FC   = "#ffaaaa"
RED_EC   = "#bb2222"
GRAY_EC  = "#888888"


# ═══════════════════════════════════════════════════════════
#  図1: 静止図 (3パネル)
# ═══════════════════════════════════════════════════════════
def draw_static():
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    fig.suptitle(
        f"平行クランク機構  |  x={x:.2f}mm  y={y:.2f}mm  "
        f"2L={2*L:.2f}mm  R={R_cr:.2f}mm  r={r:.2f}mm",
        fontsize=11, fontweight="bold",
    )

    # ── パネル①: 初期位置 + クリアランス ────────────────
    ax = axes[0]
    set_common_axes(ax)
    ax.set_title("① 初期配置とクリアランス", fontsize=10)

    P1, P1p, P2, P2p = all_pins(0.0)

    # 大ギア (薄い破線)
    for ctr, lbl in zip(GEAR_CENTERS, GEAR_LABELS):
        ax.add_patch(Circle(ctr, r, fill=False, edgecolor=GRAY_EC,
                            linewidth=1.2, linestyle="--", alpha=0.5, zorder=1))
        ax.text(*ctr, lbl, ha="center", va="center",
                fontsize=9, color="gray", zorder=2)

    # バー (矩形)
    add_bar(ax, P1, P1p, L, BLUE_FC, BLUE_EC)
    add_bar(ax, P2, P2p, L, RED_FC,  RED_EC)

    # クランク腕
    for ctr, pin, col in [(O, P1, BLUE_EC), (Op, P1p, BLUE_EC),
                           (Op, P2, RED_EC),  (O1, P2p, RED_EC)]:
        ax.annotate("", xy=pin, xytext=ctr,
                    arrowprops=dict(arrowstyle="-|>", color=col,
                                   lw=1.8, mutation_scale=12),
                    zorder=5)

    # 小ギア (実効円)
    pin_info = [(P1, "P₁", BLUE_EC), (P1p, "P₁'", BLUE_EC),
                (P2, "P₂", RED_EC),  (P2p, "P₂'", RED_EC)]
    for pin, lbl, col in pin_info:
        add_gear(ax, pin, x, x + GEAR_TOL, fc=col, ec=col, alpha_val=0.25)
        ax.text(pin[0], pin[1] + x + GEAR_TOL + 2, lbl,
                ha="center", fontsize=8, color=col, zorder=6)

    # クリアランス注釈 (P2→バーA)
    bar_dir = P1p - P1
    bar_n   = bar_dir / np.linalg.norm(bar_dir)
    bar_perp = np.array([-bar_n[1], bar_n[0]])
    closest_on_barA = P1p  # P2 は P1p に最も近い
    ax.annotate("",
        xy=P2, xytext=P1p,
        arrowprops=dict(arrowstyle="<->", color="orange", lw=1.5),
        zorder=7)
    mid = (P2 + P1p) / 2
    ax.text(mid[0] + 3, mid[1], f"gap={2*x:.1f}mm\n→L≤{x-GEAR_TOL:.1f}mm",
            fontsize=7, color="darkorange",
            bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.8))

    # ── パネル②: 全クランク角での sweep ──────────────────
    ax = axes[1]
    set_common_axes(ax)
    ax.set_title("② バーの掃引軌跡 (全回転)", fontsize=10)

    alphas = np.linspace(0, 2 * np.pi, 120)

    # バーの中心線軌跡
    for alpha_i, a in enumerate(alphas):
        P1i, P1pi, P2i, P2pi = all_pins(a)
        fade = 0.08 + 0.35 * (1 - np.sin(alpha_i / len(alphas) * np.pi) * 0.5)
        add_bar(ax, P1i, P1pi, L, BLUE_FC, BLUE_EC,
                alpha_val=fade * 0.5, lw=0.8)
        add_bar(ax, P2i, P2pi, L, RED_FC, RED_EC,
                alpha_val=fade * 0.5, lw=0.8)

    # クランクピン軌跡
    trails = {"P1": [], "P1p": [], "P2": [], "P2p": []}
    for a in alphas:
        P1i, P1pi, P2i, P2pi = all_pins(a)
        trails["P1"].append(P1i)
        trails["P1p"].append(P1pi)
        trails["P2"].append(P2i)
        trails["P2p"].append(P2pi)

    for name, col, ls in [("P1", BLUE_EC, "-"),  ("P1p", BLUE_EC, "--"),
                           ("P2", RED_EC,  "-"),  ("P2p", RED_EC,  "--")]:
        pts = np.array(trails[name])
        ax.plot(pts[:, 0], pts[:, 1], color=col, lw=1.5,
                linestyle=ls, alpha=0.9, label=name, zorder=5)

    # 大ギア + クランク半径円
    for ctr, lbl in zip(GEAR_CENTERS, GEAR_LABELS):
        ax.add_patch(Circle(ctr, r, fill=False, edgecolor=GRAY_EC,
                            linewidth=1.2, linestyle="--", alpha=0.4, zorder=1))
        ax.add_patch(Circle(ctr, R_cr, fill=False, edgecolor="mediumseagreen",
                            linewidth=1.5, linestyle=":", alpha=0.6, zorder=2))
        ax.text(*ctr, lbl, ha="center", va="center",
                fontsize=8, color="gray", zorder=3)

    ax.legend(loc="upper right", fontsize=8, ncol=2)

    legend_items = [
        plt.Line2D([0], [0], color=BLUE_EC, lw=2, label="バーA (P1→P1')"),
        plt.Line2D([0], [0], color=RED_EC,  lw=2, label="バーB (P2→P2')"),
        plt.Line2D([0], [0], color="mediumseagreen", lw=1.5,
                   linestyle=":", label=f"クランク半径 R={R_cr:.1f}mm"),
        plt.Line2D([0], [0], color=GRAY_EC, lw=1.2,
                   linestyle="--", label=f"大ギア r={r:.1f}mm"),
    ]
    ax.legend(handles=legend_items, loc="lower right", fontsize=8)

    # ── パネル③: クランク半径 vs L_max マップ ────────────
    ax = axes[2]
    ax.set_title("③ x vs L_max (R/r 等高線付き)", fontsize=10)

    # gear_crank_optimizer からインポート
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from examples.gear_crank_optimizer import L_max_for, feasible, crank_radius
        xx = np.linspace(3.0, r * 0.44, 60)
        yy = np.linspace(3.0, r * 0.44, 60)
        XX, YY = np.meshgrid(xx, yy)
        ZZ_L   = np.zeros_like(XX)
        ZZ_R   = np.zeros_like(XX)
        for i in range(len(yy)):
            for j in range(len(xx)):
                xi, yi = XX[i, j], YY[i, j]
                if feasible(xi, yi):
                    ZZ_L[i, j] = max(L_max_for(xi, yi), 0)
                    ZZ_R[i, j] = crank_radius(xi, yi) / r
                else:
                    ZZ_L[i, j] = np.nan
                    ZZ_R[i, j] = np.nan

        cf = ax.contourf(XX, YY, ZZ_L, levels=20, cmap="RdYlGn")
        fig.colorbar(cf, ax=ax, label="L_max [mm]")
        cs = ax.contour(XX, YY, ZZ_R,
                        levels=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
                        colors="navy", linewidths=0.8, alpha=0.7)
        ax.clabel(cs, fmt="R/r=%.1f", fontsize=7)

        # 最適点
        ax.scatter([x], [y], c="red", s=120, marker="*",
                   zorder=10, label=f"最適 ({x:.1f}, {y:.1f})")
        ax.annotate(f"  L={L:.2f}mm\n  2L={2*L:.2f}mm",
                    (x, y), fontsize=8, color="red",
                    bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.9))
        ax.legend(fontsize=8)

    except ImportError:
        ax.text(0.5, 0.5, "optimizer モジュールが見つかりません",
                transform=ax.transAxes, ha="center")

    ax.set_xlabel("x (小ギア半径) [mm]", fontsize=9)
    ax.set_ylabel("y (オフセット) [mm]", fontsize=9)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    out_path = os.path.join(OUT, "gear_viz_static.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"[静止図] 保存: {out_path}")
    plt.close()


# ═══════════════════════════════════════════════════════════
#  図2: アニメーション GIF
# ═══════════════════════════════════════════════════════════
def draw_animation(n_frames=90, fps=20):
    fig, ax = plt.subplots(figsize=(9, 8))
    set_common_axes(ax, margin=0.5)

    alphas = np.linspace(0, 2 * np.pi, n_frames, endpoint=False)

    # 固定要素: 大ギア円 & ラベル
    for ctr, lbl in zip(GEAR_CENTERS, GEAR_LABELS):
        ax.add_patch(Circle(ctr, r, fill=False, edgecolor=GRAY_EC,
                            linewidth=1.5, linestyle="--", alpha=0.5, zorder=1))
        ax.text(*ctr, lbl, ha="center", va="center",
                fontsize=11, color="dimgray", fontweight="bold", zorder=2)

    # ─── 可変要素 ─────────────────────────────────────────
    bar_A_patch = Polygon([[0, 0]] * 4, closed=True,
                          facecolor=BLUE_FC, edgecolor=BLUE_EC,
                          linewidth=2.5, alpha=0.55, zorder=5)
    bar_B_patch = Polygon([[0, 0]] * 4, closed=True,
                          facecolor=RED_FC,  edgecolor=RED_EC,
                          linewidth=2.5, alpha=0.55, zorder=5)
    ax.add_patch(bar_A_patch)
    ax.add_patch(bar_B_patch)

    # クランク腕 (線)
    arm_lines = []
    arm_colors = [BLUE_EC, BLUE_EC, RED_EC, RED_EC]
    for col in arm_colors:
        ln, = ax.plot([], [], color=col, linewidth=2.5,
                      linestyle="-.", alpha=0.75, zorder=4)
        arm_lines.append(ln)

    # クランクピン (円)
    pin_circles = []
    pin_colors = [BLUE_EC, BLUE_EC, RED_EC, RED_EC]
    for col in pin_colors:
        circ = Circle([0, 0], x, facecolor=col, edgecolor="white",
                      linewidth=1.5, alpha=0.8, zorder=7)
        eff_circ = Circle([0, 0], x + GEAR_TOL, fill=False,
                          edgecolor=col, linewidth=1, linestyle="--",
                          alpha=0.45, zorder=6)
        ax.add_patch(circ)
        ax.add_patch(eff_circ)
        pin_circles.append((circ, eff_circ))

    # ギア回転マーカー (外周の点)
    rot_dots = []
    rot_offsets = [a0, b0, g0, d0]
    rot_cw     = [True, False, False, True]
    rot_colors = [BLUE_EC, BLUE_EC, RED_EC, RED_EC]
    for col in rot_colors:
        dot, = ax.plot([], [], "o", color=col, ms=8, alpha=0.8, zorder=8)
        rot_dots.append(dot)

    # 大ギアの回転マーカー (外周の十字)
    large_rot_lines = []
    large_rot_cw    = [True, False, True, False]
    for ctr in GEAR_CENTERS:
        ln1, = ax.plot([], [], "-", color="lightgray", lw=1.5, alpha=0.6, zorder=2)
        ln2, = ax.plot([], [], "-", color="lightgray", lw=1.5, alpha=0.6, zorder=2)
        large_rot_lines.append((ln1, ln2))

    # トレイル (最新 N_TRAIL フレームの軌跡)
    N_TRAIL = 25
    trail_data = {k: [] for k in ["P1", "P1p", "P2", "P2p"]}
    trail_lines = {}
    trail_cols = {"P1": BLUE_EC, "P1p": "#7799ee",
                  "P2": RED_EC,  "P2p": "#ee7777"}
    trail_lss  = {"P1": "-", "P1p": "--", "P2": "-", "P2p": "--"}
    for k in trail_data:
        ln, = ax.plot([], [], color=trail_cols[k], lw=1.5,
                      linestyle=trail_lss[k], alpha=0.7, zorder=5)
        trail_lines[k] = ln

    # フレームカウンター
    frame_text = ax.text(
        0.02, 0.97, "", transform=ax.transAxes,
        fontsize=9, va="top", ha="left",
        bbox=dict(boxstyle="round", fc="white", alpha=0.8),
    )

    # 凡例
    leg_handles = [
        plt.matplotlib.patches.Patch(fc=BLUE_FC, ec=BLUE_EC, label=f"バーA (2L={2*L:.1f}mm)"),
        plt.matplotlib.patches.Patch(fc=RED_FC,  ec=RED_EC,  label=f"バーB (2L={2*L:.1f}mm)"),
        plt.Line2D([0], [0], color="mediumseagreen", lw=1.5, ls=":",
                   label=f"クランク軌跡 R={R_cr:.1f}mm"),
    ]
    ax.legend(handles=leg_handles, loc="lower right", fontsize=9)

    # クランク軌跡 (固定)
    for ctr in [O, Op, O1]:
        ax.add_patch(Circle(ctr, R_cr, fill=False, edgecolor="mediumseagreen",
                            linewidth=1.5, linestyle=":", alpha=0.4, zorder=2))

    ax.set_title(
        f"平行クランク機構 アニメーション\n"
        f"x={x:.2f}mm  y={y:.2f}mm  2L={2*L:.2f}mm  "
        f"R={R_cr:.2f}mm  (R/r={R_cr/r:.3f})",
        fontsize=10,
    )

    arm_endpoints = [(O, "P1"), (Op, "P1p"), (Op, "P2"), (O1, "P2p")]
    pin_keys      = ["P1", "P1p", "P2", "P2p"]

    def update(frame_idx):
        alpha = alphas[frame_idx]
        P1, P1p, P2, P2p = all_pins(alpha)
        pins = {"P1": P1, "P1p": P1p, "P2": P2, "P2p": P2p}

        # バー矩形
        corners_A = bar_polygon(P1, P1p, L)
        corners_B = bar_polygon(P2, P2p, L)
        if corners_A is not None:
            bar_A_patch.set_xy(corners_A)
        if corners_B is not None:
            bar_B_patch.set_xy(corners_B)

        # クランク腕
        for ln, (ctr, key) in zip(arm_lines, arm_endpoints):
            p = pins[key]
            ln.set_data([ctr[0], p[0]], [ctr[1], p[1]])

        # クランクピン
        for (circ, eff), key in zip(pin_circles, pin_keys):
            p = pins[key]
            circ.center = p
            eff.center  = p

        # 大ギア回転マーカー (外周の十字)
        for (ln1, ln2), ctr, cw in zip(large_rot_lines, GEAR_CENTERS, large_rot_cw):
            sign = -1 if cw else +1
            phi  = sign * alpha
            cp   = ctr + r * np.array([np.cos(phi), np.sin(phi)])
            cm   = ctr - r * np.array([np.cos(phi), np.sin(phi)])
            ln1.set_data([cm[0], cp[0]], [cm[1], cp[1]])
            cp2  = ctr + r * np.array([np.cos(phi + np.pi/2), np.sin(phi + np.pi/2)])
            cm2  = ctr - r * np.array([np.cos(phi + np.pi/2), np.sin(phi + np.pi/2)])
            ln2.set_data([cm2[0], cp2[0]], [cm2[1], cp2[1]])

        # 小ギア回転マーカー
        for dot, key, cw in zip(rot_dots, pin_keys, [True, False, False, True]):
            ctr = pins[key]
            sign = -1 if cw else +1
            phi  = sign * alpha
            dp   = ctr + x * np.array([np.cos(phi), np.sin(phi)])
            dot.set_data([dp[0]], [dp[1]])

        # トレイル
        for key in trail_data:
            trail_data[key].append(pins[key].copy())
            if len(trail_data[key]) > N_TRAIL:
                trail_data[key].pop(0)
            pts = np.array(trail_data[key])
            if len(pts) > 1:
                trail_lines[key].set_data(pts[:, 0], pts[:, 1])

        # フレームカウンター
        deg = np.degrees(alpha)
        frame_text.set_text(
            f"α = {deg:5.1f}°\n"
            f"|P1-P1'| = {np.linalg.norm(P1p - P1):.1f} mm\n"
            f"|P2-P2'| = {np.linalg.norm(P2p - P2):.1f} mm"
        )

        return (bar_A_patch, bar_B_patch, *arm_lines,
                *[c for pair in pin_circles for c in pair],
                *[d for d in rot_dots],
                *[ln for pair in large_rot_lines for ln in pair],
                *trail_lines.values(),
                frame_text)

    ani = animation.FuncAnimation(
        fig, update,
        frames=n_frames,
        interval=1000 // fps,
        blit=True,
    )

    out_path = os.path.join(OUT, "gear_viz_animation.gif")
    writer   = animation.PillowWriter(fps=fps)
    ani.save(out_path, writer=writer, dpi=120)
    print(f"[アニメーション] 保存: {out_path}")
    plt.close()


# ═══════════════════════════════════════════════════════════
#  図3: クリアランス詳細図
# ═══════════════════════════════════════════════════════════
def draw_clearance():
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("クリアランス詳細分析", fontsize=11, fontweight="bold")

    # ── 左: クランク角 vs バー長さ ───────────────────────
    ax = axes[0]
    alphas = np.linspace(0, 2 * np.pi, 360)
    len_A, len_B = [], []
    gap_P2_A, gap_P1_B = [], []

    for a in alphas:
        P1, P1p, P2, P2p = all_pins(a)
        len_A.append(np.linalg.norm(P1p - P1))
        len_B.append(np.linalg.norm(P2p - P2))

        # P2 → バーA中心線の距離
        from examples.gear_crank_optimizer import dist_pt_seg
        gap_P2_A.append(dist_pt_seg(P2, P1, P1p) - (x + GEAR_TOL))
        gap_P1_B.append(dist_pt_seg(P1, P2, P2p) - (x + GEAR_TOL))

    deg = np.degrees(alphas)

    ax.plot(deg, len_A, BLUE_EC, lw=2, label="|P1-P1'| バーA長さ")
    ax.plot(deg, len_B, RED_EC,  lw=2, label="|P2-P2'| バーB長さ", linestyle="--")
    ax.axhline(np.linalg.norm(
        np.array([r-x, s3+2*y-x]) - np.array([x, 2*y-x])
    ), color="gray", linestyle=":", lw=1.5, label="理論バー長 (α=0)")
    ax.set_xlabel("クランク角 α [deg]", fontsize=9)
    ax.set_ylabel("バー長さ [mm]", fontsize=9)
    ax.set_title("クランク角 vs バー長さ\n(外部噛み合い仮定時の変動)", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 360)

    ax2 = ax.twinx()
    ax2.plot(deg, gap_P2_A, color="darkorange", lw=1.5,
             label="P2→バーA クリアランス", alpha=0.7)
    ax2.plot(deg, gap_P1_B, color="purple", lw=1.5,
             label="P1→バーB クリアランス", linestyle="--", alpha=0.7)
    ax2.axhline(L_OPT, color="green", lw=1.5, linestyle=":",
                label=f"L_opt={L_OPT:.2f}mm")
    ax2.axhline(0, color="red", lw=0.8, linestyle="-")
    ax2.set_ylabel("クリアランス [mm]", fontsize=9, color="darkorange")
    ax2.tick_params(axis="y", labelcolor="darkorange")
    ax2.legend(fontsize=8, loc="upper right")

    # ── 右: 機構図 (初期位置) + クリアランス注釈 ─────────
    ax = axes[1]
    ax.set_aspect("equal")
    ax.set_xlim(-r * 0.3, 4 * r + r * 0.3)
    ax.set_ylim(-r * 0.3, s3 + r * 1.2)
    ax.set_title("初期位置 クリアランス詳細", fontsize=9)
    ax.grid(True, alpha=0.2)

    P1, P1p, P2, P2p = all_pins(0.0)

    # 大ギア
    for ctr, lbl in zip(GEAR_CENTERS, GEAR_LABELS):
        ax.add_patch(Circle(ctr, r, fill=False, edgecolor=GRAY_EC,
                            linewidth=1, linestyle="--", alpha=0.4))
        ax.text(*ctr, lbl, ha="center", va="center",
                fontsize=8, color="gray")

    # バー
    add_bar(ax, P1, P1p, L_OPT, BLUE_FC, BLUE_EC, alpha_val=0.5, lw=2)
    add_bar(ax, P2, P2p, L_OPT, RED_FC,  RED_EC,  alpha_val=0.5, lw=2)

    # ギア
    for pin, col in [(P1, BLUE_EC), (P1p, BLUE_EC), (P2, RED_EC), (P2p, RED_EC)]:
        add_gear(ax, pin, x, x + GEAR_TOL, fc=col, ec=col, alpha_val=0.2)

    # クリアランス矢印: P2 ↔ P1p  (ボトルネック)
    ax.annotate("", xy=P2, xytext=P1p,
                arrowprops=dict(arrowstyle="<->", color="orange", lw=2))
    mid = (P2 + P1p) / 2 + np.array([0, 4])
    ax.text(mid[0], mid[1],
            f"gap = {np.linalg.norm(P2-P1p):.1f}mm\n"
            f"→ L_max = {np.linalg.norm(P2-P1p)/2 - x:.1f}mm (実効半径で)\n"
            f"→ L_max = {np.linalg.norm(P2-P1p) - (x+GEAR_TOL):.1f}mm (+5mm公差)",
            fontsize=7.5, ha="center",
            bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.9))

    # バー幅矢印
    bar_dir = P1p - P1
    bn = bar_dir / np.linalg.norm(bar_dir)
    perp = np.array([-bn[1], bn[0]])
    mid_bar = (P1 + P1p) / 2
    p_plus  = mid_bar + perp * L_OPT
    p_minus = mid_bar - perp * L_OPT
    ax.annotate("", xy=p_plus, xytext=p_minus,
                arrowprops=dict(arrowstyle="<->", color=BLUE_EC, lw=2))
    ax.text(p_plus[0] + perp[0] * 3, p_plus[1] + perp[1] * 3,
            f"2L={2*L_OPT:.1f}mm", fontsize=8, color=BLUE_EC,
            bbox=dict(boxstyle="round", fc="white", alpha=0.8))

    ax.set_xlabel("x [mm]", fontsize=9)
    ax.set_ylabel("y [mm]", fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(OUT, "gear_viz_clearance.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"[クリアランス図] 保存: {out_path}")
    plt.close()


# ═══════════════════════════════════════════════════════════
#  メイン
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 50)
    print("  平行クランク機構 可視化")
    print(f"  x={x:.4f}mm  y={y:.4f}mm  2L={2*L:.4f}mm")
    print(f"  R={R_cr:.4f}mm  r={r:.4f}mm  R/r={R_cr/r:.4f}")
    print("=" * 50)

    print("\n[1/3] 静止図を生成中...")
    draw_static()

    print("[2/3] アニメーションを生成中 (約30秒)...")
    draw_animation(n_frames=90, fps=18)

    print("[3/3] クリアランス図を生成中...")
    draw_clearance()

    print("\n完了。生成ファイル:")
    for fn in ["gear_viz_static.png", "gear_viz_animation.gif", "gear_viz_clearance.png"]:
        fp = os.path.join(OUT, fn)
        if os.path.exists(fp):
            size_kb = os.path.getsize(fp) // 1024
            print(f"  {fn}  ({size_kb} KB)")
