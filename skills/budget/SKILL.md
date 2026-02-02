---
name: budget
description: This skill should be used when the user asks to "/budget", "使用量確認", "バジェット", "残り使用量", or needs to check Claude Code weekly usage percentage and pace recommendations.
version: 0.1.0
argument-hint: "[使用量%]"
allowed-tools: Bash(date *, python3 *)
---

# /budget コマンド

Claude Codeの週次使用量をパーセンテージで管理するバジェットコマンドです。`/usage` で確認した現在の使用量%を入力すると、残り時間から「今日の目標使用量」とペース配分アドバイスを表示します。

## 入力方法

- `/budget 40` — 引数で使用量%を渡す
- `/budget` — 引数なしの場合はAskUserQuestionツールで使用量%を質問する

引数は `$ARGUMENTS` で受け取ります。

## 実行シーケンス

### 1. 使用量%の取得

1. `$ARGUMENTS` に数値が含まれている場合、その値を `current_usage` として使用
2. 引数がない場合、AskUserQuestionツールで「現在の使用量%を教えてください（例: 40）」と質問
3. 数値以外が入力された場合、再度質問する

### 2. 日付情報の取得

Bashで以下を実行してJSTの日付情報を取得する：

```bash
export TZ="Asia/Tokyo" && date +"%Y-%m-%d %u %H %M %A"
```

- `%Y-%m-%d` で日付を取得
- `%u` でISO曜日番号を取得（月=1, 火=2, ..., 日=7）
- `%H` で現在の時（0-23）を取得
- `%M` で現在の分（0-59）を取得

### 3. レポート生成

ステップ2で取得した日付情報（`date` コマンドの出力 `YYYY-MM-DD u HH MM`）をパースし、以下のBashコマンドを実行する。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/budget/scripts/budget_calc.py <usage%> <year> <month> <day> <iso_weekday> <hour> <minute>
```

**実行例**:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/budget/scripts/budget_calc.py 45.0 2026 1 28 3 9 40
```

**サイクル定義**: 木曜日17:00 JSTにリセット。168時間（7日）サイクル（木17:00〜翌木17:00）。

### 4. 結果の表示

**重要**: Bashツールの出力は折りたたまれてユーザーに見えない場合があります。そのため、Pythonスクリプトの出力内容を**Claudeのテキスト応答として直接表示**してください。

1. Bashツールでスクリプトを実行し、出力を取得
2. 取得した出力（Markdownテキスト）をそのままClaudeの応答として出力する
3. ツール結果をそのまま引用するのではなく、内容をコピーしてテキストとして表示する

### 5. エラーハンドリング

#### 数値以外の入力
AskUserQuestionツールで「数値を入力してください（例: 40）」と再質問する。

#### 100%超過の入力
```markdown
⚠️ **使用量が100%を超過しています**

入力値: {current_usage}%

今週の使用量上限に達しています。
- 週次リセットを待つことを推奨します（次のリセット: MM/DD（木）17:00）
- どうしても必要な場合は、最小限の使用に留めてください
```

#### 負の値の入力
AskUserQuestionツールで「0以上の数値を入力してください」と再質問する。

## 注意事項

- Python スクリプト (`${CLAUDE_PLUGIN_ROOT}/skills/budget/scripts/budget_calc.py`) が必要です
- サイクルは木曜日17:00 JSTにリセットされます
- 使用量は0〜100%の範囲で入力してください
