"""
メインのスケジューリング最適化クラス
"""
import time
from typing import List, Optional
from ortools.sat.python import cp_model
from .data_models import (
    SchedulingProblem, SchedulingSolution, PracticeSession, 
    Player, PartType, Room, TimeSlot
)
from .constraints import SchedulingConstraints
from .objectives import SchedulingObjectives
from .constants import SchedulingConfig, ProblemConfig


class SchedulingOptimizer:
    """スケジューリング最適化のメインクラス"""
    
    def __init__(self, problem: SchedulingProblem):
        self.problem = problem
        self.constraints = SchedulingConstraints(problem)
        self.objectives = None  # 制約設定後に初期化
        
    def solve(self, time_limit_seconds: int = SchedulingConfig.DEFAULT_TIME_LIMIT, equality_weight: int = SchedulingConfig.DEFAULT_EQUALITY_WEIGHT) -> Optional[SchedulingSolution]:
        """スケジューリング問題を解く"""
        print("制約条件を設定中...")
        model = self.constraints.setup_all_constraints()
        
        print("目的関数を設定中...")
        self.objectives = SchedulingObjectives(self.problem, self.constraints.session_vars)
        self.objectives.setup_objective(model, equality_weight)
        
        print("ソルバーを実行中...")
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        
        start_time = time.time()
        status = solver.Solve(model)
        solve_time = time.time() - start_time
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"解が見つかりました (ステータス: {status})")
            print(f"求解時間: {solve_time:.2f}秒")
            
            sessions = self._extract_solution(solver)
            objective_value = self._calculate_objective_value(sessions)
            
            return SchedulingSolution(
                sessions=sessions,
                objective_value=objective_value,
                is_optimal=(status == cp_model.OPTIMAL),
                solve_time_seconds=solve_time
            )
        else:
            print(f"解が見つかりませんでした (ステータス: {status})")
            return None
    
    
    def _extract_solution(self, solver: cp_model.CpSolver) -> List[PracticeSession]:
        """ソルバーの解から練習セッションを抽出"""
        sessions = []
        session_id = 0
        
        for part in self.problem.parts:
            for room in self.problem.rooms:
                for time_slot in self.problem.time_slots:
                    for instructor in self.problem.players:
                        if instructor.is_instructor:
                            var = self.constraints.session_vars.get((part, room.id, time_slot.id, instructor.id))
                            if var is not None and solver.Value(var) == 1:
                                # 参加プレイヤーを取得
                                player_ids = [p.id for p in self.problem.get_players_by_part(part)]
                                
                                session = PracticeSession(
                                    id=session_id,
                                    part=part,
                                    room_id=room.id,
                                    time_slot_id=time_slot.id,
                                    instructor_id=instructor.id,
                                    player_ids=player_ids
                                )
                                sessions.append(session)
                                session_id += 1
        
        return sessions
    
    def _calculate_objective_value(self, sessions: List[PracticeSession]) -> float:
        """目的関数の値を計算"""
        # 指導者ごとのセッション数を計算
        instructor_counts = {}
        for session in sessions:
            instructor_id = session.instructor_id
            instructor_counts[instructor_id] = instructor_counts.get(instructor_id, 0) + 1
        
        if not instructor_counts:
            return 0.0
        
        # 分散を計算
        counts = list(instructor_counts.values())
        mean_count = sum(counts) / len(counts)
        variance = sum((count - mean_count) ** 2 for count in counts) / len(counts)
        
        return -variance  # 分散を最小化したいので負の値を返す
    
    def print_solution(self, solution: SchedulingSolution):
        """解を分かりやすく表示"""
        if not solution:
            print("解がありません")
            return
        
        print(f"\n=== スケジュール結果 ===")
        print(f"総セッション数: {len(solution.sessions)}")
        print(f"目的関数値: {solution.objective_value:.2f}")
        print(f"最適解: {'はい' if solution.is_optimal else 'いいえ'}")
        print(f"求解時間: {solution.solve_time_seconds:.2f}秒")
        
        # 指導者ごとのセッション数
        instructor_counts = {}
        for session in solution.sessions:
            instructor_id = session.instructor_id
            instructor_counts[instructor_id] = instructor_counts.get(instructor_id, 0) + 1
        
        print(f"\n=== 指導者別セッション数 ===")
        for instructor in self.problem.players:
            if instructor.is_instructor:
                count = instructor_counts.get(instructor.id, 0)
                print(f"{instructor.name} ({instructor.parts}): {count}セッション")
        
        # スケジュール表を表示
        print(f"\n=== スケジュール表 ===")
        schedule_matrix = solution.get_schedule_matrix()
        
        # ヘッダー
        print("時間\\部屋", end="")
        for room in self.problem.rooms:
            print(f"\t{room.name}", end="")
        print()
        
        # 各行
        for time_slot in self.problem.time_slots:
            print(f"{time_slot.name}", end="")
            for room in self.problem.rooms:
                sessions = schedule_matrix.get(time_slot.id, {}).get(room.id, [])
                if sessions:
                    # 複数セッションがある場合はカンマ区切りで表示
                    session_strs = []
                    for session in sessions:
                        instructor = next(i for i in self.problem.players if i.id == session.instructor_id)
                        session_strs.append(f"{session.part.value}({instructor.name})")
                    print(f"\t{','.join(session_strs)}", end="")
                else:
                    print(f"\t-", end="")
            print()


