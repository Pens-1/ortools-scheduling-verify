"""
幾何学最適化問題のデータモデル
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Point:
    """2D座標点"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """他の点までのユークリッド距離を計算"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass
class GeometryProblem:
    """幾何学最適化問題の設定"""
    point_b: Point  # 点B
    point_c_y: float  # 点Cのy座標(固定)
    
    def __post_init__(self):
        """初期化後の検証"""
        assert self.point_c_y > 0, "点Cのy座標は正の値でなければなりません"


@dataclass
class GeometrySolution:
    """幾何学最適化の解"""
    d: float  # 最小距離
    point_a: Point  # 点Aの座標
    point_c: Point  # 点Cの座標
    is_optimal: bool  # 最適解かどうか
    solve_time_seconds: float  # 求解時間
    
    def verify_constraints(self, problem: GeometryProblem) -> dict:
        """制約条件の検証結果を返す"""
        origin = Point(0, 0)
        point_b = problem.point_b
        
        # 3つの距離がすべてDに等しいか確認
        d1 = origin.distance_to(self.point_a)
        d2 = self.point_a.distance_to(point_b)
        d3 = self.point_a.distance_to(self.point_c)
        
        tolerance = 1e-5
        
        return {
            "origin_to_a_distance": d1,
            "a_to_b_distance": d2,
            "a_to_c_distance": d3,
            "all_distances_equal": abs(d1 - self.d) < tolerance and abs(d2 - self.d) < tolerance and abs(d3 - self.d) < tolerance,
            "point_a_x_positive": self.point_a.x > 0,
            "point_a_y_positive": self.point_a.y > 0,
            "point_c_x_greater_than_50": self.point_c.x > 50
        }

