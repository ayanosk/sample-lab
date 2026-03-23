# sample-lab

Claude Code や Codex で研究室の作業を整理していくための、最小構成のサンプルリポジトリです。

## 目的

- プロジェクトごとに文脈を分ける
- `sources/` と `outputs/` を分けて、元データを壊しにくくする
- `lab/skills/` に再利用したい作業をまとめる
- `CLAUDE.md` と `AGENTS.md` で AI への指示を整理する

## ディレクトリ構成

```text
sample-lab/
├── CLAUDE.md / AGENTS.md         ← AI への指示書（書き換えて使う）
├── .gitignore / .claudeignore
├── .vscode/                      ← VSCode 推奨拡張・設定
├── .claude/
│   ├── agents/                   ← エージェント定義（history/ informatics/ support/）
│   ├── skills/                   ← スキル定義（build-slide, consult-agent 等）
│   └── settings.local.json.example ← セキュリティ設定の雛形
├── lab/
│   ├── slides/                   ← Marp テーマ・ビルドスクリプト
│   └── latex/                    ← LaTeX 共通プリアンブル・latexmk 設定
├── project_a/ / project_b/       ← 個別プロジェクト
└── publications/                 ← 発表・配布物
```

## 環境準備

### 必須

| ソフトウェア | インストール方法 | 用途 |
|------------|----------------|------|
| **Git** | https://git-scm.com/ （Mac は Xcode CLI Tools に同梱） | バージョン管理 |
| **GitHub アカウント** | https://github.com/ で作成。**二要素認証（2FA）を有効にすること** | リポジトリの管理・共有 |
| **VSCode** | https://code.visualstudio.com/ | エディタ（Claude Code・Marp・LaTeX の統合環境） |
| **Claude Code** | ターミナルで `curl -fsSL https://claude.ai/install.sh \| bash`（Mac/Linux）| AI エージェント |

### スライド作成に使う場合

| ソフトウェア | インストール方法 | 用途 |
|------------|----------------|------|
| **Node.js** | https://nodejs.org/ （LTS 推奨） | Marp CLI の実行環境 |
| **Marp CLI** | `npm install -g @marp-team/marp-cli` | スライドの PDF・PPTX 出力 |

### 論文執筆に使う場合

| ソフトウェア | インストール方法 | 用途 |
|------------|----------------|------|
| **TeX Live** | https://www.tug.org/texlive/ （Mac は [MacTeX](https://www.tug.org/mactex/)） | LaTeX 組版 |
| **Zotero**（任意） | https://www.zotero.org/ + [Better BibTeX](https://retorque.re/zotero-better-bibtex/) | 文献管理・`.bib` 自動エクスポート |

### データ分析に使う場合

| ソフトウェア | インストール方法 | 用途 |
|------------|----------------|------|
| **Python 3** | https://www.python.org/ （Mac は `brew install python`） | スクリプト実行・データ処理 |

> VSCode で初めてリポジトリを開くと、推奨拡張機能（Claude Code, Marp, LaTeX Workshop, PDF Viewer）のインストールが提案されます。

## 最初にやること

1. 上記の「必須」ソフトウェアをインストールする
2. この雛形を自分の GitHub に **Use this template** で複製する（**private** 推奨）
3. GitHub Desktop か `git clone` で手元に持ってくる
4. VSCode で開き、推奨拡張機能をインストールする
5. [CLAUDE.md](./CLAUDE.md) と [AGENTS.md](./AGENTS.md) を、自分の研究室や作業スタイルに合わせて書き換える
6. セキュリティ設定を行う（下記「セキュリティ設定」参照）
7. `project_a/` や `project_b/` を、自分の研究テーマ名に合わせてリネーム・追加する
8. Claude Code または Codex に「このリポジトリを整理したい」と相談しながら育てる

## 使い方の目安

- 研究データは `project_x/sources/`
- 分析コードは `project_x/scripts/`
- 生成結果は `project_x/outputs/`
- メモや下書きは `project_x/docs/`
- 発表・配布物は `publications/`
- 横断的な設定や Skills は `lab/`

