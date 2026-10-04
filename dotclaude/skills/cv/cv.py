#!/usr/bin/env python3
"""研究業績1件を cv/pending/ に追加する（researchmap V2 インポート書式）。

  /cv --add <成果物キー>     業績を1件追加する
  /cv --clean                researchmap に取り込んだ後の後始末

内部で呼ぶサブコマンド:
  python3 .claude/skills/cv/cv.py extract <key|パス>
  python3 .claude/skills/cv/cv.py similar --table presentations --title "..."
  python3 .claude/skills/cv/cv.py header --table presentations
  python3 .claude/skills/cv/cv.py append --table presentations --json -
  python3 .claude/skills/cv/cv.py lint
  python3 .claude/skills/cv/cv.py forthcoming add|done --json -
  python3 .claude/skills/cv/cv.py clean [--archive] [--dry-run]

書き出す pending CSV はそのまま researchmap の「研究者・業績インポート」に上げられる。
カラム名はここに持たず、cv/rm_<table>*.csv の2行目（ヘッダ）を実行時に写す。
選択肢・必須・真偽値・複数値の規則だけ SCHEMA に持つ（値の正本はこの SCHEMA）。
"""
from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]   # .claude/skills/cv/ から3つ上がリポジトリルート
sys.path.insert(0, str(Path(__file__).resolve().parent))
import researchmap_to_cv as rm  # noqa: E402  正規化と重複判定を共有する

PENDING = rm.PENDING
FORTHCOMING = rm.SRC / "forthcoming.md"

# アクション列。新規は必ず insert/merge/優先度null/ID空（V2 CSV項目定義書 ※1）。
# 類似業績があるとエラーになるので、その場合だけ similar_merge/input_data に切り替える。
ACTION = {"アクション名": "insert", "アクションタイプ": "merge",
          "類似業績マージ優先度": "null", "ID": ""}

BOOL = ("TRUE", "FALSE", "null")
LANG = ("jpn", "eng")

SCHEMA = {
    "presentations": {
        "required": [("タイトル(日本語)", "タイトル(英語)")],
        "enums": {
            "会議種別": tuple(rm.KIND),          # 9値。正本は researchmap_to_cv.KIND
            "記述言語": LANG,
            "公開の有無": ("disclosed", "undisclosed"),
        },
        "bools": ("招待の有無", "国際・国内会議", "国際共著", "主要な業績かどうか"),
        "multi": ("講演者(日本語)", "講演者(英語)"),
        "dates": ("発表年月日", "開催年月日(From)", "開催年月日(To)"),
    },
    "published_papers": {
        "required": [("タイトル(日本語)", "タイトル(英語)")],
        "enums": {
            "掲載種別": ("scientific_journal", "international_conference_proceedings",
                         "symposium", "research_institution", "introduction_scientific_journal",
                         "others"),
            "記述言語": LANG,
            "公開の有無": ("disclosed", "undisclosed"),
        },
        "bools": ("査読の有無", "招待の有無", "国際・国内誌", "国際共著", "主要な業績かどうか"),
        "multi": ("著者(日本語)", "著者(英語)", "担当区分"),
        "dates": ("出版年月",),
    },
    "misc": {
        "required": [("タイトル(日本語)", "タイトル(英語)")],
        "enums": {
            "掲載種別": ("book_review", "introduction_scientific_journal",
                         "introduction_commerce_magazine", "introduction_other",
                         "meeting_report", "others"),
            "記述言語": LANG,
            "公開の有無": ("disclosed", "undisclosed"),
        },
        "bools": ("査読の有無", "招待の有無", "国際・国内誌", "国際共著", "主要な業績かどうか"),
        "multi": ("著者(日本語)", "著者(英語)", "担当区分"),
        "dates": ("出版年月",),
    },
    "books_etc": {
        "required": [("タイトル(日本語)", "タイトル(英語)")],
        "enums": {
            "担当区分": ("sole_author", "joint_author", "editor", "joint_editor",
                         "contributor", "translator", "editing_translation"),
            # dictionary_or_encycropedia は researchmap 側の綴りをそのまま使う
            "著書種別": ("scholarly_book", "general_book", "textbook",
                         "dictionary_or_encycropedia", "report", "others"),
            "記述言語": LANG,
            "公開の有無": ("disclosed", "undisclosed"),
        },
        "bools": ("査読の有無", "国際共著", "主要な業績かどうか"),
        "multi": ("著者(翻訳者)(日本語)", "著者(翻訳者)(英語)", "原著者(日本語)", "原著者(英語)"),
        "dates": ("出版年月",),
    },
    "awards": {
        "required": [("賞名(日本語)", "賞名(英語)")],
        "enums": {
            "受賞区分": ("international_society", "japan_society", "publisher",
                         "government", "public_organization", "others"),
            "公開の有無": ("disclosed", "undisclosed"),
        },
        "bools": ("主要な業績かどうか",),
        # 列名は「受賞者」ではなく「受賞者・グループ」（V2 CSV の実際の列名）
        "multi": ("受賞者・グループ(日本語)", "受賞者・グループ(英語)"),
        "dates": ("受賞年月",),
    },
    "research_projects": {
        # 題目に当たる列は「研究課題名」ではなく「タイトル」（V2 CSV の実際の列名）。
        # 誤った列名だと lint の必須チェックが常に落ち、pending の重複判定も効かない。
        "required": [("タイトル(日本語)", "タイトル(英語)")],
        "enums": {
            "資金種別": ("competitive_research_funding", "joint_research",
                         "contract_research", "subsidy", "others"),
            "担当区分": ("principal_investigator", "coinvestigator",
                         "research_collaborator", "others"),
            "公開の有無": ("disclosed", "undisclosed"),
        },
        "bools": ("国際共同研究", "主要な業績かどうか"),
        "multi": ("担当研究者(日本語)", "担当研究者(英語)"),
        "dates": ("研究期間(From)", "研究期間(To)"),
    },
}

DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")

# 業績に使う自分の表記。旧姓は当時の事実なので書き換えず、判定にだけ使う。
# ★ 自分の氏名表記をここに書く。改姓している場合は旧姓も入れる
#   （旧姓のレコードは当時の事実なので書き換えず、判定にだけ使う）
SELF_ALIASES: set[str] = set()


# ---------------------------------------------------------------- 共通
def die(msg: str) -> None:
    sys.exit(f"エラー: {msg}")


def schema(table: str) -> dict:
    if table not in SCHEMA:
        die(f"未対応のテーブル: {table}（{'/'.join(SCHEMA)}）")
    return SCHEMA[table]


#: researchmap V2 CSV の列名一覧（同梱）。エクスポートをまだ持っていない人でも
#: pending を作れるようにするため。researchmap 側で列が増減したらエクスポートが優先される。
BUNDLED_HEADERS = Path(__file__).resolve().parent / "references" / "headers.json"


def header_of(table: str) -> list[str]:
    """列名の出所。エクスポート → pending → 同梱の一覧 の順に探す。

    エクスポートを最優先にするのは、researchmap 側で列が変わったときに
    同梱の一覧より実物が正しいからである。
    """
    path = rm.latest_export(table)
    if path:
        return rm.read_rm_csv(path)[0]
    pend = rm.pending_path(table)
    if pend.exists():
        return rm.read_rm_csv(pend)[0]
    if BUNDLED_HEADERS.exists():
        bundled = json.loads(BUNDLED_HEADERS.read_text(encoding="utf-8"))
        if table in bundled:
            return bundled[table]
    die(f"ヘッダの出所がない。cv/rm_{table}*.csv を置くか、{BUNDLED_HEADERS.name} に {table} を足す")


# ---------------------------------------------------------------- extract
def _kv_header(text: str) -> dict:
    """'TITLE: ...' 形式のヘッダと本文を分ける（abstract.md の規約）。"""
    head, _, body = text.partition("\n---")
    out = {}
    for line in head.splitlines():
        m = re.match(r"^([A-Z]+):\s*(.+)$", line.strip())
        if m:
            out[m.group(1)] = re.sub(r"<br\s*/?>", " ", m.group(2)).strip()
    return out, body.strip()


