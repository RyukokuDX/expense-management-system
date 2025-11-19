BEGIN TRANSACTION;

-- 親テーブル: PDF/Excel生成ジョブ単位
CREATE TABLE IF NOT EXISTS expenses (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    category            TEXT    NOT NULL,                       -- 例: personal_research
    fiscal_year         TEXT    NOT NULL,                       -- 例: 2025
    pdf_path            TEXT    NOT NULL,
    source_json_path    TEXT,                                   -- OCR直後のJSONファイル（任意）
    excel_path          TEXT,                                   -- 生成したExcelファイル
    extracted_payload   TEXT    NOT NULL,                       -- セル番地→値をJSON文字列で保持
    status              TEXT    NOT NULL DEFAULT 'pending_review',
    is_tax_inclusive    INTEGER NOT NULL DEFAULT 1,             -- 1:内税で確定 / 0:未確定
    created_at          TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS expense_items (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id          INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
    item_index          INTEGER NOT NULL,                       -- item_title_1等のインデックス
    title               TEXT    NOT NULL,
    amount              REAL    NOT NULL,
    currency            TEXT    NOT NULL DEFAULT 'JPY',
    tax_inclusive       INTEGER NOT NULL DEFAULT 1,             -- 1:税込, 0:外税/未確認
    note                TEXT,
    created_at          TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_expenses_category_year ON expenses(category, fiscal_year);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
CREATE UNIQUE INDEX IF NOT EXISTS idx_expense_items_unique
    ON expense_items(expense_id, item_index);

CREATE TRIGGER IF NOT EXISTS trg_expenses_updated_at
AFTER UPDATE ON expenses
FOR EACH ROW
BEGIN
    UPDATE expenses SET updated_at = datetime('now') WHERE id = NEW.id;
END;

COMMIT;

