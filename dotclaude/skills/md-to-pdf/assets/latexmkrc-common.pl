# latexmkrc-common.pl — LuaLaTeX + biber の共通設定
#
# 各テンプレートの .latexmkrc から require される。呼び出し側が求めた
# リポジトリルートが $LAB_ROOT に入っている前提。
#
# ここで TEXINPUTS / BIBINPUTS を設定するので、原稿フォルダは
# リポジトリ内のどの深さに置いてもよい。main.tex は
#   \input{preamble-ja}
#   \addbibresource{references.bib}
# と、パスを書かずに参照できる。

our $LAB_ROOT;
die "latexmkrc-common.pl: \$LAB_ROOT が設定されていません\n" unless $LAB_ROOT;

my $assets = "$LAB_ROOT/.claude/skills/md-to-pdf/assets";

# 先頭の「.」でカレントを最優先にする。これを省くと、原稿の main.tex より
# assets/templates/*/main.tex が先に見つかってしまう。
# 再帰探索の「//」は使わない。理由は同じで、templates/ 以下の同名ファイルを拾うため。
# 末尾の「:」は空要素で、kpathsea 既定の検索パスを残す意味。
$ENV{TEXINPUTS} = ".:$assets:" . ($ENV{TEXINPUTS} // '') . ":";
$ENV{BIBINPUTS} = ".:$LAB_ROOT/bibliography:$assets:" . ($ENV{BIBINPUTS} // '') . ":";

$lualatex = 'lualatex -synctex=1 -interaction=nonstopmode -file-line-error %O %S';
$pdf_mode = 4;           # 4 = lualatex
$biber = 'biber %O %S';
$bibtex_use = 2;
$max_repeat = 5;
$clean_ext = 'synctex.gz run.xml bbl bcf fdb_latexmk fls log aux toc out';

1;    # require の戻り値。消さないこと
