# OR-Tools スケジューリング最適化システム

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-Latest-green.svg)](https://developers.google.com/optimization)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 概要

このプロジェクトは、Google OR-Toolsを使用して練習室でのパート別練習スケジュールを最適化するシステムです。複数のパート、部屋、時間コマ、指導者、プレイヤーを考慮し、制約条件を満たしながら最適なスケジュールを自動生成します。

## 主な機能

- 🎯 **制約充足最適化**: 複雑な制約条件を満たすスケジュール生成
- ⚖️ **均等負荷分散**: 指導者の負荷を均等に分散
- 👥 **個人別優先度**: プレイヤーの重複優先度に基づく制約
- 🏢 **多部屋対応**: 複数の練習室での同時練習
- ⏰ **時間コマ管理**: 効率的な時間割作成
- 📊 **可視化**: 分かりやすいスケジュール表の表示

## システム構成

```
ortools-scheduling-verify/
├── src/                          # ソースコード
│   ├── __init__.py              # パッケージ初期化
│   ├── scheduling_optimizer.py  # メイン最適化クラス
│   ├── constraints.py           # 制約条件定義
│   ├── objectives.py            # 目的関数定義
│   ├── data_models.py           # データモデル定義
│   └── constants.py             # 定数定義
├── examples/                     # 実行例
│   └── run_scheduling.py        # サンプル実行
├── 仕様書.md                     # 詳細仕様書
└── README.md                     # このファイル
```

## インストール

### 前提条件

- Python 3.7以上
- pip（Pythonパッケージマネージャー）

### セットアップ

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd ortools-scheduling-verify
```

2. **依存関係のインストール**
```bash
pip install ortools
```

3. **動作確認**
```bash
python examples/run_scheduling.py
```

## クイックスタート

### 基本的な使用例

```python
from src.scheduling_optimizer import SchedulingOptimizer, create_sample_problem

# サンプル問題を作成
problem = create_sample_problem()

# 最適化を実行
optimizer = SchedulingOptimizer(problem)
solution = optimizer.solve(
    time_limit_seconds=60,    # 求解時間制限
    equality_weight=100       # 均等性重み
)

# 結果を表示
if solution:
    optimizer.print_solution(solution)
else:
    print("解が見つかりませんでした")
```

### 実行例

```bash
python examples/run_scheduling.py
```

**出力例:**
```
=== 練習表作成システム ===
部屋数: 5, コマ数: 3, パート数: 9

=== プレイヤー情報 ===
田中先生 (指導者): ['A', 'B']
佐藤先生 (指導者): ['C', 'D']
...

=== スケジュール結果 ===
総セッション数: 9
目的関数値: -0.00
最適解: はい
求解時間: 0.15秒

=== 指導者別セッション数 ===
田中先生 (['A', 'B']): 2セッション
佐藤先生 (['C', 'D']): 2セッション
...

=== スケジュール表 ===
時間\部屋    練習室A    練習室B    練習室C    練習室D    練習室E
1限目        A(田中先生)  C(佐藤先生)  E(鈴木先生)  G(高橋先生)  I(山田先生)
2限目        B(田中先生)  D(佐藤先生)  F(鈴木先生)  H(高橋先生)  -
3限目        -          -          -          -          -
```

## 設定パラメータ

### 問題設定（constants.py）

```python
class ProblemConfig:
    NUM_ROOMS = 5              # 部屋数
    NUM_PARTS = 9              # パート数
    NUM_INSTRUCTORS = 5        # 指導者数
    NUM_GENERAL_PLAYERS = 18   # 一般プレイヤー数
```

### スケジューリング設定

```python
class SchedulingConfig:
    DEFAULT_TIME_LIMIT = 30        # デフォルト時間制限（秒）
    DEFAULT_EQUALITY_WEIGHT = 100  # デフォルト均等性重み
    DEFAULT_PRIORITY = 50          # デフォルト優先度
```

## 制約条件

### 基本制約

1. **パート制約**: 各パートは1日に1回だけ練習
2. **部屋制約**: 各部屋は各時間コマに最大1つのセッション
3. **指導者制約**: 各指導者は各時間コマに最大1つのセッションを指導

### 均等割り振り制約

- 各指導者の指導セッション数の差を最小化（最大1差まで）

### プレイヤー制約

- 個人の重複優先度（0-100）に基づく制約違反ペナルティ
- 優先度が高いほど重複を避ける

## 目的関数

### 均等割り振り目的関数

指導者のセッション数の分散を最小化し、負荷を均等に分散します。

### プレイヤー制約違反ペナルティ

個人の重複優先度に基づいて、制約違反にペナルティを課します。

## カスタマイズ

### 独自問題の作成

```python
from src.data_models import SchedulingProblem, Player, Room, TimeSlot, PartType

# カスタム問題を作成
players = [
    Player(id=1, name="指導者A", parts=[PartType.A], is_instructor=True),
    # ... 他のプレイヤー
]

rooms = [
    Room(id=1, name="練習室1"),
    # ... 他の部屋
]

time_slots = [
    TimeSlot(id=1, name="1限目"),
    # ... 他の時間コマ
]

problem = SchedulingProblem(
    players=players,
    rooms=rooms,
    time_slots=time_slots,
    parts=[PartType.A, PartType.B, PartType.C]
)
```

### 制約条件の追加

`src/constraints.py`の`SchedulingConstraints`クラスを拡張して、新しい制約条件を追加できます。

### 目的関数の変更

`src/objectives.py`の`SchedulingObjectives`クラスを修正して、目的関数をカスタマイズできます。

## トラブルシューティング

### 解が見つからない場合

1. **制約条件を緩和**
   - 時間制限を延長
   - プレイヤーの重複優先度を下げる

2. **問題設定を確認**
   - 部屋数とパート数のバランス
   - 指導者数とパート数の関係

3. **デバッグ情報の確認**
   ```python
   # デバッグモードで実行
   solution = optimizer.solve(time_limit_seconds=120)
   ```

### パフォーマンス問題

1. **時間制限の調整**
   ```python
   solution = optimizer.solve(time_limit_seconds=60)
   ```

2. **問題規模の縮小**
   - 部屋数やパート数を減らす
   - プレイヤー数を調整

## 開発者向け情報

### アーキテクチャ

- **SchedulingOptimizer**: メインの最適化クラス
- **SchedulingConstraints**: 制約条件の管理
- **SchedulingObjectives**: 目的関数の管理
- **データモデル**: 問題と解のデータ構造

### テスト

```bash
# 基本的な動作テスト
python examples/run_scheduling.py

# カスタム問題でのテスト
python -c "
from src.scheduling_optimizer import create_sample_problem, SchedulingOptimizer
problem = create_sample_problem()
optimizer = SchedulingOptimizer(problem)
solution = optimizer.solve()
print('テスト完了' if solution else 'テスト失敗')
"
```

### 貢献

1. フォークしてブランチを作成
2. 機能を実装
3. テストを追加
4. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 更新履歴

### v0.1.0 (2024年)
- 初回リリース
- 基本的なスケジューリング最適化機能
- 制約条件と目的関数の実装
- サンプル問題と実行例

## サポート

問題や質問がございましたら、以下の方法でお問い合わせください：

- GitHub Issues: バグ報告や機能要求
- ドキュメント: [仕様書.md](仕様書.md)で詳細仕様を確認

## 関連リンク

- [OR-Tools公式ドキュメント](https://developers.google.com/optimization)
- [制約プログラミング入門](https://developers.google.com/optimization/cp)
- [Python OR-Toolsチュートリアル](https://developers.google.com/optimization/introduction/python)

---

**注意**: このシステムは教育・研究目的で開発されています。商用利用の場合は、適切なライセンス確認を行ってください。
