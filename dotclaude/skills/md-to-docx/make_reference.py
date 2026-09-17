#!/usr/bin/env python3
"""pandoc 既定の reference.docx を和文学術文書用に加工して再生成する。

  pandoc --print-default-data-file reference.docx を取得し、
  - 本文: Times New Roman + ＭＳ 明朝（12pt）、段落後空き0
  - 見出し: Arial + ＭＳ ゴシック、色は黒
  - 用紙: A4縦・余白30mm
  に書き換えて reference.docx を出力する。

Usage: python3 make_reference.py [出力パス（省略時 reference.docx）]
"""
import shutil
import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

PANDOC = shutil.which("pandoc") or "pandoc"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "reference.docx")

MINCHO = 'w:ascii="Times New Roman" w:eastAsia="ＭＳ 明朝" w:hAnsi="Times New Roman" w:cs="Times New Roman"'
GOTHIC = 'w:ascii="Arial" w:eastAsia="ＭＳ ゴシック" w:hAnsi="Arial" w:cs="Arial"'

SECT_PROPS = (
    '<w:pgSz w:w="11906" w:h="16838" />'
    '<w:pgMar w:top="1701" w:right="1701" w:bottom="1701" w:left="1701"'
    ' w:header="851" w:footer="851" w:gutter="0" />'
)


def patch_styles(xml: str) -> str:
    # 既定フォント（minorテーマ）→ Times + ＭＳ 明朝
    xml = re.sub(r'<w:rFonts w:asciiTheme="minorHAnsi"[^/]*/>', f"<w:rFonts {MINCHO} />", xml)
    # 見出し・Title系フォント（majorテーマ）→ Arial + ＭＳ ゴシック（属性順・改行に非依存）
    xml = re.sub(r'<w:rFonts (?=[^>]*?Theme="major)[^>]*?/>', f"<w:rFonts {GOTHIC} />", xml, flags=re.S)
    # 見出し色（テーマ青）→ 黒
    xml = re.sub(r'<w:color w:val="[0-9A-Fa-f]{6}" w:themeColor="accent1"[^/]*/>', '<w:color w:val="000000" />', xml)
    # 東アジア言語を日本語に
    xml = xml.replace('w:eastAsia="zh-CN"', 'w:eastAsia="ja-JP"')
    # 段落後の空きを詰める（和文の体裁）
    xml = xml.replace('<w:spacing w:after="200" />', '<w:spacing w:after="0" w:line="360" w:lineRule="auto" />')
    xml = xml.replace('<w:spacing w:before="180" w:after="180" />', '<w:spacing w:before="0" w:after="0" />')
    return xml


def patch_document(xml: str) -> str:
    # sectPr に A4・余白を注入（既定referenceはページ設定を持たない）
    return xml.replace("<w:sectPr>", "<w:sectPr>" + SECT_PROPS, 1)


def main() -> None:
    default = subprocess.run(
        [PANDOC, "--print-default-data-file", "reference.docx"],
        capture_output=True, check=True,
    ).stdout
    src = zipfile.ZipFile(io.BytesIO(default))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/styles.xml":
                data = patch_styles(data.decode("utf-8")).encode("utf-8")
            elif item.filename == "word/document.xml":
                data = patch_document(data.decode("utf-8")).encode("utf-8")
            dst.writestr(item, data)
    OUT.write_bytes(buf.getvalue())
    print(f"OK: {OUT}")


if __name__ == "__main__":
    main()
