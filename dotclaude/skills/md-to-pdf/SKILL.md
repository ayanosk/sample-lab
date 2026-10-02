---
name: md-to-pdf
description: MarkdownをA4のPDFに変換する。レイアウトはfrontmatterの`template:`キー（旧`pdf:`も可）か--layoutで指定：resume=配布レジュメ/paper=論文体裁/thesis=学位論文体裁(章立て)/transcript=口頭発表原稿/ipsj=情報処理学会論文誌。テンプレートは .claude/skills/md-to-pdf/assets/templates/ にあり、フォルダを足すだけでレイアウトが増える。
argument-hint: "<mdファイルパス> [タイトル] [--layout resume|paper|thesis|transcript|ipsj] [--author 氏名] [--date YYYY-MM-DD]"
---

# Markdown → PDF

**引数:** $ARGUMENTS

## レイアウト

| 名前 | 体裁 | 用途 |
|------|------|------|
| `resume`（既定） | 9pt・余白15mm・詰め組・右上に作成者/日付 | ゼミ・会議の配布レジュメ。`--twocolumn` でさらに圧縮 |
| `paper` | 10.5pt・40字×30行・作成者非表示・末尾に参考文献 | 短い論文、原稿の確認用 |
| `thesis` | `paper` と同じ組で book クラス。見出し1が「第n章」になる | 学位論文の章単位の原稿 |
| `transcript` | 12pt・36字×22行・段落間空き・大きめページ番号 | 口頭発表の読み上げ原稿 |
| `ipsj` | 情報処理学会論文誌（`ipsj.cls`・2段組） | 投稿前の体裁確認。**pLaTeX で組まれる** |

指定は **frontmatter の `template:`** が基本（旧 `pdf:` も読む）。`--layout` はその上書き。どちらも無ければ `resume`。

```yaml
---
title: 発表原稿のタイトル
template: transcript
---
```

**部（`\part`）や、史料と研究文献に分けた文献一覧が要る完成稿は、md ではなく
`.claude/skills/md-to-pdf/assets/templates/thesis/main.tex` の LaTeX 雛形で組む。**

## 手順

```bash
bash .claude/skills/md-to-pdf/md2pdf.sh <入力mdパス> ["タイトル"] [options]
```

主なオプション:
- `--layout NAME`：レイアウトの明示指定
- `--author "氏名"` / `--date "2026-09-11"`：作成者・日付（`YYYY-MM-DD` は `YYYY年M月D日` へ自動整形。**`paper` と `thesis` は作成者を表示しない**＝原稿確認用）
- `--outdir DIR`：出力先。**既定は原稿の隣**。原稿が `work/publications/<名前>/` の下にあれば、完成版が `publications/<名前>/` にも自動で集まる
- `--fontsize 8pt` / `--margin 15mm` / `--twocolumn`：体裁の微調整
- `--no-secnum`：見出しに番号を振らない。原稿に「1. はじめに」と番号を書いてある場合、自動採番と二重になるので使う
- `--keep-h1`：冒頭の `# 見出し` を本文に残す（既定はタイトルブロックと重複するため除去）
- `--no-open`：生成後にPDFを開かない

スクリプトが行うこと:
1. **正規化**（`normalize.py`）：見出し直前の空行補完・リスト内コードフェンスの列0出し。本文の文言は変更しない
2. **前処理**：`\chapter{}`→`#`、`\section{}`→`##`、脚注span→pandoc脚注、callout マーカー除去、wikilink を表示テキストに
3. **pandoc**：本文をLaTeXフラグメント化。`[@key]` があれば citeproc + Chicago note で脚注書誌に展開
4. **テンプレート結合**：`.claude/skills/md-to-pdf/assets/templates/<レイアウト>/layout.tex` + `.claude/skills/md-to-pdf/assets/md-common.tex` を単一の `.tex` に
5. **LuaLaTeXコンパイル**：`latexmk -lualatex`。補助ファイルは自動で掃除

## 出力
- `<outdir>/<basename>.pdf` … 生成PDF（既定は原稿の隣。ページ数とレイアウトを報告）。`work/publications/` 配下なら `publications/` への収集も報告する
- `<outdir>/<basename>.tex` … 単一ソース（`latexmk -lualatex` で再コンパイル可・手直し可）

