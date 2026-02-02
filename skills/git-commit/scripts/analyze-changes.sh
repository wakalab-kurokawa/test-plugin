#!/bin/bash
# Git変更分析スクリプト
# 使用法: ./analyze-changes.sh [language]
# language: en | ja (デフォルト: ja)

LANG="${1:-ja}"

# ステージング状況確認
STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
UNSTAGED=$(git status --porcelain 2>/dev/null | grep -v "^[MADRC]" | wc -l | tr -d ' ')

if [ "$STAGED" -eq 0 ] && [ "$UNSTAGED" -eq 0 ]; then
    echo "ERROR: No changes to commit"
    exit 1
fi

# ステージングされていない場合は自動ステージング
if [ "$STAGED" -eq 0 ]; then
    git add .
    STAGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
    echo "AUTO_STAGED: $STAGED"
fi

# 変更ファイル一覧
echo "=== FILES ==="
git diff --cached --name-only

# 変更統計
echo "=== STATS ==="
git diff --cached --stat | tail -1

# コミットタイプ判定用のパターン検出
echo "=== PATTERNS ==="

# UI/UXファイル検出
UI_FILES=$(git diff --cached --name-only | grep -E '\.(tsx|jsx|vue|css|scss|less)$' | wc -l | tr -d ' ')
echo "UI_FILES: $UI_FILES"

# ドキュメントファイル検出
DOC_FILES=$(git diff --cached --name-only | grep -E '\.(md|txt|rst)$' | wc -l | tr -d ' ')
echo "DOC_FILES: $DOC_FILES"

# テストファイル検出
TEST_FILES=$(git diff --cached --name-only | grep -E '(test|spec)\.(ts|js|tsx|jsx)$' | wc -l | tr -d ' ')
echo "TEST_FILES: $TEST_FILES"

# 設定ファイル検出
CONFIG_FILES=$(git diff --cached --name-only | grep -E '(package\.json|tsconfig|eslint|prettier|\.yml|\.yaml)' | wc -l | tr -d ' ')
echo "CONFIG_FILES: $CONFIG_FILES"

# 差分の最初の200行（コミットメッセージ生成用）
echo "=== DIFF_PREVIEW ==="
git diff --cached | head -200
