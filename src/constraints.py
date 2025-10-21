"""
制約定義クラス
"""
from ortools.sat.python import cp_model
from typing import List, Dict, Tuple
from .data_models import SchedulingProblem, Player, PartType, Room, TimeSlot
from .constants import ProblemConfig


class SchedulingConstraints:
    """スケジューリングの制約条件を管理するクラス"""
    
    def __init__(self, problem: SchedulingProblem):
        self.problem = problem
        self.model = cp_model.CpModel()
        
        # 変数定義: (part, room, time_slot, instructor) -> BoolVar
        self.session_vars = {}
        
    def create_variables(self):
        """最適化変数を作成"""
        # 各パート、部屋、時間コマ、指導者の組み合わせに対する変数
        for part in self.problem.parts:
            for room in self.problem.rooms:
                for time_slot in self.problem.time_slots:
                    for instructor in self.problem.players:
                        if instructor.is_instructor:
                            var_name = f"session_{part.value}_{room.id}_{time_slot.id}_{instructor.id}"
                            self.session_vars[(part, room.id, time_slot.id, instructor.id)] = \
                                self.model.NewBoolVar(var_name)
    
    def add_basic_constraints(self):
        """基本的な制約条件を追加"""
        # 1. 各パートは1日に1回だけ練習する（指導者は誰でもいい）
        for part in self.problem.parts:
            # そのパートの全セッション（全時間コマ、全部屋、全指導者）
            all_sessions_for_part = []
            for room in self.problem.rooms:
                for time_slot in self.problem.time_slots:
                    for instructor in self.problem.players:
                        if instructor.is_instructor:
                            all_sessions_for_part.append(
                                self.session_vars[(part, room.id, time_slot.id, instructor.id)]
                            )
            
            # 各パートは1日に1回だけ練習する
            if all_sessions_for_part:
                self.model.Add(sum(all_sessions_for_part) == 1)
        
        # 2. 各部屋は各時間コマに最大1つのセッション（1つのパートのみ練習可能）
        for room in self.problem.rooms:
            for time_slot in self.problem.time_slots:
                sessions_in_room = []
                for part in self.problem.parts:
                    for instructor in self.problem.players:
                        if instructor.is_instructor:
                            sessions_in_room.append(
                                self.session_vars[(part, room.id, time_slot.id, instructor.id)]
                            )
                if sessions_in_room:
                    self.model.Add(sum(sessions_in_room) <= 1)
    
    def add_instructor_constraints(self):
        """指導者に関する制約条件を追加"""
        for instructor in self.problem.players:
            if not instructor.is_instructor:
                continue
                
            for time_slot in self.problem.time_slots:
                # その指導者がその時間コマに指導するセッション数
                instructor_sessions = []
                for part in self.problem.parts:
                    for room in self.problem.rooms:
                        if (part, room.id, time_slot.id, instructor.id) in self.session_vars:
                            instructor_sessions.append(
                                self.session_vars[(part, room.id, time_slot.id, instructor.id)]
                            )
                
                # その指導者の所属パートの練習数
                own_part_sessions = []
                for instructor_part in instructor.parts:
                    for room in self.problem.rooms:
                        if (instructor_part, room.id, time_slot.id, instructor.id) in self.session_vars:
                            own_part_sessions.append(
                                self.session_vars[(instructor_part, room.id, time_slot.id, instructor.id)]
                            )
                
                # 同じ時間に指導数≤1（指導者は複数のパートを同時に指導できない）
                if instructor_sessions:
                    self.model.Add(sum(instructor_sessions) <= 1)
    
    def add_player_constraints(self):
        """プレイヤーに関する制約条件を追加"""
        # プレイヤー制約はペナルティ制約として目的関数で処理するため、ここでは何もしない
        pass
    
    def add_equality_constraints(self):
        """均等割り振りのための制約条件を追加"""
        # 各指導者の指導セッション数を均等にする
        instructor_session_counts = []
        for instructor in self.problem.players:
            if not instructor.is_instructor:
                continue
                
            sessions = []
            for part in self.problem.parts:
                for room in self.problem.rooms:
                    for time_slot in self.problem.time_slots:
                        if (part, room.id, time_slot.id, instructor.id) in self.session_vars:
                            sessions.append(
                                self.session_vars[(part, room.id, time_slot.id, instructor.id)]
                            )
            instructor_session_counts.append(sum(sessions))
        
        # 各指導者のセッション数の差を最小化（最大1差まで）
        if len(instructor_session_counts) > 1:
            for i in range(len(instructor_session_counts) - 1):
                self.model.Add(
                    instructor_session_counts[i] - instructor_session_counts[i + 1] <= 1
                )
                self.model.Add(
                    instructor_session_counts[i + 1] - instructor_session_counts[i] <= 1
                )
    
    def setup_all_constraints(self):
        """すべての制約条件を設定"""
        self.create_variables()
        self.add_basic_constraints()
        self.add_instructor_constraints()
        self.add_player_constraints()
        self.add_equality_constraints()
        
        return self.model

