# 公式情報の検索クエリ

repo-audit で公式仕様の変更を確認する際に使用する検索クエリ一覧。

## WebSearch クエリ

| # | クエリ | 目的 |
|---|--------|------|
| 1 | `Claude Code agents subagents changelog 2026` | エージェント定義の仕様変更 |
| 2 | `Claude Code skills changelog 2026` | スキルの仕様変更 |
| 3 | `AGENTS.md specification latest 2026` | AGENTS.md の仕様更新 |
| 4 | `Claude Code changelog 2026` | 直近のリリースノート |

## 差異確認対象リファレンス

変更が見つかった場合、以下との差異を確認する：

- `.claude/skills/optimize-agent/references/field_mapping.md` — フロントマターフィールド定義
- `.claude/skills/optimize-agent/references/agents_md_guide.md` — AGENTS.md ガイドライン
- `.claude/skills/repo-audit/references/expected_structure.md` — ディレクトリ期待構成
