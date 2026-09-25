---
marp: true
theme: academic-intl
paginate: true
footer: "[Author] · [Affiliation] · [Conference], [Year]"
---

<!--
  雛形: 英語発表用（theme: academic-intl / 1280×720 / 本文32px）
  和文発表は template_academic-ja.md（theme: academic-ja / 1280×800 / 29px）

  使い方
    1. コピーして原稿を置くディレクトリへ
    2. 要らないスライドを消し、[  ] を置換する
    3. 図を入れたら  python3 .claude/skills/build-slide/scripts/check_svg_text.py <このファイル>
    4. /build-slide <パス>  で PDF・PPTX を出力

  手順と作図の基準の正本: publications/README.md の「スライド」節

  SVG図の文字サイズ（build_marp.sh が自動で検査する）
    図は枠に合わせて縮むので、SVG の font-size はそのままの px にならない。
    実効px = font-size × min(1168/viewBox幅, 460/viewBox高)
    viewBox を 1168×460 以内、最小 font-size を 20 以上にすれば倍率が
    1.0前後になり、viewBox の数字がほぼそのまま実効pxになる。

  記法は template_academic-ja.md と共通。academic-intl が持たないのは
  dense / compact と table-fit / table-tight の2系統だけで、
  いずれも意図して外してある（末尾のスライド参照）。
  判型も本文サイズも違うので、academic-ja のデッキの theme: だけを
  差し替えると全枚数がリフローする。
-->

<!-- _class: title -->
<!-- _paginate: skip -->
<!-- _footer: "" -->

# The academic-intl theme

## A sample deck of layouts and markup

[Author Name], [Affiliation]

[Conference Name], [Location] · [Date]

---

<!-- _class: outline -->

# Outline

1. Text, lists and quotations<span class="outline-desc">Emphasis, block quotes, parallel text, code</span>
2. Tables and figures<span class="outline-desc">Table density, fig-full, figure-layout</span>
3. Layout components<span class="outline-desc">Columns, cards, icon cards, icons, references, appendix</span>

<!--
  _class に outline を指定すると、番号付きリストが一覧の体裁になる。
  番号は 01 / 02 …（自動）、<span class="outline-desc"> は任意の補足行。
  いま話している章は <li class="now">、済んだ章は <li class="dim">。
-->

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">Part 1</p>

# Text, lists and quotations

---

# Basic text and lists

Body text is 32px with a line height of 1.55. **Bold** takes the accent colour (navy); *italic* is rendered in the serif face.

- Plain Markdown bullets work as they are; `inline code` sits on a pale wash
  - Nested items shrink and grey out automatically (two levels at most)
- Body paragraphs and lists are capped at 34em, not the full 1168px
- Use `<br>` for a line break inside a paragraph or a bullet

1. Ordered-list markers also take the accent colour
2. `h1` is the slide title; use `h2`/`h3` for sub-headings inside a slide

<p class="footnote">&lt;p class="footnote"&gt; is pushed to the foot of the slide</p>

---

# De-emphasis and single-point emphasis

<ul>
  <li class="dim">Items marked .dim go achromatic (images and SVG are greyscaled)</li>
  <li>Emphasise exactly one thing with <span class="signal">span class="signal"</span></li>
  <li>To drop a whole slide's body and leave only the title, use <code>_class: dim-body</code></li>
</ul>

<div class="highlight-box">

`.dim` and `.signal` are **a pair**. Emphasising everything emphasises nothing.

</div>

---

# Quotations and parallel text

> Que les Académiciens travailleront à bannir toutes les Erreurs qui se sont introduites dans les Sciences & dans les Arts.

<div class="quote-parallel">
<blockquote lang="fr">

Il sera tenu registre de tout ce qui se fera dans les assemblées.

</blockquote>
<blockquote lang="en">

A register shall be kept of everything done in the assemblies.

</blockquote>
</div>

<p class="source">[Reference, folio/page]. Translation mine.</p>

- A plain `>` quote renders in the serif face with a rule on the left
- `<div class="quote-parallel">` holds two `<blockquote>` elements: original (serif), translation (sans). Always set `lang` on both

---

<!-- _class: code-solo -->

# Code blocks

