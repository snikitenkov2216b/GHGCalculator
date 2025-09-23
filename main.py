# main.py - Запуск приложения
from ttkthemes import ThemedTk
from ui import GHGCalculator

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # Красивая тема
    app = GHGCalculator(root)
    root.mainloop()
