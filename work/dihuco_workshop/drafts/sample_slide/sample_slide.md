---
marp: true
theme: academic-ja
paginate: true
footer: "[氏名] · [所属] · [学会名] [年]"
lang: ja
---

<!-- _class: title -->
<!-- _paginate: skip -->
<!-- _footer: "" -->

# ワークショップ用サンプルスライド

## 自由に編集してみましょう

[氏名]（[所属]）

[学会名] | [日付] | [会場]

---

<!-- _class: outline -->

# 編集の流れ

1. 本文を編集してみましょう<span class="outline-desc">マークダウン記法を確認しましょう</span>
2. 図表を挿入してみましょう<span class="outline-desc">コピペできる記法リストを使い、画像つきのスライドを作成しましょう</span>
3. スキルを使ったビルドを試しましょう<span class="outline-desc">/build-slideを使って、publications/にPDF/PPTXファイルをエクスポートしましょう</span>

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">第1部</p>

# 本文を編集してみましょう

マークダウン記法を確認しましょう

---

# 本文の編集方法

`sample-lab/.claude/skills/build-slide/assets/templates`内のmdファイルには、基本的な記法のサンプルが並んでいます。それらを参考にしつつ、このスライドを自由に編集してみましょう。

テーマは **「AIによって自らの研究環境はいかに変わりうるか」** とします。

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">第2部</p>

# 図表を挿入してみましょう

コピペできる記法リストを使い、画像つきのスライドを作成しましょう

---

# 図表の記法

`sample-lab/.claude/skills/build-slide/assets/templates`内のmdファイルには、基本的な記法のサンプルが並んでいます。それらを使って、図とテキストからなるスライドを作成して下さい。

オリジナルの画像を作成し、挿入することも歓迎します。

---

<!-- _class: section-divider -->
<!-- _paginate: skip -->

<p class="progress">第3部</p>

# スキルを使ったビルドを試しましょう

`/build-slide`を使って、`publications/`にPDF/PPTXファイルをエクスポートしましょう

---

# スライドを出力する方法

スライドの出力には、`/build-slide`スキルを使用します。Claude Codeの場合はコマンドを入力して下さい。その他を使用している場合には、`sample-lab/dotclaude/skills/build-slide/SKILL.md`を参考パスとして支持すれば同様の処理ができます。