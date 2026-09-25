#!/bin/bash
# Markdown → LaTeX PDF（レイアウト別テンプレート）変換
# jlreq + LuaLaTeX。正規化 → 前処理 → pandoc → テンプレート結合 → lualatex。
#
# レイアウトは frontmatter の `pdf:` キーまたは --layout で指定する。
# 使えるレイアウトは .claude/skills/md-to-pdf/assets/templates/<名前>/layout.tex を走査して決まるので、
# 追加するときはそのフォルダを1つ置くだけでよい（layout.tex 先頭の %%! 行が既定値）。
# LaTeX はすべてこのスキルの assets/ にある。このスクリプトはテンプレートを持たない。
#
# Usage:
#   bash md2pdf.sh <md_path> [title] [options]
# Options:
#   --layout NAME       レイアウト名（frontmatter `pdf:` より優先）
#   --author "氏名"     タイトル部に作成者を表示（既定: 空）
#   --date "YYYY-MM-DD" タイトル部に日付を表示（YYYY年M月D日 へ自動整形。既定: 空）
#   --outdir DIR        出力先（既定: 原稿の隣。work/publications/ 下なら完成版を publications/ へ収集）
#   --fontsize 9pt      本文サイズ（既定: レイアウトごとの宣言値）
#   --margin 15mm       余白（geometry を使うレイアウトのみ有効）
#   --twocolumn         本文2段組
#   --keep-h1           冒頭の # 見出しを本文に残す（既定はタイトル行として除去）
#   --no-secnum         見出しに番号を振らない（原稿の章番号と二重になる場合に使う）
#   --no-open           生成後にPDFを自動で開かない
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
# リポジトリルート（AGENTS.md のあるフォルダ）を上へ辿って探す。
# git 管理外に展開された場合でも動くよう、git には頼りきらない。
ROOT="$SKILL_DIR"
while [[ "$ROOT" != "/" && ! -e "$ROOT/AGENTS.md" ]]; do
  ROOT="$(dirname "$ROOT")"
done
[[ "$ROOT" == "/" ]] && ROOT="$(git -C "$SKILL_DIR" rev-parse --show-toplevel 2>/dev/null || pwd)"
PANDOC="$(command -v pandoc || true)"
LATEXMK="$(command -v latexmk || true)"
# 書誌は Zotero（Better BibTeX）の自動エクスポート先をリポジトリで1本に固定する
BIB="${ROOT}/bibliography/references.bib"
CSL="${ROOT}/bibliography/chicago-note-bibliography.csl"
TPL_DIR="${SKILL_DIR}/assets/templates"
COMMON="${SKILL_DIR}/assets/md-common.tex"

# --- 引数解析 ---
OPEN=true; TWOCOL=""; FONTSIZE=""; MARGIN="top=15mm,bottom=15mm,hmargin=20mm"
AUTHOR=""; DATE=""; OUTDIR=""; LAYOUT_ARG=""; KEEP_H1=0; SECNUM=true; POS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --layout)    shift; LAYOUT_ARG="${1:?--layout にレイアウト名を指定してください}" ;;
    --author)    shift; AUTHOR="${1:?--author に氏名を指定してください}" ;;
    --date)      shift; DATE="${1:?--date に日付を指定してください}" ;;
    --outdir)    shift; OUTDIR="${1:?--outdir にディレクトリを指定してください}" ;;
    --fontsize)  shift; FONTSIZE="${1:?--fontsize にサイズを指定してください}" ;;
    --margin)    shift; MARGIN="${1:?--margin に余白を指定してください}" ;;
    --twocolumn) TWOCOL=1 ;;
    --keep-h1)   KEEP_H1=1 ;;
    --no-secnum) SECNUM=false ;;
    --no-open)   OPEN=false ;;
    *)           POS+=("$1") ;;
  esac
  shift
