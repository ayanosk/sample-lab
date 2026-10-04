---
name: git
description: gitのコミット・プッシュ・プルリク作成を --commit / --push / --pr のオプションで範囲指定して実行する。必ずブランチを切り、mainへ直接コミットしない。
argument-hint: [--commit] [--push] [--pr] [--cp] [--cpp] [--all] [--main] [path... または補足メッセージ]
allowed-tools: Bash, Read, Grep
---

# /git — コミット・プッシュ・プルリク

## いつ使うか

- **AI が書き換えた内容を GitHub に送るとき**に使う
- ブランチを切って Pull Request まで作るので、**自分が見ていない変更が main に直接入らない**
- 自分の手で直しただけなら、GitHub Desktop で main のまま commit してよい

付けたオプションの範囲**だけ**を実行する。運用規約（厳守）は末尾。

**引数:** $ARGUMENTS

---

## 0. オプション解釈

トークンを解釈して実行ステージを決める。実行順は commit → push → pr。

| フラグ | ステージ |
|---|---|
| `--commit` | ブランチ確保＋ステージ＋コミット |
| `--push` | 現在ブランチを origin へ push（`-u`） |
| `--pr` | main 向け PR 作成 |
| `--all` | ステージ対象を「追跡済みの全変更」に拡大（既定は作業に関係するファイルのみ） |
| `--main` | ブランチを切らず **main で直接作業**する明示的オプトアウト（既定はブランチ。§2・§3・§6 参照） |

**複合フラグ（短縮）**

| フラグ | 展開 |
|---|---|
| `--cp` | `--commit --push`（コミット＋プッシュ） |
| `--cpp` | `--commit --push --pr`（コミット＋プッシュ＋PRまで） |

複合フラグは単独フラグと等価に展開する。`--all` 等と併用可（例 `--cpp --all`）。

- フラグ併記でパイプライン（`--commit --push --pr` なら3つを順に）。
- **依存の自動補完**：`--pr` 指定時にブランチが未 push なら push を挟む。`--push`／`--pr` の前に未コミットの対象が残っていれば、先に commit するか 利用者に確認する。
- フラグが1つも無ければ、`git status` と本スキルの使い方を示して**停止**（誤爆防止）。
- フラグ以外のトークンは、既存パスと解釈できれば staging 対象、そうでなければコミットメッセージの補足とみなす。

## 1. 事前チェック（毎回）

```bash
git rev-parse --abbrev-ref HEAD    # 現在ブランチ
git status --short                 # 変更一覧
git remote -v | head -1            # origin
git fetch origin --prune --quiet   # リモートの削除済みブランチを反映
```

現在ブランチが `main`（既定ブランチ）なら、**絶対に main へコミットしない**。§2 でブランチを切る。

### 1-1. 現在ブランチのPRが既にマージ済みでないか（重要）

```bash
command -v gh >/dev/null && gh pr list --head "$(git branch --show-current)" --state merged --json number,url   --jq '.[] | "マージ済みPR: #\(.number) \(.url)"'
```

**マージ済みのPRがあるブランチで作業を続けると、以後のコミットが宙に浮く。** そのブランチは役目を終えているので、
`main` を更新してから新しいブランチを切るのが正しい。

- **`--commit` の前にこれを検出したら、作業を止めて 利用者に伝える。** 「このブランチのPRは既にマージ済みです。新しいブランチを切りますか」と確認し、
  了承が得られたら `git switch main && git pull --ff-only && git switch -c <新ブランチ>` を実行してからコミットする
- 既にコミット済みで push/PR だけを行う場合は、**新しいPRが必要**である旨を報告に含める（既存PRは再利用できない）

### 1-2. マージ済みローカルブランチの掃除

```bash
git switch main --quiet 2>/dev/null && git pull --ff-only --quiet 2>/dev/null   # 可能なら先に更新
git branch --merged main | grep -vE '^\*|^\s*main$|^\s*backup/'
```

