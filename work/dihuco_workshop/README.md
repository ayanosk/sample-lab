# dihuco_workshop

一通りのワークフローを体験するためのサンプルです。**`project_a/` と同じ形をした作業単位**なので、
本番と同じ操作感で試せます。**自分のワークフローを整えたら、フォルダごと削除して構いません。**

```text
work/dihuco_workshop/
  sources/ scripts/ generated/ docs/      ← 作業単位の標準の形（このサンプルでは空）
  drafts/
    sample_slide/
      sample_slide.md
      figures/                            ← この原稿で使う図を入れる
    sample_resume/
      sample_resume.md
      figures/
```

## Marpスライドの作成／PDF・PPTXの出力

`drafts/sample_slide/sample_slide.md` を開き、プレビュー画面（Marp for VS Code）で
完成イメージを見ながら中身を編集してみてください。テーマと雛形は
`.claude/skills/build-slide/assets/` にあります。

```bash
/build-slide work/dihuco_workshop/drafts/sample_slide/sample_slide.md
```

PDF・PPTX は原稿と同じフォルダに出ます。あわせて、**完成版が `publications/sample_slide/` にも集まります。**
`drafts/` の下でビルドすると収集が働く、という動きをここで確認できます。

## LaTeX論文・レジュメの作成／PDF・DOCXの出力

`drafts/sample_resume/sample_resume.md` は、配布レジュメの体裁で組めるサンプル原稿です。
見出しの階層・脚注・引用・引用キーによる文献参照・表・箇条書きが一通り入っています。

```bash
/md-to-pdf work/dihuco_workshop/drafts/sample_resume/sample_resume.md
```

frontmatter の `template:` がレイアウト名（`.claude/skills/md-to-pdf/assets/templates/` のフォルダ名）です。
`resume` `paper` `thesis` `transcript` を差し替えると体裁が変わります。

同じ原稿がそのまま docx にもなります。**こちらは pandoc だけで動くので、LaTeX が入っていなくても試せます。**

```bash
/md-to-docx work/dihuco_workshop/drafts/sample_resume/sample_resume.md
```

> **本文の出典**　総務省『令和8年版 情報通信白書』第Ⅰ部第3章第1節から引用しています。
> 同白書は「政府標準利用規約（第2.0版）」に基づき、出典を記載すれば複製・翻案・再配布が
> 自由で、商用利用も認められています（同規約は CC BY 4.0 と互換）。詳細は [NOTICE](../../../NOTICE) に。

LaTeX を直接書く場合は、雛形をコピーして使います。

```bash
cp -r .claude/skills/md-to-pdf/assets/templates/paper work/dihuco_workshop/drafts/test_paper
cd work/dihuco_workshop/drafts/test_paper && latexmk main.tex
```

docx が要るときは `/md-to-docx <パス>` です。

## 本番の原稿はどこに置くか

**自分の研究の原稿は、その研究のプロジェクトの中に置きます**（`work/<プロジェクト>/drafts/<原稿名>/`）。
置き場の考え方は [work/README.md](../README.md)、ビルドの手順は
[publications/README.md](../../publications/README.md) にまとめてあります。
