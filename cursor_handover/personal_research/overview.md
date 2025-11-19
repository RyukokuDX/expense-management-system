## 個人研究費: ハンドオフ概要

- 目的: PDF領収書をOCRし、`exel_format/expendidture_private_2025.xlsx`へ転記したExcelを生成  
- 参照ファイル: `exel_mapping.toml`, `profile_config.toml`, `実験実習費_消耗品/pdf/*`, `exel_format/`配下テンプレート  
- 金額は内税（総額表示）で入力し、外税/不明な場合はユーザーへ確認  

## 進行順
1. `task_pdf_ocr_mapping.md`: `yomitoke (pdf ocr mcp)`を用いたPDF→項目抽出、プロファイル補完  
2. `task_excel_population.md`: `exel-mcp`でテンプレート複製とセル投入、検証  

## 出力/受け渡し
- 作業1の成果物: `processed/<timestamp>_personal.json` (セル番地→値の辞書構造)  
- 作業2の成果物: `exel_format/output/<timestamp>_personal.xlsx`  

## 発展
- 他の費目が増えた場合は`cursor_handover/<category>/overview.md`を新設し、同フォーマットで手順を整理  
