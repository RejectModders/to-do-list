import tkinter as tk
from tkinter import ttk
from typing import Any

class AddCategoryDialog(tk.Toplevel):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        self.title("Add Category")
        self.result: str | None = None
        self.grab_set()
        self.resizable(False, False)
        self.configure(bg="#23272e")

        # Main frame for padding and background
        main = ttk.Frame(self, padding=18, style="Dialog.TFrame")
        main.pack(fill=tk.BOTH, expand=True)

        # Section header
        header = ttk.Label(
            main,
            text="Add New Category",
            font=("Segoe UI Variable", 13, "bold"),
            anchor="w",
            style="DialogHeader.TLabel"
        )
        header.pack(anchor="w", pady=(0, 2))

        # Subtle separator
        ttk.Separator(main, orient="horizontal").pack(fill=tk.X, pady=(0, 10))

        # Category name entry
        ttk.Label(
            main,
            text="Category Name:",
            font=("Segoe UI Variable", 11, "bold"),
            anchor="w",
            style="DialogHeader.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        self.name_var = tk.StringVar()
        entry = ttk.Entry(main, textvariable=self.name_var, font=("Segoe UI Variable", 11))
        entry.pack(fill=tk.X, pady=(0, 12))
        entry.focus_set()
        self._add_tooltip(entry, "Enter the new category name")

        # Button row
        btns = ttk.Frame(main, style="Dialog.TFrame")
        btns.pack(pady=(8, 0), fill=tk.X)

        ok_btn = ttk.Button(
            btns, text="OK", command=self.on_ok, style="Accent.TButton", cursor="hand2"
        )
        ok_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._add_tooltip(ok_btn, "Add category")

        cancel_btn = ttk.Button(
            btns, text="Cancel", command=self.destroy, style="Dialog.TButton", cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT)
        self._add_tooltip(cancel_btn, "Cancel and close")

        # Keyboard navigation
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.destroy())

    def on_ok(self) -> None:
        name = self.name_var.get().strip()
        if name:
            self.result = name
            self.destroy()

    def _add_tooltip(self, widget, text):
        def on_enter(_):
            self._show_tooltip(widget, text)
        def on_leave(_):
            self._hide_tooltip()
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _show_tooltip(self, widget, text):
        x, y, _, _ = widget.bbox("insert") if hasattr(widget, "bbox") else (0, 0, 0, 0)
        x += widget.winfo_rootx() + 30
        y += widget.winfo_rooty() + 20
        self._tooltip = tk.Toplevel(widget)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self._tooltip,
            text=text,
            background="#222",
            foreground="#fff",
            borderwidth=1,
            relief="solid",
            font=("Segoe UI Variable", 9),
            padx=6,
            pady=2,
        )
        label.pack()

    def _hide_tooltip(self):
        if hasattr(self, "_tooltip") and self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None