# meta.md の KEY は researchmap の列名そのもの（日本語・丸括弧つき）。
# abstract.md の ASCII 見出し（TITLE: 等）とは別の規約なので、パーサも分ける。
# 行頭が # の行はコメントとして捨てる（雛形の見出しを残したまま使えるようにするため）。
_META_RE = re.compile(r"^([^#:：][^:：]*)[:：]\s*(.*)$")

# 真偽値の書き方を人が書きやすい形から researchmap 書式へ寄せる。
_BOOL_WORDS = {"有": "TRUE", "無": "FALSE", "あり": "TRUE", "なし": "FALSE",
               "はい": "TRUE", "いいえ": "FALSE", "true": "TRUE", "false": "FALSE",
               "TRUE": "TRUE", "FALSE": "FALSE"}


def _meta_kv(text: str) -> dict:
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("<!--"):
            continue
        m = _META_RE.match(line)
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


def _person(name: str, ascii_col: bool) -> str:
    """'山田 太郎' → '山田\\,太郎'（日本語欄）／'Taro Yamada' → そのまま（英語欄）。

    researchmap は姓名の区切りをエスケープカンマで表す。英語欄は空白区切りのままでよい。
    """
    parts = name.split()
    if ascii_col or len(parts) < 2:
        return " ".join(parts)
    return "\\,".join(parts)


def _norm_meta(table: str, kv: dict) -> dict:
    """meta.md の値を researchmap の書式へ直す。

    真偽値は 有/無 等を TRUE/FALSE に、複数値は `;` 区切りを `[a,b]` に畳む。
    列名の妥当性はここでは見ない（append の validate が header と突き合わせて弾く）。
    """
    s = schema(table)
    out = {}
    for k, v in kv.items():
        if not v or v == "null":
            continue
        if k in s["bools"]:
            v = _BOOL_WORDS.get(v, v)
        elif k in s["multi"] and not v.startswith("["):
            people = [x.strip() for x in re.split(r"[;；]", v) if x.strip()]
            v = "[" + ",".join(_person(x, k.endswith("(英語)")) for x in people) + "]"
        out[k] = v
    return out


def extract(key: str, table: str = "presentations") -> dict:
    cands = [ROOT / "publications" / key]
    cands += sorted(ROOT.glob(f"work/*/drafts/{key}"))
    cands += sorted(ROOT.glob(f"work/*/drafts/*/{key}"))
    p = Path(key)
    if p.is_dir():
        cands.insert(0, p.resolve())
    dirs = [d for d in cands if d.is_dir()]
    if not dirs:
        die(f"成果物が見つからない: {key}")

    found, context = {}, []
    for d in dirs:
        # meta.md が最優先。researchmap の列名で書いてあるものは全部そのまま拾う。
        meta = d / "meta.md"
        if meta.exists():
            src = str(meta.relative_to(ROOT))
            for k, v in _norm_meta(table, _meta_kv(meta.read_text(encoding="utf-8"))).items():
                found.setdefault(k, {"value": v, "source": src})
        ab = d / "abstract" / "abstract.md"
        if ab.exists():
            kv, body = _kv_header(ab.read_text(encoding="utf-8"))
            src = str(ab.relative_to(ROOT))
            if kv.get("TITLE"):
                found.setdefault("タイトル(英語)", {"value": kv["TITLE"], "source": src})
            if kv.get("AUTHORS"):
                names = [n.strip() for n in kv["AUTHORS"].split(",") if n.strip()]
                names = [" ".join(w.capitalize() if w.isupper() else w for w in n.split())
                         for n in names]
                col = "著者(英語)" if "著者(英語)" in header_of(table) else "講演者(英語)"
                found.setdefault(col, {"value": "[" + ",".join(names) + "]", "source": src})
            if body:
                found.setdefault("概要(英語)", {"value": " ".join(body.split()), "source": src})
        tex = d / "manuscript" / "main.tex"
        if tex.exists() and "タイトル(英語)" not in found:
            m = re.search(r"\\title\{(.+?)\}", tex.read_text(encoding="utf-8"), re.S)
            if m:
                found.setdefault("タイトル(英語)", {"value": " ".join(m.group(1).split()),
                                                   "source": str(tex.relative_to(ROOT))})
        for name in ("README.md", "manuscript/main_ja.md"):
            f = d / name
            if f.exists():
                context.append(str(f.relative_to(ROOT)))

    header = header_of(table)
    # 固定値（references/extract.md の「固定値」節）。毎回聞かずに既定で埋める。
    for k, v in (("公開の有無", "disclosed"), ("主要な業績かどうか", "FALSE")):
        if k in header:
            found.setdefault(k, {"value": v, "source": "既定値"})
    # 残りは meta.md に書かれていない項目。Claude が散文から提案し、PIが確認する。
    skip = set(ACTION)
    unresolved = [c for c in header if c not in skip and c not in found]
    return {"key": key,
            "table": table,
            "dirs": [str(d.relative_to(ROOT)) for d in dirs],
            "extracted": found,
            "context_files": context,
            "meta_template": [c for c in header if c not in skip],
            "unresolved": unresolved}


