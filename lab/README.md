# lab

`lab/` には、複数プロジェクトで共通して使うものを置きます。

## 置き場所

- `slides/` : Marpスライド用のCSSテーマとビルドスクリプト
- `latex/` : LaTeX用の共通プリアンブルとlatexmk設定
- `logs/` : daily-start / daily-end の日次ログ

## 運用の考え方

- プロジェクト固有の事情は各 `project_x/` に置く
- どのプロジェクトでも使うものだけを `lab/` に集める
- セットアップ後、エージェント定義は `.claude/agents/`、スキルは `.claude/skills/` に配置される
