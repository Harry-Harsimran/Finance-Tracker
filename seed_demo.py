"""Optional: fill the DB with random demo expenses so charts have data.
Run:  python seed_demo.py
"""
import random
from datetime import date, timedelta

import db

db.init_db()
cats = [r["id"] for r in db.list_categories()]
notes = ["", "groceries", "uber", "electricity", "movie", "pharmacy", "lunch", "online order"]
today = date.today()
for _ in range(150):
    d = today - timedelta(days=random.randint(0, 170))
    db.add_expense(round(random.uniform(50, 3000), 2), d.isoformat(), random.choice(cats), random.choice(notes))
print("Seeded 150 demo expenses.")