**列挙されたものは `git branch -d` で削除してよい**（`-d` は未マージなら削除を拒むため安全弁になる）。削除したブランチ名は報告に含める。

- **`-D`（強制削除）は使わない。** `-d` が拒んだブランチは、マージ済みに見えても未取込のコミットを持つ。その場合は削除せず、
  `git log main..<ブランチ>` の結果とともに 利用者に報告する
- **`backup/` で始まるブランチと `main` は対象外**（意図的な保全ブランチのため）
- squash merge / rebase merge を使うリポジトリでは `--merged` が効かない。その場合は無理に消さず、
  §1-1 のPR状態で判断する

この掃除は**現在ブランチが `main` のときだけ**行う。feature ブランチ上での作業中に他ブランチを消すと混乱するため。

## 2. `--commit`

1. **ブランチ確保**：`main` 上なら feature ブランチを切る。名前は変更内容から `種別/簡潔な説明`（種別＝feat/fix/docs/chore/refactor 等、kebab-case）。迷えば候補を提示。既に feature ブランチ上ならそのまま使う。
   ```bash
   git switch -c <種別>/<説明>
   ```
   - **`--main` 指定時のみ例外**：ブランチを切らず現在の main のままコミットする。この明示的オプトアウトがある場合に限り「main 直コミット禁止」を解除する。フラグが無ければ従来どおり必ずブランチを切る。
2. **ステージ範囲を確定**：既定は「今回の作業に関係するファイルのみ」。$ARGUMENTS にパスがあればそれ、`--all` なら全変更。**何をステージするか一覧を出してから** add する。作業無関係の変更を巻き込まない。
   ```bash
   git add <対象パス...>
   git diff --cached --stat
   ```
3. **コミット**：件名＋本文を日本語で「何を・なぜ」。AI が書いたコミットであることが分かるよう、末尾に `Co-Authored-By:` のトレーラを付す。ダッシュ挿入は避ける。

## 3. `--push`

```bash
git push -u origin <現在ブランチ>
```

**main へは push しない**（feature ブランチのみ）。push 応答に出る PR 作成用URLを控える。

- **`--main` 指定時**：main への push は取り消しにくいので、**push 直前に一度 利用者に確認**してから `git push origin main` する。確認なしに main へ push しない。

## 4. `--pr`

- **`--main` と併用された場合は PR を作らない**（main→main は成立しない）。その旨を報告し、commit＋push のみで終える。
1. ブランチが push 済みか確認。未なら §3 を実行。
2. `gh` があれば作成（PR本文の末尾に生成クレジットとセッションURLを付す）：
   ```bash
   command -v gh >/dev/null && gh pr create --base main --head <ブランチ> \
     --title "<件名>" --body "<本文>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)"
   ```
3. **`gh` が無い／未認証なら**（この環境の既定）：作成を強行せず、push が返した比較URL（`https://github.com/<owner>/<repo>/pull/new/<ブランチ>`）と、貼り付け用のタイトル・本文を提示して 利用者に委ねる。黙って諦めない。導入したい場合は `! brew install gh` → `! gh auth login` を案内。

## 5. 報告

実施ステージ・ブランチ名・コミットSHA・push結果・PR URL（または比較URL）を日本語で報告。未実施ステージや保留（gh未導入等）も明示する。ツール実行だけで終えない。

---

## 運用規約（厳守）

- **既定では main へ直接コミット・push しない。必ず feature ブランチ。** 例外は `--main` の明示指定時のみで、その場合も main への push は事前確認する。
- push・PR は外向き操作。フラグ（`--push`／`--pr`）が明示の許可。指示外の一括処理はしない。
- ステージは作業関連ファイルに限定。`--all` のときのみ全変更（対象一覧を提示）。
- 破壊的操作（`push --force`、`reset --hard` 等）は本スキルの対象外。要求時は個別に確認する。
- ブランチ削除は `-d` のみ。`-D`（強制）は使わない。`backup/` と `main` は掃除の対象外。
