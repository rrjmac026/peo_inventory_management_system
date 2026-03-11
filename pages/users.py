import customtkinter as ctk
from tkinter import messagebox
from theme import *
from database import get_all_users, add_user, delete_user, change_password


class UsersPage(ctk.CTkFrame):
    def __init__(self, parent, navigate, current_user):
        super().__init__(parent, fg_color="transparent")
        self.navigate = navigate
        self.current_user = current_user
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hdr, text="Users", font=FONT_TITLE(),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(hdr, text="Manage user accounts and passwords.",
                     font=FONT_BODY(), text_color=TEXT_DIM).grid(row=1, column=0, sticky="w")
        ctk.CTkButton(hdr, text="＋  Add User", font=FONT_BODY(),
                      fg_color=ACCENT, hover_color="#3a7be0", height=38, corner_radius=10,
                      command=self._open_add).grid(row=0, column=1, rowspan=2)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color=BG_CARD, corner_radius=14)
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def _load(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        users = get_all_users()
        if not users:
            ctk.CTkLabel(self.scroll, text="No users found.", font=FONT_BODY(),
                         text_color=TEXT_DIM).pack(pady=40)
            return
        for u in users:
            self._user_card(u)

    def _user_card(self, u):
        is_self = u["id"] == self.current_user["id"]
        card = ctk.CTkFrame(self.scroll, fg_color=BG_INPUT, corner_radius=12)
        card.pack(fill="x", padx=12, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # Avatar circle
        avatar_bg = ctk.CTkFrame(card, fg_color=ACCENT if not is_self else ACCENT2,
                                 corner_radius=22, width=44, height=44)
        avatar_bg.grid(row=0, column=0, rowspan=2, padx=14, pady=12)
        avatar_bg.grid_propagate(False)
        initials = (u["full_name"] or u["username"])[:1].upper()
        ctk.CTkLabel(avatar_bg, text=initials, font=FONT_BOLD(16),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        name_row = ctk.CTkFrame(card, fg_color="transparent")
        name_row.grid(row=0, column=1, sticky="w", padx=4, pady=(12, 2))
        ctk.CTkLabel(name_row, text=u["full_name"] or u["username"],
                     font=FONT_BOLD(13), text_color=TEXT_MAIN).pack(side="left")
        if is_self:
            ctk.CTkLabel(name_row, text="  (You)", font=FONT_SMALL(),
                         text_color=ACCENT2).pack(side="left")

        ctk.CTkLabel(card, text=f"@{u['username']}   •   Joined: {u['created_at'][:10]}",
                     font=FONT_SMALL(), text_color=TEXT_DIM).grid(
                         row=1, column=1, sticky="w", padx=4, pady=(0, 12))

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=2, padx=(0, 14))

        ctk.CTkButton(btn_frame, text="🔑 Change Password", width=140, height=30,
                      corner_radius=6, fg_color=BG_CARD, hover_color=BORDER,
                      text_color=TEXT_DIM, font=FONT_SMALL(),
                      command=lambda uid=u["id"], uname=u["username"]: self._change_pwd(uid, uname)
                      ).pack(pady=(0, 4))

        del_btn = ctk.CTkButton(btn_frame, text="🗑️ Delete", width=140, height=30,
                                corner_radius=6, fg_color=BG_CARD, hover_color=DANGER,
                                text_color=TEXT_DIM, font=FONT_SMALL(),
                                command=lambda uid=u["id"], uname=u["username"]: self._delete(uid, uname))
        del_btn.pack()
        if is_self:
            del_btn.configure(state="disabled", text_color="#444")

    def _open_add(self):
        AddUserForm(self, self._load)

    def _change_pwd(self, user_id, username):
        ChangePasswordForm(self, user_id, username)

    def _delete(self, user_id, username):
        if messagebox.askyesno("Confirm Delete",
                               f"Delete user '{username}'?\nThis cannot be undone."):
            delete_user(user_id)
            self._load()


class AddUserForm(ctk.CTkToplevel):
    def __init__(self, parent, on_save):
        super().__init__(parent)
        self.on_save = on_save
        self.title("Add New User")
        self.geometry("420x380")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Add New User", font=FONT_BOLD(18),
                     text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=28, pady=(22, 4))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=28)
        form.grid_columnconfigure(0, weight=1)

        for row, (label, attr, ph, show) in enumerate([
            ("Full Name",  "e_fullname", "e.g. Juan dela Cruz",   ""),
            ("Username *", "e_username", "e.g. jdelacruz",        ""),
            ("Password *", "e_password", "At least 6 characters", "●"),
            ("Confirm Password *", "e_confirm", "Repeat password","●"),
        ]):
            ctk.CTkLabel(form, text=label, font=FONT_SMALL(), text_color=TEXT_DIM).grid(
                row=row*2, column=0, sticky="w", pady=(10, 2))
            entry = ctk.CTkEntry(form, placeholder_text=ph, height=36, show=show,
                                 fg_color=BG_INPUT, border_color=BORDER,
                                 text_color=TEXT_MAIN, font=FONT_BODY())
            entry.grid(row=row*2+1, column=0, sticky="ew")
            setattr(self, attr, entry)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=28, pady=18)
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="Cancel", fg_color=BG_INPUT, hover_color=BORDER,
                      text_color=TEXT_MAIN, height=40, corner_radius=10,
                      command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Create User", fg_color=ACCENT, hover_color="#3a7be0",
                      height=40, corner_radius=10, command=self._save).grid(row=0, column=1, sticky="ew")

    def _save(self):
        fullname = self.e_fullname.get().strip()
        username = self.e_username.get().strip()
        password = self.e_password.get()
        confirm  = self.e_confirm.get()
        if not username or not password:
            messagebox.showerror("Missing", "Username and password are required.")
            return
        if len(password) < 6:
            messagebox.showerror("Weak Password", "Password must be at least 6 characters.")
            return
        if password != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        ok, msg = add_user(username, password, fullname)
        if ok:
            self.on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg)


