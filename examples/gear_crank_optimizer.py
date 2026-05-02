#!/usr/bin/env python3
"""
キャッチロボ大会用: 平行クランク機構のギア・バー最適化
落書き (r01.jpg / r02.jpg) に基づくジオメトリ最適化

座標系 (r01.jpg より):
    O   = (0,   0)          大ギア1中心
    O'  = (r,  √3r)         大ギア2中心
    O₁  = (2r,  0)          大ギア3中心
    O₁' = (3r, √3r)         大ギア4中心

    P₁  = (x,     2y - x)
    P₁' = (r - x, √3r + 2y - x)
    P₂  = (r + x, √3r + 2y - x)
    P₂' = (2r - x, 2y - x)

    tanθ = √3r / (r - 2x)   ← バーの傾角
    r    = 35.65 mm

最適化問題:
    - 変数 : x (小ギア/クランクピン半径), y (Y方向クランクパラメータ)
    - 目的 : バー半幅 L を最大化
    - 制約 :
        * クランク半径 R = √(x²+(2y-x)²) ≤ r - x  (ピンが大ギア内に収まる)
        * バー ↔ 小ギア表面のクリアランス ≥ L
        * バーA ↔ バーB の中心線距離 / 2 ≥ L

    小ギア実効半径: x + GEAR_TOL (保守的 5.0 mm / 公称 3.0 mm)

軌道確認:
    クランク半径 R = r のとき → 点O' (バー上の基準点) は円Oの外周に沿う
"""

import sys
import os
import numpy as np
from scipy.optimize import differential_evolution, minimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ═══════════════════════════════════════════════════════════════
#  定数
# ═══════════════════════════════════════════════════════════════
R_LARGE   = 35.65   # 大ギア半径 r [mm]
GEAR_TOL  = 5.0     # 小ギア公差（保守的）[mm]
GEAR_TOL_NOM = 3.0  # 小ギア公差（公称）  [mm]


# ═══════════════════════════════════════════════════════════════
#  ジオメトリ
# ═══════════════════════════════════════════════════════════════
def calc_points(x, y, r=R_LARGE):
    s = np.sqrt(3) * r
    O   = np.array([0.0,    0.0])
    Op  = np.array([r,      s])
    O1  = np.array([2 * r,  0.0])
    O1p = np.array([3 * r,  s])
    P1  = np.array([x,          2 * y - x])
    P1p = np.array([r - x,      s + 2 * y - x])
    P2  = np.array([r + x,      s + 2 * y - x])
    P2p = np.array([2 * r - x,  2 * y - x])
    return O, Op, O1, O1p, P1, P1p, P2, P2p


def crank_radius(x, y):
    """クランク半径 |OP₁| = √(x² + (2y-x)²)"""
    return np.hypot(x, 2 * y - x)


def bar_angle(x, r=R_LARGE):
    """バーの傾き θ [deg]  (tanθ = √3r / (r-2x))"""
    return np.degrees(np.arctan2(np.sqrt(3) * r, r - 2 * x))


# ═══════════════════════════════════════════════════════════════
#  距離計算ユーティリティ
# ═══════════════════════════════════════════════════════════════
def dist_pt_seg(p, a, b):
    """点 p → 線分 a-b の最短距離"""
    v  = b - a
    vv = np.dot(v, v)
    if vv < 1e-12:
        return np.linalg.norm(p - a)
    t  = np.clip(np.dot(p - a, v) / vv, 0.0, 1.0)
    return np.linalg.norm(p - a - t * v)


def dist_seg_seg(a1, a2, b1, b2):
    """2線分間の最短距離（端点4点の組み合わせで近似）"""
    return min(
        dist_pt_seg(a1, b1, b2),
        dist_pt_seg(a2, b1, b2),
        dist_pt_seg(b1, a1, a2),
        dist_pt_seg(b2, a1, a2),
    )


