import os
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict

from PIL import Image, ImageTk

from app.controller import ToDoController
from app.gui.sidebar import Sidebar
from app.gui.task_area import TaskArea
from app.themes import THEMES

ICON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "resources", "icons"
)


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
        self.setup_style()
        self.build_gui()

    def load_icons(self) -> Dict[str, Any]:
        icons: Dict[str, Any] = {}
        for name in ["add", "delete", "category", "theme"]:
            path = os.path.join(ICON_PATH, f"{name}.png")
            if os.path.exists(path):
                img = Image.open(path).resize((20, 20))
                icons[name] = ImageTk.PhotoImage(img)
            else:
                icons[name] = None
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
            font=("Segoe UI", 11),
        )
        style.configure(
            "Sidebar.TLabel",
            background=self.theme["sidebar"],
            foreground=self.theme["fg"],
            font=("Segoe UI", 13, "bold"),
        )
        style.configure(
            "Accent.TButton",
            background=self.theme["button"],
            foreground=self.theme["button_fg"],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map(
            "Accent.TButton", background=[("active", self.theme["accent"])]
        )
        style.configure(
            "TEntry",
            fieldbackground=self.theme["entry_bg"],
            foreground=self.theme["entry_fg"],
        )

    def build_gui(self) -> None:
        self.root.configure(bg=self.theme["bg"])
        self.root.title("To-Do List")
        self.root.geometry("900x600")
        self.root.minsize(700, 400)
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
        self.sidebar.grid(row=0, column=0, sticky="nswe")

        self.main = ttk.Frame(self.root, style="Main.TFrame")
        self.main.grid(row=0, column=1, sticky="nswe")
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
        self.sidebar.refresh()

    def refresh_tasks(self) -> None:
        tasks = self.controller.get_tasks_by_category(self.selected_category)
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
