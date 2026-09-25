#!/usr/bin/env python3
"""SVG図の文字が、スライド上で実際に何pxで描かれるかを検査する。

## なぜ必要か

SVGの `font-size` は viewBox のユーザ単位であって、スライド上のpxではない。
図はスライドの枠に合わせて縮小されるので、実際の見え方は

    実効px = 図中の font-size × min(枠幅/viewBox幅, 枠高/viewBox高)

になる。viewBox が枠より大きいほど字は小さくなる。とくに**縦長の図は
高さで律速される**ため、幅だけ見て「収まっている」と判断すると字が潰れる。

実例（academic-intl で計測）:

    three-layer-architecture.svg  viewBox 1240×660 → 倍率0.70 → font 12 が実効 8.4px
    anchor-choice.svg             viewBox 1180×230 → 倍率0.99 → font 17 が実効16.8px

本文32pxに対して 8.4px は1/4以下で、会場の後方からは読めない。
この検査を通していれば、図を書いた時点で分かる。

## 使い方

    python3 .claude/skills/build-slide/scripts/check_svg_text.py FIG.svg [...]        # SVGを直接
    python3 .claude/skills/build-slide/scripts/check_svg_text.py deck.md              # デッキが参照する図を全部
    python3 .claude/skills/build-slide/scripts/check_svg_text.py figures/            # ディレクトリ内を全部

    --theme academic-ja|academic-intl 枠の大きさと本文サイズ（.md指定時は自動判定）
    --full                           fig-full スライド前提で判定（.md指定時は自動判定）
    --floor-ratio 0.6                本文に対する下限比。既定0.6
    --fix                            下限を満たすよう font-size を一律に拡大する
    --quiet                          違反だけ出す

違反があると終了コード1。build_marp.sh がこれを警告に使う。

## --fix の限界

font-size を一律k倍するだけなので、**図形の中の文字は枠からはみ出しうる**。
幾何は変えない（変えれば相対関係が元に戻り無意味になる）。余白の広い図なら
そのまま通るが、適用後は必ず目視すること。恒久的な対処は、図を作る時点で
下の「作図時の目安」に従うことである。

## 作図時の目安

viewBox の幅を W とすると、図中の最小フォントは次以上にする。

    academic-ja    (本文29px, 枠1208×560) … 最小 font-size ≧ 17.4 × W / min(1208, 560×W/H)
    academic-intl  (本文32px, 枠1168×460) … 最小 font-size ≧ 19.2 × W / min(1168, 460×W/H)

単純化した実用則: **viewBox を枠と同じ大きさで作り（academic-ja なら 1208×560 以内、
academic-intl なら 1168×460 以内）、図中の最小フォントを 18px / 20px 以上にする。**
こうすれば倍率が1.0になり、viewBox の数字がそのまま実効pxになる。
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

# ── スライド上で図に与えられる枠（px） ───────────────────────────
# 幅  = スライド幅 − 左右padding（テーマCSSの section padding）
# 高さ = テーマCSSの section img { max-height }
#   fig-full は padding が変わり max-height が 100% になるので、
#   h1 とラベルの分を引いた実測に近い値を別に持つ。
THEMES = {
    # theme            body  枠(通常)      枠(fig-full)
    "academic-ja":   {"body": 29, "frame": (1208, 560), "frame_full": (1220, 660)},
    "academic-intl": {"body": 32, "frame": (1168, 460), "frame_full": (1200, 580)},
}

# テーマ未指定・未知のときの既定
DEFAULT_THEME = "academic-ja"

# font-size="14" / font-size:14px / font-size: 14
FONT_SIZE_RE = re.compile(r"(font-size\s*[:=]\s*[\"']?\s*)(\d+(?:\.\d+)?)([a-z%]*)", re.I)
VIEWBOX_RE = re.compile(r"""viewBox\s*=\s*["']\s*([-\d.eE]+)[\s,]+([-\d.eE]+)[\s,]+([-\d.eE]+)[\s,]+([-\d.eE]+)""")
SVG_W_RE = re.compile(r"""<svg[^>]*?\swidth\s*=\s*["']\s*([\d.]+)""", re.I | re.S)
SVG_H_RE = re.compile(r"""<svg[^>]*?\sheight\s*=\s*["']\s*([\d.]+)""", re.I | re.S)

# Markdown 中の画像参照:  ![alt](path)  /  <img src="path">
MD_IMG_RE = re.compile(r"""!\[[^\]]*\]\(\s*<?([^)\s>]+)""")
MD_HTML_IMG_RE = re.compile(r"""<img[^>]*?\ssrc\s*=\s*["']([^"']+)""", re.I)


def svg_box(text: str) -> tuple[float, float] | None:
    """描画に使われる本来の寸法（viewBox 優先、無ければ width/height）。"""
    m = VIEWBOX_RE.search(text)
    if m:
        w, h = float(m.group(3)), float(m.group(4))
        if w > 0 and h > 0:
            return w, h
    mw, mh = SVG_W_RE.search(text), SVG_H_RE.search(text)
    if mw and mh:
        w, h = float(mw.group(1)), float(mh.group(1))
        if w > 0 and h > 0:
            return w, h
    return None


def font_sizes(text: str) -> list[float]:
    """px 換算できる font-size をすべて拾う（em/% は相対値なので対象外）。"""
    out = []
    for m in FONT_SIZE_RE.finditer(text):
        unit = m.group(3).lower()
        if unit in ("", "px", "pt"):
            v = float(m.group(2))
            if unit == "pt":
                v *= 4 / 3
            out.append(v)
    return out


