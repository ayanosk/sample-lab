#!/usr/bin/env python3
"""Obsidian Markdown を pandoc が正しく解釈できる形に正規化する。

Obsidian のノートは (1) 見出しの直前に空行が無く箇条書きに吸収される,
(2) リスト内の ```fence``` がタブ字下げやリスト記号付き(- ```xml)のため
コードブロックとして認識されずインラインに潰れる, という2つの癖で
pandoc 変換が壊れる。ここでその2点だけを機械的に補正する。
本文の文言は一切変更しない。

Usage: python3 normalize.py <in.md> <out.md>
"""
import re
import sys

# 行頭の空白＋任意のリスト記号("- " 等)に続く ``` を fence とみなす
FENCE = re.compile(r"^\s*(?:[-*+]\s+)?```+(.*)$")


def fence_lang(line):
    m = FENCE.match(line)
    return None if m is None else m.group(1).strip()


def is_heading(line):
    return re.match(r"^\s*#{1,6}\s", line) is not None


def normalize(src):
    out = []
    in_fence = False
    for i, line in enumerate(src):
        lang = fence_lang(line)
        if lang is not None:
            if not in_fence:
                if out and out[-1].strip() != "":
                    out.append("")            # 開始 fence の前に空行
                out.append("```" + lang)       # リスト記号・字下げを外して列0へ
                in_fence = True
            else:
                out.append("```")
                in_fence = False
                if i + 1 < len(src) and src[i + 1].strip() != "":
                    out.append("")            # 終了 fence の後に空行
            continue
        if in_fence:
            # markdown のネスト用タブを外し、コード本来の空白字下げは残す
            if "\t" in line:
                line = line[line.rindex("\t") + 1:]
            out.append(line)
            continue
        if is_heading(line):
            if out and out[-1].strip() != "":
                out.append("")               # 見出しの前に空行 → 箇条書き吸収を防ぐ
            out.append(line.lstrip())
            if i + 1 < len(src) and src[i + 1].strip() != "":
                out.append("")
            continue
        out.append(line)
    return out


def main():
    src = open(sys.argv[1], encoding="utf-8").read().split("\n")
    open(sys.argv[2], "w", encoding="utf-8").write("\n".join(normalize(src)))


if __name__ == "__main__":
    main()
