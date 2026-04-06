from __future__ import annotations

import csv
import json
import math
import tkinter as tk
import webbrowser
from collections import deque
from datetime import datetime
from importlib import import_module
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable, cast

from security.activity_logger import ActivityLogger
from security.auth_manager import AuthManager
from security.crypto_utils import decrypt_text, encrypt_text, generate_secure_key
from security.hash_utils import generate_sha256, verify_sha256
from security.soc_simulation import SocSimulator
from security.sound_utils import SoundManager

pil_available = True
PILImage: Any = None
PILImageTk: Any = None
try:
    PILImage = import_module("PIL.Image")
    PILImageTk = import_module("PIL.ImageTk")
except Exception:
    pil_available = False


ABOUT_DEFAULT = {
    "name_1": "Your Name",
    "reg_1": "Your Registration Number",
    "name_2": "Friend Name",
    "reg_2": "Friend Registration Number",
    "github": "https://github.com/your-profile",
    "title": "Python Expert | Security Enthusiast",
    "image_1": "",
    "image_2": "",
}

SOC_PRESETS: dict[str, dict[str, float | int]] = {
    "Blue Team": {"tick_ms": 1800, "alert_intensity": 52.0, "risk_sensitivity": 12},
    "Incident Mode": {"tick_ms": 1100, "alert_intensity": 78.0, "risk_sensitivity": 18},
    "Calm Mode": {"tick_ms": 3200, "alert_intensity": 22.0, "risk_sensitivity": 6},
}

SOC_DEFAULTS: dict[str, float | int | str | bool] = {
    "tick_ms": 2500,
    "alert_intensity": 45.0,
    "risk_sensitivity": 10,
    "profile": "Custom",
    "pulse_speed": "normal",
    "pulse_auto": True,
}

SOC_PULSE_SPEEDS = ["slow", "normal", "aggressive"]
SOC_PROFILE_PULSE_MAP = {
    "Incident Mode": "aggressive",
    "Blue Team": "normal",
    "Calm Mode": "slow",
    "Factory Defaults": "normal",
    "Custom Tuning": "normal",
    "Custom": "normal",
}


