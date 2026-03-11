import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Colors ─────────────────────────────────────────────────────────────────────
BG_MAIN    = "#0f1117"
BG_SIDEBAR = "#161b27"
BG_CARD    = "#1e2535"
BG_INPUT   = "#252d3d"
ACCENT     = "#4f8ef7"
ACCENT2    = "#38d9a9"
WARN       = "#f5a623"
DANGER     = "#e05c5c"
GOLD       = "#f7c948"
TEXT_MAIN  = "#e8eaf0"
TEXT_DIM   = "#6b7a99"
BORDER     = "#2a3347"
SUCCESS    = "#38d9a9"

# ── Fonts ──────────────────────────────────────────────────────────────────────
def FONT_TITLE():       return ctk.CTkFont("Helvetica", 26, "bold")
def FONT_HEADING():     return ctk.CTkFont("Helvetica", 15, "bold")
def FONT_BODY():        return ctk.CTkFont("Helvetica", 13)
def FONT_SMALL():       return ctk.CTkFont("Helvetica", 11)
def FONT_TINY():        return ctk.CTkFont("Helvetica", 10)
def FONT_BOLD(size=12): return ctk.CTkFont("Helvetica", size, "bold")