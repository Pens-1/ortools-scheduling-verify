"""
幾何学最適化ソルバー
"""
import time
from typing import Optional
import numpy as np
from scipy.optimize import minimize
from .geometry_models import Point, GeometryProblem, GeometrySolution


class GeometryOptimizer:
    """幾何学最適化のソルバークラス"""
    
    def __init__(self, problem: GeometryProblem):
        self.problem = problem
        
    def solve(self) -> Optional[GeometrySolution]:
        """幾何学最適化問題を解く"""
        print("幾何学最適化を実行中...")
        
        # 変数: [x_A, y_A, x_C, D]
        # 初期値の設定
        initial_values = np.array([30.0, 30.0, 60.0, 50.0])
        
        # 境界条件: x_A > 0, y_A > 0, x_C > 50, D > 0
        bounds = [
            (1e-6, None),  # x_A
            (1e-6, None),  # y_A
            (50 + 1e-6, None),  # x_C
            (1e-6, None)  # D
        ]
        
        # 等式制約
        constraints = [
            {
                'type': 'eq',
                'fun': lambda vars: self._constraint_origin_to_a(vars)
            },
            {
                'type': 'eq',
                'fun': lambda vars: self._constraint_a_to_b(vars)
            },
            {
                'type': 'eq',
                'fun': lambda vars: self._constraint_a_to_c(vars)
            }
        ]
        
        start_time = time.time()
        
        # SLSQP法で最適化
        result = minimize(
            fun=lambda vars: vars[3],  # Dを最小化
            x0=initial_values,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'maxiter': 1000}
        )
        
        solve_time = time.time() - start_time
        
        if result.success:
            print(f"解が見つかりました")
            print(f"求解時間: {solve_time:.4f}秒")
            print(f"最適化ステータス: {result.message}")
            
            x_a, y_a, x_c, d = result.x
            
            # is_optimalの判定: success かつ 収束ステータスが良好
            # SLSQP法では、result.success=True で収束成功を意味する
            is_optimal = result.success and result.status == 0
            
            return GeometrySolution(
                d=d,
                point_a=Point(x=x_a, y=y_a),
                point_c=Point(x=x_c, y=self.problem.point_c_y),
                is_optimal=is_optimal,
                solve_time_seconds=solve_time
            )
        else:
            print(f"解が見つかりませんでした: {result.message}")
            return None
    
    def _constraint_origin_to_a(self, vars):
        """原点(0,0)から点Aまでの距離 = D"""
        x_a, y_a, x_c, d = vars
        return np.sqrt(x_a**2 + y_a**2) - d
    
    def _constraint_a_to_b(self, vars):
        """点Aから点Bまでの距離 = D"""
        x_a, y_a, x_c, d = vars
        dx = x_a - self.problem.point_b.x
        dy = y_a - self.problem.point_b.y
        return np.sqrt(dx**2 + dy**2) - d
    
    def _constraint_a_to_c(self, vars):
        """点Aから点Cまでの距離 = D"""
        x_a, y_a, x_c, d = vars
        dx = x_a - x_c
        dy = y_a - self.problem.point_c_y
        return np.sqrt(dx**2 + dy**2) - d
    
    def print_solution(self, solution: GeometrySolution):
        """解を分かりやすく表示"""
        if not solution:
            print("解がありません")
            return
        
        print(f"\n=== 幾何学最適化結果 ===")
        print(f"最小距離 D: {solution.d:.6f}")
        print(f"点Aの座標: ({solution.point_a.x:.6f}, {solution.point_a.y:.6f})")
        print(f"点Cの座標: ({solution.point_c.x:.6f}, {solution.point_c.y:.6f})")
        print(f"最適解: {'はい' if solution.is_optimal else 'いいえ'}")
        print(f"求解時間: {solution.solve_time_seconds:.4f}秒")
        
        # 制約条件の検証
        verification = solution.verify_constraints(self.problem)
        print(f"\n=== 制約条件の検証 ===")
        print(f"原点-O間の距離: {verification['origin_to_a_distance']:.6f}")
        print(f"A-B間の距離: {verification['a_to_b_distance']:.6f}")
        print(f"A-C間の距離: {verification['a_to_c_distance']:.6f}")
        print(f"すべての距離が等しい: {verification['all_distances_equal']}")
        print(f"点Aのx座標 > 0: {verification['point_a_x_positive']}")
        print(f"点Aのy座標 > 0: {verification['point_a_y_positive']}")
        print(f"点Cのx座標 > 50: {verification['point_c_x_greater_than_50']}")


def create_geometry_problem() -> GeometryProblem:
    """サンプル幾何学問題を作成"""
    point_b = Point(x=50, y=35)
    point_c_y = 50.0
    
    return GeometryProblem(
        point_b=point_b,
        point_c_y=point_c_y
    )

