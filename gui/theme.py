import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageTk

# ---------- palette ----------
BG_TOP_LEFT = "#0f172a"        # flat background (solid — see make_gradient note below)
BG_BOTTOM_RIGHT = "#0f172a"    # same as above = no gradient, solid color
ACCENT_PINK = "#6366f1"        # repurposed as the primary indigo accent (name is just a leftover identifier)
ACCENT_PURPLE = "#4f46e5"      # darker indigo, used for headings
ACCENT_BLUE = "#3b82f6"
ACCENT_TEAL = "#10b981"
ACCENT_AMBER = "#f59e0b"

CARD_BG = "#1e293b"           # flat card color
CARD_BG_LIGHT = "#334155"     # entry/combobox/treeview field color
TEXT_LIGHT = "#f1f5f9"
TEXT_MUTED = "#94a3b8"

CHART_PALETTE = ["#6366f1", "#a78bfa", "#60a5fa", "#34d399", "#fbbf24", "#f87171", "#38bdf8", "#c084fc"]

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_H = ("Segoe UI", 12, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BODY_B = ("Segoe UI", 10, "bold")
FONT_BIG = ("Segoe UI", 20, "bold")


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def make_gradient(w, h, c1=BG_TOP_LEFT, c2=BG_BOTTOM_RIGHT):
    """Diagonal linear gradient image, top-left c1 -> bottom-right c2."""
    w, h = max(1, w), max(1, h)
    a = np.array(_hex(c1), dtype=float)
    b = np.array(_hex(c2), dtype=float)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    t = (xx / max(w - 1, 1) + yy / max(h - 1, 1)) / 2
    arr = (a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]).astype("uint8")
    return Image.fromarray(arr, "RGB")


def make_glass_panel(bg_image, x, y, w, h, radius=14, blur=0, tint=None, border=None):
    """Flat solid rounded card (no blur, no transparency)."""
    panel = Image.new("RGBA", (w, h), (*_hex(CARD_BG), 255))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    panel.putalpha(mask)
    return panel


def to_photo(pil_img):
    return ImageTk.PhotoImage(pil_img)


def configure_ttk(style):
    style.theme_use("clam")
    style.configure("Glass.TEntry", fieldbackground=CARD_BG_LIGHT, foreground=TEXT_LIGHT,
                     insertcolor=TEXT_LIGHT, bordercolor=ACCENT_PURPLE,
                     lightcolor=CARD_BG_LIGHT, darkcolor=CARD_BG_LIGHT, padding=6)
    style.configure("Glass.TCombobox", fieldbackground=CARD_BG_LIGHT, background=CARD_BG_LIGHT,
                     foreground=TEXT_LIGHT, arrowcolor=TEXT_LIGHT, padding=6)
    style.map("Glass.TCombobox",
              fieldbackground=[("readonly", CARD_BG_LIGHT)],
              foreground=[("readonly", TEXT_LIGHT)])
    style.configure("Glass.Treeview", background=CARD_BG_LIGHT, fieldbackground=CARD_BG_LIGHT,
                     foreground=TEXT_LIGHT, rowheight=26, borderwidth=0, font=FONT_BODY)
    style.map("Glass.Treeview", background=[("selected", ACCENT_PINK)], foreground=[("selected", "white")])
    style.configure("Glass.Treeview.Heading", background=ACCENT_PURPLE, foreground="white",
                     font=FONT_BODY_B, borderwidth=0)
    style.map("Glass.Treeview.Heading", background=[("active", ACCENT_PURPLE)])
