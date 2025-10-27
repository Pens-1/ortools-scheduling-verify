# OR-Tools 最適化システム

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-Latest-green.svg)](https://developers.google.com/optimization)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 概要

このプロジェクトは、以下の2つの最適化機能を提供します：
1. **練習室スケジューリング最適化**: Google OR-Toolsを使用してパート別練習スケジュールを自動生成
2. **幾何学最適化**: scipyを使用して制約条件下で距離を最小化する幾何学問題を解く

## 主な機能

### スケジューリング最適化
- 🎯 **制約充足最適化**: 複雑な制約条件を満たすスケジュール生成
- ⚖️ **均等負荷分散**: 指導者の負荷を均等に分散
- 👥 **個人別優先度**: プレイヤーの重複優先度に基づく制約
- 🏢 **多部屋対応**: 複数の練習室での同時練習
- ⏰ **時間コマ管理**: 効率的な時間割作成
- 📊 **可視化**: 分かりやすいスケジュール表の表示

### 幾何学最適化
- 📐 **等距離条件最適化**: 複数の点から等距離にある点を求める
- 🎨 **可視化機能**: matplotlibによる結果のグラフィカル表示
- ⚡ **高速求解**: scipy.optimizeによる効率的な最適化

## システム構成

```
ortools-scheduling-verify/
├── src/                          # ソースコード
│   ├── __init__.py              # パッケージ初期化
│   ├── geometry_optimizer.py   # 幾何学最適化クラス
│   └── geometry_models.py       # 幾何学データモデル
├── examples/                     # 実行例
│   └── solve_geometry.py       # 幾何学最適化実行
├── requirements.txt              # 依存関係
├── geometry_solution.png         # 最適化結果の可視化
├── LICENSE                       # ライセンス
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
pip install -r requirements.txt
```

3. **動作確認**
```bash
python examples/solve_geometry.py
```

## クイックスタート

### 基本的な使用例

```python
from src.geometry_optimizer import GeometryOptimizer, create_geometry_problem

# 幾何学問題を作成
problem = create_geometry_problem()

# 最適化を実行
optimizer = GeometryOptimizer(problem)
solution = optimizer.solve()

# 結果を表示
if solution:
    optimizer.print_solution(solution)
else:
    print("解が見つかりませんでした")
```

### 実行例
```bash
python examples/solve_geometry.py
```

**出力例:**
```
=== 幾何学最適化問題 ===
問題:
  原点(0,0)から点Aまでの距離 = D
  点Aから点B(50,35)までの距離 = D
  点Aから点C(x_C,50)までの距離 = D
  ただし: x_A > 0, y_A > 0, x_C > 50
  目的: Dを最小化

幾何学最適化を実行中...
解が見つかりました

=== 幾何学最適化結果 ===
最小距離 D: 43.156694
点Aの座標: (7.50, 42.50)
点Cの座標: (50.00, 50.00)
最適解: はい
求解時間: 0.0053秒

=== 制約条件の検証 ===
すべての距離が等しい: True
点Aのx座標 > 0: True
点Aのy座標 > 0: True
点Cのx座標 > 50: True
```

## 幾何学最適化の問題設定

### 制約条件

1. **距離制約**: 原点、点B、点Cから点Aまでの距離がすべて等しい(= D)
2. **境界条件**: 
   - 点Aのx座標 > 0
   - 点Aのy座標 > 0
   - 点Cのx座標 > 50

### 最適化アルゴリズム

- **目的関数**: D(距離)を最小化
- **制約**: 3つの等距離制約
- **最適化手法**: scipy.optimize.minimize (SLSQP法)

## カスタマイズ

### カスタム幾何学問題の作成

```python
from src.geometry_models import Point, GeometryProblem
from src.geometry_optimizer import GeometryOptimizer

# 問題を設定
point_b = Point(x=50, y=35)
point_c_y = 50.0

problem = GeometryProblem(
    point_b=point_b,
    point_c_y=point_c_y
)

# 最適化を実行
optimizer = GeometryOptimizer(problem)
solution = optimizer.solve()
```

## トラブルシューティング

### 解が見つからない場合

1. **初期値の調整**: 初期値を変更してみる
2. **制約条件の確認**: 制約条件が適切か確認
3. **求解時間の延長**: より多くの時間を割り当てる

### 貢献

1. フォークしてブランチを作成
2. 機能を実装
3. テストを追加
4. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 更新履歴

### v0.2.0 (2024年)
- 幾何学最適化機能を追加
- scipy.optimizeを使用した等距離点探索
- matplotlibによる結果の可視化
- 幾何学問題のサンプル実行例

## サポート

問題や質問がございましたら、GitHub Issuesでお問い合わせください。

## 関連リンク

- [scipy.optimizeドキュメント](https://docs.scipy.org/doc/scipy/reference/optimize.html)
- [matplotlib公式ドキュメント](https://matplotlib.org/)

---

**注意**: このシステムは教育・研究目的で開発されています。商用利用の場合は、適切なライセンス確認を行ってください。