```xml
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader><fileDesc><titleStmt>
    <title>Procès-verbaux de l'Académie</title>
  </titleStmt></fileDesc></teiHeader>
  <text><body>
    <div type="séance" when="1699-02-04">
      <p>L'Académie s'est assemblée…</p>
    </div>
  </body></text>
</TEI>
```

<p class="footnote">XML/TEI is colour-coded in the manner of oXygen</p>

---

# Adjusting a code block

Marp shrinks a block until its **longest line** fits, so a long line costs you font size.

| Class | What it changes |
|:---|:---|
| `code-body` / `code-small` | Size (0.72em / 0.66em) |
| `code-solo` | A code-only slide; tightens the margins |
| `code-fill` | Full width, larger text, tighter leading |
| `code-full` / `code-wide` / `code-fit` | Width (100% / 72–96% / 96%) |
| `code-h-compact` / `code-h-tight` | Leading and inner padding |

<p class="footnote">Same names as academic-ja. Combine them: _class: code-solo code-h-tight</p>

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">Part 2</p>

# Tables and figures

---

# Tables

| Year | Event | Sponsor | Items |
|:---:|:---|:---|---:|
| 1666 | Académie founded | Colbert | <span class="num">12</span> |
| 1699 | Statutes revised | Pontchartrain | <span class="num">70</span> |
| 1716 | Regency reform | Bignon | <span class="num">1,204</span> |

- Markdown tables cannot carry cell classes, so wrap numeric cells in `<span class="num">` (right-aligned, tabular figures)
- Density: `table-relaxed` (1.55) / none (1.4) / `table-compact` (1.28). If it still does not fit, cut rows or move the table to an appendix slide

---

<!-- _class: fig-full -->

# Maximise the figure — fig-full

<p class="chart-label">How a slide deck gets made with AI (sample figure)</p>

![Figure](../../assets/figures/ai_collaboration_slidemaking_en.svg)

<!--
  fig-full の画像枠は約 1200×580。h1 と chart-label を除いた残りに
  画像を目一杯入れる。図は上寄せになる。
  差し替えるときは viewBox を 1168×460 以内、最小 font-size 20 以上に。
-->

---

# Figure above notes — figure-layout

<div class="figure-layout" style="--figure-notes-size: 0.8em; --figure-gap: 22px;">
  <div class="figure-box"><img src="../../assets/figures/ai_collaboration_slidemaking_en_compact.svg" alt=""></div>
  <ul class="figure-notes">
    <li>A plain <code>![Figure](…)</code> followed by body text <span class="signal">also displays</span>. What differs is how much you can control</li>
    <li class="dim">Plain images are capped at 560px, always centred, and the gap is left to generic margins</li>
    <li>These notes are smaller because of <code>figure-notes-size: 0.8em</code>; the gap comes from <code>figure-gap: 22px</code></li>
  </ul>
</div>

<!--
  figure-layout は表示のためではなく、図と注記の関係を数値で決めるための
  ラッパー。使える変数（いずれも接頭辞のハイフン2つを付けて style 属性に）:
    figure-height / figure-gap / figure-justify /
    figure-offset-x / figure-offset-y / figure-notes-size
  図が枠に収まっていて注記が数行なら、素で書いて構わない。
-->

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">Part 3</p>

# Layout components

---

# Columns — columns, col-1 / col-2

<div class="columns">
<div class="col-2">

### <span class="icon">description</span> Wider (col-2)

`col-1`, `col-2` and `col-3` set the ratio. This slide is 2:1; the default with plain `<div>` children is even.

| Category | Items |
|:---|---:|
| Minutes | <span class="num">342</span> |
| Letters | <span class="num">1,208</span> |

</div>
<div class="col-1">

### Narrower (col-1)

<div class="highlight-box">

**Total**
1,550

</div>

</div>
</div>

---

# Cards — cards

<div class="cards">
  <div class="card">
    <div class="card-title">Card A</div>
    <div class="card-desc">Default: a thin rule with an accent-coloured top border</div>
  </div>
  <div class="card dim">
    <div class="card-title">Card B</div>
    <div class="card-desc">Adding .dim turns the top border achromatic</div>
  </div>
  <div class="card signal">
    <div class="card-title">Card C</div>
    <div class="card-desc">Adding .signal recolours the top border and the title</div>
  </div>
