# custom.py - Логика кастомных расчетов, экспорта и графиков
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from tkinter import messagebox


class CustomCalculator:
    def __init__(self, ax, canvas, results):
        self.ax = ax
        self.canvas = canvas
        self.results = results

    def calc(self, custom_formula_widget, custom_vars_widget, custom_result_label):
        try:
            formula_text = custom_formula_widget.get("1.0", "end").strip()
            vars_text = custom_vars_widget.get("1.0", "end").strip().split("\n")
            sym_formula = sp.sympify(formula_text)
            subs = {
                sp.symbols(k.split("=")[0].strip()): float(k.split("=")[1].strip())
                for k in vars_text
                if "=" in k
            }
            result = float(sym_formula.subs(subs))
            custom_result_label.config(text=f"Результат: {result:.2f}")
            self.results.append(result)
            self.draw_graph()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def draw_graph(self):
        self.ax.clear()
        self.ax.plot(self.results, marker="o")
        self.ax.set_title("Результаты расчётов")
        self.ax.set_xlabel("Расчёт #")
        self.ax.set_ylabel("т CO2-экв.")
        self.canvas.draw()

    def export_result(self):
        if not self.results:
            messagebox.showinfo("Инфо", "Нет результатов для экспорта")
            return
        try:
            with open("results.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Расчёт", "Значение (т CO2-экв.)"])
                for i, res in enumerate(self.results, 1):
                    writer.writerow([i, res])
            messagebox.showinfo("Успех", "Экспортировано в results.csv")
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", str(e))
