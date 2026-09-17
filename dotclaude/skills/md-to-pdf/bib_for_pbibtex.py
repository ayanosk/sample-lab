#!/usr/bin/env python3
"""日本語著者名を pBibTeX 向けに直した .bib の複製を作る。

## なぜ必要か

日本語の人名は、書誌エンジンによって期待される区切り方が違う。

    書き方          biblatex   citeproc   pBibTeX(ipsjunsrt 等)
    {山田太郎}      山田太郎   山田太郎   山田太郎
    {山田 太郎}     太郎 ←誤  太郎 ←誤   山田太郎
    {山田, 太郎}    山田太郎   山田太郎   太郎山田 ←誤

Zotero(Better BibTeX) は姓・名を分けて持つため `{山田, 太郎}` を出力する。
これは biblatex と citeproc では正しいが、学会配布の日本語 .bst では姓名が
反転してしまう。そこで natbib(pBibTeX) 経路のときだけ、CJK を含む人名の
「姓, 名」を「姓名」に詰めた複製を作って、そちらを \\bibliography に渡す。

**元の .bib は変更しない。** 欧語名（Smith, John）はそのまま残す。

Usage: bib_for_pbibtex.py <入力.bib> <出力.bib>
"""
import re
import sys

# ひらがな・カタカナ・漢字・全角記号
CJK = re.compile(r"[々぀-ヿ㐀-䶿一-鿿豈-﫿]")
# Zotero は 1フィールド1行で出す。author/editor/translator を対象にする。
FIELD = re.compile(r"^(\s*(?:author|editor|translator)\s*=\s*[{\"])(.*?)([}\"],?\s*)$",
                   re.IGNORECASE)


def join_japanese(name):
    """「姓, 名」形式の日本語人名を「姓名」に詰める。欧語名はそのまま返す。"""
    if not CJK.search(name):
        return name
    m = re.match(r"^\s*([^,]+?)\s*,\s*(.+?)\s*$", name)
    if not m:
        return name.strip()
    return m.group(1) + m.group(2)


def convert_value(value):
    return " and ".join(join_japanese(n) for n in value.split(" and "))


def main():
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    src, dst = sys.argv[1], sys.argv[2]
    changed = 0
    out = []
    with open(src, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = FIELD.match(line.rstrip("\n"))
            if m:
                new = convert_value(m.group(2))
                if new != m.group(2):
                    changed += 1
                out.append(m.group(1) + new + m.group(3) + "\n")
            else:
                out.append(line)
    with open(dst, "w", encoding="utf-8") as f:
        f.writelines(out)
    print("pBibTeX 向けに日本語人名を %d 件詰めました: %s" % (changed, dst), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
