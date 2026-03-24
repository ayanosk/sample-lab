---
marp: true
theme: academic-sample
paginate: true
footer: "Academic Theme サンプルスライド"
---

<!-- _class: title -->
<!-- _paginate: skip -->
<!-- _footer: "" -->

# Academic Theme
## Marpカスタムテーマの使用感を確認するサンプル

○○研究室
2026年3月

---

# このスライドについて

`academic-sample-theme.css` の主要コンポーネントを**実際の見た目で確認する**ためのサンプル集です。

<div class="icon-cards">
  <div class="icon-card">
    <span class="icon xxl">palette</span>
    <div class="icon-card-title">デザイン</div>
    <div class="icon-card-desc">深緑×テラコッタの<br>アカデミックトーン</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">format_list_bulleted</span>
    <div class="icon-card-title">レイアウト</div>
    <div class="icon-card-desc">カラム・カード・<br>フロー図など多数</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">tune</span>
    <div class="icon-card-title">調整クラス</div>
    <div class="icon-card-desc">dense / compact /<br>table系で密度を制御</div>
  </div>
</div>

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

# Part 1
## テキスト・リスト・引用

---

# 基本テキストとリスト

通常のテキストはNoto Sans JPで表示されます。**強調テキスト**はアクセントカラー（紺）になり、*イタリック*は明朝体で描画されます。

- Markdownの箇条書きがそのまま使える
- `インラインコード`は薄いグレー背景で表示
  - ネストされた項目は自動的に小さく・グレーに
  - 2段階まで推奨

1. 番号付きリストのマーカーにもアクセントカラーが適用
2. フォントサイズ29px・行間1.7が基本の組版

<div class="footnote">フッター右寄せの脚注は <code>&lt;div class="footnote"&gt;</code> で作れます</div>

---

# 引用ブロック — 史料引用を意識したデザイン

テーマの引用ブロックは**明朝体・ゴールドの左線**で表示されます。

> Que les Académiciens travailleront à bannir toutes les Erreurs qui se sont introduites dans les Sciences & dans les Arts, & rapporteront leurs Observations par écrit.

引用の前後に通常テキストを置くと、視覚的にセパレートされます。

> すべてのアカデミー会員は、諸学問・諸技芸に紛れ込んだ誤謬を排除するために努め、みずからの観察を文書で報告するものとする。

<div class="source">Règlement de 1699, art. I</div>

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

# Part 2
## テーブルとコード

---

# テーブル — ヘッダ色とストライプ

| 年代 | 出来事 | 主導者 | 備考 |
|:---:|:---|:---|:---|
| 1666 | 科学アカデミー設立 | コルベール | 非公式な集まりから制度化 |
| 1699 | 規約改定 | ポンシャルトラン | 組織の公式化・再編成 |
| 1716 | 摂政期の改革 | ビニョン | 地方アカデミーとの連携 |
| 1793 | アカデミー廃止 | 国民公会 | 革命期の制度改革 |

- テーブルが収まらないときは `<!-- _class: table-compact -->` や `table-tight` で段階的に詰められる

---

<!-- _class: code-solo -->

# コードブロック — XMLの例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Procès-verbaux de l'Académie royale des sciences</title>
        <editor>○○研究室</editor>
      </titleStmt>
    </fileDesc>
  </teiHeader>
  <text>
    <body>
      <div type="séance" when="1699-02-04">
        <p>L'Académie s'est assemblée…</p>
      </div>
    </body>
  </text>
