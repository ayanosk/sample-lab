#!/bin/bash
# Markdown → docx（コメント・変更履歴を付けてもらう用）変換
# \chapter{} \section{} / 脚注span を pandoc 記法に直したうえで、
# 和文reference.docx（明朝本文・ゴシック見出し・A4）を適用したdocxを生成する。
# 脚注はWordネイティブの脚注、[@key] は references.bib + Chicago note で脚注書誌に展開。
#
# Usage: bash md2docx.sh <md_path> [title] [--outdir DIR] [--no-open] [--number-sections]
#   md_path          : 入力Markdown（絶対パス or リポジトリルートからの相対パス）
#   title            : docxのタイトルメタデータ（省略時 \chapter{} → 最初の # → ファイル名）
#   --outdir DIR     : 出力先（既定: 入力mdと同じフォルダ）
#   --no-open        : 生成後にWord/Finderで開かない
#   --number-sections: 見出しに自動採番を付ける

set -euo pipefail

PANDOC="$(command -v pandoc || true)"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# リポジトリルート（AGENTS.md のあるフォルダ）を上へ辿って探す。
# git 管理外に展開された場合でも動くよう、git には頼りきらない。
ROOT="$SKILL_DIR"
while [[ "$ROOT" != "/" && ! -e "$ROOT/AGENTS.md" ]]; do
  ROOT="$(dirname "$ROOT")"
done
[[ "$ROOT" == "/" ]] && ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel 2>/dev/null || pwd)"
REF="${SKILL_DIR}/reference.docx"
# 書誌は Zotero（Better BibTeX）の自動エクスポート先をリポジトリで1本に固定する
BIB="${ROOT}/bibliography/references.bib"
CSL="${ROOT}/bibliography/chicago-note-bibliography.csl"
OUTDIR=""

# ---- 引数処理 ----
OPEN=true; NUMBER=false; ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-open)         OPEN=false; shift ;;
    --number-sections) NUMBER=true; shift ;;
    --outdir)          OUTDIR="$2"; shift 2 ;;
    *)                 ARGS+=("$1"); shift ;;
  esac
done
MD_FILE="${ARGS[0]:?引数にMarkdownファイルのパスを指定してください}"
TITLE_ARG="${ARGS[1]:-}"
[[ "$MD_FILE" != /* ]] && MD_FILE="${ROOT}/${MD_FILE}"
[[ -z "$OUTDIR" ]] && OUTDIR="$(cd "$(dirname "$MD_FILE")" && pwd)"
[[ "$OUTDIR" != /* ]] && OUTDIR="${ROOT}/${OUTDIR}"

# ---- 事前チェック ----
[[ -n "$PANDOC" ]] || { echo "ERROR: pandoc が見つかりません（'brew install pandoc'）。" >&2; exit 1; }
[[ -f "$MD_FILE" ]] || { echo "ERROR: 入力ファイルが見つかりません: $MD_FILE" >&2; exit 1; }
[[ -f "$REF" ]] || { echo "INFO: reference.docx を生成します..." >&2; python3 "${SKILL_DIR}/make_reference.py" "$REF"; }

BASE="$(basename "${MD_FILE%.md}")"
OUT="${OUTDIR}/${BASE}.docx"
MD_DIR="$(dirname "$MD_FILE")"
mkdir -p "$OUTDIR"
TMP="$(mktemp -t md2docx.XXXXXX.md)"
trap 'rm -f "$TMP"' EXIT

# タイトル: 引数 → \chapter{} → 最初の # 見出し → ファイル名
TITLE="$TITLE_ARG"
[[ -z "$TITLE" ]] && TITLE="$(grep -oE '\\chapter\{[^}]*\}' "$MD_FILE" | head -1 | sed -E 's/\\chapter\{(.*)\}/\1/' || true)"
[[ -z "$TITLE" ]] && TITLE="$(grep -oE '^# .+' "$MD_FILE" | head -1 | sed -E 's/^# //' || true)"
[[ -z "$TITLE" ]] && TITLE="$BASE"

# 前処理: \chapter{X}→# X / \section{X}→## X / 旧<sup><span>脚注→^[ ]（md-to-htmlと同一）
perl -0777 -pe '
  s/\\chapter\{([^}]*)\}/# $1/g;
  s/\\section\{([^}]*)\}/## $1/g;
  s{<sup>\d+</sup>\s*<span class="footnote">(.*?)</span>}{^[$1]}gs;
' "$MD_FILE" > "$TMP"

# citeproc（references.bib + note CSL があれば [@key] を脚注書誌に展開）
CITE=()
if [[ -f "$BIB" ]]; then
  CITE+=(--citeproc --bibliography="$BIB"
         --metadata link-citations=true --metadata suppress-bibliography=true)
  [[ -f "$CSL" ]] && CITE+=(--csl="$CSL")
fi
NUM=()
[[ "$NUMBER" == true ]] && NUM+=(--number-sections)

"$PANDOC" "$TMP" \
  --from=markdown --to=docx \
  --reference-doc="$REF" \
  --metadata title="$TITLE" \
  ${CITE[@]+"${CITE[@]}"} \
  ${NUM[@]+"${NUM[@]}"} \
  --resource-path="${MD_DIR}:${MD_DIR}/.." \
  --output="$OUT"

# 脚注数を報告（Wordネイティブ脚注として入っているかの確認）
FN=$(unzip -p "$OUT" word/footnotes.xml 2>/dev/null | grep -o '<w:footnote ' | wc -l | tr -d ' ')
FN=$((FN > 2 ? FN - 2 : 0))   # separator/continuation の2件を除く

echo "OK: $OUT ($(ls -lh "$OUT" | awk '{print $5}'))  title=\"$TITLE\"  footnotes=$FN"
[[ "$OPEN" == true ]] && open "$OUT" 2>/dev/null || true
