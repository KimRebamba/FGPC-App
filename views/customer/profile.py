"""Customer profile tab — CustomTkinter with avatar image upload and display."""

from __future__ import annotations

import customtkinter as ctk

from controllers.auth_controller import (
    change_user_password,
    update_user_profile,
    verify_user_password,
)
from models.user import User
from views import theme as T
from views.image_utils import (
    create_placeholder_image,
    load_ctk_image,
    pick_image_file,
    save_image_to_uploads,
)


def build_profile_view(
    parent: ctk.CTkFrame,
    user: User,
    database_path: str | None = None,
) -> ctk.CTkFrame:
    frame = ctk.CTkScrollableFrame(parent, fg_color=T.BG, corner_radius=0)
    frame.pack(fill="both", expand=True, padx=0, pady=0)

    
    avatar_path_var = [user.profile_image]

    
    hdr = T.card(frame, corner_radius=4)
    hdr.pack(fill="x", padx=24, pady=(24, 16))
    hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
    hdr_inner.pack(padx=24, pady=20, fill="x")

    
    avatar_frame = ctk.CTkFrame(hdr_inner, fg_color="transparent")
    avatar_frame.pack(side="left", padx=(0, 24))

    def _render_avatar(path: str | None) -> ctk.CTkImage:
        loaded = load_ctk_image(path, size=(96, 96), corner_radius=48)
        if loaded:
            return loaded
        initial = (user.first_name[:1] if user.first_name else "U").upper()
        return create_placeholder_image(
            initial, size=(96, 96), bg_color=T.SURFACE2, text_color=T.ACCENT, border_color=T.BORDER
        )

    avatar_lbl = ctk.CTkLabel(avatar_frame, text="", image=_render_avatar(user.profile_image))
    avatar_lbl.pack()

    
    info_frame = ctk.CTkFrame(hdr_inner, fg_color="transparent")
    info_frame.pack(side="left", fill="both", expand=True)

    name_title = ctk.CTkLabel(
        info_frame,
        text=f"{user.first_name} {user.last_name}",
        font=T.FONT_H1,
        text_color=T.TEXT,
        anchor="w",
    )
    name_title.pack(anchor="w")

    ctk.CTkLabel(
        info_frame, text=user.email, font=T.FONT_BODY, text_color=T.TEXT_DIM, anchor="w"
    ).pack(anchor="w", pady=(2, 0))

    role_badge = ctk.CTkLabel(
        info_frame,
        text=T.spaced(f"ROLE: {user.role.upper()}"),
        font=T.FONT_SMALL,
        text_color=T.ACCENT,
        anchor="w",
    )
    role_badge.pack(anchor="w", pady=(4, 0))

    
    form_card = T.card(frame, corner_radius=4)
    form_card.pack(fill="x", padx=24, pady=(0, 20))
    form = ctk.CTkFrame(form_card, fg_color="transparent")
    form.pack(padx=24, pady=20, fill="x")

    T.label(form, T.spaced("PROFILE SETTINGS (PASSWORD CHANGE BELOW)"), font=T.FONT_SMALL, color=T.MUTED).pack(
        anchor="w", pady=(0, 16)
    )

    
    photo_row = ctk.CTkFrame(form, fg_color="transparent")
    photo_row.pack(anchor="w", pady=(0, 16))

    def _choose_avatar() -> None:
        picked = pick_image_file()
        if picked:
            try:
                rel = save_image_to_uploads(picked, prefix=f"avatar_{user.user_id}")
                avatar_path_var[0] = rel
                new_img = _render_avatar(rel)
                avatar_lbl.configure(image=new_img)
                status_lbl.configure(text="Photo selected. Click 'SAVE PROFILE' to apply changes.", text_color=T.SUCCESS)
            except Exception as exc:
                status_lbl.configure(text=f"Failed to load image: {exc}", text_color=T.ERROR)

    T.ghost_button(
        photo_row, "CHOOSE NEW AVATAR", command=_choose_avatar, width=180
    ).pack(side="left")

    def _field(lbl: str, default: str) -> ctk.CTkEntry:
        T.label(form, lbl, font=T.FONT_LABEL, color=T.TEXT_DIM).pack(anchor="w")
        e = T.entry(form, width=400)
        e.insert(0, default)
        e.pack(anchor="w", pady=(2, 12))
        return e

    first_e = _field("First Name", user.first_name)
    last_e = _field("Last Name", user.last_name)
    contact_e = _field("Contact Number", user.contact_number or "")
    address_e = _field("Address", user.address or "")

    status_lbl = ctk.CTkLabel(
        form, text="", font=T.FONT_SMALL, text_color=T.ERROR, anchor="w"
    )
    status_lbl.pack(anchor="w", pady=(0, 8))

    def _save() -> None:
        status_lbl.configure(text="")
        try:
            updated = update_user_profile(
                user_id=user.user_id,
                first_name=first_e.get(),
                last_name=last_e.get(),
                address=address_e.get(),
                contact_number=contact_e.get(),
                profile_image=avatar_path_var[0],
                database_path=database_path,
            )
            user.first_name = updated.first_name
            user.last_name = updated.last_name
            user.profile_image = updated.profile_image
            name_title.configure(text=f"{updated.first_name} {updated.last_name}")
            status_lbl.configure(
                text="Profile and avatar updated successfully.", text_color=T.SUCCESS
            )
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.primary_button(form, "SAVE CHANGES", command=_save, width=400).pack(anchor="w")

    
    pwd_card = T.card(frame, corner_radius=4)
    pwd_card.pack(fill="x", padx=24, pady=(0, 24))
    pwd_form = ctk.CTkFrame(pwd_card, fg_color="transparent")
    pwd_form.pack(padx=24, pady=20, fill="x")

    T.label(pwd_form, T.spaced("SECURITY & PASSWORD"), font=T.FONT_SMALL, color=T.MUTED).pack(
        anchor="w", pady=(0, 6)
    )
    ctk.CTkLabel(
        pwd_form,
        text="To update your password, enter and verify your current password first.",
        font=T.FONT_SMALL,
        text_color=T.TEXT_DIM,
        anchor="w",
    ).pack(anchor="w", pady=(0, 14))

    
    T.label(pwd_form, "Current Password", font=T.FONT_LABEL, color=T.TEXT_DIM).pack(anchor="w")
    old_pw_row = ctk.CTkFrame(pwd_form, fg_color="transparent")
    old_pw_row.pack(anchor="w", pady=(2, 10))

    old_pw_e = T.entry(old_pw_row, placeholder="Enter current password", show="•", width=270)
    old_pw_e.pack(side="left", padx=(0, 10))

    pwd_verified = [False]

    
    new_pw_container = ctk.CTkFrame(pwd_form, fg_color="transparent")

    T.label(new_pw_container, "New Password", font=T.FONT_LABEL, color=T.TEXT_DIM).pack(anchor="w")
    new_pw_e = T.entry(new_pw_container, placeholder="Min 8 characters", show="•", width=400)
    new_pw_e.pack(anchor="w", pady=(2, 12))

    T.label(new_pw_container, "Confirm New Password", font=T.FONT_LABEL, color=T.TEXT_DIM).pack(anchor="w")
    confirm_pw_e = T.entry(new_pw_container, placeholder="Re-type new password", show="•", width=400)
    confirm_pw_e.pack(anchor="w", pady=(2, 14))

    pwd_status_lbl = ctk.CTkLabel(
        pwd_form, text="", font=T.FONT_SMALL, text_color=T.ERROR, anchor="w"
    )
    pwd_status_lbl.pack(anchor="w", pady=(0, 10))

    def _verify_old() -> None:
        pwd_status_lbl.configure(text="")
        old_val = old_pw_e.get().strip()
        if not old_val:
            pwd_status_lbl.configure(text="Please enter your current password first.", text_color=T.ERROR)
            return
        if verify_user_password(user.user_id, old_val, database_path):
            pwd_verified[0] = True
            old_pw_e.configure(state="disabled")
            verify_btn.configure(state="disabled", text="VERIFIED ✓")
            new_pw_container.pack(anchor="w", fill="x", pady=(0, 10))
            pwd_status_lbl.configure(
                text="Current password verified. You may now enter your new password below.",
                text_color=T.SUCCESS,
            )
        else:
            pwd_status_lbl.configure(text="Incorrect current password. Please try again.", text_color=T.ERROR)

    verify_btn = T.ghost_button(old_pw_row, "VERIFY", command=_verify_old, width=120)
    verify_btn.pack(side="left")

    def _change_password() -> None:
        pwd_status_lbl.configure(text="")
        if not pwd_verified[0]:
            pwd_status_lbl.configure(text="You must verify your current password first.", text_color=T.ERROR)
            return
        new_val = new_pw_e.get().strip()
        confirm_val = confirm_pw_e.get().strip()
        if len(new_val) < 8:
            pwd_status_lbl.configure(text="New password must contain at least 8 characters.", text_color=T.ERROR)
            return
        if new_val != confirm_val:
            pwd_status_lbl.configure(text="New password and confirmation do not match.", text_color=T.ERROR)
            return
        try:
            change_user_password(
                user_id=user.user_id,
                current_password=old_pw_e.get().strip(),
                new_password=new_val,
                database_path=database_path,
            )
            pwd_status_lbl.configure(text="Password successfully changed!", text_color=T.SUCCESS)
            
            new_pw_e.delete(0, "end")
            confirm_pw_e.delete(0, "end")
            new_pw_container.pack_forget()
            old_pw_e.configure(state="normal")
            old_pw_e.delete(0, "end")
            verify_btn.configure(state="normal", text="VERIFY")
            pwd_verified[0] = False
        except Exception as exc:
            pwd_status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.primary_button(new_pw_container, "UPDATE PASSWORD", command=_change_password, width=400).pack(anchor="w")

    return frame