@AGENTS.md

# Claude Code 固有の設定

共通ルールは [AGENTS.md](./AGENTS.md) が正本です。冒頭の `@AGENTS.md` で読み込まれます。
このファイルには **Claude Code だけに必要なこと**を書きます。共通ルールをここに複製しないでください。

> **初回セットアップ:** `dotclaude/` ディレクトリが残っている場合、まだセットアップが完了していません。
> [README.md](./README.md) の「セットアップ手順」を実行してください。

## 呼び出しの作法

- **スキル**（`.claude/skills/`）は、`/md-to-pdf` のように `/スキル名` で呼び出せます。
  どんなスキルがあるかは、各 `SKILL.md` 冒頭の `description` が一覧になります
- **サブエージェント**（`.claude/agents/`）は、Claude Code が起動時に読み込みます。
  同梱しているのは `support/academic-writer.md` の1件だけで、**分野ごとの約束
  （註の付け方、史料引用の作法など）を書き込む置き場の見本**です
- 呼び出せるのが Claude Code 固有で、**中身はどちらもただのテキストです。**
  他のツールでは `SKILL.md` を読ませれば同じ手順が動きます
  （[README.md](./README.md) の「Codex（ChatGPT）で使う場合」）

## 権限

`.claude/settings.json` の `permissions.deny` が、force push や `rm -rf` などの危険な操作と、
鍵・証明書・`.env` の読み取りをブロックします。誤って「Always allow」を押しても、deny が優先されます。

> **`Read(...)` の deny は Read ツールの読み取りだけを止めます。**
> `cat` や `grep` などシェル経由の読み取りは止まりません。
> 本当に見せたくないものは、そもそもこのリポジトリに置かないでください。

ルールを足すときは `.claude/settings.json` を編集します（このファイルは git 管理されているので、
共同作業者にも同じ保護が適用されます）。自分の環境だけの設定は `.claude/settings.local.json` へ。
