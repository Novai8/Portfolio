"""Global production configuration for Glitch World Day 02."""
import os

W, H = 1080, 1920
FPS = 30
SAFE_X = 72          # safe margin left/right
SAFE_TOP, SAFE_BOTTOM = 120, 250
SUB_Y = H - 300      # default subtitle baseline area

PATHS = {}
_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.abspath(os.path.join(_HERE, "..", "..", "..", "assets"))
PATHS["font_sans"] = os.path.join(ASSETS, "fonts", "Montserrat-VF.ttf")
PATHS["font_display"] = os.path.join(ASSETS, "fonts", "Archivo-VF.ttf")

# ---- palette -------------------------------------------------------------
NAVY      = (12, 16, 34)
NAVY_2    = (20, 26, 54)
CHARCOAL  = (10, 10, 16)
VIOLET    = (46, 38, 78)
VIOLET_D  = (28, 24, 52)
CYAN      = (64, 224, 232)
CYAN_DIM  = (34, 128, 148)
MAGENTA   = (214, 48, 142)
RED       = (210, 62, 78)
WHITE     = (236, 240, 248)
PALE      = (196, 214, 232)
GREY      = (96, 108, 132)
DARKGREY  = (34, 40, 58)
WARM      = (255, 196, 120)

INK = (8, 8, 14)          # stickman body
RIM_CYAN = (90, 234, 240)

# audio
AR = 48000
