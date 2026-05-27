import io, os, random
from datetime import date, timedelta
from pathlib import Path
import secrets

import numpy as np
from PIL import Image as PILImage, ImageDraw, ImageFont

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patheffects as pe
from matplotlib.patches import Arc

from core.analytics import get_consumer_profile, calculate_health_score
from core.report_generator import generate_weekly_report

_ROOT = Path(__file__).resolve().parent.parent
_ASSETS = _ROOT / "assets"
_FONTS = _ASSETS / "fonts"

# ==============================================================================
#  FONT SETUP
# ==============================================================================
_FONT_CANDIDATES = [
    str(_FONTS / "NaiBuErShouZhangTi-2.ttf"),
    str(_FONTS / "851ShouShu-2.ttf"),
    str(_FONTS / "ZCOOLKuaiLe.ttf"),
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
]
_usable_font = None
for _fp in _FONT_CANDIDATES:
    if os.path.exists(_fp):
        _usable_font = _fp
        break
if _usable_font is None:
    _usable_font = "C:/Windows/Fonts/msyh.ttc"

fm.fontManager.addfont(str(_FONTS / "NaiBuErShouZhangTi-2.ttf"))
fm.fontManager.addfont(str(_FONTS / "851ShouShu-2.ttf"))
try:
    _fp_obj = fm.FontProperties(fname=str(_FONTS / "NaiBuErShouZhangTi-2.ttf"))
    matplotlib.rcParams["font.sans-serif"] = ["MXNLSZ", "851tegakizatsu", "Microsoft YaHei", "SimHei"]
except Exception:
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

_BOLD_FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    str(_FONTS / "NaiBuErShouZhangTi-2.ttf"),
    str(_FONTS / "851ShouShu-2.ttf"),
    str(_FONTS / "ZCOOLKuaiLe.ttf"),
    "C:/Windows/Fonts/msyh.ttc",
]
_usable_bold_font = None
for _fp in _BOLD_FONT_CANDIDATES:
    if os.path.exists(_fp):
        _usable_bold_font = _fp
        break
if _usable_bold_font is None:
    _usable_bold_font = _usable_font

def _font(size):
    try:
        return ImageFont.truetype(_usable_font, int(size * _SCALE))
    except Exception:
        return ImageFont.load_default()

def _bold_font(size):
    try:
        return ImageFont.truetype(_usable_bold_font, int(size * _SCALE))
    except Exception:
        return _font(size)

# ==============================================================================
#  THEME — 13 character folders
# ==============================================================================
_CHAR_FOLDERS = [
    "starrail_cyy", "starrail_dht", "starrail_fj", "starrail_fy",
    "starrail_hsy", "starrail_xd",
    "ww_dny", "ww_fb", "ww_fll", "ww_jx", "ww_ktxy", "ww_qx", "ww_yn",
    "geshin_fnn",
]

_PALETTES = {
    "starrail_cyy": {"pri":"#A78BFA","light":"#F3F0FF","accent":"#FBBF24","bg":"#EDE9FE","bg2":"#DDD6FE","txt":"#3D2E5C","txt_l":"#6B5B95","tag":"#8B5CF6","border":"#C4B5FD","card":"#FFFFFF","header_bg":("#8B5CF6","#A78BFA"),"chart":["#A78BFA","#FBBF24","#EC4899","#06B6D4","#10B981","#F97316","#6366F1","#14B8A6","#EF4444","#84CC16"]},
    "starrail_dht": {"pri":"#7C3AED","light":"#F3F0FF","accent":"#F59E0B","bg":"#EDE9FE","bg2":"#DDD4F5","txt":"#322659","txt_l":"#7C5CB8","tag":"#7C3AED","border":"#C4B5FD","card":"#FFFFFF","header_bg":("#7C3AED","#A57AF7"),"chart":["#7C3AED","#F59E0B","#EC4899","#06B6D4","#10B981","#F97316","#6366F1","#14B8A6","#EF4444","#84CC16"]},
    "starrail_fj":   {"pri":"#6366F1","light":"#EEF2FF","accent":"#EAB308","bg":"#E8EAF6","bg2":"#D0D5F0","txt":"#28356A","txt_l":"#5C6DAC","tag":"#6366F1","border":"#BCC2E8","card":"#FFFFFF","header_bg":("#6366F1","#818CF8"),"chart":["#6366F1","#EAB308","#EC4899","#06B6D4","#10B981","#F97316","#A78BFA","#14B8A6","#EF4444","#84CC16"]},
    "starrail_fy":   {"pri":"#8B5CF6","light":"#F3F0FF","accent":"#F59E0B","bg":"#F5F0FF","bg2":"#DDD4F5","txt":"#3D2E5C","txt_l":"#7C6FA0","tag":"#8B5CF6","border":"#D4C5F0","card":"#FFFFFF","header_bg":("#8B5CF6","#A57AF7"),"chart":["#8B5CF6","#F59E0B","#EC4899","#06B6D4","#10B981","#F97316","#6366F1","#14B8A6","#EF4444","#84CC16"]},
    "starrail_hsy":  {"pri":"#9333EA","light":"#F5F0FF","accent":"#F59E0B","bg":"#F3E8FF","bg2":"#E0CCF5","txt":"#3B1E5C","txt_l":"#7B4FAC","tag":"#9333EA","border":"#CEB8F0","card":"#FFFFFF","header_bg":("#9333EA","#A855F7"),"chart":["#9333EA","#F59E0B","#EC4899","#06B6D4","#10B981","#F97316","#6366F1","#14B8A6","#EF4444","#84CC16"]},
    "starrail_xd":   {"pri":"#6D28D9","light":"#F3F0FF","accent":"#F97316","bg":"#F0EDFA","bg2":"#D8D0F3","txt":"#352660","txt_l":"#796ABA","tag":"#6D28D9","border":"#C8B8EB","card":"#FFFFFF","header_bg":("#6D28D9","#8B5CF6"),"chart":["#6D28D9","#F97316","#EC4899","#06B6D4","#10B981","#F59E0B","#6366F1","#14B8A6","#EF4444","#84CC16"]},
    "ww_dny":        {"pri":"#4F95D9","light":"#E8F2FE","accent":"#F472B6","bg":"#F0F6FF","bg2":"#D8E8F8","txt":"#1E3A5F","txt_l":"#5B7FA8","tag":"#4F95D9","border":"#BFD5F0","card":"#FFFFFF","header_bg":("#4F95D9","#7BAFE0"),"chart":["#4F95D9","#F472B6","#7EC8E3","#FFB347","#98D8C8","#B19CD9","#FFD93D","#6BCB77","#FF8B94","#A8D8EA"]},
    "ww_fb":         {"pri":"#3B82F6","light":"#EBF2FE","accent":"#F472B6","bg":"#F0F5FF","bg2":"#D8E4F8","txt":"#1C3D6B","txt_l":"#5C7DB8","tag":"#3B82F6","border":"#BFD5F0","card":"#FFFFFF","header_bg":("#3B82F6","#60A5FA"),"chart":["#3B82F6","#F472B6","#7EC8E3","#FFB347","#98D8C8","#B19CD9","#FFD93D","#6BCB77","#FF8B94","#A8D8EA"]},
    "ww_fll":        {"pri":"#2563EB","light":"#EAF0FE","accent":"#EC4899","bg":"#EFF4FF","bg2":"#D6E3F8","txt":"#193A6C","txt_l":"#4B6DAD","tag":"#2563EB","border":"#B8CAF0","card":"#FFFFFF","header_bg":("#2563EB","#3B82F6"),"chart":["#2563EB","#EC4899","#7EC8E3","#FFB347","#98D8C8","#B19CD9","#FFD93D","#6BCB77","#FF8B94","#A8D8EA"]},
    "ww_jx":         {"pri":"#0284C7","light":"#E0F2FE","accent":"#F97316","bg":"#F0F9FF","bg2":"#DBEAFE","txt":"#16385A","txt_l":"#3872A3","tag":"#0284C7","border":"#BAE0F5","card":"#FFFFFF","header_bg":("#0284C7","#38BDF8"),"chart":["#0284C7","#F97316","#7EC8E3","#FFB347","#98D8C8","#B19CD9","#FFD93D","#6BCB77","#FF8B94","#A8D8EA"]},
    "ww_ktxy":       {"pri":"#0EA5E9","light":"#E0F4FE","accent":"#E8789A","bg":"#F0F9FF","bg2":"#DAEFFA","txt":"#15425A","txt_l":"#427A9E","tag":"#0EA5E9","border":"#B8DEE8","card":"#FFFFFF","header_bg":("#0EA5E9","#38BDF8"),"chart":["#0EA5E9","#E8789A","#7EC8E3","#FFB347","#98D8C8","#B19CD9","#FFD93D","#6BCB77","#FF8B94","#A8D8EA"]},
    "ww_qx":         {"pri":"#E8789A","light":"#FFF0F5","accent":"#7BC67E","bg":"#FFF5FA","bg2":"#F8D8E4","txt":"#5D3A4A","txt_l":"#A07088","tag":"#E8789A","border":"#F0C5D5","card":"#FFFFFF","header_bg":("#E8789A","#F09AB4"),"chart":["#E8789A","#7BC67E","#FFB347","#87CEEB","#DDA0DD","#F0E68C","#FFA07A","#98FB98","#B0E0E6","#F8BBD0"]},
    "ww_yn":         {"pri":"#DB2777","light":"#FFF0F5","accent":"#34D399","bg":"#FFF2F6","bg2":"#F8D2E0","txt":"#5C2540","txt_l":"#9E4C70","tag":"#DB2777","border":"#F0B8D0","card":"#FFFFFF","header_bg":("#DB2777","#EC4899"),"chart":["#DB2777","#34D399","#FFB347","#87CEEB","#DDA0DD","#F0E68C","#FFA07A","#98FB98","#B0E0E6","#F8BBD0"]},
    "geshin_fnn":    {"pri":"#4A90D9","light":"#EBF5FF","accent":"#FFD700","bg":"#F0F8FF","bg2":"#D4E8F8","txt":"#1B3A5C","txt_l":"#4A7FA8","tag":"#4A90D9","border":"#B8D8F0","card":"#FFFFFF","header_bg":("#3A7BC8","#5BA0E8"),"chart":["#4A90D9","#FFD700","#5BC0EB","#FF8C69","#7EC8A0","#C490D1","#FFB347","#6BCB77","#87CEEB","#F0B8D0"]},
}

