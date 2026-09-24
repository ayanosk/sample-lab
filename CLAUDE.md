@AGENTS.md

# Claude Code 固有の設定

共通ルールは [AGENTS.md](./AGENTS.md) が正本です。冒頭の `@AGENTS.md` で読み込まれます。
このファイルには **Claude Code だけに必要なこと**を書きます。共通ルールをここに複製しないでください。

> **初回セットアップ:** `dotclaude/` ディレクトリが残っている場合、まだセットアップが完了していません。
> [README.md](./README.md) の「セットアップ手順」を実行してください。

## スキル

繰り返す作業は `/スキル名` で呼び出せます。一覧は [.claude/skills/README.md](./.claude/skills/README.md)。

| よく使うもの | 用途 |
|---|---|
| `/build-slide <パス>` | Marp スライドを PDF・PPTX にする |
| `/md-to-pdf <パス>` | Markdown を論文体裁の PDF にする |
| `/md-to-docx <パス>` | Markdown をコメント用の docx にする |

## サブエージェント

`.claude/agents/` に役割別のエージェント定義があります。**すべてサンプルです。**
自分の研究分野に合わないものは削除してください。

## 権限

`.claude/settings.json` の `permissions.deny` が、force push や `rm -rf` などの危険な操作と、
鍵・証明書・`.env` の読み取りをブロックします。誤って「Always allow」を押しても、deny が優先されます。

> **`Read(...)` の deny は Read ツールの読み取りだけを止めます。**
> `cat` や `grep` などシェル経由の読み取りは止まりません。
> 本当に見せたくないものは、そもそもこのリポジトリに置かないでください。

ルールを足すときは `.claude/settings.json` を編集します（このファイルは git 管理されているので、
共同作業者にも同じ保護が適用されます）。自分の環境だけの設定は `.claude/settings.local.json` へ。
