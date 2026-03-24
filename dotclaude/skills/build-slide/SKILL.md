---
name: build-slide
description: MarpスライドMDからPDFとPPTXを生成する。publications/以下のパスを指定する。
argument-hint: "<publications/以下のパス> [--pdf-only|--pptx-only]"
---

# スライドビルド

**引数:** $ARGUMENTS

## 手順

### 1. パスの決定

引数からファイルパスとフラグを読み取る。

- `--pdf-only` / `--pptx-only` フラグを確認
- パスは `publications/` から始まるフルパスを期待する

引数が省略された場合はIDEで開いているファイルを確認するか、ユーザーに確認する。

### 2. ファイルの存在確認・フロントマター確認

ファイルを読み込み `marp: true` があることを確認。テーマはmdのフロントマターに従う。

### 3. Marp ビルド

**リポジトリルートで実行すること。**

**PDF（`--pptx-only` でない場合）:**
```bash
npx @marp-team/marp-cli --allow-local-files --pdf [パス]
```

**PPTX（`--pdf-only` でない場合）:**
```bash
npx @marp-team/marp-cli --allow-local-files --pptx [パス]
```

> 注: CSSテーマを使う場合は `--theme` オプションを追加する。
> Mac でビルドスクリプト（`lab/slides/build_marp.sh`）がある場合はそちらを優先してもよい。
> Windows では `build_marp.sh` は動作しないため、上記の `npx` コマンドを使うこと。

### 4. 確認と報告

生成ファイルのサイズを確認して報告する。画像が表示されない場合はリポジトリルートで実行しているか確認する。

## 使用例

```
/build-slide publications/slides/my_presentation.md
/build-slide publications/slides/lecture01.md --pdf-only
```
