# ui.py - Интерфейс приложения

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageTk
from formulas import CATEGORIES
from data_tables import TABLE_1_1, TABLE_1_2


class Tooltip:
    """Класс для всплывающих подсказок"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y = event.x_root + 25, event.y_root + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(
            self.tooltip,
            text=self.text,
            background="#f0f0f0",
            relief="solid",
            borderwidth=1,
            padding=2,
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class GHGCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Система расчёта выбросов парниковых газов")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        # Стиль
        style = ttk.Style()
        style.theme_use("arc")
        style.configure(
            "TEntry",
            fieldbackground="#ffffff",
            foreground="black",
            font=("Arial", 10),
            padding=5,
        )
        style.map("TEntry", fieldbackground=[("focus", "#e6f7ff")])
        style.configure(
            "TCombobox",
            fieldbackground="#ffffff",
            foreground="black",
            font=("Arial", 10),
            padding=5,
            arrowcolor="black",
        )
        style.map("TCombobox", fieldbackground=[("focus", "#e6f7ff")])
        style.configure(
            "TButton",
            background="#ffffff",
            foreground="black",
            font=("Arial", 10, "bold"),
            padding=5,
            borderwidth=1,
            relief="solid",
        )
        style.map("TButton", background=[("active", "#f0f0f0")])
        style.configure(
            "TLabel", font=("Arial", 12, "bold"), foreground="#333333", padding=5
        )

        # Меню
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Выход", command=root.quit)
        menubar.add_cascade(label="Файл", menu=filemenu)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(
            label="О программе",
            command=lambda: messagebox.showinfo(
                "О программе", "Система для расчета выбросов ПГ по Приказу №371"
            ),
        )
        menubar.add_cascade(label="Помощь", menu=helpmenu)
        root.config(menu=menubar)

        # Главный фрейм
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Выбор категории
        self.category_label = ttk.Label(self.main_frame, text="Выберите категорию:")
        self.category_label.pack(pady=5)
        self.category_combo = ttk.Combobox(
            self.main_frame, values=list(CATEGORIES.keys()), width=50
        )
        self.category_combo.pack(pady=5)
        self.category_combo.bind("<<ComboboxSelected>>", self.load_formulas)

        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=10)

        # Выбор формулы
        self.formula_label = ttk.Label(self.main_frame, text="Выберите формулу:")
        self.formula_label.pack(pady=5)
        self.formula_combo = ttk.Combobox(self.main_frame, width=50)
        self.formula_combo.pack(pady=5)
        self.formula_combo.bind("<<ComboboxSelected>>", self.load_formula_ui)

        ttk.Separator(self.main_frame, orient="horizontal").pack(fill=tk.X, pady=10)

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
        latex_label.pack(pady=10)

        desc_label = ttk.Label(
            self.content_frame, text=formula["description"], font=("Arial", 10)
        )
        desc_label.pack()

        ttk.Separator(self.content_frame, orient="horizontal").pack(fill=tk.X, pady=10)

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
        calc_btn.pack(pady=10)

        self.result_label = ttk.Label(
            self.content_frame, text="Результат: ", font=("Arial", 12, "bold")
        )
        self.result_label.pack()

    def load_1_1_ui(self):
        # Canvas для скролла
        canvas = tk.Canvas(self.content_frame, height=300)
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
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        add_btn = ttk.Button(
            self.content_frame,
            text="Добавить топливо",
            command=lambda: self.add_fuel_entry(fuel_frame),
        )
        add_btn.pack(pady=5)

        self.add_fuel_entry(fuel_frame)

    def add_fuel_entry(self, fuel_frame):
        frame = ttk.Frame(fuel_frame, borderwidth=1, relief="solid", padding=10)
        frame.pack(fill=tk.X, pady=5)

        # Топливо
        fuel_label = ttk.Label(frame, text="Тип топлива:")
        fuel_label.grid(row=0, column=0, padx=5, pady=5)
        fuel_combo = ttk.Combobox(frame, values=list(TABLE_1_1.keys()), width=50)
        fuel_combo.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        fuel_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.update_fuel_params(frame)
        )
        Tooltip(fuel_combo, "Выберите топливо из таблицы 1.1")

        # FC
        fc_label = self.create_latex_label(frame, r"FC_{j,y}", (1.5, 0.5))
        fc_label.grid(row=1, column=0, padx=5, pady=5)
        fc_entry = ttk.Entry(frame, width=15)
        fc_entry.grid(row=1, column=1, padx=5, pady=5)
        Tooltip(fc_entry, "Расход топлива (т у.т. или ТДж)")
        fc_btn = ttk.Button(
            frame, text="Расчёт FC", command=lambda: self.open_sub_calc("FC", fc_entry)
        )
        fc_btn.grid(row=1, column=2, padx=5, pady=5)

        # EF
        ef_label = self.create_latex_label(frame, r"EF_{\text{CO}_2,j,y}", (2, 0.5))
        ef_label.grid(row=2, column=0, padx=5, pady=5)
        ef_entry = ttk.Entry(frame, width=15)
        ef_entry.grid(row=2, column=1, padx=5, pady=5)
        Tooltip(ef_entry, "Коэффициент выбросов (авто из таблицы)")
        ef_btn = ttk.Button(
            frame, text="Расчёт EF", command=lambda: self.open_sub_calc("EF", ef_entry)
        )
        ef_btn.grid(row=2, column=2, padx=5, pady=5)

        # OF
        of_label = self.create_latex_label(frame, r"OF_{j,y}", (1.5, 0.5))
        of_label.grid(row=3, column=0, padx=5, pady=5)
        of_entry = ttk.Entry(frame, width=15)
        of_entry.insert(0, "1.0")
        of_entry.grid(row=3, column=1, padx=5, pady=5)
        Tooltip(of_entry, "Коэффициент окисления (1.0 по умолчанию для gas/liquid)")
        of_btn = ttk.Button(
            frame, text="Расчёт OF", command=lambda: self.open_sub_calc("OF", of_entry)
        )
        of_btn.grid(row=3, column=2, padx=5, pady=5)

        remove_btn = ttk.Button(frame, text="Удалить", command=frame.destroy)
        remove_btn.grid(row=0, column=3, rowspan=4, padx=5, pady=5)

        self.fuel_entries.append(
            {
                "fuel_combo": fuel_combo,
                "fc_entry": fc_entry,
                "ef_entry": ef_entry,
                "of_entry": of_entry,
                "frame": frame,
            }
        )

    def update_fuel_params(self, frame):
        for entry in self.fuel_entries:
            if entry["frame"] == frame:
                fuel = entry["fuel_combo"].get()
                if fuel in TABLE_1_1:
                    data = TABLE_1_1[fuel]
                    ef_entry = entry["ef_entry"]
                    ef_entry.delete(0, tk.END)
                    ef_entry.insert(0, str(data["EF"]))

                    of_entry = entry["of_entry"]
                    of_entry.delete(0, tk.END)
                    if data["type"] in ["gas", "liquid"]:
                        of_entry.insert(0, "1.0")
                        of_entry.config(state="readonly")
                    else:
                        of_entry.insert(0, "0.95")  # Default для solid, редактируемый
                        of_entry.config(state="normal")
                break

    def load_generic_ui(self, formula):
        for input_data in formula["inputs"][1:]:  # Пропустить output
            var_frame = ttk.Frame(self.content_frame)
            var_frame.pack(fill=tk.X, pady=5)
            latex_label = self.create_latex_label(
                var_frame, input_data["var_latex"], (2, 0.5)
            )
            latex_label.pack(side=tk.LEFT, padx=5)
            desc_label = ttk.Label(
                var_frame, text=input_data["description"], font=("Arial", 10)
            )
            desc_label.pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(var_frame, width=20)
            entry.pack(side=tk.RIGHT, padx=5)
            Tooltip(entry, input_data["description"])
            self.input_entries[input_data["var_latex"]] = entry

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.input_entries = {}
        self.fuel_entries = []

    def calculate(self, formula_key, formula):
        try:
            if formula_key == "(1.1)":
                fc_list = [float(e["fc_entry"].get()) for e in self.fuel_entries]
                ef_list = [float(e["ef_entry"].get()) for e in self.fuel_entries]
                of_list = [float(e["of_entry"].get()) for e in self.fuel_entries]
                args = [fc_list, ef_list, of_list]
            else:
                args = []
                for input_data in formula["inputs"][1:]:
                    value_str = self.input_entries[input_data["var_latex"]].get()
                    if "," in value_str:  # Список
                        args.append([float(x.strip()) for x in value_str.split(",")])
                    else:
                        args.append(float(value_str))

            result = formula["function"](*args)
            output_desc = formula["inputs"][0]["description"]
            self.result_label.config(text=f"Результат ({output_desc}): {result:.4f}")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

    def open_sub_calc(self, sub_type, target_entry):
        window = tk.Toplevel(self.root)
        window.title(f"Расчёт {sub_type}")
        window.geometry("500x400")

        variant_var = tk.StringVar()
        variants = {
            "FC": ["(1.2а)", "(1.2б)"],
            "EF": ["(1.3)", "(1.4)", "(1.5)"],
            "OF": ["(1.8)", "(1.9)"],
        }[sub_type]
        for v in variants:
            ttk.Radiobutton(window, text=v, variable=variant_var, value=v).pack(
                anchor=tk.W
            )

        self.sub_input_entries = {}

        def update_sub_ui(event):
            v = variant_var.get()
            for widget in window.winfo_children()[len(variants) :]:
                widget.destroy()
            sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
            for input_data in sub_formula["inputs"][1:]:
                var_frame = ttk.Frame(window)
                var_frame.pack(fill=tk.X, pady=5)
                latex_label = self.create_latex_label(
                    var_frame, input_data["var_latex"], (2, 0.5)
                )
                latex_label.pack(side=tk.LEFT, padx=5)
                desc_label = ttk.Label(
                    var_frame, text=input_data["description"], font=("Arial", 10)
                )
                desc_label.pack(side=tk.LEFT, padx=5)
                entry = ttk.Entry(var_frame, width=30)
                entry.pack(side=tk.RIGHT, padx=5)
                Tooltip(entry, input_data["description"])
                self.sub_input_entries[input_data["var_latex"]] = entry

            if sub_type == "EF":
                w_c_btn = ttk.Button(
                    window,
                    text="Расчёт W_C",
                    command=lambda: self.open_sub_sub_calc(
                        "W_C", self.sub_input_entries.get(r"W_{C,j,y}")
                    ),
                )
                w_c_btn.pack(pady=5)

        variant_var.trace("w", update_sub_ui)
        variant_var.set(variants[0])

        def calc_sub():
            try:
                v = variant_var.get()
                sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
                args = []
                for input_data in sub_formula["inputs"][1:]:
                    value_str = self.sub_input_entries[input_data["var_latex"]].get()
                    if "," in value_str:
                        args.append([float(x.strip()) for x in value_str.split(",")])
                    else:
                        args.append(float(value_str))
                result = sub_formula["function"](*args)
                target_entry.delete(0, tk.END)
                target_entry.insert(0, str(result))
                window.destroy()
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))

        ttk.Button(window, text="Рассчитать", command=calc_sub).pack(pady=10)

    def open_sub_sub_calc(self, sub_sub_type, target_entry):
        if sub_sub_type == "W_C":
            window = tk.Toplevel(self.root)
            window.title("Расчёт W_C")
            window.geometry("500x300")

            variant_var = tk.StringVar()
            variants = ["(1.6)", "(1.7)", "(1.10)"]
            for v in variants:
                ttk.Radiobutton(window, text=v, variable=variant_var, value=v).pack(
                    anchor=tk.W
                )

            self.sub_sub_input_entries = {}

            def update_sub_sub_ui(event):
                v = variant_var.get()
                for widget in window.winfo_children()[len(variants) :]:
                    widget.destroy()
                sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
                for input_data in sub_formula["inputs"][1:]:
                    var_frame = ttk.Frame(window)
                    var_frame.pack(fill=tk.X, pady=5)
                    latex_label = self.create_latex_label(
                        var_frame, input_data["var_latex"], (2, 0.5)
                    )
                    latex_label.pack(side=tk.LEFT, padx=5)
                    desc_label = ttk.Label(
                        var_frame, text=input_data["description"], font=("Arial", 10)
                    )
                    desc_label.pack(side=tk.LEFT, padx=5)
                    entry = ttk.Entry(var_frame, width=30)
                    entry.pack(side=tk.RIGHT, padx=5)
                    Tooltip(entry, input_data["description"])
                    self.sub_sub_input_entries[input_data["var_latex"]] = entry

            variant_var.trace("w", update_sub_sub_ui)
            variant_var.set(variants[0])

            def calc_sub_sub():
                try:
                    v = variant_var.get()
                    sub_formula = CATEGORIES["1. Стационарное сжигание топлива"][v]
                    args = []
                    for input_data in sub_formula["inputs"][1:]:
                        value_str = (
                            self.sub_sub_input_entries.get(
                                input_data["var_latex"], ttk.Entry(window)
                            ).get()
                            or "0"
                        )
                        args.append(float(value_str))
                    result = sub_formula["function"](*args)
                    if target_entry:
                        target_entry.delete(0, tk.END)
                        target_entry.insert(0, str(result))
                    window.destroy()
                except ValueError as e:
                    messagebox.showerror("Ошибка", str(e))

            ttk.Button(window, text="Рассчитать", command=calc_sub_sub).pack(pady=10)

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
