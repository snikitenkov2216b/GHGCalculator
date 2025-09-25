# ui.py - Интерфейс приложения

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageTk
from formulas import CATEGORIES
from data_tables import TABLE_1_1, TABLE_1_2


class GHGCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Система расчёта выбросов парниковых газов")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        # Стиль
        style = ttk.Style()
        style.theme_use("arc")
        style.configure(
            "TEntry",
            fieldbackground="#ffffff",
            foreground="black",
            font=("Arial", 10),
            padding=3,
        )
        style.map("TEntry", fieldbackground=[("focus", "#e6f7ff")])
        style.configure(
            "TCombobox",
            fieldbackground="#ffffff",
            foreground="black",
            font=("Arial", 10),
            padding=3,
            arrowcolor="black",
        )
        style.map("TCombobox", fieldbackground=[("focus", "#e6f7ff")])
        style.configure(
            "TButton",
            background="#ffffff",
            foreground="black",
            font=("Arial", 10, "bold"),
            padding=3,
            borderwidth=1,
            relief="solid",
        )
        style.map("TButton", background=[("active", "#f0f0f0")])
        style.configure(
            "TLabel", font=("Arial", 12, "bold"), foreground="#333333", padding=3
        )

        # Главный фрейм
        self.main_frame = ttk.Frame(root, padding=3)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Выбор категории
        self.category_label = ttk.Label(self.main_frame, text="Выберите категорию:")
        self.category_label.pack(pady=0)
        self.category_combo = ttk.Combobox(
            self.main_frame, values=list(CATEGORIES.keys()), width=50
        )
        self.category_combo.pack(pady=0)
        self.category_combo.bind("<<ComboboxSelected>>", self.load_formulas)

        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=1)

        # Выбор формулы
        self.formula_label = ttk.Label(self.main_frame, text="Выберите формулу:")
        self.formula_label.pack(pady=0)
        self.formula_combo = ttk.Combobox(self.main_frame, width=50)
        self.formula_combo.pack(pady=0)
        self.formula_combo.bind("<<ComboboxSelected>>", self.load_formula_ui)

        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=1)

        # Фрейм для контента
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.input_entries = {}  # Словарь для Entry по var_latex
        self.fuel_entries = []  # Для (1.1)

    def load_formulas(self, event):
        category = self.category_combo.get()
        formulas = CATEGORIES.get(category, {})
        values = [
            f"{key} - {formula['description']}" for key, formula in formulas.items()
        ]
        self.formula_combo["values"] = values

    def load_formula_ui(self, event):
        self.clear_content()
        category = self.category_combo.get()
        selected = self.formula_combo.get()
        formula_key = selected.split(" - ", 1)[0]
        formula = CATEGORIES[category][formula_key]

        # Отображение LaTeX формулы
        latex_label = self.create_latex_label(
            self.content_frame, formula["latex"], (6, 1)
        )
        latex_label.pack(pady=1)

        desc_label = ttk.Label(
            self.content_frame, text=formula["description"], font=("Arial", 10)
        )
        desc_label.pack()

        ttk.Separator(self.content_frame, orient="horizontal").pack(fill=tk.X, pady=1)

        # Специальный UI для (1.1)
        if formula_key == "(1.1)":
            self.load_1_1_ui()
        else:
            self.load_generic_ui(formula)

        calc_btn = ttk.Button(
            self.content_frame,
            text="Рассчитать",
            command=lambda: self.calculate(formula_key, formula),
        )
        calc_btn.pack(pady=1)

        self.result_label = ttk.Label(
            self.content_frame, text="Результат: ", font=("Arial", 12, "bold")
        )
        self.result_label.pack()

    def load_1_1_ui(self):
        # Canvas для скролла
        canvas = tk.Canvas(self.content_frame, height=450)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(
            self.content_frame, orient="vertical", command=canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        fuel_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=fuel_frame, anchor="nw")
        fuel_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )
        fuel_frame.bind(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )  # Только на canvas и fuel_frame

        add_btn = ttk.Button(
            self.content_frame,
            text="Добавить топливо",
            command=lambda: self.add_fuel_entry(fuel_frame, canvas),
        )
        add_btn.pack(pady=0)

        self.add_fuel_entry(fuel_frame, canvas)

    def add_fuel_entry(self, fuel_frame, canvas):
        frame = ttk.Frame(fuel_frame, borderwidth=1, relief="solid", padding=3)
        frame.pack(fill=tk.X, pady=0)

        # Bind скролл к блоку
        frame.bind(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        # Топливо
        fuel_label = ttk.Label(frame, text="Тип топлива:")
        fuel_label.grid(row=0, column=0, padx=0, pady=0)
        fuel_combo = ttk.Combobox(frame, values=list(TABLE_1_1.keys()), width=35)
        fuel_combo.grid(row=0, column=1, columnspan=2, padx=0, pady=0)
        fuel_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.update_fuel_params(frame)
        )

        # Единицы
        unit_label = ttk.Label(frame, text="Единицы:")
        unit_label.grid(row=0, column=3, padx=0, pady=0)
        unit_combo = ttk.Combobox(frame, values=["т у.т.", "ТДж"], width=10)
        unit_combo.grid(row=0, column=4, padx=0, pady=0)
        unit_combo.set("т у.т.")
        unit_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.update_fuel_params(frame)
        )

        # FC
        fc_label = self.create_latex_label(frame, r"FC_{j,y}", (1.5, 0.5))
        fc_label.grid(row=1, column=0, padx=0, pady=0)
        fc_entry = ttk.Entry(frame, width=15)
        fc_entry.grid(row=1, column=1, padx=0, pady=0)
        fc_btn = ttk.Button(
            frame,
            text="Расчёт FC",
            command=lambda: self.open_sub_calc(
                "FC", fc_entry, fuel_combo.get(), unit_combo.get()
            ),
        )
        fc_btn.grid(row=1, column=2, padx=0, pady=0)

        fc_info_label = ttk.Label(
            frame,
            text="Коэффициенты выбросов CO2 при сжигании топлива (EFCO2,j,y) и коэффициент окисления (OFj,y) рассчитываются на основе фактических данных. Если таких данных нет, используются табличные значения.",
            font=("Arial", 7, "italic"),
            foreground="#666666",
            wraplength=250,
        )
        fc_info_label.grid(row=2, column=0, columnspan=5, padx=0, pady=0)

        # EF
        ef_label = self.create_latex_label(frame, r"EF_{\text{CO}_2,j,y}", (2, 0.5))
        ef_label.grid(row=3, column=0, padx=0, pady=0)
        ef_entry = ttk.Entry(frame, width=15)
        ef_entry.grid(row=3, column=1, padx=0, pady=0)
        ef_btn = ttk.Button(
            frame,
            text="Расчёт EF",
            command=lambda: self.open_sub_calc(
                "EF", ef_entry, fuel_combo.get(), unit_combo.get()
            ),
        )
        ef_btn.grid(row=3, column=2, padx=0, pady=0)

        # OF
        of_label = self.create_latex_label(frame, r"OF_{j,y}", (1.5, 0.5))
        of_label.grid(row=4, column=0, padx=0, pady=0)
        of_entry = ttk.Entry(frame, width=15)
        of_entry.grid(row=4, column=1, padx=0, pady=0)
        of_btn = ttk.Button(
            frame, text="Расчёт OF", command=lambda: self.open_sub_calc("OF", of_entry)
        )
        of_btn.grid(row=4, column=2, padx=0, pady=0)

        remove_btn = ttk.Button(
            frame, text="Удалить", command=lambda: self.remove_fuel_entry(frame)
        )
        remove_btn.grid(row=0, column=5, rowspan=5, padx=0, pady=0)

        self.fuel_entries.append(
            {
                "fuel_combo": fuel_combo,
                "unit_combo": unit_combo,
                "fc_entry": fc_entry,
                "ef_entry": ef_entry,
                "of_entry": of_entry,
                "frame": frame,
            }
        )

    def remove_fuel_entry(self, frame):
        self.fuel_entries = [e for e in self.fuel_entries if e["frame"] != frame]
        frame.destroy()

    def update_fuel_params(self, frame):
        for entry in self.fuel_entries:
            if entry["frame"] == frame:
                fuel = entry["fuel_combo"].get()
                unit = entry["unit_combo"].get()
                if fuel in TABLE_1_1:
                    data = TABLE_1_1[fuel]
                    ef_key = "EF_TJ" if unit == "ТДж" else "EF"
                    ef_entry = entry["ef_entry"]
                    ef_entry.delete(0, tk.END)
                    ef_entry.insert(0, str(data[ef_key]))

                    of_entry = entry["of_entry"]
                    of_entry.config(state="normal")
                    of_entry.delete(0, tk.END)
                    if data["type"] in ["gas", "liquid"]:
                        of_entry.insert(0, "1.0")
                    else:
                        of_entry.insert(0, "0.98")  # Default for solid
                break

    def load_generic_ui(self, formula):
        for input_data in formula["inputs"][1:]:  # Пропустить output
            var_frame = ttk.Frame(self.content_frame)
            var_frame.pack(fill=tk.X, pady=0)
            sub_frame = ttk.Frame(var_frame)
            sub_frame.pack()
            latex_label = self.create_latex_label(
                sub_frame, input_data["var_latex"], (2, 0.5)
            )
            latex_label.pack(side=tk.LEFT, padx=0)
            entry = ttk.Entry(sub_frame, width=20)
            entry.pack(side=tk.LEFT, padx=0)
            desc_label = ttk.Label(
                var_frame, text=input_data["description"], font=("Arial", 8)
            )
            desc_label.pack(pady=0)
            self.input_entries[input_data["var_latex"]] = entry

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.input_entries = {}
        self.fuel_entries = []

    def calculate(self, formula_key, formula):
        try:
            if formula_key == "(1.1)":
                fc_list = []
                ef_list = []
                of_list = []
                for e in self.fuel_entries:
                    fc = float(e["fc_entry"].get())
                    ef = float(e["ef_entry"].get())
                    of_val = float(e["of_entry"].get())
                    unit = e["unit_combo"].get()
                    fuel = e["fuel_combo"].get()
                    fc_list.append(fc)
                    ef_list.append(ef)
                    of_list.append(of_val)
                args = [fc_list, ef_list, of_list]
            else:
                args = []
                for input_data in formula["inputs"][1:]:
                    value_str = (
                        self.input_entries.get(input_data["var_latex"])
                        .get()
                        .replace(",", ".")
                    )
                    if "," in value_str:
                        args.append([float(x.strip()) for x in value_str.split(",")])
                    else:
                        args.append(float(value_str))

            result = formula["function"](*args)
            self.result_label.config(text=f"Результат: {result:.4f} т CO2")
        except ValueError as e:
            messagebox.showerror(
                "Ошибка", str(e) + ". Используйте точку для десятичных чисел."
            )

    def open_sub_calc(self, sub_type, target_entry, fuel="", unit=""):
        window = tk.Toplevel(self.root)
        window.title(f"Расчёт {sub_type}")
        window.geometry("500x400")

        variant_var = tk.StringVar()
        all_variants = {
            "FC": ["(1.2а)", "(1.2б)"],
            "EF": ["(1.3)", "(1.4)", "(1.5)"],
            "OF": ["(1.8)", "(1.9)"],
        }[sub_type]
        variants = (
            all_variants
            if sub_type != "FC"
            else [
                v
                for v in all_variants
                if (unit == "т у.т." and v == "(1.2а)")
                or (unit == "ТДж" and v == "(1.2б)")
            ]
        )
        if not variants:
            variants = all_variants  # Fallback
        for v in variants:
            radio_frame = ttk.Frame(window)
            radio_frame.pack(anchor=tk.W)
            ttk.Radiobutton(radio_frame, text=v, variable=variant_var, value=v).pack(
                side=tk.LEFT
            )
            desc = CATEGORIES["1. Стационарное сжигание топлива"][v]["description"]
            ttk.Label(radio_frame, text=desc, font=("Arial", 8, "italic")).pack(
                side=tk.LEFT, padx=0
            )

        self.sub_input_entries = {}

        def update_sub_ui(name, index, mode):
            v = variant_var.get()
            for widget in list(window.winfo_children())[len(variants) :]:
                widget.destroy()
            sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
            self.sub_input_entries = {}
            for input_data in sub_formula["inputs"][1:]:
                var_frame = ttk.Frame(window)
                var_frame.pack(fill=tk.X, pady=0)
                sub_frame = ttk.Frame(var_frame)
                sub_frame.pack()
                latex_label = self.create_latex_label(
                    sub_frame, input_data["var_latex"], (2, 0.5)
                )
                latex_label.pack(side=tk.LEFT, padx=0)
                if input_data["var_latex"] == r"\rho_{\text{CO}_2}":
                    rho_combo = ttk.Combobox(
                        sub_frame, values=list(TABLE_1_2.keys()), width=25
                    )
                    rho_combo.pack(side=tk.LEFT, padx=0)
                    self.sub_input_entries[input_data["var_latex"]] = rho_combo
                else:
                    entry = ttk.Entry(sub_frame, width=25)
                    entry.pack(side=tk.LEFT, padx=0)
                    self.sub_input_entries[input_data["var_latex"]] = entry
                desc_label = ttk.Label(
                    var_frame, text=input_data["description"], font=("Arial", 8)
                )
                desc_label.pack(pady=0)
                if (
                    input_data["var_latex"] == r"k_{j,y}"
                    and v == "(1.2а)"
                    and fuel in TABLE_1_1
                ):
                    entry.insert(0, str(TABLE_1_1[fuel]["k"]))
                if (
                    input_data["var_latex"] == r"NCV_{j,y}"
                    and v == "(1.2б)"
                    and fuel in TABLE_1_1
                ):
                    entry.insert(0, str(TABLE_1_1[fuel]["NCV"]))
                if input_data["var_latex"] == r"NCV_{j,y}" and fuel in TABLE_1_1:
                    entry.insert(0, str(TABLE_1_1[fuel]["NCV"]))
                if (
                    input_data["var_latex"] == r"W_{C,j,y}"
                    and sub_type == "EF"
                    and v == "(1.5)"
                    and fuel in TABLE_1_1
                ):
                    w_key = "W_TJ" if unit == "ТДж" else "W"
                    entry.insert(0, str(TABLE_1_1[fuel][w_key]))

            if sub_type == "EF":
                w_c_btn = ttk.Button(
                    window,
                    text="Расчёт W_C",
                    command=lambda: self.open_sub_sub_calc(
                        "W_C", self.sub_input_entries.get(r"W_{C,j,y}")
                    ),
                )
                w_c_btn["style"] = "TButton"  # Красиво
                w_c_btn.pack(pady=0)

            # Кнопка Рассчитать
            ttk.Button(window, text="Рассчитать", command=calc_sub).pack(pady=1)

        def calc_sub():
            try:
                v = variant_var.get()
                sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
                args = []
                for input_data in sub_formula["inputs"][1:]:
                    widget = self.sub_input_entries.get(input_data["var_latex"])
                    if widget is None:
                        args.append(0.0)
                        continue
                    value_str = widget.get().replace(",", ".")
                    if input_data["var_latex"] == r"\rho_{\text{CO}_2}":
                        condition = value_str
                        rho_value = TABLE_1_2.get(condition, {}).get("rho_CO2", 0.0)
                        args.append(rho_value)
                    elif "," in value_str:
                        args.append([float(x.strip()) for x in value_str.split(",")])
                    else:
                        args.append(float(value_str or "0"))
                result = sub_formula["function"](*args)
                target_entry.delete(0, tk.END)
                target_entry.insert(0, str(result))
                window.destroy()
            except ValueError as e:
                messagebox.showerror(
                    "Ошибка", str(e) + ". Используйте точку для десятичных."
                )

        variant_var.trace("w", update_sub_ui)
        variant_var.set(variants[0])
        update_sub_ui(None, None, None)  # Инициализация

    def open_sub_sub_calc(self, sub_sub_type, target_entry):
        if sub_sub_type == "W_C":
            window = tk.Toplevel(self.root)
            window.title("Расчёт W_C")
            window.geometry("500x300")

            variant_var = tk.StringVar()
            variants = ["(1.6)", "(1.7)", "(1.10)"]
            for v in variants:
                radio_frame = ttk.Frame(window)
                radio_frame.pack(anchor=tk.W)
                ttk.Radiobutton(
                    radio_frame, text=v, variable=variant_var, value=v
                ).pack(side=tk.LEFT)
                desc = CATEGORIES["1. Стационарное сжигание топлива"][v]["description"]
                ttk.Label(radio_frame, text=desc, font=("Arial", 8, "italic")).pack(
                    side=tk.LEFT, padx=0
                )

            self.sub_sub_input_entries = {}

            def update_sub_sub_ui(name, index, mode):
                v = variant_var.get()
                for widget in list(window.winfo_children())[len(variants) :]:
                    widget.destroy()
                sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
                self.sub_sub_input_entries = {}
                for input_data in sub_formula["inputs"][1:]:
                    var_frame = ttk.Frame(window)
                    var_frame.pack(fill=tk.X, pady=0)
                    sub_frame = ttk.Frame(var_frame)
                    sub_frame.pack()
                    latex_label = self.create_latex_label(
                        sub_frame, input_data["var_latex"], (2, 0.5)
                    )
                    latex_label.pack(side=tk.LEFT, padx=0)
                    entry = ttk.Entry(sub_frame, width=25)
                    entry.pack(side=tk.LEFT, padx=0)
                    self.sub_sub_input_entries[input_data["var_latex"]] = entry
                    desc_label = ttk.Label(
                        var_frame, text=input_data["description"], font=("Arial", 8)
                    )
                    desc_label.pack(pady=0)

                # Кнопка Рассчитать
                ttk.Button(window, text="Рассчитать", command=calc_sub_sub).pack(pady=1)

            def calc_sub_sub():
                try:
                    v = variant_var.get()
                    sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
                    args = []
                    for input_data in sub_formula["inputs"][1:]:
                        entry = self.sub_sub_input_entries.get(input_data["var_latex"])
                        value_str = entry.get().replace(",", ".") if entry else "0"
                        args.append(float(value_str))
                    result = sub_formula["function"](*args)
                    if target_entry:
                        target_entry.delete(0, tk.END)
                        target_entry.insert(0, str(result))
                    window.destroy()
                except ValueError as e:
                    messagebox.showerror(
                        "Ошибка", str(e) + ". Используйте точку для десятичных."
                    )

            variant_var.trace("w", update_sub_sub_ui)
            variant_var.set(variants[0])
            update_sub_sub_ui(None, None, None)  # Инициализация

    def create_latex_label(self, parent, latex_text, size=(6, 1)):
        try:
            fig, ax = plt.subplots(figsize=size)
            ax.text(0.5, 0.5, f"${latex_text}$", fontsize=12, ha="center", va="center")
            ax.axis("off")
            buffer = BytesIO()
            plt.savefig(
                buffer, format="png", bbox_inches="tight", dpi=150, transparent=True
            )
            buffer.seek(0)
            img = Image.open(buffer)
            photo = ImageTk.PhotoImage(img)
            label = ttk.Label(parent, image=photo)
            label.image = photo
            plt.close(fig)
            return label
        except Exception as e:
            print(f"Ошибка рендеринга LaTeX: {e}")
            return ttk.Label(parent, text=latex_text.replace("$", ""))
