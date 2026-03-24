---
name: seminar
description: ゼミを開催する。エージェントが問答形式で参加し、議事録を保存する。
argument-hint: "[議題・テーマ]"
---

# ゼミ開催（サブエージェント方式）

登録済みのエージェントを専門家として招集し、ゼミ形式の議論を行う。
**司会（メインClaude）がゲートキーパー**となり、ユーザーの指示に基づきサブエージェントを起動する。

**議題:** $ARGUMENTS

## 手順

### 1. 参加エージェントの確認

Glob で `.claude/agents/**/*.md` を検索し、利用可能なエージェント一覧をユーザーに提示する。
ユーザーが参加者を指名する（2〜4名を推奨）。

### 2. ゼミルールの読み込み

以下を順に Read する：
- `references/seminar_rules.md`（最重要ルール）
- `references/seminar_flow.md`（進行構造）
- `references/moderator_guide.md`（司会行動指針）

### 3. 前回議事録の確認

```bash
ls lab/logs/seminar_*.md 2>/dev/null | sort | tail -1
```

存在する場合は Read で読み、未解決事項を冒頭で確認する。

### 4. ゼミの実施

進行構造に従い、**ユーザーとの対話を軸に**ゼミを実施する。
- ユーザーの指名に基づき `Agent` ツールで該当エージェントを起動する
- ユーザーの追加質問は `SendMessage` で起動中のエージェントに転送する

### 5. 議事録の保存

閉会後、議事録を保存する：
- ファイル名: `seminar_YYYY-MM-DD.md`
- 保存先: `lab/logs/`

## 使用例

```
seminar "研究計画の進捗共有と課題の整理"
seminar "データ分析結果の解釈について議論したい"
seminar  # 引数なし → 本日の進捗共有
```
