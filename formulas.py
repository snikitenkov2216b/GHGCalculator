# formulas.py - Логика расчётов формул из PDF

# Импорты
import numpy as np  # Для сумм и массивов

from data_tables import TABLE_1_1, TABLE_1_2  # Импорт таблиц


def calculate_1_1(fc_list, ef_list, of_list):
    """
    Расчёт формулы (1.1): E_CO2,y = sum_{j=1}^n (FC_j,y * EF_CO2,j,y * OF_j,y)
    - fc_list: список расходов топлива (FC_j,y)
    - ef_list: список коэффициентов выбросов (EF_CO2,j,y, т CO2 / т у.т.)
    - of_list: список коэффициентов окисления (OF_j,y)
    Возвращает: E_CO2,y в т CO2
    """
    try:
        return sum(
            fc * ef * of_val for fc, ef, of_val in zip(fc_list, ef_list, of_list)
        )
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.1: {e}")


def calculate_1_2a(fc_prime, k):
    """
    Расчёт формулы (1.2а): FC_j,y = FC'_j,y * k_j,y
    - fc_prime: FC'_j,y (расход в натуральном выражении)
    - k: k_j,y (коэффициент перевода в т у.т.)
    Возвращает: FC_j,y в т у.т.
    """
    try:
        return fc_prime * k
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.2а: {e}")


def calculate_1_2b(fc_prime, ncv):
    """
    Расчёт формулы (1.2б): FC_j,y = FC'_j,y * NCV_j,y * 10^{-3}
    - fc_prime: FC'_j,y (расход в натуральном выражении)
    - ncv: NCV_j,y (низшая теплота сгорания)
    Возвращает: FC_j,y в ТДж
    """
    try:
        return fc_prime * ncv * 0.001
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.2б: {e}")


def calculate_1_3(w_list, n_c_list, rho):
    """
    Расчёт формулы (1.3): EF_CO2,j,y = sum (W_i,j,y * n_C,i) * rho * 10^{-2}
    - w_list: список W_i,j,y (объемная доля компонентов)
    - n_c_list: список n_C,i (атомы углерода)
    - rho: rho_CO2 (плотность CO2)
    Возвращает: EF_CO2,j,y в т CO2/тыс. м3
    """
    try:
        sum_wn = sum(w * n_c for w, n_c in zip(w_list, n_c_list))
        return sum_wn * rho * 0.01
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.3: {e}")


def calculate_1_4(w_list, n_c_list, m_list, rho):
    """
    Расчёт формулы (1.4): EF_CO2,j,y = sum (W_i,j,y * n_C,i * 44.011 / M_i) * rho * 10^{-2}
    - w_list: список W_i,j,y (массовая доля)
    - n_c_list: список n_C,i
    - m_list: список M_i (молярная масса)
    - rho: rho_j,y (плотность топлива)
    Возвращает: EF_CO2,j,y в т CO2/тыс. м3
    """
    try:
        sum_term = sum(
            w * n_c * 44.011 / m for w, n_c, m in zip(w_list, n_c_list, m_list)
        )
        return sum_term * rho * 0.01
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.4: {e}")


def calculate_1_5(w_c):
    """
    Расчёт формулы (1.5): EF_CO2,j,y = W_C,j,y * 3.664
    - w_c: W_C,j,y (содержание углерода)
    Возвращает: EF_CO2,j,y в т CO2/т
    """
    try:
        return w_c * 3.664
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.5: {e}")


def calculate_1_6(a, v, s):
    """
    Расчёт формулы (1.6): W_C,кокс,y = (100 - (A_кокс,y + V_кокс,y + S_кокс,y)) / 100
    - a: A_кокс,y (зола)
    - v: V_кокс,y (летучие)
    - s: S_кокс,y (сера)
    Возвращает: W_C,кокс,y в т C/т
    """
    try:
        return (100 - a - v - s) / 100
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.6: {e}")


def calculate_1_7(ef):
    """
    Расчёт формулы (1.7): W_C,j,y = EF_CO2,j,y / 3.664
    - ef: EF_CO2,j,y
    Возвращает: W_C,j,y в т C/т
    """
    try:
        return ef / 3.664
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.7: {e}")


def calculate_1_8(q4):
    """
    Расчёт формулы (1.8): OF_j,y = (100 - q4) / 100
    - q4: q4 (потери тепла от недожога)
    Возвращает: OF_j,y в долях
    """
    try:
        return (100 - q4) / 100
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.8: {e}")


def calculate_1_9(cc_a, cc_f):
    """
    Расчёт формулы (1.9): OF_j,y = 1 - CC_A,y / CC_F,y
    - cc_a: CC_A,y (углерод в золе)
    - cc_f: CC_F,y (углерод в топливе)
    Возвращает: OF_j,y в долях
    """
    try:
        if cc_f == 0:
            raise ValueError("Деление на ноль: CC_F,y не может быть 0")
        return 1 - cc_a / cc_f
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.9: {e}")


