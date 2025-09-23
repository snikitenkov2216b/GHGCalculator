# custom.py - Кастомные формулы, экспорт, графики
import sympy as sp
import csv
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def custom_calc(custom_formula, custom_vars, custom_result, results, ax, canvas):
    try:
        formula_text = custom_formula.get("1.0", "end").strip()
        vars_text = custom_vars.get("1.0", "end").strip()
        symbols = {}
        for line in vars_text.split("\n"):
            if line:
                k, v = line.split("=")
                symbols[k.strip()] = float(v.strip())
        expr = sp.sympify(formula_text)
        result = float(expr.subs(symbols))
        custom_result.config(text=f"Результат: {result:.2f} т CO2-экв.")
        results.append(result)
        draw_graph(ax, canvas, results)
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def export_result(results, formula_var):
    if not results:
        messagebox.showwarning("Нет данных", "Рассчитайте сначала.")
        return
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if file:
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Формула", "Результат"])
            writer.writerow([formula_var.get(), results[-1]])


def draw_graph(ax, canvas, results):
    ax.clear()
    ax.bar(range(len(results)), results)
    ax.set_title("Результаты расчётов")
    ax.set_xlabel("Расчёт #")
    ax.set_ylabel("Значение (т CO2-экв.)")
    canvas.draw()