done
MD_FILE="${POS[0]:?引数にMarkdownファイルのパスを指定してください}"
TITLE_ARG="${POS[1]:-}"
[[ "$MD_FILE" != /* ]] && MD_FILE="${ROOT}/${MD_FILE}"

# --- 書誌の差し替え: frontmatter の bib: があればそれを使う（citeproc / natbib 共通）---
FM_BIB="$(awk 'NR==1 && $0 !~ /^---[[:space:]]*$/ {exit}
               /^---[[:space:]]*$/ {f++; if (f==2) exit; next}
               f==1 && /^bib:[[:space:]]*/ {sub(/^bib:[[:space:]]*/,""); sub(/[[:space:]]+#.*$/,"")
                                            gsub(/^["'"'"']|["'"'"']$/,""); print; exit}' "$MD_FILE" 2>/dev/null || true)"
if [[ -n "$FM_BIB" ]]; then
  [[ "$FM_BIB" != /* ]] && FM_BIB="${ROOT}/${FM_BIB}"
  BIB="$FM_BIB"
fi

# --- 依存チェック ---
[[ -n "$PANDOC" ]]  || { echo "ERROR: pandoc が見つかりません（'brew install pandoc'）。" >&2; exit 1; }
[[ -n "$LATEXMK" ]] || { echo "ERROR: latexmk が見つかりません（TeX Live/LuaLaTeX が必要）。" >&2; exit 1; }
[[ -f "$MD_FILE" ]] || { echo "ERROR: 入力が見つかりません: $MD_FILE" >&2; exit 1; }
# 入力はMarkdownに限る。PDF等を渡されても止まらずに壊れた .tex を作りにいくのを防ぐ
[[ "$MD_FILE" == *.md ]] || {
  echo "ERROR: 入力はMarkdown(.md)を指定してください: $MD_FILE" >&2
  echo "       このスキルは Markdown から PDF を作ります。PDFやtexは入力になりません。" >&2
  exit 1; }

# --- 使えるレイアウト一覧（templates/*.tex から自動認識）---
list_layouts() {
  local d
  for d in "${TPL_DIR}"/*/; do
    [[ -f "${d}layout.tex" ]] && basename "$d"
  done | paste -sd' ' -
}

# --- レイアウトの決定: --layout > frontmatter `pdf:` > 先頭のレイアウト ---
LAYOUT="$LAYOUT_ARG"
if [[ -z "$LAYOUT" ]]; then
  LAYOUT="$(awk 'NR==1 && $0 !~ /^---[[:space:]]*$/ {exit}
                 /^---[[:space:]]*$/ {f++; if (f==2) exit; next}
                 f==1 && /^(template|pdf):[[:space:]]*/ {
                   key=$0; sub(/:.*$/,"",key)
                   sub(/^(template|pdf):[[:space:]]*/,""); sub(/#.*$/,""); gsub(/["'"'"'[:space:]]/,"")
                   if (key=="template") { print; exit } else if (v=="") v=$0
                 }
                 END {if (v!="") print v}' "$MD_FILE")"
fi
LAYOUT="${LAYOUT:-resume}"
TEMPLATE="${TPL_DIR}/${LAYOUT}/layout.tex"
[[ -f "$TEMPLATE" ]] || {
  echo "ERROR: 不明なレイアウト '$LAYOUT'。使えるのは: $(list_layouts)" >&2
  echo "       追加するには ${TPL_DIR#"$ROOT"/}/<名前>/layout.tex を作る。" >&2; exit 1; }


# --- レイアウトの既定値をテンプレート先頭の %%! 行から読む ---
tpl_directive() {
  sed -n "s/^%%![[:space:]]*$1[[:space:]]*=[[:space:]]*//p" "$TEMPLATE" | head -1 | sed 's/[[:space:]]*$//'
}
FONTSIZE="${FONTSIZE:-$(tpl_directive fontsize)}"
CLASSOPTS="$(tpl_directive classopts)"
CLASSOPTS="${CLASSOPTS//__FONTSIZE__/${FONTSIZE:-10pt}}"
[[ -n "$TWOCOL" ]] && CLASSOPTS="${CLASSOPTS},twocolumn"
TITLESTYLE="$(tpl_directive titleblock)"; TITLESTYLE="${TITLESTYLE:-title-only}"
BIBMODE="$(tpl_directive bibliography)";  BIBMODE="${BIBMODE:-suppress}"
TOPLEVEL="$(tpl_directive toplevel)";     TOPLEVEL="${TOPLEVEL:-default}"
ENGINE="$(tpl_directive engine)";         ENGINE="${ENGINE:-lualatex}"
CITEMODE="$(tpl_directive citations)";    CITEMODE="${CITEMODE:-citeproc}"
COMMON_NAME="$(tpl_directive common)";    COMMON_NAME="${COMMON_NAME:-md-common.tex}"
# common はレイアウト自身のフォルダ → assets/ の順に探す（none で読み込まない）
if [[ "$COMMON_NAME" == "none" ]]; then
  COMMON=""
elif [[ -f "${TPL_DIR}/${LAYOUT}/${COMMON_NAME}" ]]; then
  COMMON="${TPL_DIR}/${LAYOUT}/${COMMON_NAME}"
else
  COMMON="${SKILL_DIR}/assets/${COMMON_NAME}"
fi
[[ -n "$CLASSOPTS" ]] || { echo "ERROR: $TEMPLATE に '%%! classopts = ...' の宣言がありません。" >&2; exit 1; }
[[ -z "$COMMON" || -f "$COMMON" ]] || { echo "ERROR: 共通プリアンブルがありません: $COMMON" >&2; exit 1; }
case "$ENGINE" in lualatex|platex) ;; *)
  echo "ERROR: $TEMPLATE の '%%! engine = $ENGINE' は未対応（lualatex / platex）。" >&2; exit 1 ;; esac

# --margin が単一の長さ（例 15mm）なら geometry の margin= に包む
[[ "$MARGIN" =~ ^[0-9.]+(mm|cm|pt|in)$ ]] && MARGIN="margin=${MARGIN}"

SRC_DIR="$(cd "$(dirname "$MD_FILE")" && pwd)"
BASE="$(basename "${MD_FILE%.md}")"
# 出力先の既定は「原稿の隣」。中間ファイル（.tex や正規化済み .md）もここに出るので、
# 制作中のものが完成版の置き場に混ざらない。
if [[ -z "$OUTDIR" ]]; then
  OUTDIR="$SRC_DIR"
fi
[[ "$OUTDIR" != /* ]] && OUTDIR="${ROOT}/${OUTDIR}"
mkdir -p "$OUTDIR"

# 完成版の収集先。原稿が work/publications/<名前>/ の下にあるなら、
# 同じ名前の publications/<名前>/ へ PDF だけをコピーする（中間ファイルは移さない）。
# 手でコピーすると忘れるので、ビルドの一部として行う。
COLLECT_DIR=""
case "$SRC_DIR/" in
  "${ROOT}/work/publications/"*)
    COLLECT_DIR="${ROOT}/publications/${SRC_DIR#"${ROOT}/work/publications/"}"
    ;;
esac

# --- タイトル: 引数 → frontmatter title: → \chapter{} → 最初の # 見出し → ファイル名 ---
TITLE="$TITLE_ARG"
[[ -z "$TITLE" ]] && TITLE="$(awk 'NR==1 && $0 !~ /^---[[:space:]]*$/ {exit}
    /^---[[:space:]]*$/ {f++; if (f==2) exit; next}
    f==1 && /^title:[[:space:]]*/ {sub(/^title:[[:space:]]*/,""); gsub(/^["'"'"']|["'"'"']$/,""); print; exit}' "$MD_FILE")"
[[ -z "$TITLE" ]] && TITLE="$(grep -oE '\\chapter\{[^}]*\}' "$MD_FILE" | head -1 | sed -E 's/\\chapter\{(.*)\}/\1/' || true)"
[[ -z "$TITLE" ]] && TITLE="$(grep -oE '^#[[:space:]]+.+' "$MD_FILE" | head -1 | sed -E 's/^#[[:space:]]+//' || true)"
[[ -z "$TITLE" ]] && TITLE="$BASE"

NORM="${OUTDIR}/.${BASE}.norm.md"
BODY="${OUTDIR}/.${BASE}.body.tex"
TEX="${OUTDIR}/${BASE}.tex"

# --- 1) 正規化（書き癖の機械補正）＋ 記法の前処理 ---
python3 "${SKILL_DIR}/normalize.py" "$MD_FILE" "$NORM"

# 冒頭の # 見出しは原稿のタイトル行なので本文から落とす（\chapter{} 変換より前に行う
# ので、\chapter{} 記法は対象外）。--keep-h1 で抑止できる。
SHIFT=()
if [[ "$KEEP_H1" != "1" ]]; then
  cp "$NORM" "${NORM}.h1"
  perl -0777 -pi -e '
    s/\A(---\r?\n.*?\r?\n---[ \t]*\r?\n)\s*#[ \t]+[^\n]*\r?\n/$1/s
      or s/\A\s*#[ \t]+[^\n]*\r?\n//;
  ' "$NORM"
  # H1 を落としたうえで他に H1 が無ければ、## を1段繰り上げる。
  # 判定はコードフェンスの外だけで行う（```bash 内の「# コメント」を見出しと
  # 誤認すると、以降すべての見出しが1段深いまま組まれる）。
  h1_outside_fence() {
    awk '/^```/ {f=!f; next} !f && /^# / {found=1} END {exit !found}' "$1"
  }
  if ! cmp -s "$NORM" "${NORM}.h1" && ! h1_outside_fence "$NORM" \
     && ! grep -q '\\chapter{' "$NORM"; then
    SHIFT+=(--shift-heading-level-by=-1)
  fi
  rm -f "${NORM}.h1"
fi

perl -0777 -pi -e '
  s/\\chapter\{([^}]*)\}/# $1/g;
  s/\\section\{([^}]*)\}/## $1/g;
  s{<sup>\d+</sup>\s*<span class="footnote">(.*?)</span>}{^[$1]}gs;
  s/^>[ \t]*\[!\w+\][-+]?[ \t]*/> /gm;
  s/\[\[([^\]|#]+)(?:#[^\]|]*)?\|([^\]]+)\]\]/$2/g;
  s/\[\[([^\]|#]+)(?:#([^\]|]*))?\]\]/$1/g;
  s/\x{fe0e}|\x{fe0f}//g;
' "$NORM"

# --- 2) pandoc: 本文フラグメントへ ---
#     [@key] 引用が本文にあり references.bib があれば Chicago note で脚注書誌に展開
CITE=()
MISSING_BIB=""
BIBFORTEX="$BIB"
if grep -q '\[@' "$NORM"; then
  if [[ ! -f "$BIB" ]]; then
    MISSING_BIB="$BIB"
  elif [[ "$CITEMODE" == "natbib" ]]; then
    # 学会クラス（BibTeX + .bst）向け。[@key] を \citep{key} にし、書誌は LaTeX 側で組む
    CITE+=(--natbib)
    # Zotero が出す「姓, 名」は日本語 .bst で姓名が反転する。詰めた複製を作って渡す
    # （元の references.bib は変更しない）
    BIBFORTEX="${OUTDIR}/.${BASE}.bib"
    python3 "${SKILL_DIR}/bib_for_pbibtex.py" "$BIB" "$BIBFORTEX" >&2
  else
    CITE+=(--citeproc --bibliography="$BIB")
    if [[ "$BIBMODE" == "list" ]]; then
      # 末尾に参考文献リストを出す（見出しを追記。citeprocが直後に書誌を置く）
      printf '\n\n# 参考文献 {-}\n' >> "$NORM"
    else
      CITE+=(--metadata suppress-bibliography=true)
    fi
    [[ -f "$CSL" ]] && CITE+=(--csl="$CSL")
  fi
fi
TOP=()
[[ "$TOPLEVEL" == "chapter" ]] && TOP+=(--top-level-division=chapter)

"$PANDOC" "$NORM" \
  -f markdown+mark-implicit_figures --syntax-highlighting=none --wrap=none \
  ${CITE[@]+"${CITE[@]}"} ${SHIFT[@]+"${SHIFT[@]}"} ${TOP[@]+"${TOP[@]}"} \
  -t latex -o "$BODY"

# --- 3) テンプレートへ差し込んで単一の .tex を組み立てる ---
GRAPHICSPATH="{${SRC_DIR}/}{${SRC_DIR}/../}" \
TITLE="$TITLE" AUTHOR="$AUTHOR" DATE="$DATE" TITLESTYLE="$TITLESTYLE" \
CLASSOPTS="$CLASSOPTS" MARGIN="$MARGIN" \
TEMPLATE="$TEMPLATE" COMMON_TEX="$COMMON" SECNUM="$SECNUM" MD_FILE="$MD_FILE" BIBPATH="${BIBFORTEX%.bib}" \
BODY_TEX="$BODY" OUT_TEX="$TEX" ROOT="$ROOT" \
python3 <<'PY'
import os, re
tpl    = open(os.environ["TEMPLATE"], encoding="utf-8").read()
_c     = os.environ.get("COMMON_TEX", "")
common = open(_c, encoding="utf-8").read().rstrip() if _c else ""
body   = open(os.environ["BODY_TEX"], encoding="utf-8").read().rstrip()

# --- frontmatter の全キーを読む（スカラーとブロックスカラー | に対応）---
# レイアウトは __KEY__（大文字）でこれらを参照できる。学会ごとに必要な項目
# （英文タイトル・要旨・キーワード等）はレイアウト側で好きに使えばよい。
def read_frontmatter(path):
    fm, key, buf, indent, last_key = {}, None, [], None, None
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    if not lines or lines[0].strip() != "---":
        return fm
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if key is not None:                      # ブロックスカラーの継続
            if line.strip() == "" or line.startswith(" "):
                if line.strip():
                    if indent is None:
                        indent = len(line) - len(line.lstrip())
                    buf.append(line[indent:])
                else:
                    buf.append("")
                continue
            fm[key] = "\n".join(buf).strip(); key, buf, indent = None, [], None
        if line.lstrip().startswith("- ") or line.strip() == "-":
            # YAML のリスト要素。直前のキーに積む（要素にカンマを含められる）
            if last_key is not None:
                item = line.lstrip()[1:].strip().strip("\"'")
                if not isinstance(fm.get(last_key), list):
                    fm[last_key] = []
                fm[last_key].append(item)
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        last_key = k
        if v in ("|", ">", "|-", ">-"):
            key, buf, indent = k, [], None
            continue
        v = re.sub(r"\s+#.*$", "", v).strip()   # 行末コメント
        fm[k] = v.strip("\"'")
    if key is not None:
        fm[key] = "\n".join(buf).strip()
    return fm

frontmatter = read_frontmatter(os.environ["MD_FILE"])

title  = os.environ["TITLE"].strip()
author = os.environ["AUTHOR"].strip()
date   = os.environ["DATE"].strip()
style  = os.environ["TITLESTYLE"]

def _jdate(d):
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", d)
    return "%d年%d月%d日" % (int(m[1]), int(m[2]), int(m[3])) if m else d

lines = []
if style == "resume":
    # レジュメ: 右上に作成者・作成日、中央にタイトル
    meta = []
    if author: meta.append("作成者：" + author)
    if date:   meta.append("作成日：" + _jdate(date))
    if meta:
        lines.append("\\begin{flushright}\\small")
        lines.append("  " + "\\\\\n  ".join(meta))
        lines.append("\\end{flushright}\\vspace{0.5ex}")
    lines += ["\\begin{center}", "  {\\LARGE\\bfseries %s}" % title,
              "\\end{center}", "\\vspace{1ex}", ""]
elif style == "center-meta":
    # 中央にタイトル、その下に著者・日付を小書き
    meta = [x for x in (author, _jdate(date) if date else "") if x]
    lines += ["\\begin{center}", "  {\\LARGE\\bfseries %s}" % title]
    if meta:
        lines.append("  \\\\[1ex] {\\normalsize %s}" % "　".join(meta))
    lines += ["\\end{center}", "\\vspace{1ex}", ""]
elif style == "none":
    # レイアウト側が自前でタイトルを組む（学会クラスなど）
    pass
else:
    # title-only: 中央にタイトルのみ（作成者は出さない。日付は指定時のみ）
    lines += ["\\begin{center}", "  {\\LARGE\\bfseries %s}" % title]
    if date:
        lines.append("  \\\\[1ex] {\\normalsize %s}" % _jdate(date))
    lines += ["\\end{center}", "\\vspace{1ex}", ""]

titleblock = "\n".join(lines)
if os.environ.get("SECNUM") == "false":
    titleblock = "\\setcounter{secnumdepth}{-2}\n" + titleblock

# --- テンプレートへの差し込み ---
# 差し込みは「frontmatter 由来のキー」→「予約語」の順に行う。逆にすると、
# 本文（__BODY__）に含まれるコード例の __FOO__ まで置換してしまう。
VARS = dict(frontmatter)
VARS["title"] = title
# 書誌ファイルは frontmatter の bib: で原稿ごとに差し替えられる
# （学会配布の .bib を使う場合など）。相対パスはリポジトリルート基準。
if VARS.get("bib"):
    _b = VARS["bib"]
    if not _b.startswith("/"):
        _b = os.path.join(os.environ.get("ROOT", ""), _b)
    VARS["bib"] = _b[:-4] if _b.endswith(".bib") else _b
else:
    VARS["bib"] = os.environ.get("BIBPATH", "")
# YYYY-MM-DD の値からは __KEY_Y__ / __KEY_M__ / __KEY_D__ も作る。
# \受付{年}{月}{日} のように年月日を別々の引数で渡すクラスに対応するため。
for k, v in list(VARS.items()):
    m = None if isinstance(v, list) else re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", str(v).strip())
    if m:
        VARS[k + "_y"], VARS[k + "_m"], VARS[k + "_d"] = (
            m.group(1), str(int(m.group(2))), str(int(m.group(3))))

KEY_RE = re.compile(r"__([A-Z][A-Z0-9_]*)(?:\|([^_]*))?__")
# 下は本文・プリアンブル等を差し込む予約語。frontmatter の展開対象から外す
# （外さないと「原稿に無いキー」とみなされ、本文ごと空になる）。
RESERVED = {"COMMON", "CLASSOPTS", "MARGIN", "GRAPHICSPATH", "TITLEBLOCK", "BODY"}

def expand(text, get):
    """__KEY__ を展開する。__KEY|既定値__ と書くと、空のときに既定値を使う。"""
    def one(m):
        if m.group(1) in RESERVED:
            return m.group(0)
        v = get(m.group(1).lower())
        if isinstance(v, list):
            v = ", ".join(v)
        return v or (m.group(2) or "")
    return KEY_RE.sub(one, text)

# --- 繰り返しブロック ---
# 著者のように件数が原稿ごとに変わるものは、レイアウトにこう書く:
#   %%BEGIN-REPEAT author
#   \author{__AUTHOR__}{__AUTHOR_EN__}{Aff__AUTHOR_AFFILIATION|1__}[__EMAIL__]
#   %%END-REPEAT
# 見出しのキー（この例では author）の値を「,」で分け、件数ぶん繰り返す。
# ブロック内の __KEY__ は同じ位置の要素に展開され、要素が足りないキーは
# 最後の要素を使い回す（全員同じ所属、のような書き方ができる）。
# __INDEX__ は 1 から始まる通し番号。
REPEAT_RE = re.compile(r"^[ \t]*%%BEGIN-REPEAT[ \t]+(\w+)[ \t]*\n(.*?)^[ \t]*%%END-REPEAT[ \t]*\n",
                       re.S | re.M)

def parts(key):
    """繰り返しの要素列。YAML リストならそのまま、文字列なら「,」で分ける。"""
    v = VARS.get(key, "")
    if isinstance(v, list):
        return v
    return [x.strip() for x in v.split(",")] if v else []

def expand_repeat(m):
    driver, block = m.group(1).lower(), m.group(2)
    items = parts(driver)
    if not items:
        return ""
    out_blocks = []
    for i in range(len(items)):
        def get(key, i=i):
            if key == "index":
                return str(i + 1)
            p = parts(key)
            if not p and key[-2:] in ("_y", "_m", "_d"):
                # 繰り返しの中でも YYYY-MM-DD を年・月・日に割れるようにする
                q = parts(key[:-2])
                if q:
                    d = q[i] if i < len(q) else q[-1]
                    mm = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", d.strip())
                    if mm:
                        return {"_y": mm.group(1), "_m": str(int(mm.group(2))),
                                "_d": str(int(mm.group(3)))}[key[-2:]]
                return ""
            if not p:
                return ""
            return p[i] if i < len(p) else p[-1]
        out_blocks.append(expand(block, get))
    return "".join(out_blocks)

tpl = REPEAT_RE.sub(expand_repeat, tpl)
tpl = expand(tpl, lambda k: VARS.get(k, ""))
# 値が空のまま残った省略可能引数 [] は、指定なしとみなして落とす
tpl = re.sub(r"\[\s*\]", "", tpl)

out = (tpl
       .replace("__COMMON__", common)
       .replace("__CLASSOPTS__", os.environ["CLASSOPTS"])
       .replace("__MARGIN__", os.environ["MARGIN"])
       .replace("__GRAPHICSPATH__", os.environ["GRAPHICSPATH"])
       .replace("__TITLEBLOCK__", titleblock)
       .replace("__BODY__", body))

open(os.environ["OUT_TEX"], "w", encoding="utf-8").write(out)
PY

# --- 4) コンパイル（LuaLaTeX）→ 補助ファイルを掃除 ---
# レイアウトのフォルダに置かれたクラスファイル（学会指定の .cls/.sty/.bst）を探せるようにする
export TEXINPUTS="${TPL_DIR}/${LAYOUT}:${TEXINPUTS:-}"
export BSTINPUTS="${TPL_DIR}/${LAYOUT}:${BSTINPUTS:-}"
export BIBINPUTS="${ROOT}/bibliography:${SKILL_DIR}/assets:${TPL_DIR}/${LAYOUT}:${BIBINPUTS:-}"
if [[ "$ENGINE" == "platex" ]]; then
  # 日本語の .bst（ipsjunsrt 等）は is.kanji.str$ を使うため、素の bibtex では
  # 「unknown function」で落ちる。日本語版の pbibtex を明示する。
  PBIBTEX="$(command -v pbibtex || command -v jbibtex || echo bibtex)"
  # latexmk の $dvipdf の既定は Ghostscript 経由の dvipdf で、日本語のCIDフォントを
  # 扱えず本文が欧文字に化ける。dvipdfmx を明示すること。
  MKARGS=(-latex=platex -pdfdvi
          -e "\$bibtex='${PBIBTEX} %O %B';"
          -e "\$dvipdf='dvipdfmx %O -o %D %S';")
  MKSHOW="latexmk -latex=platex -pdfdvi -e \"\\\$bibtex='${PBIBTEX} %O %B';\" -e \"\\\$dvipdf='dvipdfmx %O -o %D %S';\""
else
  MKARGS=(-lualatex)
  MKSHOW="latexmk -lualatex"
fi
( cd "$OUTDIR" && "$LATEXMK" "${MKARGS[@]}" -interaction=nonstopmode -halt-on-error "${BASE}.tex" >/dev/null 2>&1 ) \
  || { echo "ERROR: LaTeX コンパイルに失敗しました。'cd \"$OUTDIR\" && $MKSHOW \"${BASE}.tex\"' で詳細を確認してください。" >&2; exit 1; }
# 掃除。-c にビルド時と同じエンジン指定を渡さないと、pLaTeX経路の .dvi が残る。
# .bbl と natbib用の一時 .bib は -c の対象外なので個別に消す（出力は .pdf と .tex のみ）。
( cd "$OUTDIR" && "$LATEXMK" "${MKARGS[@]}" -c "${BASE}.tex" >/dev/null 2>&1 ) || true
rm -f "$NORM" "$BODY" "${OUTDIR}/${BASE}.bbl" "${OUTDIR}/${BASE}.dvi"
[[ "$BIBFORTEX" != "$BIB" ]] && rm -f "$BIBFORTEX"

PDF="${OUTDIR}/${BASE}.pdf"
if command -v pdfinfo >/dev/null 2>&1; then
  PAGES="$(pdfinfo "$PDF" 2>/dev/null | awk '/^Pages:/{print $2}')"
fi
[[ -n "$MISSING_BIB" ]] && echo "WARN: [@key] 引用がありますが書誌が見つかりません: $MISSING_BIB" >&2
echo "OK: $PDF (${PAGES:-?}ページ)  layout=$LAYOUT  engine=$ENGINE  tex=$TEX"

# 完成版を publications/<名前>/ へ集める（原稿が work/publications/ 配下のときだけ）
if [[ -n "$COLLECT_DIR" ]]; then
  mkdir -p "$COLLECT_DIR"
  cp "$PDF" "$COLLECT_DIR/"
  echo "収集: ${COLLECT_DIR}/${BASE}.pdf"
fi

[[ "$OPEN" == true ]] && open "$PDF" 2>/dev/null || true
