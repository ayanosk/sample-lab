---
name: build-slide
description: MarpスライドMDからPDFとPPTXを生成する。原稿は work/<プロジェクト>/drafts/<イベント>/、完成版は publications/<イベント>/ に出す。
argument-hint: "<スライドmdのパス> [--pdf-only|--pptx-only]"
---

# スライドビルド

**引数:** $ARGUMENTS

> **このスキルの `assets/` はエディタからも参照されている。**
> `assets/academic-ja.css` と `assets/academic-intl.css` は、`.marprc.yml` の `themeSet` と
> `.vscode/settings.json` の `markdown.marp.themes` が名指ししている。
> このスキルを削除・改名・移動すると、**Marp for VS Code のプレビューがエラーも出さずに崩れる。**
> 動かすときは、その2ファイルのパスも一緒に直すこと。

## 手順

### 1. パスの決定

引数からファイルパスとフラグを読み取る。

- `--pdf-only` / `--pptx-only` フラグを確認
- **原稿mdは `work/<プロジェクト>/drafts/<イベント名>/` に置く。** 中間ファイルもそこに残る
- **完成版の PDF・PPTX は `publications/<イベント名>/` に出す**（手順3で自動的にコピーされる）
- 新規作成なら `.claude/skills/build-slide/assets/templates/template_academic-ja.md`（和文）または
  `template_academic-intl.md`（英語）をコピーして始める
- 手順とテーマ・作図の基準の正本は `publications/README.md` の「スライド」節

引数が省略された場合はIDEで開いているファイルを確認した上で、生成前にチャットで確認する。

### 2. フロントマターの確認

ファイルを読み込み、`marp: true` と `theme:` があることを確認する。テーマは
`academic-ja`（和文・16:10）か `academic-intl`（英語・16:9）。テーマ名を書き換えると
判型と基準文字サイズが変わり全枚数がリフローするので、勝手に差し替えない。

### 3. Marp ビルド

**cd は不要。** `build_marp.sh` は自分の位置からリポジトリルートを解決し、Marpの実行体
（グローバル / ローカル / npx）も自動で探すので、**どのディレクトリから呼んでもよい**。
原稿mdのパスは、呼び出し元のカレントディレクトリ基準 → リポジトリルート基準の順に探す。

**PDF（`--pptx-only` でない場合）:**
```bash
.claude/skills/build-slide/scripts/build_marp.sh --pdf [パス] 2>&1
```

**PPTX（`--pdf-only` でない場合）:**
```bash
.claude/skills/build-slide/scripts/build_marp.sh --pptx [パス] 2>&1
```

ビルド前に `check_svg_text.py` が自動で走り、図中の文字が小さすぎる場合に警告する
（ビルドは止めない）。**警告が出たらユーザに報告し、黙って通さないこと。**
一括修正は `python3 .claude/skills/build-slide/scripts/check_svg_text.py --fix [パス]`。font-size を一律拡大する
だけで図形は動かさないため、適用後は必ず出力PDFを目視確認する。

**Windows の PowerShell など `build_marp.sh` が使えない環境:**
```bash
python3 .claude/skills/build-slide/scripts/check_svg_text.py [パス]   # 検査は手動で
npx @marp-team/marp-cli --allow-local-files --pdf [パス]
npx @marp-team/marp-cli --allow-local-files --pptx [パス]
```
この場合は**リポジトリルートで実行する**（`.marprc.yml` のテーマ設定がルート基準のため）。
`build_marp.sh` は `python3` が無ければ `python` を使う。どちらも無ければ検査を飛ばす。

### 4. 確認と報告

生成ファイルのサイズを確認して報告する。

うまくいかないときの切り分け:

| 症状 | 確認すること |
|------|------------|
| 図が出ない | `build_marp.sh` を経由しているか（`marp` を直接叩くと `--allow-local-files` とテーマが効かない）。md内の画像パスが原稿mdからの相対で正しいか |
| `marp コマンドが見つかりません` | `npm i -g @marp-team/marp-cli`。または `MARP_BIN` に実行体のパスを指定 |
| ビルドが落ちる | ヘッドレスブラウザの起動が禁止されている可能性。`MARP_BROWSER_PATH` でブラウザを明示指定 |

補助的な環境変数: `MARP_BIN` / `MARP_CLI_VERSION` / `MARP_BROWSER` / `MARP_BROWSER_PATH` / `MARP_SKIP_SVG_CHECK`

## 使用例

```
/build-slide publications/2026_annual_meeting/slides.md
/build-slide publications/lecture01/slides.md --pdf-only
```
