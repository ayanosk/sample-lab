# publications

**完成した提出版・配布版・公開版を集める場所です。** PDF と PPTX だけを置きます。

原稿・図・中間ファイルはここではなく、各プロジェクトの [work/<プロジェクト>/drafts/](../work/) に置きます。
ビルドすると、完成版がここへ自動でコピーされます。手でコピーする必要はありません。

```text
work/project_a/drafts/2026_annual_meeting/   ← 制作（原稿・図・.tex などの中間ファイル）
    slides.md
    slides.pdf
    figures/                                 ← この原稿で使う図。原稿ごとに持つ
publications/2026_annual_meeting/            ← 完成版（自動で集まる）
    slides.pdf
```

**なぜ分けるか。** 原稿と中間ファイルを完成版と同じ場所に置くと、提出するファイルがどれか分からなくなります。
また、同じ内容を学会・論文誌・ポスターへ展開するとき、制作物は増える一方で、外に出すものは一つずつです。

## ビルド方法

原稿の置き場所と、そこから成果物を作る手段の対応です。**原稿はすべて `work/<プロジェクト>/drafts/<名前>/` に置きます。**

| 作りたいもの | 原稿 | ビルド |
|---|---|---|
| 発表スライド（PDF / PPTX） | Marp の Markdown | `/build-slide <パス>` |
| 論文・学位論文・レジュメ（PDF） | LaTeX の `.tex` | `latexmk`（保存時の自動ビルド） |
| 同上（PDF） | ふつうの Markdown | `/md-to-pdf <パス>` |
| コメントをもらう原稿（docx） | ふつうの Markdown | `/md-to-docx <パス>` |

原稿を LaTeX で書くか Markdown で書くかは好みで選べます。**体裁を細かく詰めるなら
LaTeX、書くことに集中したいなら Markdown** が目安です。どちらも同じ書誌データ
（`bibliography/references.bib`）を使います。

### スライド

> この節がスライド作成の説明の正本です。他の README・スキル・雛形からはここを参照します。

**1. テーマを選ぶ** — フロントマターの `theme:` で指定します。判型も基準文字サイズも違うので、途中で差し替えると全枚数がリフローします。用途に合う方で最初から書いてください。

| 用途 | `theme:` | 判型・本文 | 雛形 |
|---|---|---|---|
| 和文の発表・授業 | `academic-ja` | 16:10 (1280×800) / 29px | `.claude/skills/build-slide/assets/templates/template_academic-ja.md` |
| 国際学会（英語） | `academic-intl` | 16:9 (1280×720) / 32px | `.claude/skills/build-slide/assets/templates/template_academic-intl.md` |

**2. 雛形をコピーして書き始める** — ゼロから書く必要はありません。雛形は**テーマのレイアウトと記法のサンプル集**です。1枚が1クラスに対応し、そのスライドの本文に記法の説明が書いてあります。要らない枚を削り、残した枚の中身を差し替えて使ってください。サンプル図は `lab/assets/figures/` にあります。

コピー先は `work/<プロジェクト>/drafts/<イベント>/` です。PDF・PPTX は原稿mdと同じディレクトリに出て、**完成版が `publications/<イベント>/` にも集まります。**

**3. ビルドする**

```bash
# Claude Code
/build-slide work/<プロジェクト>/drafts/<イベント>/my_presentation.md

# Mac / Linux / Git Bash / WSL
bash .claude/skills/build-slide/scripts/build_marp.sh --pdf  work/<プロジェクト>/drafts/<イベント>/my_presentation.md
bash .claude/skills/build-slide/scripts/build_marp.sh --pptx work/<プロジェクト>/drafts/<イベント>/my_presentation.md

# Windows の PowerShell など、直接 Marp CLI を使う場合（リポジトリルートで実行）
npx @marp-team/marp-cli --allow-local-files --pdf  work/<プロジェクト>/drafts/<イベント>/my_presentation.md
npx @marp-team/marp-cli --allow-local-files --pptx work/<プロジェクト>/drafts/<イベント>/my_presentation.md
```

`/build-slide` は Claude Code 固有の機能です。Codex など他のツールでは、上のコマンドをそのまま実行するか「`work/<プロジェクト>/drafts/...` のスライドを PDF と PPTX にビルドして」と指示してください。

