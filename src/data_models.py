"""
データモデルの定義
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class PartType(Enum):
    """パートの種類"""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    H = "H"
    I = "I"


@dataclass
class Player:
    """プレイヤー（参加者）"""
    id: int
    name: str
    parts: List[PartType]  # 所属パート（複数可）
    is_instructor: bool = False  # 指導者かどうか


@dataclass
class Room:
    """練習室"""
    id: int
    name: str


@dataclass
class TimeSlot:
    """時間コマ"""
    id: int
    name: str  # 例: "1限目", "2限目", "3限目"


@dataclass
class PracticeSession:
    """練習セッション"""
    id: int
    part: PartType
    room_id: int
    time_slot_id: int
    instructor_id: int
    player_ids: List[int]  # 参加プレイヤーのIDリスト


@dataclass
class SchedulingProblem:
    """スケジューリング問題の全体設定"""
    players: List[Player]  # プレイヤーリスト（指導者含む）
    rooms: List[Room]
    time_slots: List[TimeSlot]
    parts: List[PartType]
    
    def __post_init__(self):
        """初期化後の検証"""
        assert len(self.rooms) > 0, "部屋が設定されていません"
        assert len(self.time_slots) > 0, "時間コマが設定されていません"
        assert len(self.parts) > 0, "パートが設定されていません"
        assert len(self.players) > 0, "プレイヤーが設定されていません"
    
    def get_players_by_part(self, part: PartType) -> List[Player]:
        """指定されたパートのプレイヤーリストを取得"""
        return [player for player in self.players if part in player.parts]
    
    def get_instructors_by_part(self, part: PartType) -> List[Player]:
        """指定されたパートの指導者リストを取得"""
        return [player for player in self.players if part in player.parts and player.is_instructor]
    
    def get_regular_players_by_part(self, part: PartType) -> List[Player]:
        """指定されたパートの一般プレイヤーリストを取得"""
        return [player for player in self.players if part in player.parts and not player.is_instructor]


@dataclass
class SchedulingSolution:
    """スケジューリングの解"""
    sessions: List[PracticeSession]
    objective_value: float
    is_optimal: bool
    solve_time_seconds: float
    
    def get_schedule_matrix(self) -> Dict[int, Dict[int, List[PracticeSession]]]:
        """時間コマ×部屋のスケジュールマトリックスを返す（複数セッション対応）"""
        matrix = {}
        for time_slot in range(1, 4):  # 時間コマID: 1, 2, 3
            matrix[time_slot] = {}
            for room in range(1, 4):  # 部屋ID: 1, 2, 3
                matrix[time_slot][room] = []
        
        for session in self.sessions:
            matrix[session.time_slot_id][session.room_id].append(session)
        
        return matrix

