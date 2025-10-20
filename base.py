from ortools.sat.python import cp_model

# 1. モデルを作成
model = cp_model.CpModel()

# 全タスクの最長所要時間の合計 (5+4=9) をホライズンとする
horizon = 9

# --- 変数の準備 ---
# 各タスクの「機械ごとの選択肢」をすべて定義する

# タスクAの選択肢
start_A_M1 = model.NewIntVar(0, horizon, 'start_A_M1')
end_A_M1 = model.NewIntVar(0, horizon, 'end_A_M1')
is_A_on_M1 = model.NewBoolVar('is_A_on_M1')
task_A_M1 = model.NewOptionalIntervalVar(start_A_M1, 3, end_A_M1, is_A_on_M1, 'task_A_M1')

start_A_M2 = model.NewIntVar(0, horizon, 'start_A_M2')
end_A_M2 = model.NewIntVar(0, horizon, 'end_A_M2')
is_A_on_M2 = model.NewBoolVar('is_A_on_M2')
task_A_M2 = model.NewOptionalIntervalVar(start_A_M2, 5, end_A_M2, is_A_on_M2, 'task_A_M2')

# タスクBの選択肢
start_B_M1 = model.NewIntVar(0, horizon, 'start_B_M1')
end_B_M1 = model.NewIntVar(0, horizon, 'end_B_M1')
is_B_on_M1 = model.NewBoolVar('is_B_on_M1')
task_B_M1 = model.NewOptionalIntervalVar(start_B_M1, 4, end_B_M1, is_B_on_M1, 'task_B_M1')

start_B_M2 = model.NewIntVar(0, horizon, 'start_B_M2')
end_B_M2 = model.NewIntVar(0, horizon, 'end_B_M2')
is_B_on_M2 = model.NewBoolVar('is_B_on_M2')
task_B_M2 = model.NewOptionalIntervalVar(start_B_M2, 2, end_B_M2, is_B_on_M2, 'task_B_M2')


# 3. 制約（ルール）を追加する

# (ルール1) 選択の制約: 各タスクはM1かM2のどちらか一方だけ実行
model.AddExactlyOne([is_A_on_M1, is_A_on_M2])
model.AddExactlyOne([is_B_on_M1, is_B_on_M2])

# (ルール2) 機械の制約: 各機械は重複不可
model.AddNoOverlap([task_A_M1, task_B_M1]) # M1で動く可能性のあるタスク
model.AddNoOverlap([task_A_M2, task_B_M2]) # M2で動く可能性のあるタスク


# 4. 目的（メイクスパン最小化）を設定する
# 最終的な終了時刻は、ありえる全てのタスクの終了時刻の最大値
all_possible_ends = [end_A_M1, end_A_M2, end_B_M1, end_B_M2]

makespan = model.NewIntVar(0, horizon, 'makespan')
model.AddMaxEquality(makespan, all_possible_ends)
model.Minimize(makespan)


# 5. ソルバーを実行し、結果を表示する
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print('最適解が見つかりました！')
    print(f'最短完了時間 (Makespan): {solver.Value(makespan)} 時間')
    print('---- 最適な割り当て ----')
    
    # どの選択肢が選ばれたかを表示
    if solver.Value(is_A_on_M1):
        print(f'  タスクA -> M1 (開始 {solver.Value(start_A_M1)}, 終了 {solver.Value(end_A_M1)})')
    else:
        print(f'  タスクA -> M2 (開始 {solver.Value(start_A_M2)}, 終了 {solver.Value(end_A_M2)})')

    if solver.Value(is_B_on_M1):
        print(f'  タスクB -> M1 (開始 {solver.Value(start_B_M1)}, 終了 {solver.Value(end_B_M1)})')
    else:
        print(f'  タスクB -> M2 (開始 {solver.Value(start_B_M2)}, 終了 {solver.Value(end_B_M2)})')
else:
    print('解が見つかりませんでした。')