# ═══════════════════════════════════════════════════════════════
#  クリアランス計算
# ═══════════════════════════════════════════════════════════════
def compute_clearances(x, y, gear_tol=GEAR_TOL, r=R_LARGE):
    """
    全干渉ペアのクリアランス (距離 - 実効半径) を返す。
    バー半幅 L の上限 = min(values)。
    """
    O, Op, O1, O1p, P1, P1p, P2, P2p = calc_points(x, y, r)
    eff = x + gear_tol   # 小ギア実効半径

    clrs = {}

    # ── バーA (P1→P1p) vs 他の小ギア ──
    # P1p は自分自身の端点なのでスキップ、P1 も同様
    for name, gc in [("P2", P2), ("P2p", P2p)]:
        clrs[f"barA_vs_{name}"] = dist_pt_seg(gc, P1, P1p) - eff

    # ── バーB (P2→P2p) vs 他の小ギア ──
    for name, gc in [("P1", P1), ("P1p", P1p)]:
        clrs[f"barB_vs_{name}"] = dist_pt_seg(gc, P2, P2p) - eff

    # ── バーA ↔ バーB（バー同士の中心線間距離 / 2）──
    d_ab = dist_seg_seg(P1, P1p, P2, P2p)
    clrs["barA_vs_barB_half"] = d_ab / 2.0

    # ── バー vs 大ギアのシャフト（軸）──
    # シャフト半径を小ギア半径と同等とする（実際は別途指定）
    shaft_r = max(x * 0.5, 3.0)
    for name, gc in [("O", O), ("Op", Op), ("O1", O1), ("O1p", O1p)]:
        clrs[f"barA_vs_{name}_shaft"] = dist_pt_seg(gc, P1,  P1p) - shaft_r
        clrs[f"barB_vs_{name}_shaft"] = dist_pt_seg(gc, P2,  P2p) - shaft_r

    return clrs


def L_max_for(x, y, gear_tol=GEAR_TOL):
    """与えられた (x, y) での最大バー半幅 L"""
    clrs = compute_clearances(x, y, gear_tol)
    return min(clrs.values())


# ═══════════════════════════════════════════════════════════════
#  最適化
# ═══════════════════════════════════════════════════════════════
def feasible(x, y, r=R_LARGE):
    """基本実行可能条件"""
    if x <= 0.5 or y <= 0.5:
        return False
    R = crank_radius(x, y)
    if R > r - x or R < 0.5:        # クランクピンが大ギア内に収まる
        return False
    if 2 * y - x <= 0:              # P1 が原点より上
        return False
    if x >= r / 2.0:                # P1-P2p が重ならない
        return False
    return True


def objective(params):
    x, y = params
    if not feasible(x, y):
        return 1e6
    Lm = L_max_for(x, y)
    if Lm <= 0:
        return 1e6
    return -Lm      # 最小化なので符号反転


# 微分進化法（大域最適解）
bounds = [(1.0, R_LARGE * 0.45), (1.0, R_LARGE * 0.45)]

print("=" * 55)
print("  平行クランク機構 ギア・バー最適化")
print("=" * 55)
print("大域探索中 (differential evolution)...")

de_result = differential_evolution(
    objective, bounds,
    seed=42, maxiter=3000, tol=1e-10, popsize=30, polish=True,
    workers=1,
)

x_opt, y_opt = de_result.x
Lm_opt = -de_result.fun
R_opt  = crank_radius(x_opt, y_opt)
theta  = bar_angle(x_opt)


# ═══════════════════════════════════════════════════════════════
#  結果出力
# ═══════════════════════════════════════════════════════════════
print("\n=== 最適化結果 (保守的公差 +5.0 mm) ===")
print(f"  x  : 小ギア半径          = {x_opt:.4f} mm")
print(f"  y  : Yオフセット          = {y_opt:.4f} mm")
print(f"  L  : バー半幅             = {Lm_opt:.4f} mm")
print(f"  2L : バー幅               = {2 * Lm_opt:.4f} mm")
print(f"  R  : クランク半径         = {R_opt:.4f} mm  (大ギア r = {R_LARGE} mm)")
print(f"  θ  : バー傾角             = {theta:.2f} °")

