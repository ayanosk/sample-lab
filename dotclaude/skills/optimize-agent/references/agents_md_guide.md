# AGENTS.md ベストプラクティス

AGENTS.md はツール横断の標準フォーマット（Linux Foundation / Agentic AI Foundation 管理）。
Codex CLI、GitHub Copilot、Cursor、Windsurf、Gemini CLI 等が自動読み込みする。

## 基本原則

- **≤150行** に収める（長いほどエージェントの精度が下がる）
- 標準Markdown（必須フィールドなし、柔軟な構造）
- コマンドはバッククォートで囲む（コピペ可能に）
- 境界線（always / ask first / never）を明示する

## 推奨セクション（6領域）

1. **Commands** — ビルド・テスト・リントの具体的コマンド
2. **Testing** — テスト実行方法、カバレッジ基準
3. **Project Structure** — 主要ディレクトリの説明
4. **Code Style** — 命名規則、フォーマット、言語
5. **Git Workflow** — ブランチ戦略、コミットメッセージ規約
6. **Boundaries** — やるべきこと / 聞くべきこと / 禁止事項

## CLAUDE.md との関係

| 項目 | AGENTS.md | CLAUDE.md |
|------|-----------|-----------|
| 対応ツール | Codex, Copilot, Cursor 等 | Claude Code のみ |
| 配置 | リポジトリルート | リポジトリルート + サブディレクトリ |
| 内容の重複 | プロジェクト共通の情報 | Claude Code 固有の設定 |

**方針**: AGENTS.md にツール共通の情報を、CLAUDE.md に Claude Code 固有の情報を書く。
CLAUDE.md から `AGENTS.md も参照せよ` と指示すれば、Claude Code でも活用可能。

## サブディレクトリ配置

最も近い AGENTS.md が優先される。サブプロジェクトごとに配置可能：
```
project_root/AGENTS.md        ← グローバル
project_root/frontend/AGENTS.md  ← フロントエンド固有
project_root/backend/AGENTS.md   ← バックエンド固有
```
