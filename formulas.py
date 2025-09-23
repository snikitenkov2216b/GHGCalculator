# formulas.py - Данные и логика расчётов формул из PDF
import math

GWP = {
    "CO2": 1,
    "CH4": 28,
    "N2O": 265,
    "CHF3": 11600,
    "CF4": 6630,
    "C2F6": 11100,
    "SF6": 23500,
}

# Таблицы EF добавим в следующих шагах

CATEGORIES = {
    "Общие": [
        "Формула (1) - Расход ресурса (Mрасход = Mпост - Mотгр + Mзапас_нач - Mзапас_кон)",
        "Формула (2) - CO2-эквивалент (E_CO2e = sum(E_i * GWP_i))",
    ],
    # Другие группы добавим позже
}


def calculate_formula(formula_name, inputs):
    if "Формула (1)" in formula_name:
        m_post, m_otgr, m_zap_nach, m_zap_kon = map(float, inputs)
        return m_post - m_otgr + m_zap_nach - m_zap_kon
    elif "Формула (2)" in formula_name:
        # Упрощённо для одного газа; для sum - расширим позже
        e_i = float(inputs[0])
        gas = inputs[1]  # Из combobox
        return e_i * GWP.get(gas, 1)
    return 0.0