# ==============================================================================
#  ASSET LOADERS
# ==============================================================================

def _load_lines(folder):
    p = _ASSETS / folder / "Lines.txt"
    result = []
    if not p.exists():
        return result
    content = p.read_text(encoding="utf-8").strip()
    for raw in content.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        if raw.lower().endswith(":") and not raw.startswith(("1.", "2.", "3.")):
            continue
        if raw and raw[0].isdigit() and "." in raw[:3]:
            text = raw.split(".", 1)[1].strip()
            if text:
                result.append(text)
    return result

def _load_folder_images(folder):
    imgs = []
    d = _ASSETS / folder
    if not d.exists():
        return imgs
    for f in sorted(d.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        if f.stem == "Lines":
            continue
        try:
            pil = PILImage.open(str(f))
            w, h = pil.size
            imgs.append({
                "path": str(f), "stem": f.stem,
                "w": w, "h": h, "orient": "portrait" if h > w else "landscape",
            })
        except Exception:
            pass
    return imgs

def pick_assets():
    # Reseed from OS entropy so each report gets a truly independent random selection
    random.seed(secrets.randbits(128))
    folder = random.choice(_CHAR_FOLDERS)
    images = _load_folder_images(folder)
    quotes = _load_lines(folder)
    portrait = None
    landscapes = []
    for img in images:
        if img["orient"] == "portrait":
            if portrait is None and img["h"] / img["w"] > 1.15:
                portrait = img
            else:
                landscapes.append(img)
        else:
            landscapes.append(img)
    if portrait is None and landscapes:
        portrait = landscapes[0]
        landscapes = landscapes[1:] if len(landscapes) > 1 else []
    new_lands = []
    for img in landscapes:
        if img["path"] != (portrait["path"] if portrait else None):
            new_lands.append(img)
    landscapes = new_lands
    if len(landscapes) < 2 and portrait:
        for img in images:
            if img["path"] != (portrait["path"] if portrait else None) and img not in landscapes:
                landscapes.append(img)
                if len(landscapes) >= 2:
                    break
    if len(landscapes) < 2:
        for img in images:
            if img not in landscapes and img["path"] != (portrait["path"] if portrait else None):
                landscapes.append(img)
                if len(landscapes) >= 2:
                    break
    return {
        "folder": folder,
        "pal": _PALETTES.get(folder, _PALETTES["starrail_cyy"]),
        "portrait": portrait,
        "landscapes": landscapes[:2],
        "quotes": quotes,
    }

# ==============================================================================
#  ROUNDED CORNER
# ==============================================================================

def _rounded_image(pil_img, radius):
    if pil_img is None:
        return None
    w, h = pil_img.size
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")
    mask = PILImage.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (w - 1, h - 1)], radius=radius, fill=255)
    result = PILImage.new("RGBA", (w, h), (0, 0, 0, 0))
    result.paste(pil_img, (0, 0), mask)
    return result

# ==============================================================================
#  DECOR CACHE
# ==============================================================================
_DECOR_CACHE = {}

def _load_decor(name):
    if name in _DECOR_CACHE:
        return _DECOR_CACHE[name]
    fp = _ASSETS / (name + ".png")
    if not fp.exists():
        _DECOR_CACHE[name] = None
        return None
    try:
        _DECOR_CACHE[name] = PILImage.open(fp).convert("RGBA")
        return _DECOR_CACHE[name]
    except Exception:
        _DECOR_CACHE[name] = None
        return None

def _put_decor(cv, name, x, y, w, h, alpha=1.0):
    img = _load_decor(name)
    if img is None:
        return
    try:
        rs = img.resize((int(w * _SCALE), int(h * _SCALE)), PILImage.LANCZOS)
        if alpha < 1.0:
            r, g, b, a = rs.split()
            a = a.point(lambda p: int(p * alpha))
            rs = PILImage.merge("RGBA", (r, g, b, a))
        cv.paste(rs, (int(x * _SCALE), int(y * _SCALE)), rs)
    except Exception:
        pass

# ==============================================================================
#  IMAGE CACHE
# ==============================================================================
_RESIZE_CACHE = {}

def _load_pil(img_info, max_w=2400):
    if img_info is None:
        return None
    path = img_info["path"]
    key = (path, max_w)
    if key in _RESIZE_CACHE:
        return _RESIZE_CACHE[key]
    try:
        pil = PILImage.open(path).convert("RGBA")
        if pil.width > max_w:
            ratio = max_w / pil.width
            pil = pil.resize((max_w, int(pil.height * ratio)), PILImage.LANCZOS)
        _RESIZE_CACHE[key] = pil
        return pil
    except Exception:
        return None

def _load_pil_rounded(img_info, max_w=1800, radius=36):
    pil = _load_pil(img_info, max_w)
    if pil is None:
        return None
    return _rounded_image(pil, radius)

