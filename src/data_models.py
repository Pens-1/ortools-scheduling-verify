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
class Instructor:
    """指導者"""
    id: int
    name: str


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


@dataclass
class SchedulingProblem:
    """スケジューリング問題の全体設定"""
    instructors: List[Instructor]
    rooms: List[Room]
    time_slots: List[TimeSlot]
    parts: List[PartType]
    
    def __post_init__(self):
        """初期化後の検証"""
        assert len(self.rooms) > 0, "部屋が設定されていません"
        assert len(self.time_slots) > 0, "時間コマが設定されていません"
        assert len(self.parts) > 0, "パートが設定されていません"
        assert len(self.instructors) > 0, "指導者が設定されていません"


@dataclass
class SchedulingSolution:
    """スケジューリングの解"""
    sessions: List[PracticeSession]
    objective_value: float
    is_optimal: bool
    solve_time_seconds: float
    
    def get_schedule_matrix(self) -> Dict[int, Dict[int, Optional[PracticeSession]]]:
        """時間コマ×部屋のスケジュールマトリックスを返す"""
        matrix = {}
        for time_slot in range(len(self.problem.time_slots)):  # 実際の時間コマ数
            matrix[time_slot] = {}
            for room in range(len(self.problem.rooms)):  # 実際の部屋数
                matrix[time_slot][room] = None
        
        for session in self.sessions:
            matrix[session.time_slot_id][session.room_id] = session
        
        return matrix

