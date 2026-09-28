# sample-lab

Claude Code や Codex で研究の作業を整理していくための、最小構成のサンプルリポジトリです。

## このリポジトリが扱う範囲

**1つの研究のまとまりに1つのリポジトリ**、という使い方を想定しています。研究活動の全部を1つに詰め込む器ではありません。

次のどれかが違うものは、**このリポジトリに入れず、テンプレートからもう1つリポジトリを作ってください。**

- 主な共同研究者や、読み書きさせたい相手が違う
- 公開する範囲や時期が違う（公開データと未公開の草稿を同居させない）
- ライセンス・倫理審査・データの保存期間が違う

詰め込むと、こうなります。

- エージェントが関係ないファイルまで探しに行き、`draft.md` のような同名ファイルを取り違える
- コミットに無関係な変更が混ざり、履歴から「何をしたか」が読めなくなる
- 公開できないものと配布するものが同じ履歴に乗る
- リポジトリが肥大して clone が重くなる

同じ研究目的に属するのに、Git の管理条件だけが違うもの（公開データセット、共同開発のソフトウェアなど）は、
`repos/` に別リポジトリとして置きます（[repos/README.md](./repos/README.md)）。

## ディレクトリ構成

```text
sample-lab/
├── AGENTS.md                     ← AI への指示書（共通ルールの正本。書き換えて使う）
├── CLAUDE.md                     ← Claude Code 固有の設定だけ（冒頭で AGENTS.md を読み込む）
├── .gitignore
├── bibliography/                 ← 書誌データ（Zotero の自動エクスポート先）と引用スタイル
├── cv/                           ← 履歴書に転記する業績一覧（researchmap が正本）
├── dotclaude/                    ← セットアップ時に .claude/ にリネーム（下記参照）
│   ├── agents/                   ← エージェント定義
│   ├── skills/                   ← スキル定義。雛形・テーマ・スクリプトも中にある
│   ├── settings.json             ← 危険な操作をブロックする設定
│   └── marprc.yml                ← → .marprc.yml にコピー
├── dotvscode/                    ← セットアップ時に .vscode/ にリネーム
├── lab/
│   ├── assets/figures/           ← 使い回す図
│   └── logs/                     ← 日次ログ
├── work/                         ← 作業単位。ここが日々の作業場
│   ├── project_a/ project_b/     ← sources/ scripts/ outputs/ docs/
│   └── publications/             ← 原稿の制作（原稿・図・中間ファイル）
├── publications/                 ← 完成版の収集場所（PDF・PPTX だけ。自動で集まる）
├── repos/                        ← 別Gitが必要なもの（このリポジトリでは追跡しない）
└── sample-files/                 ← 動作確認用のサンプル。不要になったら削除してよい
```

## 環境準備（AI エージェント起動前に必要なもの）

以下の操作を実行後、起動した Claude Code または Codex に README.md を参考に初期設定を頼んでください。

1. **GitHub Desktop**のインストール — ターミナルでのGit操作に不安がある場合は、GitHub Desktopをインストールする。
2. テンプレートを自分のフォルダにCloneする - 右上の**Use this template**をクリックし、自身の好きな名前でリポジトリを作る（必ず**private** を選択する）
3. GitHub Desktopの左上から作ったリポジトリを選択し、ローカルフォルダに保存する
4. **VSCode**か**Cursor**のインストール — https://code.visualstudio.com/ または https://cursor.com/ja
   インストールしたらアプリを開き、使える状態にする（Cursorなら無料版で構わないのでアカウント登録等が必要。GitHubと接続する）
