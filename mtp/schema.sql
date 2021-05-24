DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS budget_expense;
DROP TABLE IF EXISTS budget_revenue;
DROP TABLE IF EXISTS budget_savings;
DROP TABLE IF EXISTS budget_utilities;
DROP TABLE IF EXISTS validation;
DROP TABLE IF EXISTS validation_items;
DROP TABLE IF EXISTS validation_categories;
DROP TABLE IF EXISTS validation_sources;
DROP TABLE IF EXISTS validation_savings_accounts;
DROP TABLE IF EXISTS avalidation_savings_action_types;
DROP TABLE IF EXISTS validation_savings_reason;
--DROP TABLE IF EXISTS collections_ledger;
--DROP TABLE IF EXISTS collections_media;
--DROP TABLE IF EXISTS health_biometrics;
--DROP TABLE IF EXISTS health_workout;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEST NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

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

CREATE TABLE budget_revenue(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    revenue_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revenue_value REAL NOT NULL,
    revenue_source TEXT NOT NULL
);

CREATE TABLE budget_savings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    savings_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    savings_value REAL NOT NULL,
    savings_source TEXT NOT NULL,
    savings_reason TEXT NOT NULL,
    savings_action TEXT NOT NULL
);

CREATE TABLE budget_utilities(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilities_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    utilities_rent_value INTEGER NOT NULL,
    utilities_energy_value INTEGER NOT NULL,
    utilities_sattelite_value INTEGER NOT NULL,
    utilities_maintenance_value INTEGER NOT NULL,
    utilities_info TEXT
);

CREATE TABLE validation_items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    items TEXT NOT NULL
);

CREATE TABLE validation_categories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categories TEXT NOT NULL

);

CREATE TABLE validation_sources(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sources TEXT NOT NULL
);

CREATE TABLE validation_savings_accounts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    savings_accounts TEXT NOT NULL
);

CREATE TABLE validation_savings_action_types(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    savings_action_types TEXT NOT NULL
);

CREATE TABLE validation_savings_reason(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    savings_reason TEXT NOT NULL
);

--CREATE TABLE collections_ledger(
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    month TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
--    number_of_books INTEGER NOT NULL,
--    book_title TEXT NOT NULL,
--    book_author TEXT NOT NULL,
--    book_genre TEXT NOT NULL,
--    book_pages INTEGER NOT NULL,
--    book_publish_date TEXT NOT NULL,
--    book_status TEXT NOT NULL,
--    book_id TEXT NOT NULL
--);



--validation_tables = ['types', 'levels', 'regions', 'workouts', 'reps', 'sets']
--
--types = ['body weight', 'weighted']
--levels = ['beginner', 'intermediate', 'advanced']
--regions = ['Anterior Lower - Squats', 'Upper Push', 'Posterior Lower - Hinge', 'Upper Pull', 'Abs', 'Corrective',
--           'Anterior Lower - Lunge', 'Calf', 'Forearm', 'Postural', 'Stretch']
--workouts = ['Workout A', 'Workout B', 'Variation A', 'Variation B', 'Variation C', 'Rest day']
--reps = ['8-12']
--sets = ['3', '1 minute', '45 seconds', 'failure']
