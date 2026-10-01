import calendar as _cal
import tkinter as tk
from datetime import date as _date
from tkinter import filedialog, messagebox, ttk

import db
from gui import theme
from gui.utils import money, month_label, shift_month, this_month
from gui.widgets import GlassCanvas, GradientButton


class ReportPage(tk.Frame):
    def __init__(self, parent, app, width, height):
        super().__init__(parent, bg=theme.BG_TOP_LEFT)
        self.app = app
        self.month = this_month()

        self.canvas = GlassCanvas(self, width, height)
        self.canvas.pack(fill="both", expand=True)

        pad, gap = 20, 12
        header_h, stats_h = 46, 80
        self.header_card = self.canvas.add_card(pad, pad, width - 2 * pad, header_h)

        stats_y = pad + header_h + gap
        card_w = (width - 2 * pad - 3 * gap) // 4
        self.stat_cards = [self.canvas.add_card(pad + i * (card_w + gap), stats_y, card_w, stats_h)
                            for i in range(4)]

        panels_y = stats_y + stats_h + gap
        panel_w = (width - 2 * pad - gap) // 2
        panel_h = height - panels_y - pad
        self.cat_card = self.canvas.add_card(pad, panels_y, panel_w, panel_h)
        self.top_card = self.canvas.add_card(pad + panel_w + gap, panels_y, panel_w, panel_h)

        self._build_header()
        self._build_stats()
        self._build_panels()

    def _build_header(self):
        f = self.header_card
        GradientButton(f, "\u2039", command=lambda: self._shift(-1), variant="secondary",
                       width=36, height=30, bg=theme.CARD_BG).pack(side="left", padx=(4, 8))
        self.month_lbl = tk.Label(f, text="", font=theme.FONT_H, fg=theme.TEXT_LIGHT, bg=theme.CARD_BG)
        self.month_lbl.pack(side="left")
        GradientButton(f, "\u203a", command=lambda: self._shift(1), variant="secondary",
                       width=36, height=30, bg=theme.CARD_BG).pack(side="left", padx=8)
        GradientButton(f, "Export CSV", command=self._export, variant="accent",
                       width=110, height=30, bg=theme.CARD_BG).pack(side="right", padx=4)

    def _build_stats(self):
        titles = ["Total", "Avg / day", "Transactions", "vs last month"]
        self.stat_labels = []
        for card, title in zip(self.stat_cards, titles):
            tk.Label(card, text=title, font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.CARD_BG)\
                .pack(anchor="w", padx=12, pady=(10, 0))
            lbl = tk.Label(card, text="-", font=theme.FONT_BIG, fg=theme.TEXT_LIGHT, bg=theme.CARD_BG)
            lbl.pack(anchor="w", padx=12)
            self.stat_labels.append(lbl)

    def _build_panels(self):
        tk.Label(self.cat_card, text="Category breakdown", font=theme.FONT_H, fg=theme.TEXT_LIGHT,
                  bg=theme.CARD_BG).pack(anchor="w", padx=10, pady=(8, 4))
        self.cat_tree = ttk.Treeview(self.cat_card, columns=("cat", "amt", "pct"), show="headings",
                                       height=9, style="Glass.Treeview")
        for c, t, w in zip(("cat", "amt", "pct"), ("Category", "Amount", "Share"), (150, 110, 80)):
            self.cat_tree.heading(c, text=t)
            self.cat_tree.column(c, width=w, anchor="w" if c == "cat" else "e")
        self.cat_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(self.top_card, text="Top 5 expenses", font=theme.FONT_H, fg=theme.TEXT_LIGHT,
                  bg=theme.CARD_BG).pack(anchor="w", padx=10, pady=(8, 4))
        self.top_tree = ttk.Treeview(self.top_card, columns=("date", "cat", "amt"), show="headings",
                                       height=9, style="Glass.Treeview")
        for c, t, w in zip(("date", "cat", "amt"), ("Date", "Category", "Amount"), (100, 160, 100)):
            self.top_tree.heading(c, text=t)
            self.top_tree.column(c, width=w, anchor="w" if c != "amt" else "e")
        self.top_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _shift(self, d):
        self.month = shift_month(self.month, d)
        self.refresh()

    def _export(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="expenses.csv",
                                             filetypes=[("CSV", "*.csv")])
        if path:
            n = db.export_csv(path)
            messagebox.showinfo("Exported", f"Exported {n} expense(s) to {path}")

    def refresh(self):
        self.month_lbl.config(text=month_label(self.month))
        total, count = db.month_total(self.month)
        prev_total, _ = db.month_total(shift_month(self.month, -1))
        y, mo = map(int, self.month.split("-"))
        days_in_month = _cal.monthrange(y, mo)[1]
        days_elapsed = _date.today().day if self.month == this_month() else days_in_month

        self.stat_labels[0].config(text=money(total))
        self.stat_labels[1].config(text=money(total / days_elapsed if days_elapsed else 0))
        self.stat_labels[2].config(text=str(count))
        if prev_total == 0:
            self.stat_labels[3].config(text="-")
        else:
            change = round((total - prev_total) / prev_total * 100, 1)
            self.stat_labels[3].config(text=f"{'+' if change > 0 else ''}{change}%")

        cats = db.by_category(self.month)
        self.cat_tree.delete(*self.cat_tree.get_children())
        for c in cats:
            pct = round(c["total"] / total * 100, 1) if total else 0
            self.cat_tree.insert("", "end", values=(c["name"], f"{c['total']:.2f}", f"{pct}%"))

        top = db.top_expenses(self.month)
        self.top_tree.delete(*self.top_tree.get_children())
        for t in top:
            label = t["category"] + (f" ({t['note']})" if t["note"] else "")
            self.top_tree.insert("", "end", values=(t["date"], label, f"{t['amount']:.2f}"))
