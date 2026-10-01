import tkinter as tk

from PIL import Image, ImageDraw

from gui import theme


class GradientButton(tk.Canvas):
    """A rounded button filled with a 2-color gradient, drawn on a Canvas."""

    VARIANTS = {
        "primary": (theme.ACCENT_PINK, theme.ACCENT_PINK),
        "secondary": (theme.CARD_BG_LIGHT, theme.CARD_BG_LIGHT),
        "danger": ("#ef4444", "#ef4444"),
        "accent": (theme.ACCENT_TEAL, theme.ACCENT_TEAL),
    }

    def __init__(self, parent, text, command=None, variant="primary", width=110, height=34,
                 radius=10, font=None, bg=None):
        bg = bg or theme.CARD_BG
        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0, bg=bg)
        self.command = command
        self._bw, self._bh, self._radius = width, height, radius
        self._font = font or theme.FONT_BODY_B
        c1, c2 = self.VARIANTS.get(variant, self.VARIANTS["primary"])
        self._photo = theme.to_photo(self._render(c1, c2))
        self._img_id = self.create_image(0, 0, anchor="nw", image=self._photo)
        self.text_id = self.create_text(width // 2, height // 2, text=text, fill="white", font=self._font)
        self.bind("<Button-1>", self._click)
        self.config(cursor="hand2")

    def _render(self, c1, c2):
        img = theme.make_gradient(self._bw, self._bh, c1, c2).convert("RGBA")
        mask = Image.new("L", (self._bw, self._bh), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, self._bw - 1, self._bh - 1), radius=self._radius, fill=255)
        img.putalpha(mask)
        return img

    def set_variant(self, variant):
        c1, c2 = self.VARIANTS.get(variant, self.VARIANTS["primary"])
        self._photo = theme.to_photo(self._render(c1, c2))
        self.itemconfig(self._img_id, image=self._photo)
        self.tag_raise(self.text_id)

    def set_text(self, text):
        self.itemconfig(self.text_id, text=text)

    def _click(self, _evt):
        if self.command:
            self.command()


class GlassCanvas(tk.Canvas):
    """A canvas painted with a gradient background, on top of which frosted
    'glass' cards can be placed via add_card(). Each card returns a plain
    tk.Frame that callers pack/grid their own widgets into."""

    def __init__(self, parent, width, height, c1=None, c2=None):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0)
        self._cw, self._ch = width, height
        self._bg_img = theme.make_gradient(width, height, c1 or theme.BG_TOP_LEFT, c2 or theme.BG_BOTTOM_RIGHT)
        self._bg_photo = theme.to_photo(self._bg_img)
        self.create_image(0, 0, anchor="nw", image=self._bg_photo)
        self._refs = []

    def add_card(self, x, y, w, h, radius=18, inset=8):
        glass = theme.make_glass_panel(self._bg_img, x, y, w, h, radius=radius)
        photo = theme.to_photo(glass)
        self._refs.append(photo)
        self.create_image(x, y, anchor="nw", image=photo)
        frame = tk.Frame(self, bg=theme.CARD_BG, bd=0)
        self.create_window(x + inset, y + inset, anchor="nw", window=frame,
                            width=w - 2 * inset, height=h - 2 * inset)
        return frame
