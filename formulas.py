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

FORMULA_DESCRIPTIONS = {
    "Расход ресурса": "Mрасход = Mпост - Mотгр + Mзапас_нач - Mзапас_кон. Введите Mпост, Mотгр, Mзапас_нач, Mзапас_кон для расчёта расхода ресурса.",
    "CO2-эквивалент": "E_CO2e = sum(E_i * GWP_i). Введите E_i и выберите газ для расчёта CO2-эквивалента.",
    "Постоянная реакции ЗПП": "k = ln(2)/t1/2. Введите t1/2 для расчёта постоянной реакции.",
    "Суммарное изменение углерода": "ΔC = ΔCбиомасса + ΔCмертвая + ΔCподстилка + ΔCпочва. Введите ΔCбиомасса, ΔCмертвая, ΔCподстилка, ΔCпочва для суммарного изменения углерода.",
    "Изменение в биомассе": "ΔCбиомасса = (C_после - C_до) * A. Введите C_после, C_до, A для изменения в биомассе.",
    "Выбросы от пожаров": "Lпожар = A * MB * Cf * Gef * 10^-3. Введите A, MB, Cf, Gef для выбросов от пожаров.",
    "CO2 от осушенных почв": "CO2_organic = Aосуш * EF * 44 / 12. Введите Aосуш, EF для CO2 от осушенных почв.",
    "N2O от осушенных почв": "N2O_organic = Aосуш * EFN_N2O * 44 / 28. Введите Aосуш, EFN_N2O для N2O от осушенных почв.",
    "CH4 от осушенных почв": "CH4_organic = Aосуш * (1 - Fracditch) * EFland + Aосуш * Fracditch * EFditch. Введите Aосуш, Fracditch, EFland, EFditch для CH4 от осушенных почв.",
    "Выбросы от карбонатов": "E_CO2 = sum(M_j * EF_j * F_j) / 1000. Введите M_j, выберите карбонат, F_j для выбросов от карбонатов.",
    "Смолистые вещества": "P_см = 0.785 * d^2 * h * q * c * rho * (1 - k) * n. Введите d, h, q, c, rho, k, n для смолистых веществ.",
    "Углеродная пыль": "W_пыль = P_пыль * W_C. Введите P_пыль, W_C для углеродной пыли.",
    "Углеродная пена": "M_пена = P_пена * W_пена / 1000. Введите P_пена, W_пена для углеродной пены.",
    "N2O от обводнения": "N2Orewetted = (Arewetted * EFN2O-N * 44 / 28) / 1000. Введите Arewetted, EFN2O-N для N2O от обводнения.",
    "Изменение углерода в минеральных почвах": "ΔCминеральные = Cfert + Clime + Cplant - Cresp + Cerosion. Введите Cfert, Clime, Cplant, Cresp, Cerosion.",
    "Поступление углерода с удобрениями": "Cfert = sum(Cорг_i * i) + sum(Cмин_j * j). Введите Cорг, i, Cмин, j.",
    "Поступление углерода с известкованием": "Clime = Lime * 8.75 / 100. Введите Lime.",
    "Поступление углерода с растительными остатками": "Cplant = Cab + Cun. Введите Cab, Cun.",
    "Расчёт Cab + Cun": "Cab + Cun = sum(a * Yi + b) * 0.5. Введите a, Yi, b.",
    "Потери от эрозии": "Cerosion = A * EFerosion. Введите A, EFerosion.",
    "Изменение углерода в торфяниках": "ΔC_торф = (C_нач - C_кон) * A_торф. Введите C_нач, C_кон, A_торф.",
    "CH4 от торфяников": "CH4_торф = A_торф * EF_CH4. Введите A_торф, EF_CH4.",
    "N2O от перевода земель": "N2O_перевод = A_перевод * EF_N2O * 44 / 28. Введите A_перевод, EF_N2O.",
    "Итоговое изменение углерода": "ΔC_итог = sum(ΔC_i). Введите список ΔC_i через пробел.",
    "Коэффициент выбросов CO2 (1.3)": "EFCO2 = W * nC * rho * 10^-3. Введите W, nC, rho.",
    "Коэффициент выбросов CO2 (1.4)": "EFCO2 = W * nC * 44.011 * rho * 10^-3 / M. Введите W, nC, M.",
    "Коэффициент выбросов CO2 (1.5)": "EFCO2 = W * 3.664. Введите W.",
    "Коэффициент окисления (1.8)": "OF = (100 - q4) / 100. Введите q4.",
    "Коэффициент окисления (1.9)": "OF = 1 - CC_A / CC_F. Введите CC_A, CC_F.",
}