# ==============================================================================
#  REPORT CANVAS
# ==============================================================================
class ReportCanvas:
    def __init__(self, w, h=8000):
        self.w = w
        self.h = h
        self.M = 90
        self.uw = self.w - self.M * 2
        self._iw = int(w * _SCALE)
        self._ih = int(h * _SCALE)
        self.img = PILImage.new("RGBA", (self._iw, self._ih), (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.y = 0

    def set_margins(self, m):
        self.M = m
        self.uw = self.w - m * 2

    def crop(self):
        py = min(self.y + 60, self.h)
        img = self.img.crop((0, 0, self._iw, int(py * _SCALE)))
        return img.resize((self.w, int(py)), PILImage.LANCZOS)

    def _s(self, v):
        return int(v * _SCALE)

    def fill_bg(self, rgb):
        self.draw.rectangle([(0, 0), (self._iw, self._ih)], fill=rgb + (255,))

    def paste_bg(self, pil_img, alpha=0.25):
        if pil_img is None:
            return
        cw = self._iw
        iw, ih = pil_img.size
        scale = min(cw / iw, 1.0)
        nw, nh = int(iw * scale), int(ih * scale)
        if nw < cw:
            nw, nh = int(nw * 1.05), int(nh * 1.05)
        resized = pil_img.resize((nw, nh), PILImage.LANCZOS)
        r, g, b, a = resized.split()
        a = a.point(lambda p: int(p * alpha))
        faded = PILImage.merge("RGBA", (r, g, b, a))
        x_pos = (self._iw - nw) // 2
        self.img.paste(faded, (x_pos, 0), faded)

    def paste_bg_full(self, pil_img, alpha=0.92):
        if pil_img is None:
            return
        iw, ih = pil_img.size
        cw = self._iw
        scale = cw / iw
        nw = int(iw * scale)
        nh = int(ih * scale)
        if nw < cw:
            nw = int(nw * 1.05)
            nh = int(ih * nw / iw)
        resized = pil_img.resize((nw, nh), PILImage.LANCZOS)
        if alpha < 1.0:
            r, g, b, a_ch = resized.split()
            a_ch = a_ch.point(lambda p: int(p * alpha))
            resized = PILImage.merge("RGBA", (r, g, b, a_ch))
        x_pos = (cw - nw) // 2
        self.img.paste(resized, (x_pos, 0), resized)

    def rounded_rect(self, x, y, w, h, r, fill=None, border=None, bw=1):
        sx, sy, sw, sh = self._s(x), self._s(y), self._s(w), self._s(h)
        box = (sx, sy, sx + sw, sy + sh)
        if fill:
            self.draw.rounded_rectangle(box, radius=self._s(r), fill=fill)
        if border:
            self.draw.rounded_rectangle(box, radius=self._s(r), outline=border, width=self._s(bw))

    def text(self, x, y, txt, font, color, anchor="la"):
        self.draw.text((self._s(x), self._s(y)), str(txt), font=font, fill=color, anchor=anchor)

    def text_mid(self, txt, font, color):
        self.draw.text((self._iw / 2, self._s(self.y)), str(txt), font=font, fill=color, anchor="ma")
        self.y += self._texth(str(txt), font) + 10

    def text_height(self, txt, font):
        bbox = font.getbbox(str(txt))
        return (bbox[3] - bbox[1]) / _SCALE

    _texth = text_height

    def wrap_text(self, txt, font, max_w):
        lines = []
        scaled_max_w = max_w * _SCALE
        for p in str(txt).split("\n"):
            if not p:
                lines.append("")
                continue
            line = ""
            for ch in p:
                if font.getlength(line + ch) > scaled_max_w:
                    if line:
                        lines.append(line)
                    line = ch
                else:
                    line += ch
            if line:
                lines.append(line)
        return lines

    def draw_block(self, x, y, txt, font, color, max_w, spacing=6):
        lines = self.wrap_text(txt, font, max_w)
        lh = self._texth("测", font) + spacing
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, font, color)
        return len(lines) * lh

    def _center_img(self, pil_img, w_ratio, h_ratio, alpha=1.0):
        if pil_img is None:
            return 0
        max_w = int(self.uw * w_ratio)
        max_h = int(max_w * h_ratio)
        piw, pih = pil_img.size
        s = min(max_w / piw, max_h / pih)
        nw, nh = int(piw * s), int(pih * s)
        rs = pil_img.resize((self._s(nw), self._s(nh)), PILImage.LANCZOS)
        if rs.mode != "RGBA":
            rs = rs.convert("RGBA")
        if alpha < 1.0:
            r, g, b, a_ch = rs.split()
            a_ch = a_ch.point(lambda p: int(p * alpha))
            rs = PILImage.merge("RGBA", (r, g, b, a_ch))
        x = (self._iw - self._s(nw)) // 2
        self.img.paste(rs, (int(x), self._s(self.y)), rs)
        self.y += nh + 14
        return nh

    def image(self, x, y, pil_img, max_w, max_h, cr=0):
        if pil_img is None:
            return 0, 0
        iw, ih = pil_img.size
        s = min(max_w / iw, max_h / ih)
        nw, nh = int(iw * s), int(ih * s)
        rs = pil_img.resize((self._s(nw), self._s(nh)), PILImage.LANCZOS)
        if rs.mode != "RGBA":
            rs = rs.convert("RGBA")
        if cr > 0:
            rs = _rounded_image(rs, self._s(cr))
        self.img.paste(rs, (self._s(x), self._s(y)), rs)
        return nw, nh

    def chart(self, x, y, buf, max_w, max_h):
        buf.seek(0)
        return self.image(x, y, PILImage.open(buf).convert("RGBA"), max_w, max_h)

    def section(self, text, pal):
        self.y += 6
        # subtle background band (semi-transparent)
        self.rounded_rect(self.M, self.y, self.uw, 40, 8, fill=_hex_rgba(pal["light"], 90))
        # accent bar
        self.rounded_rect(self.M + 4, self.y + 5, 8, 30, 4, fill=pal["pri"])
        self.text(self.M + 22, self.y + 6, text, _bold_font(28), pal["txt"])
        self.y += 50

    def cards(self, data, pal, gap=20):
        n = len(data)
        cw = (self.uw - gap * (n - 1)) / n
        ch = 120
        for i, (label, value) in enumerate(data):
            cx = self.M + i * (cw + gap)
            # soft shadow (very faint)
            self.rounded_rect(cx + 2, self.y + 2, cw, ch, 16, fill=_hex_rgba(pal["border"], 50))
            # card body (semi-transparent white)
            self.rounded_rect(cx, self.y, cw, ch, 16, fill=(255, 255, 255, 140), border=_hex_rgba(pal["border"], 100), bw=1)
            dc = pal["chart"][i % len(pal["chart"])]
            # accent bar
            self.rounded_rect(cx + 16, self.y + 20, 12, ch - 40, 6, fill=_hex_rgba(dc, 180))
            self.text(cx + 40, self.y + 20, label, _font(18), pal["txt_l"])
            self.text(cx + cw - 22, self.y + 62, str(value), _bold_font(30), pal["txt"], "ra")
        self.y += ch + 18

    def quote(self, pal, quotes):
        if not quotes:
            return
        q = random.choice(quotes)
        txt = f"「{q}」"
        font = _font(22)
        mw = self.w - 200
        while font.getlength(txt) > mw * _SCALE and len(txt) > 15:
            txt = txt[:-1] + "…"
        # subtle background band behind quote (very faint)
        txt_w = int(font.getlength(txt) / _SCALE) + 60
        qx = (self.w - txt_w) // 2
        self.rounded_rect(qx, self.y - 8, txt_w, 42, 12, fill=_hex_rgba(pal["light"], 60))
        # decorative left quote mark
        self.draw.text((self._s(qx + 10), self._s(self.y - 4)), "❝", font=_bold_font(20), fill=_hex_rgba(pal["accent"], 180), anchor="la")
        self.draw.text((self._iw / 2, self._s(self.y)), txt, font=font, fill=pal["pri"], anchor="ma")
        self.y += 46

    def fmt_divider(self, pal):
        img = _load_decor("wavy_divider")
        if img:
            iw, ih = img.size
            h = int(ih * self.uw / iw)
            resized = img.resize((self._s(self.uw), self._s(h)), PILImage.LANCZOS)
            self.img.paste(resized, (self._s(self.M), self._s(self.y)), resized)
            self.y += h + 12
        else:
            self.y += self.divider(pal["border"])

    def divider(self, color, t=3):
        my = self._s(self.y + t // 2)
        self.draw.line(
            [(self._s(self.M), my), (self._s(self.M + self.uw), my)],
            fill=color, width=self._s(t),
        )
        self.y += t + 14

    def footer(self, pal):
        self.y += 12
        footers = [
            "记账本 · 用心记录每一笔",
            "记账本 · 让每一分钱都有故事",
            "记账本 · 你的财务小管家",
            "记账本 · 数字会说话",
        ]
        self.draw.text((self._iw / 2, self._s(self.y)), random.choice(footers), font=_font(20), fill=pal["txt_l"], anchor="ma")
        self.y += 36

    def header(self, pal, title, sub):
        hh = 160
        c1 = _hex_to_rgb(pal["header_bg"][0])
        c2 = _hex_to_rgb(pal["header_bg"][1])
        shh = self._s(hh)
        for i in range(shh):
            t = i / max(shh - 1, 1)
            color = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
            self.draw.line([(0, i), (self._iw, i)], fill=color + (255,))
        self.draw.text((self._iw / 2, self._s(38)), title, font=_bold_font(48), fill="#FFFFFF", anchor="ma")
        self.draw.text((self._iw / 2, self._s(95)), sub, font=_font(22), fill="#FFFFFFDD", anchor="ma")
        self.y = hh + 20


# ==============================================================================
#  BACKGROUND HELPER
# ==============================================================================

def _apply_bg(result_img, pil_img):
    """Paste pil_img as single full background behind the (RGBA) result."""
    if pil_img is None:
        return result_img.convert("RGB")
    iw, ih = pil_img.size
    rw, rh = result_img.size
    scale = max(rw / iw, rh / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    bg = pil_img.resize((nw, nh), PILImage.LANCZOS).convert("RGBA")
    x = (rw - nw) // 2
    y = (rh - nh) // 2
    final = PILImage.new("RGBA", (rw, rh), (255, 255, 255, 0))
    final.paste(bg, (x, y))
    final.paste(result_img, (0, 0), result_img)
    return final.convert("RGB")


# ==============================================================================
#  CHARTS (transparent bg)
# ==============================================================================
_DPI = 800

_SCALE = 2

def _donut(data, pal, total=0, size=(5.0, 3.8)):
    fig, ax = plt.subplots(figsize=size, dpi=_DPI)
    labels = [d[0] for d in data]
    vals = [d[1] for d in data]
    cc = pal["chart"]
    w, _, autotexts = ax.pie(vals, labels=None,
        autopct=lambda p: f"{p:.0f}%" if p > 5 else "",
        colors=cc[:len(data)], startangle=140, pctdistance=0.75,
        textprops={"fontsize":13,"color":"white","fontweight":"bold"},
        wedgeprops={"linewidth":3,"edgecolor":"white","width":0.40},
        explode=[0.01]*len(data))
    # fix percentage label visibility on light segments
    for i, at in enumerate(autotexts):
        r, g, b = _hex_to_rgb(cc[i % len(cc)])
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum > 180:
            at.set_color("#333333")
    if total > 0:
        ax.text(0, 0.08, f"¥{total:,.0f}", ha="center", va="center", fontsize=18, fontweight="bold", color=pal["txt"])
        ax.text(0, -0.12, "总支出", ha="center", va="center", fontsize=12, color=pal["txt_l"])
    lg = ax.legend(w, labels, loc="center left", bbox_to_anchor=(1,0,0.5,1), fontsize=12, frameon=False)
    for t in lg.get_texts(): t.set_color(pal["txt"])
    fig.patch.set_alpha(0); ax.set_facecolor("none"); fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight", transparent=True); plt.close(fig)
    buf.seek(0); return buf

def _line(months, inc, exp, pal, size=(8.0,3.8)):
    fig, ax = plt.subplots(figsize=size, dpi=_DPI)
    x = np.arange(len(months)); cc = pal["chart"]
    ax.fill_between(x, 0, inc, alpha=0.10, color=cc[0])
    ax.fill_between(x, 0, exp, alpha=0.10, color=cc[1])
    ax.plot(x, inc, "o-", color=cc[0], label="收入", lw=2.8, ms=10, markeredgecolor="white", markeredgewidth=2, zorder=5)
    ax.plot(x, exp, "o-", color=cc[1], label="支出", lw=2.8, ms=10, markeredgecolor="white", markeredgewidth=2, zorder=5)
    if inc and max(inc)>0:
        mi = max(inc); ii = inc.index(mi)
        ax.annotate(f"¥{mi:,.0f}", (x[ii], mi), textcoords="offset points", xytext=(0,14), ha="center", fontsize=11, color=cc[0])
    if exp and max(exp)>0:
        me = max(exp); ie = exp.index(me)
        ax.annotate(f"¥{me:,.0f}", (x[ie], me), textcoords="offset points", xytext=(0,14), ha="center", fontsize=11, color=cc[1])
    ax.set_xticks(x); ax.set_xticklabels(months, fontsize=12, color=pal["txt"])
    lg = ax.legend(fontsize=13, frameon=True, fancybox=True, framealpha=0.6)
    for t in lg.get_texts(): t.set_color(pal["txt"])
    ax.grid(axis="y", alpha=0.10, linestyle="--")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(pal["border"]); ax.spines["left"].set_color(pal["border"])
    ax.tick_params(colors=pal["txt_l"])
    fig.patch.set_alpha(0); ax.set_facecolor("none"); fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight", transparent=True); plt.close(fig)
    buf.seek(0); return buf

def _hbar(labels, values, pal, size=(7.0,3.0)):
    fig, ax = plt.subplots(figsize=size, dpi=_DPI)
    y = np.arange(len(labels)); cc = pal["chart"]
    cols = [cc[i%len(cc)] for i in range(len(labels))]
    bars = ax.barh(y, values, color=cols, edgecolor="white", lw=1.5, height=0.50, capstyle="round")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=12, color=pal["txt"]); ax.invert_yaxis()
    mv = max(values) if values else 1
    for bar, val in zip(bars, values):
        ax.text(bar.get_width()+mv*0.02, bar.get_y()+bar.get_height()/2, f"¥{val:,.0f}", va="center", fontsize=11, color=pal["txt"])
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(left=False, colors=pal["txt_l"]); ax.grid(axis="x", alpha=0.08, linestyle="--")
    fig.patch.set_alpha(0); ax.set_facecolor("none"); fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight", transparent=True); plt.close(fig)
    buf.seek(0); return buf

def _gauge(score, hd=None, pal=None, size=(5.0,2.4)):
    if pal is None: pal = _PALETTES["starrail_cyy"]
    gc = "#4CAF50" if score>=80 else ("#2196F3" if score>=60 else ("#FF9800" if score>=40 else "#F44336"))
    hb = hd and "breakdown" in hd
    if hb:
        fig = plt.figure(figsize=size, dpi=_DPI)
        ag = fig.add_axes([0.04,0.28,0.38,0.68])
        ab = fig.add_axes([0.50,0.06,0.47,0.88])
    else:
        fig, ag = plt.subplots(figsize=size, dpi=_DPI); ab = None
    ag.add_patch(Arc((0.5,0.4),0.8,0.8,theta1=225,theta2=-45,color="#D0D0D0",lw=13,capstyle="round"))
    if score>0:
        sw = score/100*270
        ag.add_patch(Arc((0.5,0.4),0.8,0.8,theta1=225,theta2=225+sw,color=gc,lw=13,capstyle="round"))
    # score text with shadow for readability
    ag.text(0.5,0.36,str(score),ha="center",va="center",fontsize=36,fontweight="bold",color=gc,
            path_effects=[pe.withStroke(linewidth=4, foreground="white")])
    ag.text(0.5,0.10,"健康评分",ha="center",va="center",fontsize=11,color=pal["txt_l"])
    ag.set_xlim(0,1); ag.set_ylim(0,1); ag.axis("off"); ag.set_facecolor("none")
    if ab and hb:
        bd=hd["breakdown"]; ll,sl,ml=[],[],[]
        for k in ["savings","coverage","consistency","diversity"]:
            if k in bd: ll.append(bd[k]["label"]); sl.append(bd[k]["score"]); ml.append(bd[k]["max"])
        by = np.arange(len(ll))
        for i,(_,sc,mx) in enumerate(zip(ll,sl,ml)):
            p=sc/mx if mx>0 else 0
            ab.barh(i,p,height=0.40,color=gc,alpha=0.7,edgecolor="none")
            ab.text(p+0.03,i,f"{sc}/{mx}",va="center",fontsize=10,color=pal["txt"])
        ab.set_yticks(by); ab.set_yticklabels(ll,fontsize=11,color=pal["txt"])
        ab.set_xlim(0,1.35); ab.invert_yaxis()
        for s in ab.spines.values(): s.set_visible(False)
        ab.tick_params(bottom=False,left=False); ab.set_xticks([]); ab.set_facecolor("none")
    fig.patch.set_alpha(0)
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight", transparent=True); plt.close(fig)
    buf.seek(0); return buf

def _wday(bills, pal, size=(5.0,1.8)):
    dn = ["一","二","三","四","五","六","日"]; dt=[0.0]*7
    for b in bills:
        wd = b.bill_date.weekday() if hasattr(b.bill_date,"weekday") else 0
        dt[wd] += b.amount
    if max(dt)==0: return None
    fig, ax = plt.subplots(figsize=size, dpi=_DPI); cc=pal["chart"]
    mi=dt.index(max(dt))
    cols = [pal["accent"] if i==mi else cc[i%len(cc)] for i in range(7)]
    bars=ax.bar(range(7),dt,color=cols,edgecolor="white",lw=1.5,width=0.55)
    ax.set_xticks(range(7)); ax.set_xticklabels([f"周{d}" for d in dn],fontsize=11,color=pal["txt"])
    for bar,val in zip(bars,dt):
        if val>0: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(dt)*0.03, f"¥{val:,.0f}", ha="center", fontsize=10, color=pal["txt"])
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(pal["border"]); ax.spines["left"].set_color(pal["border"])
    ax.tick_params(colors=pal["txt_l"]); ax.grid(axis="y",alpha=0.08,linestyle="--")
    fig.patch.set_alpha(0); ax.set_facecolor("none"); fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight", transparent=True); plt.close(fig)
    buf.seek(0); return buf

def _spk(daily, pal, size=(5.0,1.4)):
    if not daily or len(daily)<2: return None
    fig,ax=plt.subplots(figsize=size,dpi=_DPI); x=np.arange(len(daily)); v=[d[1] for d in daily]
    ax.fill_between(x,v,alpha=0.15,color=pal["pri"]); ax.plot(x,v,color=pal["pri"],lw=2.2,zorder=3)
    mi=v.index(max(v)); ni=v.index(min(v))
    ax.plot(mi,v[mi],"o",color=pal["accent"],ms=6,zorder=4)
    ax.plot(ni,v[ni],"o",color="#66BB6A",ms=6,zorder=4)
    if v[mi]>0: ax.annotate(f"¥{v[mi]:,.0f}",(mi,v[mi]),textcoords="offset points",xytext=(5,10),fontsize=9,color=pal["accent"])
    ax.axis("off"); fig.patch.set_alpha(0); ax.set_facecolor("none"); fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=_DPI, bbox_inches="tight", transparent=True); plt.close(fig)
    buf.seek(0); return buf

