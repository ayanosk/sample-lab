---
name: md-to-docx
description: Markdownを、コメント・変更履歴を付けてもらうためのdocxに変換する。Wordネイティブ脚注・明朝本文・ゴシック見出し・A4。本文の[@key]はbibliography/references.bibで脚注書誌に展開する。
argument-hint: "<mdファイルパス> [タイトル] [--outdir DIR] [--number-sections]"
---

# Markdown → docx

**引数:** $ARGUMENTS

指導教員・共著者にコメントや変更履歴を付けてもらうための docx を作る。
LaTeX 原稿と同じ章・節構造（`\chapter{}`→見出し1、`\section{}`→見出し2）で出力される。

## 手順

### 1. 入力ファイルの決定

引数からMarkdownファイルのパスを読み取る。省略時はIDEで開いているファイルを使う。

### 2. 変換スクリプトの実行

```bash
bash .claude/skills/md-to-docx/md2docx.sh <入力mdパス> ["タイトル"]
```

スクリプトが自動で行うこと:

- **前処理**（md-to-pdf と同一）: `\chapter{X}` → 見出し1、`\section{X}` → 見出し2、`<sup>N</sup><span class="footnote">…</span>` → pandoc脚注
- **脚注**: Wordネイティブの脚注（ページ下部・自動採番）として出力
- **書誌**: `[@key]` は `bibliography/references.bib` + Chicago note CSL で脚注書誌に展開
- **体裁**: 同梱 `reference.docx` を適用。本文 Times New Roman + ＭＳ 明朝 12pt（行間1.5）、見出し Arial + ＭＳ ゴシック（黒）、A4縦・余白30mm
- **出力先**: 入力mdと同じフォルダ（`--outdir` で変更可）
- **表示**: 生成後にWordで自動オープン（`--no-open` で抑止）

オプション: `--number-sections`（見出しに自動採番）

### 3. 報告

スクリプト出力（`OK: <パス> (<サイズ>) title="…" footnotes=N`）を確認し、出力パス・サイズ・脚注数を報告する。**citeproc の「citation not found」警告が出た場合は、references.bib に無い引用キーとして必ず列挙して伝える**（docx自体は生成される）。

## 体裁の調整

`reference.docx` は `make_reference.py` が pandoc 既定から自動生成する（フォント・A4・行間のパッチ）。体裁を変えるときは make_reference.py を編集して再実行する。reference.docx を手で直接編集した場合は再実行で上書きされることに注意。

```bash
python3 .claude/skills/md-to-docx/make_reference.py
```

## 前提
- `pandoc`（`brew install pandoc`）。LaTeX は不要

## 使用例

```
/md-to-docx work/project_a/docs/draft_ch3.md
/md-to-docx work/publications/20260911_seminar/resume.md "ゼミレジュメ" --number-sections
```

## 関連スキル

- `/md-to-pdf` — 同じ原稿をレイアウト別PDF（resume/paper/thesis/transcript）に
