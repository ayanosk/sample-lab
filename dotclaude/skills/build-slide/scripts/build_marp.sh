#!/usr/bin/env bash

set -euo pipefail

# --- Python 実行体の解決 ---
# Windows の python.org 版は python.exe しか作らず、python3 が無い。
# python3 → python の順に探し、見つかったほうを $PY として使う。
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  PY=""
fi

usage() {
  cat <<'EOF'
Usage: build_marp.sh --pdf|--pptx <markdown-file>

どのディレクトリから実行してもよい。
  <markdown-file> は「呼び出し元のカレントディレクトリ基準」で解決し、
  見つからなければリポジトリルート基準でも探す。

Optional env vars:
  MARP_BROWSER          Browser kind for Marp (chrome|edge|firefox)
  MARP_BROWSER_PATH     Explicit browser executable path
  MARP_BIN              marp 実行体を明示指定する（未指定なら自動解決）
  MARP_CLI_VERSION      npx フォールバック時に使う marp-cli のバージョン
  MARP_SKIP_SVG_CHECK   1 にするとSVG図の文字サイズ検査を飛ばす
EOF
}

if [[ $# -ne 2 ]]; then
  usage >&2
  exit 1
fi

format="$1"
target_file="$2"

case "$format" in
  --pdf|--pptx)
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# リポジトリルート（AGENTS.md のあるフォルダ）を上へ辿って探す。
# 「../..」のように階層数を決め打ちすると、スキルを置き直したときに壊れる。
repo_root="$script_dir"
while [[ "$repo_root" != "/" && ! -e "$repo_root/AGENTS.md" ]]; do
  repo_root="$(dirname "$repo_root")"
done
if [[ "$repo_root" == "/" ]]; then
  repo_root="$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

# --- 入力パスの解決は cd する前に行う ---
# Marp の themeSet（.marprc.yml）はリポジトリルート基準なので、後で cd "$repo_root" する。
# その cd で相対パスの意味が変わってしまうため、引数はここで絶対パスに直しておく。
# これにより、どのディレクトリから呼び出しても同じように動く。
invocation_dir="$PWD"

to_abs() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *)  printf '%s\n' "${2%/}/$1" ;;
  esac
}

# 呼び出し元のカレントディレクトリ基準 → リポジトリルート基準 の順に探す
resolved_target="$(to_abs "$target_file" "$invocation_dir")"
if [[ ! -f "$resolved_target" ]]; then
  fallback_target="$(to_abs "$target_file" "$repo_root")"
  if [[ -f "$fallback_target" ]]; then
    resolved_target="$fallback_target"
  else
    echo "Target file not found: $target_file" >&2
    echo "  試したパス:" >&2
    echo "    $(to_abs "$target_file" "$invocation_dir")" >&2
    [[ "$fallback_target" != "$(to_abs "$target_file" "$invocation_dir")" ]] \
      && echo "    $fallback_target" >&2
    exit 1
  fi
fi
target_file="$resolved_target"

cd "$repo_root"

# --- 前処理: HTMLタグ内のバッククォートを <code> タグに変換 ---
# Marp はHTMLブロック内のMarkdown記法を処理しないため、
# `text` → <code>text</code> に変換した一時ファイルを生成する。
# 山括弧もエスケープ: <tag> → &lt;tag&gt;
# Python が無い環境ではこの前処理だけ飛ばす（ビルド自体は通る）。
preprocess_md() {
  if [[ -z "$PY" ]]; then
    cat
    return 0
  fi
  "$PY" -c "
import re, sys

text = sys.stdin.read()
# HTMLタグ内（<div ...> ~ </div>）のバッククォートを変換
def convert_backticks(m):
    content = m.group(0)
    def replace_inline(bm):
        inner = bm.group(1)
        escaped = inner.replace('<', '&lt;').replace('>', '&gt;')
        return '<code>' + escaped + '</code>'
    return re.sub(r'\x60([^\x60]+)\x60', replace_inline, content)

# HTMLブロック（<div で始まり </div> で終わる範囲）を検出
result = re.sub(r'<div[^>]*>.*?</div>', convert_backticks, text, flags=re.DOTALL)
sys.stdout.write(result)
"
}

# 一時ファイルは原稿mdと同じディレクトリに作る（md内の相対画像パスを解決させるため）。
# mktemp は「テンプレート末尾」のXしか置換しないので、拡張子は後から付け直す。
# （`.tmp.XXXXXX.md` と書くと置換されず固定名になり、並行ビルドで衝突する）
tmp_base="$(mktemp "${target_file%.md}.tmp.XXXXXX")"
tmp_file="${tmp_base}.md"
trap 'rm -f "$tmp_base" "$tmp_file"' EXIT
mv "$tmp_base" "$tmp_file"

preprocess_md < "$target_file" > "$tmp_file"

# ── SVG図の文字サイズ検査 ──────────────────────────────────────
# SVGの font-size は viewBox のユーザ単位なので、図がスライドの枠に
# 合わせて縮むと実際の見え方も小さくなる。ここで気づかないと、刷ってから
# 「図の字が小さい」と指摘される。ビルドは止めず警告にとどめる。
# MARP_SKIP_SVG_CHECK=1 で黙らせられる。
if [[ -z "${MARP_SKIP_SVG_CHECK:-}" && -f "${script_dir}/check_svg_text.py" ]] \
   && [[ -n "$PY" ]]; then
  if ! "$PY" "${script_dir}/check_svg_text.py" --quiet "$target_file" >&2; then
    cat >&2 <<'SVGWARN'
[WARN] 図の中の文字が小さすぎます。上の指示どおり font-size を上げてください。
       一括で直す: python3 .claude/skills/build-slide/scripts/check_svg_text.py --fix <このmd>
       （拡大後は枠からのはみ出しを目視で確認すること）
       この検査を飛ばす: MARP_SKIP_SVG_CHECK=1
