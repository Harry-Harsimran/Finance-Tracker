import tkinter as tk
from tkinter import colorchooser, messagebox, ttk

import db
from gui import theme
from gui.widgets import GlassCanvas, GradientButton


class CategoriesPage(tk.Frame):
    def __init__(self, parent, app, width, height):
        super().__init__(parent, bg=theme.BG_TOP_LEFT)
        self.app = app
        self.color_hex = theme.ACCENT_PURPLE

        self.canvas = GlassCanvas(self, width, height)
        self.canvas.pack(fill="both", expand=True)

        pad = 20
        self.add_card = self.canvas.add_card(pad, pad, width - 2 * pad, 90)
        table_y = pad + 90 + 14
        self.table_card = self.canvas.add_card(pad, table_y, width - 2 * pad, height - table_y - pad)

        self._build_add()
        self._build_table()

    def _build_add(self):
        f = self.add_card
        tk.Label(f, text="Add category", font=theme.FONT_H, fg=theme.TEXT_LIGHT, bg=theme.CARD_BG)\
            .pack(anchor="w", pady=(6, 8))
        row = tk.Frame(f, bg=theme.CARD_BG)
        row.pack(fill="x")
        tk.Label(row, text="Name", font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.CARD_BG).pack(side="left")
        self.name_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.name_var, width=22, style="Glass.TEntry").pack(side="left", padx=8)
        self.swatch = tk.Label(row, text="   ", bg=self.color_hex, width=3)
        self.swatch.pack(side="left", padx=6)
        GradientButton(row, "Pick color", command=self._pick_color, variant="secondary",
                       width=100, height=30, bg=theme.CARD_BG).pack(side="left", padx=6)
        GradientButton(row, "Add", command=self._add, variant="primary",
                       width=90, height=30, bg=theme.CARD_BG).pack(side="left", padx=10)

    def _build_table(self):
        f = self.table_card
        cols = ("name", "count", "total")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=12, style="Glass.Treeview")
        for c, t, w in zip(cols, ("Name", "Count", "Total"), (220, 100, 140)):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="w" if c == "name" else "e")
        self.tree.pack(fill="both", expand=True, padx=10, pady=(10, 6))
        GradientButton(f, "Delete selected", command=self._delete, variant="danger", width=140, height=30,
                       bg=theme.CARD_BG).pack(anchor="w", padx=10, pady=(0, 10))

    def _pick_color(self):
        _, hexcode = colorchooser.askcolor(color=self.color_hex)
        if hexcode:
            self.color_hex = hexcode
            self.swatch.config(bg=hexcode)

    def _add(self):
        name = self.name_var.get().strip()[:40]
        if not name:
            messagebox.showerror("Name required", "Enter a category name.")
            return
        try:
            db.add_category(name, self.color_hex)
        except Exception as e:
            messagebox.showerror("Error", "Category already exists." if "UNIQUE" in str(e) else str(e))
            return
        self.name_var.set("")
        self.refresh()
        self.app.refresh_all()

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select a row", "Select a category first.")
            return
        cid = int(sel[0])
        if not messagebox.askyesno("Delete", "Delete this category?"):
            return
        try:
            db.delete_category(cid)
        except ValueError as e:
            messagebox.showerror("Can't delete", str(e))
            return
        self.refresh()
        self.app.refresh_all()

    def refresh(self):
        rows = db.category_totals()
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", iid=str(r["id"]), values=(r["name"], r["n"], f"{r['total']:.2f}"))
