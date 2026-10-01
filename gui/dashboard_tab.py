import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import db
from gui import theme
from gui.utils import money, month_label, shift_month, this_month
from gui.widgets import GlassCanvas, GradientButton


class DashboardPage(tk.Frame):
    def __init__(self, parent, app, width, height):
        super().__init__(parent, bg=theme.BG_TOP_LEFT)
        self.app = app
        self.month = this_month()

        self.canvas = GlassCanvas(self, width, height)
        self.canvas.pack(fill="both", expand=True)

        pad, gap = 20, 20
        card_w = (width - 2 * pad - 2 * gap) // 3
        y0 = 16
        self.card_total = self.canvas.add_card(pad, y0, card_w, 90)
        self.card_count = self.canvas.add_card(pad + card_w + gap, y0, card_w, 90)
        self.card_top = self.canvas.add_card(pad + 2 * (card_w + gap), y0, card_w, 90)
        self._fill_stat_card(self.card_total, "Total spent")
        self._fill_stat_card(self.card_count, "Transactions")
        self._fill_stat_card(self.card_top, "Top category")

        chart_y = y0 + 90 + 16
        chart_h = height - chart_y - 16
        self.chart_card = self.canvas.add_card(pad, chart_y, width - 2 * pad, chart_h)

        nav = tk.Frame(self.chart_card, bg=theme.CARD_BG)
        nav.pack(fill="x", pady=(0, 6))
        GradientButton(nav, "\u2039 Prev", command=lambda: self._shift(-1), variant="secondary",
                       width=80, height=30, bg=theme.CARD_BG).pack(side="left")
        self.month_lbl = tk.Label(nav, text="", font=theme.FONT_H, fg=theme.TEXT_LIGHT, bg=theme.CARD_BG)
        self.month_lbl.pack(side="left", padx=14)
        GradientButton(nav, "Next \u203a", command=lambda: self._shift(1), variant="secondary",
                       width=80, height=30, bg=theme.CARD_BG).pack(side="left")

        self.chart_area = tk.Frame(self.chart_card, bg=theme.CARD_BG)
        self.chart_area.pack(fill="both", expand=True)

    def _fill_stat_card(self, frame, title):
        tk.Label(frame, text=title, font=theme.FONT_BODY, fg=theme.TEXT_MUTED, bg=theme.CARD_BG)\
            .pack(anchor="w", padx=14, pady=(12, 0))
        lbl = tk.Label(frame, text="-", font=theme.FONT_BIG, fg=theme.TEXT_LIGHT, bg=theme.CARD_BG)
        lbl.pack(anchor="w", padx=14)
        frame.value_label = lbl

    def _shift(self, d):
        self.month = shift_month(self.month, d)
        self.refresh()

    def refresh(self):
        self.month_lbl.config(text=month_label(self.month))
        total, count = db.month_total(self.month)
        cats = db.by_category(self.month)
        self.card_total.value_label.config(text=money(total))
        self.card_count.value_label.config(text=str(count))
        self.card_top.value_label.config(text=cats[0]["name"] if cats else "-")

        for w in self.chart_area.winfo_children():
            w.destroy()

        if not cats:
            tk.Label(self.chart_area, text="No expenses this month.", fg=theme.TEXT_MUTED,
                     bg=theme.CARD_BG).pack(pady=40)
            return

        fig = Figure(figsize=(10, 3.6), dpi=100)
        fig.patch.set_alpha(0)
        ax1 = fig.add_subplot(1, 3, 1)
        ax2 = fig.add_subplot(1, 3, 2)
        ax3 = fig.add_subplot(1, 3, 3)
        for ax in (ax1, ax2, ax3):
            ax.set_facecolor("none")

        names = [c["name"] for c in cats]
        totals = [c["total"] for c in cats]
        colors = [theme.CHART_PALETTE[i % len(theme.CHART_PALETTE)] for i in range(len(cats))]
        _, texts, autotexts = ax1.pie(totals, labels=names, colors=colors, autopct="%1.0f%%",
                                       textprops={"fontsize": 7, "color": "white"})
        for t in texts:
            t.set_color("white")
        ax1.set_title("By category", fontsize=9, color="white")

        months = [shift_month(self.month, i) for i in range(-5, 1)]
        trend = [db.month_total(m)[0] for m in months]
        ax2.bar([m[5:] for m in months], trend, color=theme.ACCENT_PINK)
        ax2.set_title("Last 6 months", fontsize=9, color="white")
        ax2.tick_params(labelsize=7, colors="white")
        for spine in ax2.spines.values():
            spine.set_color("#ffffff55")

        days = db.by_day(self.month)
        if days:
            ax3.plot([d["date"][8:] for d in days], [d["total"] for d in days],
                     color=theme.ACCENT_TEAL, marker="o", markersize=3)
        ax3.set_title("Daily spending", fontsize=9, color="white")
        ax3.tick_params(labelsize=6, rotation=45, colors="white")
        for spine in ax3.spines.values():
            spine.set_color("#ffffff55")

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.get_tk_widget().config(bg=theme.CARD_BG, highlightthickness=0)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
