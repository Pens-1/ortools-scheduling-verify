from ortools.sat.python import cp_model

# 1. モデルを作成
model = cp_model.CpModel()

# 2. 変数を定義する
# 全タスクの合計時間 (3+2+4+1 = 10) をホライズンとする
horizon = 10

# --- ジョブ 1 ---
# 工程A (M1, 3h)
start_1A = model.NewIntVar(0, horizon, 'start_1A')
duration_1A = 3
end_1A = model.NewIntVar(0, horizon, 'end_1A')
task_1A = model.NewIntervalVar(start_1A, duration_1A, end_1A, 'task_1A_M1')

# 工程B (M2, 2h)
start_1B = model.NewIntVar(0, horizon, 'start_1B')
duration_1B = 2
end_1B = model.NewIntVar(0, horizon, 'end_1B')
task_1B = model.NewIntervalVar(start_1B, duration_1B, end_1B, 'task_1B_M2')

# --- ジョブ 2 ---
# 工程C (M2, 4h)
start_2C = model.NewIntVar(0, horizon, 'start_2C')
duration_2C = 4
end_2C = model.NewIntVar(0, horizon, 'end_2C')
task_2C = model.NewIntervalVar(start_2C, duration_2C, end_2C, 'task_2C_M2')

# 工程D (M1, 1h)
start_2D = model.NewIntVar(0, horizon, 'start_2D')
duration_2D = 1
end_2D = model.NewIntVar(0, horizon, 'end_2D')
task_2D = model.NewIntervalVar(start_2D, duration_2D, end_2D, 'task_2D_M1')


# 3. 制約（ルール）を追加する

# (ルール1) ジョブ内の順序 (依存関係)
# ジョブ1: A -> B
model.Add(start_1B >= end_1A)
# ジョブ2: C -> D
model.Add(start_2D >= end_2C)

# (ルール2) 機械ごとの重複禁止
# 機械1 (M1) で実行されるタスク
tasks_on_m1 = [task_1A, task_2D]
model.AddNoOverlap(tasks_on_m1)

# 機械2 (M2) で実行されるタスク
tasks_on_m2 = [task_1B, task_2C]
model.AddNoOverlap(tasks_on_m2)


# 4. 目的（メイクスパン最小化）を設定する
# 最終的に終わるタスクは、各ジョブの最後のタスク (1B と 2D)
last_tasks = [end_1B, end_2D]

makespan = model.NewIntVar(0, horizon, 'makespan')
model.AddMaxEquality(makespan, last_tasks)
model.Minimize(makespan)


# 5. ソルバーを実行し、結果を表示する
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print('最適解が見つかりました！')
    print(f'---- 機械 1 (M1) ----')
    print(f'  工程A (Job1): 開始 {solver.Value(start_1A)} -> 終了 {solver.Value(end_1A)} (3h)')
    print(f'  工程D (Job2): 開始 {solver.Value(start_2D)} -> 終了 {solver.Value(end_2D)} (1h)')
    print(f'---- 機械 2 (M2) ----')
    print(f'  工程C (Job2): 開始 {solver.Value(start_2C)} -> 終了 {solver.Value(end_2C)} (4h)')
    print(f'  工程B (Job1): 開始 {solver.Value(start_1B)} -> 終了 {solver.Value(end_1B)} (2h)')
    print('---------------------')
    print(f'最短完了時間 (Makespan): {solver.Value(makespan)} 時間')
else:
    print('解が見つかりませんでした。')