</div>

- Three levels: `cards` > `card` > `card-title` / `card-desc`
- Three or four across; marking one `signal` draws the eye to it

---

# Icon cards — icon-cards

<div class="icon-cards">
  <div class="icon-card">
    <span class="icon xxl">account_balance</span>
    <div class="icon-card-title">Institution</div>
    <div class="icon-card-desc">Statutes, offices and<br>appointments</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">groups</span>
    <div class="icon-card-title">Networks</div>
    <div class="icon-card-desc">Letters, patronage and<br>joint work, mapped</div>
  </div>
  <div class="icon-card">
    <span class="icon xxl">precision_manufacturing</span>
    <div class="icon-card-title">The arts</div>
    <div class="icon-card-desc">Technical review and<br>privilege as state ties</div>
  </div>
</div>

- `icon-cards` > `icon-card` > `icon-card-title` / `icon-card-desc`
- **A separate component from `cards`**: a pale accent fill with rounded corners, for icon-led summaries such as the strands of a project
- Use `cards` when one of the three must stand out (`signal`); use `icon-cards` when the three are genuinely parallel

---

# Icons and icon-flow

<div class="icon-flow">
  <div class="icon-flow-item">
    <span class="icon xxl">search</span>
    <div>Survey<span class="sub">archives</span></div>
  </div>
  <div class="icon-flow-arrow">→</div>
  <div class="icon-flow-item">
    <span class="icon xxl">edit_note</span>
    <div>Transcribe<span class="sub">HTR + review</span></div>
  </div>
  <div class="icon-flow-arrow">→</div>
  <div class="icon-flow-item">
    <span class="icon xxl">code</span>
    <div>Encode<span class="sub">TEI/XML</span></div>
  </div>
  <div class="icon-flow-arrow">→</div>
  <div class="icon-flow-item">
    <span class="icon xxl">analytics</span>
    <div>Analyse<span class="sub">counts, networks</span></div>
  </div>
</div>

- Alternate `icon-flow-item` and `icon-flow-arrow` inside `icon-flow`; `<span class="sub">` adds a smaller grey second line
- Inline sizes: `<span class="icon">`, and `lg` / `xl` / `xxl`. Names are at [fonts.google.com/icons](https://fonts.google.com/icons)

---

# Per-slide CSS — style scoped

<style scoped>
section { background: linear-gradient(135deg, #ffffff 0%, #eef3f8 100%); }
.highlight-box { text-align: left !important; }
</style>

For an adjustment the theme does not offer, `<style scoped>` applies CSS to **this slide only**. This one carries a faint gradient, and the highlight box has lost its centring.

<div class="highlight-box">

**How:** put `<style scoped>` … `</style>` at the top of the slide. The theme itself stays untouched

</div>

- Use it for a one-off tweak to spacing, size or background
- Writing the same tweak on several slides is a sign it belongs in the theme as a class

---

<!-- _class: references -->

# References

[Author, Name. *Title*. Place: Publisher, Year.]

[Author, Name. "Title." *Journal* vol, no. (Year): pp. DOI.]

**Data / code**: [repository URL]

<!--
  _class に references を指定すると文字が小さくなり、ぶら下げインデントに
  なる。1項目 = 1段落（空行区切り）で書く。
-->

---

<!-- _class: appendix -->

# Detail held back for Q&A

Adding `_class: appendix` changes the background and prefixes the `h1` with "Appendix · " automatically.

- Somewhere to park detailed tables, robustness checks and full source texts
- The change of ground makes the boundary with the main sequence visible

---

# Two things this theme leaves out

Everything else in `academic-ja` is available here under the same markup. These two are omitted on purpose, not by oversight.

| Not defined here | Why | Do this instead |
|:---|:---|:---|
| `dense` / `compact` | A talk is projected, not handed out. Shrinking body text to fit is the wrong repair | Cut content, or split the slide in two |
| `table-fit` / `table-tight` | Both drop below what the back row can read | `table-compact`, then cut rows or move the table to an appendix |

<p class="footnote">Build with /build-slide, or bash .claude/skills/build-slide/scripts/build_marp.sh --pdf &lt;file&gt;</p>
