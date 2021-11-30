CREATE TABLE budget_utilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilities_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    utilities_rent_value INTEGER NOT NULL,
    utilities_energy_value INTEGER NOT NULL,
    utilities_satellite_value INTEGER NOT NULL,
    utilities_maintenance_value INTEGER NOT NULL,
    utilities_info TEXT
);