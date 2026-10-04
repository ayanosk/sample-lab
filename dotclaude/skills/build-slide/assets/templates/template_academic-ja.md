---
marp: true
theme: academic-ja
paginate: true
footer: "[氏名] · [所属] · [学会名] [年]"
lang: ja
---

<!--
  雛形: 和文発表用（theme: academic-ja / 1280×800 / 本文29px）
  英語発表は template_academic-intl.md（theme: academic-intl / 1280×720 / 32px）

  使い方
    1. コピーして原稿を置くディレクトリへ（例: publications/<event>/）
    2. 要らないスライドを消し、[  ] を置換する
    3. 図を入れたら  python3 .claude/skills/build-slide/scripts/check_svg_text.py <このファイル>
    4. /build-slide <パス>  で PDF・PPTX を出力

  手順と作図の基準の正本: publications/README.md の「スライド」節

  SVG図の文字サイズ（build_marp.sh が自動で検査する）
    図はスライド上の枠に合わせて縮むので、SVG の font-size はそのままの
    px にはならない。  実効px = font-size × min(1208/viewBox幅, 560/viewBox高)
    viewBox を 1208×560 以内、図中の最小 font-size を 18 以上にすると
    倍率が1.0前後になり、viewBox の数字がほぼそのまま実効pxになる。

  記法は template_academic-intl.md と共通。academic-ja だけが持つのは
  dense / compact と table-fit / table-tight の2系統で、intl 側は意図して
  外してある（理由は intl の雛形の末尾スライド）。
-->

<!-- _class: title -->
<!-- _paginate: skip -->
<!-- _footer: "" -->

# academic-ja テーマ

## レイアウトと記法のサンプル

[氏名]（[所属]）

[学会名] | [日付] | [会場]

---

<!-- _class: outline -->

# テーマのアウトライン

1. 本文・リスト・引用<span class="outline-desc">見出し・強調・引用・コードブロック・密度調整</span>
2. 図表<span class="outline-desc">表の密度、fig-full、figure-layout、幅のユーティリティ</span>
3. レイアウト部品<span class="outline-desc">カラム、カード、アイコンカード、アイコン、参考文献、付録</span>

<!--
  _class に outline を指定すると、番号付きリストが一覧の体裁になる。
  番号は 01 / 02 …（自動）、項目名は太字、<span class="outline-desc"> は
  任意の補足行。項目は4〜6件まで。

  章区切り（section-divider）と対応させて、聴衆が同じ地図を持てるようにする。
  いま話している章を目立たせたいときは <li class="now">、
  終わった章を落としたいときは <li class="dim"> を使う。
-->

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">第1部</p>

# 本文・リスト・引用

`<p class="progress">` は章区切りの進行度を示す

---

# 基本テキストとリスト

本文は Noto Sans JP・29px・行間1.7。**強調**はアクセントカラー（紺）、*イタリック*は<br>明朝体で描画される

- Markdown の箇条書きがそのまま使える
- `インラインコード`は薄いグレー背景
  - ネストされた項目は自動的に小さく・グレーに
  - 2段階まで推奨
- 段落や項目の途中で改行したいときは `<br>` を書く

1. 番号付きリストのマーカーにもアクセントカラーが適用される
2. 見出しは h1 が最上位。h2・h3 はスライド内の小見出しに使う

<p class="footnote">右寄せの脚注は &lt;p class="footnote"&gt;</p>

---

<!-- _class: dense -->

# 密度エスケープ — dense / compact

本文の詰め具合はスライド単位で2段階に切り替えられる。このスライドには `dense` が掛かっている。

| クラス | font-size | line-height |
|:---|:---:|:---:|
| （なし） | 29px | 1.7 |
| `dense` | 29px | 1.45 |
| `compact` | 25px | 1.35 |

- まず `dense` で試し、それでも溢れたら `compact`
- どちらも academic-ja のみ。`academic-intl` には定義されていない

---

# 脱強調と一点強調

<ul>
  <li class="dim">.dim を付けた項目は無彩色になる（画像・SVGはグレースケール化）</li>
  <li>強調したい一点だけ <span class="signal">span class="signal"</span> で色を変える</li>
  <li>スライド全体の本文を落として見出しだけ立てるなら <code>&lt;!-- _class: dim-body --&gt;</code></li>
</ul>

<div class="highlight-box">

`.dim` と `.signal` は**対で使う**と効果的

</div>

<p class="source">クラス定義は academic-ja.css 末尾のブロック</p>

---

# 史料やテキストの引用と対訳

> すべてのアカデミー会員は、諸学問・諸技芸に紛れ込んだ誤謬を排除するために努め、<br>みずからの観察を文書で報告するものとする。

<p class="source">［典拠、巻・丁数または頁］</p>

<div class="quote-parallel">
<blockquote>

Que les Académiciens travailleront à bannir toutes les Erreurs qui se sont introduites dans les Sciences & dans les Arts.

</blockquote>
<blockquote>

アカデミー会員は、諸学問・諸技芸に紛れ込んだ誤謬を排除するために努めるものとする。

