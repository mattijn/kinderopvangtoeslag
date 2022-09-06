import streamlit as st
from bereken import *

with st.container():
    st.write("Informatie van de ouders")

    ouder_1_inkomen = st.slider("Inkomen ouder 1 (jaar)", 0, 60000, 53457)
    ouder_2_inkomen = st.slider("Inkomen ouder 2 (jaar)", 0, 60000, 26023)

    minste_uren_ouder_week = st.selectbox(
        "Minst aantal uren ouder (week)", options=[40, 32, 24, 16], index=1
    )

with st.container():
    st.write("Informatie van de kinderen")
    (
        kind1_col1,
        kind1_col2,
        kind1_col3,
    ) = st.columns(3)
    with kind1_col1:
        kind_1_uren_maand = st.number_input(
            "Kind 1 aantal uren (maand)", min_value=0, max_value=150, value=44
        )

    with kind1_col2:
        kind_1_uur_tarief = st.selectbox(
            "Kind 1 tarief/soort contract (uur)",
            options=tarief_opties,
            index=4,
        )

    with kind1_col3:
        kind_1_type_opvang = st.selectbox(
            "Kind 1 type opvang",
            options=type_opvang,
            index=0,
        )

    (
        kind2_col1,
        kind2_col2,
        kind2_col3,
    ) = st.columns(3)
    with kind2_col1:
        kind_2_uren_maand = st.number_input(
            "Kind 2 aantal uren (maand)", min_value=0, max_value=150, value=44
        )
    with kind2_col2:
        kind_2_uur_tarief = st.selectbox(
            "Kind 2 tarief/soort contract (uur)",
            options=tarief_opties,
            index=4,
        )

    with kind2_col3:
        kind_2_type_opvang = st.selectbox(
            "Kind 2 type opvang",
            options=type_opvang,
            index=0,
        )

    (
        kind3_col1,
        kind3_col2,
        kind3_col3,
    ) = st.columns(3)
    with kind3_col1:
        kind_3_uren_maand = st.number_input(
            "Kind 3 aantal uren (maand)", min_value=0, max_value=150, value=88
        )
    with kind3_col2:
        kind_3_uur_tarief = st.selectbox(
            "Kind 3 tarief/soort contract (uur)",
            options=tarief_opties,
            index=2,
        )

    with kind3_col3:
        kind_3_type_opvang = st.selectbox(
            "Kind 3 type opvang",
            options=type_opvang,
            index=1,
        )


selected_kinderen = st.multiselect(
    "Welke kinderen doen mee in de berekening?",
    ["kind1", "kind2", "kind3"],
    ["kind1", "kind2", "kind3"],
)

st.write("Aantal kinderen:", len(selected_kinderen))

st.dataframe(
    bereken_toeslag_bijbetaling(
        ouder_1_inkomen,
        ouder_2_inkomen,
        minste_uren_ouder_week,
        kind_1_uren_maand,
        kind_2_uren_maand,
        kind_3_uren_maand,
        kind_1_uur_tarief[0],
        kind_2_uur_tarief[0],
        kind_3_uur_tarief[0],
        kind_1_type_opvang,
        kind_2_type_opvang,
        kind_3_type_opvang,
        selected_kinderen,
        df_pcts,
        df_limit,
    )
)
