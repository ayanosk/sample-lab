# メタスキル整合性チェックリスト

監査時に、以下のメタスキルが公式最新情報と整合しているか確認する。

## optimize-agent

Read ツールで以下を読み、公式情報との差異を確認する：
- `.claude/skills/optimize-agent/references/field_mapping.md` — フロントマターフィールドの過不足
- `.claude/skills/optimize-agent/references/agents_md_guide.md` — AGENTS.md 仕様の更新有無

**チェック項目：**
- 公式で新しいフロントマターフィールドが追加されていないか
- 非推奨になったフィールドがないか
- tools 推奨設定が公式の変更を反映しているか
- AGENTS.md の推奨セクション・行数制限に変更がないか

## optimize-skill

Read ツールで `.claude/skills/optimize-skill/SKILL.md` を読み、以下を確認する：
- スキルの公式フォーマット（フロントマターフィールド）に変更がないか
- 外部化の判断基準が公式推奨と合っているか

差異が見つかった場合は、監査レポートに🟡推奨として含め、具体的な更新案を提示する。
