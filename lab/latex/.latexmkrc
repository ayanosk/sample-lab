# lab/latex/.latexmkrc — LuaLaTeX + biber 共通設定
# 使い方: 各プロジェクトの .latexmkrc から require するか、コピーして使う
$lualatex = 'lualatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$pdf_mode = 4;           # 4 = lualatex
$biber = 'biber %O %S';
$bibtex_use = 2;
$max_repeat = 5;
$clean_ext = 'synctex.gz run.xml bbl bcf fdb_latexmk fls log aux toc out';
