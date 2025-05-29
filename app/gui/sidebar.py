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
        self.selected_category = "All"
        self.cat_frame: ttk.Frame
        self.add_cat_btn: ttk.Button
        self.category_buttons: dict[str, ttk.Button] = {}
        self.build()

    def build(self) -> None:
        # Title
        ttk.Label(
            self,
            text="Categories",
            style="Sidebar.TLabel",
            anchor="center"
        ).pack(pady=(24, 12), padx=8, fill=tk.X)

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, padx=8, pady=(0, 8))

        # Category list frame
        self.cat_frame = ttk.Frame(self, style="Sidebar.TFrame")
        self.cat_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        # Add Category button
        self.add_cat_btn = ttk.Button(
            self,
            text="Add Category",
            image=self.icons["add"],
            compound=tk.LEFT,
            style="Accent.TButton",
            command=self.add_category_dialog,
            cursor="hand2"
        )
        self.add_cat_btn.pack(side=tk.BOTTOM, pady=(6, 6), padx=12, fill=tk.X)

        # Switch Theme button
        self.theme_btn = ttk.Button(
            self,
            text="Switch Theme",
            image=self.icons["theme"],
            compound=tk.LEFT,
            style="Accent.TButton",
            command=self.switch_theme,
            cursor="hand2"
        )
        self.theme_btn.pack(side=tk.BOTTOM, pady=(0, 18), padx=12, fill=tk.X)

        self.refresh()

    def refresh(self) -> None:
        for widget in self.cat_frame.winfo_children():
            widget.destroy()
        self.category_buttons.clear()
        for cat in self.controller.categories:
            btn = ttk.Button(
                self.cat_frame,
                text=cat.name,
                image=self.icons["category"],
                compound=tk.LEFT,
                style="Accent.TButton" if cat.name != self.selected_category else "SelectedCategory.TButton",
                command=lambda c=cat.name: self.on_category_click(c),
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=3, ipady=2)
            self.category_buttons[cat.name] = btn
            if cat.name != "All":
                btn.bind(
                    "<Button-3>",
                    lambda e, c=cat.name: self.show_context_menu(e, c),
                )
                btn.bind(
                    "<Button-2>",
                    lambda e, c=cat.name: self.show_context_menu(e, c),
                )  # For macOS

        # Custom style for selected category
        style = ttk.Style(self)
        style.configure(
            "SelectedCategory.TButton",
            background=self.theme["accent"],
            foreground=self.theme["button_fg"],
            font=("Segoe UI Variable", 11, "bold"),
            borderwidth=0,
            relief="flat",
            padding=6,
        )
        style.map(
            "SelectedCategory.TButton",
            background=[("active", self.theme["accent"])],
            foreground=[("active", self.theme["button_fg"])]
        )

    def on_category_click(self, category: str) -> None:
        self.selected_category = category
        self.select_category(category)
        self.refresh()  # Update highlight

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
        from app.gui.add_category_dialog import AddCategoryDialog

        dialog = AddCategoryDialog(self)
        self.wait_window(dialog)
        name = dialog.result
        if name:
            if self.controller.add_category(name):
                self.refresh_categories()
            else:
                messagebox.showwarning(
                    "Category Error",
                    "Category already exists or name is invalid.",
                )

    def delete_category(self, name: str) -> None:
        if messagebox.askyesno(
            "Delete Category", f"Delete category '{name}' and its tasks?"
        ):
            self.controller.delete_category(name)
            self.refresh_categories()