# ---------------------------------------------------------------- similar
def similar(table: str, title: str, limit: int = 3) -> list:
    recs = rm.load(table)
    cols = rm.TITLE_COLS.get(table, rm.DEFAULT_TITLE_COLS)
    key = rm.norm_title(title)
    scored = []
    for r in recs:
        for c in cols:
            t = rm.val(r, c)
            if not t:
                continue
            ratio = difflib.SequenceMatcher(None, key, rm.norm_title(t)).ratio()
            scored.append((ratio, t))
    scored.sort(reverse=True)
    return [{"ratio": round(x, 3), "title": t} for x, t in scored[:limit]]


# ---------------------------------------------------------------- append
def validate(table: str, rec: dict, header: list[str]) -> list[str]:
    s = schema(table)
    errs = []
    for group in s["required"]:
        if not any(rm.val(rec, c) for c in group):
            errs.append(f"必須項目が空: {' または '.join(group)}")
    for col, allowed in s["enums"].items():
        v = rec.get(col, "null")
        if v not in ("", "null") and v not in allowed:
            errs.append(f"{col} の値が選択肢外: {v}（{'/'.join(allowed)}）")
    for col in s["bools"]:
        v = rec.get(col, "null")
        if v not in BOOL:
            errs.append(f"{col} は TRUE/FALSE/null のいずれか: {v}")
    for col in s["multi"]:
        v = rec.get(col, "null")
        if v not in ("", "null") and not (v.startswith("[") and v.endswith("]")):
            errs.append(f"{col} は [a,b] 形式にする: {v}")
    for col in s["dates"]:
        v = rec.get(col, "null")
        if v not in ("", "null") and not DATE_RE.match(v):
            errs.append(f"{col} は yyyy / yyyy-mm / yyyy-mm-dd: {v}")
    for col in rec:
        if col not in header:
            errs.append(f"ヘッダにない列: {col}")
    return errs


def append(table: str, rec: dict) -> None:
    header = header_of(table)
    row = dict(ACTION)
    row.update({k: v for k, v in rec.items() if v is not None})
    errs = validate(table, row, header)
    if errs:
        die("\n  ".join(["入力が不正"] + errs))

    dup = [r for r in rm.load(table)
           if rm.record_keys(table, r) & rm.record_keys(table, row)]
    if dup:
        cols = rm.TITLE_COLS.get(table, rm.DEFAULT_TITLE_COLS)
        die(f"同じ題目が既にある: {rm.val(dup[0], *cols)}")

    PENDING.mkdir(parents=True, exist_ok=True)
    path = rm.pending_path(table)
    new_file = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow([table])
            w.writerow(header)
        w.writerow([row.get(c, "null") or ("" if c == "ID" else "null") for c in header])
    print(f"追記した: {path.relative_to(ROOT)}")
    print(f"researchmap には このファイルをそのままアップロードする（整合性チェック→反映）")