5. **Claude Code または Codex** を使える状態にする
   - Claude Code を使う場合: Claude Code公式のクイックスタート（https://code.claude.com/docs/ja/quickstart）から、自身のOSに合わせてコマンドをコピーし、ターミナル（VSCodeまたはCursorのものでも可）に貼り付けてEnter
   - Codex を使う場合: Codex Quickstart（https://developers.openai.com/codex/quickstart）を開き、VSCode / Cursor 拡張または Codex CLI の手順でセットアップする
   - **Windows で Codex を使う場合:** OpenAI 公式の Windows guide（https://developers.openai.com/codex/windows）も確認し、できるだけ **WSL ワークスペース** で使う

## 最初にやること

1. 上記の「環境準備」を終わらせる
2. ターミナル（VSCodeまたはCursorのものでも可）を開く
   - **Mac:** そのまま標準ターミナルか VSCode / Cursor のターミナルを使う
   - **Windows + Claude Code:** VSCode / Cursor のターミナルを **Git Bash** に切り替えると、この README の bash コマンドをそのまま使いやすい
   - **Windows + Codex:** できるだけ **WSL ターミナル** を使い、VSCode / Cursor も **WSL でフォルダを開いた状態** にする
   - **Windows + Codex + WSL:** 可能ならリポジトリは WSL 側（例: `~/code/リポジトリ名`）に置く。GitHub Desktop で Windows 側に clone した場合も始められるが、WSL 側の方が安定しやすい
3. `cd 準備でローカルに保存したGitHubのフォルダパス` を実行する
   - **Windows + WSL:** `C:\...` ではなく、WSL から見えるパス（例: `~/code/...` や `/mnt/c/...`）で移動する
4. 移動したら、使う AI エージェントを起動する（Claude Code なら `claude`。Codex は VSCode / Cursor の Codex パネルを開くか、CLI を使う場合は `codex` を実行する）
   - **Windows + Codex IDE 拡張:** まず `WSL: Reopen Folder in WSL` で開き直してから使うと安定しやすい
5. AI エージェントに **「README.md を読んでセットアップして」** と伝える

Claude Code / Codex が以下を自動で行います（人間の操作が必要な箇所は都度指示されます）。

### セットアップ手順（Claude Code / Codex 向け）

> **Claude Code / Codex へ:** 以下の手順を順に実行してください。人間にしかできない操作（API キーの入力等）は、ユーザに指示を出して待ってください。
> Mac と Windows の両方に対応してください。
> Windows の場合は、Claude Code は Git Bash または WSL、Codex は WSL ワークスペースを優先してください。
> bash と PowerShell の両方の例がある場合は、現在のシェルに合う方を使ってください。

1. **環境チェック**（以下のコマンドで必要なツールが入っているか確認する）
   ```bash
   git --version
   node --version
   lualatex --version
   biber --version
   ```
   - コマンドが見つからない、またはエラー終了したものは「未インストール」とみなしてよい
   - 不足しているツールがあれば、用途を確認した上でインストールを案内する
   - **Node.js が未インストールの場合:** スライド作成（Marp）に必要。ユーザにスライド作成を使うか確認し、使う場合のみインストールを案内する。https://nodejs.org/ から LTS 版をダウンロード・インストールするよう伝える。完了後 `node --version` で確認し、続けて `npm install -g @marp-team/marp-cli` を実行する。Mac で EACCES エラーが出たら `sudo npm install -g @marp-team/marp-cli` を案内する
   - **LaTeX が未インストールの場合:** 論文執筆に必要。ユーザに LaTeX での論文執筆を使うか確認し、使う場合のみインストールを案内する（約5GB、時間がかかるため）。Mac: https://www.tug.org/mactex/ から .pkg。Windows: https://www.tug.org/texlive/ から install-tl-windows.exe。完了後 `lualatex --version` と `biber --version` で確認する
   - インストール不要なツールは飛ばしてよい。ユーザが「今は使わない」と言えば次に進む

