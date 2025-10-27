#!/usr/bin/env python3
"""
幾何学最適化問題の実行例
"""
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.geometry_optimizer import GeometryOptimizer, create_geometry_problem
from src.geometry_models import Point, GeometryProblem, GeometrySolution


def visualize_solution(problem, solution):
    """解を可視化"""
    if not solution:
        print("解がないため可視化できません")
        return
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # 点をプロット
    origin = (0, 0)
    point_a = (solution.point_a.x, solution.point_a.y)
    point_b = (problem.point_b.x, problem.point_b.y)
    point_c = (solution.point_c.x, solution.point_c.y)
    
    # 各点をプロット
    ax.plot(0, 0, 'ko', markersize=10, label='原点 (0,0)')
    ax.plot(point_a[0], point_a[1], 'ro', markersize=10, label=f'点A ({solution.point_a.x:.2f}, {solution.point_a.y:.2f})')
    ax.plot(point_b[0], point_b[1], 'go', markersize=10, label=f'点B ({point_b[0]}, {point_b[1]})')
    ax.plot(point_c[0], point_c[1], 'mo', markersize=10, label=f'点C ({solution.point_c.x:.2f}, {solution.point_c.y:.2f})')
    
    # 円を描画（距離Dの可視化）
    from matplotlib.patches import Circle
    
    # 原点を中心とした円
    circle1 = Circle((0, 0), solution.d, fill=False, linestyle='--', color='blue', linewidth=1.5)
    ax.add_patch(circle1)
    
    # 点Bを中心とした円
    circle2 = Circle(point_b, solution.d, fill=False, linestyle='--', color='green', linewidth=1.5)
    ax.add_patch(circle2)
    
    # 点Cを中心とした円
    circle3 = Circle(point_c, solution.d, fill=False, linestyle='--', color='purple', linewidth=1.5)
    ax.add_patch(circle3)
    
    # 線を描画
    ax.plot([0, point_a[0]], [0, point_a[1]], 'b-', linewidth=2, label=f'原点-A ({solution.d:.2f})')
    ax.plot([point_a[0], point_b[0]], [point_a[1], point_b[1]], 'g-', linewidth=2, label=f'A-B ({solution.d:.2f})')
    ax.plot([point_a[0], point_c[0]], [point_a[1], point_c[1]], 'm-', linewidth=2, label=f'A-C ({solution.d:.2f})')
    
    # グリッドとラベル
    ax.set_xlabel('X座標', fontsize=12)
    ax.set_ylabel('Y座標', fontsize=12)
    ax.set_title(f'幾何学最適化結果（最小距離D={solution.d:.4f}）', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    ax.legend(loc='upper left')
    
    # 解像度を上げるため範囲を調整
    margin = 5
    ax.set_xlim(-margin, max(point_b[0], point_c[0]) + margin)
    ax.set_ylim(-margin, max(point_b[1], point_c[1], solution.point_c.y) + margin)
    
    plt.tight_layout()
    
    # PNGとして保存
    output_file = 'geometry_solution.png'
    plt.savefig(output_file, dpi=150)
    print(f"\n可視化結果を保存しました: {output_file}")
    
    plt.show()


def main():
    """メイン実行関数"""
    print("=== 幾何学最適化問題 ===")
    print("問題:")
    print("  原点(0,0)から点Aまでの距離 = D")
    print("  点Aから点B(50,35)までの距離 = D")
    print("  点Aから点C(x_C,50)までの距離 = D")
    print("  ただし: x_A > 0, y_A > 0, x_C > 50")
    print("  目的: Dを最小化")
    print()
    
    # 問題を作成
    problem = create_geometry_problem()
    
    print(f"点B: ({problem.point_b.x}, {problem.point_b.y})")
    print(f"点Cのy座標: {problem.point_c_y}")
    print()
    
    # 最適化を実行
    optimizer = GeometryOptimizer(problem)
    solution = optimizer.solve()
    
    if solution:
        optimizer.print_solution(solution)
        
        # 可視化
        print("\n可視化中...")
        visualize_solution(problem, solution)
    else:
        print("解が見つかりませんでした。")


if __name__ == "__main__":
    main()

