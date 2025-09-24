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
    "Формула (1) - Расход ресурса": "Mрасход = Mпост - Mотгр + Mзапас_нач - Mзапас_кон. Введите Mпост, Mотгр, Mзапас_нач, Mзапас_кон для расчёта расхода ресурса.",
    "Формула (2) - CO2-эквивалент": "E_CO2e = sum(E_i * GWP_i). Введите E_i и выберите газ для расчёта CO2-эквивалента.",
    "Формула (1.9) - Постоянная реакции ЗПП": "k = ln(2)/t1/2. Введите t1/2 для расчёта постоянной реакции.",
    "Формула (1) - Суммарное изменение углерода": "ΔC = ΔCбиомасса + ΔCмертвая + ΔCподстилка + ΔCпочва. Введите ΔCбиомасса, ΔCмертвая, ΔCподстилка, ΔCпочва для суммарного изменения углерода.",
    "Формула (2) - Изменение в биомассе": "ΔCбиомасса = (C_после - C_до) * A. Введите C_после, C_до, A для изменения в биомассе.",
    "Формула (6) - Выбросы от пожаров": "Lпожар = A * MB * Cf * Gef * 10^-3. Введите A, MB, Cf, Gef для выбросов от пожаров.",
    "Формула (7) - CO2 от осушенных почв": "CO2_organic = Aосуш * EF * 44 / 12. Введите Aосуш, EF для CO2 от осушенных почв.",
    "Формула (8) - N2O от осушенных почв": "N2O_organic = Aосуш * EFN_N2O * 44 / 28. Введите Aосуш, EFN_N2O для N2O от осушенных почв.",
    "Формула (9) - CH4 от осушенных почв": "CH4_organic = Aосуш * (1 - Fracditch) * EFland + Aосуш * Fracditch * EFditch. Введите Aосуш, Fracditch, EFland, EFditch для CH4 от осушенных почв.",
    "Формула E_CO2 - Выбросы от карбонатов": "E_CO2 = sum(M_j * EF_j * F_j) / 1000. Введите M_j, выберите карбонат, F_j для выбросов от карбонатов.",
    "Формула (16.10) - Смолистые вещества": "P_см = 0.785 * d^2 * h * q * c * rho * (1 - k) * n. Введите d, h, q, c, rho, k, n для смолистых веществ.",
    "Формула (16.12) - Углеродная пыль": "W_пыль = P_пыль * W_C. Введите P_пыль, W_C для углеродной пыли.",
    "Формула (16.15) - Углеродная пена": "M_пена = P_пена * W_пена / 1000. Введите P_пена, W_пена для углеродной пены.",
    "Формула (126) - N2O от обводнения": "N2Orewetted = (Arewetted * EFN2O-N * 44 / 28) / 1000. Введите Arewetted, EFN2O-N для N2O от обводнения.",
    "Формула (80) - Изменение углерода в минеральных почвах": "ΔCминеральные = Cfert + Clime + Cplant - Cresp + Cerosion. Введите Cfert, Clime, Cplant, Cresp, Cerosion.",
    "Формула (81) - Поступление углерода с удобрениями": "Cfert = sum(Cорг_i * i) + sum(Cмин_j * j). Введите Cорг, i, Cмин, j.",
    "Формула (82) - Поступление углерода с известкованием": "Clime = Lime * 8.75 / 100. Введите Lime.",
    "Формула (83) - Поступление углерода с растительными остатками": "Cplant = Cab + Cun. Введите Cab, Cun.",
    "Формула (84) - Расчёт Cab + Cun": "Cab + Cun = sum(a * Yi + b) * 0.5. Введите a, Yi, b.",
    "Формула (85) - Потери от эрозии": "Cerosion = A * EFerosion. Введите A, EFerosion.",
    "Формула (10) - Изменение углерода в торфяниках": "ΔC_торф = (C_нач - C_кон) * A_торф. Введите C_нач, C_кон, A_торф.",
    "Формула (118) - CH4 от торфяников": "CH4_торф = A_торф * EF_CH4. Введите A_торф, EF_CH4.",
    "Формула (135) - N2O от перевода земель": "N2O_перевод = A_перевод * EF_N2O * 44 / 28. Введите A_перевод, EF_N2O.",
    "Формула (143) - Итоговое изменение углерода": "ΔC_итог = sum(ΔC_i). Введите список ΔC_i через пробел.",
}

