#!/usr/bin/env python3
"""researchmap のエクスポートCSVから、履歴書記入用のマスターCSVを生成する。

  python3 .claude/skills/cv/researchmap_to_cv.py

入力: cv/rm_*.csv（researchmap「業績一覧ダウンロード」の出力。最新の日付のものを自動選択）
出力: cv/master/*.csv（UTF-8 BOM付き。Excelでそのまま開ける）

researchmap に無い情報のセルは ★ を入れてある。★ を検索して埋めれば履歴書に転記できる。
01〜10 の項目立ては、大学の非常勤講師用履歴書によくある様式に合わせてある
（1.学歴 2.学位 3.職歴 4.所属学会 5.専門分野 6.学術論文 7.著書・翻訳 8.講演・口頭発表）。
様式が違っても同じマスターから転記できる。

11 以降は履歴書の様式には無いが researchmap が持っている業績で、科研費の業績報告や
別紙での提出に使う（受賞・研究課題・委員歴・社会貢献・メディア報道・作品・産業財産権）。
researchmap に登録がないテーブルはファイルを作らず、実行の最後に一覧で知らせる。

「（参考）」付きの列は様式に欄がないことが多い項目である。査読の有無・国際共著・配分額など、
別紙や科研費の報告で求められるものを落とさないために持たせてある。様式に欄がなければ
転記時に無視すればよい。エクスポートが持っている値はメモ欄に畳まず、必ず列として出す。

現住所と自宅・携帯電話は提出のたびに直接入力する方針のため、意図的に項目を持たない。
本務先の住所・電話は固定なので保持する。
"""
from __future__ import annotations

import argparse
import calendar
import csv
import difflib
import hashlib
import io
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]   # .claude/skills/cv/ から3つ上がリポジトリルート
SRC = ROOT / "cv"
OUT = SRC / "master"
TODO = "★"
MANIFEST = OUT / ".manifest.json"
BACKUP = OUT / ".backup"
PREVIEW = OUT / ".preview"
PENDING = SRC / "pending"
IMPORTED = PENDING / "imported"


def rebind(src: Path) -> None:
    """入力ディレクトリを差し替える（検証用の --src）。"""
    global SRC, OUT, MANIFEST, BACKUP, PREVIEW, PENDING, IMPORTED
    SRC = src
    OUT = SRC / "master"
    MANIFEST = OUT / ".manifest.json"
    BACKUP = OUT / ".backup"
    PREVIEW = OUT / ".preview"
    PENDING = SRC / "pending"
    IMPORTED = PENDING / "imported"

# 手で記入したファイルを再生成で消さないための状態。
# 生成時のハッシュを .manifest.json に記録し、次回実行時に照合する。
# モジュールを import しただけでは何も読まない（cv スキルから関数を再利用するため）。
FORCE = False
DRY_RUN = False
ONLY: set = set()
_manifest: dict = {}
_first_run = True
_skipped: list = []
_state_loaded = False
_empty: list = []   # 実データが無くて生成を飛ばした (ファイル名, テーブル名)


def load_state() -> None:
    """manifest を読む。main() と write() から呼ぶ。2回目以降は何もしない。"""
    global _manifest, _first_run, _state_loaded
    if _state_loaded:
        return
    _manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    _first_run = not MANIFEST.exists()
    _state_loaded = True

# ---------------------------------------------------------------- 入力ユーティリティ


def latest_export(table: str) -> Path | None:
    """rm_<table><日付>-<連番>.csv のうち最も新しいものを返す。無ければ None。

    ダウンロード時のファイル名は揺れる（`...260924-1.csv` と `...20260925.csv` の両方が来る）。
    日付は6桁=YYMMDD／8桁=YYYYMMDD として正規化し、(日付, 連番) の数値で比較する。
    連番は省略可（無ければ0）。文字列ソートだと -10 が -9 より前に来る点も避けられる。
    日付が読めないファイルは最後に置き、更新時刻で比べる。
    """
    def key(p: Path) -> tuple:
        m = re.search(r"(\d{6}|\d{8})(?:-(\d+))?\.csv$", p.name)
        if not m:
            return (0, 0, p.stat().st_mtime)
        d = m.group(1)
        day = int(d) if len(d) == 8 else 20000000 + int(d)
        return (day, int(m.group(2) or 0), p.stat().st_mtime)

    cands = sorted(SRC.glob(f"rm_{table}*.csv"), key=key)
    return cands[-1] if cands else None


def read_rm_csv(path: Path) -> tuple[list[str], list[dict]]:
    """researchmap 書式のCSVを読む。1行目はテーブル名、2行目がヘッダ。"""
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        return ([], [])
    header = rows[1]
    return (header, [dict(zip(header, r)) for r in rows[2:]])


# ---------------------------------------------------------------- pending の合成
# researchmap に登録する前の追加分を cv/pending/ に置き、エクスポート原本と合成する。
# 取り込み後は次のエクスポートに同じ題目が現れるので、題目一致で pending 行を落とす。
# 「取り込み済み」を人が宣言する運用にしないのは、宣言を忘れた時点で二重計上するため。

# 題目に当たる列がテーブルごとに違う。ここに無いテーブルは DEFAULT_TITLE_COLS を使う。
# research_projects は「研究課題名」ではなく「タイトル」である（V2 CSV の実際の列名）。
# 誤った列名を書くと照合キーが空集合になり、pending が常に未取り込み扱いになる。
TITLE_COLS = {
    "awards": ("賞名(日本語)", "賞名(英語)"),
    "association_memberships": ("所属学協会名(日本語)", "所属学協会名(英語)"),
    "committee_memberships": ("委員名(日本語)", "委員名(英語)"),
    "industrial_property_rights": ("産業財産権名(日本語)", "産業財産権名(英語)"),
    "works": ("作品名(日本語)", "作品名(英語)"),
    "teaching_experience": ("科目(日本語)", "科目(英語)"),
    "research_areas": ("小分類名(日本語)", "小分類名(英語)"),
    "research_interests": ("キーワード(日本語)", "キーワード(英語)"),
    "education": ("学校名(日本語)", "学校名(英語)"),
    "research_experience": ("所属(日本語)", "所属(英語)"),
}
DEFAULT_TITLE_COLS = ("タイトル(日本語)", "タイトル(英語)")

# table -> {"new": [...], "imported": [...]}。--pending-status と実行末尾の通知で使う。
PENDING_STATS: dict = {}

