# ui.py - Интерфейс приложения
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from formulas import (
    CATEGORIES,
    GWP,
    calculate_formula,
    EF_CARBONATES_6_1,
    FORMULA_DESCRIPTIONS,
)
from custom import custom_calc, export_result, draw_graph
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
            command=lambda: export_result(self.results, self.formula_var),
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
            command=lambda: custom_calc(
                self.custom_formula,
                self.custom_vars,
                self.custom_result,
                self.results,
                self.ax,
                self.canvas,
            ),
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

    def update_formulas(self, event):
        group = self.group_var.get()
        self.formula_menu["values"] = CATEGORIES.get(group, [])

    def load_fields(self, event):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.input_widgets = []
        formula = self.formula_var.get()
        description = FORMULA_DESCRIPTIONS.get(formula, "")
        ttk.Label(self.inputs_frame, text=description, wraplength=800).pack(pady=5)
        if "Расход ресурса" in formula:
            self.input_widgets.append(self.create_entry("Mпост (т или тыс. м³):"))
            self.input_widgets.append(self.create_entry("Mотгр (т или тыс. м³):"))
            self.input_widgets.append(self.create_entry("Mзапас_нач (т или тыс. м³):"))
            self.input_widgets.append(self.create_entry("Mзапас_кон (т или тыс. м³):"))
        elif "CO2-эквивалент" in formula:
            self.input_widgets.append(self.create_entry("E_i (т):"))
            self.input_widgets.append(self.create_combobox("Газ:", list(GWP.keys())))
        elif "Постоянная реакции ЗПП" in formula:
            self.input_widgets.append(self.create_entry("t1/2 (полураспад):"))
        elif "Суммарное изменение углерода" in formula:
            self.input_widgets.append(self.create_entry("ΔCбиомасса:"))
            self.input_widgets.append(self.create_entry("ΔCмертвая:"))
            self.input_widgets.append(self.create_entry("ΔCподстилка:"))
            self.input_widgets.append(self.create_entry("ΔCпочва:"))
        elif "Изменение в биомассе" in formula:
            self.input_widgets.append(self.create_entry("C_после:"))
            self.input_widgets.append(self.create_entry("C_до:"))
            self.input_widgets.append(self.create_entry("A (площадь):"))
        elif "Выбросы от пожаров" in formula:
            self.input_widgets.append(self.create_entry("A (площадь):"))
            self.input_widgets.append(self.create_entry("MB (масса биомассы):"))
            self.input_widgets.append(self.create_entry("Cf (коэффициент горения):"))
            self.input_widgets.append(self.create_entry("Gef (коэффициент выбросов):"))
        elif "CO2 от осушенных почв" in formula:
            self.input_widgets.append(self.create_entry("Aосуш:"))
            self.input_widgets.append(self.create_entry("EF:"))
        elif "N2O от осушенных почв" in formula:
            self.input_widgets.append(self.create_entry("Aосуш:"))
            self.input_widgets.append(self.create_entry("EFN_N2O:"))
        elif "CH4 от осушенных почв" in formula:
            self.input_widgets.append(self.create_entry("Aосуш:"))
            self.input_widgets.append(self.create_entry("Fracditch:"))
            self.input_widgets.append(self.create_entry("EFland:"))
            self.input_widgets.append(self.create_entry("EFditch:"))
        elif "Выбросы от карбонатов" in formula:
            self.input_widgets.append(self.create_entry("M_j (масса карбоната):"))
            self.input_widgets.append(
                self.create_combobox("Карбонат:", list(EF_CARBONATES_6_1.keys()))
            )
            self.input_widgets.append(self.create_entry("F_j (доля):"))
        elif "Выбросы CO2 от сжигания топлива" in formula:
            self.input_widgets.append(self.create_entry("FC (расход топлива):"))
            self.input_widgets.append(self.create_entry("EF (коэффициент выбросов):"))
            self.input_widgets.append(self.create_entry("OF (коэффициент окисления):"))
        elif "Коэффициент выбросов CO2 (1.3)" in formula:
            self.input_widgets.append(self.create_entry("W (доля компонента):"))
            self.input_widgets.append(self.create_entry("nC (атомы углерода):"))
            self.input_widgets.append(self.create_entry("rho (плотность):"))
        elif "Коэффициент выбросов CO2 (1.4)" in formula:
            self.input_widgets.append(self.create_entry("W (доля компонента):"))
            self.input_widgets.append(self.create_entry("nC (атомы углерода):"))
            self.input_widgets.append(self.create_entry("M (молярная масса):"))
        elif "Коэффициент выбросов CO2 (1.5)" in formula:
            self.input_widgets.append(self.create_entry("W (содержание углерода):"))
        elif "Содержание углерода в коксе" in formula:
            self.input_widgets.append(self.create_entry("A (содержание золы):"))
            self.input_widgets.append(self.create_entry("V (содержание летучих):"))
            self.input_widgets.append(self.create_entry("S (содержание серы):"))
        elif "Содержание углерода" in formula:
            self.input_widgets.append(
                self.create_entry("EFCO2 (коэффициент выбросов):")
            )
        elif "Коэффициент окисления (1.8)" in formula:
            self.input_widgets.append(self.create_entry("q4 (потери тепла):"))
        elif "Коэффициент окисления (1.9)" in formula:
            self.input_widgets.append(self.create_entry("CC_A (углерод в золе):"))
            self.input_widgets.append(self.create_entry("CC_F (углерод в топливе):"))
        elif "Выбросы от кокса" in formula:
            self.input_widgets.append(self.create_entry("FC:"))
            self.input_widgets.append(self.create_entry("EF:"))
            self.input_widgets.append(self.create_entry("OF:"))
        elif "Выбросы от ТКО" in formula:
            self.input_widgets.append(self.create_entry("M:"))
            self.input_widgets.append(self.create_entry("EF:"))
            self.input_widgets.append(self.create_entry("R:"))
        elif "Запас углерода в биомассе" in formula:
            self.input_widgets.append(self.create_entry("Vij:"))
            self.input_widgets.append(self.create_entry("KPij:"))
        elif "CO2 от осушения" in formula:
            self.input_widgets.append(self.create_entry("A:"))
            self.input_widgets.append(self.create_entry("EF:"))
        elif "Смолистые вещества" in formula:
            self.input_widgets.append(self.create_entry("d (диаметр лунки, дм):"))
            self.input_widgets.append(self.create_entry("h (высота лунки, дм):"))
            self.input_widgets.append(self.create_entry("q (степень заполнения):"))
            self.input_widgets.append(self.create_entry("c (содержание пека):"))
            self.input_widgets.append(
                self.create_entry("rho (плотность жидкой анодной массы):")
            )
            self.input_widgets.append(self.create_entry("k (выход кокса):"))
            self.input_widgets.append(self.create_entry("n (количество штырей):"))
        elif "Углеродная пыль" in formula:
            self.input_widgets.append(self.create_entry("P_пыль (поступление пыли):"))
            self.input_widgets.append(self.create_entry("W_C (содержание углерода):"))
        elif "Углеродная пена" in formula:
            self.input_widgets.append(self.create_entry("P_пена (выход пены):"))
            self.input_widgets.append(
                self.create_entry("W_пена (содержание углерода в пене):")
            )
        elif "N2O от обводнения" in formula:
            self.input_widgets.append(
                self.create_entry("Arewetted (площадь обводненных):")
            )
            self.input_widgets.append(
                self.create_entry("EFN2O-N (коэффициент выброса N2O):")
            )
        elif "Изменение углерода в минеральных почвах" in formula:
            self.input_widgets.append(self.create_entry("Cfert:"))
            self.input_widgets.append(self.create_entry("Clime:"))
            self.input_widgets.append(self.create_entry("Cplant:"))
            self.input_widgets.append(self.create_entry("Cresp:"))
            self.input_widgets.append(self.create_entry("Cerosion:"))
        elif "Поступление углерода с удобрениями" in formula:
            self.input_widgets.append(self.create_entry("C_org:"))
            self.input_widgets.append(self.create_entry("i:"))
            self.input_widgets.append(self.create_entry("C_min:"))
            self.input_widgets.append(self.create_entry("j:"))
        elif "Поступление углерода с известкованием" in formula:
            self.input_widgets.append(self.create_entry("Lime:"))
        elif "Поступление углерода с растительными остатками" in formula:
            self.input_widgets.append(self.create_entry("Cab:"))
            self.input_widgets.append(self.create_entry("Cun:"))
        elif "Расчёт Cab + Cun" in formula:
            self.input_widgets.append(self.create_entry("a:"))
            self.input_widgets.append(self.create_entry("Yi:"))
            self.input_widgets.append(self.create_entry("b:"))
        elif "Потери от эрозии" in formula:
            self.input_widgets.append(self.create_entry("A:"))
            self.input_widgets.append(self.create_entry("EFerosion:"))
        elif "Изменение углерода в торфяниках" in formula:
            self.input_widgets.append(self.create_entry("C_нач:"))
            self.input_widgets.append(self.create_entry("C_кон:"))
            self.input_widgets.append(self.create_entry("A_торф:"))
        elif "CH4 от торфяников" in formula:
            self.input_widgets.append(self.create_entry("A_торф:"))
            self.input_widgets.append(self.create_entry("EF_CH4:"))
        elif "N2O от перевода земель" in formula:
            self.input_widgets.append(self.create_entry("A_перевод:"))
            self.input_widgets.append(self.create_entry("EF_N2O:"))
        elif "Итоговое изменение углерода" in formula:
            self.input_widgets.append(
                self.create_entry("ΔC_i (через пробел, напр. 1 2 3):")
            )

    def create_entry(self, label):
        ttk.Label(self.inputs_frame, text=label).pack()
        entry = tk.Entry(self.inputs_frame, font=("Arial", 12))
        entry.pack()
        return entry

    def create_combobox(self, label, values):
        ttk.Label(self.inputs_frame, text=label).pack()
        var = tk.StringVar()
        combobox = ttk.Combobox(
            self.inputs_frame, textvariable=var, values=values, font=("Arial", 12)
        )
        combobox.pack()
        return var

    def calculate(self):
        formula = self.formula_var.get()
        inputs = [w.get() for w in self.input_widgets]
        try:
            result = calculate_formula(formula, inputs)
            self.result_label.config(text=f"Результат: {result:.2f} т CO2-экв.")
            self.results.append(result)
            draw_graph(self.ax, self.canvas, self.results)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
