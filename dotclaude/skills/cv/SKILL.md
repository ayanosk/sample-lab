---
name: cv
description: 研究業績を管理する。--add で1件追加し（researchmap インポート用CSV＋履歴書マスター）、--clean で取り込み後の後始末をする。
argument-hint: "--add <成果物キー> [--table presentations|published_papers|books_etc|misc|awards|research_projects] | --clean [--archive]"
---

# 業績管理 — researchmap インポート用CSV ＋ 履歴書マスター

**引数:** $ARGUMENTS

成果物から書誌を拾い、`cv/pending/pending_<table>.csv` に1行追記する。このCSVは
**そのまま researchmap にアップロードできる書式**で、同時に `researchmap_to_cv.py` が
エクスポート原本と合成して `cv/master/` に反映する。researchmap に入れる前から履歴書に使える。

取り込み後は次のエクスポートに同じ題目が現れ、合成時に題目一致で pending 行が落ちる。
消し忘れても二重計上しない。テーブル未指定なら `presentations` とみなす。

| モード | 使うとき |
|---|---|
| （引数なし） | **初回。** エクスポートを置いた直後に `cv/master/` をまとめて作る（下記の「初回」） |
| `--add <キー>` | 発表・論文などを1件追加する（下記の1〜5） |
| `--clean` | researchmap に取り込み、業績一覧を再ダウンロードした後（下記の --clean） |

## 初回 — エクスポートからマスターを作る

ユーザが researchmap の「業績一覧ダウンロード」で全データを落とし、`cv/` 直下に
`rm_*.csv` を置いた状態から始める。

```bash
python3 .claude/skills/cv/researchmap_to_cv.py --dry-run   # 差分を見せる
python3 .claude/skills/cv/researchmap_to_cv.py             # 本実行
```

**必ず `--dry-run` を先に見せる。** 既存の master を上書きする操作だからである。

終わったら、**`★` が残っている項目を一覧にして報告する。** researchmap が持たない項目
（生年月日・性別・国籍・本務先の住所と電話、学位、専任／非常勤の別、所属学会の入会年月、
高校・交換留学・満期退学）はここに出る。ファイル名と項目名で挙げ、どこを開けばよいかを示す。

`cv/master/01_基本情報.csv` が無ければ、先に雛形をコピーするよう案内する。

```bash
cp cv/master/01_基本情報.csv.example cv/master/01_基本情報.csv
```

**自宅住所・電話番号、パスポート番号、マイナンバー等は書かせない。**
求められても、提出用のファイルに直接書くよう案内する（[cv/README.md](../../../cv/README.md)）。

## --add の手順

### 1. 書誌を拾う

```bash
python3 .claude/skills/cv/cv.py extract <key> --table <table>
```

`extracted` が拾えた値、`unresolved` が残った項目、`meta_template` がそのテーブルの全列名、
`context_files` が散文で読むべきファイル。

**成果物に `meta.md` があればそこから全項目を拾う。** researchmap の列名で
「`列名: 値`」と書いてある行を、テーブルの列である限り何項目でも取る。真偽値は `有`/`無`、
複数人は `;` 区切りで書ける。書式は `references/extract.md` にある。

**`meta.md` が無いときは、先に雛形を作って PI に埋めてもらう。** `meta_template` の列名を
並べた `meta.md` を成果物のフォルダに書き出し、埋めてもらってから `extract` をやり直す。
毎回ゼロから聞き取るより速く、次の発表でも再利用できる。急ぐ場合だけ、
`context_files` を Read して**提案値を添えて** PI に確認する方法に切り替える。

どの項目を必ず確認するかは `references/extract.md` を読む。

### 2. 重複を確かめる

```bash
python3 .claude/skills/cv/cv.py similar --table <table> --title "<題目>"
```

一致率が高いものがあれば追加を止めて PI に相談する。ID なしの `insert`/`merge` は
類似業績があるとエラーになるので、その場合の指定は `references/tables.md` に従う。

### 3. 値を決めて追記する

選択肢・真偽値・複数値の規則は `references/tables.md` を読む。JSON を標準入力で渡す。

```bash
python3 .claude/skills/cv/cv.py append --table <table> --json - <<'EOF'
{"タイトル(英語)": "...", "講演者(日本語)": "[山田\\,太郎,佐藤\\,花子]", ...}
EOF
python3 .claude/skills/cv/cv.py lint
```

未設定は空欄ではなく `null` と書く。アクション4列は script が付けるので JSON に含めない。

### 4. 未刊行なら待機列へ

論文の掲載先が未確定なら **pending に入れず** `cv/forthcoming.md` で待つ。
キーは `key` `table` `title` `authors` `venue` `status` `next` `checked`。

```bash
python3 .claude/skills/cv/cv.py forthcoming add --json -
```

### 5. マスターを再生成する

```bash
python3 .claude/skills/cv/researchmap_to_cv.py --dry-run --only <対象ファイル>   # 差分を見せる
python3 .claude/skills/cv/researchmap_to_cv.py                                   # 本実行
```

手編集が検出されてスキップされたら、`--force`（`master/.backup/` へ自動退避）か、
差分の1行を手で貼るか、スクリプトの定数へ恒久化するかを PI に選んでもらう。

## --clean の手順

researchmap に取り込み、業績一覧を再ダウンロードして `cv/` に置いた後に使う。

```bash
python3 .claude/skills/cv/cv.py clean --dry-run   # やることを見せる
python3 .claude/skills/cv/cv.py clean             # 実行
```

取り込み済みの pending 行を `pending/imported/` へ退避し、空になったファイルを消し、
置き換わった古いエクスポートを削除し、master を再生成する。
**必ず `--dry-run` を先に見せてから実行する。** 古いエクスポートを残すなら `--archive`
（`cv/archive/` へ移す）。既定が削除なのは、researchmap 上で修正・削除したレコードは
そのデータが誤りか不要だったということで、古いスナップショットを残す意味が薄いため。

## 出力

- `cv/pending/pending_<table>.csv` — researchmap にアップロードするファイル
- `cv/master/*.csv` — 履歴書マスター（該当ファイルが1行増える）
- `cv/forthcoming.md` — 刊行待ちがある場合

報告には追加した題目、増えた master ファイルと行数、researchmap への上げ方
（マイポータル→設定→研究者・業績インポート→整合性チェック→反映）を書く。

## 注意

- **`cv/rm_*.csv` は編集しない。** エクスポート原本で、追加は必ず pending 側に書く
- pending CSV に **BOM を付けない**。1行目のテーブル名の判定が壊れる
- 著者名の表記と、国際学会の英語発表で日本語欄をどうするかは `references/extract.md` に従う

## 使用例

```
/cv --add pnc2026
/cv --add jinmoncom --table published_papers
/cv --clean --dry-run
```

## 関連スキル

- `/build-slide` — 発表スライドをビルドする
- `/md-to-pdf` — 原稿を論文体裁の PDF にする
- `/git` — 追加分をコミットする