2. **dotclaude/ の展開**（以下のコマンドを順に実行する）
   **bash / Git Bash / WSL:**
   ```bash
   # 隠しファイルをルートにコピー（リネーム前に行うこと）
   cp dotclaude/marprc.yml .marprc.yml
   # ディレクトリをリネーム
   mv dotclaude .claude
   mv dotvscode .vscode
   ```
   **PowerShell:**
   ```powershell
   Copy-Item dotclaude/marprc.yml .marprc.yml
   Move-Item dotclaude .claude
   Move-Item dotvscode .vscode
   ```
   - 完了後、ユーザに「VSCode の左下に推奨拡張機能の通知が出ていたらインストールしてください」と伝える

3. **Codex を使う場合の追加設定**（Claude Code だけ使うなら省略可）
   **bash / Git Bash / WSL:**
   ```bash
   # エージェント定義を Codex 用ディレクトリにコピー
   mkdir -p .agents
   cp -r .claude/agents/* .agents/

   # スキルを Codex 用ディレクトリにコピー
   mkdir -p .agents/skills
   cp -r .claude/skills/* .agents/skills/
   ```
   **PowerShell:**
   ```powershell
   New-Item -ItemType Directory -Force .agents | Out-Null
   Copy-Item -Recurse .claude/agents/* .agents/
   New-Item -ItemType Directory -Force .agents/skills | Out-Null
   Copy-Item -Recurse .claude/skills/* .agents/skills/
   ```
   - Codex は `AGENTS.md` を自動で読むため、共通ルールは `AGENTS.md` に集約されている
   - **コピーすると同じスキルが2か所になる。** 片方だけ直すとずれるので、直すときは `.claude/skills/` を正本にして再コピーする
   - **Windows + Codex:** ネイティブ Windows よりも、WSL 上でこのコピーを行う方が安定しやすい

4. **セキュリティ設定の確認**
   - `.claude/settings.json` に deny ルールが入っていることを確認する（手順2のリネームで配置済み）
   - 内容をユーザに説明する。**`Read(...)` の deny は Read ツールだけを止め、`cat` などシェル経由の読み取りは止まらない**ことも伝える
   - 初回セットアップでは **確認モードのまま** 進め、危険な操作に `Always allow` を付けない
   - `git push`、依存追加、ネットワークアクセス、作業フォルダ外の読み書き、大量削除は都度ユーザ確認を取る

5. **このリポジトリが扱う範囲を決める**
   - **リネームより先に、境界を確認する。** ユーザに次を尋ねる
     - このリポジトリで扱う研究のまとまりは何か（1つの研究目的に絞れているか）
     - 一緒に入れようとしているものの中に、**共同研究者・公開範囲・ライセンス・保存期間が違うもの**はないか
   - 違うものがあれば、**このリポジトリに入れず別のリポジトリにする**よう提案する。
     同じ目的だが Git の条件だけ違うものは `repos/` に置くよう案内する
   - 決まった範囲を [AGENTS.md](./AGENTS.md) の「このリポジトリが扱う範囲」に書く

6. **AGENTS.md のカスタマイズ**
   - ユーザに研究分野・用途・作業単位の数・応答言語をヒアリングする
   - 回答をもとに [AGENTS.md](./AGENTS.md) の `[角括弧]` 部分を書き換える
   - **共通ルールはすべて AGENTS.md に書く。** [CLAUDE.md](./CLAUDE.md) は `@AGENTS.md` でそれを読み込む薄い入口なので、同じ内容を書き写さない
   - `.claude/agents/` のエージェント定義はサンプルである。ユーザの研究分野に合わないものがあれば削除を提案する

7. **作業ディレクトリのリネーム**
   - 手順5で決めた範囲に合わせて `work/project_a/`, `work/project_b/` をリネームする
   - 各フォルダの `README.md` も更新する

8. **初回コミット**
   - セットアップ完了後、変更をまとめてコミットする（push はユーザの許可を得てから）

## 使い方の目安