# ==============================================================================
#  HELPERS
# ==============================================================================

def _spending_math(total_exp, cat_data):
    items = []
    if total_exp <= 0: return items
    pool = [
        (30, 1, "杯咖啡"), (15, 5, "杯奶茶"), (50, 2, "场电影"),
        (40, 3, "本书"), (8, 3, "顿外卖"), (120, 1, "次打车"),
        (25, 3, "杯果汁"), (60, 1, "顿火锅"), (200, 1, "件衣服"),
        (35, 2, "份甜品"), (18, 3, "包零食"), (45, 1, "次理发"),
    ]
    random.shuffle(pool)
    for price, min_n, label in pool:
        n = int(total_exp / price)
        if n >= min_n:
            items.append(f"{n}{label}")
        if len(items) >= 3:
            break
    if cat_data:
        for name, val in cat_data:
            if name == "餐饮" and val > 500:
                items.append(f"够吃{int(val/30)}顿饭")
                break
            if name == "交通" and val > 300:
                items.append(f"打车{int(val/15)}次")
                break
    return items[:4]

def _money_quote(sr):
    if sr > 50:
        return random.choice([
            "你的钱包比你更会养生。",
            "储蓄率爆表！你是藏钱界的隐藏BOSS。",
            "财务自由的路上，你已经走了一半。",
            "这个储蓄率，巴菲特看了都要点赞。",
            "你的存钱速度，比外卖小哥还快。",
            "钱在你手里，比在银行还安心。",
        ])
    elif sr > 20:
        return random.choice([
            "还不错，继续保持！",
            "你的财务健康状态——小康水平。",
            "收入和支出在跳双人舞，节奏不错。",
            "收支平衡，稳如老司机。",
            "你的钱包正在慢慢变胖，继续保持！",
            "存钱如登山，你已经到了半山腰。",
        ])
    elif sr > 0:
        return random.choice([
            "月光贫族附近，小心别过界哦。",
            "钱包在哭泣，但还没有绝望。",
            "每一笔花费都是你的选择，不过……也许可以少选几次？",
            "收支勉强打平，像走钢丝一样刺激。",
            "你的钱包在喊：主人，手下留情！",
            "钱：我来了，我又走了。",
        ])
    else:
        return random.choice([
            "财务红灯亮起来了！是时候制定计划了。",
            "别担心，每一次记录都是改变的开始。",
            "今天的花费，是明天的经验值。",
            "钱包已阵亡，但记账的习惯还在。",
            "入不敷出不可怕，可怕的是不知道钱花哪了。",
            "先止血，再疗伤，财务康复从今天开始。",
        ])

