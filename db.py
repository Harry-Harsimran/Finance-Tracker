import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("FINANCE_DB", os.path.join(BASE, "finance.db"))

DEFAULT_CATEGORIES = [
    ("Food", "#f97316"), ("Rent", "#6366f1"), ("Transport", "#0ea5e9"),
    ("Bills", "#ef4444"), ("Shopping", "#ec4899"), ("Health", "#10b981"),
    ("Entertainment", "#a855f7"), ("Other", "#64748b"),
]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        with open(os.path.join(BASE, "schema.sql")) as f:
            conn.executescript(f.read())
        if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] == 0:
            conn.executemany("INSERT INTO categories (name, color) VALUES (?, ?)", DEFAULT_CATEGORIES)


def query(sql, args=(), one=False):
    conn = get_conn()
    try:
        rows = conn.execute(sql, args).fetchall()
    finally:
        conn.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, args=()):
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute(sql, args)
        return cur.lastrowid
    finally:
        conn.close()


# ---------- categories ----------

def list_categories():
    return query("SELECT * FROM categories ORDER BY name")


def add_category(name, color):
    execute("INSERT INTO categories (name, color) VALUES (?,?)", (name, color))


def delete_category(cid):
    used = query("SELECT COUNT(*) n FROM expenses WHERE category_id=?", (cid,), one=True)["n"]
    if used:
        raise ValueError(f"Can't delete: {used} expense(s) use this category.")
    execute("DELETE FROM categories WHERE id=?", (cid,))


def category_totals():
    return query("""
        SELECT c.*, COUNT(e.id) n, COALESCE(SUM(e.amount),0) total
        FROM categories c LEFT JOIN expenses e ON e.category_id=c.id
        GROUP BY c.id ORDER BY c.name""")


# ---------- expenses ----------

def add_expense(amount, date, category_id, note):
    execute("INSERT INTO expenses (amount, date, category_id, note) VALUES (?,?,?,?)",
            (amount, date, category_id, note))


def update_expense(eid, amount, date, category_id, note):
    execute("UPDATE expenses SET amount=?, date=?, category_id=?, note=? WHERE id=?",
            (amount, date, category_id, note, eid))


def delete_expense(eid):
    execute("DELETE FROM expenses WHERE id=?", (eid,))


def get_expense(eid):
    return query("SELECT * FROM expenses WHERE id=?", (eid,), one=True)


def list_expenses(month=None, category_id=None):
    sql = ("SELECT e.*, c.name category, c.color FROM expenses e "
           "JOIN categories c ON c.id=e.category_id WHERE 1=1")
    args = []
    if month:
        sql += " AND substr(e.date,1,7)=?"
        args.append(month)
    if category_id:
        sql += " AND e.category_id=?"
        args.append(category_id)
    sql += " ORDER BY e.date DESC, e.id DESC"
    return query(sql, args)


# ---------- reports (month = 'YYYY-MM') ----------

def month_total(month):
    r = query("SELECT COALESCE(SUM(amount),0) t, COUNT(*) n FROM expenses WHERE substr(date,1,7)=?", (month,), one=True)
    return r["t"], r["n"]


def by_category(month):
    return query("""
        SELECT c.name, c.color, ROUND(SUM(e.amount),2) total, COUNT(*) n
        FROM expenses e JOIN categories c ON c.id = e.category_id
        WHERE substr(e.date,1,7)=?
        GROUP BY c.id ORDER BY total DESC""", (month,))


def by_day(month):
    return query("""
        SELECT date, ROUND(SUM(amount),2) total FROM expenses
        WHERE substr(date,1,7)=? GROUP BY date ORDER BY date""", (month,))


def top_expenses(month, limit=5):
    return query("""
        SELECT e.*, c.name category FROM expenses e JOIN categories c ON c.id=e.category_id
        WHERE substr(e.date,1,7)=? ORDER BY e.amount DESC LIMIT ?""", (month, limit))


def export_csv(path):
    import csv
    rows = query("""SELECT e.date, c.name category, e.amount, e.note
                    FROM expenses e JOIN categories c ON c.id=e.category_id
                    ORDER BY e.date DESC, e.id DESC""")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "category", "amount", "note"])
        for r in rows:
            w.writerow([r["date"], r["category"], r["amount"], r["note"]])
    return len(rows)