CATEGORIES = {
    "Общие": ["Расход ресурса", "CO2-эквивалент", "Постоянная реакции ЗПП"],
    "Поглощения (Леса, земли)": [
        "Суммарное изменение углерода",
        "Изменение в биомассе",
        "Выбросы от пожаров",
        "CO2 от осушенных почв",
        "N2O от осушенных почв",
        "CH4 от осушенных почв",
    ],
    "Выбросы (Производство извести)": [
        "Выбросы от карбонатов",
        "Смолистые вещества",
        "Углеродная пыль",
    ],
    "Выбросы (Сжигание топлива)": [
        "Выбросы CO2 от сжигания топлива",
        "Коэффициент выбросов CO2 (1.3)",
        "Коэффициент выбросов CO2 (1.4)",
        "Коэффициент выбросов CO2 (1.5)",
        "Содержание углерода в коксе",
        "Содержание углерода",
        "Коэффициент окисления (1.8)",
        "Коэффициент окисления (1.9)",
    ],
    "Выбросы (Кокс, ТКО)": [
        "Выбросы от кокса",
        "Выбросы от ТКО",
        "Запас углерода в биомассе",
        "CO2 от осушения",
    ],
    "Выбросы (Алюминий, Химия)": [
        "Смолистые вещества",
        "Углеродная пыль",
        "Углеродная пена",
        "N2O от обводнения",
    ],
    "Выбросы (Сельское хозяйство)": [
        "Изменение углерода в минеральных почвах",
        "Поступление углерода с удобрениями",
        "Поступление углерода с известкованием",
        "Поступление углерода с растительными остатками",
        "Расчёт Cab + Cun",
        "Потери от эрозии",
    ],
    "Поглощения (Торфяники и земли)": [
        "Изменение углерода в торфяниках",
        "CH4 от торфяников",
        "N2O от перевода земель",
        "Итоговое изменение углерода",
    ],
}


