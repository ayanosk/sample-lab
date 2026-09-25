# templates（.claude/skills/md-to-pdf/assets/templates）

論文・レジュメの雛形です。**新しい学会テンプレートを足すときは、ここにフォルダを1つ作るだけ**で済みます。他のファイルを書き換える必要はありません。

## 入っているもの

| フォルダ | 用途 |
|---|---|
| `paper/` | 短い論文。まずこれをビルドして LaTeX 環境を確認する |
| `thesis/` | 学位論文。章を `chapters/` に分割、部と史料／研究文献に分けた文献一覧つき |
| `resume/` | ゼミ・会議の配布レジュメ |
| `transcript/` | 口頭発表の読み上げ原稿（Markdown からの変換専用） |
| `ipsj/` | 情報処理学会論文誌。学会配布の `.cls` `.bst` 同梱。pLaTeX で組む |

## 1つのフォルダに入る2種類のファイル

原稿を LaTeX で書くか Markdown で書くかで、使われるファイルが変わります。**どちらも同じフォルダに同居しています。**

| ファイル | いつ使われるか |
|---|---|
| `main.tex` ＋ `.latexmkrc`（＋ `chapters/`） | **LaTeX で書くとき。** フォルダごと `work/publications/<名前>/` にコピーして、`main.tex` を直接編集する |
| `layout.tex` | **Markdown で書くとき。** `/md-to-pdf <パス> --layout <フォルダ名>` が本文を流し込む型枠。コピーしない |

どちらか一方だけでも構いません。`transcript/` は `layout.tex` だけを持ちます（読み上げ原稿を LaTeX で直接書くことはまずないため）。

## 新しいテンプレートの足し方

`jsai/`（人工知能学会）を例にすると、`.claude/skills/md-to-pdf/assets/templates/jsai/` を作り、必要な方を置きます。

**Markdown から出したい場合** — `jsai/layout.tex` を作ります。既存の `paper/layout.tex` をコピーして直すのが早いです。

```tex
%%! fontsize     = 10pt
%%! classopts    = a4paper,fontsize=__FONTSIZE__,line_length=44zw,number_of_lines=45
%%! titleblock   = title-only   % resume / title-only / center-meta
%%! bibliography = list         % list（末尾に一覧）/ suppress（脚注のみ）
%%! toplevel     = default      % default（見出し1→節）/ chapter（→章）

\documentclass[__CLASSOPTS__]{jlreq}
__COMMON__

\begin{document}
__TITLEBLOCK__
__BODY__

\end{document}
```

`__COMMON__` `__TITLEBLOCK__` `__BODY__` は変換時に差し替わる目印です。消さないでください。`__COMMON__` には `assets/md-common.tex` が入ります。

置いた時点で `/md-to-pdf 原稿.md --layout jsai` が使えます。`/md-to-pdf` に一覧を教える設定はありません（このフォルダを毎回見に行きます）。

**LaTeX で直接書きたい場合** — `jsai/main.tex` と `jsai/.latexmkrc` を置きます。`paper/` をコピーして中身を差し替えるのが早いです。パスは書かないでください（`\input{preamble-ja}` のように名前だけ）。`.latexmkrc` がリポジトリルートを探して検索パスを通します。

**学会指定のクラスファイル**（`ipsj.cls` など）がある場合は、`.cls` `.sty` `.bst` をまとめて同じフォルダに置きます。`/md-to-pdf` はビルド時にこのフォルダを `TEXINPUTS` / `BSTINPUTS` に加えるので、コピーや登録は不要です。

### 学会クラスは pLaTeX 専用のことが多い

日本の学会が配布するクラスファイルは pLaTeX 前提で、既定の LuaLaTeX では組めません（`ipsj.cls` は `JT1` エンコーディングが解決できず失敗します）。その場合は `layout.tex` で3つ宣言を足します。

```tex
%%! engine    = platex                  % 既定は lualatex
%%! common    = md-common-platex.tex    % LuaLaTeX 用の md-common.tex は使えない
%%! citations = natbib                  % 学会の .bst（BibTeX）に合わせる。既定は citeproc
```

`engine = platex` にすると、ビルドが `platex → dvipdfmx` になり、書誌も日本語対応の `pbibtex` で処理されます。実例は `ipsj/layout.tex` を見てください。

### 投稿用の最終原稿は main.tex で

`layout.tex` 経由（Markdown）では、巻号・受付日・英文タイトル・英文要旨といった投稿時固有の項目を渡せません。**体裁の下見は `/md-to-pdf --layout <学会名>`、投稿用の仕上げは `main.tex` をコピー**、と使い分けてください。

## 注意

- 雛形は**その場でビルドしないでください**。このスキルの中に出力が散らかります。まず `work/publications/<名前>/` へコピーしてください（コピー先の深さは問いません）
- 書誌は `bibliography/references.bib` の1本を共有します。雛形ごとに `.bib` は持ちません
- 学会の制約が体裁以外（提出物の構成、`.bbl` の同梱など）にも及ぶ場合は、テンプレートに加えて `build-<学会名>` のスキルを作ることを検討してください
