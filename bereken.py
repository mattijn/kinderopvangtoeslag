import pandas as pd


def p2f(x):
    return float(x.replace(",", ".").strip("%")) / 100


def werkuren2opvanguren(uren_ouder_week):
    # returns uren opvang / maand
    uren_opvang_jaar = uren_ouder_week * 1.4 * 52
    return uren_opvang_jaar // 12 + (uren_opvang_jaar % 12 > 0)


def toeslag_bijbetaling(s_kind, pcts):
    if s_kind[1] > s_kind[3]:
        toeslag_kind = s_kind[0] * s_kind[3] * pcts[2]
        bijbetalen_kind = (s_kind[0] * s_kind[3] * (1 - pcts[2])) + (
            s_kind[0] * s_kind[4]
        )
    else:
        toeslag_kind = s_kind[0] * s_kind[1] * pcts[2]
        bijbetalen_kind = s_kind[0] * s_kind[3] * (1 - pcts[2])
    return toeslag_kind, bijbetalen_kind


tarief_opties = [
    (8.47, "KDV 52 weken"),
    (10.17, "KDV 40 weken"),
    (9.45, "BSO 52 weken"),
    (10.93, "BSO 40 weken"),
]

uur_opties = [43, 65, 101, 132]

type_opvang = ["bso", "dagopvang", "gastouder"]

url_toeslagen = "https://www.rijksoverheid.nl/onderwerpen/kinderopvangtoeslag/bedragen-kinderopvangtoeslag-2022"
tables = pd.read_html(
    url_toeslagen, decimal=",", thousands=".", converters={2: p2f, 3: p2f}
)
df_pcts = tables[0]
df_pcts.iloc[:, 0:2] = df_pcts.iloc[:, 0:2].apply(pd.to_numeric, errors="coerce")

limit_config = {"bso": 7.27, "dagopvang": 8.46, "gastouder": 6.49}
df_limit = pd.DataFrame().from_dict(
    limit_config, orient="index", columns=["max_opvang"]
)


def bereken_toeslag_bijbetaling(
    ouder_1_inkomen,
    ouder_2_inkomen,
    minste_uren_ouder_week,
    kind_1_uren_maand,
    kind_2_uren_maand,
    kind_3_uren_maand,
    kind_1_uur_tarief,
    kind_2_uur_tarief,
    kind_3_uur_tarief,
    kind_1_type_opvang,
    kind_2_type_opvang,
    kind_3_type_opvang,
    selected_kinderen,
    df_pcts,
    df_limit,
):

    opvanguren = werkuren2opvanguren(minste_uren_ouder_week)
    print(f"max-uren/maand {opvanguren}")

    toetsingsinkomen = ouder_1_inkomen + ouder_2_inkomen
    # netto_ouder2 = int(ouder_2_inkomen / 12 * 0.8416)

    # definieer dataframe met kinder-data
    kinder_config = [
        {
            "uren_per_maand": kind_1_uren_maand,
            "tarief_per_uur": kind_1_uur_tarief,
            "soort_opvang": kind_1_type_opvang,
        },
        {
            "uren_per_maand": kind_2_uren_maand,
            "tarief_per_uur": kind_2_uur_tarief,
            "soort_opvang": kind_2_type_opvang,
        },
        {
            "uren_per_maand": kind_3_uren_maand,
            "tarief_per_uur": kind_3_uur_tarief,
            "soort_opvang": kind_3_type_opvang,
        },
    ]
    df_kinds = pd.DataFrame().from_dict(kinder_config)

    # bepaal de percentage van toepassing obv van toetsingsinkomen
    idx = (
        df_pcts["Toetsingsinkomen (gezamenlijk) tot en met"]
        .gt(toetsingsinkomen)
        .idxmax()
    )
    pcts = df_pcts.loc[idx]

    # combineer gegevens kinderen tarieven met maximale tarieven
    df_kinds_limit = pd.merge(
        df_kinds, df_limit, left_on="soort_opvang", right_index=True
    )
    df_kinds_limit["bijbetalen_per_uur"] = (
        df_kinds_limit.tarief_per_uur - df_kinds_limit.max_opvang
    )

    # bepaal 1e kind en bereken toeslag
    idx_kind1 = df_kinds_limit["uren_per_maand"].argmax()
    s_kind1 = df_kinds_limit.iloc[idx_kind1]
    toeslag_kind1, bijbetalen_kind1 = toeslag_bijbetaling(s_kind1, pcts)
    df_kinds_limit.at[idx_kind1, "toeslag_per_maand"] = toeslag_kind1
    df_kinds_limit.at[idx_kind1, "bijbetalen_per_maand"] = bijbetalen_kind1

    # bepaal de toeslagen overige kinderen
    df_next_kinds = df_kinds_limit.loc[~df_kinds_limit.index.isin([idx_kind1])]
    for idx_kind_n, s_kind_n in df_next_kinds.iterrows():
        toeslag_kind_n, bijbetalen_kind_n = toeslag_bijbetaling(s_kind_n, pcts)
        df_kinds_limit.at[idx_kind_n, "toeslag_per_maand"] = toeslag_kind_n
        df_kinds_limit.at[idx_kind_n, "bijbetalen_per_maand"] = bijbetalen_kind_n

    df_kinds_limit.index = selected_kinderen
    df_kinds_limit.loc["totalen"] = df_kinds_limit[
        ["toeslag_per_maand", "bijbetalen_per_maand"]
    ].sum()
    df_kinds_limit = df_kinds_limit.round(2)
    df_kinds_limit = df_kinds_limit.fillna("")
    # print(netto_ouder2)
    # print(netto_ouder2 - df_kinds_limit.at['totalen', 'bijbetalen_per_maand'])
    return df_kinds_limit.T.astype(str)
