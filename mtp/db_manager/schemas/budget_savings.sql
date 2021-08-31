CREATE TABLE budget_savings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    savings_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    savings_value REAL NOT NULL,
    savings_source TEXT NOT NULL,
    savings_reason TEXT NOT NULL,
    savings_action TEXT NOT NULL
);