- 研究データは `work/<名前>/sources/`
- 分析コードは `work/<名前>/scripts/`
- 生成結果は `work/<名前>/outputs/`
- メモや下書きは `work/<名前>/docs/`
- 発表・論文の**原稿**は `work/publications/<名前>/`、**完成版**は `publications/<名前>/`（ビルドすると自動で集まる）
- 書誌は `bibliography/references.bib`、履歴書用の業績一覧は `cv/master/`
- `lab/` は自分が開く共通部品、`.claude/skills/` はエージェントへの手順書

## セキュリティ設定

`.claude/settings.json` の `permissions.deny` が、force push や `rm -rf` などの危険なコマンドと、
`.env` / 証明書 / 鍵 / `credentials/` / `secrets/` の読み取りをブロックします。
誤って「Always allow」を押しても deny が優先されます。この設定は git で管理されているので、
同じリポジトリを使う人には同じ保護がかかります。追加のルールは `.claude/settings.json` に書いてください。
自分の環境でだけ効かせたい設定は `.claude/settings.local.json` へ（`.gitignore` で除外済み）。

> **deny は「読ませない」の完全な手段ではありません。**
> `Read(...)` は Read ツールの読み取りだけを止めます。`cat` や `grep` をシェルで実行する経路は止まりません。
> **本当に見せたくないものは、そもそもリポジトリに置かないでください**（`.gitignore` に入れる、リポジトリの外に置く）。
>
> なお `.claudeignore` や `.agentignore` というファイルは Claude Code にも Codex にもありません。
> 置いても無視されるだけなので、使わないでください。

この設定は Claude Code 用です。Codex を使う場合は、Codex 側のサンドボックスと承認モードを別途確認してください。
Codex でも、初回セットアップでは確認モードを維持し、`full-auto` や広い自動承認は有効にしないでください。

## ツール連携

### VSCode 拡張機能

VSCode でこのリポジトリを開くと、いくつかの拡張機能のインストールが推奨されます（`.vscode/extensions.json`）。Claude Code / Codex は使う方を入れてください。

| 拡張機能 | 用途 |
|---------|------|
| **Japanese** | 日本語設定（再起動で適用される） |
| **Claude Code** | AI エージェント本体。必要なものを入れる |
| **Codex** | AI エージェント本体。必要なら VSCode Marketplace から入れる |
| **Marp for VS Code** | Markdown スライドのプレビュー。スライド作成を効率化させたいなら入れることを推奨 |
| **LaTeX Workshop** | LaTeX の保存時自動ビルド・PDFプレビュー。LaTeXで論文を作成したければ入れる。面倒な設定はすべてエージェントに任せるため最低限のタグを使って書ければ使える。Zotero連携で参考文献管理も効率化できる |
| **vscode-pdf** | PDF 閲覧（論文を横に開きながら作業） |

### Marp スライド

Node.js と Marp CLI が必要です（セットアップ手順の環境チェックでインストールを案内します）。

**作り方の手順・コマンド・作図の基準は [publications/README.md](./publications/README.md) にまとめてあります。** ここに置くのは全体像だけです。

- カスタムテーマが2つ登録済み。フロントマターの `theme:` で選ぶ
  - `academic-ja` — 16:10・本文29px。和文の学会発表と授業用
  - `academic-intl` — 16:9・本文32px・ラテン書体優先。国際学会（英語）用
  - 判型も基準文字サイズも違うので、`theme:` だけ差し替えると全枚数がリフローする。用途に合う方で最初から書く
- **新規作成はゼロからではなく `.claude/skills/build-slide/assets/templates/` の雛形のコピーから始める**
- Markdown のフロントマターに `marp: true` と書けばプレビューが有効になる
- 図（SVG）の文字サイズは `check_svg_text.py` が検査する。`build_marp.sh` 経由なら自動で走る
- Claude Code では `/build-slide <パス>` で PDF・PPTX を出力できる

### LaTeX 論文

TeX Live（Mac は MacTeX）が必要です（セットアップ手順の環境チェックでインストールを案内します）。