def _yearly_tips(sr):
    pool = [
        "📝 坚持记账是财务自律的第一步，新的一年继续加油！",
        "💡 每月初做一次预算，月底复盘，收支会更清晰。",
        "🏦 把储蓄看作给自己的\"工资\"，先存后花是黄金法则。",
        "🛒 大额消费前给自己24小时冷静期，冲动会自然消退。",
        "📊 关注消费结构比只看总金额更重要，找到你的\"拿铁因子\"。",
        "🎯 设定一个可量化的小目标，比如\"每月餐饮不超2000\"。",
        "🍳 周末自己做饭不仅能省钱，还能收获满满的成就感。",
        "📱 定期检查订阅服务，那些自动续费的小额支出积少成多。",
        "🚇 如果能用公共交通代替打车，一年能省下一趟旅行。",
        "💳 减少信用卡分期，利息虽小累积起来也是一笔开销。",
        "🎁 送礼重在心意而非价格，手工礼物往往更打动人。",
        "📚 投资自己是最好的投资，但也要关注投入产出比。",
        "🛡️ 建立应急基金，3-6个月生活费的安全垫让人安心。",
        "🌟 记账不是为了限制消费，而是让每一笔钱都花得值得。",
        "📈 尝试用闲钱做小额理财，让钱为你工作而不是只躺在账户里。",
    ]
    if sr > 40:
        pool += [
            "🏆 你的储蓄率很棒！可以考虑把部分存款投入稳健理财产品。",
            "💰 储蓄是手段不是目的，适当提升生活品质也很重要哦。",
        ]
    elif sr < 15:
        pool += [
            "⚠️ 储蓄率偏低，试着找出最大的支出项并设立上限。",
            "🔍 回顾过去三个月的账单，看看哪些支出是\"想要\"而非\"需要\"。",
        ]
    return random.sample(pool, min(3, len(pool)))

def _day_pattern(db, start, end):
    daily = db.get_daily_trend(start, end)
    if not daily:
        return None
    try:
        dt = {str(d[0]): float(d[1]) + float(d[2]) for d in daily if len(d) >= 3}
    except (IndexError, TypeError, ValueError):
        return None
    if not dt:
        return None
    sd = sorted(dt.items(), key=lambda x: x[1], reverse=True)
    total = sum(v for _, v in dt.items())
    days = len(daily)
    bills = db.get_bills(start_date=start, end_date=end, bill_type="expense", limit=500)
    return {"max_day":sd[0] if sd else ("",0),"min_day":sd[-1] if sd else ("",0),"active_days":days,"avg":total/max(days,1),"total":total,"bills":bills,"daily_data":sorted(dt.items())}

def _week_comparison(db, start, end):
    span = (end - start).days
    prev_start = start - timedelta(days=span+1)
    prev_end = start - timedelta(days=1)
    cur = db.get_summary(start, end)
    prev = db.get_summary(prev_start, prev_end)
    ce, pe = cur.total_expense, prev.total_expense
    chg = round((ce-pe)/pe*100) if pe>0 else 0
    return {"cur_income":cur.total_income,"cur_expense":ce,"prev_income":prev.total_income,"prev_expense":pe,"change_pct":chg,"direction":"up" if chg>0 else ("down" if chg<0 else "same")}

def _streak_info(db, start, end):
    today = date.today()
    days = min((end-start).days+1, (today-start).days+1)
    active_dates = db.get_days_with_bills(start, min(end, today))
    record = sum(1 for d in range(days) if (start+timedelta(days=d)).isoformat() in active_dates)
    return {"record":record,"total":days,"pct":round(record/max(days,1)*100)}

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

def _hex_rgba(h, alpha):
    """Convert hex color to RGBA tuple with given alpha (0-255)."""
    return _hex_to_rgb(h) + (alpha,)


# ==============================================================================
#  WEEKLY REPORT
# ==============================================================================

