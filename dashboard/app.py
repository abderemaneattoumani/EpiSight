#  EpiSight — Dashboard Épidémiologique Interactif
#  Auteur : Abderemane Attoumani

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Configuration page
st.set_page_config(
    page_title="EpiSight — Dashboard Épidémiologique",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-setup pour déploiement cloud streamlit
sys.path.append(str(Path(__file__).parent.parent / "src"))
BASE_PATH = Path(__file__).parent.parent

try:
    from data_loader import pipeline_complet
    if not (BASE_PATH / "data" / "processed" / "indicateurs_tests.csv").exists():
        with st.spinner("⏳ Téléchargement et préparation des données (2-3 min)..."):
            pipeline_complet(BASE_PATH)
        st.rerun()
except Exception:
    pass

#  Injection CSS (dark theme + glassmorphism)
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* ── Variables de couleur ── */
:root {
    --primary:   #e65c5c;
    --secondary: #3b82f6;
    --accent:    #f97316;
    --success:   #10b981;
    --bg-900:    #0a0e1a;
    --bg-800:    #131a2e;
    --bg-700:    #1e293b;
    --glass:     rgba(30, 41, 59, 0.45);
    --border:    rgba(255, 255, 255, 0.08);
    --text-muted: #94a3b8;
}

/* ── Reset global ── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Fond principal ── */
.stApp {
    background-color: var(--bg-900) !important;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(230,92,92,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(59,130,246,0.05) 0%, transparent 50%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg-800) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ── Header sticky ── */
[data-testid="stHeader"] {
    background: rgba(10, 14, 26, 0.85) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ── Métriques (KPI cards) ── */
[data-testid="stMetric"] {
    background: var(--glass) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.4rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 32px rgba(230, 92, 92, 0.15) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* ── Onglets ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--glass) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--primary) !important;
    color: white !important;
    box-shadow: 0 0 16px rgba(230, 92, 92, 0.35) !important;
}

/* ── Titres ── */
h1, h2, h3, h4 {
    color: #f8fafc !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Selectbox et date input ── */
[data-testid="stSelectbox"] > div,
[data-testid="stDateInput"] > div {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Texte général ── */
p, span, label, div {
    color: #cbd5e1;
}

/* ── Séparateur ── */
hr {
    border-color: var(--border) !important;
}

/* ── Alertes et info boxes ── */
[data-testid="stAlert"] {
    background: var(--glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(8px) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    background: var(--glass) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-900); }
::-webkit-scrollbar-thumb {
    background: rgba(230, 92, 92, 0.4);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--primary) !important; }

/* ── Bouton ── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary), #f97316) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    box-shadow: 0 0 16px rgba(230, 92, 92, 0.3) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 24px rgba(230, 92, 92, 0.5) !important;
}
</style>
""", unsafe_allow_html=True)


#  Chargement des données
@st.cache_data
def charger_donnees():
    base = Path(__file__).parent.parent / "data" / "processed"
    tests_nat = pd.read_csv(base / "indicateurs_tests.csv",  parse_dates=['jour'])
    hosp_nat  = pd.read_csv(base / "indicateurs_hosp.csv",   parse_dates=['jour'])
    vacc_nat  = pd.read_csv(base / "indicateurs_vacc.csv",   parse_dates=['jour'])
    tests_dep = pd.read_csv(base / "tests_par_dep.csv",      parse_dates=['jour'])
    vagues    = pd.read_csv(base / "vagues_detectees.csv",   parse_dates=['debut','fin'])
    tests_dep['dep'] = tests_dep['dep'].astype(str).str.zfill(2)
    return tests_nat, hosp_nat, vacc_nat, tests_dep, vagues

tests_nat, hosp_nat, vacc_nat, tests_dep, vagues = charger_donnees()

# Thème Plotly
PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(13,17,30,0)",
    plot_bgcolor="rgba(13,17,30,0)",
    font=dict(family="Space Grotesk", color="#94a3b8"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
)

#  Sidebar
with st.sidebar:
    # Logo / titre
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
        <div style="width:36px; height:36px; border-radius:8px;
                    background:rgba(230,92,92,0.2); display:flex;
                    align-items:center; justify-content:center;
                    border:1px solid rgba(230,92,92,0.3);">
            🦠
        </div>
        <span style="font-size:1.3rem; font-weight:700;
                     color:#f8fafc; font-family:'Space Grotesk',sans-serif;">
            EpiSight
        </span>
    </div>
    <p style="font-size:0.75rem; color:#64748b; margin-bottom:2px;
              font-family:'Space Grotesk',sans-serif;">
        Dashboard Épidémiologique
    </p>
                <p style="font-size:0.75rem; color:#64748b; margin-bottom:20px;
              font-family:'Space Grotesk',sans-serif;">
        France COVID-19
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ Filtres")

    date_min = tests_nat['jour'].min().date()
    date_max = tests_nat['jour'].max().date()
    periode = st.date_input("📅 Période", value=(date_min, date_max),
                             min_value=date_min, max_value=date_max)

    deps = sorted(tests_dep['dep'].unique().tolist())
    dep_selectionne = st.selectbox("🗺️ Département",
                                    options=deps,
                                    index=deps.index('75') if '75' in deps else 0)

    st.markdown("---")
    st.markdown("### 🌊 Vagues détectées")
    noms_vagues = [
        "2e vague — Automne 2020",
        "3e vague — Printemps 2021",
        "Delta — Été 2021",
        "Omicron — Jan. 2022",
        "BA.2 — Mars 2022",
        "BA.5 — Juillet 2022",
        "Automne 2022",
        "Hiver 2022",
    ]
    for i, row in vagues.iterrows():
        nom = noms_vagues[i] if i < len(noms_vagues) else f"Vague {i+1}"
        st.markdown(
            f"<div style='font-size:0.78rem; color:#94a3b8; "
            f"padding:4px 0; border-left:2px solid #e65c5c; "
            f"padding-left:8px; margin-bottom:4px;'>"
            f"<b style='color:#f8fafc;'>{nom}</b></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem; color:#475569; line-height:1.6;'>"
        "📊 Source : <a href='https://www.data.gouv.fr' "
        "style='color:#e65c5c;'>data.gouv.fr</a><br>"
        "🗓️ Période : mai 2020 → juin 2023<br>"
        "💻 <a href='https://github.com/abderemaneattoumani/EpiSight' "
        "style='color:#e65c5c;'>GitHub</a>"
        "</div>",
        unsafe_allow_html=True
    )

#  Filtre temporel
if len(periode) == 2:
    debut, fin = pd.Timestamp(periode[0]), pd.Timestamp(periode[1])
else:
    debut, fin = tests_nat['jour'].min(), tests_nat['jour'].max()

t = tests_nat[(tests_nat['jour'] >= debut) & (tests_nat['jour'] <= fin)].copy()
h = hosp_nat[(hosp_nat['jour']  >= debut) & (hosp_nat['jour']  <= fin)].copy()
v = vacc_nat[(vacc_nat['jour']  >= debut) & (vacc_nat['jour']  <= fin)].copy()

#  En-tête
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem 0;">
    <h1 style="font-size:3rem; font-weight:900; letter-spacing:-1px;
               background: linear-gradient(135deg, #e65c5c, #f97316, #fbbf24);
               -webkit-background-clip: text;
               -webkit-text-fill-color: transparent;
               background-clip: text;
               text-shadow: none;
               margin-bottom: 0.5rem;">
        🦠 EpiSight
    </h1>
    <p style="color:#64748b; font-size:1rem; font-weight:400;
              font-family:'Space Grotesk',sans-serif; margin:0;">
        Dashboard Épidémiologique Interactif — France COVID-19
        &nbsp;·&nbsp; Données Santé Publique France
    </p>
</div>
""", unsafe_allow_html=True)

#  KPI Cards
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🦠 Cas positifs",
              f"{int(t['cas_positifs'].sum()):,}".replace(",", " "))
with col2:
    st.metric("📈 Pic MM7",
              f"{int(t['cas_mm7'].max()):,}".replace(",", " "))
with col3:
    st.metric("🏥 Pic hospitalisations",
              f"{int(h['hospitalises'].max()) if len(h) > 0 else 0:,}".replace(",", " "))
with col4:
    st.metric("🚨 Pic réanimation",
              f"{int(h['reanimation'].max()) if len(h) > 0 else 0:,}".replace(",", " "))
with col5:
    couv = v['couv_complet_pct'].max() if len(v) > 0 else 0
    st.metric("💉 Couverture vaccinale", f"{couv:.1f}%")

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:rgba(255,255,255,0.06);'>",
            unsafe_allow_html=True)

#  Onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Évolution temporelle",
    "🏥 Hospitalisations",
    "💉 Vaccination",
    "🗺️ Analyse départementale",
    "🔮 Prédiction IA"
])

# ONGLET 1 — Évolution temporelle
with tab1:
    st.markdown("#### Évolution de l'épidémie — France entière")

    fig_cas = go.Figure()
    for _, vague in vagues.iterrows():
        if vague['debut'] >= debut and vague['fin'] <= fin:
            fig_cas.add_vrect(x0=vague['debut'], x1=vague['fin'],
                              fillcolor="rgba(230,92,92,0.07)",
                              layer="below", line_width=0)

    fig_cas.add_trace(go.Scatter(
        x=t['jour'], y=t['cas_positifs'], mode='lines',
        line=dict(color='rgba(230,92,92,0.2)', width=1),
        name='Données brutes',
        hovertemplate='%{x|%d/%m/%Y}<br>Brut : %{y:,.0f}<extra></extra>'
    ))
    fig_cas.add_trace(go.Scatter(
        x=t['jour'], y=t['cas_mm7'], mode='lines',
        line=dict(color='#e65c5c', width=2.5),
        name='Moyenne mobile 7j',
        hovertemplate='%{x|%d/%m/%Y}<br>MM7 : %{y:,.0f}<extra></extra>'
    ))
    fig_cas.update_layout(
        **PLOTLY_THEME,
        title=dict(text="Cas positifs quotidiens (zones = vagues épidémiques)",
                   font=dict(size=14, color="#94a3b8")),
        xaxis_title=None, yaxis_title="Cas / jour",
        hovermode='x unified', height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))
    )
    st.plotly_chart(fig_cas, width='stretch')

    fig_tp = go.Figure()
    fig_tp.add_trace(go.Scatter(
        x=t['jour'], y=t['tp_mm7'], mode='lines',
        fill='tozeroy',
        line=dict(color='#f97316', width=2),
        fillcolor='rgba(249,115,22,0.12)',
        name='Taux positivité MM7',
        hovertemplate='%{x|%d/%m/%Y}<br>Taux : %{y:.1f}%<extra></extra>'
    ))
    fig_tp.add_hline(y=5, line_dash="dash", line_color="rgba(230,92,92,0.6)",
                     annotation_text="Seuil alerte 5%",
                     annotation_font_color="#e65c5c",
                     annotation_position="bottom right")
    fig_tp.update_layout(
        **PLOTLY_THEME,
        title=dict(text="Taux de positivité — Moyenne mobile 7 jours",
                   font=dict(size=14, color="#94a3b8")),
        xaxis_title=None, yaxis_title="Taux (%)",
        height=340, hovermode='x unified',
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))
    )
    st.plotly_chart(fig_tp, width='stretch')

# ONGLET 2 — Hospitalisations
with tab2:
    st.markdown("#### Pression hospitalière")

    col_h1, col_h2 = st.columns(2)

    with col_h1:
        fig_hosp = go.Figure()
        fig_hosp.add_trace(go.Scatter(
            x=h['jour'], y=h['hosp_mm7'], mode='lines',
            fill='tozeroy',
            line=dict(color='#3b82f6', width=2),
            fillcolor='rgba(59,130,246,0.12)',
            name='Hospitalisés MM7',
            hovertemplate='%{x|%d/%m/%Y}<br>Hospitalisés : %{y:,.0f}<extra></extra>'
        ))
        fig_hosp.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Patients hospitalisés (MM7)",
                       font=dict(size=13, color="#94a3b8")),
            height=340, hovermode='x unified',
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_hosp, width='stretch')

    with col_h2:
        fig_rea = go.Figure()
        fig_rea.add_trace(go.Scatter(
            x=h['jour'], y=h['rea_mm7'], mode='lines',
            fill='tozeroy',
            line=dict(color='#a855f7', width=2),
            fillcolor='rgba(168,85,247,0.12)',
            name='Réanimation MM7',
            hovertemplate='%{x|%d/%m/%Y}<br>Réanimation : %{y:,.0f}<extra></extra>'
        ))
        fig_rea.add_hline(y=5000, line_dash="dash",
                          line_color="rgba(230,92,92,0.5)",
                          annotation_text="Capacité normale (~5 000)",
                          annotation_font_color="#e65c5c",
                          annotation_position="bottom right")
        fig_rea.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Patients en réanimation (MM7)",
                       font=dict(size=13, color="#94a3b8")),
            height=340, hovermode='x unified',
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_rea, width='stretch')

    if 'deces_mm7' in h.columns:
        fig_dc = go.Figure()
        fig_dc.add_trace(go.Scatter(
            x=h['jour'], y=h['deces_mm7'], mode='lines',
            fill='tozeroy',
            line=dict(color='#64748b', width=2),
            fillcolor='rgba(100,116,139,0.12)',
            name='Décès MM7',
            hovertemplate='%{x|%d/%m/%Y}<br>Décès : %{y:.1f}<extra></extra>'
        ))
        fig_dc.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Décès quotidiens — Moyenne mobile 7 jours",
                       font=dict(size=13, color="#94a3b8")),
            xaxis_title=None, yaxis_title="Décès / jour",
            height=300, hovermode='x unified',
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_dc, width='stretch')

# ONGLET 3 — Vaccination
with tab3:
    st.markdown("#### Campagne de vaccination nationale")

    fig_vacc = go.Figure()
    couleurs_vacc = ['#10b981', '#34d399', '#6ee7b7']
    labels_vacc   = ['1ère dose', 'Schéma complet', 'Rappel']
    cols_vacc     = ['couv_dose1_pct', 'couv_complet_pct', 'couv_rappel_pct']

    for col, label, couleur in zip(cols_vacc, labels_vacc, couleurs_vacc):
        fig_vacc.add_trace(go.Scatter(
            x=v['jour'], y=v[col], mode='lines',
            line=dict(color=couleur, width=2.5),
            name=label,
            hovertemplate=f'%{{x|%d/%m/%Y}}<br>{label} : %{{y:.1f}}%<extra></extra>'
        ))

    fig_vacc.add_hline(y=70, line_dash="dot",
                       line_color="rgba(255,255,255,0.2)",
                       annotation_text="Objectif immunité collective 70%",
                       annotation_font_color="#94a3b8",
                       annotation_position="bottom right")
    fig_vacc.update_layout(
        **PLOTLY_THEME,
        title=dict(text="Couverture vaccinale — Population française (%)",
                   font=dict(size=14, color="#94a3b8")),
        xaxis_title=None, yaxis_title="% population",
        height=400, hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))
    )
    st.plotly_chart(fig_vacc, width='stretch')

    if 'doses_jour' in v.columns:
        fig_doses = go.Figure()
        fig_doses.add_trace(go.Bar(
            x=v['jour'], y=v['doses_jour'],
            marker_color='rgba(16,185,129,0.5)',
            marker_line_color='rgba(16,185,129,0.8)',
            marker_line_width=0.5,
            name='Doses quotidiennes',
            hovertemplate='%{x|%d/%m/%Y}<br>Doses : %{y:,}<extra></extra>'
        ))
        fig_doses.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Doses administrées par jour",
                       font=dict(size=13, color="#94a3b8")),
            height=280, hovermode='x unified',
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_doses, width='stretch')

# ONGLET 4 — Analyse départementale
with tab4:
    st.markdown(f"#### Analyse locale — Département **{dep_selectionne}**")

    dep_data = tests_dep[
        (tests_dep['dep'] == dep_selectionne) &
        (tests_dep['jour'] >= debut) &
        (tests_dep['jour'] <= fin)
    ].sort_values('jour').copy()

    if len(dep_data) > 0:
        dep_data['cas_mm7_dep'] = dep_data['cas_positifs'].rolling(7, min_periods=1).mean()

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.metric("Cas totaux",
                      f"{int(dep_data['cas_positifs'].sum()):,}".replace(",", " "))
        with col_d2:
            st.metric("Taux incidence max",
                      f"{dep_data['taux_incidence'].max():.0f} /100k hab.")
        with col_d3:
            st.metric("Taux positivité moyen",
                      f"{dep_data['taux_positivite'].mean():.1f}%")

        fig_dep = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            subplot_titles=('Taux d\'incidence (cas/100k hab., 7j glissants)',
                            'Taux de positivité (%)'),
            vertical_spacing=0.12
        )
        fig_dep.update_layout(
            **PLOTLY_THEME,
            height=520, hovermode='x unified', showlegend=False
        )

        fig_dep.add_trace(go.Scatter(
            x=dep_data['jour'], y=dep_data['taux_incidence'],
            mode='lines', fill='tozeroy',
            line=dict(color='#e65c5c', width=2),
            fillcolor='rgba(230,92,92,0.1)',
            hovertemplate='%{x|%d/%m/%Y}<br>TI : %{y:.1f}/100k<extra></extra>'
        ), row=1, col=1)

        for seuil, label, couleur in [
            (50,  "Alerte",          "rgba(249,115,22,0.5)"),
            (150, "Alerte renforcée","rgba(230,92,92,0.5)"),
            (250, "Urgence",         "rgba(220,38,38,0.7)")
        ]:
            fig_dep.add_hline(y=seuil, line_dash="dash",
                              line_color=couleur, opacity=0.6,
                              annotation_text=label,
                              annotation_font_color=couleur,
                              row=1, col=1)

        fig_dep.add_trace(go.Scatter(
            x=dep_data['jour'], y=dep_data['taux_positivite'],
            mode='lines', fill='tozeroy',
            line=dict(color='#f97316', width=2),
            fillcolor='rgba(249,115,22,0.1)',
            hovertemplate='%{x|%d/%m/%Y}<br>TP : %{y:.1f}%<extra></extra>'
        ), row=2, col=1)

        fig_dep.add_hline(y=5, line_dash="dash",
                          line_color="rgba(230,92,92,0.5)",
                          annotation_text="Seuil 5%",
                          annotation_font_color="#e65c5c",
                          row=2, col=1)

        st.plotly_chart(fig_dep, width='stretch')
    else:
        st.warning(f"Aucune donnée pour le département {dep_selectionne} sur cette période.")

# ONGLET 5 — Prédiction IA
with tab5:
    st.markdown("#### 🔮 Prédiction IA — 7 prochains jours")

    st.info("""
    **Modèle : Prophet (Meta/Facebook)**  
    Entraîné sur 1 141 jours de données Covid · Détecte tendances, saisonnalités hebdo et annuelles · Intervalle de confiance à 95%
    """)

    predictions_path = (Path(__file__).parent.parent
                        / "data" / "processed" / "predictions_7j.csv")

    if predictions_path.exists():
        pred = pd.read_csv(predictions_path, parse_dates=['date'])

        # Tableau
        st.markdown("##### Prévisions quotidiennes")
        pred_affich = pred.copy()
        pred_affich.columns = ['Date', 'Prédiction (cas/j)',
                                'Borne basse (95%)', 'Borne haute (95%)']
        pred_affich['Date'] = pred_affich['Date'].dt.strftime('%A %d %b %Y')
        for col in ['Prédiction (cas/j)', 'Borne basse (95%)', 'Borne haute (95%)']:
            pred_affich[col] = pred_affich[col].apply(
                lambda x: f"{int(x):,}".replace(",", " "))
        st.dataframe(pred_affich, use_container_width=False, hide_index=True)

        # Graphique prédiction
        derniers_30j = tests_nat.sort_values('jour').tail(30)
        date_limite  = tests_nat['jour'].max()

        fig_pred = go.Figure()

        # Historique
        fig_pred.add_trace(go.Scatter(
            x=derniers_30j['jour'], y=derniers_30j['cas_mm7'],
            mode='lines', line=dict(color='#e65c5c', width=2.5),
            name='Historique (MM7)',
            hovertemplate='%{x|%d/%m/%Y}<br>Réel : %{y:,.0f}<extra></extra>'
        ))

        # Intervalle de confiance
        fig_pred.add_trace(go.Scatter(
            x=pd.concat([pred['date'], pred['date'].iloc[::-1]]),
            y=pd.concat([pred['borne_haute'], pred['borne_basse'].iloc[::-1]]),
            fill='toself',
            fillcolor='rgba(59,130,246,0.12)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Intervalle confiance 95%',
            hoverinfo='skip'
        ))

        # Prédiction centrale
        fig_pred.add_trace(go.Scatter(
            x=pred['date'], y=pred['prediction'],
            mode='lines+markers',
            line=dict(color='#3b82f6', width=2.5, dash='dash'),
            marker=dict(size=8, color='#3b82f6',
                        line=dict(color='#0a0e1a', width=2)),
            name='Prédiction Prophet',
            hovertemplate='%{x|%d/%m/%Y}<br>Prédit : %{y:,.0f}<extra></extra>'
        ))

        # Ligne séparation réel / prédit
        fig_pred.add_trace(go.Scatter(
            x=[date_limite, date_limite],
            y=[0, tests_nat['cas_mm7'].max()],
            mode='lines',
            line=dict(color='rgba(255,255,255,0.2)', width=1.5, dash='dot'),
            name='Fin données réelles',
            hoverinfo='skip'
        ))

        fig_pred.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Prédiction des cas positifs — 7 prochains jours",
                       font=dict(size=14, color="#94a3b8")),
            xaxis_title=None, yaxis_title="Cas / jour (MM7)",
            height=420, hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"))
        )
        st.plotly_chart(fig_pred, width='stretch')

        st.warning("""
        ⚠️ **Limite du modèle** : Prophet prolonge les tendances passées.
        Il ne peut anticiper un nouveau variant ou un changement comportemental brutal.
        Ces prédictions sont à caractère **démonstratif** — données jusqu'en juin 2023.
        """)
    else:
        st.error("Fichier predictions_7j.csv introuvable.")
        st.code("python src/predictions.py", language="bash")
        st.markdown("Lance cette commande dans ton terminal pour générer les prédictions.")

#  FOOTER
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="
    text-align:center;
    padding: 1.2rem;
    background: rgba(30,41,59,0.3);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.8rem;
    color: #475569;
    line-height: 2;
">
    <b style='color:#94a3b8;'>EpiSight v1.0</b>
    &nbsp;·&nbsp; Données : Santé Publique France / data.gouv.fr
    &nbsp;·&nbsp; Abderemane Attoumani — Analyse Data IA
    &nbsp;·&nbsp;
    <a href='https://github.com/abderemaneattoumani/EpiSight'
       style='color:#e65c5c; text-decoration:none;'>
       GitHub ↗
    </a>
    <br>
    <span style='font-size:0.72rem; color:#334155;'>
        Données à caractère démonstratif · période mai 2020 → juin 2023
    </span>
</div>
""", unsafe_allow_html=True)
