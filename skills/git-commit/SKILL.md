---
name: git-commit
description: This skill should be used when the user asks to "/git-commit", "コミット", "commit", "git commit", or needs to create a git commit with Conventional Commits format. Does not push.
version: 0.1.0
argument-hint: "(引数なし)"
context: fork
agent: Bash
allowed-tools: Bash(git *, bash ${CLAUDE_PLUGIN_ROOT}/skills/git-commit/*), Read
---

# Git Commit Automation

**COMMITのみ実行、PUSHは絶対に行わない**

## 実行手順

### 1. 変更分析スクリプト実行

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/git-commit/scripts/analyze-changes.sh
```

出力から以下を確認:
- `AUTO_STAGED`: 自動ステージングされたファイル数
- `UI_FILES`: UI/UXファイル数（feat判定用）
- `DOC_FILES`: ドキュメントファイル数（docs判定用）
- `TEST_FILES`: テストファイル数（test判定用）
- `CONFIG_FILES`: 設定ファイル数（chore判定用）

### 2. コミットタイプ判定

| 条件 | タイプ |
|------|--------|
| UI_FILES > 0 | `feat` |
| DOC_FILES のみ | `docs` |
| TEST_FILES のみ | `test` |
| CONFIG_FILES のみ | `chore` |
| バグ修正キーワード | `fix` |
| リファクタリング | `refactor` |
| その他 | 差分内容から判断 |

### 3. コミットメッセージ生成

**形式**: `type(scope): 簡潔な説明`

**言語**: CLAUDE.md の `commit-language` 設定を確認
- `en` → 英語
- 設定なし → 日本語

### 4. コミット実行

```bash
git commit -m "$(cat <<'EOF'
{生成したメッセージ}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

### 5. 完了報告

```
🎉 コミット完了

ハッシュ: {hash}
メッセージ: {message}

⚠️ PUSHは実行されていません
```

## Pre-commitフックエラー対応

ESLint/Prettierエラーの場合:
```bash
npm run lint:fix || npx prettier --write .
git add .
```
→ コミット再実行

## 注意

- 分割が必要な場合は提案のみ（自動分割しない）
- TypeScript型エラー等は手動修正を案内