</TEI>
```

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

# Part 3
## レイアウトコンポーネント

---

# 2カラムレイアウト

<div class="columns">
<div>

### <span class="icon">description</span> 一次史料

- 議事録（procès-verbaux）
- 書簡コレクション
- 会計帳簿
- 出版許可記録

テキストは左右均等に配分される

</div>
<div>

### <span class="icon">auto_stories</span> 二次文献

- 制度史研究
- 科学史・技術史
- 社会史・文化史
- デジタル人文学

`<div class="columns">` でラップ

</div>
</div>

---

# カラム比率の変更

<div class="columns">
<div class="col-2">

### 広い方（col-2）

`col-1` と `col-2` で比率を 1:2 にできる。メインコンテンツを広く取りたいときに便利。

| 分類 | 件数 |
|:---|---:|
| 議事録 | 342 |
| 書簡 | 1,208 |
| 報告書 | 89 |

</div>
<div class="col-1">

### 狭い方（col-1）

補足情報やメモを入れる。

<div class="highlight-box">

**合計**
1,639件

</div>

</div>
</div>

---

# ハイライトボックス

重要なメッセージにはゴールド系の補色ボックスが使える。

<div class="highlight-box">

**ポイント:** `<div class="highlight-box">` で囲むだけ

</div>

テーブルと組み合わせても整う。

| クラス | 用途 |
|:---|:---|
| `.highlight-box` | 強調メッセージ |
| `.footnote` | 右寄せ脚注 |
| `.source` | 出典表記（右寄せ・イタリック） |

<div class="footnote">ユーティリティクラスは CSS の末尾にまとめて定義されています</div>

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

# Part 4
## アイコンとビジュアル要素

---

# Material Symbols — 4サイズで使える

Google Material Symbolsがテーマに組み込まれています。アイコン名は[公式サイト](https://fonts.google.com/icons)で検索できます。

| サイズ | クラス | 表示 |
|:---|:---|:---|
| 通常 | `<span class="icon">search</span>` | <span class="icon">search</span> テキストと同じ |
| lg | `<span class="icon lg">school</span>` | <span class="icon lg">school</span> 1.5em |
| xl | `<span class="icon xl">account_balance</span>` | <span class="icon xl">account_balance</span> 2em |
| xxl | `<span class="icon xxl">history_edu</span>` | <span class="icon xxl">history_edu</span> 3em |

- 色はデフォルトでアクセントカラー（深緑）。`style="color: var(--color-highlight)"` でテラコッタに変更可

---

# アイコンフロー — ワークフローの可視化

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
    <div>計量分析</div>
  </div>
  <div class="icon-flow-arrow">→</div>
  <div class="icon-flow-item">
    <span class="icon xxl">menu_book</span>
    <div>論文執筆</div>
  </div>
</div>

- `<div class="icon-flow">` の中に `icon-flow-item` と `icon-flow-arrow` を並べる
- アイコンのサイズは `xxl`（3em）を推奨

---

# アイコンカード — 研究の柱を紹介

<div class="icon-cards">
  <div class="icon-card">
    <span class="icon xxl">account_balance</span>
    <div class="icon-card-title">制度分析</div>
    <div class="icon-card-desc">アカデミーの規約・組織・<br>人事制度を解明する</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">groups</span>
    <div class="icon-card-title">人的ネットワーク</div>
    <div class="icon-card-desc">会員間の書簡・推薦・<br>共同研究の関係を可視化</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">precision_manufacturing</span>
    <div class="icon-card-title">技芸と実用知</div>
    <div class="icon-card-desc">技術審査・特権付与を通じた<br>国家との関係を分析</div>
  </div>
</div>

- 3〜4枚で横並び。背景はアクセントカラーの淡色

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

# Part 5
## 密度調整と特殊スライド

---

<!-- _class: dense -->

# Dense — 行間を詰める

`<!-- _class: dense -->` を指定するとline-heightが1.45に縮まります。文字サイズは変わりません。

**使いどころ:** テキストが多く、あと少しで収まりそうなスライドに。

| クラス | font-size | line-height | 用途 |
|:---:|:---:|:---:|:---|
| （なし） | 29px | 1.7 | 通常のスライド |
| `dense` | 29px | 1.45 | やや詰め。箇条書きが多いとき |
| `compact` | 25px | 1.35 | 最大限詰め。情報量が多い概要スライド |

- `dense` と `compact` は**段階的に適用する**。まず `dense` で試し、それでも溢れたら `compact`
- テーブルにも `table-compact` / `table-tight` がある

---

<!-- _class: compact -->

# Compact — 文字サイズも縮小

`<!-- _class: compact -->` で文字サイズ25px・行間1.35。配布テンプレートの構成紹介のように、**情報をなるべく1枚に収めたい場面**で使う。

```
sample-lab/
├── CLAUDE.md / AGENTS.md      ← AIへの指示書
├── dotclaude/                 ← テンプレート配布時の設定一式
│   ├── agents/                ← エージェント定義（セットアップ後は .claude/agents/）
│   ├── skills/                ← スキル定義（セットアップ後は .claude/skills/）
│   └── settings.json.example  ← セキュリティ設定の雛形
├── dotvscode/                 ← セットアップ後は .vscode/
├── lab/
│   ├── slides/                ← Marpテーマ・ビルドスクリプト
│   └── latex/                 ← LaTeX共通プリアンブル
├── project_a/                 ← 個別プロジェクト
└── publications/              ← 完成した発表資料
```

- `code-solo` などのコード用クラスと組み合わせることも可能
- **乱用は禁物**。読みやすさとのバランスを取ること

---

# Scoped Style — スライド単位のCSS調整

<style scoped>
section { background: linear-gradient(135deg, #f8f9fb 0%, #e8f0f8 100%); }
.highlight-box { text-align: left !important; font-size: 0.9em; }
</style>

`<style scoped>` で**このスライドだけ**にCSSを適用できる。

<div class="highlight-box">

**例：** 背景にグラデーション、ハイライトボックスのテキスト配置を変更

```html
<style scoped>
section { background: linear-gradient(135deg, #f8f9fb 0%, #e8f0f8 100%); }
.highlight-box { text-align: left !important; }
</style>
```

</div>

- テーマを壊さずにスライド単位で微調整できる
- フォントサイズ・余白・背景色の変更に便利

---

<!-- _class: references -->

# テーマの主要クラス一覧

`title` — タイトルスライド。深緑のグラデーション背景＋テラコッタバー

`section-divider` — セクション区切り。タイトルと同系色で左寄せ

`dense` / `compact` — テキスト密度の段階調整

`table-compact` / `table-fit` / `table-tight` — テーブル密度の段階調整

`code-solo` / `code-fill` / `code-wide` — コードブロックの幅・余白調整

`fig-full` — 画像を最大化。タイトル＋図解だけのスライドに

`figure-top` — 図を上・説明を下に配置

`references` — 参考文献。ぶら下げインデント付き

---

# ビルド方法

PDF・PPTX の生成方法は利用環境によって使い分けます。

```bash
# Mac / Linux / Git Bash / WSL
bash lab/slides/build_marp.sh --pdf publications/sample_slide.md
bash lab/slides/build_marp.sh --pptx publications/sample_slide.md

# 直接 Marp CLI を使う場合（PowerShell を含む）
npx @marp-team/marp-cli --allow-local-files --pdf publications/sample_slide.md
npx @marp-team/marp-cli --allow-local-files --pptx publications/sample_slide.md
```

- Claude Code では `/build-slide publications/sample_slide.md` でもビルドできる
- Codex では `publications/sample_slide.md を PDF と PPTX にビルドして` と指示してもよい
- テーマCSSはセットアップ後の `.vscode/settings.json` に登録済み
- VS Codeプレビューはリロード後に反映される
