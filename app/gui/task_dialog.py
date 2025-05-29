import tkinter as tk
from tkinter import ttk
from typing import Any

class TaskDialog(tk.Toplevel):
    def __init__(
        self,
        parent: Any,
        title: str = "",
        custom_fields: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(parent)
        self.title("Task Details")
        self.result: dict[str, Any] | None = None
        self.grab_set()
        self.resizable(False, False)
        self.configure(bg="#23272e")
        self.custom_fields: dict[str, Any] = (
            custom_fields.copy() if custom_fields else {}
        )

        # Main frame for padding and background
        main = ttk.Frame(self, padding=18, style="Dialog.TFrame")
        main.pack(fill=tk.BOTH, expand=True)

        # Section header
        header = ttk.Label(
            main,
            text="Custom Fields",
            font=("Segoe UI Variable", 13, "bold"),
            anchor="w",
            style="DialogHeader.TLabel"
        )
        header.pack(anchor="w", pady=(0, 2))

        # Subtle separator
        ttk.Separator(main, orient="horizontal").pack(fill=tk.X, pady=(0, 10))

        # Fields area
        self.fields_frame: ttk.Frame = ttk.Frame(main, style="Dialog.TFrame")
        self.fields_frame.pack(fill=tk.X, pady=(0, 10))
        self.field_vars: list[tuple[ttk.Frame, tk.StringVar, tk.StringVar]] = []

        for key, value in self.custom_fields.items():
            self.add_field_row(key, value)
        if not self.field_vars:
            self.add_field_row()

        # Button row
        btns: ttk.Frame = ttk.Frame(main, style="Dialog.TFrame")
        btns.pack(pady=(8, 0), fill=tk.X)

        add_btn = ttk.Button(
            btns, text="Add Field", command=self.add_field_row, style="Accent.TButton", cursor="hand2"
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._add_tooltip(add_btn, "Add a new custom field")

        ok_btn = ttk.Button(
            btns, text="OK", command=self.on_ok, style="Accent.TButton", cursor="hand2"
        )
        ok_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._add_tooltip(ok_btn, "Save and close")

        cancel_btn = ttk.Button(
            btns, text="Cancel", command=self.destroy, style="Dialog.TButton", cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT)
        self._add_tooltip(cancel_btn, "Cancel and close")

        # Keyboard navigation
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.destroy())

        # Focus on first entry
        self.after(100, self._focus_first_entry)

        # Custom styles
        style = ttk.Style(self)
        style.configure("Dialog.TFrame", background="#23272e")
        style.configure("DialogHeader.TLabel", background="#23272e", foreground="#fff")
        style.configure("Dialog.TButton", background="#444", foreground="#fff", font=("Segoe UI Variable", 10), borderwidth=0, padding=6)
        style.configure("Accent.TButton", background="#3b82f6", foreground="#fff", font=("Segoe UI Variable", 10, "bold"), borderwidth=0, padding=6)
        style.map("Accent.TButton", background=[("active", "#2563eb")])

    def add_field_row(self, key: str = "", value: str = "") -> None:
        row: ttk.Frame = ttk.Frame(self.fields_frame, style="Dialog.TFrame")
        key_var: tk.StringVar = tk.StringVar(value=key)
        value_var: tk.StringVar = tk.StringVar(value=value)
        key_entry = ttk.Entry(row, textvariable=key_var, width=15, font=("Segoe UI Variable", 10))
        key_entry.pack(side=tk.LEFT, padx=(0, 5))
        value_entry = ttk.Entry(row, textvariable=value_var, width=25, font=("Segoe UI Variable", 10))
        value_entry.pack(side=tk.LEFT, padx=(0, 5))
        del_btn: ttk.Button = ttk.Button(
            row, text="Remove", command=lambda: self.remove_field_row(row), style="Dialog.TButton", cursor="hand2"
        )
        del_btn.pack(side=tk.LEFT)
        self._add_tooltip(del_btn, "Remove this field")
        row.pack(fill=tk.X, pady=2)
        self.field_vars.append((row, key_var, value_var))

    def remove_field_row(self, row: ttk.Frame) -> None:
        for i, (r, _, _) in enumerate(self.field_vars):
            if r == row:
                r.destroy()
                self.field_vars.pop(i)
                break

    def on_ok(self) -> None:
        fields: dict[str, Any] = {}
        for _, key_var, value_var in self.field_vars:
            key = key_var.get().strip()
            value = value_var.get().strip()
            if key:
                fields[key] = value
        self.result = fields
        self.destroy()

    def _focus_first_entry(self):
        if self.field_vars:
            row, _, _ = self.field_vars[0]
            entry = row.winfo_children()[0]
            entry.focus_set()

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