_PUNCT = re.compile(r"[、。，．：；・「」『』〈〉《》【】（）()\[\]\"'“”‘’—–\-~〜_/\\|!?！？.,:;]")


def norm_title(s: str) -> str:
    """題目の照合キー。NFKC → 小文字 → 空白と記号を除去。"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"\s+", "", s)
    return _PUNCT.sub("", s)


def record_keys(table: str, rec: dict) -> set:
    """1レコードの照合キー集合。日英どちらかが一致すれば同一とみなす。

    受賞だけは賞名が短く再受賞もあり得るので受賞年を併用する。
    """
    suffix = ""
    if table == "awards":
        d = val(rec, "受賞年月")
        suffix = "|" + d[:4] if d else ""
    cols = TITLE_COLS.get(table, DEFAULT_TITLE_COLS)
    return {norm_title(val(rec, c)) + suffix for c in cols if norm_title(val(rec, c))}


def pending_path(table: str) -> Path:
    return PENDING / f"pending_{table}.csv"


def load(table: str) -> list[dict]:
    """エクスポート原本に pending の未取り込み分を足して返す。"""
    path = latest_export(table)
    recs = read_rm_csv(path)[1] if path else []

    pend = pending_path(table)
    if not pend.exists():
        return recs

    seen = set()
    for r in recs:
        seen |= record_keys(table, r)

    new, imported = [], []
    for r in read_rm_csv(pend)[1]:
        (imported if record_keys(table, r) & seen else new).append(r)
    PENDING_STATS[table] = {"new": new, "imported": imported}
    return recs + new


def pending_tables() -> list[str]:
    if not PENDING.exists():
        return []
    return sorted(p.stem[len("pending_"):] for p in PENDING.glob("pending_*.csv"))


def val(rec: dict, *keys: str) -> str:
    """最初に中身のある値を返す。researchmap は空欄を 'null' と書き出す。"""
    for k in keys:
        v = (rec.get(k) or "").strip()
        if v and v != "null":
            return v
    return ""


def people(field: str) -> list[str]:
    """'[山田\\,太郎,佐藤花子]' 形式の著者欄をリストにする。

    researchmap は姓と名の区切りをエスケープしたカンマ `\\,` で表す。日本語名は
    区切りを詰めて「山田太郎」、欧文名は空白を入れて「Taro Yamada」にする
    （一律に詰めると欧文が YamadaTaro に潰れる）。
    """
    if not field or field == "null":
        return []
    body = field.strip()
    if body.startswith("[") and body.endswith("]"):
        body = body[1:-1]
    out = []
    for name in re.split(r"(?<!\\),", body):
        parts = [p.strip() for p in name.split("\\,") if p.strip()]
        if not parts:
            continue
        sep = " " if all(p.isascii() for p in parts) else ""
        out.append(sep.join(parts).replace("\\", "").strip())
    return out


def ym(s: str) -> tuple[str, str]:
    """'2024-05' / '2024-11-30' → ('2024', '5')"""
    if not s or s == "null":
        return (TODO, TODO)
    parts = s.split("-")
    y = parts[0]
    m = str(int(parts[1])) if len(parts) > 1 and parts[1].isdigit() else TODO
    return (y, m)


def eom(year: str, month: str) -> str:
    """離任日に使う月末日。'2024','4' → '30'"""
    if not (year.isdigit() and month.isdigit()):
        return TODO
    return str(calendar.monthrange(int(year), int(month))[1])


def yn(rec: dict, key: str) -> str:
    """真偽値を履歴書向けの表記にする。未設定は空欄のまま。

    エクスポートは小文字 true／インポート仕様（V2 CSV項目定義書）は TRUE。どちらも拾う。
    空欄と FALSE は意味が違う（未登録か、否と登録したか）ので潰さない。
    """
    return {"true": "有", "false": "無"}.get(val(rec, key).lower(), "")


def span_ym(rec: dict, frm: str, to: str) -> tuple[str, str, str, str]:
    """期間列を (自年, 自月, 至年, 至月) にする。継続中（9999）は至を「～現在」にする。"""
    fy, fm = ym(val(rec, frm))
    t = val(rec, to)
    if not t:
        return (fy, fm, "", "")
    if t.startswith("9999"):
        return (fy, fm, "～現在", "")
    ty, tm = ym(t)
    return (fy, fm, ty, tm)


def skip_empty(name: str, table: str, rows: list) -> bool:
    """実データのないテーブルはファイルを作らない。末尾の報告に回す。"""
    if rows:
        return False
    _empty.append((name, table))
    return True


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backup(path: Path) -> Path:
    """上書き前の退避。.backup/<日時>/<ファイル名> に残す。"""
    d = BACKUP / datetime.now().strftime("%Y%m%d_%H%M%S")
    d.mkdir(parents=True, exist_ok=True)
    dest = d / path.name
    shutil.copy2(path, dest)
    return dest


def _csv_text(header: list[str], rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def write(name: str, header: list[str], rows: list[list]) -> None:
    load_state()
    if ONLY and name not in ONLY:
        return
    path = OUT / name
    todo = "".join(map(str, [c for r in rows for c in r])).count(TODO)

    if DRY_RUN:
        # 実ファイルと manifest には触らず、差分だけ見せる。
        PREVIEW.mkdir(parents=True, exist_ok=True)
        (PREVIEW / name).write_text(_csv_text(header, rows), encoding="utf-8-sig")
        old = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
        new = _csv_text(header, rows).splitlines()
        d = list(difflib.unified_diff(old, new, fromfile=f"現在/{name}", tofile=f"生成/{name}", lineterm=""))
        print(f"  {name}: {len(old) - 1 if old else 0}行 → {len(rows)}行（★ {todo}個）")
        for line in d:
            print(f"    {line}")
        if not d:
            print("    差分なし")
        return

    OUT.mkdir(parents=True, exist_ok=True)
    if path.exists():
        edited = digest(path) != _manifest.get(name)
        if edited and not (FORCE or _first_run):
            _skipped.append(name)
            print(f"  {name}: 手編集を検出したのでスキップした（上書きするなら --force）")
            return
        if edited:
            print(f"  {name}: 上書き前に {backup(path).parent.name}/ へ退避した")

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    _manifest[name] = digest(path)
    todo = "".join(map(str, [c for r in rows for c in r])).count(TODO)
    print(f"  {name}: {len(rows)}行（★ {todo}個）")


# ---------------------------------------------------------------- 1. 基本情報
def basic_info() -> None:
    rows_src = load("researchers")
    if not rows_src:
        print("  01_基本情報.csv: rm_researchers*.csv が無いので飛ばした")
        return
    r = rows_src[0]
    kana2hira = lambda s: "".join(
        chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s
    )
    sei, mei = val(r, "姓(日本語)"), val(r, "名(日本語)")
    furi = f"{kana2hira(val(r, '姓(カナ)'))}　{kana2hira(val(r, '名(カナ)'))}"
    org = " ".join(x for x in [val(r, "所属名(日本語)"), val(r, "部署名(日本語)"), val(r, "職名(日本語)")] if x)
    # 生年月日・性別・国籍は researchers に列がある（V2 CSV の researchers テーブル）。
    # 登録されていればそれを使い、空のときだけ ★ を出す。
    bd = val(r, "生年月日").split("-")
    by = bd[0] if bd[0] else TODO
    bm = str(int(bd[1])) if len(bd) > 1 and bd[1].isdigit() else TODO
    bdd = str(int(bd[2])) if len(bd) > 2 and bd[2].isdigit() else TODO
    rm_note = "researchmapの登録値。空欄なら手で埋める"
    rows = [
        ["作成日（年）", "", "提出時に記入（様式は「20□□年□□月□□日現在」）。作成日で変わるため★の対象外"],
        ["作成日（月）", "", ""],
        ["作成日（日）", "", ""],
        ["ふりがな", furi, "researchmapのカナ表記から生成"],
        ["戸籍氏名", f"{sei}　{mei}", "researchmapの表記。旧姓・通称の併記が要る様式なら手で直す"],
        ["業績に使用する名前の表記", val(r, "業績に使用する名前の表記"), "researchmapの登録値。業績欄の著者名と揃える"],
        ["通称等の別名", val(r, "通称等の別名(日本語)"), "旧姓・通称。併記が要る様式で使う"],
        ["性別", val(r, "性別") or TODO, rm_note],
        ["アルファベット氏名（ファミリーネーム）", val(r, "姓(英語)").upper(), "様式は大文字表記"],
        ["アルファベット氏名（ファーストネーム）", val(r, "名(英語)"), ""],
        ["アルファベット氏名（ミドルネーム）", "", "該当なしなら空欄"],
        ["生年月日（年）", by, rm_note],
        ["生年月日（月）", bm, ""],
        ["生年月日（日）", bdd, ""],
        ["満年齢", "", "提出時に記入。作成日で変わるため★の対象外"],
        ["国籍", val(r, "国籍・地域") or TODO, rm_note],
        ["メールアドレス", val(r, "公開用メールアドレス"), "researchmapの公開用アドレス。私用アドレスにするか要判断"],
        ["本務先", org, "様式の「現住所以外の連絡先」欄"],
        ["本務先郵便番号", TODO, "本務先のもの。自宅は書かない"],
        ["本務先住所", TODO, "本務先のもの。自宅は書かない"],
        ["本務先電話番号", TODO, "本務先のもの。自宅・携帯は書かない"],
        ["研究者番号", val(r, "研究者番号"), "科研費等の申請で使う。researchmapの登録値"],
        ["ORCID ID", val(r, "ORCID ID"), "researchmapの登録値"],
        ["Researcher ID", val(r, "Researcher ID"), "researchmapの登録値"],
        ["J-Global ID", val(r, "J-Global ID"), "researchmapの登録値"],
        ["researchmapパーマリンク", val(r, "パーマリンク"), "業績一覧のURLとして申請書に書ける"],
    ]
    write("01_基本情報.csv", ["項目", "値", "メモ"], rows)


# ---------------------------------------------------------------- 2. 学歴
# researchmap の education は「期間1レコード」だが、様式は入学行・卒業行に分ける。
# 日付は researchmap が年月までしか持たないため、慣例値（入学=1日／年度末修了=31日）を
# 仮入力し、メモで要確認を示す。
# 高校・交換留学・満期退学などは researchmap に項目がない。末尾に ★ の行を置くので、
# 必要なものを手で足し、不要な行は削除する。
def education() -> None:
    note_day = "日は慣例値（入学=1日／卒業・修了=31日）。学位記・卒業証書で要確認"
    rows = []
    for r in sorted(load("education"), key=lambda x: x.get("年月(From)", "")):
        school = val(r, "学校名(日本語)", "学校名(英語)")
        dept = " ".join(x for x in [val(r, "学部・研究科等(日本語)"),
                                    val(r, "学科等(日本語)")] if x)
        name = f"{school}{dept}"
        # education に「課程」という列は無い。課程名に当たるのは備考欄である。
        course = val(r, "備考(日本語)", "備考(英語)")
        area = val(r, "国・地域")
        fy, fm = ym(val(r, "年月(From)"))
        if fy:
            rows.append([fy, fm, "1", name, course, "入学", area, note_day])
        to = val(r, "年月(To)")
        if to and not to.startswith("9999"):
            ty, tm = ym(to)
            rows.append([ty, tm, eom(ty, tm), name, course, "卒業・修了", area, note_day])
    rows.sort(key=lambda r: (str(r[0]), str(r[1]).zfill(2)))
    rows.append([TODO, TODO, TODO, TODO, "", TODO, "",
                 "researchmap に項目がないもの（高校、交換留学、満期退学など）を手で足す。"
                 "不要なら行ごと削除する"])
    write("02_学歴.csv",
          ["西暦年", "月", "日", "学校名（学部・学科名、研究科・専攻名）", "課程名", "入学・卒業・修了等",
           "国・地域（参考）", "メモ"],
          rows)


# ---------------------------------------------------------------- 3. 学位
# researchmap の学位欄は researchers テーブルにある
# （学位名(日本語)／学位 授与機関(日本語)／学位 取得年月）。
# ただし researchers は1人1行なので学位も1件しか持てない。他の学位は手で足す。
# 種別（学士／修士／博士）と日は researchmap に項目がないので ★ を出す。
def degrees() -> None:
    note = "researchmapの学位欄から生成。種別と日は未登録なので学位記で確認する"
    add = "researchmapは学位を1件しか持てない。他の学位は手で足す。不要なら行ごと削除する"
    rows = []
    for r in load("researchers")[:1]:
        name = val(r, "学位名(日本語)", "学位名(英語)")
        inst = val(r, "学位 授与機関(日本語)", "学位 授与機関(英語)")
        if not (name or inst):
            continue
        y, m = ym(val(r, "学位 取得年月"))
        rows.append([y, m, TODO, TODO, name or TODO, inst or TODO, note])
    rows += [[TODO, TODO, TODO, TODO, TODO, TODO, add] for _ in range(2)]
    write("03_学位.csv", ["西暦年", "月", "日", "種別（学/修/博/専/他）", "学位名", "授与大学名", "メモ"], rows)


# ---------------------------------------------------------------- 4. 職歴
# research_experience（研究職）と teaching_experience（非常勤講師）を1本にまとめる。
# 日付は researchmap が年月までしか持たないが、様式には「日」列がある（記入例も記入済）ため、
# 慣例値（着任=1日／離任=月末）を仮入力し、メモで要確認を示す。
# 様式の「専任・非常勤の別」は researchmap にない項目なので、★ を出して手で埋める。
# 様式の「専任・非常勤の別」は researchmap に項目がないので、常に ★ を出して手で埋める。
# フルタイムでない研究員は非常勤、学振特別研究員は雇用関係がないため区分に該当しない、
# といった判断は所属ごとに違うため、自動では決めない。
EMPLOYMENT: dict[str, tuple[str, str]] = {}
NOTE_DAY = "日は慣例値（着任=1日／離任=月末）。辞令で要確認"
def careers() -> None:
    def span(r: dict) -> tuple:
        """(自年, 自月, 自日, 至年, 至月, 至日) を返す。継続中は至に「～現在」。"""
        fy, fm = ym(val(r, "年月(From)"))
        to = val(r, "年月(To)")
        if to.startswith("9999"):
            return (fy, fm, "1", "～現在", "", "")
        ty, tm = ym(to)
        return (fy, fm, "1", ty, tm, eom(ty, tm))

    rows = []
    for r in sorted(load("research_experience"), key=lambda x: x.get("年月(From)", "")):
        org = val(r, "所属(日本語)")
        post = " ".join(x for x in [org, val(r, "部署(日本語)"), val(r, "職名(日本語)")] if x)
        kind, memo = EMPLOYMENT.get(org, (TODO, "区分（専任／非常勤）を要確認"))
        rows.append(list(span(r)) + [kind, post,
                                     val(r, "職階"), val(r, "称号(日本語)", "称号(英語)"),
                                     val(r, "国・地域"), val(r, "備考(日本語)", "備考(英語)"),
                                     "／".join([memo, NOTE_DAY])])

    for r in sorted(load("teaching_experience"), key=lambda x: x.get("年月(From)", "")):
        inst = val(r, "機関名(日本語)")
        subj = val(r, "科目(日本語)")
        memo = "職名はresearchmap未登録のため補記／" + NOTE_DAY
        # teaching_experience に職階・称号はない。科目区分と概要は備考にまとめる。
        note = "／".join(x for x in [
            f"科目区分: {val(r, '科目区分')}" if val(r, "科目区分") else "",
            val(r, "概要(日本語)", "概要(英語)"),
        ] if x)
        rows.append(list(span(r)) + ["非常勤", f"{inst} 非常勤講師　担当科目：{subj}",
                                     "", "", val(r, "国・地域"), note, memo])

    rows.append([TODO, TODO, TODO, TODO, TODO, TODO, TODO, "", "", "", "", "",
                 "researchmap に未登録の職歴があれば手で足す。不要なら行ごと削除する"])
    rows.sort(key=lambda r: (str(r[0]), str(r[1]).zfill(2)))
    write("04_職歴.csv",
          ["自_西暦年", "自_月", "自_日", "至_西暦年", "至_月", "至_日", "専任・非常勤の別", "勤務先及び職名",
           "職階（参考）", "称号（参考）", "国・地域（参考）", "備考（参考）", "メモ"],
          rows)


# ---------------------------------------------------------------- 5. 所属学会
# association_memberships は在籍期間の列（年月(From)/(To)）を持つ。researchmap 側で
# 未入力なら空で出てくるので、その場合だけ ★ を出す。役職の列は無い。
# 入会年月の手がかりを学会名ごとに書いておくと、メモ欄に出る。
# （その学会で最初に発表した年月が入会時期の下限になることが多い）
JOINED_HINT: dict[str, str] = {}


def societies() -> None:
    # 様式は年月までで日は求められない。役職は researchmap に項目がないので手で足す。
    base = "継続中は至に「～現在」と書く"
    unreg = "入会年月がresearchmap未入力。researchmap側に入れると次回から反映される"
    rows = []
    for r in load("association_memberships"):
        name = val(r, "所属学協会名(日本語)", "所属学協会名(英語)")
        fy, fm, ty, tm = span_ym(r, "年月(From)", "年月(To)")
        note = base if val(r, "年月(From)") else unreg
        if not val(r, "年月(From)"):
            fy = fm = TODO
        memo = "／".join(x for x in [note, JOINED_HINT.get(name, "")] if x)
        # 役職は researchmap に項目がない。全行に ★ を出すと埋める対象が膨らむので空で置く。
        rows.append([fy, fm, ty, tm, name, "", val(r, "URL"), memo])
    rows.append(["", "", "", "", "（未登録の学会があれば追記）", "", "",
                 "researchmap に未登録の学会があれば手で足す。不要なら行ごと削除する"])
    write("05_所属学会.csv",
          ["自_西暦年", "自_月", "至_西暦年", "至_月", "学会名", "役職", "URL（参考）", "メモ"], rows)


# ---------------------------------------------------------------- 6. 専門分野
# research_areas（研究分野）と research_interests（研究キーワード）を合わせて並べる。
# 履歴書では自分の言葉に直すことが多いので、メモでそれを促す。
def fields() -> None:
    kws = []
    for table in ("research_areas", "research_interests"):
        for r in load(table):
            k = val(r, "キーワード(日本語)", "小分類名(日本語)", "キーワード(英語)")
            if k and k not in kws:
                kws.append(k)
    text = "、".join(kws) if kws else TODO
    write("06_専門分野.csv", ["専門分野", "メモ"],
          [[text, "researchmapのキーワードを並べたもの。履歴書用の表現に書き直してよい"]])


# ---------------------------------------------------------------- 7. 学術論文
# 様式の「発行所」は researchmap の出版者・発行元。未登録分は誌名から補記する。
# 誌名から発行所を補える場合はここに書いておく（例: "紀要名": "大学名"）。
PUBLISHER_FALLBACK: dict[str, str] = {}


def papers() -> None:
    rows = []
    for r in sorted(load("published_papers"), key=lambda x: x.get("出版年月", "")):
        y, m = ym(val(r, "出版年月"))
        authors = people(val(r, "著者(日本語)", "著者(英語)"))
        kind = "単著" if len(authors) == 1 else "共著"
        journal = val(r, "誌名(日本語)", "誌名(英語)")
        pub = val(r, "出版者・発行元(日本語)", "出版者・発行元(英語)")
        memo = []
        if not pub:
            pub = PUBLISHER_FALLBACK.get(journal, "")
            memo.append("発行所はresearchmap未登録のため誌名から補記。要確認" if pub else "発行所★")
            if not pub:
                pub = TODO
        vol, no = val(r, "巻"), val(r, "号")
        pages = "-".join(x for x in [val(r, "開始ページ"), val(r, "終了ページ")] if x)
        ref = "　".join(x for x in [f"{vol}巻" if vol else "", f"{no}号" if no else "", f"{pages}頁" if pages else ""] if x)
        rows.append([y, m, kind, val(r, "タイトル(日本語)", "タイトル(英語)"), journal, pub,
                     ref, "、".join(authors),
                     yn(r, "査読の有無"), yn(r, "招待の有無"), val(r, "掲載種別"),
                     yn(r, "国際・国内誌"), yn(r, "国際共著"), val(r, "記述言語"),
                     "、".join(people(val(r, "担当区分"))), val(r, "DOI"),
                     val(r, "ISSN"), val(r, "eISSN"), val(r, "URL", "URL2"),
                     yn(r, "主要な業績かどうか"), val(r, "概要(日本語)", "概要(英語)"),
                     "／".join(memo)])
    write("07_学術論文.csv",
          ["西暦年", "月", "単著・共著の別", "論文名", "掲載誌名", "発行所", "巻号頁（参考）", "著者（参考）",
           "査読（参考）", "招待（参考）", "掲載種別（参考）", "国際・国内誌（参考）", "国際共著（参考）",
           "記述言語（参考）", "担当区分（参考）", "DOI", "ISSN", "eISSN", "URL（参考）",
           "主要業績（参考）", "概要（参考）", "メモ"],
          rows)


# ---------------------------------------------------------------- 8. 著書・翻訳
ROLE = {
    "contributor": "共著（分担執筆）",
    "joint_editor": "共編著",
    "sole_author": "単著",
    "joint_author": "共著",
    "editor": "編著",
    "translator": "翻訳",
}


def books() -> None:
    rows = []
    for r in sorted(load("books_etc"), key=lambda x: x.get("出版年月", "")):
        y, m = ym(val(r, "出版年月"))
        role = ROLE.get(val(r, "担当区分"), val(r, "担当区分") or TODO)
        title = val(r, "タイトル(日本語)", "タイトル(英語)")
        part = val(r, "担当範囲(日本語)")
        name = f"{title}　{part}" if part else title
        pages = val(r, "担当ページ")
        # 共著者は books_etc の「著者(翻訳者)」に入っている。★ を置かずそのまま使う。
        authors = people(val(r, "著者(翻訳者)(日本語)", "著者(翻訳者)(英語)"))
        memo = "" if authors else "共著者がresearchmap未登録（様式は備考欄に共著名を記載）"
        note = "／".join(x for x in [
            f"共著者：{'、'.join(authors)}" if authors else f"共著者：{TODO}",
            f"担当 {pages}頁" if pages else "",
        ] if x)
        rows.append([y, m, role, name, val(r, "出版者・発行元(日本語)", "出版者・発行元(英語)"), note,
                     "、".join(authors), "、".join(people(val(r, "原著者(日本語)", "原著者(英語)"))),
                     val(r, "著書種別"), yn(r, "査読の有無"), yn(r, "国際共著"),
                     val(r, "記述言語"), val(r, "総ページ数"), val(r, "ISBN"), val(r, "DOI"),
                     val(r, "URL", "URL2"), yn(r, "主要な業績かどうか"),
                     val(r, "概要(日本語)", "概要(英語)"), memo])
    write("08_著書・翻訳.csv",
          ["西暦年", "月", "単著・共著の別", "書名（＋執筆箇所の題目）", "出版社", "備考",
           "著者（参考）", "原著者（参考）", "著書種別（参考）", "査読（参考）", "国際共著（参考）",
           "記述言語（参考）", "総ページ数", "ISBN", "DOI", "URL（参考）",
           "主要業績（参考）", "概要（参考）", "メモ"], rows)


# ---------------------------------------------------------------- 9. 講演・口頭発表
# researchmap V2 CSV項目定義書 3.14「講演・口頭発表等」の会議種別9値。
# 辞書に無い値を入れると master に英語コードが漏れるので、仕様の全値を網羅しておく。
KIND = {
    "oral_presentation": "口頭発表",
    "invited_oral_presentation": "招待講演",
    "keynote_oral_presentation": "基調講演",
    "poster_presentation": "ポスター発表",
    "public_symposium": "公開シンポジウム",
    "nominated_symposium": "シンポジウム（指名）",
    "public_discourse": "公開講演",
    "media_report": "メディア報道",
    "others": "その他",
}


def presentations() -> None:
    rows = []
    recs = load("presentations")

    def when(r: dict) -> str:
        return val(r, "発表年月日", "開催年月日(From)")

    for r in sorted(recs, key=when):
        y, m = ym(when(r))
        title = val(r, "タイトル(日本語)", "タイトル(英語)")
        conf = val(r, "会議名(日本語)", "会議名(英語)")
        raw_kind = val(r, "会議種別")
        kind = KIND.get(raw_kind, raw_kind)
        # エクスポートは小文字 true、インポート仕様（V2 CSV項目定義書）は TRUE。どちらも拾う。
        invited = "招待" if val(r, "招待の有無").lower() == "true" else ""
        memo = []
        if raw_kind and raw_kind not in KIND:
            memo.append(f"会議種別「{raw_kind}」がKIND未登録。要確認")
        if not val(r, "発表年月日"):
            memo.append("発表年月日が未登録のため開催年月日で代替。要確認")
        if invited and val(r, "会議種別") in ("invited_oral_presentation", "public_discourse"):
            memo.append("様式の注記により題目の前に「（講演）」を付けるか要判断")
        period = "～".join(x for x in [val(r, "開催年月日(From)"), val(r, "開催年月日(To)")] if x)
        rows.append([y, m, title, conf, kind, invited,
                     "、".join(people(val(r, "講演者(日本語)", "講演者(英語)"))),
                     val(r, "主催者(日本語)", "主催者(英語)"),
                     val(r, "開催地(日本語)", "開催地(英語)"), val(r, "国・地域"),
                     yn(r, "国際・国内会議"), yn(r, "国際共著"), val(r, "記述言語"),
                     period, val(r, "URL", "URL2"), yn(r, "主要な業績かどうか"),
                     val(r, "概要(日本語)", "概要(英語)"), "／".join(memo)])
    write("09_講演・口頭発表.csv",
          ["西暦年", "月", "題目又は作品名、記録名", "学会名等", "種別（参考）", "招待（参考）",
           "講演者（参考）", "主催者（参考）", "開催地（参考）", "国・地域（参考）",
           "国際・国内会議（参考）", "国際共著（参考）", "記述言語（参考）", "開催期間（参考）",
           "URL（参考）", "主要業績（参考）", "概要（参考）", "メモ"], rows)


# ---------------------------------------------------------------- その他（様式外）
def misc() -> None:
    """書評・翻訳論文・連載等。様式のどの欄に載せるか（または載せないか）を判断するための一覧。

    カラム構成は published_papers と同一なので、拾う列も揃える。
    どの欄に載せるかを決めたら 07 か 08 へ転記する。
    """
    rows = []
    for r in sorted(load("misc"), key=lambda x: x.get("出版年月", "")):
        y, m = ym(val(r, "出版年月"))
        vol, no = val(r, "巻"), val(r, "号")
        pages = "-".join(x for x in [val(r, "開始ページ"), val(r, "終了ページ")] if x)
        ref = "　".join(x for x in [f"{vol}巻" if vol else "", f"{no}号" if no else "",
                                    f"{pages}頁" if pages else ""] if x)
        rows.append([y, m, val(r, "タイトル(日本語)", "タイトル(英語)"),
                     val(r, "誌名(日本語)", "誌名(英語)"), val(r, "掲載種別"), TODO,
                     "、".join(people(val(r, "著者(日本語)", "著者(英語)"))),
                     val(r, "出版者・発行元(日本語)", "出版者・発行元(英語)"), ref,
                     yn(r, "査読の有無"), yn(r, "招待の有無"),
                     yn(r, "国際・国内誌"), yn(r, "国際共著"), val(r, "記述言語"),
                     "、".join(people(val(r, "担当区分"))), val(r, "DOI"),
                     val(r, "ISSN"), val(r, "eISSN"), val(r, "URL", "URL2"),
                     yn(r, "主要な業績かどうか"), val(r, "概要(日本語)", "概要(英語)")])
    write("10_その他（掲載欄の判断用）.csv",
          ["西暦年", "月", "タイトル", "誌名", "researchmap掲載種別",
           "履歴書に載せる欄（6学術論文／7著書・翻訳／載せない）",
           "著者（参考）", "発行所（参考）", "巻号頁（参考）", "査読（参考）", "招待（参考）",
           "国際・国内誌（参考）", "国際共著（参考）", "記述言語（参考）", "担当区分（参考）",
           "DOI", "ISSN", "eISSN", "URL（参考）", "主要業績（参考）", "概要（参考）"],
          rows)


# ---------------------------------------------------------------- 11. 受賞
# awards は様式の受賞欄に対応する。従来このテーブルを一切読んでいなかった。
def awards() -> None:
    rows = []
    for r in sorted(load("awards"), key=lambda x: x.get("受賞年月", "")):
        y, m = ym(val(r, "受賞年月"))
        rows.append([y, m, val(r, "賞名(日本語)", "賞名(英語)"),
                     val(r, "授与機関(日本語)", "授与機関(英語)"),
                     val(r, "受賞区分"), val(r, "受賞国・地域"),
                     "、".join(people(val(r, "受賞者・グループ(日本語)", "受賞者・グループ(英語)"))),
                     val(r, "タイトル(日本語)", "タイトル(英語)"),
                     val(r, "URL"), yn(r, "主要な業績かどうか"),
                     val(r, "概要(日本語)", "概要(英語)")])
    if skip_empty("11_受賞.csv", "awards", rows):
        return
    write("11_受賞.csv",
          ["西暦年", "月", "賞名", "授与機関", "受賞区分（参考）", "受賞国・地域（参考）",
           "受賞者（参考）", "対象業績（参考）", "URL（参考）", "主要業績（参考）", "概要（参考）"],
          rows)


# ---------------------------------------------------------------- 12. 研究課題
# research_projects は科研費等の業績報告で要になる。従来このテーブルも読んでいなかった。
# 題目に当たる列は「研究課題名」ではなく「タイトル」である（TITLE_COLS の注記を参照）。
def projects() -> None:
    rows = []
    for r in sorted(load("research_projects"), key=lambda x: x.get("研究期間(From)", "")):
        fy, fm, ty, tm = span_ym(r, "研究期間(From)", "研究期間(To)")
        rows.append([fy, fm, ty, tm, val(r, "タイトル(日本語)", "タイトル(英語)"),
                     val(r, "提供機関(日本語)", "提供機関(英語)"),
                     val(r, "制度名(日本語)", "制度名(英語)"),
                     val(r, "研究種目(日本語)", "研究種目(英語)"),
                     val(r, "課題番号"), val(r, "担当区分"), val(r, "資金種別"),
                     val(r, "配分額(総額)"), val(r, "配分額(直接経費)"), val(r, "配分額(間接経費)"),
                     "、".join(people(val(r, "担当研究者(日本語)", "担当研究者(英語)"))),
                     val(r, "研究機関名(日本語)", "研究機関名(英語)"),
                     yn(r, "国際共同研究"), val(r, "URL"), yn(r, "主要な業績かどうか"),
                     val(r, "研究概要(日本語)", "研究概要(英語)")])
    if skip_empty("12_研究課題.csv", "research_projects", rows):
        return
    write("12_研究課題.csv",
          ["自_西暦年", "自_月", "至_西暦年", "至_月", "研究課題名", "提供機関", "制度名",
           "研究種目", "課題番号", "担当区分", "資金種別",
           "配分額（総額）", "配分額（直接経費）", "配分額（間接経費）",
           "担当研究者（参考）", "研究機関名（参考）", "国際共同研究（参考）", "URL（参考）",
           "主要業績（参考）", "研究概要（参考）"],
          rows)


# ---------------------------------------------------------------- 13. 委員歴
def committees() -> None:
    rows = []
    for r in sorted(load("committee_memberships"), key=lambda x: x.get("年月(From)", "")):
        fy, fm, ty, tm = span_ym(r, "年月(From)", "年月(To)")
        rows.append([fy, fm, ty, tm, val(r, "団体名(日本語)", "団体名(英語)"),
                     val(r, "委員名(日本語)", "委員名(英語)"), val(r, "団体区分"),
                     val(r, "特記事項(日本語)", "特記事項(英語)"), yn(r, "主要な業績かどうか")])
    if skip_empty("13_委員歴.csv", "committee_memberships", rows):
        return
    write("13_委員歴.csv",
          ["自_西暦年", "自_月", "至_西暦年", "至_月", "団体名", "委員名", "団体区分（参考）",
           "特記事項（参考）", "主要業績（参考）"],
          rows)


# ---------------------------------------------------------------- 14. 社会貢献・学術貢献
# social_contribution（社会貢献）と academic_contribution（学術貢献）は列構成が近いので1本にする。
def contributions() -> None:
    rows = []
    for r in sorted(load("social_contribution"), key=lambda x: x.get("年月日(From)", "")):
        fy, fm, ty, tm = span_ym(r, "年月日(From)", "年月日(To)")
        rows.append(["社会貢献", fy, fm, ty, tm, val(r, "タイトル(日本語)", "タイトル(英語)"),
                     val(r, "役割"), val(r, "種別"),
                     val(r, "主催者・発行元(日本語)", "主催者・発行元(英語)"),
                     val(r, "イベント・番組・新聞雑誌名(日本語)", "イベント・番組・新聞雑誌名(英語)"),
                     val(r, "場所・掲載箇所(日本語)", "場所・掲載箇所(英語)"), val(r, "対象"),
                     "", val(r, "URL"), yn(r, "主要な業績かどうか"),
                     val(r, "概要(日本語)", "概要(英語)")])
    for r in sorted(load("academic_contribution"), key=lambda x: x.get("実施年月日(From)", "")):
        fy, fm, ty, tm = span_ym(r, "実施年月日(From)", "実施年月日(To)")
        rows.append(["学術貢献", fy, fm, ty, tm, val(r, "タイトル(日本語)", "タイトル(英語)"),
                     val(r, "役割"), val(r, "種別"),
                     val(r, "主催者・責任者(日本語)", "主催者・責任者(英語)"), "",
                     val(r, "場所(日本語)", "場所(英語)"), "",
                     yn(r, "国際学術貢献"), val(r, "URL"), yn(r, "主要な業績かどうか"),
                     val(r, "概要(日本語)", "概要(英語)")])
    rows.sort(key=lambda r: (str(r[1]), str(r[2]).zfill(2)))
    if skip_empty("14_社会貢献・学術貢献.csv", "social_contribution / academic_contribution", rows):
        return
    write("14_社会貢献・学術貢献.csv",
          ["区分", "自_西暦年", "自_月", "至_西暦年", "至_月", "タイトル", "役割", "種別",
           "主催者", "イベント・媒体名（参考）", "場所・掲載箇所（参考）", "対象（参考）",
           "国際学術貢献（参考）", "URL（参考）", "主要業績（参考）", "概要（参考）"],
          rows)


# ---------------------------------------------------------------- 15. メディア報道
def media() -> None:
    rows = []
    for r in sorted(load("media_coverage"), key=lambda x: x.get("報道年月", "")):
        y, m = ym(val(r, "報道年月"))
        rows.append([y, m, val(r, "タイトル(日本語)", "タイトル(英語)"),
                     val(r, "番組・新聞雑誌名(日本語)", "番組・新聞雑誌名(英語)"),
                     val(r, "発行元・放送局(日本語)", "発行元・放送局(英語)"),
                     val(r, "執筆者"), val(r, "種別"),
                     val(r, "掲載箇所(日本語)", "掲載箇所(英語)"),
                     val(r, "URL"), yn(r, "主要な業績かどうか"),
                     val(r, "概要(日本語)", "概要(英語)")])
    if skip_empty("15_メディア報道.csv", "media_coverage", rows):
        return
    write("15_メディア報道.csv",
          ["西暦年", "月", "タイトル", "番組・新聞雑誌名", "発行元・放送局", "執筆者（参考）",
           "種別（参考）", "掲載箇所（参考）", "URL（参考）", "主要業績（参考）", "概要（参考）"],
          rows)


# ---------------------------------------------------------------- 16. 作品等
def artworks() -> None:
    rows = []
    for r in sorted(load("works"), key=lambda x: x.get("年月(From)", "")):
        fy, fm, ty, tm = span_ym(r, "年月(From)", "年月(To)")
        rows.append([fy, fm, ty, tm, val(r, "作品名(日本語)", "作品名(英語)"),
                     "、".join(people(val(r, "発表者(日本語)", "発表者(英語)"))),
                     val(r, "作品分類"), val(r, "発表場所(日本語)", "発表場所(英語)"),
                     yn(r, "国際共著"), val(r, "DOI"), val(r, "URL", "URL2"),
                     yn(r, "主要な業績かどうか"), val(r, "発表内容(日本語)", "発表内容(英語)")])
    if skip_empty("16_作品.csv", "works", rows):
        return
    write("16_作品.csv",
          ["自_西暦年", "自_月", "至_西暦年", "至_月", "作品名", "発表者", "作品分類（参考）",
           "発表場所（参考）", "国際共著（参考）", "DOI", "URL（参考）", "主要業績（参考）",
           "発表内容（参考）"],
          rows)


# ---------------------------------------------------------------- 17. 産業財産権
def ipr() -> None:
    rows = []
    for r in sorted(load("industrial_property_rights"), key=lambda x: x.get("出願日", "")):
        rows.append([val(r, "産業財産権の種類"),
                     val(r, "産業財産権名(日本語)", "産業財産権名(英語)"),
                     "、".join(people(val(r, "発明者/考案者/創作者(日本語)",
                                          "発明者/考案者/創作者(英語)"))),
                     val(r, "出願番号"), val(r, "出願日"),
                     val(r, "出願人(機関)(日本語)", "出願人(機関)(英語)"),
                     val(r, "公開番号"), val(r, "公開日"), val(r, "公表番号"), val(r, "公表日"),
                     val(r, "特許番号/登録番号"), val(r, "登録日"), val(r, "発行日"),
                     val(r, "権利者(日本語)", "権利者(英語)"),
                     val(r, "出願国"), val(r, "取得国"), val(r, "URL"),
                     yn(r, "主要な業績かどうか"), val(r, "概要(日本語)", "概要(英語)")])
    if skip_empty("17_産業財産権.csv", "industrial_property_rights", rows):
        return
    write("17_産業財産権.csv",
          ["種類", "名称", "発明者・考案者・創作者", "出願番号", "出願日", "出願人（機関）",
           "公開番号", "公開日", "公表番号", "公表日", "特許番号・登録番号", "登録日", "発行日",
           "権利者", "出願国", "取得国", "URL（参考）", "主要業績（参考）", "概要（参考）"],
          rows)


# ---------------------------------------------------------------- 18. その他
def others() -> None:
    rows = []
    for r in sorted(load("others"), key=lambda x: x.get("年月(From)", "")):
        fy, fm, ty, tm = span_ym(r, "年月(From)", "年月(To)")
        rows.append([fy, fm, ty, tm, val(r, "タイトル(日本語)", "タイトル(英語)"),
                     val(r, "内容(日本語)", "内容(英語)"), yn(r, "主要な業績かどうか")])
    if skip_empty("18_その他.csv", "others", rows):
        return
    write("18_その他.csv",
          ["自_西暦年", "自_月", "至_西暦年", "至_月", "タイトル", "内容", "主要業績（参考）"],
          rows)


# ---------------------------------------------------------------- pending の点検と掃除
def pending_status() -> int:
    """pending 各行が未取り込み（NEW）か取り込み済み（IMPORTED）かを一覧する。"""
    tables = pending_tables()
    if not tables:
        print(f"pending はない（{PENDING}）")
        return 0
    total_imported = 0
    for t in tables:
        load(t)  # PENDING_STATS を埋める
        st = PENDING_STATS.get(t, {"new": [], "imported": []})
        print(f"\n{pending_path(t).name}")
        cols = TITLE_COLS.get(t, DEFAULT_TITLE_COLS)
        for label, recs in (("NEW     ", st["new"]), ("IMPORTED", st["imported"])):
            for r in recs:
                print(f"  {label}  {val(r, *cols)[:60]}")
        total_imported += len(st["imported"])
    if total_imported:
        print(f"\nIMPORTED が {total_imported}件ある。--sweep-pending で pending/imported/ へ退避できる。")
    return total_imported


def sweep_pending() -> None:
    """取り込み済みの行を pending から imported/ へ移す。"""
    stamp = datetime.now().strftime("%Y%m%d")
    moved = 0
    for t in pending_tables():
        load(t)
        st = PENDING_STATS.get(t, {"new": [], "imported": []})
        if not st["imported"]:
            continue
        path = pending_path(t)
        header = read_rm_csv(path)[0]
        IMPORTED.mkdir(parents=True, exist_ok=True)
        dest = IMPORTED / f"{stamp}_{path.name}"
        with dest.open("a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            if dest.stat().st_size == 0:
                w.writerow([t])
                w.writerow(header)
            for r in st["imported"]:
                w.writerow([r.get(c, "null") for c in header])
        if st["new"]:
            with path.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow([t])
                w.writerow(header)
                for r in st["new"]:
                    w.writerow([r.get(c, "null") for c in header])
        else:
            path.unlink()
        moved += len(st["imported"])
        print(f"  {path.name}: {len(st['imported'])}行を {dest.name} へ退避（残り {len(st['new'])}行）")
    print(f"退避した行: {moved}件" if moved else "退避するものはない")


def report_pending() -> None:
    """通常実行の末尾で pending の状況を必ず知らせる。"""
    if not PENDING_STATS:
        return
    new = sum(len(s["new"]) for s in PENDING_STATS.values())
    imp = sum(len(s["imported"]) for s in PENDING_STATS.values())
    print(f"\npending: {new + imp}件（NEW {new} / IMPORTED {imp}）")
    if imp:
        print("  IMPORTED は researchmap 側に取り込み済み。--sweep-pending で退避できる。")


def main(argv: list[str] | None = None) -> None:
    global FORCE, DRY_RUN, ONLY
    ap = argparse.ArgumentParser(description="researchmap のCSVから履歴書マスターを生成する")
    ap.add_argument("--force", action="store_true",
                    help="手編集されたファイルも上書きする（前に master/.backup/ へ退避）")
    ap.add_argument("--dry-run", action="store_true",
                    help="実ファイルを書かず master/.preview/ に生成して差分を表示する")
    ap.add_argument("--only", action="append", default=[],
                    help="生成するマスターCSVを絞る（ファイル名。複数指定可）")
    ap.add_argument("--src", type=Path,
                    help="入力ディレクトリを差し替える（検証用。既定は cv/）")
    ap.add_argument("--pending-status", action="store_true",
                    help="pending 各行が未取り込みか取り込み済みかを一覧する")
    ap.add_argument("--sweep-pending", action="store_true",
                    help="取り込み済みの pending 行を pending/imported/ へ退避する")
    args = ap.parse_args(argv)

    if args.src:
        rebind(args.src.resolve())
    FORCE = args.force
    DRY_RUN = args.dry_run
    ONLY = set(args.only)

    if args.pending_status:
        pending_status()
        return
    if args.sweep_pending:
        sweep_pending()
        return

    load_state()
    print(f"出力先: {OUT}")
    basic_info()
    education()
    degrees()
    careers()
    societies()
    fields()
    papers()
    books()
    presentations()
    misc()
    awards()
    projects()
    committees()
    contributions()
    media()
    artworks()
    ipr()
    others()
    if _empty:
        print("\nresearchmap に登録がないため生成しなかったもの:")
        for name, table in _empty:
            print(f"  - {name}（{table}）")
    report_pending()
    if DRY_RUN:
        print(f"\n--dry-run のため実ファイルは変更していない（生成物は {PREVIEW}）。")
        return
    MANIFEST.write_text(json.dumps(_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if _skipped:
        print("\n手編集を検出してスキップしたファイル:")
        for n in _skipped:
            print(f"  - {n}")
        print("記入内容をスクリプト側に取り込むか、--force で上書きする（上書き前に .backup/ へ退避する）。")
    print(f"\n{TODO} が入っているセルを埋めれば履歴書に転記できる。")


if __name__ == "__main__":
    main()
