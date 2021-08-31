CREATE TABLE budget_expense (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expense_item TEXT NOT NULL,
    expense_value REAL NOT NULL,
    expense_item_category TEXT NOT NULL,
    expense_source TEXT NOT NULL,
    FOREIGN KEY (expense_source) REFERENCES budget_revenue (revenue_source),
    FOREIGN KEY (expense_source) REFERENCES budget_savings (savings_source)
);
