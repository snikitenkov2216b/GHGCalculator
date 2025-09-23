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

EF_CARBONATES_6_1 = {
    "CaCO3": 0.440,
    "MgCO3": 0.522,
    "CaMg(CO3)2": 0.477,
    "FeCO3": 0.380,
}

EF_CARBONATES_8_1 = {
    "Na2CO3": 0.415,
    "NaHCO3": 0.524,
    "BaCO3": 0.223,
    "K2CO3": 0.318,
    "Li2CO3": 0.596,
    "SrCO3": 0.284,
}

CATEGORIES = {
    "Общие": [
        "Формула (1) - Расход ресурса (Mрасход = Mпост - Mотгр + Mзапас_нач - Mзапас_кон)",
        "Формула (2) - CO2-эквивалент (E_CO2e = sum(E_i * GWP_i))",
        "Формула (1.9) - Постоянная реакции ЗПП (k = ln(2)/t1/2)",
    ],
    "Поглощения (Леса, земли)": [
        "Формула (1) - Суммарное изменение углерода (ΔC = ΔCбиомасса + ΔCмертвая + ΔCподстилка + ΔCпочва)",
        "Формула (2) - Изменение в биомассе (ΔCбиомасса = (C_после - C_до) * A)",
        "Формула (6) - Выбросы от пожаров (Lпожар = A * MB * Cf * Gef * 10^-3)",
        "Формула (7) - CO2 от осушенных почв (CO2_organic = Aосуш * EF * 44 / 12)",
        "Формула (8) - N2O от осушенных почв (N2O_organic = Aосуш * EFN_N2O * 44 / 28)",
        "Формула (9) - CH4 от осушенных почв (CH4_organic = Aосуш * (1 - Fracditch) * EFland + Aосуш * Fracditch * EFditch)",
    ],
    "Выбросы (Производство извести)": [
        "Формула E_CO2 - Выбросы от карбонатов (E_CO2 = sum(M_j * EF_j * F_j) / 1000)",
        "Формула (16.10) - Смолистые вещества (P_см = ...)",
        "Формула (16.12) - Углеродная пыль (W_пыль = ...)",
    ],
    "Выбросы (Сжигание топлива)": [
        "Формула (1.1) - Выбросы CO2 от сжигания топлива (E_CO2 = sum(FC * EF * OF))",
        "Формула (1.3) - Коэффициент выбросов CO2 (EFCO2 = sum(W * nC * rho * 10^-3))",
        "Формула (1.4) - Коэффициент выбросов CO2 (EFCO2 = sum(W * nC * 44.011 * rho * 10^-3 / M))",
        "Формула (1.5) - Коэффициент выбросов CO2 (EFCO2 = W * 3.664)",
        "Формула (1.6) - Содержание углерода в коксе (W_C = (100 - A - V - S) / 100)",
        "Формула (1.7) - Содержание углерода (W_C = EFCO2 / 3.664)",
        "Формула (1.8) - Коэффициент окисления (OF = (100 - q4) / 100)",
        "Формула (1.9) - Коэффициент окисления (OF = 1 - CC_A / CC_F)",
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
    elif "Формула (1.9)" in formula_name and "ЗПП" in formula_name:
        t_half = float(inputs[0])
        return math.log(2) / t_half
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
    elif "Формула E_CO2" in formula_name:
        m_j = float(inputs[0])
        carb = inputs[1]
        f_j = float(inputs[2])
        ef_j = EF_CARBONATES_6_1.get(carb, 0.440)
        return (m_j * ef_j * f_j) / 1000
    elif "Формула (1.1)" in formula_name:
        # Упрощённо для одного j; для sum - inputs as list
        fc, ef, of = map(float, inputs)
        return fc * ef * of
    elif "Формула (1.3)" in formula_name:
        w, nc, rho = map(float, inputs)
        return w * nc * rho * 10**-3
    elif "Формула (1.4)" in formula_name:
        w, nc, m = map(float, inputs)
        return w * nc * 44.011 * rho * 10**-3 / m
    elif "Формула (1.5)" in formula_name:
        w = float(inputs[0])
        return w * 3.664
    elif "Формула (1.6)" in formula_name:
        a, v, s = map(float, inputs)
        return (100 - a - v - s) / 100
    elif "Формула (1.7)" in formula_name:
        ef = float(inputs[0])
        return ef / 3.664
    elif "Формула (1.8)" in formula_name:
        q4 = float(inputs[0])
        return (100 - q4) / 100
    elif "Формула (1.9)" in formula_name and "окисления" in formula_name:
        cc_a, cc_f = map(float, inputs)
        return 1 - cc_a / cc_f
    return 0.0
