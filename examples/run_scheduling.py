#!/usr/bin/env python3
"""
練習表作成システムの実行例
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scheduling_optimizer import SchedulingOptimizer, create_sample_problem


def main():
    """メイン実行関数"""
    print("=== 練習表作成システム ===")
    print("部屋数: 3, コマ数: 3, パート数: 9")
    print()
    
    # サンプル問題を作成
    print("サンプル問題を作成中...")
    problem = create_sample_problem()
    
    print(f"プレイヤー数: {len(problem.players)}")
    print(f"指導者数: {len([p for p in problem.players if p.is_instructor])}")
    print(f"部屋数: {len(problem.rooms)}")
    print(f"時間コマ数: {len(problem.time_slots)}")
    print(f"パート数: {len(problem.parts)}")
    print()
    
    # プレイヤー情報を表示
    print("=== プレイヤー情報 ===")
    for player in problem.players:
        role = "指導者" if player.is_instructor else "プレイヤー"
        print(f"{player.name} ({role}): {[p.value for p in player.parts]}")
    print()
    
    # 最適化を実行
    optimizer = SchedulingOptimizer(problem)
    solution = optimizer.solve(time_limit_seconds=60)
    
    if solution:
        optimizer.print_solution(solution)
    else:
        print("解が見つかりませんでした。制約条件を緩和するか、時間制限を延長してください。")


if __name__ == "__main__":
    main()
