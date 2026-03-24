---
name: repo-audit
description: ディレクトリ構成を監査し、不要ファイルの削除・アーカイブを提案する。
argument-hint: [--apply（提案の自動実行）]
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# リポジトリ衛生監査

リポジトリのディレクトリ構成を監査する。
不要ファイル・陳腐化した参照・構成の改善点を特定し、対処案を提示する。

**引数:** $ARGUMENTS

---

## フェーズ1: ディレクトリ構成の監査

### 1-1. 期待構成の参照

Read ツールで `references/expected_structure.md` を読み、期待構成を確認する。

### 1-2. 現状のスキャン

```bash
# 公式ディレクトリ
ls .claude/agents/*/ .claude/agent-memory/ .claude/skills/ .claude/rules/ 2>/dev/null

# ルートファイル
ls CLAUDE.md AGENTS.md 2>/dev/null
```

### 1-3. 陳腐化した参照チェック

スキル・ルール内に旧パスや不整合が残っていないか検索する。

Grep ツールで `.claude/skills/` と `.claude/rules/` を検索する。

### 1-4. メモリの健全性チェック

各エージェントのMEMORY.mdについて：

- 行数が200行を超えていないか
- CLAUDE.md・rules と重複する内容がないか

### 1-5. スキルの整合性チェック

Read ツールで `references/metaskill_checklist.md` を読み、メタスキルの整合性を確認する。

---

## フェーズ2: 監査レポートの生成

Read ツールで `assets/report_template.md` を読み、この形式でレポートを作成する。

---

## フェーズ3: 対処の実行（`--apply` 指定時のみ）

`--apply` が指定されている場合、ユーザーの承認後に提案アクションを実行する。
指定がない場合はレポート提示のみで終了する。

**実行可能なアクション：**
- ファイルの削除（`rm` / `git rm`）
- スキル内のパス更新（Edit）
- MEMORY.md の圧縮（Write）
- expected_structure.md の更新（Write）

**実行しないアクション（手動対応を促す）：**
- スキルのロジック変更
- CLAUDE.md / AGENTS.md の内容変更
- git commit / push