## セキュリティ設定（推奨）

Claude Code を安全に使うために、以下の設定を推奨します。

### 1. 危険なコマンドのブロック

`.claude/settings.local.json` を作成し、破壊的な操作を deny ルールで禁止します。
同梱の `.claude/settings.local.json.example` をコピーして使えます。

```bash
cp .claude/settings.local.json.example .claude/settings.local.json
```

deny ルールは allow より優先されるため、誤って「Always allow」を押しても安全です。

### 2. サンドボックスの有効化（グローバル設定）

サンドボックスはファイルシステムとネットワークへのアクセスを OS レベルで制限する仕組みです。
これはプロジェクト単位ではなく、**グローバル設定**（`~/.claude/settings.json`）で管理します。

```json
{
  "sandbox": {
    "enabled": true,
    "filesystem": {
      "denyRead": ["~/"],
      "allowRead": [".", "~/Documents/GitHub"]
    },
    "network": {
      "allowedDomains": [
        "github.com", "api.github.com",
        "registry.npmjs.org", "pypi.org"
      ]
    }
  }
}
```

- `denyRead: ["~/"]` でホームディレクトリ全体をブロックし、作業フォルダだけ許可する
- `allowedDomains` で通信先を業務に必要なドメインだけに制限する
- `/sandbox` コマンドで現在の状態を確認できる

### 3. 確認モードで始める

初期設定の「確認モード」（実行前に毎回許可を求める）のまま使い始めてください。
慣れてきたら、deny ルールを設定した上で許可リストを追加していくのが安全です。

## ツール連携

### VSCode 拡張機能

VSCode でこのリポジトリを開くと、以下の拡張機能のインストールが推奨されます（`.vscode/extensions.json`）。

| 拡張機能 | 用途 |
|---------|------|
| **Claude Code** | AI エージェント本体 |
| **Marp for VS Code** | Markdown スライドのプレビュー |
| **LaTeX Workshop** | LaTeX の保存時自動ビルド・PDF プレビュー |
| **vscode-pdf** | PDF 閲覧（論文を横に開きながら作業） |

### Marp スライド

Node.js と Marp CLI が必要です（「環境準備」参照）。

- `lab/slides/academic-theme.css` がカスタムテーマとして登録済み
- Markdown のフロントマターに `marp: true` と書けばプレビューが有効になる
- `/build-slide` スキルで PDF・PPTX を出力できる
- `lab/slides/build_marp.sh` はブラウザを自動検出して Marp CLI を実行する

### LaTeX 論文

TeX Live（Mac は MacTeX）が必要です（「環境準備」参照）。

- `lab/latex/preamble-ja.tex` が日欧混在の学術論文用共通プリアンブル（LuaLaTeX + jlreq）
- `lab/latex/.latexmkrc` を各プロジェクトにコピーまたは参照して使う
- LaTeX Workshop が保存時に自動ビルドし、VSCode 内で PDF プレビューできる

### Zotero 文献管理（任意）

[Better BibTeX for Zotero](https://retorque.re/zotero-better-bibtex/) を使うと、Zotero の文献データベースと LaTeX を自動連携できます。

1. Zotero に Better BibTeX 拡張をインストール
2. コレクションを右クリック → Export Collection → **Better BibLaTeX** 形式
3. **Keep updated** にチェックし、エクスポート先をプロジェクト内の `.bib` ファイルに指定
4. Zotero で文献を追加・編集するたびに `.bib` が自動更新される
5. LaTeX 側は `\addbibresource{references.bib}` で読むだけ

`.bib` を git 管理しておけば、Zotero がない端末でもビルドが通ります。

## Codex（ChatGPT）で使う場合

このテンプレートは Claude Code 向けに最適化されていますが、Codex CLI でも基本的な作業は可能です。
Codex は `AGENTS.md` を自動的に読み込むため、基本ルール・ディレクトリ規約はそのまま機能します。

Codex を中心に使いたい場合は、以下のファイルを `.agents/` にコピーしてください。

```bash
# エージェント定義を Codex 用ディレクトリにコピー
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
