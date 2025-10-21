"""
スケジューリング最適化の目的関数
"""
from typing import List, Optional
from ortools.sat.python import cp_model
from .data_models import SchedulingProblem, PartType


class SchedulingObjectives:
    """スケジューリングの目的関数を管理するクラス"""
    
    def __init__(self, problem: SchedulingProblem, session_vars: dict):
        self.problem = problem
        self.session_vars = session_vars
    
    def setup_objective(self, model: cp_model.CpModel, player_priority: int = 100):
        """目的関数を設定"""
        # 均等割り振りの目的関数
        equality_objective = self.create_equality_objective(model)
        
        # プレイヤー制約違反ペナルティ（優先度付き）
        player_penalty = self.create_player_penalty(model, player_priority)
        
        # 目的関数を設定
        if player_penalty is not None:
            model.Minimize(equality_objective + player_penalty)
        else:
            model.Minimize(equality_objective)
    
    def create_equality_objective(self, model: cp_model.CpModel):
        """均等割り振りの目的関数を作成"""
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
        
        # セッション数の分散を最小化
        if len(instructor_session_counts) > 1:
            # 分散を最小化（簡略化：最大値と最小値の差を最小化）
            max_var = model.NewIntVar(0, 100, "max_sessions")
            min_var = model.NewIntVar(0, 100, "min_sessions")
            
            for count in instructor_session_counts:
                model.Add(count <= max_var)
                model.Add(count >= min_var)
            
            return max_var - min_var
        else:
            # 指導者が1人の場合は単純にセッション数を最大化
            return -sum(instructor_session_counts)  # 最大化のため負の値を返す
    
    def create_player_penalty(self, model: cp_model.CpModel, priority_level: int = 100):
        """プレイヤー制約違反ペナルティを作成（100段階の優先度）"""
        player_violations = []
        
        for player in self.problem.players:
            if player.is_instructor:
                continue
                
            for time_slot in self.problem.time_slots:
                # そのプレイヤーの所属パートの練習数
                player_part_sessions = []
                for player_part in player.parts:
                    for room in self.problem.rooms:
                        for instructor in self.problem.players:
                            if instructor.is_instructor:
                                if (player_part, room.id, time_slot.id, instructor.id) in self.session_vars:
                                    player_part_sessions.append(
                                        self.session_vars[(player_part, room.id, time_slot.id, instructor.id)]
                                    )
                
                # 違反数 = max(0, 所属パート数 - 1)
                if player_part_sessions:
                    violation = model.NewIntVar(0, 10, f"player_violation_{player.id}_{time_slot.id}")
                    model.Add(violation >= sum(player_part_sessions) - 1)
                    
                    # 優先度を適用（100段階）
                    weighted_violation = model.NewIntVar(0, 1000, f"weighted_violation_{player.id}_{time_slot.id}")
                    model.Add(weighted_violation == violation * priority_level)
                    player_violations.append(weighted_violation)
        
        return sum(player_violations) if player_violations else None
