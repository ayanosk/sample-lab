# publications/<名前>/ にコピーして使う。パスの書き換えは不要。
# ipsj.cls は pLaTeX 専用なので、共通の .latexmkrc（LuaLaTeX）は読み込まない。
$latex     = 'platex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$bibtex    = 'pbibtex %O %B';      # 日本語の .bst（is.kanji.str$）に対応
$dvipdf    = 'dvipdfmx %O -o %D %S';
$pdf_mode  = 3;                    # 3 = dvi → pdf (dvipdfmx)
$max_repeat = 5;
$clean_ext = 'synctex.gz bbl fdb_latexmk fls log aux dvi';