def calculate_formula(formula_name, inputs):
    if "Расход ресурса" in formula_name:
        m_post, m_otgr, m_zap_nach, m_zap_kon = map(float, inputs)
        return m_post - m_otgr + m_zap_nach - m_zap_kon
    elif "CO2-эквивалент" in formula_name:
        e_i = float(inputs[0])
        gas = inputs[1]
        return e_i * GWP.get(gas, 1)
    elif "Постоянная реакции ЗПП" in formula_name:
        t_half = float(inputs[0])
        return math.log(2) / t_half
    elif "Суммарное изменение углерода" in formula_name:
        dc_biom, dc_mert, dc_podst, dc_poch = map(float, inputs)
        return dc_biom + dc_mert + dc_podst + dc_poch
    elif "Изменение в биомассе" in formula_name:
        c_posle, c_do, a = map(float, inputs)
        return (c_posle - c_do) * a
    elif "Выбросы от пожаров" in formula_name:
        a, mb, cf, gef = map(float, inputs)
        return a * mb * cf * gef * 10**-3
    elif "CO2 от осушенных почв" in formula_name:
        a_osush, ef = map(float, inputs)
        return a_osush * ef * 44 / 12
    elif "N2O от осушенных почв" in formula_name:
        a_osush, efn_n2o = map(float, inputs)
        return a_osush * efn_n2o * 44 / 28
    elif "CH4 от осушенных почв" in formula_name:
        a_osush, fracditch, efland, efditch = map(float, inputs)
        return a_osush * (1 - fracditch) * efland + a_osush * fracditch * efditch
    elif "Выбросы от карбонатов" in formula_name:
        m_j = float(inputs[0])
        carb = inputs[1]
        f_j = float(inputs[2])
        ef_j = EF_CARBONATES_6_1.get(carb, 0.440)
        return (m_j * ef_j * f_j) / 1000
    elif "Выбросы CO2 от сжигания топлива" in formula_name:
        fc, ef, of = map(float, inputs)
        return fc * ef * of
    elif "Коэффициент выбросов CO2 (1.3)" in formula_name:
        w, nc, rho = map(float, inputs)
        return w * nc * rho * 10**-3
    elif "Коэффициент выбросов CO2 (1.4)" in formula_name:
        w, nc, m = map(float, inputs)
        return w * nc * 44.011 * rho * 10**-3 / m
    elif "Коэффициент выбросов CO2 (1.5)" in formula_name:
        w = float(inputs[0])
        return w * 3.664
    elif "Содержание углерода в коксе" in formula_name:
        a, v, s = map(float, inputs)
        return (100 - a - v - s) / 100
    elif "Содержание углерода" in formula_name:
        ef = float(inputs[0])
        return ef / 3.664
    elif "Коэффициент окисления (1.8)" in formula_name:
        q4 = float(inputs[0])
        return (100 - q4) / 100
    elif "Коэффициент окисления (1.9)" in formula_name:
        cc_a, cc_f = map(float, inputs)
        return 1 - cc_a / cc_f
    elif "Выбросы от кокса" in formula_name:
        fc, ef, of = map(float, inputs)
        return fc * ef * of
    elif "Выбросы от ТКО" in formula_name:
        m, ef, r = map(float, inputs)
        return m * ef * (1 - r)
    elif "Запас углерода в биомассе" in formula_name:
        vij, kpij = map(float, inputs)
        return vij * kpij
    elif "CO2 от осушения" in formula_name:
        a, ef = map(float, inputs)
        return a * ef * 44 / 12
    elif "Смолистые вещества" in formula_name:
        d, h, q, c, rho, k, n = map(float, inputs)
        return 0.785 * (d**2) * h * q * c * rho * (1 - k) * n
    elif "Углеродная пыль" in formula_name:
        p_pyl, w_c = map(float, inputs)
        return p_pyl * w_c
    elif "Углеродная пена" in formula_name:
        p_pena, w_pena = map(float, inputs)
        return p_pena * w_pena / 1000
    elif "N2O от обводнения" in formula_name:
        a_rewetted, efn2o_n = map(float, inputs)
        return (a_rewetted * efn2o_n * 44 / 28) / 1000
    elif "Изменение углерода в минеральных почвах" in formula_name:
        cfert, clime, cplant, cresp, cerosion = map(float, inputs)
        return cfert + clime + cplant - cresp + cerosion
    elif "Поступление углерода с удобрениями" in formula_name:
        c_org, i, c_min, j = map(float, inputs)
        return (c_org * i) + (c_min * j)
    elif "Поступление углерода с известкованием" in formula_name:
        lime = float(inputs[0])
        return lime * 8.75 / 100
    elif "Поступление углерода с растительными остатками" in formula_name:
        cab, cun = map(float, inputs)
        return cab + cun
    elif "Расчёт Cab + Cun" in formula_name:
        a, yi, b = map(float, inputs)
        return (a * yi + b) * 0.5
    elif "Потери от эрозии" in formula_name:
        a, ef_erosion = map(float, inputs)
        return a * ef_erosion
    elif "Изменение углерода в торфяниках" in formula_name:
        c_nach, c_kon, a_torf = map(float, inputs)
        return (c_nach - c_kon) * a_torf
    elif "CH4 от торфяников" in formula_name:
        a_torf, ef_ch4 = map(float, inputs)
        return a_torf * ef_ch4
    elif "N2O от перевода земель" in formula_name:
        a_perevod, ef_n2o = map(float, inputs)
        return a_perevod * ef_n2o * 44 / 28
    elif "Итоговое изменение углерода" in formula_name:
        dc_i = list(map(float, inputs))
        return sum(dc_i)
    return 0.0
