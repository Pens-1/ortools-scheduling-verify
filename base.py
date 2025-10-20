from ortools.sat.python import cp_model

model = cp_model.CpModel()
solver = cp_model.CpSolver()

horizon = 9

# 全タスクの期間の合計
horizon = 3 + 2 + 4

# 各タスクの「開始」「終了」「期間」を定義します
# model.NewIntVar(最小値, 最大値, '名前') で変数を作成

# タスクA (期間 3)
start_A = model.NewIntVar(0, horizon, 'start_A')
duration_A = 3
end_A = model.NewIntVar(0, horizon, 'end_A')
task_A = model.NewIntervalVar(start_A, duration_A, end_A, 'task_A')

# タスクB (期間 2)
start_B = model.NewIntVar(0, horizon, 'start_B')
duration_B = 2
end_B = model.NewIntVar(0, horizon, 'end_B')
task_B = model.NewIntervalVar(start_B, duration_B, end_B, 'task_B')

# タスクC (期間 4)
start_C = model.NewIntVar(0, horizon, 'start_C')
duration_C = 4
end_C = model.NewIntVar(0, horizon, 'end_C')
task_C = model.NewIntervalVar(start_C, duration_C, end_C, 'task_C')

# 3. 制約を追加
# [task_A, task_B, task_C] のリストにあるタスクは、
# 時間的に重複してはいけない、という制約
model.AddNoOverlap([task_A, task_B, task_C])

# 4. 目的を設定
# 全体の終了時刻（makespan）を表す変数を作る
makespan = model.NewIntVar(0, horizon, 'makespan')

# makespan が A, B, C の終了時刻の最大値と等しくなるように制約
model.AddMaxEquality(makespan, [end_A, end_B, end_C])

# その makespan を最小化する
model.Minimize(makespan)


# 5. ソルバーを実行
status = solver.Solve(model)

# 6. 結果の表示
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('スケジュールが見つかりました！')
    print(f'タスクA: 開始 {solver.Value(start_A)}, 終了 {solver.Value(end_A)}')
    print(f'タスクB: 開始 {solver.Value(start_B)}, 終了 {solver.Value(end_B)}')
    print(f'タスクC: 開始 {solver.Value(start_C)}, 終了 {solver.Value(end_C)}')
    print(f'最短完了時間 (Makespan): {solver.Value(makespan)} 時間')
else:
    print('解が見つかりませんでした。')