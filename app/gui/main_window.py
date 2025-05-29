import os
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict

from PIL import Image, ImageTk

from app.controller import ToDoController
from app.gui.sidebar import Sidebar
from app.gui.task_area import TaskArea
from app.themes import THEMES

class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root: tk.Tk = root
        self.theme_name: str = "dark"
        self.theme: Dict[str, Any] = THEMES[self.theme_name]
        self.controller: ToDoController = ToDoController()
        self.selected_category: str = "All"
        self.icons: Dict[str, Any] = self.load_icons()
        self.sidebar: Sidebar
        self.main: ttk.Frame
        self.task_area: TaskArea
        self.status_bar: ttk.Label
        self.setup_style()
        self.build_gui()
        self.fade_in()

    def load_icons(self) -> Dict[str, Any]:
        icons: Dict[str, Any] = {}
        for name in ["add", "delete", "category", "theme"]:
            icons[name] = None  # No icon loading for now
        return icons

    def setup_style(self) -> None:
        style: ttk.Style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Sidebar.TFrame", background=self.theme["sidebar"])
        style.configure("Main.TFrame", background=self.theme["bg"])
        style.configure(
            "TLabel",
            background=self.theme["bg"],
            foreground=self.theme["fg"],
            font=("Segoe UI Variable", 12),
            padding=4,
        )
        style.configure(
            "Sidebar.TLabel",
            background=self.theme["sidebar"],
            foreground=self.theme["fg"],
            font=("Segoe UI Variable", 14, "bold"),
            padding=6,
        )
        style.configure(
            "Accent.TButton",
            background=self.theme["button"],
            foreground=self.theme["button_fg"],
            font=("Segoe UI Variable", 11, "bold"),
            borderwidth=0,
            padding=6,
        )
        style.map(
            "Accent.TButton", background=[("active", self.theme["accent"])]
        )
        style.configure(
            "TEntry",
            fieldbackground=self.theme["entry_bg"],
            foreground=self.theme["entry_fg"],
            font=("Segoe UI Variable", 11),
            padding=4,
        )
        style.configure(
            "Statusbar.TLabel",
            background=self.theme["sidebar"],
            foreground=self.theme["fg"],
            font=("Segoe UI Variable", 10),
            anchor="w",
            padding=4,
        )
        # --- Dialog styles ---
        style.configure("Dialog.TFrame", background="#23272e")
        style.configure(
            "DialogHeader.TLabel", background="#23272e", foreground="#fff"
        )
        style.configure(
            "Dialog.TButton",
            background="#444",
            foreground="#fff",
            font=("Segoe UI Variable", 10),
            borderwidth=0,
            padding=6,
        )
        style.configure(
            "Accent.TButton",
            background="#3b82f6",
            foreground="#fff",
            font=("Segoe UI Variable", 10, "bold"),
            borderwidth=0,
            padding=6,
        )
        style.map("Accent.TButton", background=[("active", "#2563eb")])

    def build_gui(self) -> None:
        self.root.configure(bg=self.theme["bg"])
        self.root.title("To-Do List")
        self.root.geometry("950x650")
        self.root.minsize(750, 450)
        self.root.resizable(True, True)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(
            self.root,
            self.controller,
            self.icons,
            self.theme,
            self.select_category,
            self.refresh_categories,
            self.switch_theme,
        )
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=(0, 2), pady=2)

        self.main = ttk.Frame(self.root, style="Main.TFrame", padding=10)
        self.main.grid(row=0, column=1, sticky="nswe", padx=(2, 0), pady=2)
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.task_area = TaskArea(
            self.main,
            self.controller,
            self.icons,
            self.theme,
            self.get_selected_category,
            self.refresh_tasks,
        )
        self.task_area.grid(row=0, column=0, sticky="nsew")

        self.refresh_categories()
        self.refresh_tasks()
        self.root.title("To-Do List - All")

    def select_category(self, category: str) -> None:
        self.selected_category = category
        self.refresh_tasks()
        self.root.title(f"To-Do List - {category}")

    def get_selected_category(self) -> str:
        return self.selected_category

    def refresh_categories(self) -> None:
        self.sidebar.theme = self.theme
        self.sidebar.refresh()

    def refresh_tasks(self) -> None:
        tasks = self.controller.get_tasks_by_category(self.selected_category)
        self.task_area.theme = self.theme
        self.task_area.refresh(tasks)

    def switch_theme(self) -> None:
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.theme = THEMES[self.theme_name]
        self.setup_style()
        self.root.configure(bg=self.theme["bg"])
        self.sidebar.theme = self.theme
        self.task_area.theme = self.theme
        self.refresh_categories()
        self.refresh_tasks()

    def fade_in(self) -> None:
        self.root.attributes("-alpha", 0.0)
        def _fade(step=0):
            alpha = min(1.0, step / 10)
            self.root.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.root.after(30, _fade, step + 1)
        _fade()