</blockquote>
</div>

<p class="source">［典拠、巻・丁数または頁］</p>

- `<div class="quote-parallel">` の中に `<blockquote>` を2つ並べる
- 左（1つめ）が原文で**明朝**、右（2つめ）が訳文で**ゴシック**になる
- 欧文史料なら原文側に `lang="fr"` などを入れる
- 出典表記は `<p class="source">`（右寄せ・小さめ）

---

<!-- _class: code-full -->

# コードブロック

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Procès-verbaux de l'Académie royale des sciences</title>
      </titleStmt>
    </fileDesc>
  </teiHeader>
  <text><body>
    <div type="séance" when="1699-02-04">
      <p>L'Académie s'est assemblée…</p>
    </div>
  </body></text>
</TEI>
```

---

# コードブロックの調整

| クラス | 効き方 |
|:---|:---|
| `code-body` / `code-small` | 文字サイズ（1em / 0.94em） |
| `code-solo` | コード1つだけのスライド。上下の余白を詰める |
| `code-fill` | 幅100%・文字大きめ・行間狭め |
| `code-full` / `code-wide` / `code-fit` | 幅の指定（100% / 72–96% / 96%） |
| `code-h-compact` / `code-h-tight` | 行間と内側余白 |

- 組み合わせて書ける: `<!-- _class: code-solo code-h-tight -->`
- XML/TEI は タグと属性に色分けされる


---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">第2部</p>

# 図表

---

# テーブルの記法と密度調整

| クラス | 行間 | 用途 |
|:---|:---:|:---|
| （なし） | 1.4 | 通常 |
| `table-relaxed` | 1.55 | 行数が少なく余白があるとき |
| `table-compact` | 1.28 | やや詰める |
| `table-fit` | — | 文字も小さくする |
| `table-tight` | — | 最大限詰める |

- Markdown の表ではセルにクラスを付けられないので、数値セルは
  `<span class="num">` で包む（右揃え・等幅数字になる）
- 列の揃えは `|:---|` `|:---:|` `|---:|` で指定する
- スライド冒頭に `<!-- _class: table-compact -->` のように書くと小さめに表示
- `table-fit` `table-tight` は academic-ja のみ（academic-intl にはない）

---

<!-- _class: fig-full -->

# 図だけを最大化する — fig-full

<p class="chart-label">AI協働型のスライド作成フロー（サンプル図）。図解はsvgで作成すれば自力でも修正しやすい</p>

![図](../../../lab/assets/figures/ai_collaboration_slidemaking.svg)


---

# 図と注記を上下に置く — figure-layout

<div class="figure-layout" style="--figure-notes-size: 0.8em; --figure-gap: 24px;">
  <div class="figure-box"><img src="../../../lab/assets/figures/ai_collaboration_slidemaking_compact.svg" alt=""></div>
  <ul class="figure-notes">
    <li>素の <code>![図](…)</code> と地の文でも<span class="signal">表示はされる</span>。違うのは制御できる範囲</li>
    <li class="dim">素だと図は「高さ上限560px・中央寄せ」で固定、図と注記の間隔も汎用マージン任せ</li>
    <li>この注記は <code>--figure-notes-size: 0.8em</code>、図との間隔は <code>--figure-gap: 24px</code> を<br>指定した結果</li>
  </ul>
</div>

<!--
  素の  ![図](…) ＋ 地の文  でも表示はされる。figure-layout は表示のため
  ではなく、図と注記の関係を数値で決めるためのラッパー。

    figure-height      図の高さの上限（素は section img の 560px 固定）
    figure-gap         図と注記の間隔（素は汎用マージン任せ）
    figure-justify     図の左右寄せ（素は中央固定）
    figure-offset-x/y  図のずらし（素では不可）
    figure-notes-size  注記だけの文字サイズ（素は本文と同じ）

  いずれも接頭辞のハイフン2つを付けて style 属性に書く。
  図が枠に収まっていて注記が数行なら、素で書いて構わない。
-->
---

# 図版・幅のユーティリティ

<div class="columns">
<div>

**幅（単体要素・中央揃え）**

`w-25` `w-33` `w-50` `w-66` `w-75` `w-full`

```html
<img class="w-50" src="...">
<table class="w-66">
```

</div>
<div>

**図版レイアウト**

`fig-grid` — 史料画像を格子状に並べる
`figure-top` — 図を上・箇条書きを下（`figure-layout` の `_class` 版）
`step-flow` — 画像つきの横並びステップ

</div>
</div>

<p class="footnote">いずれも academic-intl にも同じ名前で用意してある</p>

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">第3部</p>

# レイアウト部品

---

# 2カラム — columns

<div class="columns">
<div>

### <span class="icon">description</span> 一次史料

- 議事録
- 書簡コレクション
- 会計帳簿

`<div class="columns">` の直下に `<div>` を並べる

</div>
<div>

### <span class="icon">auto_stories</span> 二次文献

- 制度史研究
- 科学史・技術史
- デジタル人文学

既定は左右均等（1:1）

</div>
</div>

---

# カラム比率 — col-1 / col-2

<div class="columns">
<div class="col-2">

### 広い方（col-2）

`col-1` `col-2` `col-3` で比率を変えられる。ここは 2:1。

| 分類 | 件数 |
|:---|---:|
| 議事録 | <span class="num">342</span> |
| 書簡 | <span class="num">1,208</span> |

</div>
<div class="col-1">

### 狭い方（col-1）

<div class="highlight-box">

**合計**
1,550件

</div>

</div>
</div>

---

# カード — cards

<div class="cards">
  <div class="card">
    <div class="card-title">カードA</div>
    <div class="card-desc">上罫がアクセントカラー（紺）の既定形</div>
  </div>
  <div class="card dim">
    <div class="card-title">カードB</div>
    <div class="card-desc">.dim を足すと上罫が無彩色になる</div>
  </div>
  <div class="card signal">
    <div class="card-title">カードC</div>
    <div class="card-desc">.signal を足すと上罫と見出しが強調色になる</div>
  </div>
</div>

- `cards` > `card` > `card-title` / `card-desc` の3層で書く
- 3〜4枚で横並び。1枚だけ `signal` にすると視線が集まる

---

# アイコンカード — icon-cards

<div class="icon-cards">
  <div class="icon-card">
    <span class="icon xxl">account_balance</span>
    <div class="icon-card-title">制度</div>
    <div class="icon-card-desc">規約・組織・人事を<br>史料から追う</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">groups</span>
    <div class="icon-card-title">人的つながり</div>
    <div class="icon-card-desc">書簡・推薦・共同研究の<br>関係を可視化する</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">precision_manufacturing</span>
    <div class="icon-card-title">技芸</div>
    <div class="icon-card-desc">技術審査と特権付与から<br>国家との関係を見る</div>
  </div>
</div>

- `icon-cards` > `icon-card` > `icon-card-title` / `icon-card-desc`
- **`cards` とは別部品**。こちらは淡い塗り＋角丸で、アイコン主体の紹介向け。研究の柱や機能の一覧に使う
- `cards` は細い罫線で、1枚だけ `signal` にして視線を誘導する型。強調が要るなら `cards`、並列に見せたいなら `icon-cards`

---

# アイコン — Material Symbols

<div class="icon-flow">
  <div class="icon-flow-item">
    <span class="icon xxl">search</span>
    <div>史料調査</div>
  </div>
  <div class="icon-flow-arrow">→</div>
  <div class="icon-flow-item">
    <span class="icon xxl">edit_note</span>
    <div>翻刻</div>
  </div>
  <div class="icon-flow-arrow">→</div>
  <div class="icon-flow-item">
    <span class="icon xxl">code</span>
    <div>TEIマークアップ</div>
  </div>
  <div class="icon-flow-arrow">→</div>
  <div class="icon-flow-item">
    <span class="icon xxl">analytics</span>
    <div>分析</div>
  </div>
</div>

| サイズ | 記法 | 表示 |
|:---|:---|:---|
| 通常 | `<span class="icon">search</span>` | <span class="icon">search</span> |
| lg | `<span class="icon lg">school</span>` | <span class="icon lg">school</span> |
| xl | `<span class="icon xl">account_balance</span>` | <span class="icon xl">account_balance</span> |
| xxl | `<span class="icon xxl">history_edu</span>` | <span class="icon xxl">history_edu</span> |

- アイコン名はGoogle Fontsの[公式サイト](https://fonts.google.com/icons)で検索できる
- 色は既定でアクセントカラー。`style="color: var(--color-highlight)"` で変更可

---

# スライド単位のCSS調整 — style scoped

<style scoped>
section { background: linear-gradient(135deg, #ffffff 0%, #eef3f8 100%); }
.highlight-box { text-align: left !important; }
</style>

テーマに無い調整は `<style scoped>` で**その1枚だけ**に効かせられる。このスライドは背景に薄いグラデーションが掛かり、ハイライトボックスの中央寄せが解除してある。

<div class="highlight-box">

**書き方:** スライドの先頭に `<style scoped>` … `</style>` を置くだけ。テーマ本体は触らない

</div>

- 余白・文字サイズ・背景色の一時的な微調整に使う
- 同じ調整を何枚も書くようなら、テーマ側にクラスとして足すべきというサイン

---

<!-- _class: references -->

# 参考文献

［著者名『書名』出版社、刊行年。］

［著者名「論文名」『雑誌名』巻号、刊行年、頁。］

［Author, Name. *Title*. Place: Publisher, Year.］

**データ / コード**: ［リポジトリURL］

<!--
  _class に references を指定すると文字が小さくなり、ぶら下げインデントに
  なる。1項目 = 1段落（空行区切り）で書く。
-->

---

<!-- _class: appendix -->

# 付録スライド

`<!-- _class: appendix -->` を付けると地色が変わり、h1 の頭に「付録 · 」が自動で入ります。

- 本編に入れると過積載になる詳細表・史料全文などの置き場
- 地色が変わるので、めくったときに本編との境が分かる
