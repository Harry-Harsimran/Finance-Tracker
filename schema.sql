CREATE TABLE IF NOT EXISTS categories (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE,
    color TEXT NOT NULL DEFAULT '#6366f1'
);

CREATE TABLE IF NOT EXISTS expenses (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amount      REAL NOT NULL CHECK (amount > 0),
    date        TEXT NOT NULL,              -- YYYY-MM-DD
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    note        TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
