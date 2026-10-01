import tkinter as tk
from tkinter import messagebox, ttk

import db
from gui import theme
from gui.utils import today_str, valid_date
from gui.widgets import GlassCanvas, GradientButton


class ExpensesPage(tk.Frame):
    def __init__(self, parent, app, width, height):
        super().__init__(parent, bg=theme.BG_TOP_LEFT)
        self.app = app
        self.editing_id = None
        self.cats = []

        self.canvas = GlassCanvas(self, width, height)
        self.canvas.pack(fill="both", expand=True)

        pad, gap = 20, 14
        form_h, filter_h = 120, 50
        table_y = pad + form_h + gap + filter_h + gap
        table_h = height - table_y - pad

        self.form_card = self.canvas.add_card(pad, pad, width - 2 * pad, form_h)
        self.filter_card = self.canvas.add_card(pad, pad + form_h + gap, width - 2 * pad, filter_h)
        self.table_card = self.canvas.add_card(pad, table_y, width - 2 * pad, table_h)

        self._build_form()
        self._build_filter()
        self._build_table()

    def _label(self, parent, text):
        return tk.Label(parent, text=text, font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.CARD_BG)

    def _build_form(self):
        f = self.form_card
        tk.Label(f, text="Add / edit expense", font=theme.FONT_H, fg=theme.TEXT_LIGHT, bg=theme.CARD_BG)\
            .grid(row=0, column=0, columnspan=8, sticky="w", pady=(4, 10))

        r = 1
        self._label(f, "Amount").grid(row=r, column=0, sticky="w")
        self.amount_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.amount_var, width=10, style="Glass.TEntry").grid(row=r, column=1, padx=6)

        self._label(f, "Date").grid(row=r, column=2, sticky="w")
        self.date_var = tk.StringVar(value=today_str())
        ttk.Entry(f, textvariable=self.date_var, width=11, style="Glass.TEntry").grid(row=r, column=3, padx=6)

        self._label(f, "Category").grid(row=r, column=4, sticky="w")
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(f, textvariable=self.cat_var, state="readonly", width=14, style="Glass.TCombobox")
        self.cat_combo.grid(row=r, column=5, padx=6)

        self._label(f, "Note").grid(row=r, column=6, sticky="w")
        self.note_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.note_var, width=18, style="Glass.TEntry").grid(row=r, column=7, padx=6)

        btnrow = tk.Frame(f, bg=theme.CARD_BG)
        btnrow.grid(row=2, column=0, columnspan=8, sticky="w", pady=(12, 0))
        self.save_btn = GradientButton(btnrow, "Add", command=self._save, variant="primary",
                                        width=90, height=32, bg=theme.CARD_BG)
        self.save_btn.pack(side="left")
        self.cancel_btn = GradientButton(btnrow, "Cancel", command=self._reset_form, variant="secondary",
                                          width=90, height=32, bg=theme.CARD_BG)
        self.cancel_btn.pack(side="left", padx=8)
        self.cancel_btn.pack_forget()

    def _build_filter(self):
        f = self.filter_card
        self._label(f, "Month").pack(side="left", padx=(4, 4))
        self.filter_month = tk.StringVar()
        ttk.Entry(f, textvariable=self.filter_month, width=9, style="Glass.TEntry").pack(side="left")
        self._label(f, "Category").pack(side="left", padx=(14, 4))
        self.filter_cat = tk.StringVar()
        self.filter_combo = ttk.Combobox(f, textvariable=self.filter_cat, state="readonly", width=14, style="Glass.TCombobox")
        self.filter_combo.pack(side="left")
        GradientButton(f, "Filter", command=self.refresh, variant="accent", width=80, height=30, bg=theme.CARD_BG)\
            .pack(side="left", padx=10)
        GradientButton(f, "Reset", command=self._reset_filter, variant="secondary", width=80, height=30, bg=theme.CARD_BG)\
            .pack(side="left")
        self.total_lbl = tk.Label(f, text="", font=theme.FONT_BODY_B, fg=theme.TEXT_LIGHT, bg=theme.CARD_BG)
        self.total_lbl.pack(side="right", padx=10)

    def _build_table(self):
        f = self.table_card
        cols = ("date", "category", "note", "amount")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=10, style="Glass.Treeview")
        for c, w in zip(cols, (100, 130, 220, 100)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w, anchor="w" if c != "amount" else "e")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(10, 6))

        btns = tk.Frame(f, bg=theme.CARD_BG)
        btns.pack(fill="x", padx=10, pady=(0, 10))
        GradientButton(btns, "Edit selected", command=self._load_for_edit, variant="accent",
                       width=120, height=30, bg=theme.CARD_BG).pack(side="left")
        GradientButton(btns, "Delete selected", command=self._delete, variant="danger",
                       width=130, height=30, bg=theme.CARD_BG).pack(side="left", padx=8)

    def load_categories(self):
        self.cats = db.list_categories()
        names = [c["name"] for c in self.cats]
        self.cat_combo["values"] = names
        self.filter_combo["values"] = ["All"] + names
        if names and not self.cat_var.get():
            self.cat_var.set(names[0])
        if not self.filter_cat.get():
            self.filter_cat.set("All")

    def _cat_id_by_name(self, name):
        for c in self.cats:
            if c["name"] == name:
                return c["id"]
        return None

    def _reset_filter(self):
        self.filter_month.set("")
        self.filter_cat.set("All")
        self.refresh()

    def _reset_form(self):
        self.editing_id = None
        self.amount_var.set("")
        self.date_var.set(today_str())
        self.note_var.set("")
        self.save_btn.set_text("Add")
        self.cancel_btn.pack_forget()

    def _save(self):
        amount = self.amount_var.get().strip()
        date = self.date_var.get().strip()
        note = self.note_var.get().strip()[:200]
        cat_id = self._cat_id_by_name(self.cat_var.get())
        try:
            amount = round(float(amount), 2)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a positive number.")
            return
        if not valid_date(date):
            messagebox.showerror("Invalid date", "Use YYYY-MM-DD.")
            return
        if not cat_id:
            messagebox.showerror("Category required", "Pick a category.")
            return
        if self.editing_id:
            db.update_expense(self.editing_id, amount, date, cat_id, note)
        else:
            db.add_expense(amount, date, cat_id, note)
        self._reset_form()
        self.refresh()
        self.app.refresh_all()

    def _selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _load_for_edit(self):
        eid = self._selected_id()
        if not eid:
            messagebox.showinfo("Select a row", "Select an expense first.")
            return
        row = db.get_expense(eid)
        self.editing_id = eid
        self.amount_var.set(str(row["amount"]))
        self.date_var.set(row["date"])
        self.note_var.set(row["note"])
        cat = next((c["name"] for c in self.cats if c["id"] == row["category_id"]), "")
        self.cat_var.set(cat)
        self.save_btn.set_text("Save")
        self.cancel_btn.pack(side="left", padx=8)

    def _delete(self):
        eid = self._selected_id()
        if not eid:
            messagebox.showinfo("Select a row", "Select an expense first.")
            return
        if messagebox.askyesno("Delete", "Delete this expense?"):
            db.delete_expense(eid)
            self.refresh()
            self.app.refresh_all()

    def refresh(self):
        self.load_categories()
        month = self.filter_month.get().strip() or None
        cat_name = self.filter_cat.get()
        cat_id = self._cat_id_by_name(cat_name) if cat_name and cat_name != "All" else None
        rows = db.list_expenses(month, cat_id)
        self.tree.delete(*self.tree.get_children())
        total = 0
        for r in rows:
            self.tree.insert("", "end", iid=str(r["id"]), values=(r["date"], r["category"], r["note"], f"{r['amount']:.2f}"))
            total += r["amount"]
        self.total_lbl.config(text=f"Total: Rs {total:,.2f}  ({len(rows)})")
