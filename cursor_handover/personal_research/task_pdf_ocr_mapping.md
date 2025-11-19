## 作業1: PDF抽出と項目整形 (yomitoke)

### 1. 前提準備
- `pip install -r requirements.txt`などでMCPクライアント環境を整備  
- `yomitoke (pdf ocr mcp)`サーバを起動し、PDF(OCR)機能が有効であることを確認  
- 処理対象PDFを`実験実習費_消耗品/pdf/`など既存構造に配置し、ファイル名とタイムスタンプを記録  

### 2. OCR実行
1. `yomitoke`クライアントを起動し、PDFを指定  
2. 言語を日本語優先に設定し、レイアウト保持モードを有効にする  
3. OCR完了後、出力テキスト(JSON/TSVなど)を保存  
4. 保存したOCR結果から以下のキーを抽出し、`exel_mapping.toml`のセル番地と対応付ける  

```
[expendidture.personal.mapping]
application_date -> U2
affiliation_position -> Q8
employee_number -> Q9
applicant -> Q10
research_representative -> Q11
expense_category -> G23
item_title_1..10 -> G28..G37
item_price_1..10 -> V28..V37
install_campus -> P40
install_location -> U40
delivery_campus -> P41
delivery_location -> U41
payment_destination -> G43
advance_payer -> T43
```

### 3. プロファイル適用
- `profile_config.toml`内の`[expendidture.personal.profile]`を参照  
- OCR結果に値が無い/固定値にしたい項目は、同プロファイルから補完  
  - `affiliation_position`, `staff_number`, `applicant`, `research_representative`など  

### 4. データ整形
1. 取得した値をキー名で統一し、欠損は空文字もしくは0で管理  
2. Excelセルごとの辞書を作成（例: `{"U2":"2025/04/22", "Q8":"数理・情報科学過程・准教授", ...}`）  
3. 金額フィールドは数値型へ正規化（カンマ除去、円単位）  
4. 金額が外税や税区分不明と判断された場合はユーザーへ問い合わせ、内税（総額）での入力方針を確認できるまで保留  
5. 項目が複数ある場合は`item_title_*`と`item_price_*`を同じインデックスで揃える  

### 5. ハンドオフ
- 整形済みデータをJSON等で保存し、作業2へ渡す  
- 保存ファイル名例: `processed/20250422113155_personal.json`  

