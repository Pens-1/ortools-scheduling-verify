"""
幾何学最適化問題のデータモデル
"""
from dataclasses import dataclass


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
    point_b_y: float  # 点Bのy座標(固定)
    point_c_y: float  # 点Cのy座標(固定)

    def __post_init__(self):
        """初期化後の検証"""
        assert self.point_b_y > 0, "点Bのy座標は正の値でなければなりません"
        assert self.point_c_y > 0, "点Cのy座標は正の値でなければなりません"


@dataclass
class GeometrySolution:
    """幾何学最適化の解"""
    d: float  # 最小距離
    point_a: Point  # 点Aの座標
    point_b: Point  # 点Bの座標
    point_c: Point  # 点Cの座標
    is_optimal: bool  # 最適解かどうか
    solve_time_seconds: float  # 求解時間
    
    def verify_constraints(self, problem: GeometryProblem) -> dict:
        """制約条件の検証結果を返す"""
        origin = Point(0, 0)
        
        # 3つの距離がすべてDに等しいか確認
        d1 = origin.distance_to(self.point_a)
        d2 = self.point_a.distance_to(self.point_b)
        d3 = self.point_a.distance_to(self.point_c)
        
        tolerance = 1e-5
        
        return {
            "origin_to_a_distance": d1,
            "a_to_b_distance": d2,
            "a_to_c_distance": d3,
            "all_distances_equal": abs(d1 - self.d) < tolerance and abs(d2 - self.d) < tolerance and abs(d3 - self.d) < tolerance,
            "point_x_a_within_range": 100 < self.point_a.x and self.point_a.x < 700,
            "point_y_a_within_range": self.point_a.y > 0,
            "point_x_b_within_range": 770 < self.point_b.x and self.point_b.x < 830,
            "point_x_c_within_range": 710 < self.point_c.x and self.point_c.x < 890
        }

