# lab

複数の work で共通して使うもののうち、**自分が開いて使うもの**を置きます。

## 置き場所

- `assets/figures/` : スライドや論文で使い回す図
- `logs/` : daily-start / daily-end の日次ログ

## lab とスキルの使い分け

- **`lab/`** は自分が開くもの
- **`.claude/skills/`** はエージェントへの手順書。そのスキルしか読まない雛形・スクリプト・テーマも中に入っている

Marp のテーマと雛形は `.claude/skills/build-slide/assets/`、LaTeX の雛形とプリアンブルは
`.claude/skills/md-to-pdf/assets/` にあります。**コピーして使う雛形もそこです**（パスは各 README に書いてあります）。

書誌データ `bibliography/references.bib` と引用スタイル `bibliography/*.csl` は**研究資産なので、スキルに入れません。**
スキルは入れ替えても、書誌は残るようにしてあります。

## 運用の考え方

- 特定の work だけで使うものは、その `work/<名前>/` に置く
- どの work でも使うものだけを `lab/` に集める

## 共通ツールを複数のリポジトリで使い回したくなったら

スキルをこのリポジトリの外に出せます。`~/.agents/skills/` に置いて、

```bash
claude --plugin-dir "$HOME/.agents"
```

で起動すると、Claude Code はコピーも symlink もなしに同じ実体を読みます。
Codex・Gemini CLI・GitHub Copilot も `~/.agents/skills/` を共通の置き場として使えます。

**このリポジトリの中にスキルを置いているのは、最初の練習を1つのフォルダで完結させるためです。**
使い回す段階になったら外に出してください。
