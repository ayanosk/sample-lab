# 期待されるディレクトリ構成

## Claude Code 公式ディレクトリ

| パス | 用途 | 管理方針 |
|------|------|---------|
| `.claude/agents/{カテゴリ}/*.md` | サブエージェント定義 | git管理。公式フォーマット（YAMLフロントマター付きMD） |
| `.claude/agent-memory/*/MEMORY.md` | エージェント記憶 | git管理。200行以内推奨 |
| `.claude/skills/*/SKILL.md` | スキル定義 | git管理 |
| `.claude/rules/*.md` | ルール（globs付き） | git管理。条件付きで自動ロード |
| `.claude/settings.json` | プロジェクト設定 | git管理 |
| `.claude/settings.local.json` | ローカル設定 | git除外 |
| `CLAUDE.md` | Claude Code 固有の指示 | git管理 |
| `AGENTS.md` | ツール横断の指示（Codex/Cursor等） | git管理。≤150行推奨 |

## プロジェクトディレクトリ

| パス | 用途 | 管理方針 |
|------|------|---------|
| `lab/` | 横断的な共通機能 | git管理 |
| `project_*/` | 個別プロジェクト | git管理 |
| `publications/` | 成果物 | git管理 |

## 廃止候補の判定基準

以下に該当するファイル・ディレクトリは削除またはアーカイブを提案する：

1. **未使用スキル**: `.claude/skills/` に存在するが機能していないもの
2. **孤立ファイル**: どのスキル・エージェントからも参照されていないファイル
3. **サイズ超過**: MEMORY.md が200行を超えているもの
4. **陳腐化した設定**: 旧パス参照が残っているスキル・ルール