print("\n=== 各クリアランス詳細 ===")
clrs = compute_clearances(x_opt, y_opt)
for k, v in sorted(clrs.items(), key=lambda kv: kv[1]):
    mark = "  ← ボトルネック" if abs(v - Lm_opt) < 0.01 else ""
    print(f"  {k:<40s} = {v:7.4f} mm{mark}")

# 公称公差でも確認
Lm_nom = L_max_for(x_opt, y_opt, gear_tol=GEAR_TOL_NOM)
print(f"\n  [参考] 公称公差 +3.0 mm での L = {Lm_nom:.4f} mm  (2L = {2*Lm_nom:.4f} mm)")


# ═══════════════════════════════════════════════════════════════
#  点O'の軌道確認
# ═══════════════════════════════════════════════════════════════
print("\n=== 点O'の軌道確認 ===")
print(f"  クランク半径 R = {R_opt:.4f} mm")
print(f"  大ギア半径   r = {R_LARGE} mm")
ratio = R_opt / R_LARGE
print(f"  R / r = {ratio:.4f}")

if abs(ratio - 1.0) < 0.02:
    print("  → R ≈ r : 点O' は円Oの外周に沿う ✓")
elif ratio < 1.0:
    print(f"  → R < r : 点O' は円Oより内側の半径 {R_opt:.2f} mm の円を描く")
else:
    print(f"  → R > r : 点O' は円Oより外側を旋回（制約違反の可能性）")

print(f"\n  [条件式] x² + (2y-x)² = r²  → R = r")
lhs = x_opt**2 + (2 * y_opt - x_opt)**2
print(f"  現在値: {lhs:.4f}  vs  r² = {R_LARGE**2:.4f}")
print(f"  差異: {abs(lhs - R_LARGE**2):.4f} mm²")

print("\n  [参考] R=r となる (x, y) での L_max:")
print(f"  {'x [mm]':>8} {'y [mm]':>10} {'L_max [mm]':>12} {'2L [mm]':>10}")
for xv in np.linspace(3.0, R_LARGE * 0.44, 10):
    disc = R_LARGE**2 - xv**2
    if disc < 0:
        continue
    yv = (xv + np.sqrt(disc)) / 2
    if not feasible(xv, yv):
        continue
    lm = L_max_for(xv, yv)
    print(f"  {xv:8.2f} {yv:10.4f} {max(lm, 0):12.4f} {max(2*lm, 0):10.4f}")


# ═══════════════════════════════════════════════════════════════
#  可視化
# ═══════════════════════════════════════════════════════════════
def draw_bar_rect(ax, a, b, L, color, label, alpha=0.35):
    """バーを矩形で描画"""
    d    = b - a
    dn   = d / np.linalg.norm(d)
    perp = np.array([-dn[1], dn[0]]) * L
    corners = np.array([a + perp, b + perp, b - perp, a - perp])
    ax.fill(corners[:, 0], corners[:, 1], color=color, alpha=alpha)
    ax.plot(
        np.append(corners[:, 0], corners[0, 0]),
        np.append(corners[:, 1], corners[0, 1]),
        color=color, linewidth=2,
    )
    mid = (a + b) / 2
    ax.text(mid[0], mid[1], label, ha="center", va="center",
            fontsize=8, color=color,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.7))