**PPTX は2種類あります。** 出力ファイル名はどちらも `<名前>.pptx` なので、両方は持てません。

| | 体裁 | PowerPoint での編集 | 必要なもの |
|---|---|---|---|
| `--pptx`（既定） | 崩れない（各ページを画像として貼る） | できない。文字の検索もリンクもできない | ブラウザのみ |
| `--pptx-editable` | **ずれることがある** | できる（文字が文字のまま入る） | LibreOffice |

会場のPCに挿して映すだけなら既定で十分です。渡した相手が手を入れる場合だけ `--pptx-editable` を使い、**生成後に必ず開いて体裁を確かめてください**（Marp CLI では実験的機能の扱いです）。

> **Marp CLI を直接叩いた場合、完成版は `publications/` に集まりません。**
> `build_marp.sh` か `/build-slide` を使うと自動でコピーされます。

`build_marp.sh` はどのディレクトリから実行してもよく、Marp 本体（グローバル / ローカル / `npx`）も自動で探します。うまく動かないときは `MARP_BIN`（marp の実行体）、`MARP_BROWSER_PATH`（ブラウザ）で明示指定できます。

**4. 図（SVG）の文字サイズを検査する**

SVG の `font-size` は viewBox のユーザ単位なので、図が枠に合わせて縮むと文字も一緒に縮みます。会場の後方から読めない図は、たいていこれが原因です。

```bash
python3 .claude/skills/build-slide/scripts/check_svg_text.py work/<プロジェクト>/drafts/<イベント>/my_presentation.md
```

- `build_marp.sh` を使う場合はビルド時に自動で走ります（ビルドは止めません。`MARP_SKIP_SVG_CHECK=1` で抑止）
- 一括修正は `--fix`。font-size を一律拡大するだけで図形は動かさないため、適用後は必ず出力PDFを目視確認してください
- **作図の実用則: viewBox を `academic-ja` なら 1208×560、`academic-intl` なら 1168×460 以内で作り、最小 `font-size` を 18／20 以上にする**

### 論文・レジュメ・学位論文

雛形は `.claude/skills/md-to-pdf/assets/templates/` にあります。**フォルダごと `work/<プロジェクト>/drafts/<名前>/` にコピーして、`main.tex` を編集するだけ**です。パスの書き換えは要りません。

| 用途 | 雛形 | 特徴 |
|---|---|---|
| 短い論文・動作確認 | `paper/` | 1ファイル。まずこれをビルドして環境を確認する |
| 学位論文・長い論文 | `thesis/` | 章を `chapters/` に分割。部（`\part`）と、史料／研究文献に分けた文献一覧つき |
| レジュメ・配布資料 | `resume/` | 1ファイル完結。囲み枠・図の回り込み・手書きの参考文献リスト |
| 口頭発表原稿 | `transcript/` | 読み上げ用。`/md-to-pdf` 専用（LaTeX 直書きの雛形はなし） |

```bash
cp -r .claude/skills/md-to-pdf/assets/templates/paper work/<プロジェクト>/drafts/20260911_mypaper
cd work/<プロジェクト>/drafts/20260911_mypaper && latexmk main.tex
```

> **雛形の置き場所のままビルドしないでください。** スキルの中に出力が散らかります。必ずコピーしてから使います。
> コピー先はリポジトリ内ならどの深さでもかまいません。`.latexmkrc` がリポジトリルートを自分で探します。

**共通ファイル**（`.claude/skills/md-to-pdf/assets/`）

- `preamble-ja.tex` — 日欧混在の学術論文用プリアンブル（LuaLaTeX + jlreq + biblatex）。
  脚注形式の引用、言語別の句読点・引用符の切替、邦語／欧語で異なる短縮引用に対応
- `md-common.tex` — `/md-to-pdf` が使う共通プリアンブル（citeproc 用）
- `latexmkrc-common.pl` — LuaLaTeX + biber のビルド設定。`TEXINPUTS` / `BIBINPUTS` もここで設定する

`main.tex` が `\input{preamble-ja}` とパスなしで書けるのは、`.latexmkrc` が検索パスを通しているためです。

**文献の分類**（`thesis/`）

参考文献一覧の節分けは `.bib` の `keywords` で行います。`source-archive` は未公刊史料、
`source-printed` は刊行史料、どちらも付けなければ研究文献です。`keywords = {japanese}` を
付けた文献は邦語文献として別立てで出力されます。分類を増やすときは `.bib` と
`main.tex` の `\printbibliography` の両方に同じキーワードを足してください。