class ChangePasswordForm(ctk.CTkToplevel):
    def __init__(self, parent, user_id, username):
        super().__init__(parent)
        self.user_id  = user_id
        self.username = username
        self.title("Change Password")
        self.geometry("380x260")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        self.grab_set()
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=f"Change password for @{self.username}",
                     font=FONT_BOLD(14), text_color=TEXT_MAIN).grid(
                         row=0, column=0, sticky="w", padx=28, pady=(22, 4))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.grid(row=1, column=0, sticky="nsew", padx=28)
        form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(form, text="New Password", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=0, column=0, sticky="w", pady=(8, 2))
        self.e_new = ctk.CTkEntry(form, show="●", height=36, fg_color=BG_INPUT,
                                  border_color=BORDER, text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_new.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(form, text="Confirm Password", font=FONT_SMALL(), text_color=TEXT_DIM).grid(
            row=2, column=0, sticky="w", pady=(12, 2))
        self.e_confirm = ctk.CTkEntry(form, show="●", height=36, fg_color=BG_INPUT,
                                      border_color=BORDER, text_color=TEXT_MAIN, font=FONT_BODY())
        self.e_confirm.grid(row=3, column=0, sticky="ew")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=28, pady=18)
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="Cancel", fg_color=BG_INPUT, hover_color=BORDER,
                      text_color=TEXT_MAIN, height=40, corner_radius=10,
                      command=self.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(btn_row, text="Update Password", fg_color=ACCENT, hover_color="#3a7be0",
                      height=40, corner_radius=10, command=self._save).grid(row=0, column=1, sticky="ew")

    def _save(self):
        new     = self.e_new.get()
        confirm = self.e_confirm.get()
        if not new:
            messagebox.showerror("Missing", "Please enter a new password.")
            return
        if len(new) < 6:
            messagebox.showerror("Weak", "Password must be at least 6 characters.")
            return
        if new != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return
        change_password(self.user_id, new)
        messagebox.showinfo("Success", "Password updated successfully.")
        self.destroy()