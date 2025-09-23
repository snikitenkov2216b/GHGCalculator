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

CATEGORIES = {
    "Общие": [
        "Формула (1) - Расход ресурса (Mрасход = Mпост - Mотгр + Mзапас_нач - Mзапас_кон)",
        "Формула (2) - CO2-эквивалент (E_CO2e = sum(E_i * GWP_i))",
    ],
    "Поглощения (Леса, земли)": [
        "Формула (1) - Суммарное изменение углерода (ΔC = ΔCбиомасса + ΔCмертвая + ΔCподстилка + ΔCпочва)",
        "Формула (2) - Изменение в биомассе (ΔCбиомасса = (C_после - C_до) * A)",
        "Формула (6) - Выбросы от пожаров (Lпожар = A * MB * Cf * Gef * 10^-3)",
        "Формула (7) - CO2 от осушенных почв (CO2_organic = Aосуш * EF * 44 / 12)",
        "Формула (8) - N2O от осушенных почв (N2O_organic = Aосуш * EFN_N2O * 44 / 28)",
        "Формула (9) - CH4 от осушенных почв (CH4_organic = Aосуш * (1 - Fracditch) * EFland + Aосуш * Fracditch * EFditch)",
    ],
    # Другие группы добавим позже
}


def calculate_formula(formula_name, inputs):
    if "Формула (1)" in formula_name and "Расход" in formula_name:
        m_post, m_otgr, m_zap_nach, m_zap_kon = map(float, inputs)
        return m_post - m_otgr + m_zap_nach - m_zap_kon
    elif "Формула (2)" in formula_name and "CO2" in formula_name:
        e_i = float(inputs[0])
        gas = inputs[1]
        return e_i * GWP.get(gas, 1)
    elif "Формула (1)" in formula_name and "Суммарное" in formula_name:
        dc_biom, dc_mert, dc_podst, dc_poch = map(float, inputs)
        return dc_biom + dc_mert + dc_podst + dc_poch
    elif "Формула (2)" in formula_name and "биомассе" in formula_name:
        c_posle, c_do, a = map(float, inputs)
        return (c_posle - c_do) * a
    elif "Формула (6)" in formula_name:
        a, mb, cf, gef = map(float, inputs)
        return a * mb * cf * gef * 10**-3
    elif "Формула (7)" in formula_name:
        a_osush, ef = map(float, inputs)
        return a_osush * ef * 44 / 12
    elif "Формула (8)" in formula_name:
        a_osush, efn_n2o = map(float, inputs)
        return a_osush * efn_n2o * 44 / 28
    elif "Формула (9)" in formula_name:
        a_osush, fracditch, efland, efditch = map(float, inputs)
        return a_osush * (1 - fracditch) * efland + a_osush * fracditch * efditch
    return 0.0
