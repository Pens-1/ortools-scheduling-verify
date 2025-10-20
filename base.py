from ortools.sat.python import cp_model

# 1. モデルを作成
model = cp_model.CpModel()

# 2. 変数を定義する
# 全タスクの合計時間 (3+2+4+1 = 10) をホライズン（最大時間）とする
horizon = 10

# タスクA (M1, 3h)
start_A = model.NewIntVar(0, horizon, 'start_A')
duration_A = 3
end_A = model.NewIntVar(0, horizon, 'end_A')
task_A = model.NewIntervalVar(start_A, duration_A, end_A, 'task_A')

# タスクB (M2, 2h)
start_B = model.NewIntVar(0, horizon, 'start_B')
duration_B = 2
end_B = model.NewIntVar(0, horizon, 'end_B')
task_B = model.NewIntervalVar(start_B, duration_B, end_B, 'task_B')

# タスクC (M1, 4h)
start_C = model.NewIntVar(0, horizon, 'start_C')
duration_C = 4
end_C = model.NewIntVar(0, horizon, 'end_C')
task_C = model.NewIntervalVar(start_C, duration_C, end_C, 'task_C')

# タスクD (M2, 1h)
start_D = model.NewIntVar(0, horizon, 'start_D')
duration_D = 1
end_D = model.NewIntVar(0, horizon, 'end_D')
task_D = model.NewIntervalVar(start_D, duration_D, end_D, 'task_D')


# 3. 制約（ルール）を追加する

# (ルール1) 機械ごとの重複禁止
tasks_on_m1 = [task_A, task_C]
model.AddNoOverlap(tasks_on_m1)

tasks_on_m2 = [task_B, task_D]
model.AddNoOverlap(tasks_on_m2)

# (ルール2) 依存関係 (A->C, B->D)
model.Add(start_C >= end_A)
model.Add(start_D >= end_B)


# 4. 目的（メイクスパン最小化）を設定する
# 最終的に終わるタスクは C と D のどちらか
makespan = model.NewIntVar(0, horizon, 'makespan')
model.AddMaxEquality(makespan, [end_C, end_D])
model.Minimize(makespan)


# 5. ソルバーを実行し、結果を表示する
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print('最適解が見つかりました！')
    print(f'---- 機械 1 (M1) ----')
    print(f'タスクA: 開始 {solver.Value(start_A)} -> 終了 {solver.Value(end_A)} (3h)')
    print(f'タスクC: 開始 {solver.Value(start_C)} -> 終了 {solver.Value(end_C)} (4h)')
    print(f'---- 機械 2 (M2) ----')
    print(f'タスクB: 開始 {solver.Value(start_B)} -> 終了 {solver.Value(end_B)} (2h)')
    print(f'タスクD: 開始 {solver.Value(start_D)} -> 終了 {solver.Value(end_D)} (1h)')
    print('---------------------')
    print(f'最短完了時間 (Makespan): {solver.Value(makespan)} 時間')
else:
    print('解が見つかりませんでした。')