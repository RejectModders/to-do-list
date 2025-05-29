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
        self.grab_set()
        self.resizable(False, False)
        self.custom_fields: dict[str, Any] = (
            custom_fields.copy() if custom_fields else {}
        )

        ttk.Label(self, text="Add custom fields (key/value):").pack(
            padx=10, pady=(10, 0), anchor="w"
        )
        self.fields_frame: ttk.Frame = ttk.Frame(self)
        self.fields_frame.pack(padx=10, pady=5, fill=tk.X)
        self.field_vars: list[
            tuple[ttk.Frame, tk.StringVar, tk.StringVar]
        ] = []

        for key, value in self.custom_fields.items():
            self.add_field_row(key, value)
        if not self.field_vars:
            self.add_field_row()

        btns: ttk.Frame = ttk.Frame(self)
        btns.pack(pady=5)
        ttk.Button(btns, text="Add Field", command=self.add_field_row).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btns, text="OK", command=self.on_ok).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def add_field_row(self, key: str = "", value: str = "") -> None:
        row: ttk.Frame = ttk.Frame(self.fields_frame)
        key_var: tk.StringVar = tk.StringVar(value=key)
        value_var: tk.StringVar = tk.StringVar(value=value)
        ttk.Entry(row, textvariable=key_var, width=15).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Entry(row, textvariable=value_var, width=25).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        del_btn: ttk.Button = ttk.Button(
            row, text="Remove", command=lambda: self.remove_field_row(row)
        )
        del_btn.pack(side=tk.LEFT)
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