# ---------------------------------------------------------------- lint
def lint() -> int:
    tables = rm.pending_tables()
    if not tables:
        print("pending はない")
        return 0
    bad = 0
    for t in tables:
        path = rm.pending_path(t)
        raw = path.read_bytes()
        rows = list(csv.reader(path.open(encoding="utf-8", newline="")))
        errs = []
        if raw.startswith(b"\xef\xbb\xbf"):
            errs.append("BOM が付いている（インポートでテーブル名の判定を壊す）")
        if not rows or rows[0] != [t]:
            errs.append(f"1行目はテーブル名 {t} の単独セルにする")
        export = rm.latest_export(t)
        if export and len(rows) > 1 and rows[1] != rm.read_rm_csv(export)[0]:
            errs.append("2行目がエクスポートのヘッダと一致しない")
        if len(raw) > 10 * 1024 * 1024:
            errs.append("10MB を超えている")
        header = rows[1] if len(rows) > 1 else []
        for i, r in enumerate(rows[2:], start=3):
            rec = dict(zip(header, r))
            if "" in [v for k, v in rec.items() if k != "ID"]:
                errs.append(f"{i}行目: 空欄がある（未設定は null と書く）")
            for k, v in ACTION.items():
                if rec.get(k, "") != v:
                    errs.append(f"{i}行目: {k} は {v!r} にする（現在 {rec.get(k)!r}）")
            errs += [f"{i}行目: {e}" for e in validate(t, rec, header)]
        print(f"{path.name}: {'OK' if not errs else str(len(errs)) + '件の問題'}")
        for e in errs:
            print(f"  - {e}")
        bad += len(errs)
    return bad


# ---------------------------------------------------------------- clean
ARCHIVE = rm.SRC / "archive"
_EXPORT_RE = re.compile(r"^rm_(.+?)(\d{6}|\d{8})(?:-(\d+))?\.csv$")


def superseded_exports() -> list:
    """同じテーブルのエクスポートが複数あるとき、最新以外を返す。"""
    groups: dict = {}
    for p in rm.SRC.glob("rm_*.csv"):
        m = _EXPORT_RE.match(p.name)
        if m:
            groups.setdefault(m.group(1), []).append(p)
    old = []
    for table, paths in groups.items():
        if len(paths) > 1:
            keep = rm.latest_export(table)
            old += [p for p in paths if p != keep]
    return sorted(old)


def clean_up(archive: bool = False, dry: bool = False) -> None:
    """researchmap に取り込んだ後の後始末。

    1. 取り込み済みの pending 行を pending/imported/ へ退避し、空になったファイルを消す
    2. 新しいエクスポートに置き換わった古いファイルを削除する（--archive なら archive/ へ移す）
    3. master を再生成する

    古いエクスポートを既定で消すのは、researchmap 上でレコードを修正・削除したということは
    そのデータが誤りか不要だったということであり、古いスナップショットを残す意味が薄いため
    （2026-09-26 方針）。残したい場合だけ --archive を付ける。
    """
    print("1. pending の掃除")
    if dry:
        for t in rm.pending_tables():
            rm.load(t)
            st = rm.PENDING_STATS.get(t, {"new": [], "imported": []})
            print(f"   {rm.pending_path(t).name}: NEW {len(st['new'])} / IMPORTED {len(st['imported'])}")
    else:
        rm.sweep_pending()
        for t in rm.pending_tables():           # ヘッダだけ残った殻を片付ける
            path = rm.pending_path(t)
            if not rm.read_rm_csv(path)[1]:
                path.unlink()
                print(f"  {path.name}: 中身が無くなったので削除した")

    print("\n2. 置き換わったエクスポート")
    old = superseded_exports()
    if not old:
        print("   重複しているエクスポートはない")
    for p in old:
        if dry:
            print(f"   {p.name} → {'archive/' if archive else '削除'}（--dry-run のため未実行）")
        elif archive:
            ARCHIVE.mkdir(parents=True, exist_ok=True)
            p.rename(ARCHIVE / p.name)
            print(f"   {p.name}: archive/ へ移した")
        else:
            p.unlink()
            print(f"   {p.name}: 削除した")

    print("\n3. master の再生成")
    rm.main(["--dry-run"] if dry else [])


