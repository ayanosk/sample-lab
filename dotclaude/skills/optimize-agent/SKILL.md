---
name: optimize-agent
description: エージェント定義を公式形式に最適化する。system_prompt圧縮、AGENTS.md更新を行う。
argument-hint: <エージェントID | all | agents-md>
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent, WebSearch
---

# エージェント定義の最適化

エージェント定義を公式推奨形式に変換・最適化する。

**引数:** $ARGUMENTS

---

## モード判定

引数に応じて実行モードを切り替える。

| 引数 | モード | 説明 |
|------|--------|------|
| `<エージェントID>` | 単体最適化 | 指定エージェントを最適化 |
| `all` | 一括最適化 | 全エージェントを順次最適化 |
| `agents-md` | AGENTS.md更新 | プロジェクトルートのAGENTS.mdを再生成 |

---

## モード1: 単体最適化（メインフロー）

### 1-1. 現行定義の読み込みと計測

Glob で `.claude/agents/**/*[エージェントID]*.md` を探し、Read で全文読む。
行数を計測する。

### 1-2. フィールドマッピングの参照

Read ツールで `references/field_mapping.md` を読み、フロントマターの過不足を確認する。

### 1-3. 最適化案の提示

Read ツールで `assets/conversion_template.md` を読み、この形式でユーザーに提示して承認を得る。

### 1-4. 最適化の実行

ユーザーの承認後：

1. `.claude/agents/[部門]/[id].md` を Edit で更新（YAMLフロントマター + Markdown本文）
2. 最適化後の行数を計測して報告

---

## モード2: 一括最適化（all）

1. `.claude/agents/**/*.md` を全件リストアップし、状態を表示する：

```
エージェント最適化状況:
  ✅ engineer            （30行、適正）
  🟡 academic-writer     （85行、圧縮余地あり）
  ...
```

2. 改善余地のあるエージェントを1件ずつモード1で処理する。
3. 各エージェントの最適化後にユーザーの承認を得てから次に進む。

---

## モード3: AGENTS.md更新（agents-md）

### 3-1. ガイドラインと現行ファイルの読み込み

Read ツールで `references/agents_md_guide.md` を読み、ベストプラクティスを確認する。
プロジェクトルートの `AGENTS.md` を Read で読む。

### 3-2. 更新案の提示

ガイドライン（≤150行、6領域カバー）に基づき、更新案をユーザーに提示する。
CLAUDE.md 固有の内容（コンパクション指示、`.claude/` 参照、スキル呼び出し）は含めない。

### 3-3. ユーザーの承認後に書き込み

承認を得てから AGENTS.md を更新する。
