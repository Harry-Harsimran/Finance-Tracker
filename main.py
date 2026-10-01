import tkinter as tk
from tkinter import ttk

import db
from gui import theme
from gui.widgets import GradientButton
from gui.dashboard_tab import DashboardPage
from gui.expenses_tab import ExpensesPage
from gui.categories_tab import CategoriesPage
from gui.report_tab import ReportPage

WIN_W, WIN_H = 1100, 700
BANNER_H = 64
TABBAR_H = 54
CONTENT_H = WIN_H - BANNER_H - TABBAR_H


class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracker")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(bg=theme.BG_TOP_LEFT)
        self.selected_month = None

        db.init_db()

        style = ttk.Style(self)
        theme.configure_ttk(style)
        self.option_add("*TCombobox*Listbox.background", theme.CARD_BG_LIGHT)
        self.option_add("*TCombobox*Listbox.foreground", theme.TEXT_LIGHT)
        self.option_add("*TCombobox*Listbox.selectBackground", theme.ACCENT_PINK)

        banner_img = theme.make_gradient(WIN_W, BANNER_H, theme.ACCENT_PURPLE, theme.ACCENT_PURPLE)
        self._banner_photo = theme.to_photo(banner_img)
        banner = tk.Canvas(self, width=WIN_W, height=BANNER_H, highlightthickness=0, bd=0)
        banner.create_image(0, 0, anchor="nw", image=self._banner_photo)
        banner.create_text(24, BANNER_H // 2, anchor="w", text="\U0001F4B0  Personal Finance Tracker",
                            fill="white", font=theme.FONT_TITLE)
        banner.pack(fill="x")

        tabbar = tk.Frame(self, bg=theme.BG_TOP_LEFT, height=TABBAR_H)
        tabbar.pack(fill="x")
        tabbar.pack_propagate(False)
        self.tab_names = ["Dashboard", "Expenses", "Categories", "Report"]
        self.tab_buttons = {}
        for i, name in enumerate(self.tab_names):
            btn = GradientButton(tabbar, name, command=lambda n=name: self.show_tab(n),
                                  variant="secondary", width=160, height=38, radius=19,
                                  bg=theme.BG_TOP_LEFT)
            btn.pack(side="left", padx=(20 if i == 0 else 8, 0), pady=8)
            self.tab_buttons[name] = btn

        host = tk.Frame(self, width=WIN_W, height=CONTENT_H, bg=theme.BG_TOP_LEFT)
        host.pack(fill="both", expand=True)
        host.pack_propagate(False)

        self.dashboard = DashboardPage(host, self, WIN_W, CONTENT_H)
        self.expenses = ExpensesPage(host, self, WIN_W, CONTENT_H)
        self.categories = CategoriesPage(host, self, WIN_W, CONTENT_H)
        self.report = ReportPage(host, self, WIN_W, CONTENT_H)
        self.pages = {
            "Dashboard": self.dashboard, "Expenses": self.expenses,
            "Categories": self.categories, "Report": self.report,
        }
        for page in self.pages.values():
            page.place(x=0, y=0, width=WIN_W, height=CONTENT_H)

        self.show_tab("Dashboard")

    def show_tab(self, name):
        for n, btn in self.tab_buttons.items():
            btn.set_variant("primary" if n == name else "secondary")
        self.pages[name].tkraise()
        self.pages[name].refresh()

    def refresh_all(self):
        for p in self.pages.values():
            p.refresh()


if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
