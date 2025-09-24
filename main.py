# main.py - Запуск приложения
import tkinter as tk
from ttkthemes import ThemedTk
from ui import GHGCalculator

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Красивая тема
    app = GHGCalculator(root)
    root.mainloop()