def parse_deck(md_path: Path):
    """デッキ .md から (テーマ, [(svgパス, fig-fullか)]) を得る。"""
    text = md_path.read_text(encoding="utf-8")
    theme = None
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            m = re.search(r"^theme:\s*(\S+)", text[:end], re.M)
            if m:
                theme = m.group(1).strip("\"'")
    # スライド境界は行頭の --- （frontmatter の閉じも含むが害はない）
    slides = re.split(r"^---\s*$", text, flags=re.M)
    found = []
    for slide in slides:
        is_full = bool(re.search(r"_class:.*\bfig-full\b", slide))
        for m in list(MD_IMG_RE.finditer(slide)) + list(MD_HTML_IMG_RE.finditer(slide)):
            src = m.group(1).strip()
            if src.lower().endswith(".svg") and not src.startswith(("http://", "https://", "data:")):
                found.append(((md_path.parent / src).resolve(), is_full))
    # 同じ図が複数枚で使われていたら、厳しい方（fig-fullでない方）で判定する
    merged: dict[Path, bool] = {}
    for p, full in found:
        merged[p] = merged.get(p, True) and full
    return theme, sorted(merged.items())


def collect(paths: list[str], theme_opt: str | None, full_opt: bool):
    """検査対象を (svgパス, テーマ, fig-fullか) に正規化する。"""
    targets = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for svg in sorted(p.rglob("*.svg")):
                targets.append((svg, theme_opt or DEFAULT_THEME, full_opt))
        elif p.suffix.lower() == ".md":
            deck_theme, figs = parse_deck(p)
            t = theme_opt or deck_theme or DEFAULT_THEME
            if t not in THEMES:
                print(f"  ! {p}: theme '{t}' は未知なので {DEFAULT_THEME} として扱う", file=sys.stderr)
                t = DEFAULT_THEME
            for svg, is_full in figs:
                targets.append((svg, t, full_opt or is_full))
        elif p.suffix.lower() == ".svg":
            targets.append((p, theme_opt or DEFAULT_THEME, full_opt))
        else:
            print(f"  ! {p}: .svg / .md / ディレクトリ のいずれでもない", file=sys.stderr)
    return targets


def main() -> int:
    ap = argparse.ArgumentParser(
        description="SVG図の文字がスライド上で何pxになるかを検査する",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("paths", nargs="+", help=".svg / デッキ.md / ディレクトリ")
    ap.add_argument("--theme", choices=sorted(THEMES), help="枠と本文サイズ（.md なら自動判定）")
    ap.add_argument("--full", action="store_true", help="fig-full 前提で判定する")
    ap.add_argument("--floor-ratio", type=float, default=0.6, help="本文に対する下限比（既定0.6）")
    ap.add_argument("--fix", action="store_true", help="下限を満たすよう font-size を一律拡大")
    ap.add_argument("--quiet", action="store_true", help="違反だけ表示")
    args = ap.parse_args()

    targets = collect(args.paths, args.theme, args.full)
    if not targets:
        print("検査対象のSVGが見つかりませんでした。", file=sys.stderr)
        return 0

    violations = 0
    fixed = 0
    for svg, theme, is_full in targets:
        if not svg.exists():
            print(f"NG  {svg}: ファイルが無い")
            violations += 1
            continue
        spec = THEMES[theme]
        fw, fh = spec["frame_full"] if is_full else spec["frame"]
        floor = spec["body"] * args.floor_ratio

        text = svg.read_text(encoding="utf-8")
        box = svg_box(text)
        if box is None:
            print(f"?   {svg.name}: viewBox も width/height も読めない（手で確認）")
            continue
        vw, vh = box
        sizes = font_sizes(text)
        if not sizes:
            if not args.quiet:
                print(f"--  {svg.name}: font-size 指定なし（テキストが無いか、CSS継承）")
            continue

        scale = min(fw / vw, fh / vh)
        smallest = min(sizes)
        effective = smallest * scale
        tag = "OK " if effective >= floor else "NG "
        need = floor / scale  # 下限を満たすのに必要な authored font-size

        if effective < floor:
            violations += 1
        if args.quiet and effective >= floor:
            continue

        label = f"{theme}{'/fig-full' if is_full else ''}"
        print(
            f"{tag} {svg.name}\n"
            f"      viewBox {vw:g}×{vh:g} → 枠 {fw}×{fh} で {scale:.3f}倍"
            f"（{'高さ' if fh / vh < fw / vw else '幅'}律速, {label}）\n"
            f"      最小 font-size {smallest:g} → 実効 {effective:.1f}px"
            f"（下限 {floor:.1f}px = 本文{spec['body']}px × {args.floor_ratio}）"
        )
        if effective < floor:
            print(f"      → 図中の最小フォントを {math.ceil(need)} 以上にする"
                  f"（または viewBox を小さく作り直す）")

        if args.fix and effective < floor:
            k = need / smallest

            def bump(m: re.Match) -> str:
                unit = m.group(3).lower()
                if unit not in ("", "px", "pt"):
                    return m.group(0)
                return f"{m.group(1)}{round(float(m.group(2)) * k, 1):g}{m.group(3)}"

            svg.write_text(FONT_SIZE_RE.sub(bump, text), encoding="utf-8")
            fixed += 1
            print(f"      [fix] font-size を一律 {k:.2f}倍した。"
                  f"枠からのはみ出しを目視で確認すること")

    print()
    if violations:
        print(f"下限割れ {violations}件 / 検査 {len(targets)}件"
              + (f"（うち {fixed}件を --fix で拡大）" if fixed else ""))
        return 0 if args.fix and fixed == violations else 1
    print(f"すべて下限を満たしています（検査 {len(targets)}件）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