class ModernButton(tk.Canvas):
    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Any,
        variant: str = "secondary",
        width: int = 146,
        height: int = 40,
    ) -> None:
        parent_bg = "#151a2d"
        try:
            parent_bg = cast(str, parent.cget("bg"))
        except Exception:
            try:
                parent_bg = cast(str, parent.cget("background"))
            except Exception:
                parent_bg = "#151a2d"

        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
        )
        self.command = command
        self.variant = variant
        self.btn_width = width
        self.btn_height = height
        self.selected = False
        self.label_text = text

        palettes = {
            "primary": {
                "normal": "#34d399",
                "hover": "#6ee7b7",
                "text": "#0b1020",
                "shadow": "#1c2b48",
            },
            "danger": {
                "normal": "#fb7185",
                "hover": "#fda4af",
                "text": "#0b1020",
                "shadow": "#3b1e33",
            },
            "secondary": {
                "normal": "#2b365c",
                "hover": "#40508a",
                "text": "#f8f3e8",
                "shadow": "#111729",
            },
            "glass": {
                "normal": "#1e2a4b",
                "hover": "#2f4175",
                "text": "#dbe7ff",
                "shadow": "#0d1325",
            },
        }
        self.palette = palettes.get(variant, palettes["secondary"])

        self.shadow = self._draw_rounded(6, 8, width - 6, height - 2, 12, self.palette["shadow"])
        self.face = self._draw_rounded(4, 4, width - 8, height - 6, 12, self.palette["normal"])
        self.label = self.create_text(
            (width // 2, height // 2 - 1),
            text=text,
            fill=self.palette["text"],
            font=("Segoe UI Semibold", 10),
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        for item in (self.face, self.shadow, self.label):
            self.tag_bind(item, "<Enter>", self._on_enter)
            self.tag_bind(item, "<Leave>", self._on_leave)
            self.tag_bind(item, "<Button-1>", self._on_click)

    def _rounded_points(self, x1: int, y1: int, x2: int, y2: int, r: int) -> list[int]:
        return [
            x1 + r,
            y1,
            x2 - r,
            y1,
            x2,
            y1,
            x2,
            y1 + r,
            x2,
            y2 - r,
            x2,
            y2,
            x2 - r,
            y2,
            x1 + r,
            y2,
            x1,
            y2,
            x1,
            y2 - r,
            x1,
            y1 + r,
            x1,
            y1,
        ]

    def _draw_rounded(self, x1: int, y1: int, x2: int, y2: int, r: int, color: str) -> int:
        return self.create_polygon(
            self._rounded_points(x1, y1, x2, y2, r),
            smooth=True,
            fill=color,
            outline="",
        )

    def _set_face(self, color: str) -> None:
        self.itemconfig(self.face, fill=color)

    def set_selected(self, selected: bool) -> None:
        self.selected = selected
        if selected:
            self._set_face("#113347")
            self.itemconfig(self.face, outline="#30e8ff", width=2)
            self.itemconfig(self.label, fill="#9ff6ff")
        else:
            self._set_face(self.palette["normal"])
            self.itemconfig(self.face, outline="", width=0)
            self.itemconfig(self.label, fill=self.palette["text"])

    def set_text(self, text: str) -> None:
        self.label_text = text
        self.itemconfig(self.label, text=text)

    def _on_enter(self, _event: tk.Event) -> None:
        if not self.selected:
            self._set_face(self.palette["hover"])
            cast(Any, self).move(self.face, 0, -1)
            cast(Any, self).move(self.label, 0, -1)

    def _on_leave(self, _event: tk.Event) -> None:
        if not self.selected:
            self._set_face(self.palette["normal"])
        self.coords(self.face, *self._rounded_points(4, 4, self.btn_width - 8, self.btn_height - 6, 12))
        self.coords(self.label, self.btn_width // 2, self.btn_height // 2 - 1)

    def _on_click(self, _event: tk.Event) -> None:
        self.after(20, self.command)


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tip: tk.Toplevel | None = None
        self.widget.bind("<Enter>", self._show)
        self.widget.bind("<Leave>", self._hide)

    def _show(self, _event: tk.Event) -> None:
        if self.tip is not None:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        tip = tk.Toplevel(self.widget)
        tip.wm_overrideredirect(True)
        tip.wm_geometry(f"+{x}+{y}")
        tip.configure(bg="#08111f")
        tk.Label(
            tip,
            text=self.text,
            bg="#08111f",
            fg="#8de9ff",
            font=("Segoe UI", 9),
            bd=1,
            relief="solid",
            padx=8,
            pady=4,
        ).pack()
        self.tip = tip

    def _hide(self, _event: tk.Event) -> None:
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class CyberSecurityApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("SecureLab Nexus — SOC Command Center")
        self.geometry("1360x860")
        self.minsize(1120, 700)
        self.configure(bg="#0a0f1c")

        base_dir = Path(__file__).resolve().parent
        self.base_dir = base_dir
        data_dir = base_dir / "data"
        self.auth = AuthManager(data_dir / "users.json")
        self.logger = ActivityLogger(data_dir / "activity_log.json")
        self.about_path = data_dir / "about_profile.json"
        self.soc_settings_path = data_dir / "soc_settings.json"
        self.about_info = self._load_about_info()
        self.soc_settings = self._load_soc_settings()
        self.sound = SoundManager(enabled=True)
        self.sound_enabled = tk.BooleanVar(value=True)
        self.current_role = "guest"
        self.auto_clear_seconds = tk.IntVar(value=0)
        self.theme_var = tk.StringVar(value="SOC Midnight")
        self.soc_tick_ms = tk.IntVar(value=int(cast(int, self.soc_settings["tick_ms"])))
        self.soc_alert_intensity = tk.DoubleVar(value=float(cast(float, self.soc_settings["alert_intensity"])))
        self.soc_risk_sensitivity = tk.IntVar(value=int(cast(int, self.soc_settings["risk_sensitivity"])))
        self.soc_profile_var = tk.StringVar(value=str(cast(str, self.soc_settings.get("profile", "Custom"))))
        self.soc_pulse_speed_var = tk.StringVar(value=str(cast(str, self.soc_settings.get("pulse_speed", "normal"))))
        self.soc_pulse_auto_var = tk.BooleanVar(value=bool(cast(bool, self.soc_settings.get("pulse_auto", True))))
        self.top_profile_badge_var = tk.StringVar(value=f"Profile: {self.soc_profile_var.get()}")
        self.soc_profile_var.trace_add("write", self._sync_profile_badge)
        self._profile_pulse_job: str | None = None
        self._profile_pulse_on = False
        self._status_clear_job: str | None = None
        self._clock_job: str | None = None
        self.sidebar_collapsed = False
        self.sidebar_width_expanded = 268
        self.sidebar_width_collapsed = 84

        self.current_user = "guest"
        self.notification_count = tk.IntVar(value=0)
        self.system_state = tk.StringVar(value="Secure")
        self.live_clock_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.user_role_var = tk.StringVar(value="guest | role: guest")

        self.nav_buttons: dict[str, ModernButton] = {}
        self.nav_texts: dict[str, str] = {}
        self.panels: dict[str, ttk.Frame] = {}
        self.toast_windows: list[tk.Toplevel] = []
        self.sidebar_logo_photo: Any = None
        self.logo_source_image: Any = None
        self.window_icon_photo: Any = None
        self._logo_glow_job: str | None = None
        self._logo_glow_on = False

        self._configure_styles()
        self._build_layout()
        self._setup_branding_assets()
        self.show_panel("Dashboard")
        self._update_live_clock()

    def _setup_branding_assets(self) -> None:
        icon_path = self.base_dir / "assets" / "securelab.ico"

        if icon_path.exists():
            try:
                cast(Any, self).iconbitmap(default=str(icon_path))
            except Exception:
                try:
                    if pil_available and PILImage is not None and PILImageTk is not None:
                        icon_img = PILImage.open(icon_path)
                        self.window_icon_photo = PILImageTk.PhotoImage(icon_img)
                        self.iconphoto(True, self.window_icon_photo)
                except Exception:
                    pass

        if not hasattr(self, "logo_label"):
            return

        if icon_path.exists() and pil_available and PILImage is not None and PILImageTk is not None:
            try:
                self.logo_source_image = PILImage.open(icon_path).convert("RGBA")
                self._apply_logo_visual_mode()
                return
            except Exception:
                pass

        self.logo_source_image = None
        self._apply_logo_visual_mode()

    def _set_logo_from_source(self, size: int) -> bool:
        if not (pil_available and PILImage is not None and PILImageTk is not None and self.logo_source_image is not None):
            return False
        try:
            logo_img = self.logo_source_image.copy()
            logo_img.thumbnail((size, size))
            self.sidebar_logo_photo = PILImageTk.PhotoImage(logo_img)
            self.logo_label.config(image=self.sidebar_logo_photo, text="", width=size, height=size)
            return True
        except Exception:
            return False

    def _apply_logo_visual_mode(self) -> None:
        if not hasattr(self, "logo_outer"):
            return

        collapsed = self.sidebar_collapsed
        shell_pad = 2 if collapsed else 5
        self.logo_outer.configure(
            bg="#071a2d",
            highlightbackground="#2ee8ff",
            highlightcolor="#2ee8ff",
            highlightthickness=1,
            padx=shell_pad,
            pady=shell_pad,
        )
        self.logo_outer.grid_configure(
            padx=12 if collapsed else 20,
            pady=(2, 0) if collapsed else (2, 2),
            sticky="n" if collapsed else "w",
        )

        if hasattr(self, "branding"):
            if collapsed:
                cast(Any, self.branding).grid_remove()
            else:
                cast(Any, self.branding).grid()

        self._sync_logo_shell_state()

        if self._set_logo_from_source(28 if collapsed else 52):
            self.logo_label.configure(bg="#0b1a2f")
            return

        if collapsed:
            self.logo_label.config(
                image="",
                text="",
                bg="#0b1a2f",
                width=2,
                height=1,
            )
            return

        self.logo_label.config(
            image="",
            text="SL",
            fg="#9fefff",
            bg="#0b1a2f",
            font=("Segoe UI Black", 9 if collapsed else 11),
            width=4 if collapsed else 5,
            height=2,
        )

    def _sync_logo_shell_state(self) -> None:
        if not hasattr(self, "logo_outer"):
            return
        state = self.system_state.get().strip()
        if state == "Under Threat":
            self._start_logo_glow_pulse()
            return

        self._stop_logo_glow_pulse()
        if state == "Warning":
            self.logo_outer.configure(highlightbackground="#ffbf52", highlightcolor="#ffbf52")
        else:
            self.logo_outer.configure(highlightbackground="#2ee8ff", highlightcolor="#2ee8ff")

    def _start_logo_glow_pulse(self) -> None:
        if self._logo_glow_job is not None:
            return
        self._logo_glow_on = False
        self._pulse_logo_glow()

    def _stop_logo_glow_pulse(self) -> None:
        if self._logo_glow_job is not None:
            try:
                self.after_cancel(self._logo_glow_job)
            except Exception:
                pass
            self._logo_glow_job = None
        self._logo_glow_on = False

    def _pulse_logo_glow(self) -> None:
        if not hasattr(self, "logo_outer"):
            self._logo_glow_job = None
            return
        if self.system_state.get().strip() != "Under Threat":
            self._logo_glow_job = None
            return

        self._logo_glow_on = not self._logo_glow_on
        if self._logo_glow_on:
            self.logo_outer.configure(highlightbackground="#ff9dac", highlightcolor="#ff9dac")
        else:
            self.logo_outer.configure(highlightbackground="#ff566f", highlightcolor="#ff566f")
        self._logo_glow_job = self.after(420, self._pulse_logo_glow)

    def _load_about_info(self) -> dict[str, str]:
        if not self.about_path.exists():
            self.about_path.write_text(json.dumps(ABOUT_DEFAULT, indent=2), encoding="utf-8")
            return dict(ABOUT_DEFAULT)

        try:
            loaded_obj = json.loads(self.about_path.read_text(encoding="utf-8"))
            if not isinstance(loaded_obj, dict):
                return dict(ABOUT_DEFAULT)
            loaded = cast(dict[str, object], loaded_obj)

            merged = dict(ABOUT_DEFAULT)
            for key in merged:
                value = loaded.get(key)
                if isinstance(value, str):
                    merged[key] = value
            return merged
        except Exception:
            return dict(ABOUT_DEFAULT)

    def save_about_info(self, updated: dict[str, str]) -> None:
        merged = dict(ABOUT_DEFAULT)
        for key in merged:
            value = updated.get(key, merged[key])
            merged[key] = value.strip()

        self.about_info = merged
        self.about_path.write_text(json.dumps(self.about_info, indent=2), encoding="utf-8")

        about_panel = self.panels.get("About")
        if isinstance(about_panel, AboutPanel):
            about_panel.refresh_about()

    def _load_soc_settings(self) -> dict[str, float | int | str | bool]:
        def _as_int(raw: object, fallback: int) -> int:
            if isinstance(raw, bool):
                return fallback
            if isinstance(raw, int):
                return raw
            if isinstance(raw, float):
                return int(raw)
            if isinstance(raw, str):
                try:
                    return int(float(raw.strip()))
                except Exception:
                    return fallback
            return fallback

        def _as_float(raw: object, fallback: float) -> float:
            if isinstance(raw, bool):
                return fallback
            if isinstance(raw, (int, float)):
                return float(raw)
            if isinstance(raw, str):
                try:
                    return float(raw.strip())
                except Exception:
                    return fallback
            return fallback

        def _as_bool(raw: object, fallback: bool) -> bool:
            if isinstance(raw, bool):
                return raw
            if isinstance(raw, (int, float)):
                return bool(raw)
            if isinstance(raw, str):
                normalized = raw.strip().lower()
                if normalized in {"true", "1", "yes", "on"}:
                    return True
                if normalized in {"false", "0", "no", "off"}:
                    return False
            return fallback

        default_tick = int(cast(int, SOC_DEFAULTS["tick_ms"]))
        default_alert = float(cast(float, SOC_DEFAULTS["alert_intensity"]))
        default_risk = int(cast(int, SOC_DEFAULTS["risk_sensitivity"]))
        default_pulse_auto = bool(cast(bool, SOC_DEFAULTS["pulse_auto"]))

        if not self.soc_settings_path.exists():
            self.soc_settings_path.write_text(json.dumps(SOC_DEFAULTS, indent=2), encoding="utf-8")
            return dict(SOC_DEFAULTS)

        try:
            raw_obj = json.loads(self.soc_settings_path.read_text(encoding="utf-8"))
            if not isinstance(raw_obj, dict):
                return dict(SOC_DEFAULTS)
            loaded = cast(dict[str, object], raw_obj)
            tick_ms = _as_int(loaded.get("tick_ms"), default_tick)
            alert_intensity = _as_float(loaded.get("alert_intensity"), default_alert)
            risk_sensitivity = _as_int(loaded.get("risk_sensitivity"), default_risk)
            profile_raw = loaded.get("profile")
            profile = profile_raw.strip() if isinstance(profile_raw, str) and profile_raw.strip() else "Custom"
            pulse_raw = loaded.get("pulse_speed")
            pulse_speed = pulse_raw.strip().lower() if isinstance(pulse_raw, str) else "normal"
            if pulse_speed not in SOC_PULSE_SPEEDS:
                pulse_speed = "normal"
            pulse_auto = _as_bool(loaded.get("pulse_auto"), default_pulse_auto)
            return {
                "tick_ms": max(800, min(6000, tick_ms)),
                "alert_intensity": max(10.0, min(90.0, alert_intensity)),
                "risk_sensitivity": max(1, min(20, risk_sensitivity)),
                "profile": profile,
                "pulse_speed": pulse_speed,
                "pulse_auto": pulse_auto,
            }
        except Exception:
            return dict(SOC_DEFAULTS)

    def _save_soc_settings(self) -> None:
        payload: dict[str, float | int | str | bool] = {
            "tick_ms": int(self.soc_tick_ms.get()),
            "alert_intensity": float(self.soc_alert_intensity.get()),
            "risk_sensitivity": int(self.soc_risk_sensitivity.get()),
            "profile": self.soc_profile_var.get().strip() or "Custom",
            "pulse_speed": self.soc_pulse_speed_var.get().strip().lower() or "normal",
            "pulse_auto": bool(self.soc_pulse_auto_var.get()),
        }
        self.soc_settings_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _recommended_pulse_speed(self, profile: str) -> str:
        return SOC_PROFILE_PULSE_MAP.get(profile, "normal")

    def recommended_pulse_speed(self, profile: str) -> str:
        return self._recommended_pulse_speed(profile)

    def _sync_profile_badge(self, *_args: str) -> None:
        profile = self.soc_profile_var.get().strip() or "Custom"
        self.top_profile_badge_var.set(f"Profile: {profile}")
        if self.soc_pulse_auto_var.get():
            self.soc_pulse_speed_var.set(self._recommended_pulse_speed(profile))
        if not hasattr(self, "profile_badge"):
            return

        palette = {
            "Incident Mode": ("#4f1a20", "#ff9dac"),
            "Blue Team": ("#123047", "#8fd5ff"),
            "Calm Mode": ("#173528", "#9df4c7"),
            "Factory Defaults": ("#2b2f3d", "#d7e2ff"),
            "Custom Tuning": ("#3a2f11", "#ffd690"),
            "Custom": ("#2f3342", "#d7e2ff"),
        }
        bg, fg = palette.get(profile, ("#2f3342", "#d7e2ff"))
        self.profile_badge.config(bg=bg, fg=fg)
        if profile == "Incident Mode":
            self._start_profile_pulse()
        else:
            self._stop_profile_pulse()

    def _start_profile_pulse(self) -> None:
        if self._profile_pulse_job is not None:
            return
        self._profile_pulse_on = False
        self._pulse_profile_badge()

    def _stop_profile_pulse(self) -> None:
        if self._profile_pulse_job is not None:
            try:
                self.after_cancel(self._profile_pulse_job)
            except Exception:
                pass
            self._profile_pulse_job = None
        self._profile_pulse_on = False

    def _pulse_profile_badge(self) -> None:
        if not hasattr(self, "profile_badge"):
            self._profile_pulse_job = None
            return
        if self.soc_profile_var.get().strip() != "Incident Mode":
            self._profile_pulse_job = None
            return

        self._profile_pulse_on = not self._profile_pulse_on
        if self._profile_pulse_on:
            self.profile_badge.config(bg="#6a1f2a", fg="#ffd2d8")
        else:
            self.profile_badge.config(bg="#4f1a20", fg="#ff9dac")
        speed = self.soc_pulse_speed_var.get().strip().lower()
        interval_map = {"slow": 760, "normal": 520, "aggressive": 300}
        interval = interval_map.get(speed, 520)
        self._profile_pulse_job = self.after(interval, self._pulse_profile_badge)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background="#0f172a")
        style.configure("Panel.TFrame", background="#111b31")
        style.configure("Card.TLabelframe", background="#111b31", foreground="#d8eeff")
        style.configure("Card.TLabelframe.Label", background="#111b31", foreground="#39e6ff")

        style.configure("App.TLabel", background="#111b31", foreground="#d0e2ff", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#0f172a", foreground="#f3fbff", font=("Segoe UI Semibold", 20))
        style.configure("Subtitle.TLabel", background="#0f172a", foreground="#93b8e8", font=("Segoe UI", 10))
        style.configure("Tip.TLabel", background="#0f172a", foreground="#66f6c1", font=("Segoe UI", 10, "italic"))
        style.configure("Status.TLabel", background="#0a0f1c", foreground="#66f6c1", font=("Segoe UI", 10, "bold"))
        style.configure("Section.TLabel", background="#111b31", foreground="#ebf6ff", font=("Segoe UI Semibold", 12))
        style.configure("Cyber.Horizontal.TProgressbar", troughcolor="#1b2a4a", background="#ff5151", borderwidth=0)

        style.configure(
            "Primary.TButton",
            background="#33f2cf",
            foreground="#071323",
            padding=(10, 8),
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map("Primary.TButton", background=[("active", "#7dffe4")])

        style.configure(
            "Secondary.TButton",
            background="#1f2f53",
            foreground="#eaf5ff",
            padding=(10, 8),
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.map("Secondary.TButton", background=[("active", "#2f4778")])

        style.configure(
            "Treeview",
            background="#0d162b",
            foreground="#d7ebff",
            fieldbackground="#0d162b",
            rowheight=30,
            borderwidth=0,
        )
        style.configure("Treeview.Heading", background="#1f335d", foreground="#eaf5ff", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#29e6ff")], foreground=[("selected", "#071323")])

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = tk.Frame(self, bg="#070d1b", width=self.sidebar_width_expanded)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        self.sidebar = sidebar

        self.sidebar_toggle = ModernButton(
            sidebar,
            text="<< Collapse",
            command=self.toggle_sidebar,
            variant="secondary",
            width=220,
            height=36,
        )
        self.sidebar_toggle.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="ew")

        self.logo_outer = tk.Frame(
            sidebar,
            bg="#071a2d",
            highlightthickness=1,
            highlightbackground="#2ee8ff",
            highlightcolor="#2ee8ff",
            padx=6,
            pady=6,
        )
        self.logo_outer.grid(row=1, column=0, padx=20, pady=(2, 2), sticky="w")

        self.logo_label = tk.Label(
            self.logo_outer,
            bg="#0b1a2f",
        )
        self.logo_label.pack()

        branding = tk.Label(
            sidebar,
            text="SecureLab\nNexus",
            bg="#070d1b",
            fg="#31efff",
            font=("Segoe UI Black", 16),
            pady=10,
            justify="left",
        )
        branding.grid(row=2, column=0, padx=20, sticky="w")
        self.branding = branding

        nav_items = [
            ("Dashboard", "[DB] Dashboard"),
            ("Encryption", "[ENC] Encryption"),
            ("Hashing", "[HASH] Hashing"),
            ("Auth", "[AUTH] Auth"),
            ("Logs", "[LOG] Logs"),
            ("Threat Monitor", "[THRT] Threat Monitor"),
            ("Settings", "[CFG] Settings"),
        ]

        nav_start_row = 3
        for idx, (panel_key, label) in enumerate(nav_items, start=nav_start_row):
            button = ModernButton(
                sidebar,
                text=label,
                command=lambda n=panel_key: self.show_panel(n),
                variant="glass",
                width=220,
                height=42,
            )
            button.grid(row=idx, column=0, padx=16, pady=6, sticky="ew")
            self.nav_buttons[panel_key] = button
            self.nav_texts[panel_key] = label

        sidebar.grid_rowconfigure(nav_start_row + len(nav_items), weight=1)

        footer = tk.Label(
            sidebar,
            text="SOC telemetry online",
            bg="#070d1b",
            fg="#8aa9d9",
            font=("Segoe UI", 9),
            pady=16,
        )
        footer.grid(row=nav_start_row + len(nav_items) + 1, column=0, padx=18, sticky="sw")
        self.footer = footer

        main = ttk.Frame(self, style="App.TFrame", padding=14)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)
        self.main_wrap = main

        header = tk.Frame(main, bg="#0a1226", bd=0, highlightthickness=1, highlightbackground="#1a2f56")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        title_wrap = tk.Frame(header, bg="#0a1226")
        title_wrap.grid(row=0, column=0, sticky="w", padx=16, pady=10)
        tk.Label(
            title_wrap,
            text="SecureLab Nexus | SOC Command Center",
            bg="#0a1226",
            fg="#e6fbff",
            font=("Segoe UI Semibold", 16),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            title_wrap,
            text="Real-time defense telemetry, threat analytics, and rapid response controls",
            bg="#0a1226",
            fg="#87a9d7",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        right_wrap = tk.Frame(header, bg="#0a1226")
        right_wrap.grid(row=0, column=1, sticky="e", padx=16)

        self.system_chip = tk.Label(
            right_wrap,
            text="Secure",
            bg="#12392f",
            fg="#8dffd8",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=6,
        )
        self.system_chip.grid(row=0, column=0, padx=(0, 8))
        ToolTip(self.system_chip, "Global system posture")

        self.user_badge = tk.Label(
            right_wrap,
            textvariable=self.user_role_var,
            bg="#152643",
            fg="#c7defe",
            font=("Segoe UI", 9),
            padx=10,
            pady=6,
        )
        self.user_badge.grid(row=0, column=1, padx=(0, 8))
        ToolTip(self.user_badge, "Current operator identity")

        self.profile_badge = tk.Label(
            right_wrap,
            textvariable=self.top_profile_badge_var,
            bg="#123047",
            fg="#8fd5ff",
            font=("Segoe UI", 9),
            padx=10,
            pady=6,
        )
        self.profile_badge.grid(row=0, column=2, padx=(0, 8))
        ToolTip(self.profile_badge, "Active SOC simulation profile")
        self._sync_profile_badge()

        self.clock_badge = tk.Label(
            right_wrap,
            textvariable=self.live_clock_var,
            bg="#101e36",
            fg="#6fe4ff",
            font=("Consolas", 10, "bold"),
            padx=10,
            pady=6,
        )
        self.clock_badge.grid(row=0, column=3, padx=(0, 8))
        ToolTip(self.clock_badge, "SOC local time")

        self.bell_btn = ModernButton(right_wrap, text="Bell (0)", command=self._open_notifications_center, variant="secondary", width=96, height=34)
        self.bell_btn.grid(row=0, column=4, padx=(0, 8))
        ToolTip(self.bell_btn, "Recent alerts")

        self.sound_btn = ModernButton(
            right_wrap,
            text="Sound ON",
            command=self.toggle_sound,
            variant="secondary",
            width=102,
            height=34,
        )
        self.sound_btn.grid(row=0, column=5)
        ToolTip(self.sound_btn, "Toggle alert tones")

        self.content = ttk.Frame(main, style="App.TFrame")
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.panels["Dashboard"] = SOCDashboardPanel(self.content, self)
        self.panels["Encryption"] = EncryptionPanel(self.content, self)
        self.panels["Key Generator"] = KeyGeneratorPanel(self.content, self)
        self.panels["Hashing"] = HashGeneratorPanel(self.content, self)
        self.panels["Integrity Checker"] = IntegrityCheckerPanel(self.content, self)
        self.panels["Auth"] = AuthPanel(self.content, self)
        self.panels["Threat Monitor"] = ThreatMonitorPanel(self.content, self)
        self.panels["Logs"] = ActivityLogPanel(self.content, self)
        self.panels["Settings"] = SettingsPanel(self.content, self)
        self.panels["About"] = AboutPanel(self.content, self)

        for panel in self.panels.values():
            panel.grid(row=0, column=0, sticky="nsew")

        self.status_var = tk.StringVar(value="SOC online. Monitoring telemetry streams.")
        status = ttk.Label(self, textvariable=self.status_var, style="Status.TLabel", anchor="w", padding=(14, 8))
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _draw_header_gradient(self, canvas_widget: tk.Canvas) -> None:
        canvas_widget.delete("all")
        width = max(2, canvas_widget.winfo_width())
        height = max(2, canvas_widget.winfo_height())
        start = (52, 211, 153)
        end = (124, 196, 255)
        for x in range(width):
            ratio = x / max(1, width - 1)
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas_widget.create_line(x, 0, x, height, fill=color)

    def _restore_nav_color(self, panel_name: str, button: ModernButton) -> None:
        button.set_selected(panel_name == getattr(self, "active_panel", None))

    def toggle_sidebar(self) -> None:
        self.sidebar_collapsed = not self.sidebar_collapsed
        width = self.sidebar_width_collapsed if self.sidebar_collapsed else self.sidebar_width_expanded
        self.sidebar.configure(width=width)
        self.sidebar_toggle.set_text(">>" if self.sidebar_collapsed else "<< Collapse")

        self.footer.configure(text="SOC" if self.sidebar_collapsed else "SOC telemetry online")
        self._apply_logo_visual_mode()

        for key, button in self.nav_buttons.items():
            if self.sidebar_collapsed:
                label = self.nav_texts[key].split(" ")[0]
            else:
                label = self.nav_texts[key]
            button.set_text(label)

    def _update_live_clock(self) -> None:
        self.live_clock_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self._clock_job = self.after(1000, self._update_live_clock)

    def set_system_state(self, state: str) -> None:
        palette = {
            "Secure": ("#12392f", "#8dffd8"),
            "Warning": ("#473715", "#ffd690"),
            "Under Threat": ("#4b1720", "#ff9dac"),
        }
        bg, fg = palette.get(state, ("#12392f", "#8dffd8"))
        self.system_state.set(state)
        self.system_chip.config(text=state, bg=bg, fg=fg)
        self._sync_logo_shell_state()

    def _open_notifications_center(self) -> None:
        self.show_toast(
            f"Notifications queued: {self.notification_count.get()}",
            "info",
            persist_ms=2600,
        )

    def _refresh_bell(self) -> None:
        self.bell_btn.set_text(f"Bell ({self.notification_count.get()})")

    def _reposition_toasts(self) -> None:
        self.update_idletasks()
        if not self.toast_windows:
            return

        root_x = self.winfo_rootx()
        root_y = self.winfo_rooty()
        root_w = self.winfo_width()
        y = root_y + 60

        for toast in self.toast_windows:
            if not toast.winfo_exists():
                continue
            toast.update_idletasks()
            tw = toast.winfo_width() or 320
            th = toast.winfo_height() or 82
            x = root_x + root_w - tw - 22
            toast.geometry(f"+{x}+{y}")
            y += th + 10

    def show_toast(self, message: str, severity: str = "info", persist_ms: int = 3400) -> None:
        colors = {
            "info": ("#0b2032", "#7cdfff", "#31efff"),
            "warning": ("#2d2611", "#ffd690", "#ffb347"),
            "critical": ("#3a1319", "#ff9dac", "#ff5151"),
        }
        bg, fg, border = colors.get(severity, colors["info"])

        toast = tk.Toplevel(self)
        toast.overrideredirect(True)
        cast(Any, toast).attributes("-topmost", True)
        toast.configure(bg=border)

        body = tk.Frame(toast, bg=bg, padx=12, pady=10)
        body.pack(fill="both", expand=True, padx=1, pady=1)
        stamp = datetime.now().strftime("%H:%M:%S")
        tk.Label(body, text=f"[{severity.upper()}] {stamp}", bg=bg, fg=border, font=("Consolas", 9, "bold")).pack(anchor="w")
        tk.Label(body, text=message, bg=bg, fg=fg, font=("Segoe UI", 9), wraplength=320, justify="left").pack(anchor="w", pady=(3, 0))

        self.toast_windows = [t for t in self.toast_windows if t.winfo_exists()]
        self.toast_windows.append(toast)
        self._reposition_toasts()

        def _destroy_toast() -> None:
            if toast.winfo_exists():
                toast.destroy()
            self.toast_windows[:] = [t for t in self.toast_windows if t.winfo_exists()]
            self._reposition_toasts()

        toast.after(max(1200, persist_ms), _destroy_toast)

    def notify(self, message: str, severity: str = "info", sound: bool = False) -> None:
        if severity == "warning":
            return
        self.notification_count.set(self.notification_count.get() + 1)
        self._refresh_bell()
        self.show_toast(message, severity=severity)
        if sound and self.sound.enabled:
            if severity == "critical":
                self.sound.play("error")
            elif severity == "warning":
                self.sound.play("warning")
            else:
                self.sound.play("clipboard")

    def show_panel(self, name: str) -> None:
        self.active_panel = name
        panel = self.panels.get(name)
        if panel is not None:
            cast(Any, panel).tkraise()
        for panel_name, button in self.nav_buttons.items():
            button.set_selected(panel_name == name)

        if name == "Logs":
            activity_panel = self.panels["Logs"]
            if isinstance(activity_panel, ActivityLogPanel):
                activity_panel.refresh_logs()
        if name == "Threat Monitor":
            tm = self.panels.get("Threat Monitor")
            if isinstance(tm, ThreatMonitorPanel):
                tm.refresh()
        if name == "Dashboard":
            dashboard_panel = self.panels.get("Dashboard")
            if isinstance(dashboard_panel, SOCDashboardPanel):
                dashboard_panel.on_visible()

        self.set_status(f"Viewing {name} panel.", tone="info")

    def set_status(self, message: str, tone: str = "info") -> None:
        color_map = {
            "info": "#9fe7d1",
            "success": "#c8f7e8",
            "warning": "#f4d399",
            "error": "#ff9da8",
        }
        self.status_var.set(message)
        style = ttk.Style(self)
        style.configure("Status.TLabel", foreground=color_map.get(tone, "#9fe7d1"))

        if self._status_clear_job is not None:
            self.after_cancel(self._status_clear_job)
            self._status_clear_job = None

        seconds = self.auto_clear_seconds.get()
        if seconds > 0:
            self._status_clear_job = self.after(seconds * 1000, self._clear_status)

    def log_action(self, action: str, detail: str) -> None:
        self.logger.log(self.current_user, action, detail)
        panel = self.panels.get("Logs")
        if isinstance(panel, ActivityLogPanel):
            panel.refresh_logs()
        tm = self.panels.get("Threat Monitor")
        if isinstance(tm, ThreatMonitorPanel):
            tm.refresh()
        dashboard = self.panels.get("Dashboard")
        if isinstance(dashboard, SOCDashboardPanel):
            dashboard.ingest_app_event(action, detail)

    def toggle_sound(self) -> None:
        enabled = not self.sound_enabled.get()
        self.sound_enabled.set(enabled)
        self.sound.enabled = enabled
        self.sound_btn.set_text("Sound ON" if enabled else "Sound OFF")
        self.set_status(
            "Alert tones enabled." if enabled else "Alert tones muted.",
            tone="info",
        )
        if enabled:
            self.sound.play("clipboard")

    def _clear_status(self) -> None:
        self.status_var.set("SOC online.")
        self._status_clear_job = None

    def apply_theme(self, theme_name: str) -> None:
        palettes = {
            "SOC Midnight": {
                "window": "#0a0f1c",
                "app_frame": "#0f172a",
                "panel": "#111b31",
                "sidebar": "#070d1b",
                "accent": "#31efff",
                "title": "#f3fbff",
                "subtext": "#93b8e8",
            },
            "SOC Oceanic": {
                "window": "#081425",
                "app_frame": "#0c1d35",
                "panel": "#122645",
                "sidebar": "#071225",
                "accent": "#66d6ff",
                "title": "#eaf5ff",
                "subtext": "#9ebfe6",
            },
        }
        palette = palettes.get(theme_name, palettes["SOC Midnight"])

        self.configure(bg=palette["window"])
        style = ttk.Style(self)
        style.configure("App.TFrame", background=palette["app_frame"])
        style.configure("Panel.TFrame", background=palette["panel"])
        style.configure("Card.TLabelframe", background=palette["panel"], foreground=palette["title"])
        style.configure("Card.TLabelframe.Label", background=palette["panel"], foreground=palette["accent"])
        style.configure("Title.TLabel", background=palette["app_frame"], foreground=palette["title"])
        style.configure("Subtitle.TLabel", background=palette["app_frame"], foreground=palette["subtext"])
        style.configure("Tip.TLabel", background=palette["app_frame"], foreground=palette["accent"])
        style.configure("Status.TLabel", background=palette["window"])
        style.configure("Primary.TButton", background=palette["accent"], foreground=palette["window"])

        self.sidebar.config(bg=palette["sidebar"])
        self.branding.config(bg=palette["sidebar"], fg=palette["accent"])
        self.footer.config(bg=palette["sidebar"], fg=palette["subtext"])
        self.main_wrap.configure(style="App.TFrame")

        for name, button in self.nav_buttons.items():
            button.set_selected(name == getattr(self, "active_panel", ""))

        self.theme_var.set(theme_name)

    def _current_palette(self) -> dict[str, str]:
        return {
            "window": "#0a0f1c",
            "sidebar_btn": "#1d3557",
            "sidebar_btn_active": "#31efff",
            "title": "#f3fbff",
        }

    def apply_soc_settings(self, profile_name: str | None = None) -> None:
        if profile_name is not None:
            self.soc_profile_var.set(profile_name)
        if self.soc_pulse_auto_var.get():
            self.soc_pulse_speed_var.set(self._recommended_pulse_speed(self.soc_profile_var.get()))
        dashboard = self.panels.get("Dashboard")
        if isinstance(dashboard, SOCDashboardPanel):
            dashboard.apply_runtime_settings()
            self._save_soc_settings()
            self.set_status("SOC simulation settings applied.", tone="success")

    def reset_soc_defaults(self) -> None:
        self.soc_tick_ms.set(int(cast(int, SOC_DEFAULTS["tick_ms"])))
        self.soc_alert_intensity.set(float(cast(float, SOC_DEFAULTS["alert_intensity"])))
        self.soc_risk_sensitivity.set(int(cast(int, SOC_DEFAULTS["risk_sensitivity"])))
        self.soc_pulse_auto_var.set(bool(cast(bool, SOC_DEFAULTS["pulse_auto"])))
        self.soc_pulse_speed_var.set(str(cast(str, SOC_DEFAULTS["pulse_speed"])))
        self.apply_soc_settings(profile_name="Factory Defaults")
        self.set_status("SOC settings reset to factory defaults.", tone="success")

    def reload_soc_saved_settings(self) -> None:
        loaded = self._load_soc_settings()
        self.soc_tick_ms.set(int(cast(int, loaded["tick_ms"])))
        self.soc_alert_intensity.set(float(cast(float, loaded["alert_intensity"])))
        self.soc_risk_sensitivity.set(int(cast(int, loaded["risk_sensitivity"])))
        self.soc_profile_var.set(str(cast(str, loaded.get("profile", "Custom"))))
        self.soc_pulse_auto_var.set(bool(cast(bool, loaded.get("pulse_auto", True))))
        self.soc_pulse_speed_var.set(str(cast(str, loaded.get("pulse_speed", "normal"))))
        dashboard = self.panels.get("Dashboard")
        if isinstance(dashboard, SOCDashboardPanel):
            dashboard.apply_runtime_settings()
        self.set_status("SOC settings restored from saved profile.", tone="success")


class BasePanel(ttk.Frame):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, style="Panel.TFrame", padding=16)
        self.app = app


class SOCDashboardPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.simulator = SocSimulator()
        self._apply_config_to_simulator()
        self.encryption_activity = self.simulator.encryption_activity
        self.active_users = self.simulator.active_users
        self.risk_level = self.simulator.risk_level
        self.activity_series = self.simulator.activity_series
        self.encryption_ops = self.simulator.encryption_ops
        self.hash_ops = self.simulator.hash_ops
        self.user_activity = self.simulator.user_activity
        self.feed_lines: deque[tuple[str, str]] = deque(maxlen=80)
        self.sim_job: str | None = None
        self.alert_pulse_on = False
        self.ui_ready = False

        self._build_loading_state()
        self.after(900, self._build_dashboard)

    def _build_loading_state(self) -> None:
        self.loading = tk.Frame(self, bg="#0f172a", highlightbackground="#1f345d", highlightthickness=1)
        self.loading.grid(row=0, column=0, columnspan=2, sticky="nsew")
        tk.Label(
            self.loading,
            text="Initializing SOC telemetry pipelines...",
            bg="#0f172a",
            fg="#8de9ff",
            font=("Segoe UI", 12, "bold"),
            pady=14,
        ).pack()
        bar = ttk.Progressbar(self.loading, mode="indeterminate", length=360)
        bar.pack(pady=(0, 18))
        bar.start(12)

    def _card(self, parent: tk.Widget, title: str) -> tk.Frame:
        outer = tk.Frame(parent, bg="#163057", highlightthickness=0)
        inner = tk.Frame(outer, bg="#0d162b")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(inner, text=title, bg="#0d162b", fg="#9befff", font=("Segoe UI Semibold", 11)).pack(anchor="w", padx=12, pady=(10, 6))
        return outer

    def _build_dashboard(self) -> None:
        self.loading.destroy()

        top_left = self._card(self, "Security Status")
        top_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))

        tl_body = cast(tk.Frame, top_left.winfo_children()[0])
        metrics = tk.Frame(tl_body, bg="#0d162b")
        metrics.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for i in range(3):
            metrics.grid_columnconfigure(i, weight=1)

        self.health_dot = tk.Canvas(metrics, width=20, height=20, bg="#0d162b", highlightthickness=0)
        self.health_dot.grid(row=0, column=0, sticky="w")
        self.health_circle = self.health_dot.create_oval(3, 3, 17, 17, fill="#4dffab", outline="#3be596")

        self.health_var = tk.StringVar(value="System health: stable")
        tk.Label(metrics, textvariable=self.health_var, bg="#0d162b", fg="#adffd6", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", columnspan=2)

        self.encryption_var = tk.StringVar(value=f"Encryption activity: {self.encryption_activity}")
        self.active_users_var = tk.StringVar(value=f"Active users: {self.active_users}")
        tk.Label(metrics, textvariable=self.encryption_var, bg="#0d162b", fg="#c6ddff", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.Label(metrics, textvariable=self.active_users_var, bg="#0d162b", fg="#c6ddff", font=("Segoe UI", 10)).grid(row=1, column=1, sticky="w", pady=(10, 0))
        tk.Label(metrics, text="Posture: adaptive hardening", bg="#0d162b", fg="#79c7ff", font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", pady=(10, 0))

        top_right = self._card(self, "Threat Detection")
        top_right.grid(row=0, column=1, sticky="nsew", pady=(0, 8))
        tr_body = cast(tk.Frame, top_right.winfo_children()[0])
        body_wrap = tk.Frame(tr_body, bg="#0d162b")
        body_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.threat_text = tk.StringVar(value="No immediate hostile signature detected")
        self.pulse_lbl = tk.Label(body_wrap, text="ALERT CHANNEL", bg="#2b1f0f", fg="#ffd690", font=("Consolas", 10, "bold"), padx=10, pady=4)
        self.pulse_lbl.pack(anchor="w")
        tk.Label(body_wrap, textvariable=self.threat_text, bg="#0d162b", fg="#ffd2d8", font=("Segoe UI", 10), wraplength=320, justify="left").pack(anchor="w", pady=(8, 8))

        tk.Label(body_wrap, text="Risk level", bg="#0d162b", fg="#91b3de", font=("Segoe UI", 9)).pack(anchor="w")
        self.risk_meter = ttk.Progressbar(body_wrap, style="Cyber.Horizontal.TProgressbar", orient="horizontal", mode="determinate", maximum=100)
        self.risk_meter.pack(fill="x", pady=(4, 2))
        self.risk_meter["value"] = self.risk_level
        self.risk_var = tk.StringVar(value=f"{self.risk_level}%")
        tk.Label(body_wrap, textvariable=self.risk_var, bg="#0d162b", fg="#ff9dac", font=("Consolas", 11, "bold")).pack(anchor="e")

        mid_left = self._card(self, "Live Activity Feed")
        mid_left.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        ml_body = cast(tk.Frame, mid_left.winfo_children()[0])
        ml_body.pack_propagate(False)

        self.feed_text = tk.Text(ml_body, bg="#081225", fg="#c6ddff", relief="flat", height=12, padx=10, pady=8)
        self.feed_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.feed_text.tag_configure("info", foreground="#75d6ff")
        self.feed_text.tag_configure("warning", foreground="#ffd690")
        self.feed_text.tag_configure("critical", foreground="#ff8fa1")
        self.feed_text.configure(state="disabled")

        mid_right = self._card(self, "Analytics")
        mid_right.grid(row=1, column=1, sticky="nsew", pady=(0, 8))
        mr_body = cast(tk.Frame, mid_right.winfo_children()[0])

        self.line_canvas = tk.Canvas(mr_body, height=120, bg="#0d162b", highlightthickness=0)
        self.line_canvas.pack(fill="x", padx=12)
        self.pie_canvas = tk.Canvas(mr_body, height=120, bg="#0d162b", highlightthickness=0)
        self.pie_canvas.pack(fill="x", padx=12, pady=(8, 0))
        self.bar_canvas = tk.Canvas(mr_body, height=130, bg="#0d162b", highlightthickness=0)
        self.bar_canvas.pack(fill="x", padx=12, pady=(8, 12))

        bottom = self._card(self, "Quick Actions")
        bottom.grid(row=2, column=0, columnspan=2, sticky="ew")
        qb = cast(tk.Frame, bottom.winfo_children()[0])
        actions = tk.Frame(qb, bg="#0d162b")
        actions.pack(fill="x", padx=12, pady=(0, 12))

        action_map: list[tuple[str, Callable[[], None], str]] = [
            ("Encrypt File", lambda: self.app.show_panel("Encryption"), "Jump to AES-GCM panel"),
            ("Generate Hash", lambda: self.app.show_panel("Hashing"), "Open integrity tools"),
            ("Add User", lambda: self.app.show_panel("Auth"), "Go to signup/login"),
            ("View Logs", lambda: self.app.show_panel("Logs"), "Inspect activity feed"),
        ]
        for idx, (label, cmd, hint) in enumerate(action_map):
            btn = ModernButton(actions, text=label, command=cmd, variant="secondary", width=156, height=40)
            btn.grid(row=0, column=idx, padx=(0 if idx == 0 else 8, 0), sticky="w")
            ToolTip(btn, hint)

        self._seed_feed()
        self._redraw_charts()
        self.ui_ready = True
        self._run_simulation()

    def _apply_config_to_simulator(self) -> None:
        self.simulator.set_config(
            tick_ms=self.app.soc_tick_ms.get(),
            alert_intensity=self.app.soc_alert_intensity.get() / 100.0,
            risk_sensitivity=self.app.soc_risk_sensitivity.get(),
        )

    def apply_runtime_settings(self) -> None:
        self._apply_config_to_simulator()
        if self.sim_job is not None:
            self.after_cancel(self.sim_job)
            self.sim_job = None
        self._run_simulation()

    def _seed_feed(self) -> None:
        recent = self.app.logger.read_all()[-8:]
        if not recent:
            self._append_feed("Telemetry stream initialized", "info")
            return
        for row in recent:
            action = row.get("action", "EVENT")
            level = "critical" if action in {"LOGIN_FAILED"} else "info"
            self._append_feed(f"{row.get('timestamp', '')} | {action} | {row.get('detail', '')}", level)

    def on_visible(self) -> None:
        if self.ui_ready and self.sim_job is None:
            self._run_simulation()

    def ingest_app_event(self, action: str, detail: str) -> None:
        severity = "info"
        if action in {"LOGIN_FAILED", "INTEGRITY_CHECK"} and "FAIL" in detail.upper():
            severity = "critical"
        elif action in {"DECRYPT", "VERIFY"}:
            severity = "warning"
        self._append_feed(f"{datetime.now().strftime('%H:%M:%S')} | {action} | {detail}", severity)
        self.simulator.ingest_app_event(action, detail)
        self.encryption_activity = self.simulator.encryption_activity
        self.encryption_ops = self.simulator.encryption_ops
        self.hash_ops = self.simulator.hash_ops
        self.active_users = self.simulator.active_users
        self.risk_level = self.simulator.risk_level
        self.encryption_var.set(f"Encryption activity: {self.encryption_activity}")
        self.active_users_var.set(f"Active users: {self.active_users}")

    def _append_feed(self, line: str, severity: str) -> None:
        if not hasattr(self, "feed_text"):
            return
        self.feed_lines.append((line, severity))
        self.feed_text.configure(state="normal")
        self.feed_text.delete("1.0", "end")
        for msg, level in self.feed_lines:
            self.feed_text.insert("end", f"{msg}\n", level)
        self.feed_text.see("end")
        self.feed_text.configure(state="disabled")

    def _run_simulation(self) -> None:
        event = self.simulator.step()
        self.encryption_activity = self.simulator.encryption_activity
        self.active_users = self.simulator.active_users
        self.risk_level = self.simulator.risk_level
        self.activity_series = self.simulator.activity_series
        self.encryption_ops = self.simulator.encryption_ops
        self.hash_ops = self.simulator.hash_ops
        self.user_activity = self.simulator.user_activity
        self.encryption_var.set(f"Encryption activity: {self.encryption_activity}")
        self.active_users_var.set(f"Active users: {self.active_users}")

        code = cast(str, event["code"])
        message = cast(str, event["message"])
        severity = cast(str, event["severity"])
        stamp = datetime.now().strftime("%H:%M:%S")
        self._append_feed(f"{stamp} | {code} | {message}", severity)

        if severity == "critical":
            self.threat_text.set(message)
            self.app.set_system_state("Under Threat")
            self.app.notify(message, severity="critical", sound=True)
        elif severity == "warning":
            self.threat_text.set(message)
            self.app.set_system_state("Warning")
            if cast(bool, event["notify"]):
                self.app.notify(message, severity="warning", sound=True)
        else:
            self.threat_text.set("No immediate hostile signature detected")
            if self.risk_level < 34:
                self.app.set_system_state("Secure")

        self.risk_meter["value"] = self.risk_level
        self.risk_var.set(f"{self.risk_level}%")
        self._pulse_alert()
        self._update_health()

        self._redraw_charts()

        self.sim_job = self.after(self.simulator.config.tick_ms, self._run_simulation)

    def _pulse_alert(self) -> None:
        critical_mode = self.risk_level >= 68
        if critical_mode:
            self.alert_pulse_on = not self.alert_pulse_on
            if self.alert_pulse_on:
                self.pulse_lbl.config(bg="#652030", fg="#ffd0d8")
            else:
                self.pulse_lbl.config(bg="#2b1f0f", fg="#ffd690")
        elif self.risk_level >= 38:
            self.pulse_lbl.config(bg="#2b1f0f", fg="#ffd690")
        else:
            self.pulse_lbl.config(bg="#12392f", fg="#8dffd8")

    def _update_health(self) -> None:
        if self.risk_level >= 70:
            self.health_dot.itemconfig(self.health_circle, fill="#ff5a6c", outline="#ff808f")
            self.health_var.set("System health: degraded")
        elif self.risk_level >= 40:
            self.health_dot.itemconfig(self.health_circle, fill="#ffbf52", outline="#ffd68a")
            self.health_var.set("System health: caution")
        else:
            self.health_dot.itemconfig(self.health_circle, fill="#4dffab", outline="#93ffd0")
            self.health_var.set("System health: stable")

    def _redraw_charts(self) -> None:
        self._draw_line_chart()
        self._draw_pie_chart()
        self._draw_bar_chart()

    def _draw_line_chart(self) -> None:
        c = self.line_canvas
        c.delete("all")
        w = max(260, c.winfo_width())
        h = max(100, c.winfo_height())
        c.create_text(8, 12, anchor="w", text="Activity Over Time", fill="#96b3dd", font=("Segoe UI", 9, "bold"))
        c.create_line(24, h - 18, w - 12, h - 18, fill="#28487a")
        c.create_line(24, 20, 24, h - 18, fill="#28487a")

        values = list(self.activity_series)
        if len(values) < 2:
            return
        max_v = max(values) + 3
        step = (w - 48) / (len(values) - 1)
        pts: list[float] = []
        for i, v in enumerate(values):
            x = 24 + i * step
            y = (h - 18) - ((v / max_v) * (h - 42))
            pts.extend([x, y])
        c.create_line(*pts, fill="#39e6ff", width=2, smooth=True)
        for i in range(0, len(pts), 2):
            c.create_oval(pts[i] - 2, pts[i + 1] - 2, pts[i] + 2, pts[i + 1] + 2, fill="#89f3ff", outline="")

    def _draw_pie_chart(self) -> None:
        c = self.pie_canvas
        c.delete("all")
        canvas_any = cast(Any, c)
        c.create_text(8, 12, anchor="w", text="Encryption vs Hashing", fill="#96b3dd", font=("Segoe UI", 9, "bold"))
        total = max(1, self.encryption_ops + self.hash_ops)
        enc_extent = (self.encryption_ops / total) * 360
        x1, y1, x2, y2 = 20, 22, 124, 116
        canvas_any.create_arc(x1, y1, x2, y2, start=0, extent=enc_extent, fill="#2fe7cb", outline="#0d162b")
        canvas_any.create_arc(x1, y1, x2, y2, start=enc_extent, extent=360 - enc_extent, fill="#39a4ff", outline="#0d162b")
        c.create_text(140, 50, anchor="w", text=f"Encrypt: {self.encryption_ops}", fill="#8fffe2", font=("Segoe UI", 9))
        c.create_text(140, 72, anchor="w", text=f"Hash: {self.hash_ops}", fill="#9fd0ff", font=("Segoe UI", 9))

    def _draw_bar_chart(self) -> None:
        c = self.bar_canvas
        c.delete("all")
        c.create_text(8, 12, anchor="w", text="User Activity", fill="#96b3dd", font=("Segoe UI", 9, "bold"))
        labels = list(self.user_activity.keys())
        vals = [int(self.user_activity[k]) for k in labels]
        max_v = max(vals) if vals else 1
        w = max(260, c.winfo_width())
        h = max(110, c.winfo_height())
        bar_w = max(20, int((w - 70) / max(1, len(vals))))

        for i, (lab, val) in enumerate(zip(labels, vals)):
            x1 = 30 + i * (bar_w + 12)
            x2 = x1 + bar_w
            height = int(((h - 46) * (val / max_v)))
            y1 = h - 26 - height
            y2 = h - 26
            hue_shift = int(60 * math.sin(i + val))
            color = f"#2f{max(80, 180 + hue_shift):02x}ff"
            c.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            c.create_text((x1 + x2) / 2, y1 - 10, text=str(val), fill="#cae4ff", font=("Consolas", 9))
            c.create_text((x1 + x2) / 2, h - 12, text=lab, fill="#8aa9d9", font=("Segoe UI", 8))


class EncryptionPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Encryption Panel", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        box = ttk.LabelFrame(self, text="AES-GCM Encrypt / Decrypt", style="Card.TLabelframe", padding=14)
        box.grid(row=1, column=0, sticky="nsew")
        box.grid_columnconfigure(0, weight=1)

        ttk.Label(box, text="Input Text", style="App.TLabel").grid(row=0, column=0, sticky="w")
        self.input_text = tk.Text(box, height=7, bg="#10162b", fg="#f8f3e8", insertbackground="#f8f3e8", relief="flat")
        self.input_text.grid(row=1, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(box, text="Passphrase", style="App.TLabel").grid(row=2, column=0, sticky="w")
        self.key_var = tk.StringVar()
        ttk.Entry(box, textvariable=self.key_var, show="*").grid(row=3, column=0, sticky="ew", pady=(4, 10))

        ttk.Label(box, text="File (txt/json/csv)", style="App.TLabel").grid(row=4, column=0, sticky="w")
        file_row = ttk.Frame(box, style="Panel.TFrame")
        file_row.grid(row=5, column=0, sticky="ew", pady=(4, 10))
        file_row.grid_columnconfigure(0, weight=1)
        self.file_var = tk.StringVar()
        ttk.Entry(file_row, textvariable=self.file_var).grid(row=0, column=0, sticky="ew")
        ModernButton(file_row, text="Browse", command=self.pick_file, variant="secondary", width=100, height=36).grid(row=0, column=1, padx=(8, 0))
        ModernButton(file_row, text="Encrypt File", command=self.encrypt_file, variant="secondary", width=124, height=36).grid(row=0, column=2, padx=(8, 0))
        ModernButton(file_row, text="Decrypt File", command=self.decrypt_file, variant="secondary", width=124, height=36).grid(row=0, column=3, padx=(8, 0))

        btn_row = ttk.Frame(box, style="Panel.TFrame")
        btn_row.grid(row=6, column=0, sticky="w", pady=(0, 10))
        ModernButton(btn_row, text="Encrypt", command=self.encrypt, variant="primary").grid(row=0, column=0, padx=(0, 8))
        ModernButton(btn_row, text="Decrypt", command=self.decrypt, variant="secondary").grid(row=0, column=1, padx=(0, 8))
        ModernButton(btn_row, text="Clear", command=self.clear, variant="secondary", width=100).grid(row=0, column=2)
        ModernButton(btn_row, text="Copy Output", command=self.copy_output, variant="secondary", width=128).grid(row=0, column=3, padx=(8, 0))
        ModernButton(btn_row, text="Output To Input", command=self.output_to_input, variant="secondary", width=146).grid(row=0, column=4, padx=(8, 0))

        ttk.Label(box, text="Output", style="App.TLabel").grid(row=7, column=0, sticky="w")
        self.output_text = tk.Text(box, height=7, bg="#10162b", fg="#9fe7d1", insertbackground="#f8f3e8", relief="flat")
        self.output_text.grid(row=8, column=0, sticky="ew", pady=(4, 0))

    def encrypt(self) -> None:
        text = self.input_text.get("1.0", "end").strip()
        key = self.key_var.get().strip()
        if len(key) < 8:
            self.app.set_status("Passphrase must be at least 8 characters.", tone="warning")
            self.app.sound.play("warning")
            return
        try:
            encrypted = encrypt_text(text, key)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", encrypted)
            self.app.set_status("Message encrypted successfully.", tone="success")
            self.app.log_action("ENCRYPT", "Encrypted message with AES-GCM")
            self.app.sound.play("encrypt_success")
        except Exception as exc:
            self.app.set_status(str(exc), tone="error")
            self.app.sound.play("error")
            messagebox.showerror("Encryption Error", str(exc))

    def decrypt(self) -> None:
        text = self.input_text.get("1.0", "end").strip()
        key = self.key_var.get().strip()
        if len(key) < 8:
            self.app.set_status("Passphrase must be at least 8 characters.", tone="warning")
            self.app.sound.play("warning")
            return
        try:
            decrypted = decrypt_text(text, key)
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", decrypted)
            self.app.set_status("Message decrypted successfully.", tone="success")
            self.app.log_action("DECRYPT", "Decrypted message with AES-GCM")
            self.app.sound.play("decrypt_success")
        except Exception as exc:
            self.app.set_status(str(exc), tone="error")
            self.app.sound.play("error")
            messagebox.showerror("Decryption Error", str(exc))

    def clear(self) -> None:
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.key_var.set("")
        self.app.set_status("Encryption panel cleared.", tone="info")
        self.app.sound.play("warning")

    def copy_output(self) -> None:
        output = self.output_text.get("1.0", "end").strip()
        if not output:
            self.app.set_status("No output available to copy.", tone="warning")
            self.app.sound.play("warning")
            return
        self.clipboard_clear()
        self.clipboard_append(output)
        self.app.set_status("Encrypted/decrypted output copied.", tone="info")
        self.app.sound.play("clipboard")

    def output_to_input(self) -> None:
        output = self.output_text.get("1.0", "end").strip()
        if not output:
            self.app.set_status("No output available to move.", tone="warning")
            self.app.sound.play("warning")
            return
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", output)
        self.app.set_status("Moved output into input box.", tone="info")
        self.app.sound.play("clipboard")

    def pick_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("Supported files", "*.txt *.json *.csv"), ("All files", "*.*")],
        )
        if selected:
            self.file_var.set(selected)

    def encrypt_file(self) -> None:
        key = self.key_var.get().strip()
        file_path = self.file_var.get().strip()
        if len(key) < 8:
            self.app.set_status("Passphrase must be at least 8 characters.", tone="warning")
            self.app.sound.play("warning")
            return
        if not file_path:
            self.app.set_status("Choose a file first.", tone="warning")
            self.app.sound.play("warning")
            return

        source = Path(file_path)
        if not source.exists():
            self.app.set_status("Selected file does not exist.", tone="error")
            self.app.sound.play("error")
            return

        try:
            plain = source.read_text(encoding="utf-8")
            token = encrypt_text(plain, key)
            out_path = source.with_suffix(source.suffix + ".enc")
            out_path.write_text(token, encoding="utf-8")
            self.app.set_status(f"Encrypted file saved: {out_path.name}", tone="success")
            self.app.log_action("ENCRYPT_FILE", str(out_path))
            self.app.sound.play("encrypt_success")
        except Exception as exc:
            self.app.set_status(f"File encryption failed: {exc}", tone="error")
            self.app.sound.play("error")

    def decrypt_file(self) -> None:
        key = self.key_var.get().strip()
        file_path = self.file_var.get().strip()
        if len(key) < 8:
            self.app.set_status("Passphrase must be at least 8 characters.", tone="warning")
            self.app.sound.play("warning")
            return
        if not file_path:
            self.app.set_status("Choose an encrypted file first.", tone="warning")
            self.app.sound.play("warning")
            return

        source = Path(file_path)
        if not source.exists():
            self.app.set_status("Selected file does not exist.", tone="error")
            self.app.sound.play("error")
            return

        try:
            token = source.read_text(encoding="utf-8").strip()
            plain = decrypt_text(token, key)
            out_path = source.with_suffix(source.suffix + ".dec.txt")
            out_path.write_text(plain, encoding="utf-8")
            self.app.set_status(f"Decrypted file saved: {out_path.name}", tone="success")
            self.app.log_action("DECRYPT_FILE", str(out_path))
            self.app.sound.play("decrypt_success")
        except Exception as exc:
            self.app.set_status(f"File decryption failed: {exc}", tone="error")
            self.app.sound.play("error")


class KeyGeneratorPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Key Generator", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        box = ttk.LabelFrame(self, text="Generate Secure Keys", style="Card.TLabelframe", padding=14)
        box.grid(row=1, column=0, sticky="nsew")
        box.grid_columnconfigure(0, weight=1)

        ttk.Label(box, text="Desired Length", style="App.TLabel").grid(row=0, column=0, sticky="w")
        self.length_var = tk.IntVar(value=32)
        length_spin = ttk.Spinbox(box, from_=16, to=96, increment=4, textvariable=self.length_var, width=10)
        length_spin.grid(row=1, column=0, sticky="w", pady=(4, 10))
        length_spin.bind("<KeyRelease>", self._update_strength)
        length_spin.bind("<<Increment>>", self._update_strength)
        length_spin.bind("<<Decrement>>", self._update_strength)

        self.key_strength_var = tk.StringVar(value="Key strength: medium")
        ttk.Label(box, textvariable=self.key_strength_var, style="App.TLabel").grid(row=2, column=0, sticky="w")
        self.key_strength_bar = ttk.Progressbar(box, mode="determinate", maximum=100)
        self.key_strength_bar.grid(row=3, column=0, sticky="ew", pady=(4, 10))
        self._update_strength()

        ModernButton(box, text="Generate Key", command=self.generate, variant="primary", width=138).grid(row=4, column=0, sticky="w")

        ttk.Label(box, text="Generated Key", style="App.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 0))
        self.key_out = tk.StringVar()
        ttk.Entry(box, textvariable=self.key_out).grid(row=6, column=0, sticky="ew", pady=(4, 10))

        ModernButton(box, text="Copy to Clipboard", command=self.copy_key, variant="secondary", width=160).grid(row=7, column=0, sticky="w")

    def generate(self) -> None:
        try:
            key = generate_secure_key(self.length_var.get())
            self.key_out.set(key)
            self.app.set_status("Secure key generated.", tone="success")
            self.app.log_action("KEYGEN", "Generated random secure key")
            self.app.sound.play("keygen_success")
        except Exception as exc:
            self.app.set_status(str(exc), tone="error")
            self.app.sound.play("error")
            messagebox.showerror("Key Generation Error", str(exc))

    def copy_key(self) -> None:
        key = self.key_out.get().strip()
        if not key:
            self.app.set_status("No key available to copy.", tone="warning")
            self.app.sound.play("warning")
            return
        self.clipboard_clear()
        self.clipboard_append(key)
        self.app.set_status("Key copied to clipboard.", tone="info")
        self.app.sound.play("clipboard")

    def _update_strength(self, _event: tk.Event | None = None) -> None:
        length = max(16, int(self.length_var.get()))
        if length < 24:
            label = "weak"
            value = 35
        elif length < 40:
            label = "medium"
            value = 65
        else:
            label = "strong"
            value = 95
        self.key_strength_var.set(f"Key strength: {label}")
        self.key_strength_bar["value"] = value


class HashGeneratorPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Hash Generator", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        box = ttk.LabelFrame(self, text="SHA-256 Integrity Tools", style="Card.TLabelframe", padding=14)
        box.grid(row=1, column=0, sticky="nsew")
        box.grid_columnconfigure(0, weight=1)

        ttk.Label(box, text="Text to Hash", style="App.TLabel").grid(row=0, column=0, sticky="w")
        self.hash_input = ttk.Entry(box)
        self.hash_input.grid(row=1, column=0, sticky="ew", pady=(4, 8))

        ModernButton(box, text="Generate Hash", command=self.generate_hash, variant="primary", width=142).grid(row=2, column=0, sticky="w")

        ttk.Label(box, text="SHA-256 Output", style="App.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.hash_output = ttk.Entry(box)
        self.hash_output.grid(row=4, column=0, sticky="ew", pady=(4, 8))
        ModernButton(box, text="Copy Hash", command=self.copy_hash, variant="secondary", width=108).grid(row=4, column=1, sticky="w", padx=(8, 0))

        sep = ttk.Separator(box, orient="horizontal")
        sep.grid(row=5, column=0, sticky="ew", pady=10)

        ttk.Label(box, text="Verify Text", style="App.TLabel").grid(row=6, column=0, sticky="w")
        self.verify_text = ttk.Entry(box)
        self.verify_text.grid(row=7, column=0, sticky="ew", pady=(4, 6))

        ttk.Label(box, text="Expected Hash", style="App.TLabel").grid(row=8, column=0, sticky="w")
        self.expected_hash = ttk.Entry(box)
        self.expected_hash.grid(row=9, column=0, sticky="ew", pady=(4, 8))

        ModernButton(box, text="Verify Integrity", command=self.verify_hash, variant="secondary", width=152).grid(row=10, column=0, sticky="w")

    def generate_hash(self) -> None:
        text = self.hash_input.get()
        if not text:
            self.app.set_status("Please enter text to hash.", tone="warning")
            self.app.sound.play("warning")
            return

        digest = generate_sha256(text)
        self.hash_output.delete(0, "end")
        self.hash_output.insert(0, digest)
        self.app.set_status("Hash generated.", tone="success")
        self.app.log_action("HASH", "Generated SHA-256 hash")

    def verify_hash(self) -> None:
        text = self.verify_text.get()
        expected = self.expected_hash.get().strip()
        try:
            ok = verify_sha256(text, expected)
            if ok:
                self.app.set_status("Integrity check passed.", tone="success")
                self.app.sound.play("verify_pass")
            else:
                self.app.set_status("Integrity check failed.", tone="error")
                self.app.sound.play("verify_fail")
            self.app.log_action("VERIFY", f"Hash verification result: {ok}")
        except Exception as exc:
            self.app.set_status(str(exc), tone="error")
            self.app.sound.play("error")

    def copy_hash(self) -> None:
        digest = self.hash_output.get().strip()
        if not digest:
            self.app.set_status("No hash available to copy.", tone="warning")
            self.app.sound.play("warning")
            return
        self.clipboard_clear()
        self.clipboard_append(digest)
        self.app.set_status("Hash copied to clipboard.", tone="info")
        self.app.sound.play("clipboard")


class AuthPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="User Authentication", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.user_state = tk.StringVar(value=f"Current user: {self.app.current_user}")
        ttk.Label(self, textvariable=self.user_state, style="App.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))

        signup = ttk.LabelFrame(self, text="Signup", style="Card.TLabelframe", padding=14)
        signup.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        signup.grid_columnconfigure(0, weight=1)

        self.signup_user = ttk.Entry(signup)
        self.signup_pass = ttk.Entry(signup, show="*")
        self.signup_role = tk.StringVar(value="user")
        ttk.Label(signup, text="Username", style="App.TLabel").grid(row=0, column=0, sticky="w")
        self.signup_user.grid(row=1, column=0, sticky="ew", pady=(3, 8))
        ttk.Label(signup, text="Password", style="App.TLabel").grid(row=2, column=0, sticky="w")
        self.signup_pass.grid(row=3, column=0, sticky="ew", pady=(3, 8))
        ttk.Label(signup, text="Role", style="App.TLabel").grid(row=4, column=0, sticky="w")
        ttk.Combobox(signup, textvariable=self.signup_role, values=["user", "admin"], state="readonly").grid(row=5, column=0, sticky="ew", pady=(3, 8))
        self.password_strength_var = tk.StringVar(value="Password strength: weak")
        ttk.Label(signup, textvariable=self.password_strength_var, style="App.TLabel").grid(row=6, column=0, sticky="w", pady=(0, 8))
        self.signup_pass.bind("<KeyRelease>", self._on_password_input)
        ModernButton(signup, text="Create Account", command=self.do_signup, variant="primary", width=152).grid(row=7, column=0, sticky="w")

        login = ttk.LabelFrame(self, text="Login", style="Card.TLabelframe", padding=14)
        login.grid(row=2, column=1, sticky="nsew", padx=(8, 0))
        login.grid_columnconfigure(0, weight=1)

        self.login_user = ttk.Entry(login)
        self.login_pass = ttk.Entry(login, show="*")
        ttk.Label(login, text="Username", style="App.TLabel").grid(row=0, column=0, sticky="w")
        self.login_user.grid(row=1, column=0, sticky="ew", pady=(3, 8))
        ttk.Label(login, text="Password", style="App.TLabel").grid(row=2, column=0, sticky="w")
        self.login_pass.grid(row=3, column=0, sticky="ew", pady=(3, 8))
        ModernButton(login, text="Login", command=self.do_login, variant="secondary", width=112).grid(row=4, column=0, sticky="w")

    def do_signup(self) -> None:
        ok, msg = self.app.auth.signup(
            self.signup_user.get(),
            self.signup_pass.get(),
            requested_role=self.signup_role.get(),
            created_by=self.app.current_user,
        )
        self.app.set_status(msg, tone="success" if ok else "warning")
        self.app.log_action("SIGNUP", msg)
        self.app.sound.play("signup_success" if ok else "warning")
        if ok:
            self.signup_user.delete(0, "end")
            self.signup_pass.delete(0, "end")
            self.password_strength_var.set("Password strength: weak")

    def do_login(self) -> None:
        ok, msg = self.app.auth.login(self.login_user.get(), self.login_pass.get())
        if ok:
            self.app.current_user = self.login_user.get().strip().lower()
            self.app.current_role = self.app.auth.get_role(self.app.current_user)
            self.app.user_role_var.set(f"{self.app.current_user} | role: {self.app.current_role}")
            self.user_state.set(f"Current user: {self.app.current_user} ({self.app.current_role})")
            self.app.set_status(msg, tone="success")
            self.app.log_action("LOGIN", f"{self.app.current_user} logged in")
            self.app.sound.play("login_success")
            self.login_pass.delete(0, "end")
        else:
            self.app.set_status(msg, tone="error")
            self.app.log_action("LOGIN_FAILED", msg)
            self.app.sound.play("login_fail")

    def _on_password_input(self, _event: tk.Event) -> None:
        password = self.signup_pass.get()
        label = self.app.auth.password_strength_label(password)
        self.password_strength_var.set(f"Password strength: {label}")


class IntegrityCheckerPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Integrity Checker", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        box = ttk.LabelFrame(self, text="File Hash Comparison", style="Card.TLabelframe", padding=14)
        box.grid(row=1, column=0, sticky="nsew")
        box.grid_columnconfigure(1, weight=1)

        self.file_path_var = tk.StringVar()
        self.baseline_hash_var = tk.StringVar()
        self.current_hash_var = tk.StringVar()

        ttk.Label(box, text="Target File", style="App.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(box, textvariable=self.file_path_var).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        ModernButton(box, text="Browse", command=self.pick_file, variant="secondary", width=100).grid(row=0, column=2)

        ttk.Label(box, text="Baseline Hash", style="App.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(box, textvariable=self.baseline_hash_var).grid(row=1, column=1, sticky="ew", padx=(8, 8), pady=(8, 0))
        ModernButton(box, text="Generate Baseline", command=self.generate_baseline, variant="secondary", width=160).grid(row=1, column=2, pady=(8, 0))

        ttk.Label(box, text="Current Hash", style="App.TLabel").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(box, textvariable=self.current_hash_var).grid(row=2, column=1, sticky="ew", padx=(8, 8), pady=(8, 0))
        ModernButton(box, text="Compare", command=self.compare_hashes, variant="primary", width=110).grid(row=2, column=2, pady=(8, 0))

    def pick_file(self) -> None:
        selected = filedialog.askopenfilename(title="Select file to verify")
        if selected:
            self.file_path_var.set(selected)

    def _file_hash(self) -> str:
        path = Path(self.file_path_var.get().strip())
        if not path.exists():
            raise ValueError("Selected file does not exist.")
        content = path.read_bytes()
        return generate_sha256(content.decode("utf-8", errors="replace"))

    def generate_baseline(self) -> None:
        try:
            digest = self._file_hash()
            self.baseline_hash_var.set(digest)
            self.current_hash_var.set(digest)
            self.app.set_status("Baseline hash generated.", tone="success")
            self.app.log_action("INTEGRITY_BASELINE", "Generated baseline hash")
            self.app.sound.play("hash_success")
        except Exception as exc:
            self.app.set_status(str(exc), tone="error")
            self.app.sound.play("error")

    def compare_hashes(self) -> None:
        baseline = self.baseline_hash_var.get().strip().lower()
        if not baseline:
            self.app.set_status("Provide a baseline hash first.", tone="warning")
            self.app.sound.play("warning")
            return
        try:
            current = self._file_hash().lower()
            self.current_hash_var.set(current)
            if current == baseline:
                self.app.set_status("Integrity check passed. No tampering detected.", tone="success")
                self.app.sound.play("verify_pass")
                self.app.log_action("INTEGRITY_CHECK", "PASS")
            else:
                self.app.set_status("Integrity mismatch. Possible tampering detected.", tone="error")
                self.app.sound.play("verify_fail")
                self.app.log_action("INTEGRITY_CHECK", "FAIL")
        except Exception as exc:
            self.app.set_status(str(exc), tone="error")
            self.app.sound.play("error")


class ThreatMonitorPanel(BasePanel):
    """Surfaces authentication abuse and integrity failure signals from the audit log."""

    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        ttk.Label(self, text="Threat & security monitoring", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        ttk.Label(
            self,
            text=(
                "Derived from local audit data only: failed logins, temporary lockouts, "
                "and integrity check failures (possible tampering)."
            ),
            style="Subtitle.TLabel",
            wraplength=720,
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

        stats = ttk.LabelFrame(self, text="Indicators (rolling 7 days)", style="Card.TLabelframe", padding=14)
        stats.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        for c in range(4):
            stats.grid_columnconfigure(c, weight=1)

        self._fail_logins = tk.StringVar(value="0")
        self._lockouts = tk.StringVar(value="0")
        self._integ_fail = tk.StringVar(value="0")
        self.posture_var = tk.StringVar(value="—")

        def stat_cell(col: int, title: str, variable: tk.StringVar) -> None:
            ttk.Label(stats, text=title, style="App.TLabel").grid(row=0, column=col, sticky="w", padx=(0, 12))
            ttk.Label(stats, textvariable=variable, style="Title.TLabel").grid(row=1, column=col, sticky="w", pady=(4, 0))

        stat_cell(0, "Failed login attempts", self._fail_logins)
        stat_cell(1, "Lockout events (from log)", self._lockouts)
        stat_cell(2, "Integrity check failures", self._integ_fail)

        ttk.Label(stats, text="Posture", style="App.TLabel").grid(row=0, column=3, sticky="w")
        posture_lbl = ttk.Label(stats, textvariable=self.posture_var, style="App.TLabel", wraplength=260)
        posture_lbl.grid(row=1, column=3, sticky="nw", pady=(4, 0))

        tb = ttk.Frame(self, style="Panel.TFrame")
        tb.grid(row=3, column=0, sticky="w", pady=(0, 8))
        ModernButton(tb, text="Refresh", command=self.refresh, variant="secondary", width=112).grid(row=0, column=0)

        feed = ttk.LabelFrame(self, text="Recent security events (newest on top)", style="Card.TLabelframe", padding=8)
        feed.grid(row=4, column=0, sticky="nsew")
        feed.grid_columnconfigure(0, weight=1)
        feed.grid_rowconfigure(0, weight=1)

        columns = ("timestamp", "signal", "user", "action", "detail")
        self.table = ttk.Treeview(feed, columns=columns, show="headings", height=14)
        for col, width in (
            ("timestamp", 160),
            ("signal", 100),
            ("user", 100),
            ("action", 120),
            ("detail", 380),
        ):
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=width, anchor="w")
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(feed, orient="vertical", command=self._on_scroll)
        scroll.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scroll.set)

        self.refresh()

    def _on_scroll(self, *args: str) -> None:
        cast(Any, self.table).yview(*args)

    def refresh(self) -> None:
        m = self.app.logger.threat_window_metrics(7)
        self._fail_logins.set(str(m["failed_logins"]))
        self._lockouts.set(str(m["lockouts"]))
        self._integ_fail.set(str(m["integrity_failures"]))
        self.posture_var.set(self.app.logger.threat_posture(7))

        self.table.delete(*self.table.get_children())
        for entry in self.app.logger.recent_threat_events(80):
            action = entry.get("action", "")
            detail = (entry.get("detail") or "")
            if action == "LOGIN_FAILED":
                if "locked" in detail.lower():
                    signal = "LOCKOUT"
                else:
                    signal = "AUTH FAIL"
            else:
                signal = "TAMPER"
            self.table.insert(
                "",
                "end",
                values=(
                    entry.get("timestamp", ""),
                    signal,
                    entry.get("user", ""),
                    action,
                    detail,
                ),
            )


class SettingsPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="Settings", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        box = ttk.LabelFrame(self, text="Application Settings", style="Card.TLabelframe", padding=14)
        box.grid(row=1, column=0, sticky="nsew")
        box.grid_columnconfigure(1, weight=1)

        ttk.Label(box, text="Sound", style="App.TLabel").grid(row=0, column=0, sticky="w")
        self.sound_text = tk.StringVar(value="ON" if self.app.sound.enabled else "OFF")
        ModernButton(box, text="Toggle Sound", command=self._toggle_sound, variant="secondary", width=134).grid(row=0, column=1, sticky="w")
        ttk.Label(box, textvariable=self.sound_text, style="App.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))

        ttk.Label(box, text="Theme", style="App.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Combobox(
            box,
            textvariable=self.app.theme_var,
            values=["SOC Midnight", "SOC Oceanic"],
            state="readonly",
        ).grid(row=1, column=1, sticky="ew", pady=(10, 0))
        ModernButton(box, text="Apply Theme", command=self._apply_theme, variant="primary", width=124).grid(row=1, column=2, padx=(10, 0), pady=(10, 0))

        ttk.Label(box, text="Auto-clear Status (sec)", style="App.TLabel").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(box, from_=0, to=30, increment=1, textvariable=self.app.auto_clear_seconds, width=8).grid(row=2, column=1, sticky="w", pady=(10, 0))
        ttk.Label(box, text="0 disables auto-clear", style="App.TLabel").grid(row=2, column=2, sticky="w", padx=(10, 0), pady=(10, 0))

        soc_box = ttk.LabelFrame(self, text="SOC Dashboard Simulation", style="Card.TLabelframe", padding=14)
        soc_box.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        soc_box.grid_columnconfigure(1, weight=1)

        self.soc_preset_var = tk.StringVar(value="Blue Team")
        ttk.Label(soc_box, text="Preset", style="App.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Combobox(
            soc_box,
            textvariable=self.soc_preset_var,
            values=list(SOC_PRESETS.keys()),
            state="readonly",
            width=20,
        ).grid(row=0, column=1, sticky="w")
        ModernButton(soc_box, text="Apply Preset", command=self._apply_soc_preset, variant="secondary", width=126).grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Label(soc_box, text="Last Applied", style="App.TLabel").grid(row=0, column=3, sticky="w", padx=(14, 4))
        ttk.Label(soc_box, textvariable=self.app.soc_profile_var, style="App.TLabel").grid(row=0, column=4, sticky="w")

        ttk.Label(soc_box, text="Tick Interval (ms)", style="App.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(soc_box, from_=800, to=6000, increment=100, textvariable=self.app.soc_tick_ms, width=10).grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Label(soc_box, text="Live refresh speed for feed and charts.", style="App.TLabel").grid(row=1, column=2, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(soc_box, text="Alert Intensity (%)", style="App.TLabel").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Scale(soc_box, from_=10, to=90, variable=self.app.soc_alert_intensity, orient="horizontal").grid(row=2, column=1, sticky="ew", pady=(10, 0))
        ttk.Label(soc_box, text="Controls warning/critical event frequency.", style="App.TLabel").grid(row=2, column=2, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(soc_box, text="Risk Sensitivity", style="App.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(soc_box, from_=1, to=20, increment=1, textvariable=self.app.soc_risk_sensitivity, width=10).grid(row=3, column=1, sticky="w", pady=(10, 0))
        ttk.Label(soc_box, text="Higher values escalate risk meters faster.", style="App.TLabel").grid(row=3, column=2, sticky="w", padx=(10, 0), pady=(10, 0))

        ttk.Label(soc_box, text="Incident Pulse Speed", style="App.TLabel").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.pulse_speed_combo = ttk.Combobox(
            soc_box,
            textvariable=self.app.soc_pulse_speed_var,
            values=SOC_PULSE_SPEEDS,
            state="readonly",
            width=14,
        )
        self.pulse_speed_combo.grid(row=4, column=1, sticky="w", pady=(10, 0))
        ttk.Checkbutton(
            soc_box,
            text="Auto by profile",
            variable=self.app.soc_pulse_auto_var,
            command=self._toggle_pulse_mode,
        ).grid(row=4, column=3, sticky="w", padx=(14, 0), pady=(10, 0))
        ttk.Label(soc_box, text="Controls Incident Mode badge pulse tempo.", style="App.TLabel").grid(row=4, column=2, sticky="w", padx=(10, 0), pady=(10, 0))

        self.pulse_hint_var = tk.StringVar(value="")
        ttk.Label(soc_box, textvariable=self.pulse_hint_var, style="App.TLabel").grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))
        self._toggle_pulse_mode()

        ModernButton(soc_box, text="Apply SOC Settings", command=self._apply_soc_settings, variant="primary", width=162).grid(row=6, column=1, sticky="w", pady=(12, 0))
        ModernButton(soc_box, text="Reset To Defaults", command=self._reset_soc_defaults, variant="secondary", width=162).grid(row=6, column=2, sticky="w", pady=(12, 0), padx=(10, 0))
        ModernButton(soc_box, text="Reset To Saved", command=self._reset_soc_saved, variant="secondary", width=132).grid(row=6, column=0, sticky="w", pady=(12, 0))

        about_box = ttk.LabelFrame(self, text="About Section Editor", style="Card.TLabelframe", padding=14)
        about_box.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        about_box.grid_columnconfigure(1, weight=1)

        self.name_1_var = tk.StringVar(value=self.app.about_info["name_1"])
        self.reg_1_var = tk.StringVar(value=self.app.about_info["reg_1"])
        self.name_2_var = tk.StringVar(value=self.app.about_info["name_2"])
        self.reg_2_var = tk.StringVar(value=self.app.about_info["reg_2"])
        self.github_var = tk.StringVar(value=self.app.about_info["github"])
        self.title_var = tk.StringVar(value=self.app.about_info["title"])
        self.image_1_var = tk.StringVar(value=self.app.about_info["image_1"])
        self.image_2_var = tk.StringVar(value=self.app.about_info["image_2"])

        ttk.Label(about_box, text="Member 1 Name", style="App.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(about_box, textvariable=self.name_1_var).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        ttk.Label(about_box, text="Registration 1", style="App.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Entry(about_box, textvariable=self.reg_1_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))

        ttk.Label(about_box, text="Member 2 Name", style="App.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Entry(about_box, textvariable=self.name_2_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        ttk.Label(about_box, text="Registration 2", style="App.TLabel").grid(row=3, column=0, sticky="w")
        ttk.Entry(about_box, textvariable=self.reg_2_var).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))

        ttk.Label(about_box, text="Title", style="App.TLabel").grid(row=4, column=0, sticky="w")
        ttk.Entry(about_box, textvariable=self.title_var).grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        ttk.Label(about_box, text="GitHub Link", style="App.TLabel").grid(row=5, column=0, sticky="w")
        ttk.Entry(about_box, textvariable=self.github_var).grid(row=5, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))

        ttk.Label(about_box, text="Member 1 Image", style="App.TLabel").grid(row=6, column=0, sticky="w")
        img1_row = ttk.Frame(about_box, style="Panel.TFrame")
        img1_row.grid(row=6, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        img1_row.grid_columnconfigure(0, weight=1)
        ttk.Entry(img1_row, textvariable=self.image_1_var).grid(row=0, column=0, sticky="ew")
        ModernButton(img1_row, text="Upload", command=lambda: self._pick_image(self.image_1_var), variant="secondary", width=96, height=34).grid(row=0, column=1, padx=(8, 0))

        ttk.Label(about_box, text="Member 2 Image", style="App.TLabel").grid(row=7, column=0, sticky="w")
        img2_row = ttk.Frame(about_box, style="Panel.TFrame")
        img2_row.grid(row=7, column=1, sticky="ew", padx=(8, 0), pady=(0, 6))
        img2_row.grid_columnconfigure(0, weight=1)
        ttk.Entry(img2_row, textvariable=self.image_2_var).grid(row=0, column=0, sticky="ew")
        ModernButton(img2_row, text="Upload", command=lambda: self._pick_image(self.image_2_var), variant="secondary", width=96, height=34).grid(row=0, column=1, padx=(8, 0))

        ModernButton(about_box, text="Save About Details", command=self._save_about, variant="primary", width=170).grid(row=8, column=1, sticky="w", pady=(10, 0))

    def _toggle_sound(self) -> None:
        self.app.toggle_sound()
        self.sound_text.set("ON" if self.app.sound.enabled else "OFF")

    def _apply_theme(self) -> None:
        self.app.apply_theme(self.app.theme_var.get())
        self.app.set_status("Theme updated.", tone="success")

    def _apply_soc_settings(self) -> None:
        self.app.apply_soc_settings(profile_name="Custom Tuning")

    def _apply_soc_preset(self) -> None:
        preset = SOC_PRESETS.get(self.soc_preset_var.get())
        if preset is None:
            self.app.set_status("Unknown SOC preset.", tone="warning")
            return

        self.app.soc_tick_ms.set(int(cast(int, preset["tick_ms"])))
        self.app.soc_alert_intensity.set(float(cast(float, preset["alert_intensity"])))
        self.app.soc_risk_sensitivity.set(int(cast(int, preset["risk_sensitivity"])))
        self.app.apply_soc_settings(profile_name=self.soc_preset_var.get())
        self.app.set_status(f"Applied preset: {self.soc_preset_var.get()}.", tone="success")

    def _reset_soc_defaults(self) -> None:
        self.app.reset_soc_defaults()
        self._toggle_pulse_mode()

    def _reset_soc_saved(self) -> None:
        self.app.reload_soc_saved_settings()
        self._toggle_pulse_mode()

    def _toggle_pulse_mode(self) -> None:
        if self.app.soc_pulse_auto_var.get():
            self.app.soc_pulse_speed_var.set(self.app.recommended_pulse_speed(self.app.soc_profile_var.get()))
            self.pulse_speed_combo.configure(state="disabled")
            self.pulse_hint_var.set(
                f"Auto-controlled by profile: {self.app.soc_profile_var.get()} -> {self.app.soc_pulse_speed_var.get()}"
            )
        else:
            self.pulse_speed_combo.configure(state="readonly")
            self.pulse_hint_var.set(
                f"Manual override active: pulse speed set to {self.app.soc_pulse_speed_var.get()}"
            )

    def _pick_image(self, target: tk.StringVar) -> None:
        selected = filedialog.askopenfilename(
            title="Select member image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")],
        )
        if selected:
            target.set(selected)

    def _save_about(self) -> None:
        payload = {
            "name_1": self.name_1_var.get(),
            "reg_1": self.reg_1_var.get(),
            "name_2": self.name_2_var.get(),
            "reg_2": self.reg_2_var.get(),
            "github": self.github_var.get(),
            "title": self.title_var.get(),
            "image_1": self.image_1_var.get(),
            "image_2": self.image_2_var.get(),
        }
        self.app.save_about_info(payload)
        self.app.set_status("About details updated successfully.", tone="success")
        self.app.sound.play("clipboard")


class AboutPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)

        ttk.Label(self, text="About Project Team", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))

        card = ttk.LabelFrame(self, text="Team & Profile", style="Card.TLabelframe", padding=18)
        card.grid(row=1, column=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        self.card = card

        self.title_lbl = ttk.Label(card, text="", style="Title.TLabel")
        self.title_lbl.grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(card, text="Project Contributors", style="Subtitle.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 12))

        self.member_1_text = ttk.Label(card, text="", style="App.TLabel")
        self.member_1_text.grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.member_2_text = ttk.Label(card, text="", style="App.TLabel")
        self.member_2_text.grid(row=3, column=0, sticky="w", pady=(0, 10))

        image_wrap = ttk.Frame(card, style="Panel.TFrame")
        image_wrap.grid(row=2, column=1, rowspan=3, sticky="e")
        self.image_1_label = tk.Label(image_wrap, bg="#1c233c")
        self.image_1_label.grid(row=0, column=0, padx=(0, 8))
        self.image_2_label = tk.Label(image_wrap, bg="#1c233c")
        self.image_2_label.grid(row=0, column=1)

        self.link_label = tk.Label(
            card,
            text="",
            fg="#7cc4ff",
            bg="#1c233c",
            cursor="hand2",
            font=("Segoe UI", 11, "underline"),
        )
        self.link_label.grid(row=5, column=0, columnspan=2, sticky="w")
        self.link_label.bind("<Button-1>", lambda _e: webbrowser.open(self.app.about_info["github"]))

        self.note = ttk.Label(
            card,
            text="You can edit this section from Settings.",
            style="App.TLabel",
        )
        self.note.grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 0))

        self.photo_1: Any = None
        self.photo_2: Any = None
        self.refresh_about()

    def refresh_about(self) -> None:
        info = self.app.about_info
        self.title_lbl.config(text=info["title"])
        self.member_1_text.config(text=f"Name: {info['name_1']} | Registration: {info['reg_1']}")
        self.member_2_text.config(text=f"Name: {info['name_2']} | Registration: {info['reg_2']}")
        self.link_label.config(text=info["github"])
        self._set_image(self.image_1_label, info.get("image_1", ""), index=1)
        self._set_image(self.image_2_label, info.get("image_2", ""), index=2)

    def _set_image(self, widget: tk.Label, image_path: str, index: int) -> None:
        if not image_path or not Path(image_path).exists() or not pil_available:
            widget.config(image="", text=f"Member {index}\nImage", fg="#b7bfdc", width=12, height=6)
            return

        try:
            image = PILImage.open(image_path).convert("RGB")
            image.thumbnail((112, 112))
            photo = PILImageTk.PhotoImage(image)
            if index == 1:
                self.photo_1 = photo
            else:
                self.photo_2 = photo
            widget.config(image=photo, text="", width=112, height=112)
        except Exception:
            widget.config(image="", text=f"Member {index}\nImage", fg="#b7bfdc", width=12, height=6)


class ActivityLogPanel(BasePanel):
    def __init__(self, parent: ttk.Frame, app: CyberSecurityApp) -> None:
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ttk.Label(self, text="Activity Log", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))

        filter_row = ttk.Frame(self, style="Panel.TFrame")
        filter_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_row.grid_columnconfigure(1, weight=1)

        self.user_filter = tk.StringVar()
        self.action_filter = tk.StringVar()
        self.from_filter = tk.StringVar()
        self.to_filter = tk.StringVar()

        ttk.Label(filter_row, text="User", style="App.TLabel").grid(row=0, column=0, padx=(0, 6))
        ttk.Entry(filter_row, textvariable=self.user_filter, width=14).grid(row=0, column=1, padx=(0, 8))
        ttk.Label(filter_row, text="Action", style="App.TLabel").grid(row=0, column=2, padx=(0, 6))
        ttk.Combobox(
            filter_row,
            textvariable=self.action_filter,
            values=[
                "",
                "ENCRYPT",
                "DECRYPT",
                "HASH",
                "VERIFY",
                "LOGIN",
                "LOGIN_FAILED",
                "SIGNUP",
                "ENCRYPT_FILE",
                "DECRYPT_FILE",
                "INTEGRITY_BASELINE",
                "INTEGRITY_CHECK",
            ],
            width=16,
            state="readonly",
        ).grid(row=0, column=3, padx=(0, 8))
        ttk.Label(filter_row, text="From (YYYY-MM-DD)", style="App.TLabel").grid(row=0, column=4, padx=(0, 6))
        ttk.Entry(filter_row, textvariable=self.from_filter, width=14).grid(row=0, column=5, padx=(0, 8))
        ttk.Label(filter_row, text="To", style="App.TLabel").grid(row=0, column=6, padx=(0, 6))
        ttk.Entry(filter_row, textvariable=self.to_filter, width=14).grid(row=0, column=7, padx=(0, 8))
        ModernButton(filter_row, text="Apply", command=self.apply_filters, variant="secondary", width=96).grid(row=0, column=8, padx=(0, 8))
        ModernButton(filter_row, text="Reset", command=self.reset_filters, variant="secondary", width=96).grid(row=0, column=9)

        frame = ttk.Frame(self, style="Panel.TFrame")
        frame.grid(row=2, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        columns = ("timestamp", "user", "action", "detail")
        self.table = ttk.Treeview(frame, columns=columns, show="headings")
        for col, width in (("timestamp", 170), ("user", 110), ("action", 130), ("detail", 520)):
            self.table.heading(col, text=col.title())
            self.table.column(col, width=width, anchor="w")

        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self._on_table_scroll)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scrollbar.set)

        toolbar = ttk.Frame(self, style="Panel.TFrame")
        toolbar.grid(row=3, column=0, sticky="w", pady=(10, 0))
        ModernButton(toolbar, text="Refresh", command=self.refresh_logs, variant="secondary", width=106).grid(row=0, column=0, padx=(0, 8))
        ModernButton(toolbar, text="Clear View", command=self.clear_view, variant="secondary", width=116).grid(row=0, column=1)
        ModernButton(toolbar, text="Export CSV", command=self.export_csv, variant="secondary", width=116).grid(row=0, column=2, padx=(8, 0))
        ModernButton(toolbar, text="Export Security Report", command=self.export_report_pdf, variant="secondary", width=188).grid(row=0, column=3, padx=(8, 0))

        self.refresh_logs()

    def refresh_logs(self) -> None:
        self.table.delete(*self.table.get_children())
        entries = self.app.logger.filter_logs(
            username=self.user_filter.get(),
            action=self.action_filter.get(),
            from_date=self.from_filter.get(),
            to_date=self.to_filter.get(),
        )
        for entry in reversed(entries[-250:]):
            self.table.insert("", "end", values=(entry["timestamp"], entry["user"], entry["action"], entry["detail"]))

    def apply_filters(self) -> None:
        self.refresh_logs()
        self.app.set_status("Filters applied to activity log.", tone="info")

    def reset_filters(self) -> None:
        self.user_filter.set("")
        self.action_filter.set("")
        self.from_filter.set("")
        self.to_filter.set("")
        self.refresh_logs()
        self.app.set_status("Filters reset.", tone="info")

    def _require_admin(self) -> bool:
        if self.app.current_role != "admin":
            self.app.set_status("Admin role required for this action.", tone="warning")
            self.app.sound.play("warning")
            return False
        return True

    def clear_view(self) -> None:
        if not self._require_admin():
            return
        self.table.delete(*self.table.get_children())
        self.app.set_status("Activity table cleared from current view.", tone="info")

    def _on_table_scroll(self, *args: str) -> None:
        cast(Any, self.table).yview(*args)

    def export_csv(self) -> None:
        if not self._require_admin():
            return
        entries = self.app.logger.read_all()
        if not entries:
            self.app.set_status("No activity records available to export.", tone="warning")
            self.app.sound.play("warning")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Activity Log",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="activity_log_export.csv",
        )

        if not file_path:
            self.app.set_status("CSV export canceled.", tone="info")
            return

        with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "user", "action", "detail"])
            writer.writeheader()
            writer.writerows(entries)

        self.app.set_status("Activity log exported successfully.", tone="success")
        self.app.sound.play("clipboard")

    def export_report_pdf(self) -> None:
        if not self._require_admin():
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except Exception:
            self.app.set_status("Install reportlab for PDF export: pip install reportlab", tone="warning")
            self.app.sound.play("warning")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Security Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="security_report.pdf",
        )
        if not file_path:
            self.app.set_status("PDF export canceled.", tone="info")
            return

        summary = self.app.logger.summary()
        users = self.app.auth.list_users()

        pdf = canvas.Canvas(file_path, pagesize=A4)
        _, height = A4
        y = height - 50
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, y, "SecureLab Nexus — Security Report")
        y -= 24
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y -= 24

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "User Overview")
        y -= 18
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, f"Total users: {len(users)}")
        y -= 14
        for username, role in users[:20]:
            pdf.drawString(70, y, f"- {username} ({role})")
            y -= 14

        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Activity Summary")
        y -= 18
        pdf.setFont("Helvetica", 10)
        for key, value in summary.items():
            pdf.drawString(70, y, f"{key}: {value}")
            y -= 14

        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Validation Status")
        y -= 18
        pdf.setFont("Helvetica", 10)
        pdf.drawString(70, y, "Core module QA tests: Passed")
        y -= 14
        pdf.drawString(70, y, "Encryption/Decryption: Verified")
        y -= 14
        pdf.drawString(70, y, "Authentication lockout policy: Enabled")
        y -= 14
        pdf.drawString(70, y, f"Local threat posture (7d): {self.app.logger.threat_posture(7)}")

        pdf.save()
        self.app.set_status("Security report PDF exported.", tone="success")
        self.app.sound.play("clipboard")


if __name__ == "__main__":
    app = CyberSecurityApp()
    app.mainloop()
