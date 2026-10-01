# Personal Finance Tracker (Desktop App)

Native desktop app — Python + Tkinter + SQLite + Matplotlib. Gradient background
with frosted-glass ("glassmorphism") cards, gradient-filled buttons. No browser, no server.

## Setup
```bash
python -m venv venv
venv\Scripts\activate        # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python seed_demo.py          # optional: adds 150 sample expenses
python main.py                # launches the window (fixed size, 1100x700)
```

`finance.db` is created automatically next to `main.py` on first run.

## Look
- Flat dark slate background, flat indigo/teal accent buttons, flat cards
- No gradients or glass/blur effects

## Tabs
- **Dashboard** – monthly total, transaction count, top category, pie/bar/line charts
- **Expenses** – add, edit, delete, filter by month/category
- **Categories** – add/delete categories (delete blocked if expenses use it)
- **Report** – total, avg/day, % change vs last month, category breakdown, top 5 expenses, CSV export
