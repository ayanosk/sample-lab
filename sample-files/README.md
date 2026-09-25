# sample-files

一通りのワークフローを体験するためのサンプルファイルです。

**自分のワークフローを整えたら、フォルダごと削除して構いません。**

## Marpスライドの作成／PDF・PPTXの出力

`sample-files/sample-slides/sample_slide.md` を開き、プレビュー画面（Marp for VS Code）で
完成イメージを見ながら中身を編集してみてください。テーマと雛形は
`.claude/skills/build-slide/assets/` にあります。

```bash
/build-slide sample-files/sample-slides/sample_slide.md
```

PDF・PPTX は原稿と同じフォルダに出ます。

## LaTeX論文・レジュメの作成／PDF・DOCXの出力

`sample-files/sample-papers/sample_ipsj_jpaper.md` は、情報処理学会論文誌の体裁で組めるサンプル原稿です。

```bash
/md-to-pdf sample-files/sample-papers/sample_ipsj_jpaper.md
```

frontmatter の `template:` がレイアウト名（`.claude/skills/md-to-pdf/assets/templates/` のフォルダ名）です。
`resume` `paper` `thesis` `transcript` `ipsj` を差し替えると体裁が変わります。

LaTeX を直接書く場合は、雛形をコピーして使います。

```bash
cp -r .claude/skills/md-to-pdf/assets/templates/paper work/publications/test_paper
cd work/publications/test_paper && latexmk main.tex
```

docx が要るときは `/md-to-docx <パス>` です。

## 本番の原稿はどこに置くか

**サンプルを試したあと、実際の原稿は `work/publications/<名前>/` に置いてください。**
そこでビルドすると、完成版の PDF・PPTX が `publications/<名前>/` に自動で集まります。

手順・コマンド・作図の基準は [publications/README.md](../publications/README.md) にまとめてあります。
