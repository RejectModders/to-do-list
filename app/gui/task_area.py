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
        button_width = 14  # Common width for all buttons

        # Top frame for search and filter
        top_frame = ttk.Frame(self, style="Main.TFrame")
        top_frame.pack(fill=tk.X, padx=30, pady=(0, 0))  # Remove top padding

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            top_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11),
            style="TEntry",
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_search())

        filter_btn = ttk.Menubutton(
            top_frame,
            text="Filter",
            style="Accent.TButton",
            direction="below",
            width=button_width,
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

        # Entry and Add button
        entry_frame = ttk.Frame(self, style="Main.TFrame")
        entry_frame.pack(
            fill=tk.X, padx=30, pady=(0, 0)
        )  # Remove vertical padding

        self.task_var = tk.StringVar()
        entry = ttk.Entry(
            entry_frame,
            textvariable=self.task_var,
            font=("Segoe UI", 12),
            style="TEntry",
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=6)
        add_btn = ttk.Button(
            entry_frame,
            text="Add Task",
            image=self.icons["add"],
            compound=tk.LEFT,
            style="Accent.TButton",
            command=self.open_add_task_dialog,
            width=button_width,
        )
        add_btn.grid(row=0, column=1, sticky="ew")
        entry_frame.columnconfigure(0, weight=1)
        entry_frame.columnconfigure(1, weight=0)

        # Header row: "Tasks" label left, "Delete Task" button right
        tasks_header = ttk.Frame(self, style="Main.TFrame")
        tasks_header.pack(
            fill=tk.X, padx=32, pady=(0, 0)
        )  # Remove vertical padding

        tasks_label = ttk.Label(
            tasks_header,
            text="Tasks",
            style="TLabel",
            anchor="w",
            font=("Segoe UI", 13, "bold"),
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
        )
        del_btn.grid(row=0, column=1, sticky="e", padx=(0, 0))

        tasks_header.columnconfigure(0, weight=1)
        tasks_header.columnconfigure(1, weight=1)  # Make both columns expand

        # Listbox frame
        listbox_frame = ttk.Frame(
            self, style="Main.TFrame", borderwidth=1, relief=tk.GROOVE
        )
        listbox_frame.pack(
            fill=tk.BOTH, expand=True, padx=30, pady=(0, 0)
        )  # Remove bottom padding

        self.task_listbox = tk.Listbox(
            listbox_frame,
            font=("Segoe UI", 12),
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
        self.task_listbox.bind(
            "<Button-2>", self.show_task_context_menu
        )  # macOS

        scrollbar = ttk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.task_listbox.yview,  # type: ignore
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
            self.task_listbox.insert(tk.END, t.text)

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
        index: int = int(self.task_listbox.nearest(event.y))  # type: ignore
        if index < 0 or index >= self.task_listbox.size():
            return
        self.task_listbox.selection_clear(0, tk.END)
        self.task_listbox.selection_set(index)  # type: ignore
        menu: tk.Menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Edit", command=lambda: self.open_edit_task_dialog(index)
        )
        menu.add_command(
            label="Complete", command=lambda: self.complete_task(index)
        )
        menu.add_command(
            label="Delete", command=lambda: self.delete_task(index=index)
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def add_task(self) -> None:
        pass  # Deprecated

    def delete_task(self, index: int | None = None) -> None:
        if index is None:
            selected = self.task_listbox.curselection()  # type: ignore
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
        if search_text:
            return [t for t in tasks if search_text in t.text.lower()]
        return tasks
