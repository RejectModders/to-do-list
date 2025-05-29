import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable

from .task_dialog import TaskDialog

class TaskArea(ttk.Frame):
    def __init__(
        self,
        parent: Any,
        controller: Any,
        icons: dict[str, Any],
        theme: dict[str, Any],
        get_selected_category: Callable[[], str],
        refresh_tasks: Callable[[], None],
    ) -> None:
        super().__init__(parent, style="Main.TFrame")
        self.controller = controller
        self.icons = icons
        self.theme = theme
        self.get_selected_category = get_selected_category
        self.refresh_tasks = refresh_tasks
        self.active_filter = "All"
        self.tasks: list[Any] = []
        self.search_var: tk.StringVar
        self.task_var: tk.StringVar
        self.task_listbox: tk.Listbox
        self.filter_menu: tk.Menu
        self.build()

    def build(self) -> None:
        button_width = 14

        # Top frame for search and filter
        top_frame = ttk.Frame(self, style="Main.TFrame")
        top_frame.pack(fill=tk.X, padx=30, pady=(18, 0))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            top_frame,
            textvariable=self.search_var,
            font=("Segoe UI Variable", 11),
            style="TEntry",
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=4)
        search_entry.bind("<KeyRelease>", lambda e: self.apply_search())
        search_entry.insert(0, "Search tasks...")
        search_entry.bind("<FocusIn>", lambda e: self._clear_placeholder(search_entry))
        search_entry.bind("<FocusOut>", lambda e: self._add_placeholder(search_entry))

        filter_btn = ttk.Menubutton(
            top_frame,
            text="Filter",
            style="Accent.TButton",
            direction="below",
            width=button_width,
            cursor="hand2"
        )
        self.filter_menu = tk.Menu(filter_btn, tearoff=0)
        for f in ["All", "Completed", "Incomplete"]:
            self.filter_menu.add_command(
                label=f, command=lambda f=f: self.set_filter(f)
            )
        filter_btn["menu"] = self.filter_menu
        filter_btn.grid(row=0, column=1, sticky="ew")
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=0)

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, padx=30, pady=(10, 8))

        # Entry and Add button
        entry_frame = ttk.Frame(self, style="Main.TFrame")
        entry_frame.pack(fill=tk.X, padx=30, pady=(0, 0))

        self.task_var = tk.StringVar()
        entry = ttk.Entry(
            entry_frame,
            textvariable=self.task_var,
            font=("Segoe UI Variable", 12),
            style="TEntry",
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=6)
        entry.bind("<Return>", lambda e: self.open_add_task_dialog())
        self._add_tooltip(entry, "Enter a new task and press Enter or click Add Task")

        add_btn = ttk.Button(
            entry_frame,
            text="Add Task",
            image=self.icons["add"],
            compound=tk.LEFT,
            style="Accent.TButton",
            command=self.open_add_task_dialog,
            width=button_width,
            cursor="hand2"
        )
        add_btn.grid(row=0, column=1, sticky="ew")
        self._add_tooltip(add_btn, "Add a new task")
        entry_frame.columnconfigure(0, weight=1)
        entry_frame.columnconfigure(1, weight=0)

        # Header row: "Tasks" label left, "Delete Task" button right
        tasks_header = ttk.Frame(self, style="Main.TFrame")
        tasks_header.pack(fill=tk.X, padx=32, pady=(10, 0))

        tasks_label = ttk.Label(
            tasks_header,
            text="Tasks",
            style="TLabel",
            anchor="w",
            font=("Segoe UI Variable", 13, "bold"),
        )
        tasks_label.grid(row=0, column=0, sticky="w")

        del_btn = ttk.Button(
            tasks_header,
            text="Delete Task",
            image=self.icons["delete"],
            compound=tk.LEFT,
            style="Accent.TButton",
            command=self.delete_task,
            width=button_width,
            takefocus=False,
            cursor="hand2"
        )
        del_btn.grid(row=0, column=1, sticky="e", padx=(0, 0))
        self._add_tooltip(del_btn, "Delete the selected task")

        tasks_header.columnconfigure(0, weight=1)
        tasks_header.columnconfigure(1, weight=1)

        # Listbox frame
        listbox_frame = ttk.Frame(
            self, style="Main.TFrame", borderwidth=1, relief=tk.GROOVE
        )
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(8, 18))

        self.task_listbox = tk.Listbox(
            listbox_frame,
            font=("Segoe UI Variable", 12),
            bg=self.theme["listbox_bg"],
            fg=self.theme["listbox_fg"],
            selectbackground=self.theme["select_bg"],
            selectforeground=self.theme["select_fg"],
            activestyle="none",
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        self.task_listbox.grid(row=0, column=0, sticky="nsew")
        self.task_listbox.bind("<Button-3>", self.show_task_context_menu)
        self.task_listbox.bind("<Button-2>", self.show_task_context_menu)
        self.task_listbox.bind("<Double-Button-1>", self._on_double_click)
        self.task_listbox.bind("<Return>", self._on_enter_key)
        self.task_listbox.bind("<Motion>", self._on_hover)
        self.task_listbox.bind("<Leave>", self._on_leave)
        self.task_listbox.bind("<FocusIn>", self._on_focus_in)
        self.task_listbox.bind("<FocusOut>", self._on_focus_out)

        scrollbar = ttk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.task_listbox.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.task_listbox.config(yscrollcommand=scrollbar.set)

        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.columnconfigure(0, weight=1)

    def refresh(self, tasks: list[Any]) -> None:
        self.tasks = self.apply_filter_logic(tasks)
        self.tasks = self.apply_search_logic(self.tasks)
        self.task_listbox.delete(0, tk.END)
        for t in self.tasks:
            display = t.text
            if getattr(t, "completed", False):
                display = f"\u2713 {t.text}"
            self.task_listbox.insert(tk.END, display)
            if getattr(t, "completed", False):
                self.task_listbox.itemconfig(
                    tk.END,
                    fg=self.theme.get("completed_fg", "#888"),
                    selectforeground=self.theme.get("completed_fg", "#888"),
                )

    def open_add_task_dialog(self) -> None:
        title: str = self.task_var.get().strip()
        if not title:
            messagebox.showwarning("Input Error", "Task name cannot be empty.")  # type: ignore
            return
        dialog: TaskDialog = TaskDialog(self, title=title)
        self.wait_window(dialog)
        if dialog.result:
            custom_fields: dict[str, Any] = dialog.result
            category: str = self.get_selected_category()
            self.controller.add_task(title, category, **custom_fields)
            self.task_var.set("")
            self.refresh_tasks()

    def open_edit_task_dialog(self, index: int) -> None:
        task: Any = self.tasks[index]
        dialog: TaskDialog = TaskDialog(
            self,
            title=task.text,
            custom_fields=getattr(task, "custom_fields", {}),
        )
        self.wait_window(dialog)
        if dialog.result:
            custom_fields: dict[str, Any] = dialog.result
            category: str = self.get_selected_category()
            self.controller.edit_task(
                index, category, task.text, **custom_fields
            )
            self.refresh_tasks()

    def show_task_context_menu(self, event: tk.Event) -> None:
        index: int = int(self.task_listbox.nearest(event.y))
        if index < 0 or index >= self.task_listbox.size():
            return
        self.task_listbox.selection_clear(0, tk.END)
        self.task_listbox.selection_set(index)
        task = self.tasks[index]
        menu: tk.Menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Edit", command=lambda: self.open_edit_task_dialog(index)
        )
        menu.add_command(
            label="Complete",
            command=lambda: self.complete_task(index),
            state="disabled" if getattr(task, "completed", False) else "normal"
        )
        menu.add_command(
            label="Delete", command=lambda: self.delete_task(index=index)
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def delete_task(self, index: int | None = None) -> None:
        if index is None:
            selected = self.task_listbox.curselection()
            if not selected:
                messagebox.showwarning("Selection Error", "No task selected.")  # type: ignore
                return
            index = selected[0]
        category: str = self.get_selected_category()
        self.controller.delete_task(index, category)
        self.refresh_tasks()

    def complete_task(self, index: int) -> None:
        category: str = self.get_selected_category()
        self.controller.complete_task(index, category)
        self.refresh_tasks()

    def set_filter(self, filter_name: str) -> None:
        self.active_filter = filter_name
        self.refresh_tasks()

    def apply_filter_logic(self, tasks: list[Any]) -> list[Any]:
        if self.active_filter == "Completed":
            return [t for t in tasks if getattr(t, "completed", False)]
        elif self.active_filter == "Incomplete":
            return [t for t in tasks if not getattr(t, "completed", False)]
        return tasks

    def apply_search(self) -> None:
        self.refresh_tasks()

    def apply_search_logic(self, tasks: list[Any]) -> list[Any]:
        search_text: str = self.search_var.get().strip().lower()
        if search_text and search_text != "search tasks...":
            return [t for t in tasks if search_text in t.text.lower()]
        return tasks

    # --- UI polish helpers ---

    def _clear_placeholder(self, entry):
        if entry.get() == "Search tasks...":
            entry.delete(0, tk.END)
            entry.config(foreground=self.theme["entry_fg"])

    def _add_placeholder(self, entry):
        if not entry.get():
            entry.insert(0, "Search tasks...")
            entry.config(foreground="#888")

    def _on_double_click(self, event):
        index = self.task_listbox.curselection()
        if index:
            self.open_edit_task_dialog(index[0])

    def _on_enter_key(self, event):
        index = self.task_listbox.curselection()
        if index:
            self.open_edit_task_dialog(index[0])

    def _on_hover(self, event):
        index = self.task_listbox.nearest(event.y)
        if 0 <= index < self.task_listbox.size():
            self.task_listbox.activate(index)

    def _on_leave(self, event):
        self.task_listbox.activate(-1)

    def _on_focus_in(self, event):
        self.task_listbox.config(highlightbackground=self.theme["accent"], highlightthickness=2)

    def _on_focus_out(self, event):
        self.task_listbox.config(highlightthickness=0)

    def _add_tooltip(self, widget, text):
        # Simple tooltip for accessibility
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