def create_sample_problem() -> SchedulingProblem:
    """サンプル問題を作成"""
    # パート定義
    parts = [
        PartType.A, PartType.B, PartType.C, PartType.D, PartType.E,
        PartType.F, PartType.G, PartType.H, PartType.I
    ]
    
    # 部屋定義
    rooms = []
    for i in range(1, ProblemConfig.NUM_ROOMS + 1):
        rooms.append(Room(id=i, name=f"練習室{chr(64 + i)}"))  # A, B, C, D
    
    # 時間コマ定義
    time_slots = []
    num_time_slots = ProblemConfig.get_num_time_slots()
    for i in range(1, num_time_slots + 1):
        time_slots.append(TimeSlot(id=i, name=f"{i}限目"))
    
    # プレイヤー定義（指導者含む）
    players = [
        # 指導者（5人、全員2つのパートに所属）
        Player(id=1, name="田中先生", parts=[PartType.A, PartType.B], is_instructor=True, overlap_priority=100),  # 厳格
        Player(id=2, name="佐藤先生", parts=[PartType.C, PartType.D], is_instructor=True, overlap_priority=75),   # やや厳格
        Player(id=3, name="鈴木先生", parts=[PartType.E, PartType.F], is_instructor=True, overlap_priority=50),   # 中程度
        Player(id=4, name="高橋先生", parts=[PartType.G, PartType.H], is_instructor=True, overlap_priority=25),   # 緩い
        Player(id=5, name="山田先生", parts=[PartType.I, PartType.A], is_instructor=True, overlap_priority=0),    # 制限なし
        # 一般プレイヤー（複数パート所属、個人別優先度設定）
        Player(id=6, name="佐々木さん", parts=[PartType.A, PartType.B], overlap_priority=100),  # 厳格
        Player(id=7, name="松本さん", parts=[PartType.B, PartType.C], overlap_priority=50),   # 中程度
        Player(id=8, name="井上さん", parts=[PartType.C, PartType.D], overlap_priority=0),    # 制限なし
        Player(id=9, name="木村さん", parts=[PartType.D, PartType.E], overlap_priority=100),  # 厳格
        Player(id=10, name="林さん", parts=[PartType.E, PartType.F], overlap_priority=25),    # 緩い
        Player(id=11, name="清水さん", parts=[PartType.F, PartType.G], overlap_priority=75),   # やや厳格
        Player(id=12, name="森さん", parts=[PartType.G, PartType.H], overlap_priority=0),     # 制限なし
        Player(id=13, name="石川さん", parts=[PartType.H, PartType.I], overlap_priority=100), # 厳格
        Player(id=14, name="田村さん", parts=[PartType.I, PartType.A], overlap_priority=50),   # 中程度
        Player(id=15, name="山田さん", parts=[PartType.A, PartType.C], overlap_priority=75),   # やや厳格
        Player(id=16, name="佐藤さん", parts=[PartType.B, PartType.D], overlap_priority=25),   # 緩い
        Player(id=17, name="鈴木さん", parts=[PartType.C, PartType.E], overlap_priority=50),   # 中程度
        Player(id=18, name="高橋さん", parts=[PartType.D, PartType.F], overlap_priority=100),  # 厳格
        Player(id=19, name="伊藤さん", parts=[PartType.E, PartType.G], overlap_priority=0),    # 制限なし
        Player(id=20, name="渡辺さん", parts=[PartType.F, PartType.H], overlap_priority=75),   # やや厳格
        Player(id=21, name="中村さん", parts=[PartType.G, PartType.I], overlap_priority=25),   # 緩い
        Player(id=22, name="小林さん", parts=[PartType.H, PartType.A], overlap_priority=50),   # 中程度
        Player(id=23, name="加藤さん", parts=[PartType.I, PartType.B], overlap_priority=100),  # 厳格
    ]
    
    return SchedulingProblem(
        players=players,
        rooms=rooms,
        time_slots=time_slots,
        parts=parts
    )