CATEGORIES = {
    "Общие": [
        "Формула (1) - Расход ресурса",
        "Формула (2) - CO2-эквивалент",
        "Формула (1.9) - Постоянная реакции ЗПП",
    ],
    "Поглощения (Леса, земли)": [
        "Формула (1) - Суммарное изменение углерода",
        "Формула (2) - Изменение в биомассе",
        "Формула (6) - Выбросы от пожаров",
        "Формула (7) - CO2 от осушенных почв",
        "Формула (8) - N2O от осушенных почв",
        "Формула (9) - CH4 от осушенных почв",
    ],
    "Выбросы (Производство извести)": [
        "Формула E_CO2 - Выбросы от карбонатов",
        "Формула (16.10) - Смолистые вещества",
        "Формула (16.12) - Углеродная пыль",
    ],
    "Выбросы (Сжигание топлива)": [
        "Формула (1.1) - Выбросы CO2 от сжигания топлива",
        "Формула (1.3) - Коэффициент выбросов CO2",
        "Формула (1.4) - Коэффициент выбросов CO2",
        "Формула (1.5) - Коэффициент выбросов CO2",
        "Формула (1.6) - Содержание углерода в коксе",
        "Формула (1.7) - Содержание углерода",
        "Формула (1.8) - Коэффициент окисления",
        "Формула (1.9) - Коэффициент окисления",
    ],
    "Выбросы (Кокс, ТКО)": [
        "Формула (5.1) - Выбросы от кокса",
        "Формула (3.1) - Выбросы от ТКО",
        "Формула (27) - Запас углерода в биомассе",
        "Формула 14.2 - CO2 от осушения",
    ],
    "Выбросы (Алюминий, Химия)": [
        "Формула (16.10) - Смолистые вещества",
        "Формула (16.12) - Углеродная пыль",
        "Формула (16.15) - Углеродная пена",
        "Формула (126) - N2O от обводнения",
    ],
    "Выбросы (Сельское хозяйство)": [
        "Формула (80) - Изменение углерода в минеральных почвах",
        "Формула (81) - Поступление углерода с удобрениями",
        "Формула (82) - Поступление углерода с известкованием",
        "Формула (83) - Поступление углерода с растительными остатками",
        "Формула (84) - Расчёт Cab + Cun",
        "Формула (85) - Потери от эрозии",
    ],
    "Поглощения (Торфяники и земли)": [
        "Формула (10) - Изменение углерода в торфяниках",
        "Формула (118) - CH4 от торфяников",
        "Формула (135) - N2O от перевода земель",
        "Формула (143) - Итоговое изменение углерода",
    ],
}


