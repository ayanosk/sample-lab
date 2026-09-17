# sample-lab

Claude Code や Codex で研究室の作業を整理していくための、最小構成のサンプルリポジトリです。

## 目的

- プロジェクトごとに文脈を分ける
- `sources/` と `outputs/` を分けて、元データを壊しにくくする
- `.claude/skills/` に再利用したい作業をまとめる
- `CLAUDE.md` と `AGENTS.md` で AI への指示を整理する

## ディレクトリ構成

```text
sample-lab/
├── CLAUDE.md / AGENTS.md         ← AI への指示書（書き換えて使う）
├── .gitignore
├── dotclaude/                    ← セットアップ時に展開（下記参照）
│   ├── agents/                   ← エージェント定義（→ .claude/agents/）
│   ├── skills/                   ← スキル定義（→ .claude/skills/）
│   ├── settings.json.example      ← セキュリティ設定の雛形（→ .claude/settings.local.json）
│   ├── claudeignore              ← → .claudeignore にコピー
│   ├── agentignore               ← → .agentignore にコピー
│   └── marprc.yml                ← → .marprc.yml にコピー
├── dotvscode/                    ← セットアップ時に .vscode/ にリネーム（下記参照）
├── lab/
│   ├── slides/                   ← Marp テーマ・ビルドスクリプト
│   └── latex/                    ← LaTeX 共通プリアンブル・latexmk 設定・論文雛形
├── project_a/ / project_b/       ← 個別プロジェクト
└── publications/                 ← 発表・配布物
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
   cp dotclaude/claudeignore .claudeignore
   cp dotclaude/agentignore .agentignore
   cp dotclaude/marprc.yml .marprc.yml
   # セキュリティ設定を配置
   cp dotclaude/settings.json.example dotclaude/settings.local.json
   # ディレクトリをリネーム
   mv dotclaude .claude
   mv dotvscode .vscode
   ```
   **PowerShell:**
   ```powershell
   Copy-Item dotclaude/claudeignore .claudeignore
   Copy-Item dotclaude/agentignore .agentignore
   Copy-Item dotclaude/marprc.yml .marprc.yml
   Copy-Item dotclaude/settings.json.example dotclaude/settings.local.json
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
   - Codex は `AGENTS.md` を自動で読むため、Codex 固有の運用ルールは `AGENTS.md` に集約する
   - `.env`、`*.pem`、`*.key`、`credentials/` などの機密ファイルは、Claude Code / Codex のどちらでも読ませない・コミットしない
   - **Windows + Codex:** ネイティブ Windows よりも、WSL 上でこのコピーを行う方が安定しやすい

4. **セキュリティ設定の確認**
   - `.claude/settings.local.json` に deny ルールが含まれていることを確認する（手順2で配置済み）
   - 内容をユーザに説明し、必要に応じて調整を提案する
   - 初回セットアップでは **確認モードのまま** 進め、危険な操作に `Always allow` を付けない
   - `git push`、依存追加、ネットワークアクセス、作業フォルダ外の読み書き、大量削除は都度ユーザ確認を取る

5. **CLAUDE.md のカスタマイズ**
   - ユーザに研究分野・用途・並走プロジェクト数・応答言語をヒアリングする
   - 回答をもとに [CLAUDE.md](./CLAUDE.md) の `[角括弧]` 部分を書き換える

6. **AGENTS.md のカスタマイズ**
   - ユーザの研究分野に合わせて [AGENTS.md](./AGENTS.md) を調整する
   - このテンプレートは Claude Code と Codex の併用を前提にしている。CLAUDE.md は Claude Code 専用、AGENTS.md は両方が読む共通ルール。どちらか一方しか使わない場合は、不要な方の記述をユーザに確認の上で削除する
   - `.claude/agents/` のエージェント定義はサンプルである。ユーザの研究分野に合わないものがあれば削除を提案する

7. **プロジェクトディレクトリのリネーム**
   - ユーザの研究テーマに合わせて `project_a/`, `project_b/` をリネームする
   - 各プロジェクトの `CLAUDE.md` と `README.md` も更新する

8. **初回コミット**
   - セットアップ完了後、変更をまとめてコミットする（push はユーザの許可を得てから）

## 使い方の目安

- 研究データは `project_x/sources/`
- 分析コードは `project_x/scripts/`
- 生成結果は `project_x/outputs/`
- メモや下書きは `project_x/docs/`
- 発表・配布物は `publications/`
- 横断的な設定・テーマ・雛形は `lab/`、繰り返す作業の手順は `.claude/skills/`

## セキュリティ設定

セットアップ手順で `.claude/settings.local.json` が自動配置されます。
force push や `rm -rf` などの危険なコマンドが deny ルールでブロックされており、誤って「Always allow」を押しても安全です。
.env / 証明書 / 鍵 / `credentials/` / `secrets/` も読み取り対象から外す想定です。
追加のルールが必要な場合は `.claude/settings.local.json` を編集してください（`.gitignore` で除外済み）。

この設定は Claude Code 用です。Codex を使う場合は、Codex 側のセキュリティ設定を別途確認してください。
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
  - `academic-ja`（`lab/slides/academic-ja.css`）— 16:10・本文29px。和文の学会発表と授業用
  - `academic-intl`（`lab/slides/academic-intl.css`）— 16:9・本文32px・ラテン書体優先。国際学会（英語）用
  - 判型も基準文字サイズも違うので、`theme:` だけ差し替えると全枚数がリフローする。用途に合う方で最初から書く
- **新規作成はゼロからではなく `lab/slides/templates/` の雛形のコピーから始める**
- Markdown のフロントマターに `marp: true` と書けばプレビューが有効になる
- 図（SVG）の文字サイズは `lab/slides/check_svg_text.py` が検査する。`build_marp.sh` 経由なら自動で走る
- Claude Code では `/build-slide <パス>` で PDF・PPTX を出力できる

### LaTeX 論文

TeX Live（Mac は MacTeX）が必要です（セットアップ手順の環境チェックでインストールを案内します）。

**雛形の選び方・使い方・文献の書き方は [publications/README.md](./publications/README.md) にまとめてあります。**

- 雛形は `lab/latex/templates/` に。`paper/`（短い論文・動作確認）、`thesis/`（学位論文。章分割・部・史料／研究文献の分離）、`resume/`（レジュメ）、`transcript/`（口頭発表原稿）
- **LaTeX はすべて `lab/latex/` にある。**新しい学会テンプレートを足すときは、ここにフォルダを1つ置けば LaTeX 直書きでも `/md-to-pdf` でも使える（手順は `lab/latex/templates/README.md`）
- `lab/latex/preamble-ja.tex` が日欧混在の学術論文用共通プリアンブル（LuaLaTeX + jlreq + biblatex）
- `lab/latex/.latexmkrc` を各プロジェクトにコピーまたは参照して使う
- LaTeX Workshop が保存時に自動ビルドし、VSCode 内で PDF プレビューできる
- LaTeX を書かずに、ふつうの Markdown から同じ体裁の PDF・docx を作ることもできる（`/md-to-pdf`・`/md-to-docx`）
- 書誌は `lab/latex/references.bib` の1本にまとめる。Zotero（Better BibTeX）の自動エクスポート先に指定して使う

## Codex（ChatGPT）で使う場合

このテンプレートは **Claude Code と Codex の併用**を前提に設計されています。
両方をそのまま使えますが、それぞれの設定ファイルの役割が異なります。

- **CLAUDE.md** — Claude Code だけが読む詳細指示
- **AGENTS.md** — Claude Code と Codex の両方が読む共通ルール

Codex は `AGENTS.md` を自動的に読み込むため、基本ルール・ディレクトリ規約はそのまま機能します。
インストールや初回起動は、Codex Quickstart（https://developers.openai.com/codex/quickstart）を見るのが確実です。
Windows で Codex を使う場合は、OpenAI 公式も **WSL ワークスペース** を推奨しています。Windows guide（https://developers.openai.com/codex/windows）に沿って進めると安定します。

Codex を中心に使いたい場合は、エージェント定義を `.agents/` にコピーしてください。

```bash
# エージェント定義を Codex 用ディレクトリにコピー
mkdir -p .agents
cp -r .claude/agents/* .agents/

# スキルを Codex 用ディレクトリにコピー
mkdir -p .agents/skills
cp -r .claude/skills/* .agents/skills/
```

| 機能 | Claude Code | Codex |
|------|:-----------:|:-----:|
| AGENTS.md の基本ルール | ✅ | ✅ |
| CLAUDE.md の詳細指示 | ✅ | ❌（AGENTS.md に集約してください） |
| エージェント定義 | `.claude/agents/` | `.agents/` にコピー |
| スキル（SKILL.md） | `/スキル名` で呼び出し | プロンプトで手順を指示 |
| セキュリティ設定 | `settings.local.json` | Codex 側の設定を参照 |

> スキルの自動呼び出し（`/daily-start` 等）は Claude Code 固有の機能です。
> Codex では SKILL.md の内容をプロンプトに貼り付けるか、手順を AGENTS.md に転記して使ってください。

## 補足

- `project_a` と `project_b` はサンプル名です。自分の用途に合わせて名前を変えて構いません
- `CLAUDE.md` と `AGENTS.md` は完成品ではなく、書き換え前提のテンプレートです
- `.claude/agents/` のエージェント定義も雛形です。不要なものは削除して構いません
- `dotclaude/` と `dotvscode/` は GitHub テンプレート配布のためにリネームしてあります。セットアップ手順で `.claude/` や `.vscode/` 等に展開されます