def plot_mechanism(x, y, L, filename="gear_crank_result.png"):
    r   = R_LARGE
    O, Op, O1, O1p, P1, P1p, P2, P2p = calc_points(x, y, r)
    eff = x + GEAR_TOL
    R_c = crank_radius(x, y)

    fig, axes = plt.subplots(1, 2, figsize=(16, 9))

    for ax_idx, ax in enumerate(axes):
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.25)

        # 大ギア（薄い破線円）
        colors_large = ["gray", "gray", "gray", "gray"]
        for center, label in [(O, "O"), (Op, "O'"), (O1, "O₁"), (O1p, "O₁'")]:
            circ = plt.Circle(center, r, fill=False,
                              color="gray", linestyle="--", linewidth=1.2, alpha=0.6)
            ax.add_patch(circ)
            ax.text(center[0], center[1], label,
                    ha="center", va="center", fontsize=9, color="dimgray")

        # クランク軌跡（円）
        for center, col in [(O, "#3366cc"), (Op, "#9933cc"), (O1, "#cc3300")]:
            circ = plt.Circle(center, R_c, fill=False,
                              color=col, linestyle=":", linewidth=1.5, alpha=0.5)
            ax.add_patch(circ)

        # バーA・B
        draw_bar_rect(ax, P1, P1p, L, "#2255bb",
                      f"バーA  2L={2*L:.1f}mm")
        draw_bar_rect(ax, P2, P2p, L, "#bb2222",
                      f"バーB  2L={2*L:.1f}mm")

        # 小ギア（クランクピン）
        pin_info = [
            (P1,  "P₁",  "#2255bb"),
            (P1p, "P₁'", "#2255bb"),
            (P2,  "P₂",  "#bb2222"),
            (P2p, "P₂'", "#bb2222"),
        ]
        for center, label, col in pin_info:
            # ピッチ円（実際のギア）
            ax.add_patch(plt.Circle(center, x, color=col, alpha=0.25))
            # 実効円（干渉判定）
            ax.add_patch(plt.Circle(center, eff, fill=False,
                                    color=col, linewidth=1.5, linestyle="-"))
            ax.text(center[0], center[1] + eff + 1.5, label,
                    ha="center", fontsize=8, color=col)

        # クランクアーム（線）
        for O_c, P_c, col in [(O, P1, "#2255bb"), (Op, P1p, "#9933cc"),
                               (Op, P2, "#bb2222"), (O1, P2p, "#cc5500")]:
            ax.plot([O_c[0], P_c[0]], [O_c[1], P_c[1]],
                    color=col, linewidth=1.5, linestyle="-.", alpha=0.7)

        if ax_idx == 1:
            # 右図: 円Oの外周に沿う条件 R=r の場合を重ねる
            x_r, y_r = x_opt, y_opt
            disc = r**2 - x_r**2
            if disc >= 0:
                y_on = (x_r + np.sqrt(disc)) / 2
                _, _, _, _, P1r, P1pr, P2r, P2pr = calc_points(x_r, y_on, r)
                Lr = L_max_for(x_r, y_on)
                if Lr > 0:
                    for center in [P1r, P1pr, P2r, P2pr]:
                        ax.add_patch(plt.Circle(center, x_r + GEAR_TOL, fill=False,
                                                color="green", linewidth=1, linestyle="--", alpha=0.5))
                    ax.text(r * 1.5, -r * 0.3,
                            f"破線: R=r 条件 (L={Lr:.1f}mm)",
                            color="green", fontsize=8, alpha=0.7)

        # 軸
        ax.set_xlabel("x [mm]", fontsize=10)
        ax.set_ylabel("y [mm]", fontsize=10)
        ax.autoscale_view()
        margin = r * 0.3
        ax.set_xlim(-margin, 4 * r + margin)
        ax.set_ylim(-margin, np.sqrt(3) * r + 2 * r + margin)

    axes[0].set_title(
        f"最適解\n"
        f"x={x:.2f}mm  y={y:.2f}mm  L={L:.2f}mm  2L={2*L:.2f}mm\n"
        f"クランク半径 R={R_c:.2f}mm  (r={R_LARGE}mm, R/r={R_c/R_LARGE:.3f})",
        fontsize=9,
    )
    axes[1].set_title(
        f"O'の軌道\n"
        f"{'R≈r → 円Oの外周に沿う' if abs(R_c/R_LARGE - 1) < 0.02 else f'R={R_c:.2f}mm < r={R_LARGE}mm → 内側を旋回'}\n"
        f"（緑破線: R=r 強制時のギア位置）",
        fontsize=9,
    )

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), "..", filename)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\n図を保存: {os.path.abspath(out_path)}")


plot_mechanism(x_opt, y_opt, Lm_opt)
print("\n完了。")