def calculate_formula(formula_name, inputs):
    if "Формула (1) - Расход ресурса" in formula_name:
        m_post, m_otgr, m_zap_nach, m_zap_kon = map(float, inputs)
        return m_post - m_otgr + m_zap_nach - m_zap_kon
    elif "Формула (2) - CO2-эквивалент" in formula_name:
        e_i = float(inputs[0])
        gas = inputs[1]
        return e_i * GWP.get(gas, 1)
    elif "Формула (1.9) - Постоянная реакции ЗПП" in formula_name:
        t_half = float(inputs[0])
        return math.log(2) / t_half
    elif "Формула (1) - Суммарное изменение углерода" in formula_name:
        dc_biom, dc_mert, dc_podst, dc_poch = map(float, inputs)
        return dc_biom + dc_mert + dc_podst + dc_poch
    elif "Формула (2) - Изменение в биомассе" in formula_name:
        c_posle, c_do, a = map(float, inputs)
        return (c_posle - c_do) * a
    elif "Формула (6) - Выбросы от пожаров" in formula_name:
        a, mb, cf, gef = map(float, inputs)
        return a * mb * cf * gef * 10**-3
    elif "Формула (7) - CO2 от осушенных почв" in formula_name:
        a_osush, ef = map(float, inputs)
        return a_osush * ef * 44 / 12
    elif "Формула (8) - N2O от осушенных почв" in formula_name:
        a_osush, efn_n2o = map(float, inputs)
        return a_osush * efn_n2o * 44 / 28
    elif "Формула (9) - CH4 от осушенных почв" in formula_name:
        a_osush, fracditch, efland, efditch = map(float, inputs)
        return a_osush * (1 - fracditch) * efland + a_osush * fracditch * efditch
    elif "Формула E_CO2 - Выбросы от карбонатов" in formula_name:
        m_j = float(inputs[0])
        carb = inputs[1]
        f_j = float(inputs[2])
        ef_j = EF_CARBONATES_6_1.get(carb, 0.440)
        return (m_j * ef_j * f_j) / 1000
    elif "Формула (1.1) - Выбросы CO2 от сжигания топлива" in formula_name:
        fc, ef, of = map(float, inputs)
        return fc * ef * of
    elif "Формула (1.3) - Коэффициент выбросов CO2" in formula_name:
        w, nc, rho = map(float, inputs)
        return w * nc * rho * 10**-3
    elif "Формула (1.4) - Коэффициент выбросов CO2" in formula_name:
        w, nc, m = map(float, inputs)
        return w * nc * 44.011 * rho * 10**-3 / m
    elif "Формула (1.5) - Коэффициент выбросов CO2" in formula_name:
        w = float(inputs[0])
        return w * 3.664
    elif "Формула (1.6) - Содержание углерода в коксе" in formula_name:
        a, v, s = map(float, inputs)
        return (100 - a - v - s) / 100
    elif "Формула (1.7) - Содержание углерода" in formula_name:
        ef = float(inputs[0])
        return ef / 3.664
    elif "Формула (1.8) - Коэффициент окисления" in formula_name:
        q4 = float(inputs[0])
        return (100 - q4) / 100
    elif "Формула (1.9) - Коэффициент окисления" in formula_name:
        cc_a, cc_f = map(float, inputs)
        return 1 - cc_a / cc_f
    elif "Формула (5.1) - Выбросы от кокса" in formula_name:
        fc, ef, of = map(float, inputs)
        return fc * ef * of
    elif "Формула (3.1) - Выбросы от ТКО" in formula_name:
        m, ef, r = map(float, inputs)
        return m * ef * (1 - r)
    elif "Формула (27) - Запас углерода в биомассе" in formula_name:
        vij, kpij = map(float, inputs)
        return vij * kpij
    elif "Формула 14.2 - CO2 от осушения" in formula_name:
        a, ef = map(float, inputs)
        return a * ef * 44 / 12
    elif "Формула (16.10) - Смолистые вещества" in formula_name:
        d, h, q, c, rho, k, n = map(float, inputs)
        return 0.785 * (d**2) * h * q * c * rho * (1 - k) * n
    elif "Формула (16.12) - Углеродная пыль" in formula_name:
        p_pyl, w_c = map(float, inputs)
        return p_pyl * w_c
    elif "Формула (16.15) - Углеродная пена" in formula_name:
        p_pena, w_pena = map(float, inputs)
        return p_pena * w_pena / 1000
    elif "Формула (126) - N2O от обводнения" in formula_name:
        a_rewetted, efn2o_n = map(float, inputs)
        return (a_rewetted * efn2o_n * 44 / 28) / 1000
    elif "Формула (80) - Изменение углерода в минеральных почвах" in formula_name:
        cfert, clime, cplant, cresp, cerosion = map(float, inputs)
        return cfert + clime + cplant - cresp + cerosion
    elif "Формула (81) - Поступление углерода с удобрениями" in formula_name:
        c_org, i, c_min, j = map(float, inputs)
        return (c_org * i) + (c_min * j)
    elif "Формула (82) - Поступление углерода с известкованием" in formula_name:
        lime = float(inputs[0])
        return lime * 8.75 / 100
    elif (
        "Формула (83) - Поступление углерода с растительными остатками" in formula_name
    ):
        cab, cun = map(float, inputs)
        return cab + cun
    elif "Формула (84) - Расчёт Cab + Cun" in formula_name:
        a, yi, b = map(float, inputs)
        return (a * yi + b) * 0.5
    elif "Формула (85) - Потери от эрозии" in formula_name:
        a, ef_erosion = map(float, inputs)
        return a * ef_erosion
    elif "Формула (10) - Изменение углерода в торфяниках" in formula_name:
        c_nach, c_kon, a_torf = map(float, inputs)
        return (c_nach - c_kon) * a_torf
    elif "Формула (118) - CH4 от торфяников" in formula_name:
        a_torf, ef_ch4 = map(float, inputs)
        return a_torf * ef_ch4
    elif "Формула (135) - N2O от перевода земель" in formula_name:
        a_perevod, ef_n2o = map(float, inputs)
        return a_perevod * ef_n2o * 44 / 28
    elif "Формула (143) - Итоговое изменение углерода" in formula_name:
        dc_i = list(map(float, inputs))
        return sum(dc_i)
    return 0.0
