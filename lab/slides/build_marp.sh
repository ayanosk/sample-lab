#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build_marp.sh --pdf|--pptx <markdown-file>

Optional env vars:
  MARP_BROWSER       Browser kind for Marp (chrome|edge|firefox)
  MARP_BROWSER_PATH  Explicit browser executable path
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
repo_root="$(cd "${script_dir}/../.." && pwd)"

cd "$repo_root"

if [[ ! -f "$target_file" ]]; then
  echo "Target file not found: $target_file" >&2
  exit 1
fi

# --- 前処理: HTMLタグ内のバッククォートを <code> タグに変換 ---
# Marp はHTMLブロック内のMarkdown記法を処理しないため、
# `text` → <code>text</code> に変換した一時ファイルを生成する。
# 山括弧もエスケープ: <tag> → &lt;tag&gt;
preprocess_md() {
  python3 -c "
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

tmp_file="$(mktemp "${target_file%.md}.tmp.XXXXXX.md")"
trap 'rm -f "$tmp_file"' EXIT

preprocess_md < "$target_file" > "$tmp_file"

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

# 出力ファイル名は元のファイルに合わせる
case "$format" in
  --pdf)  out_file="${target_file%.md}.pdf" ;;
  --pptx) out_file="${target_file%.md}.pptx" ;;
esac

marp_cmd=(
  "$HOME/.npm-global/bin/marp"
  --allow-local-files
  --no-stdin
  "${browser_args[@]}"
  "$format"
  -o "$out_file"
  "$tmp_file"
)

if ! "${marp_cmd[@]}"; then
  cat >&2 <<'EOF'

Marpのブラウザ起動に失敗しました。
- build_marp.sh は Chrome / Edge / Firefox を自動解決するようにしています。
- それでも失敗する場合は、Codexなどのサンドボックス環境がヘッドレスブラウザ起動を禁止している可能性があります。
- その場合は権限付きで再実行するか、ローカル端末で同じコマンドを実行してください。
EOF
  exit 1
fi