SVGWARN
  fi
fi

detect_browser_kind() {
  local browser_path="$1"
  case "$browser_path" in
    *"Microsoft Edge"*|*msedge*)
      echo "edge"
      ;;
    *firefox*|*"Firefox"*)
      echo "firefox"
      ;;
    *)
      echo "chrome"
      ;;
  esac
}

resolve_browser_path() {
  if [[ -n "${MARP_BROWSER_PATH:-}" ]]; then
    printf '%s\n' "$MARP_BROWSER_PATH"
    return 0
  fi

  local candidates=(
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  if command -v firefox >/dev/null 2>&1; then
    command -v firefox
    return 0
  fi

  return 1
}

browser_args=()
if browser_path="$(resolve_browser_path)"; then
  browser_kind="${MARP_BROWSER:-$(detect_browser_kind "$browser_path")}"
  browser_args=(--browser "$browser_kind" --browser-path "$browser_path")
fi

# 出力ファイル名は元のファイルに合わせる（原稿mdと同じディレクトリに出る）
case "$format" in
  --pdf)  out_file="${target_file%.md}.pdf" ;;
  --pptx) out_file="${target_file%.md}.pptx" ;;
esac

# 完成版の収集先。原稿が work/<プロジェクト>/drafts/<名前>/ の下にあるなら、
# 同じ名前の publications/<名前>/ へ完成版だけをコピーする。
# 手でコピーすると忘れるので、ビルドの一部として行う。
src_dir="$(cd "$(dirname "$target_file")" && pwd)"
collect_dir=""
case "$src_dir/" in
  "${repo_root}"/work/*/drafts/*)
    rel="${src_dir}/"
    rel="${rel##*/drafts/}"
    collect_dir="${repo_root}/publications/${rel%/}"
    ;;
esac

# --- marp 実行体の解決 ---
# インストール方法（グローバル / ローカル / npx）に依存しないよう多段で探す。
# 見つかった順に採用する:
#   1. MARP_BIN（明示指定）
#   2. PATH 上の marp
#   3. 既知のインストール先（npm global prefix, ~/.npm-global, リポジトリの node_modules）
#   4. npx フォールバック
marp_launcher=()
resolve_marp_launcher() {
  local candidate

  if [[ -n "${MARP_BIN:-}" ]]; then
    if [[ -x "$MARP_BIN" ]]; then
      marp_launcher=("$MARP_BIN")
      return 0
    fi
    if candidate="$(command -v "$MARP_BIN" 2>/dev/null)"; then
      marp_launcher=("$candidate")
      return 0
    fi
    echo "[WARN] MARP_BIN を実行できません。他の候補を探します: $MARP_BIN" >&2
  fi

  if candidate="$(command -v marp 2>/dev/null)"; then
    marp_launcher=("$candidate")
    return 0
  fi

  local npm_prefix=""
  if command -v npm >/dev/null 2>&1; then
    npm_prefix="$(npm config get prefix 2>/dev/null)" || npm_prefix=""
  fi

  local fallbacks=(
    "$HOME/.npm-global/bin/marp"
    "$repo_root/node_modules/.bin/marp"
  )
  [[ -n "$npm_prefix" && "$npm_prefix" != "undefined" ]] \
    && fallbacks=("$npm_prefix/bin/marp" "${fallbacks[@]}")

  for candidate in "${fallbacks[@]}"; do
    if [[ -x "$candidate" ]]; then
      marp_launcher=("$candidate")
      return 0
    fi
  done

  # npx フォールバック。バージョンを固定しておくと npx のキャッシュに当たり、
  # レジストリ参照なし（＝オフラインでも）即座に起動する。
  if command -v npx >/dev/null 2>&1; then
    echo "[INFO] marp コマンドが見つからないため npx で実行します。" >&2
    echo "       常用するなら 'npm i -g @marp-team/marp-cli' を推奨します。" >&2
    marp_launcher=(npx --yes "@marp-team/marp-cli@${MARP_CLI_VERSION:-4.3.1}")
    return 0
  fi

  return 1
}

if ! resolve_marp_launcher; then
  cat >&2 <<'EOF'

marp コマンドが見つかりません。
- インストール: npm i -g @marp-team/marp-cli
- すでに入っている場合は MARP_BIN に実行体のパスを指定してください。
    例: MARP_BIN=/path/to/marp .claude/skills/build-slide/scripts/build_marp.sh --pdf slide.md
- Node.js（npm / npx）自体が入っていない可能性もあります。
EOF
  exit 1
fi

marp_cmd=(
  "${marp_launcher[@]}"
  --allow-local-files
  --no-stdin
  "${browser_args[@]}"
  "$format"
  -o "$out_file"
  "$tmp_file"
)

if ! "${marp_cmd[@]}"; then
  cat >&2 <<'EOF'

Marpのビルドに失敗しました。
- 図が出ないのではなく、変換そのものが失敗しています。
- ブラウザ起動の失敗が最も多い原因です。build_marp.sh は Chrome / Edge / Firefox を自動解決しますが、
  サンドボックス環境がヘッドレスブラウザの起動を禁止していることがあります。
- その場合は権限付きで再実行するか、ローカル端末で同じコマンドを実行してください。
- MARP_BROWSER_PATH でブラウザを明示指定することもできます。
EOF
  exit 1
fi

echo "OK: $out_file"

# 完成版を publications/<名前>/ へ集める
if [[ -n "$collect_dir" ]]; then
  mkdir -p "$collect_dir"
  cp "$out_file" "$collect_dir/"
  echo "収集: ${collect_dir}/$(basename "$out_file")"
fi