**雛形の選び方・使い方・文献の書き方は [publications/README.md](./publications/README.md) にまとめてあります。**

- 雛形は `.claude/skills/md-to-pdf/assets/templates/` に。`paper/`（短い論文・動作確認）、`thesis/`（学位論文）、`resume/`（レジュメ）、`transcript/`（口頭発表原稿）、`ipsj/`（情報処理学会論文誌）
- **新しい学会テンプレートを足すときは、そこにフォルダを1つ置けば** LaTeX 直書きでも `/md-to-pdf` でも使える（手順は `templates/README.md`）
- 雛形は `work/publications/<名前>/` にコピーして使う。**パスの書き換えは不要**で、コピー先の深さも問わない（`.latexmkrc` がリポジトリルートを自分で探す）
- LaTeX Workshop が保存時に自動ビルドし、VSCode 内で PDF プレビューできる
- LaTeX を書かずに、ふつうの Markdown から同じ体裁の PDF・docx を作ることもできる（`/md-to-pdf`・`/md-to-docx`）
- 書誌は `bibliography/references.bib` の1本にまとめる。Zotero（Better BibTeX）の自動エクスポート先に指定して使う

### 共通ツールを複数のリポジトリで使い回したくなったら

このテンプレートは、スキルをリポジトリの中に置いています（`.claude/skills/`）。
**最初の練習を1つのフォルダで完結させるため**で、本来スキルは研究成果とは別に管理する方が自然です。

使い回す段階になったら、スキルを `~/.agents/skills/` に移し、

```bash
claude --plugin-dir "$HOME/.agents"
```

で起動してください。コピーも symlink もなしに、Claude Code・Codex・Gemini CLI・GitHub Copilot が
同じスキルの実体を読みます。

## Codex（ChatGPT）で使う場合

このテンプレートは **Claude Code と Codex の併用**を前提に設計されています。
指示ファイルは次のように役割を分けています。

- **AGENTS.md** — 共通ルールの正本。Codex はこれを直接読む
- **CLAUDE.md** — Claude Code 固有の設定だけ。冒頭の `@AGENTS.md` で AGENTS.md を読み込む

共通ルールを両方に書き写さないのが要点です。片方だけ直したときにずれるのを防ぎます。

インストールや初回起動は、Codex Quickstart（https://developers.openai.com/codex/quickstart）を見るのが確実です。
Windows で Codex を使う場合は、OpenAI 公式も **WSL ワークスペース** を推奨しています。Windows guide（https://developers.openai.com/codex/windows）に沿って進めると安定します。

| 機能 | Claude Code | Codex |
|------|:-----------:|:-----:|
| AGENTS.md の共通ルール | ✅（CLAUDE.md の `@AGENTS.md` 経由） | ✅（直接読む） |
| CLAUDE.md の製品固有設定 | ✅ | ❌（読まないので、共通ルールを書かない） |
| エージェント定義 | `.claude/agents/` | `.agents/` にコピー |
| スキル（SKILL.md） | `/スキル名` で呼び出し | プロンプトで手順を指示 |
| セキュリティ設定 | `.claude/settings.json` | Codex 側のサンドボックス設定 |

> スキルの自動呼び出し（`/daily-start` 等）は Claude Code 固有の機能です。
> Codex では SKILL.md の内容をプロンプトに貼り付けるか、手順を AGENTS.md に転記して使ってください。

## 補足

- `project_a` と `project_b` はサンプル名です。自分の用途に合わせて名前を変えてください
- `AGENTS.md` と `CLAUDE.md` は完成品ではなく、書き換え前提のテンプレートです
- `.claude/agents/` のエージェント定義も雛形です。不要なものは削除して構いません
- `dotclaude/` と `dotvscode/` は GitHub テンプレート配布のためにリネームしてあります。セットアップ手順で `.claude/` や `.vscode/` に展開されます
- `sample-files/` は動作確認用です。ひと通り試したらフォルダごと削除して構いません
