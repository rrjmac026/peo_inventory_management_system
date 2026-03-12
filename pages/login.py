import customtkinter as ctk
import tkinter as tk
from theme import *
from database import login
import math


class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="#0a0e17")
        self.on_login_success = on_login_success
        self._anim_angle = 0
        self._pulse = 0
        self._pulse_dir = 1
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build()
        self._animate()

    def _build(self):
        # Two-column root: left=canvas art, right=form
        root = tk.Frame(self, bg="#0a0e17")
        root.place(relx=0, rely=0, relwidth=1, relheight=1)
        root.grid_columnconfigure(0, weight=3)
        root.grid_columnconfigure(1, weight=2)
        root.grid_rowconfigure(0, weight=1)

        # ── LEFT: animated canvas art panel ───────────────────────────────────
        self.canvas = tk.Canvas(root, bg="#0a0e17", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self._draw_bg())

        # ── RIGHT: login form panel ────────────────────────────────────────────
        right_bg = tk.Frame(root, bg="#0d1220")
        right_bg.grid(row=0, column=1, sticky="nsew")

        right = ctk.CTkFrame(right_bg, fg_color="#0d1220", corner_radius=0)
        right.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Subtle left border accent
        accent_bar = tk.Frame(right_bg, bg="#1a3a7c", width=1)
        accent_bar.place(relx=0, rely=0, relheight=1, x=0)

        # Centered form wrapper
        form_wrap = ctk.CTkFrame(right, fg_color="transparent")
        form_wrap.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.76)
        form_wrap.grid_columnconfigure(0, weight=1)

        # ── Logo ──────────────────────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(form_wrap, fg_color="#111c35", corner_radius=16,
                                  width=56, height=56)
        logo_frame.grid(row=0, column=0, pady=(0, 20))
        logo_frame.grid_propagate(False)
        logo_frame.grid_columnconfigure(0, weight=1)
        logo_frame.grid_rowconfigure(0, weight=1)
        ctk.CTkLabel(logo_frame, text="AM",
                     font=ctk.CTkFont("Georgia", 18, "bold"),
                     text_color="#4f8ef7").grid(row=0, column=0)

        # ── App title ─────────────────────────────────────────────────────────
        ctk.CTkLabel(form_wrap, text="AssetMate",
                     font=ctk.CTkFont("Georgia", 28, "bold"),
                     text_color="#dce8ff").grid(row=1, column=0, pady=(0, 4))

        # Subtitle pill
        pill_frame = ctk.CTkFrame(form_wrap, fg_color="#111c35", corner_radius=20)
        pill_frame.grid(row=2, column=0, pady=(0, 32))
        ctk.CTkLabel(pill_frame,
                     text="  Equipment & Asset Inventory  ",
                     font=ctk.CTkFont("Helvetica", 9),
                     text_color="#3d5fa0").pack(padx=6, pady=4)

        # ── Username ──────────────────────────────────────────────────────────
        ctk.CTkLabel(form_wrap, text="USERNAME",
                     font=ctk.CTkFont("Helvetica", 9, "bold"),
                     text_color="#253c5e",
                     anchor="w").grid(row=3, column=0, sticky="w", pady=(0, 4))

        user_field = ctk.CTkFrame(form_wrap, fg_color="#111c35", corner_radius=10,
                                  border_width=1, border_color="#1a2d50", height=46)
        user_field.grid(row=4, column=0, sticky="ew")
        user_field.grid_propagate(False)
        user_field.grid_columnconfigure(1, weight=1)
        user_field.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(user_field, text="👤",
                     font=ctk.CTkFont("Segoe UI Emoji", 12),
                     text_color="#253c5e").grid(row=0, column=0, padx=(12, 0))
        self.e_user = ctk.CTkEntry(user_field, fg_color="transparent", border_width=0,
                                   text_color="#c8d8f5",
                                   font=ctk.CTkFont("Helvetica", 13),
                                   placeholder_text="Enter username",
                                   placeholder_text_color="#2a3d60")
        self.e_user.grid(row=0, column=1, sticky="ew", padx=(8, 12))

        # ── Password ──────────────────────────────────────────────────────────
        ctk.CTkLabel(form_wrap, text="PASSWORD",
                     font=ctk.CTkFont("Helvetica", 9, "bold"),
                     text_color="#253c5e",
                     anchor="w").grid(row=5, column=0, sticky="w", pady=(18, 4))

        pass_field = ctk.CTkFrame(form_wrap, fg_color="#111c35", corner_radius=10,
                                  border_width=1, border_color="#1a2d50", height=46)
        pass_field.grid(row=6, column=0, sticky="ew")
        pass_field.grid_propagate(False)
        pass_field.grid_columnconfigure(1, weight=1)
        pass_field.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(pass_field, text="🔒",
                     font=ctk.CTkFont("Segoe UI Emoji", 12),
                     text_color="#253c5e").grid(row=0, column=0, padx=(12, 0))
        self.e_pass = ctk.CTkEntry(pass_field, show="●",
                                   fg_color="transparent", border_width=0,
                                   text_color="#c8d8f5",
                                   font=ctk.CTkFont("Helvetica", 13),
                                   placeholder_text="Enter password",
                                   placeholder_text_color="#2a3d60")
        self.e_pass.grid(row=0, column=1, sticky="ew", padx=(8, 4))

        self._show_pass = False
        self.vis_btn = ctk.CTkButton(
            pass_field, text="◉", width=34, height=34, corner_radius=8,
            fg_color="transparent", hover_color="#162040",
            text_color="#253c5e", font=ctk.CTkFont("Helvetica", 14),
            command=self._toggle_pass)
        self.vis_btn.grid(row=0, column=2, padx=(0, 6))

        # ── Error ─────────────────────────────────────────────────────────────
        self.err_lbl = ctk.CTkLabel(form_wrap, text="",
                                    font=ctk.CTkFont("Helvetica", 11),
                                    text_color="#d95f5f")
        self.err_lbl.grid(row=7, column=0, pady=(10, 0))

        # ── Login button ──────────────────────────────────────────────────────
        self.login_btn = ctk.CTkButton(
            form_wrap, text="Sign In  →",
            height=48, corner_radius=12,
            fg_color="#2655c8", hover_color="#1e44a8",
            font=ctk.CTkFont("Helvetica", 14, "bold"),
            text_color="white",
            command=self._attempt_login)
        self.login_btn.grid(row=8, column=0, sticky="ew", pady=(16, 0))

        # ── Divider ───────────────────────────────────────────────────────────
        div = ctk.CTkFrame(form_wrap, fg_color="transparent")
        div.grid(row=9, column=0, sticky="ew", pady=(28, 0))
        div.grid_columnconfigure((0, 2), weight=1)
        ctk.CTkFrame(div, fg_color="#16243a", height=1).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(div, text="  DEFAULT  ",
                     font=ctk.CTkFont("Helvetica", 8),
                     text_color="#1a2d45").grid(row=0, column=1)
        ctk.CTkFrame(div, fg_color="#16243a", height=1).grid(row=0, column=2, sticky="ew")

        # ── Credential chips ──────────────────────────────────────────────────
        chips = ctk.CTkFrame(form_wrap, fg_color="transparent")
        chips.grid(row=10, column=0, sticky="ew", pady=(14, 0))
        chips.grid_columnconfigure((0, 1), weight=1)

        for col, (cap, val) in enumerate([("USERNAME", "admin"), ("PASSWORD", "admin123")]):
            ch = ctk.CTkFrame(chips, fg_color="#0e1a30", corner_radius=10,
                              border_width=1, border_color="#162035")
            ch.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 4, 4 if col == 0 else 0))
            ctk.CTkLabel(ch, text=cap,
                         font=ctk.CTkFont("Helvetica", 8),
                         text_color="#1e3052").pack(pady=(8, 1))
            ctk.CTkLabel(ch, text=val,
                         font=ctk.CTkFont("Helvetica", 12, "bold"),
                         text_color="#3060c0").pack(pady=(0, 8))

        # ── Footer ────────────────────────────────────────────────────────────
        ctk.CTkLabel(form_wrap, text="v1.0  ·  Office Edition  ·  © 2025",
                     font=ctk.CTkFont("Helvetica", 8),
                     text_color="#142030").grid(row=11, column=0, pady=(30, 0))

        # Bindings
        self.e_pass.bind("<Return>", lambda e: self._attempt_login())
        self.e_user.bind("<Return>", lambda e: self.e_pass.focus())
        self.after(120, self.e_user.focus)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _toggle_pass(self):
        self._show_pass = not self._show_pass
        self.e_pass.configure(show="" if self._show_pass else "●")
        self.vis_btn.configure(text_color="#4f8ef7" if self._show_pass else "#253c5e")

    def _attempt_login(self):
        username = self.e_user.get().strip()
        password = self.e_pass.get()
        if not username or not password:
            self.err_lbl.configure(text="⚠  Please fill in both fields.")
            return
        user = login(username, password)
        if user:
            self.err_lbl.configure(text="", text_color="#2ecc71")
            self.login_btn.configure(text="✓  Welcome!", fg_color="#1a9e6e")
            self.after(450, lambda: self.on_login_success(user))
        else:
            self.err_lbl.configure(text="✕  Incorrect username or password.")
            self.e_pass.delete(0, "end")
            self.login_btn.configure(fg_color="#8b2020")
            self.after(700, lambda: self.login_btn.configure(
                fg_color="#2655c8", text="Sign In  →"))

    # ── Animated Canvas ───────────────────────────────────────────────────────
    def _draw_bg(self):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width() or 720
        H = c.winfo_height() or 700
        a = self._anim_angle
        p = self._pulse

        # Deep gradient background
        for i in range(50):
            t = i / 50
            r = int(10 + t * 6)
            g = int(14 + t * 8)
            b = int(23 + t * 16)
            c.create_rectangle(0, int(H * t), W, int(H * (t + 1/50) + 1),
                                fill=f"#{r:02x}{g:02x}{b:02x}", outline="")

        # Glowing radial orbs
        orbs = [
            (0.20, 0.25, 300, "#06111e"),
            (0.75, 0.68, 240, "#05101c"),
            (0.48, 0.82, 180, "#06111e"),
            (0.85, 0.18, 220, "#04101a"),
            (0.12, 0.72, 160, "#050e1a"),
        ]
        for rx, ry, rad, col in orbs:
            dx = math.sin(a + rx * 10) * 15
            dy = math.cos(a + ry * 10) * 10
            cx_, cy_ = W * rx + dx, H * ry + dy
            for layer in [2.4, 1.7, 1.0]:
                r2 = int(rad * layer)
                # blend darker for outer
                base_c = "#030a12" if layer > 1.5 else col
                c.create_oval(cx_ - r2, cy_ - r2, cx_ + r2, cy_ + r2,
                              fill=base_c, outline="")

        # Perspective grid
        grid_c = "#0b1626"
        # Horizontal lines
        for i in range(20):
            y = int(H * i / 19)
            c.create_line(0, y, W, y, fill=grid_c, width=1)
        # Vertical converging lines
        vp = (W * 0.5, H * 0.38)
        for i in range(22):
            bx = int(W * i / 21)
            c.create_line(bx, H, vp[0], vp[1], fill=grid_c, width=1)

        # Large central glow circle
        gR = 110 + p * 0.5
        for layer, fill in [(2.0, "#030b18"), (1.4, "#05101e"), (0.9, "#071424")]:
            r2 = int(gR * layer)
            cx_, cy_ = W * 0.5, H * 0.42
            c.create_oval(cx_ - r2, cy_ - r2, cx_ + r2, cy_ + r2, fill=fill, outline="")

        # Rotating hexagonal rings
        for hx, hy, hr, hcol, spd in [
            (W * 0.5,  H * 0.42, 92 + p * 0.3,  "#0c2050", 1.0),
            (W * 0.5,  H * 0.42, 130 + p * 0.2, "#091838", -0.7),
            (W * 0.22, H * 0.30, 55,              "#091832", 1.3),
            (W * 0.78, H * 0.58, 42,              "#09182e", -1.1),
        ]:
            pts = []
            for k in range(6):
                ang = math.radians(60 * k + a * spd * 15)
                pts += [hx + hr * math.cos(ang), hy + hr * math.sin(ang)]
            c.create_polygon(pts, outline=hcol, fill="", width=1)

        # "AM" monogram
        c.create_text(W * 0.5, H * 0.42,
                      text="AM", font=("Georgia", 46, "bold"),
                      fill="#0f2248", anchor="center")

        # Branding label
        c.create_text(W * 0.5, H * 0.565,
                      text="ASSETMATE",
                      font=("Helvetica", 15, "bold"),
                      fill="#0d1f3e", anchor="center")
        c.create_text(W * 0.5, H * 0.61,
                      text="Equipment & Asset Inventory Management",
                      font=("Helvetica", 9),
                      fill="#0a1830", anchor="center")

        # Floating particles
        import random
        rng = random.Random(7)
        for _ in range(50):
            px = rng.uniform(0, W)
            py = rng.uniform(0, H)
            ps = rng.uniform(1, 2.2)
            pc = rng.choice(["#0c1c30", "#0e2040", "#0a1628"])
            c.create_oval(px - ps, py - ps, px + ps, py + ps, fill=pc, outline="")

        # Diagonal accent streaks
        for sx1, sy1, sx2, sy2, sc in [
            (0.0, 0.5, 0.4, 0.0,  "#091830"),
            (1.0, 0.6, 0.6, 0.0,  "#07142a"),
            (0.0, 0.9, 0.55, 0.5, "#091832"),
            (1.0, 0.1, 0.5, 0.7,  "#070f20"),
        ]:
            c.create_line(W * sx1, H * sy1, W * sx2, H * sy2, fill=sc, width=1)

        # Bottom tagline
        c.create_text(W * 0.5, H * 0.92,
                      text="Secure  ·  Professional  ·  Reliable",
                      font=("Helvetica", 9), fill="#0a1628", anchor="center")

    def _animate(self):
        self._anim_angle += 0.005
        self._pulse += self._pulse_dir * 0.35
        if self._pulse >= 14 or self._pulse <= 0:
            self._pulse_dir *= -1
        self._draw_bg()
        self.after(48, self._animate)