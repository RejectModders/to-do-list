import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable


class Sidebar(ttk.Frame):
    def __init__(
        self,
        parent: Any,
        controller: Any,
        icons: dict[str, Any],
        theme: dict[str, Any],
        select_category: Callable[[str], None],
        refresh_categories: Callable[[], None],
        switch_theme: Callable[[], None],
    ) -> None:
        super().__init__(parent, style="Sidebar.TFrame")
        self.controller = controller
        self.icons = icons
        self.theme = theme
        self.select_category = select_category
        self.refresh_categories = refresh_categories
        self.switch_theme = switch_theme
        self.cat_frame: ttk.Frame
        self.add_cat_btn: ttk.Button
        self.build()

    def build(self) -> None:
        ttk.Label(self, text="Categories", style="Sidebar.TLabel").pack(
            pady=(20, 10)
        )
        self.cat_frame = ttk.Frame(self, style="Sidebar.TFrame")
        self.cat_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        self.add_cat_btn = ttk.Button(
            self,
            text="Add Category",
            image=self.icons["add"],
            compound=tk.LEFT,
            style="Accent.TButton",
            command=self.add_category_dialog,
        )
        self.add_cat_btn.pack(side=tk.BOTTOM, pady=(5, 5), padx=10, fill=tk.X)

        # Add Switch Theme button at the very bottom
        self.theme_btn = ttk.Button(
            self,
            text="Switch Theme",
            image=self.icons["theme"],
            compound=tk.LEFT,
            style="Accent.TButton",
            command=self.switch_theme,
        )
        self.theme_btn.pack(side=tk.BOTTOM, pady=(0, 15), padx=10, fill=tk.X)

        self.refresh()

    def refresh(self) -> None:
        for widget in self.cat_frame.winfo_children():
            widget.destroy()
        for cat in self.controller.categories:
            btn = ttk.Button(
                self.cat_frame,
                text=cat.name,
                image=self.icons["category"],
                compound=tk.LEFT,
                style="Accent.TButton",
                command=lambda c=cat.name: self.select_category(c),
            )
            btn.pack(fill=tk.X, pady=4)
            if cat.name != "All":
                btn.bind(
                    "<Button-3>",
                    lambda e, c=cat.name: self.show_context_menu(e, c),
                )
                btn.bind(
                    "<Button-2>",
                    lambda e, c=cat.name: self.show_context_menu(e, c),
                )  # For macOS

    def show_context_menu(self, event: tk.Event, category_name: str) -> None:
        menu: tk.Menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Delete", command=lambda: self.delete_category(category_name)
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def add_category_dialog(self) -> None:
        from tkinter import simpledialog

        name: str | None = simpledialog.askstring(
            "New Category", "Enter category name:", parent=self
        )
        if name:
            if self.controller.add_category(name):
                self.refresh_categories()
            else:
                messagebox.showwarning(  # type: ignore
                    "Category Error",
                    "Category already exists or name is invalid.",
                )

    def delete_category(self, name: str) -> None:
        if messagebox.askyesno(  # type: ignore
            "Delete Category", f"Delete category '{name}' and its tasks?"
        ):
            self.controller.delete_category(name)
            self.refresh_categories()
