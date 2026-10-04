# researchmap V2 CSV のテーブル別規則

値の正本は `cv.py` の `SCHEMA`。ここは対話で使う説明。
出典は researchmap V2 CSV項目定義書 V2.1（https://researchmap.jp/outline/v2api/v2CSV.pdf）。

## すべてのテーブルに共通

| 決まり | 内容 |
|---|---|
| ファイル構造 | 1行目=種別（テーブル名だけの1セル）、2行目=ヘッダ、3行目以降=データ |
| 文字コード | UTF-8。**BOM を付けない**。1ファイル10MBまで |
| 空欄 | 空白ではなく文字列 `null` を書く |
| アクション4列 | 新規は `アクション名=insert` / `アクションタイプ=merge` / `類似業績マージ優先度=null` / `ID` は空。`cv.py append` が自動で付ける |
| 類似業績があるとき | ID なしの `merge` は**エラーになる**。`similar_merge` ＋ `input_data`（入力データ優先）か `similar_data`（既存優先）に変える |
| 日付 | `yyyy` / `yyyy-mm` / `yyyy-mm-dd`。カラム名が「年月」でも日まで入れてよい |
| 複数値 | `[a,b]` で囲みカンマ区切り。データ中のカンマは `\` でエスケープ（`[山田\,太郎]` で姓名分離） |
| 真偽値 | `TRUE` / `FALSE` / `null`（未設定）。エクスポートは小文字だがインポートは大文字 |
| 公開の有無 | `disclosed` / `undisclosed`。既存は全件 `disclosed` |
| 主要な業績かどうか | 既存は全件 `FALSE` |
| 記述言語 | `jpn` / `eng`。他は言語コード一覧を参照 |
| 国・地域 | ISO 3166-1 alpha-3（日本 `JPN`、台湾 `TWN`、ポルトガル `PRT`） |

## presentations（講演・口頭発表等）

必須はタイトル（日英いずれか）だけ。

- `会議種別`: `oral_presentation`（口頭発表・一般）/ `invited_oral_presentation`（招待・特別）/ `keynote_oral_presentation`（基調）/ `poster_presentation` / `public_symposium`（パネル・公募）/ `nominated_symposium`（パネル・指名）/ `public_discourse`（公開講演・セミナー・チュートリアル・講習）/ `media_report` / `others`
- 真偽値: `招待の有無` `国際・国内会議` `国際共著`
- 複数値: `講演者(日本語)` `講演者(英語)`
- 日付: `発表年月日` `開催年月日(From)` `開催年月日(To)`
- **査読の列がない。** 査読付きフルペーパーという事実はここには書けない

## published_papers（論文）／ misc（MISC）

カラム構成は同一で、`掲載種別` の値だけが違う。書評・連載・イベントレポートは misc。

- `published_papers.掲載種別`: `scientific_journal` / `international_conference_proceedings` / `symposium` / `research_institution` / `introduction_scientific_journal` / `others`
- `misc.掲載種別`: `book_review` / `introduction_scientific_journal` / `introduction_commerce_magazine` / `introduction_other` / `meeting_report` / `others`
- 真偽値: `査読の有無` `招待の有無` `国際・国内誌` `国際共著`
- 複数値: `著者(日本語)` `著者(英語)` `担当区分`
- `担当区分` は `[lead]` のような**複数値**で、単著／共著の別ではない。master 側の単著・共著は著者の人数で決まる

## books_etc（書籍等出版物）

- `担当区分`: `sole_author` / `joint_author` / `editor` / `joint_editor` / `contributor` / `translator` / `editing_translation`
- `著書種別`: `scholarly_book` / `general_book` / `textbook` / `dictionary_or_encycropedia` / `report` / `others`
  （`encycropedia` は researchmap 側の綴りのまま。直さない）
- 複数値: `著者(翻訳者)(日本語)` `著者(翻訳者)(英語)` `原著者(日本語)` `原著者(英語)`
- `担当範囲(日本語)` に執筆箇所、`担当ページ` に頁範囲を書く（履歴書の書名欄で使う）

## awards（受賞）

- `受賞区分`: `international_society` / `japan_society` / `publisher` / `government` / `public_organization` / `others`
- 必須はタイトルではなく `賞名`。**重複判定に受賞年を併用する**（賞名が短く再受賞があり得るため）

## research_projects（研究課題）

- `資金種別`: `competitive_research_funding` / `joint_research` / `contract_research` / `subsidy` / `others`
- `担当区分`: `principal_investigator` / `coinvestigator` / `research_collaborator` / `others`
- 日付は `研究期間(From)` `研究期間(To)`
