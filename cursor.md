## 目的
- 費目ごとのハンドオフ構造を`cursor.md`から俯瞰し、各費目の詳細作業手順(作業1/作業2/...)へナビゲートする  
- 個人研究費では`yomitoke (pdf ocr mcp)`と`exel-mcp`を組み合わせ、PDF→Excel化を自動化する  

## ハンドオフ構造
- 個人研究費
  - `cursor_handover/personal_research/overview.md`
    - `cursor_handover/personal_research/task_pdf_ocr_mapping.md` (PDF抽出〜項目整形)
    - `cursor_handover/personal_research/task_excel_population.md` (Excelテンプレート入力)

## 新規費目追加手順
1. `cursor_handover/<category>/`ディレクトリを作成  
2. `overview.md`で目的・参照ファイル・作業順・成果物を定義  
3. 作業内容ごとに`task_<summary>.md`を作成し、`cursor.md`のハンドオフ構造に追記  
4. 金額関連ルール（内税のみ・不明時はユーザーへ確認）を明記  

※ 新しい費目を扱う際は同ディレクトリ配下に`<category>/overview.md`とタスクファイル群を追加する  

## 共通参照
- `exel_mapping.toml`: PDF項目→Excelセル対応  
- `profile_config.toml`: プロファイル固定値  
- `exel_format/expendidture_private_2025.xlsx`: 個人研究費テンプレート  
- `sql/00000000000000_create_expenses.sql`: 初期DBスキーマ。以降のマイグレーションは`yyyymmddhhmm_<category>_<summary>.sql`命名で追加する  

## 注意点
- 設定ファイルのバージョン番号は変更しない  
- OCR結果は必ず人手で再確認する  
- Excel生成後は`exel_format/output/`など別名保存し、テンプレートを上書きしない  
- Excelへ記載する金額はすべて内税価格に統一し、外税・判断不明時はユーザーへ確認する  