def calculate_1_10(a, v):
    """
    Расчёт формулы (1.10): W_C,кокс.уголь,y = (100 - A_кокс.уголь,y - 0.47 * V_кокс.уголь,y) / 100
    - a: A_кокс.уголь,y (зола в углях)
    - v: V_кокс.уголь,y (летучие в углях)
    Возвращает: W_C,кокс.уголь,y в т C/т
    """
    try:
        return (100 - a - 0.47 * v) / 100
    except (TypeError, ValueError) as e:
        raise ValueError(f"Ошибка в расчёте формулы 1.10: {e}")


# Словарь категорий и формул (расширяемо, с inputs для UI)
CATEGORIES = {
    "1. Стационарное сжигание топлива": {
        "(1.1)": {
            "description": "Выбросы CO2 от стационарного сжигания топлива за период y, т CO2",
            "latex": r"E_{\text{CO}_2,y} = \sum_{j=1}^n (FC_{j,y} \cdot EF_{\text{CO}_2,j,y} \cdot OF_{j,y})",
            "function": calculate_1_1,
            "inputs": [
                {
                    "var_latex": r"E_{\text{CO}_2,y}",
                    "description": "Выбросы CO2 от стационарного сжигания топлива за период y, т CO2",
                    "output": True,
                },
                {
                    "var_latex": r"FC_{j,y}",
                    "description": "Расход топлива j за период y, тыс. м3, т, т у.т. или ТДж",
                },
                {
                    "var_latex": r"EF_{\text{CO}_2,j,y}",
                    "description": "Коэффициент выбросов CO2 от сжигания топлива j за период y, т CO2/ед.",
                },
                {
                    "var_latex": r"OF_{j,y}",
                    "description": "Коэффициент окисления топлива j, доля",
                },
                {
                    "var_latex": r"j",
                    "description": "Вид топлива, используемого для сжигания",
                },
                {
                    "var_latex": r"n",
                    "description": "Количество видов топлива, используемых за период y",
                },
            ],
        },
        "(1.2а)": {
            "description": "расход топлива в энергетическом эквиваленте (т у.т.)",
            "latex": r"FC_{j,y} = FC'_{j,y} \cdot k_{j,y}",
            "function": calculate_1_2a,
            "inputs": [
                {
                    "var_latex": r"FC_{j,y}",
                    "description": "Расход топлива j в энергетическом эквиваленте за период y, т у.т.",
                    "output": True,
                },
                {
                    "var_latex": r"FC'_{j,y}",
                    "description": "Расход топлива j в натуральном выражении за период y, т или тыс. м3",
                },
                {
                    "var_latex": r"k_{j,y}",
                    "description": "Коэффициент перевода в тонны условного топлива, т у.т./т, т у.т./тыс. м3",
                },
            ],
        },
        "(1.2б)": {
            "description": "расход топлива в энергетическом эквиваленте (ТДж)",
            "latex": r"FC_{j,y} = FC'_{j,y} \cdot NCV_{j,y} \cdot 10^{-3}",
            "function": calculate_1_2b,
            "inputs": [
                {
                    "var_latex": r"FC_{j,y}",
                    "description": "Расход топлива j в энергетическом эквиваленте за период y, ТДж",
                    "output": True,
                },
                {
                    "var_latex": r"FC'_{j,y}",
                    "description": "Расход топлива j в натуральном выражении за период y, т или тыс. м3",
                },
                {
                    "var_latex": r"NCV_{j,y}",
                    "description": "Низшая теплота сгорания топлива j за период y, МДж/кг, МДж/м3",
                },
            ],
        },
        "(1.3)": {
            "description": "коэффициент выбросов CO2 для газообразного топлива (объемная доля)",
            "latex": r"EF_{\text{CO}_2,j,y} = \sum_{i=1}^n (W_{i,j,y} \cdot n_{C,i}) \cdot \rho_{\text{CO}_2} \cdot 10^{-2}",
            "function": calculate_1_3,
            "inputs": [
                {
                    "var_latex": r"EF_{\text{CO}_2,j,y}",
                    "description": "Коэффициент выбросов CO2 от сжигания газообразного топлива j за период y, т CO2/тыс. м3",
                    "output": True,
                },
                {
                    "var_latex": r"W_{i,j,y}",
                    "description": "Объемная доля (молярная доля) i-компонента газообразного топлива j за период y, % об. (% мол.)",
                },
                {
                    "var_latex": r"n_{C,i}",
                    "description": "Количество атомов углерода в молекуле i-компонента газообразного топлива",
                },
                {
                    "var_latex": r"\rho_{\text{CO}_2}",
                    "description": "Плотность диоксида углерода (CO2), кг/м3 (принимается по таблице 1.2)",
                },
            ],
        },
        "(1.4)": {
            "description": "коэффициент выбросов CO2 для газообразного топлива (массовая доля)",
            "latex": r"EF_{\text{CO}_2,j,y} = \sum_{i=1}^n (\frac{W_{i,j,y} \cdot n_{C,i} \cdot 44.011}{M_i}) \cdot \rho_{j,y} \cdot 10^{-2}",
            "function": calculate_1_4,
            "inputs": [
                {
                    "var_latex": r"EF_{\text{CO}_2,j,y}",
                    "description": "Коэффициент выбросов CO2 от сжигания газообразного топлива j за период y, т CO2/тыс. м3",
                    "output": True,
                },
                {
                    "var_latex": r"W_{i,j,y}",
                    "description": "Массовая доля i-компонента газообразного топлива j за период y, % мас.",
                },
                {
                    "var_latex": r"n_{C,i}",
                    "description": "Количество молей углерода на моль i-компонента газообразного топлива",
                },
                {
                    "var_latex": r"\rho_{j,y}",
                    "description": "Плотность газообразного топлива j за период y, кг/м3",
                },
                {
                    "var_latex": r"M_i",
                    "description": "Молярная масса i-компонента газообразного топлива, г/моль",
                },
            ],
        },
        "(1.5)": {
            "description": "коэффициент выбросов CO2 для твердого и жидкого топлива",
            "latex": r"EF_{\text{CO}_2,j,y} = W_{C,j,y} \cdot 3.664",
            "function": calculate_1_5,
            "inputs": [
                {
                    "var_latex": r"EF_{\text{CO}_2,j,y}",
                    "description": "Коэффициент выбросов CO2 от сжигания j-топлива за период y, т CO2/т",
                    "output": True,
                },
                {
                    "var_latex": r"W_{C,j,y}",
                    "description": "Содержание углерода в j-топливе за период y, т C/т",
                },
            ],
        },
        "(1.6)": {
            "description": "содержание углерода в коксе",
            "latex": r"W_{C,\text{кокс},y} = [\frac{100 - (A_{\text{кокс},y} + V_{\text{кокс},y} + S_{\text{кокс},y})}{100}]",
            "function": calculate_1_6,
            "inputs": [
                {
                    "var_latex": r"W_{C,\text{кокс},y}",
                    "description": "Содержание углерода в коксе за период y, т C/т",
                    "output": True,
                },
                {
                    "var_latex": r"A_{\text{кокс},y}",
                    "description": "Содержание золы в коксе за период y, %",
                },
                {
                    "var_latex": r"V_{\text{кокс},y}",
                    "description": "Содержание летучих в коксе за период y, %",
                },
                {
                    "var_latex": r"S_{\text{кокс},y}",
                    "description": "Содержание серы в коксе за период y, %",
                },
            ],
        },
        "(1.7)": {
            "description": "содержание углерода в топливе",
            "latex": r"W_{C,j,y} = \frac{EF_{CO_2,j,y}}{3.664}",
            "function": calculate_1_7,
            "inputs": [
                {
                    "var_latex": r"W_{C,j,y}",
                    "description": "Содержание углерода в j-топливе за период y, т C/т, т C/тыс. м3",
                    "output": True,
                },
                {
                    "var_latex": r"EF_{\text{CO}_2,j,y}",
                    "description": "Коэффициент выбросов CO2 от сжигания топлива j за период y, т CO2/т, т CO2/тыс. м3",
                },
            ],
        },
        "(1.8)": {
            "description": "коэффициент окисления твердого топлива (на основе недожога)",
            "latex": r"OF_{j,y} = \frac{(100 - q_4)}{100}",
            "function": calculate_1_8,
            "inputs": [
                {
                    "var_latex": r"OF_{j,y}",
                    "description": "Коэффициент окисления твердого топлива j, доля",
                    "output": True,
                },
                {
                    "var_latex": r"q4",
                    "description": "Потери тепла вследствие механической неполноты сгорания топлива, %",
                },
            ],
        },
        "(1.9)": {
            "description": "коэффициент окисления твердого топлива (на основе углерода в золе)",
            "latex": r"OF_{j,y} = 1 - \frac{CC_{A,y}}{CC_{F,y}}",
            "function": calculate_1_9,
            "inputs": [
                {
                    "var_latex": r"OF_{j,y}",
                    "description": "Коэффициент окисления твердого топлива j, доля",
                    "output": True,
                },
                {
                    "var_latex": r"CC_{A,y}",
                    "description": "Содержание углерода в золе и шлаке, образованными за период y, т",
                },
                {
                    "var_latex": r"CC_{F,y}",
                    "description": "Содержание углерода в твердом топливе, израсходованном за период y, т",
                },
            ],
        },
        "(1.10)": {
            "description": "содержание углерода в коксующихся углях",
            "latex": r"W_{C,\text{кокс.уголь},y} = (100 - A_{\text{кокс.уголь},y} - 0.47 * V_{\text{кокс.уголь},y}) / 100",
            "function": calculate_1_10,
            "inputs": [
                {
                    "var_latex": r"W_{C,\text{кокс.уголь},y}",
                    "description": "Содержание углерода в коксующихся углях за период y, т C/т",
                    "output": True,
                },
                {
                    "var_latex": r"A_{\text{кокс.уголь},y}",
                    "description": "Содержание золы в коксующихся углях за период y, %",
                },
                {
                    "var_latex": r"V_{\text{кокс.уголь},y}",
                    "description": "Содержание летучих в коксующихся углях за период y, %",
                },
            ],
        },
    },
    # Добавьте другие категории здесь для будущего расширения
}
