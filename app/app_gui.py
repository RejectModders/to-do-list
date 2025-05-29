def run_app() -> None:
    import tkinter as tk

    from app.gui.main_window import MainWindow

    root: tk.Tk = tk.Tk()
    MainWindow(root)
    root.mainloop()
