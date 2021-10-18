CREATE TABLE budget_revenue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    revenue_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revenue_value REAL NOT NULL,
    revenue_source TEXT NOT NULL
);
