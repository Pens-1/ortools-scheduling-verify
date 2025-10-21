"""
スケジューリングシステムの定数定義
"""

# 制約関連
class ConstraintLimits:
    """制約の上限値"""
    MAX_VIOLATIONS = 10        # 最大違反数
    MAX_WEIGHTED_VIOLATIONS = 1000  # 最大重み付き違反数
    MAX_SESSIONS = 100         # 最大セッション数
    MAX_WEIGHTED_EQUALITY = 10000  # 最大重み付き均等性

# スケジューリング設定
class SchedulingConfig:
    """スケジューリング設定"""
    DEFAULT_TIME_LIMIT = 30    # デフォルト時間制限（秒）
    DEFAULT_EQUALITY_WEIGHT = 100  # デフォルト均等性重み
    DEFAULT_PRIORITY = 50  # デフォルト優先度

# パート・部屋・時間コマ設定
class ProblemConfig:
    """問題設定"""
    NUM_ROOMS = 3              # 部屋数
    NUM_TIME_SLOTS = 3         # 時間コマ数
    NUM_PARTS = 9              # パート数
    NUM_INSTRUCTORS = 5        # 指導者数
    NUM_GENERAL_PLAYERS = 18   # 一般プレイヤー数
