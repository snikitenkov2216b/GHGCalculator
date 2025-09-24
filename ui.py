# ui.py - Интерфейс приложения
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import sympy as sp  # Для custom_calc
from formulas import (
    CATEGORIES,
    GWP,
    calculate_formula,
    EF_CARBONATES_6_1,
    FORMULA_DESCRIPTIONS,
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv


class GHGCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор парниковых газов (Приказ 371)")
        self.root.geometry("900x700")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TButton", font=("Arial", 12), padding=10)

        self.tab_control = ttk.Notebook(root)
        self.tab_main = ttk.Frame(self.tab_control)
        self.tab_custom = ttk.Frame(self.tab_control)
        self.tab_graph = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_main, text="Расчёты по формулам")
        self.tab_control.add(self.tab_custom, text="Своя формула")
        self.tab_control.add(self.tab_graph, text="График результатов")
        self.tab_control.pack(expand=1, fill="both")

        # Основная вкладка
        ttk.Label(self.tab_main, text="Группа формул:").pack(pady=5)
        self.group_var = tk.StringVar()
        self.group_menu = ttk.Combobox(
            self.tab_main,
            textvariable=self.group_var,
            values=list(CATEGORIES.keys()),
            font=("Arial", 12),
        )
        self.group_menu.pack(pady=5)
        self.group_menu.config(width=60)
        self.group_menu.bind("<<ComboboxSelected>>", self.update_formulas)

        ttk.Label(self.tab_main, text="Формула:").pack(pady=5)
        self.formula_var = tk.StringVar()
        self.formula_menu = ttk.Combobox(
            self.tab_main, textvariable=self.formula_var, font=("Arial", 12)
        )
        self.formula_menu.pack(pady=5)
        self.formula_menu.config(width=60)
        self.formula_menu.bind("<<ComboboxSelected>>", self.load_fields)

        self.inputs_frame = ttk.Frame(self.tab_main)
        self.inputs_frame.pack(fill="both", expand=True, pady=10)

        self.calc_button = ttk.Button(
            self.tab_main, text="Рассчитать", command=self.calculate
        )
        self.calc_button.pack(pady=10)

        self.result_label = ttk.Label(
            self.tab_main, text="", font=("Arial", 14, "bold")
        )
        self.result_label.pack(pady=10)

        self.export_button = ttk.Button(
            self.tab_main,
            text="Экспорт в CSV",
            command=self.export_result,
        )
        self.export_button.pack(pady=10)

        # Кастомная формула
        ttk.Label(self.tab_custom, text="Введите формулу (sympy синтаксис):").pack(
            pady=5
        )
        self.custom_formula = tk.Text(self.tab_custom, height=5, font=("Arial", 12))
        self.custom_formula.pack(pady=5)

        ttk.Label(self.tab_custom, text="Переменные (key=value, по строкам):").pack(
            pady=5
        )
        self.custom_vars = tk.Text(self.tab_custom, height=10, font=("Arial", 12))
        self.custom_vars.pack(pady=5)

        ttk.Button(
            self.tab_custom,
            text="Вычислить",
            command=self.custom_calc,
        ).pack(pady=10)

        self.custom_result = ttk.Label(
            self.tab_custom, text="", font=("Arial", 14, "bold")
        )
        self.custom_result.pack(pady=10)

        # График
        self.fig = plt.Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self.tab_graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.results = []
        self.input_widgets = []
        self.current_formula_number = None

    def update_formulas(self, event):
        group = self.group_var.get()
        category = CATEGORIES.get(group, {})
        self.formula_menu["values"] = [
            f"{key} - {desc}" for key, desc in category.items()
        ]
        self.formula_var.set("")  # Сброс выбора формулы

    def load_fields(self, event):
        # Очистка предыдущих полей
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.input_widgets = []

        formula_str = self.formula_var.get()
        if not formula_str:
            return
        # Извлечение номера формулы из строки (например, "(1.1)")
        number = formula_str.split(" - ")[0]
        if number in FORMULA_DESCRIPTIONS:
            desc = FORMULA_DESCRIPTIONS[number]
            ttk.Label(self.inputs_frame, text=desc["description"]).pack(pady=5)
            for inp in desc["inputs"]:
                ttk.Label(self.inputs_frame, text=inp).pack()
                entry = ttk.Entry(self.inputs_frame, font=("Arial", 12))
                entry.pack()
                self.input_widgets.append(entry)
            self.current_formula_number = number

    def calculate(self):
        if not self.current_formula_number:
            messagebox.showerror("Ошибка", "Выберите формулу")
            return
        inputs = [w.get() for w in self.input_widgets if w.get()]
        try:
            result = calculate_formula(self.current_formula_number, inputs)
            self.result_label.config(text=f"Результат: {result:.2f} т CO2-экв.")
            self.results.append(result)
            self.draw_graph()
        except ValueError as ve:
            messagebox.showerror("Ошибка ввода", str(ve))
        except Exception as e:
            messagebox.showerror("Ошибка расчёта", str(e))

    def custom_calc(self):
        try:
            formula_text = self.custom_formula.get("1.0", "end").strip()
            vars_text = self.custom_vars.get("1.0", "end").strip().split("\n")
            sym_formula = sp.sympify(formula_text)
            subs = {
                sp.symbols(k.split("=")[0].strip()): float(k.split("=")[1].strip())
                for k in vars_text
                if "=" in k
            }
            result = float(sym_formula.subs(subs))
            self.custom_result.config(text=f"Результат: {result:.2f}")
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