def generate_weekly_report_png(db, filepath, folder=None, target_date=None):
    global _RESIZE_CACHE, _DECOR_CACHE
    _RESIZE_CACHE = {}; _DECOR_CACHE = {}

    assets = pick_assets()
    pal = assets["pal"]
    # Calculate week_offset based on target_date
    week_offset = 0
    if target_date is not None:
        today = date.today()
        current_monday = today - timedelta(days=today.weekday())
        target_monday = target_date - timedelta(days=target_date.weekday())
        week_offset = (target_monday - current_monday).days // 7
    report = generate_weekly_report(db, week_offset)
    quotes = assets["quotes"]
    portrait = _load_pil(assets["portrait"], max_w=2400)
    l0 = _load_pil_rounded(assets["landscapes"][0], max_w=1400, radius=36) if assets["landscapes"] else None
    l1 = _load_pil_rounded(assets["landscapes"][1], max_w=1400, radius=36) if len(assets["landscapes"])>1 else None

    W = 2000; M = 90
    c = ReportCanvas(W); c.set_margins(M)

    if not report or (report["total_income"]==0 and report["total_expense"]==0):
        c.header(pal, "本周消费手帐", report["week_label"] if report else date.today().isoformat())
        c.y += 20
        if l0: c._center_img(l0, 0.60, 0.40, alpha=0.88)
        c.text(W/2, c.y, "这周还没有记账呢~", _font(32), pal["txt_l"], "ma")
        c.y += 50; c.quote(pal, quotes); c.y += 12; c.footer(pal)
        _put_decor(c.img, "kawaii_piggy", W-100, c.y-60, 80, 80)
        img = c.crop(); result = _apply_bg(img, portrait); result.save(filepath, "PNG"); plt.close("all"); return filepath

    sign = "+" if report["balance"]>=0 else "-"
    sr = report["savings_rate"]

    c.header(pal, "✦ 本周消费手帐 ✦", report["week_label"])

    # --- hero image + caption ---
    if l0:
        c._center_img(l0, 0.82, 0.46, alpha=0.88)
        c.quote(pal, quotes)

    # --- cards ---
    c.cards([
        ("总收入", f"¥{report['total_income']:,.0f}"),
        ("总支出", f"¥{report['total_expense']:,.0f}"),
        ("结余", f"{sign}¥{abs(report['balance']):,.0f}"),
        ("储蓄率", f"{sr:.1f}%"),
    ], pal)

    # --- week comparison ---
    comp = _week_comparison(db, report["week_start"], report["week_end"])
    arrow = "↑" if comp["direction"]=="up" else ("↓" if comp["direction"]=="down" else "→")
    ct = f"📊  较上周 {arrow} {abs(comp['change_pct'])}%   |   上周 ¥{comp['prev_expense']:,.0f}  →  本周 ¥{comp['cur_expense']:,.0f}"
    c.rounded_rect(M, c.y, c.uw, 58, 14, fill=_hex_rgba(pal["light"], 80), border=_hex_rgba(pal["border"], 80), bw=1)
    c.text(M+28, c.y+15, ct, _font(20), pal["txt"])
    _put_decor(c.img, "chart_up", M+c.uw-60, c.y+13, 38, 38)
    c.y += 78

    # --- donut + category bars ---
    cat_data = db.get_category_summary(report["week_start"], report["week_end"], "expense")
    total_exp = sum(v for _, v in cat_data) if cat_data else 0

    if cat_data and total_exp>0:
        c.section("钱钱去哪儿了", pal)
        dbuf = _donut(cat_data, pal, total=total_exp, size=(5.5, 4.0))
        dw = int(c.uw * 0.40); dh = int(dw * 0.73)
        cat_x = M + dw + 30; cat_w = c.uw - dw - 30
        cy2 = c.y
        for i, (name, val) in enumerate(cat_data[:6]):
            pct = val / total_exp * 100
            color = pal["chart"][i % len(pal["chart"])]
            c.rounded_rect(cat_x, cy2+6, 14, 14, 3, fill=color)
            c.text(cat_x+24, cy2, name, _font(20), pal["txt"])
            c.text(cat_x+cat_w, cy2, f"¥{val:,.0f}  {pct:.0f}%", _bold_font(20), pal["txt"], "ra")
            cy2 += 38
            fw = max(18, int(cat_w * pct / 100))
            c.rounded_rect(cat_x, cy2, cat_w, 22, 11, fill=_hex_rgba(pal["border"], 100))
            c.rounded_rect(cat_x, cy2, fw, 22, 11, fill=color)
            cy2 += 40
        c.chart(M, c.y, dbuf, dw, dh)
        c.y = max(c.y + dh + 14, cy2 + 6)

    fun = _spending_math(total_exp, cat_data)
    if fun:
        c.text(M, c.y, "💡  "+"  |  ".join(fun[:4]), _font(18), pal["txt_l"])
        c.y += 38

    # --- daily rhythm ---
    dp = _day_pattern(db, report["week_start"], report["week_end"])
    if dp and dp["max_day"][0]:
        c.section("每日消费节奏", pal)
        max_d, max_v = dp["max_day"]; min_d, min_v = dp["min_day"]
        c.text(M, c.y, f"活跃 {dp['active_days']} 天 · 最高 {max_d} ¥{max_v:,.0f} · 最低 {min_d} ¥{min_v:,.0f} · 日均 ¥{dp['avg']:,.0f}", _font(17), pal["txt_l"])
        c.y += 38
        charts = []
        if dp.get("bills"):
            wb = _wday(dp["bills"], pal, size=(5.0, 1.6))
            if wb: charts.append(wb)
        if dp.get("daily_data") and len(dp["daily_data"])>1:
            sb = _spk(dp["daily_data"], pal, size=(5.0, 1.2))
            if sb: charts.append(sb)
        if len(charts)==2:
            hw = (c.uw - 24)/2
            c.chart(M, c.y, charts[0], hw, 180)
            c.chart(M+hw+24, c.y, charts[1], hw, 140)
            c.y += 190
        elif charts:
            c.chart(M, c.y, charts[0], c.uw, 180)
            c.y += 190

    # --- health + 2nd image ---
    profile = get_consumer_profile(db)
    health = calculate_health_score(db)

    c.section("财务健康与消费人格", pal)

    gbuf = _gauge(health["score"], health, pal, size=(5.0, 2.4))
    gw = int(c.uw * 0.36); gh = int(gw * 0.48)
    c.chart(M, c.y, gbuf, gw, gh)
    # kawaii_wallet decoration next to gauge
    _put_decor(c.img, "kawaii_wallet", M + gw + 20, c.y + gh - 60, 70, 70)
    iy = c.y + gh + 14
    c.text(M, iy, f"🎭  {profile['emoji']}  {profile['title']}", _bold_font(26), pal["txt"])
    c.text(M, iy+38, profile["desc"][:85]+"...", _font(17), pal["txt_l"])
    c.text(M, iy+64, _money_quote(sr), _font(17), pal["accent"])
    c.y = iy + 100

    if l1:
        c._center_img(l1, 0.85, 0.45, alpha=0.88)
        c.quote(pal, quotes)

    # --- achievements ---
    ach_items = []
    streak = _streak_info(db, report["week_start"], report["week_end"])
    if streak["record"]==streak["total"] and streak["record"]>0:
        ach_items.append(("全勤打卡","star_badge"))
    if sr>50: ach_items.append(("储蓄之王","crown"))
    elif sr>30: ach_items.append(("攒钱达人","green_badge"))
    for t in report.get("trends",[])[:2]:
        if t["direction"]=="down": ach_items.append((f"{t['category'][:2]}↓{t['change_pct']}%","medal"))
    if health["score"]>=80: ach_items.append(("财务健康","trophy"))
    if streak["pct"]>=80: ach_items.append(("坚持记账","heart"))

    if ach_items:
        c.section("本周成就", pal)
        # kawaii_stars decoration above achievements
        _put_decor(c.img, "kawaii_stars", W - M - 140, c.y - 10, 120, 40)
        ay = c.y + 4
        badge_w = 210  # width per badge slot
        max_per_row = max(1, int(c.uw / badge_w))
        for i, (at, ab) in enumerate(ach_items):
            row, col = divmod(i, max_per_row)
            bx = M + col * badge_w
            by = ay + row * 56
            _put_decor(c.img, ab, bx, by, 44, 44)
            c.text(bx+54, by+8, at, _font(19), pal["txt"])
        rows = (len(ach_items) + max_per_row - 1) // max_per_row
        c.y = ay + rows * 56 + 6

    # --- footer ---
    c.y += 12; c.fmt_divider(pal)
    # kawaii_hearts decoration above piggy
    _put_decor(c.img, "kawaii_hearts", W/2-80, c.y, 160, 30)
    c.y += 36
    _put_decor(c.img, "kawaii_piggy", W/2-35, c.y, 70, 70)
    c.y += 20; c.footer(pal)
    img = c.crop(); result = _apply_bg(img, portrait); result.save(filepath, "PNG")
    plt.close("all")
    return filepath


# ==============================================================================
#  MONTHLY REPORT
# ==============================================================================