## レイアウトを増やす

**このスキルは LaTeX を一切持たない。**テンプレートは `.claude/skills/md-to-pdf/assets/templates/<名前>/layout.tex`
にあり、スクリプトは実行のたびにこのフォルダを走査してレイアウト名を認識する。
足すときはフォルダを1つ作るだけでよい（引数解析にも SKILL.md にも手を入れない）。
`layout.tex` 先頭の `%%!` 行がそのレイアウトの既定値になる。手順は
`.claude/skills/md-to-pdf/assets/templates/README.md`。

```tex
%%! fontsize     = 10pt
%%! classopts    = a4paper,fontsize=__FONTSIZE__,line_length=42zw,number_of_lines=32
%%! titleblock   = title-only   % resume / title-only / center-meta
%%! bibliography = list         % list（末尾に一覧）/ suppress（脚注のみ）
%%! toplevel     = default      % default（見出し1→節）/ chapter（→章）
```

### 学会指定のクラスファイルを使う場合

pLaTeX 専用のクラス（`ipsj.cls` など）も同じ仕組みに載る。レイアウトで engine と
common と citations を宣言し、`.cls` `.sty` `.bst` をレイアウトのフォルダに置く
（スクリプトが `TEXINPUTS` / `BSTINPUTS` にそのフォルダを追加する）。

```tex
%%! engine    = platex                  % lualatex（既定）/ platex
%%! common    = md-common-platex.tex    % LuaLaTeX 用の md-common.tex は使えない
%%! citations = natbib                  % 学会の .bst（BibTeX）に合わせる。既定は citeproc
```

投稿用の最終原稿は、巻号・受付日・英文要旨など Markdown から渡せない項目があるため、
同じフォルダの `main.tex` を `work/publications/<名前>/` にコピーして LaTeX で仕上げる。
このレイアウトは体裁の下見用と位置づける。

## 書誌（Zotero 連携）

本文に `[@citekey]` と書くと、`bibliography/references.bib` を引いて脚注書誌になる。
このファイルは Zotero の Better BibTeX から自動エクスポートする想定。

**日本語の著者名は `author = {山田, 太郎}` と姓と名をカンマで区切る。**
Zotero で姓・名の欄を分けて入れるとこの形になる。citeproc は CJK の人名を判別し、
文献一覧では「山田太郎」と連結し、脚注では「山田」に短縮する。
`{山田 太郎}` と空白で区切ると「名 姓」と読まれて姓が「太郎」になり、
`{山田太郎}` とまとめ書きすると全体が姓とみなされ脚注が短縮されない。**`.bib` のコメントにアットマーク記号を書かないこと**
（BibTeX がエントリ開始と誤認して止まる）。

## 前提
- **Python**（`python3` または `python`。Windows の python.org 版は `python` のみ）
- `pandoc`・`latexmk`・**LuaLaTeX** と、`jlreq` `luatexja-adjust` `enumitem` `fvextra` `adjustbox`（TeX Live）
- `engine = platex` のレイアウトを使う場合は `platex` `pbibtex` `dvipdfmx` も必要（TeX Live に同梱）

## 注意
- 入力は **Markdown(.md) のみ**。PDFやtexを渡すとエラーで止まる
- frontmatter の `bib:` で書誌ファイルを原稿ごとに差し替えられる（citeproc・natbib のどちらの経路でも効く）
- 引用キーが `references.bib` に無いと citeproc が「citation not found」を出す。**警告が出たキーは必ず列挙して報告する**
- `[@key]` を書いたのに書誌ファイルが無い場合、スクリプトが `WARN:` を出す。これも報告する
- pandocのMarkdown解釈は原稿構造に敏感。破綻したら `.tex` を直接手直しして再コンパイルするのが早い

## 使用例
```
/md-to-pdf work/publications/20260911_seminar/resume.md --author "山田太郎" --date "2026-09-11"
/md-to-pdf work/project_a/docs/draft_ch3.md --layout thesis
/md-to-pdf 発表原稿.md   # frontmatter に pdf: transcript があれば発表原稿体裁
```

## 関連スキル
- `/md-to-docx` — 同じ原稿を、コメント・変更履歴を付けられる docx に
