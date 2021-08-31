CREATE TABLE validation_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    FOREIGN KEY (category) REFERENCES query_validation_categories (categories)
);