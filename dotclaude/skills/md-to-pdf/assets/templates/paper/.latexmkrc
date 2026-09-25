# このフォルダごと work/publications/<名前>/ にコピーして使う。
# パスの書き換えは不要。リポジトリ内ならどの深さに置いてもよい。
#
# リポジトリルート（AGENTS.md のあるフォルダ）を上へ辿って探し、
# 共通設定を読み込む。共通設定側が TEXINPUTS / BIBINPUTS を設定するので、
# main.tex はパスを書かずに \input{preamble-ja} と書ける。
use Cwd qw(abs_path);
our $LAB_ROOT = abs_path('.');
$LAB_ROOT = abs_path("$LAB_ROOT/..")
    while $LAB_ROOT ne '/' && !-e "$LAB_ROOT/AGENTS.md";
die "リポジトリルートが見つかりません（AGENTS.md のあるフォルダを探しています）\n"
    if $LAB_ROOT eq '/';
require "$LAB_ROOT/.claude/skills/md-to-pdf/assets/latexmkrc-common.pl";

$out_dir = 'build';
