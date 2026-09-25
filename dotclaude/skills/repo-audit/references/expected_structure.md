# 期待されるディレクトリ構成

## Claude Code 公式ディレクトリ

| パス | 用途 | 管理方針 |
|------|------|---------|
| `.claude/agents/{カテゴリ}/*.md` | サブエージェント定義 | git管理。公式フォーマット（YAMLフロントマター付きMD） |
| `.claude/agent-memory/*/MEMORY.md` | エージェント記憶 | git管理。200行以内推奨 |
| `.claude/skills/*/SKILL.md` | スキル定義 | git管理 |
| `.claude/rules/*.md` | ルール（globs付き） | git管理。条件付きで自動ロード |
| `.claude/settings.json` | プロジェクト設定（deny ルール） | git管理。共有したい保護はここ |
| `.claude/settings.local.json` | ローカル設定 | git除外 |
| `AGENTS.md` | **共通ルールの正本** | git管理。≤150行推奨 |
| `CLAUDE.md` | Claude Code 固有の設定のみ | git管理。冒頭 `@AGENTS.md`。共通ルールを複製しない |

`.claudeignore` / `.agentignore` は **Claude Code にも Codex にも存在しない**。
あったら削除を提案し、ファイルを読ませない目的なら `settings.json` の `permissions.deny` を案内する。

## プロジェクトディレクトリ

| パス | 用途 | 管理方針 |
|------|------|---------|
| `work/<名前>/` | 作業単位（`sources` `scripts` `outputs` `docs`） | git管理。`outputs/` は除外 |
| `work/publications/<名前>/` | 原稿の制作。原稿・図・中間ファイル | git管理（生成物を除く） |
| `publications/<名前>/` | 完成版の収集場所。PDF・PPTX のみ | git管理。中身は `.gitignore` で除外 |
| `bibliography/` | 書誌データと引用スタイル | git管理。**スキルに入れない** |
| `lab/` | 自分が開く共通部品（図・ログ） | git管理 |
| `repos/` | 別Gitが必要なもの | **git除外**。入れ子repoを追跡しない |

## 廃止候補の判定基準

以下に該当するファイル・ディレクトリは削除またはアーカイブを提案する：

1. **未使用スキル**: `.claude/skills/` に存在するが機能していないもの
2. **孤立ファイル**: どのスキル・エージェントからも参照されていないファイル
3. **サイズ超過**: MEMORY.md が200行を超えているもの
4. **陳腐化した設定**: 旧パス参照が残っているスキル・ルール
5. **効かない除外設定**: `.claudeignore` / `.agentignore`

## 境界の点検

構成の監査では、次も確認する。

- `work/` の中に、**研究目的・共同研究者・公開範囲が異なるもの**が同居していないか
  → あれば別リポジトリへの分離を提案する
- `repos/` が `.gitignore` で除外されているか（入れ子repoが gitlink として登録されていないか）
- `publications/` に原稿や中間ファイル（`.md` `.tex`）が混ざっていないか
- スキルの中に**研究データ・原稿・書誌・成果物**が入り込んでいないか

## パスの決め打ちを避ける

スクリプトや設定がリポジトリルートを求めるときは、`../..` のような階層数の決め打ちではなく、
`AGENTS.md` を目印に上方探索する。スキルや雛形を置き直したときに壊れないようにするため。
既存の実装は `md2pdf.sh` / `build_marp.sh` / 各雛形の `.latexmkrc` にある。