# ---------------------------------------------------------------- forthcoming
HEAD = ("| key | 予定テーブル | 題目 | 著者 | 掲載予定 | 状態 | 次アクション | 最終確認日 |\n"
        "|---|---|---|---|---|---|---|---|\n")


def forthcoming(op: str, rec: dict) -> None:
    """刊行待ちの業績を cv/forthcoming.md で待つ。pending には入れない。"""
    if not FORTHCOMING.exists():
        FORTHCOMING.write_text(
            "# 刊行待ちの業績\n\n"
            "掲載先が未確定のものはここで待つ。誌名・巻号頁・DOI が `null` のまま\n"
            "researchmap に insert すると不完全なレコードが残り、正式版を入れるときに\n"
            "類似業績エラーになるため。刊行後に `/cv --add <key> --table published_papers`。\n\n"
            + HEAD, encoding="utf-8")
    text = FORTHCOMING.read_text(encoding="utf-8")
    if op == "add":
        cells = [rec.get(k, "") for k in
                 ("key", "table", "title", "authors", "venue", "status", "next", "checked")]
        FORTHCOMING.write_text(text.rstrip("\n") + "\n| " + " | ".join(cells) + " |\n",
                               encoding="utf-8")
        print(f"待機列に追加した: {FORTHCOMING.relative_to(ROOT)}")
    else:
        key = rec.get("key", "")
        lines = [ln for ln in text.splitlines(True) if not ln.startswith(f"| {key} |")]
        FORTHCOMING.write_text("".join(lines), encoding="utf-8")
        print(f"待機列から外した: {key}")


# ---------------------------------------------------------------- CLI
def read_json(arg: str) -> dict:
    return json.loads(sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("extract", help="成果物から書誌を拾う")
    p.add_argument("key")
    p.add_argument("--table", default="presentations",
                   help="対象テーブル（既定 presentations）。拾う列と残りの項目がこれで決まる")

    p = sub.add_parser("similar", help="類似する既存業績を探す")
    p.add_argument("--table", required=True)
    p.add_argument("--title", required=True)

    p = sub.add_parser("header", help="テーブルのカラム名を出す")
    p.add_argument("--table", required=True)

    p = sub.add_parser("append", help="pending CSV に1件追記する")
    p.add_argument("--table", required=True)
    p.add_argument("--json", required=True, help="'-' で標準入力")

    sub.add_parser("lint", help="pending CSV を検証する")

    p = sub.add_parser("clean", help="取り込み後の後始末（pending掃除＋古いエクスポート削除＋再生成）")
    p.add_argument("--archive", action="store_true", help="古いエクスポートを削除せず archive/ へ移す")
    p.add_argument("--dry-run", action="store_true", help="何もせず、やることだけ表示する")

    p = sub.add_parser("forthcoming", help="刊行待ちの待機列を操作する")
    p.add_argument("op", choices=("add", "done"))
    p.add_argument("--json", required=True)

    a = ap.parse_args()
    if a.cmd == "extract":
        print(json.dumps(extract(a.key, a.table), ensure_ascii=False, indent=2))
    elif a.cmd == "similar":
        print(json.dumps(similar(a.table, a.title), ensure_ascii=False, indent=2))
    elif a.cmd == "header":
        print("\n".join(header_of(a.table)))
    elif a.cmd == "append":
        append(a.table, read_json(a.json))
    elif a.cmd == "lint":
        sys.exit(1 if lint() else 0)
    elif a.cmd == "clean":
        clean_up(archive=a.archive, dry=a.dry_run)
    elif a.cmd == "forthcoming":
        forthcoming(a.op, read_json(a.json))


if __name__ == "__main__":
    main()