def generate_monthly_report_png(db, filepath, folder=None, year=None, month=None):
    global _RESIZE_CACHE, _DECOR_CACHE
    _RESIZE_CACHE = {}; _DECOR_CACHE = {}

    assets = pick_assets()
    pal = assets["pal"]
    quotes = assets["quotes"]
    portrait = _load_pil(assets["portrait"], max_w=2400)
    l0 = _load_pil_rounded(assets["landscapes"][0], max_w=1600, radius=40) if assets["landscapes"] else None
    l1 = _load_pil_rounded(assets["landscapes"][1], max_w=1600, radius=40) if len(assets["landscapes"])>1 else None

    today = date.today()
    # Use provided year/month or default to current month
    target_year = year if year is not None else today.year
    target_month = month if month is not None else today.month
    m_start = date(target_year, target_month, 1)
    if target_month < 12:
        m_end = date(target_year, target_month + 1, 1) - timedelta(days=1)
    else:
        m_end = date(target_year + 1, 1, 1) - timedelta(days=1)

    ms = db.get_summary(m_start, m_end)
    profile = get_consumer_profile(db)
    health = calculate_health_score(db)
    cat_data = db.get_category_summary(m_start, m_end, "expense")
    total_exp = sum(v for _, v in cat_data) if cat_data else 0
    sr = (ms.balance / ms.total_income * 100) if ms.total_income > 0 else 0

    W = 2200; M = 100

    # ===== PAGE 1 — COVER =====
    p1 = ReportCanvas(W); p1.set_margins(M)

    _put_decor(p1.img, "kawaii_ribbon", W/2-100, 28, 200, 150)
    p1.y = 50
    p1.text(W/2, p1.y, "月度生活报告", _bold_font(60), pal["txt"], "ma")
    p1.y += 86
    p1.text(W/2, p1.y, f"{target_year}年 {target_month}月", _font(30), pal["txt_l"], "ma")
    p1.y += 48
    # kawaii_cloud decoration next to title
    _put_decor(p1.img, "kawaii_cloud", W - M - 120, 55, 100, 50)

    star_n = min(5, max(0, int(sr/20)))
    stars = "★"*star_n + "☆"*(5-star_n)
    p1.text(W/2, p1.y, f"{stars}  储蓄率 {sr:.1f}%", _bold_font(22), pal["accent"], "ma")
    p1.y += 44

    if l0:
        p1._center_img(l0, 0.80, 0.42, alpha=0.93)
        p1.quote(pal, quotes)
        p1.y += 6

    p1.cards([
        ("总收入", f"¥{ms.total_income:,.0f}"),
        ("总支出", f"¥{ms.total_expense:,.0f}"),
        ("结余", f"¥{ms.balance:,.0f}"),
    ], pal)

    p1.y += 18
    _put_decor(p1.img, "kawaii_corner", M-6, p1.y, 44, 44)
    _put_decor(p1.img, "kawaii_flower", W-M-38, p1.y, 44, 44)
    p1.y += 50

    # ===== PAGE 2 — ANALYSIS =====
    p2 = ReportCanvas(W); p2.set_margins(M)
    p2.y = 28

    if l1:
        p2._center_img(l1, 0.78, 0.42, alpha=0.93)
        p2.quote(pal, quotes)
        p2.y += 6

    if cat_data and total_exp > 0:
        p2.section("消费结构", pal)
        dbuf = _donut(cat_data, pal, total=total_exp, size=(5.2, 4.0))
        dw = int(p2.uw * 0.38)
        dh = int(dw * 0.73)
        cat_x = M + dw + 32
        cat_w = p2.uw - dw - 32
        cy2 = p2.y
        for i, (name, val) in enumerate(cat_data[:6]):
            pct = val / total_exp * 100
            color = pal["chart"][i % len(pal["chart"])]
            p2.rounded_rect(cat_x, cy2 + 6, 14, 14, 3, fill=color)
            p2.text(cat_x + 24, cy2, name, _font(20), pal["txt"])
            p2.text(cat_x + cat_w, cy2, f"¥{val:,.0f}  {pct:.0f}%", _bold_font(20), pal["txt"], "ra")
            cy2 += 38
            fw = max(18, int(cat_w * pct / 100))
            p2.rounded_rect(cat_x, cy2, cat_w, 22, 11, fill=_hex_rgba(pal["border"], 100))
            p2.rounded_rect(cat_x, cy2, fw, 22, 11, fill=color)
            cy2 += 40
        p2.chart(M, p2.y, dbuf, dw, dh)
        p2.y = max(p2.y + dh + 14, cy2 + 6)

    fun = _spending_math(total_exp, cat_data)
    if fun:
        p2.text(M, p2.y, "💡  " + "  |  ".join(fun[:4]), _font(18), pal["txt_l"])
        p2.y += 38

    p2.section("人格画像 & 月度之最", pal)
    p2.text(M, p2.y, f"🎭  {profile['emoji']}  {profile['title']}", _bold_font(24), pal["txt"])
    p2.y += 34
    p2.text(M, p2.y, profile["desc"][:90] + "…", _font(16), pal["txt_l"])
    p2.y += 34

    gauge_y = p2.y
    gbuf = _gauge(health["score"], health, pal, size=(5.2, 2.5))
    gw = int(p2.uw * 0.42); gh = int(gw * 0.46)
    p2.chart(M, p2.y, gbuf, gw, gh)

    bx = M + gw + 36; by = gauge_y + 6
    bills = db.get_bills(start_date=m_start, end_date=m_end, bill_type="expense", limit=300)
    biggest = None; day_spend = {}
    for b in bills:
        if biggest is None or b.amount > biggest.amount: biggest = b
        dk = b.bill_date.isoformat() if hasattr(b.bill_date, "isoformat") else str(b.bill_date)
        day_spend[dk] = day_spend.get(dk, 0) + b.amount

    best = []
    if biggest: best.append(("🥇", f"最大单笔  {biggest.category_name or '未分类'}  ¥{biggest.amount:,.0f}", "crown"))
    if day_spend:
        cheap = min(day_spend.items(), key=lambda x: x[1])
        best.append(("🥈", f"最省一天  {cheap[0]}  ¥{cheap[1]:,.0f}", "green_badge"))
    if cat_data: best.append(("🥉", f"TOP1  {cat_data[0][0]}  ¥{cat_data[0][1]:,.0f}", "medal"))

    for medal, text, badge in best:
        _put_decor(p2.img, badge, bx + 6, by + 4, 34, 34)
        p2.text(bx + 50, by + 8, text, _font(18), pal["txt"])
        by += 42

    # Calculate days passed in the target month
    if target_year == today.year and target_month == today.month:
        days_passed = max((today - m_start).days, 1)
    else:
        days_passed = (m_end - m_start).days + 1
    p2.text(bx, by + 8, f"日均 ¥{ms.total_expense / days_passed:,.0f}", _font(17), pal["txt_l"])
    if target_year == today.year and target_month == today.month:
        proj = (ms.total_expense / days_passed) * ((m_end - m_start).days + 1)
        p2.text(bx, by + 34, f"预计本月 ¥{proj:,.0f}", _font(17), pal["txt_l"])
    _put_decor(p2.img, "kawaii_coins", bx + p2.uw // 4, by + 4, 44, 44)
    # kawaii_trophy decoration
    _put_decor(p2.img, "kawaii_trophy", bx + p2.uw // 2, by - 10, 50, 50)

    right_h = (by + 36) - gauge_y
    p2.y = gauge_y + max(gh, right_h) + 12

    charts = []
    if bills:
        wb = _wday(bills, pal, size=(5.0, 1.6))
        if wb: charts.append(wb)
    if day_spend and len(day_spend) > 1:
        sb = _spk(sorted(day_spend.items()), pal, size=(5.0, 1.2))
        if sb: charts.append(sb)
    if charts:
        p2.section("消费节奏", pal)
        if len(charts) == 2:
            hw = (p2.uw - 24) / 2
            p2.chart(M, p2.y, charts[0], hw, 180)
            p2.chart(M + hw + 24, p2.y, charts[1], hw, 140)
            p2.y += 192
        else:
            p2.chart(M, p2.y, charts[0], p2.uw, 180)
            p2.y += 192

    p2.fmt_divider(pal)
    _put_decor(p2.img, "kawaii_hearts", W/2-80, p2.y, 160, 30)
    p2.y += 36
    _put_decor(p2.img, "kawaii_piggy", W/2 - 35, p2.y, 70, 70)
    p2.y += 22
    p2.footer(pal)

    img1 = p1.crop()
    img2 = p2.crop()
    combined = PILImage.new("RGBA", (W, img1.height + img2.height), (255, 255, 255, 0))
    combined.paste(img1, (0, 0), img1)
    combined.paste(img2, (0, img1.height), img2)
    result = _apply_bg(combined, portrait)
    result.save(filepath, "PNG")
    plt.close("all")
    return filepath


# ==============================================================================
#  YEARLY REPORT
# ==============================================================================

def generate_yearly_report_png(db, filepath, folder=None, year=None):
    global _RESIZE_CACHE, _DECOR_CACHE
    _RESIZE_CACHE = {}; _DECOR_CACHE = {}

    assets = pick_assets()
    pal = assets["pal"]
    quotes = assets["quotes"]
    portrait = _load_pil(assets["portrait"], max_w=2400)
    l0 = _load_pil_rounded(assets["landscapes"][0], max_w=1800, radius=46) if assets["landscapes"] else None
    l1 = _load_pil_rounded(assets["landscapes"][1], max_w=1800, radius=46) if len(assets["landscapes"])>1 else None

    today = date.today()
    # Use provided year or default to current year
    target_year = year if year is not None else today.year
    y_start = date(target_year, 1, 1)
    if target_year == today.year:
        y_end = min(date(target_year, 12, 31), today)
    else:
        y_end = date(target_year, 12, 31)

    ys = db.get_summary(y_start, y_end)
    profile = get_consumer_profile(db)
    health = calculate_health_score(db)
    cat_data = db.get_category_summary(y_start, y_end, "expense")
    total_exp = sum(v for _, v in cat_data) if cat_data else 0
    sr = (ys.balance / ys.total_income * 100) if ys.total_income > 0 else 0
    if target_year == today.year:
        months_passed = today.month
    else:
        months_passed = 12
    monthly_avg = ys.total_expense / max(months_passed, 1)

    W = 2400; M = 110

    # ===== PAGE 1 — COVER =====
    p1 = ReportCanvas(W); p1.set_margins(M)

    if l0:
        p1._center_img(l0, 0.86, 0.44, alpha=0.93)
        p1.y += 2

    _put_decor(p1.img, "kawaii_ribbon", W/2-100, p1.y, 200, 155)
    p1.y += 34
    p1.text(W/2, p1.y, "年度生活回忆录", _bold_font(60), pal["txt"], "ma")
    p1.y += 84
    p1.text(W/2, p1.y, str(target_year), _font(30), pal["txt_l"], "ma")
    p1.y += 54

    p1.quote(pal, quotes)
    p1.y += 8

    hw = (p1.uw-24)/2; ch2 = 120
    cards2 = [
        ("总收入", f"¥{ys.total_income:,.0f}", "coin"),
        ("总支出", f"¥{ys.total_expense:,.0f}", "money_bag"),
        ("净储蓄", f"¥{ys.balance:,.0f}", "piggy"),
        ("月均支出", f"¥{monthly_avg:,.0f}", "chart_up"),
    ]
    for i, (label, value, deco) in enumerate(cards2):
        r, c2 = divmod(i, 2)
        cx = M + c2*(hw+24); cy = p1.y + r*(ch2+16)
        # shadow (very faint)
        p1.rounded_rect(cx+2, cy+2, hw, ch2, 20, fill=_hex_rgba(pal["border"], 50))
        p1.rounded_rect(cx, cy, hw, ch2, 20, fill=(255, 255, 255, 140), border=_hex_rgba(pal["border"], 80), bw=1)
        _put_decor(p1.img, deco, cx+24, cy+24, 48, 48)
        p1.text(cx+88, cy+24, label, _font(22), pal["txt_l"])
        p1.text(cx+hw-24, cy+70, value, _bold_font(34), pal["txt"], "ra")
    p1.y += 2*(ch2+16)+30

    if target_year == today.year:
        p1.text(W/2, p1.y, f"储蓄率 {sr:.1f}%  ·  坚持 {months_passed} 个月  ·  健康评分 {health['score']}", _bold_font(24), pal["txt"], "ma")
    else:
        p1.text(W/2, p1.y, f"储蓄率 {sr:.1f}%  ·  共 {months_passed} 个月", _bold_font(24), pal["txt"], "ma")
    p1.y += 46

    fun = _spending_math(total_exp, cat_data)
    if fun:
        p1.text(W/2, p1.y, "💡  "+"  |  ".join(fun[:4]), _font(20), pal["txt_l"], "ma")
        p1.y += 40
    p1.text(W/2, p1.y, _money_quote(sr), _font(20), pal["accent"], "ma")
    p1.y += 50

    # ===== PAGE 2 — TRENDS =====
    p2 = ReportCanvas(W); p2.set_margins(M)
    p2.y = 24

    p2.section("年度收支趋势", pal)

    months_l, incomes, expenses = [], [], []
    # For current year, show months up to current month; for past years, show all 12 months
    if target_year == today.year:
        max_month = today.month
    else:
        max_month = 12
    for m in range(1, max_month + 1):
        if m < 12:
            ms_end = date(target_year, m + 1, 1) - timedelta(days=1)
        else:
            ms_end = y_end
        s = db.get_summary(date(target_year, m, 1), ms_end)
        months_l.append(f"{m}月")
        incomes.append(s.total_income)
        expenses.append(s.total_expense)

    if any(v>0 for v in incomes+expenses):
        lb = _line(months_l, incomes, expenses, pal, size=(9.5,4.2))
        lh = int(p2.uw*0.30)
        p2.chart(M, p2.y, lb, p2.uw, lh)
        p2.y += lh + 18

    if l1:
        p2._center_img(l1, 0.82, 0.44, alpha=0.93)
        p2.quote(pal, quotes)

    p2.text(M, p2.y, f"🎭  {profile['emoji']}  {profile['title']}", _bold_font(28), pal["txt"])
    p2.y += 42
    p2.text(M, p2.y, profile["desc"][:100]+"...", _font(17), pal["txt_l"])
    p2.y += 40

    gbuf = _gauge(health["score"], health, pal, size=(5.0,2.2))
    gw2 = int(p2.uw*0.30); gh2 = int(gw2*0.44)
    p2.chart(M, p2.y, gbuf, gw2, gh2)
    p2.y += gh2 + 28

    # ===== PAGE 3 — RANKINGS + CLOSING =====
    p3 = ReportCanvas(W); p3.set_margins(M)
    p3.y = 24

    p3.section("消费榜单 TOP5", pal)
    _put_decor(p3.img, "kawaii_trophy", W - M - 100, p3.y - 48, 60, 60)
    medals = ["🥇","🥈","🥉","④","⑤"]
    rk_hw = (p3.uw-24)/2
    ry = p3.y
    if cat_data:
        for i, (n, v) in enumerate(cat_data[:5]):
            pct = round(v/total_exp*100) if total_exp>0 else 0
            p3.text(M+12, ry, f"{medals[i]}  {n}: ¥{v:,.0f}  ({pct}%)", _font(22), pal["txt"])
            ry += 46

    fy = p3.y; fact_items = []
    if cat_data:
        tn, tv = cat_data[0]
        if tn=="餐饮" and tv>1000: fact_items.append(f"🍜  约{int(tv/35)}顿饭")
        if tn=="购物" and tv>1000: fact_items.append(f"🛍  购物 ¥{tv:,.0f}")
    fact_items.append(f"📝  坚持{months_passed}个月记录")
    bills_all = db.get_bills(start_date=y_start, end_date=y_end, bill_type="expense", limit=500)
    dt = {}
    for b in bills_all:
        dk = b.bill_date.isoformat() if hasattr(b.bill_date,"isoformat") else str(b.bill_date)
        dt[dk] = dt.get(dk,0)+b.amount
    if dt:
        md = max(dt, key=dt.get)
        fact_items.append(f"📅  最贵一天 {md} ¥{dt[md]:,.0f}")
    if ys.total_income>0: fact_items.append(f"💎  收入是支出的 {ys.total_income/max(ys.total_expense,1):.1f}x")

    fh = len(fact_items)*36+66
    p3.rounded_rect(M+rk_hw+24, fy, rk_hw, fh, 18, fill=(255, 248, 225, 120), border=_hex_rgba(pal["border"], 80), bw=1)
    _put_decor(p3.img, "party", M+rk_hw+40, fy+16, 38, 38)
    p3.text(M+rk_hw+90, fy+20, "🎲  趣味数据", _bold_font(22), pal["txt"])
    for fi, fact in enumerate(fact_items):
        p3.text(M+rk_hw+52, fy+60+fi*36, fact, _font(19), pal["txt_l"])
    p3.y = max(ry, fy+fh+20)

    if cat_data and len(cat_data)>1:
        bl = [c[0] for c in cat_data[:6]]; bv = [c[1] for c in cat_data[:6]]
        bb = _hbar(bl, bv, pal, size=(8.5,3.4))
        bh = int(p3.uw*0.28)
        p3.chart(M, p3.y, bb, int(p3.uw*0.60), bh)
        p3.y += bh+28

    kw_pool = ["精致","自律","烟火气","成长","从容","热情","自由","积累","探索","温暖","突破","理性","平衡"]
    kws = random.sample(kw_pool, min(5, len(kw_pool)))
    _put_decor(p3.img, "kawaii_ribbon", W/2-80, p3.y, 160, 124)
    p3.y += 46
    p3.text(W/2, p3.y, f"💎  {target_year}  年度关键词", _bold_font(34), pal["txt"], "ma")
    _put_decor(p3.img, "kawaii_stars", M + 20, p3.y - 10, 100, 36)
    p3.y += 56
    tg = 24; ttw = len(kws)*170+(len(kws)-1)*tg; ts = (W-ttw)/2
    for i, kw in enumerate(kws):
        tx = ts+i*(170+tg)
        p3.rounded_rect(tx, p3.y, 170, 52, 26, fill=_hex_rgba(pal["tag"], 160))
        p3.text(tx+85, p3.y+26, f"「{kw}」", _font(22), "#FFFFFF", "ma")
    p3.y += 78

    advice = profile["suggestion"]
    if cat_data:
        tn, tv = cat_data[0]; tp = round(tv/total_exp*100) if total_exp>0 else 0
        if tp>35: advice += f"\n{tn}占比{tp}%，可适当控制~"

    ytips = _yearly_tips(sr)
    tip_lines = len(ytips)
    tip_h = tip_lines * 32 + 60
    p3.fmt_divider(pal); p3.y += 2

    p3.rounded_rect(M, p3.y, p3.uw, tip_h, 20, fill=_hex_rgba(pal["light"], 80), border=_hex_rgba(pal["border"], 80), bw=1)
    _put_decor(p3.img, "rocket", M+24, p3.y+16, 38, 54)
    p3.text(M+78, p3.y+20, "📝  新年Tips", _bold_font(24), pal["txt"])
    _put_decor(p3.img, "kawaii_wallet", W - M - 80, p3.y + 10, 56, 56)
    for ti, tip in enumerate(ytips):
        p3.text(M+36, p3.y+58+ti*32, tip, _font(17), pal["txt_l"])
    p3.y += tip_h + 20

    p3.quote(pal, quotes)
    p3.y += 16
    p3.text(W/2, p3.y, "新的一年，继续用心记录每一笔", _font(26), pal["txt"], "ma")
    p3.y += 42
    _put_decor(p3.img, "kawaii_hearts", W/2-80, p3.y, 160, 30)
    p3.y += 36
    _put_decor(p3.img, "kawaii_piggy", W/2-35, p3.y, 72, 72)
    p3.y += 26; p3.footer(pal)

    img1 = p1.crop(); img2 = p2.crop(); img3 = p3.crop()
    th = img1.height+img2.height+img3.height
    combined = PILImage.new("RGBA", (W, th), (255, 255, 255, 0))
    combined.paste(img1, (0,0), img1); combined.paste(img2, (0,img1.height), img2); combined.paste(img3, (0,img1.height+img2.height), img3)
    result = _apply_bg(combined, portrait)
    result.save(filepath, "PNG")
    plt.close("all")
    return filepath