> **TeX Live のバージョンに注意。** 共通プリアンブルは `\AddToHook`（LaTeX 2020-10 以降）と
> LuaTeX の文字コード判定を使います。TeX Live 2019 以前では引用の書式が正しく組めません。
> 現行の TeX Live（Mac は MacTeX）を入れてください。

### Markdown から PDF・docx

LaTeX を書かずに、ふつうの Markdown から同じ体裁の PDF を作れます。

```bash
/md-to-pdf work/<プロジェクト>/drafts/<イベント>/resume.md --author "山田太郎" --date "2026-09-11"
/md-to-docx work/project_a/docs/draft_ch3.md
```

レイアウトは frontmatter の `template:` キーか `--layout` で選びます（旧 `pdf:` キーも読めます）。

| `template:` | 体裁 | 用途 |
|---|---|---|
| `resume`（既定） | 9pt・詰め組・右上に作成者/日付 | ゼミ・会議の配布レジュメ |
| `paper` | 10.5pt・40字×30行・末尾に参考文献 | 短い論文、原稿の確認 |
| `thesis` | 同上＋見出し1が「第n章」になる | 学位論文の章単位の原稿 |
| `transcript` | 12pt・36字×22行・広い行間 | 口頭発表の読み上げ原稿 |

```yaml
---
title: 発表原稿のタイトル
template: transcript
---
```

レイアウト名は `.claude/skills/md-to-pdf/assets/templates/` のフォルダ名です。**新しい学会テンプレートを足すときも、
ここにフォルダを1つ作るだけ**で、LaTeX 直書きと `/md-to-pdf` の両方で使えるようになります。
手順は [templates/README.md](../.claude/skills/md-to-pdf/assets/templates/README.md) にあります。

PDF は原稿の隣に出て、原稿が `work/<プロジェクト>/drafts/` の下にあれば完成版が `publications/` にも集まります。

部（`\part`）や、史料と研究文献に分けた文献一覧が要る完成稿は、Markdown ではなく
`thesis/main.tex` の LaTeX 雛形で組んでください。

### 書誌データと Zotero

**書誌はリポジトリで1本にまとめます: `bibliography/references.bib`**

Zotero を使う場合は、Better BibTeX プラグインの自動エクスポート先をこのファイルに
指定します（Zotero でライブラリを右クリック → Export Library → 形式に Better BibTeX
を選び、**Keep updated** にチェック）。以後、Zotero に文献を足すとファイルが自動で
更新されます。Zotero を使わない場合は、このファイルに直接書き足しても構いません。

> **書誌は `bibliography/` に置き、スキルの中には入れません。** スキルは入れ替えても、
> 積み上げた書誌は残るようにしてあります。引用スタイル（`.csl`）も同じ理由でここに置きます。

参照のしかた:

- **Markdown**（`/md-to-pdf`・`/md-to-docx`）: 本文に `[@citekey]` と書くと脚注書誌になります。
  ページ指定は `[@citekey, 42]`
- **LaTeX**: `main.tex` の `\addbibresource{references.bib}` はそのままで、本文で `\autocite{citekey}`

> **日本語の著者名は `author = {山田太郎}` と姓名を区切らず1語で書いてください。**
> 区切り方によって、3つの書誌エンジンが別々の壊れ方をします。

| 書き方 | biblatex（LaTeX直書き） | citeproc（`/md-to-pdf`） | pBibTeX（学会クラス） |
|---|---|---|---|
| `{山田太郎}` | 山田太郎 | 山田太郎 | 山田太郎 |
| `{山田 太郎}` | 姓が「太郎」に | 姓が「太郎」に | 山田太郎 |
| `{山田, 太郎}` | 山田太郎 | 山田太郎 | 「太郎山田」と反転 |

区切らない形だけが全部で正しく出ます。Zotero では姓のフィールドに姓名をまとめて入れると、この形で出力されます。欧語名は `{Smith, John}` のままで構いません。

> **`.bib` のコメント欄にアットマーク記号を書かないこと。** BibTeX は行頭以外でも
> アットマークを見つけるとエントリの開始とみなし、`I was expecting a '{'` で止まります。
