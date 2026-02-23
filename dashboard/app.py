#  EpiSight — Dashboard Épidémiologique Interactif
#  Auteur  : Abderemane Attoumani
#  Données : Santé Publique France / data.gouv.fr

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="EpiSight | Dashboard Épidémiologique",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-title {
        font-size: 4.2rem;
        font-weight: 800;
        color: #e74c3c;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        text-align: center;
    }
    .metric-label {
        font-size: 0.8rem;
        opacity: 0.85;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Chargement des données
@st.cache_data  # Cache = chargement une seule fois
def charger_donnees():
    base = Path(__file__).parent.parent / "data" / "processed"
    
    tests_nat = pd.read_csv(base / "indicateurs_tests.csv",  parse_dates=['jour'])
    hosp_nat  = pd.read_csv(base / "indicateurs_hosp.csv",   parse_dates=['jour'])
    vacc_nat  = pd.read_csv(base / "indicateurs_vacc.csv",   parse_dates=['jour'])
    tests_dep = pd.read_csv(base / "tests_par_dep.csv",      parse_dates=['jour'])
    vagues    = pd.read_csv(base / "vagues_detectees.csv",   parse_dates=['debut','fin'])
    
    return tests_nat, hosp_nat, vacc_nat, tests_dep, vagues

tests_nat, hosp_nat, vacc_nat, tests_dep, vagues = charger_donnees()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Flag_of_France.svg/320px-Flag_of_France.svg.png", width=80)
    st.markdown("## Filtres")
    
    # Filtre période
    date_min = tests_nat['jour'].min().date()
    date_max = tests_nat['jour'].max().date()
    
    periode = st.date_input(
        "Période d'analyse",
        value=(date_min, date_max),
        min_value=date_min,
        max_value=date_max
    )
    
    # Filtre département (pour la section carte)
    # Forcer tous les codes département en chaîne de caractères
    tests_dep['dep'] = tests_dep['dep'].astype(str).str.zfill(2)
    deps = sorted(tests_dep['dep'].unique().tolist())
    dep_selectionne = st.selectbox(
        "Département (analyse locale)",
        options=deps,
        index=deps.index('75') if '75' in deps else 0
    )
    
    # Afficher les vagues
    st.markdown("---")
    st.markdown("### Vagues détectées")
    for i, row in vagues.iterrows():
        st.markdown(f"**Vague {i+1}** : {row['debut'].strftime('%b %Y')}")
    
    st.markdown("---")
    st.markdown("### Source des données")
    st.markdown("[Santé Publique France](https://www.data.gouv.fr)")
    st.markdown("Période : mai 2020 → juin 2023")
    st.markdown("---")
    st.markdown("*EpiSight*")
    st.markdown("*[Abderemane Attoumani](https://github.com/abderemaneattoumani)*")

# Filtre temporel appliqué
if len(periode) == 2:
    debut, fin = pd.Timestamp(periode[0]), pd.Timestamp(periode[1])
else:
    debut, fin = tests_nat['jour'].min(), tests_nat['jour'].max()

mask_tests = (tests_nat['jour'] >= debut) & (tests_nat['jour'] <= fin)
mask_hosp  = (hosp_nat['jour']  >= debut) & (hosp_nat['jour']  <= fin)
mask_vacc  = (vacc_nat['jour']  >= debut) & (vacc_nat['jour']  <= fin)

t = tests_nat[mask_tests].copy()
h = hosp_nat[mask_hosp].copy()
v = vacc_nat[mask_vacc].copy()

# En-tête
st.markdown('<p class="main-title">EpiSight</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Dashboard Épidémiologique Interactif — France COVID-19 | Données Santé Publique France</p>', unsafe_allow_html=True)

# KPIs Ligne du haut
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_cas = int(t['cas_positifs'].sum())
    st.metric("Cas positifs", f"{total_cas:,}".replace(",", " "))

with col2:
    pic = int(t['cas_mm7'].max())
    st.metric("Pic quotidien (MM7)", f"{pic:,}".replace(",", " "))

with col3:
    pic_hosp = int(h['hospitalises'].max()) if len(h) > 0 else 0
    st.metric("Pic hospitalisations", f"{pic_hosp:,}".replace(",", " "))

with col4:
    pic_rea = int(h['reanimation'].max()) if len(h) > 0 else 0
    st.metric("Pic réanimation", f"{pic_rea:,}".replace(",", " "))

with col5:
    couv = v['couv_complet_pct'].max() if len(v) > 0 else 0
    st.metric("Couverture vaccinale", f"{couv:.1f}%")

st.markdown("---")

# Onglets Principaux
tab1, tab2, tab3, tab4 = st.tabs([
    "Évolution temporelle",
    "Hospitalisations",
    "Vaccination",
    "Analyse départementale"
])


# ONGLET 1 — Évolution temporelle
with tab1:
    st.subheader("Évolution de l'épidémie — France entière")
    
    # Graphique cas positifs
    fig_cas = go.Figure()
    
    # Zones vagues en fond
    for _, vague in vagues.iterrows():
        if vague['debut'] >= debut and vague['fin'] <= fin:
            fig_cas.add_vrect(
                x0=vague['debut'], x1=vague['fin'],
                fillcolor="rgba(231, 76, 60, 0.08)",
                layer="below", line_width=0
            )
    
    # Données brutes (transparentes)
    fig_cas.add_trace(go.Scatter(
        x=t['jour'], y=t['cas_positifs'],
        mode='lines',
        line=dict(color='rgba(231,76,60,0.25)', width=1),
        name='Données brutes',
        hovertemplate='%{x|%d/%m/%Y}<br>Cas bruts: %{y:,.0f}<extra></extra>'
    ))
    
    # Moyenne mobile 7j
    fig_cas.add_trace(go.Scatter(
        x=t['jour'], y=t['cas_mm7'],
        mode='lines',
        line=dict(color='#e74c3c', width=2.5),
        name='Moyenne mobile 7j',
        hovertemplate='%{x|%d/%m/%Y}<br>MM7: %{y:,.0f}<extra></extra>'
    ))
    
    fig_cas.update_layout(
        title="Cas positifs quotidiens (zones roses = vagues épidémiques)",
        xaxis_title="Date",
        yaxis_title="Nombre de cas",
        hovermode='x unified',
        height=400,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_cas, use_container_width=True)
    
    # Graphique taux de positivité
    fig_tp = go.Figure()
    
    fig_tp.add_trace(go.Scatter(
        x=t['jour'], y=t['tp_mm7'],
        mode='lines',
        fill='tozeroy',
        line=dict(color='#e67e22', width=2),
        fillcolor='rgba(230, 126, 34, 0.15)',
        name='Taux positivité MM7',
        hovertemplate='%{x|%d/%m/%Y}<br>Taux: %{y:.1f}%<extra></extra>'
    ))
    
    fig_tp.add_hline(y=5, line_dash="dash", line_color="red",
                     annotation_text="Seuil alerte 5%",
                     annotation_position="bottom right")
    
    fig_tp.update_layout(
        title="Taux de positivité — Moyenne mobile 7 jours",
        xaxis_title="Date", yaxis_title="Taux (%)",
        height=350, template='plotly_white',
        hovermode='x unified'
    )
    st.plotly_chart(fig_tp, use_container_width=True)


# ONGLET 2 — Hospitalisations
with tab2:
    st.subheader("Pression hospitalière")
    
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        fig_hosp = go.Figure()
        fig_hosp.add_trace(go.Scatter(
            x=h['jour'], y=h['hosp_mm7'],
            mode='lines', fill='tozeroy',
            line=dict(color='#3498db', width=2),
            fillcolor='rgba(52, 152, 219, 0.2)',
            name='Hospitalisés MM7',
            hovertemplate='%{x|%d/%m/%Y}<br>Hospitalisés: %{y:,.0f}<extra></extra>'
        ))
        fig_hosp.update_layout(
            title="Patients hospitalisés (MM7)",
            height=350, template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_hosp, use_container_width=True)
    
    with col_h2:
        fig_rea = go.Figure()
        fig_rea.add_trace(go.Scatter(
            x=h['jour'], y=h['rea_mm7'],
            mode='lines', fill='tozeroy',
            line=dict(color='#8e44ad', width=2),
            fillcolor='rgba(142, 68, 173, 0.2)',
            name='Réanimation MM7',
            hovertemplate='%{x|%d/%m/%Y}<br>Réanimation: %{y:,.0f}<extra></extra>'
        ))
        fig_rea.add_hline(y=5000, line_dash="dash", line_color="red",
                          annotation_text="Capacité normale (~5000)")
        fig_rea.update_layout(
            title="Patients en réanimation (MM7)",
            height=350, template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_rea, use_container_width=True)
    
    # Décès
    if 'deces_mm7' in h.columns:
        fig_dc = go.Figure()
        fig_dc.add_trace(go.Scatter(
            x=h['jour'], y=h['deces_mm7'],
            mode='lines', fill='tozeroy',
            line=dict(color='#2c3e50', width=2),
            fillcolor='rgba(44, 62, 80, 0.15)',
            name='Décès MM7',
            hovertemplate='%{x|%d/%m/%Y}<br>Décès: %{y:.1f}<extra></extra>'
        ))
        fig_dc.update_layout(
            title="Décès quotidiens — Moyenne mobile 7 jours",
            xaxis_title="Date", yaxis_title="Décès / jour",
            height=320, template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_dc, use_container_width=True)

# ONGLET 3 — Vaccination
with tab3:
    st.subheader("Campagne de vaccination nationale")
    
    fig_vacc = go.Figure()
    fig_vacc.add_trace(go.Scatter(
        x=v['jour'], y=v['couv_dose1_pct'],
        mode='lines', line=dict(color='#27ae60', width=2.5),
        name='1ère dose',
        hovertemplate='%{x|%d/%m/%Y}<br>1 dose: %{y:.1f}%<extra></extra>'
    ))
    fig_vacc.add_trace(go.Scatter(
        x=v['jour'], y=v['couv_complet_pct'],
        mode='lines', line=dict(color='#2ecc71', width=2.5),
        name='Schéma complet',
        hovertemplate='%{x|%d/%m/%Y}<br>Complet: %{y:.1f}%<extra></extra>'
    ))
    fig_vacc.add_trace(go.Scatter(
        x=v['jour'], y=v['couv_rappel_pct'],
        mode='lines', line=dict(color='#1abc9c', width=2.5),
        name='Rappel',
        hovertemplate='%{x|%d/%m/%Y}<br>Rappel: %{y:.1f}%<extra></extra>'
    ))
    fig_vacc.add_hline(y=70, line_dash="dot", line_color="gray",
                       annotation_text="Objectif immunité collective 70%")
    fig_vacc.update_layout(
        title="Couverture vaccinale — Population française (%)",
        xaxis_title="Date", yaxis_title="% population",
        height=420, template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig_vacc, use_container_width=True)
    
    # Doses journalières
    if 'doses_jour' in v.columns:
        fig_doses = go.Figure()
        fig_doses.add_trace(go.Bar(
            x=v['jour'], y=v['doses_jour'],
            marker_color='rgba(39, 174, 96, 0.6)',
            name='Doses quotidiennes',
            hovertemplate='%{x|%d/%m/%Y}<br>Doses: %{y:,}<extra></extra>'
        ))
        fig_doses.update_layout(
            title="Doses administrées par jour",
            xaxis_title="Date", yaxis_title="Doses",
            height=320, template='plotly_white'
        )
        st.plotly_chart(fig_doses, use_container_width=True)

# ONGLET 4 — Analyse départementale
with tab4:
    st.subheader(f"Analyse locale — Département {dep_selectionne}")
    
    dep_data = tests_dep[
        (tests_dep['dep'] == dep_selectionne) &
        (tests_dep['jour'] >= debut) &
        (tests_dep['jour'] <= fin)
    ].sort_values('jour').copy()
    
    if len(dep_data) > 0:
        # Recalcul MM7 pour ce département
        dep_data['cas_mm7_dep'] = dep_data['cas_positifs'].rolling(7, min_periods=1).mean()
        
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.metric("Cas totaux", f"{int(dep_data['cas_positifs'].sum()):,}".replace(",", " "))
        with col_d2:
            ti_max = dep_data['taux_incidence'].max()
            st.metric("Taux incidence max", f"{ti_max:.0f} / 100k hab.")
        with col_d3:
            tp_moy = dep_data['taux_positivite'].mean()
            st.metric("Taux positivité moyen", f"{tp_moy:.1f}%")
        
        # Graphique taux d'incidence département
        fig_dep = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                subplot_titles=('Taux d\'incidence (cas/100k hab., 7j glissants)',
                                                'Taux de positivité (%)'))
        
        # Zones de couleur selon seuils
        couleur_ti = dep_data['taux_incidence'].apply(
            lambda x: '#e74c3c' if x > 250 else ('#e67e22' if x > 150 else
                      ('#f1c40f' if x > 50 else '#2ecc71'))
        )
        
        fig_dep.add_trace(go.Scatter(
            x=dep_data['jour'], y=dep_data['taux_incidence'],
            mode='lines', fill='tozeroy',
            line=dict(color='#e74c3c', width=2),
            fillcolor='rgba(231, 76, 60, 0.15)',
            name='Taux incidence',
            hovertemplate='%{x|%d/%m/%Y}<br>TI: %{y:.1f}/100k<extra></extra>'
        ), row=1, col=1)
        
        # Lignes seuils
        for seuil, label, couleur in [(50, "Alerte", "#e67e22"),
                                       (150, "Alerte renforcée", "#e74c3c"),
                                       (250, "Urgence", "#c0392b")]:
            fig_dep.add_hline(y=seuil, line_dash="dash",
                              line_color=couleur, opacity=0.5,
                              annotation_text=label, row=1, col=1)
        
        fig_dep.add_trace(go.Scatter(
            x=dep_data['jour'], y=dep_data['taux_positivite'],
            mode='lines', fill='tozeroy',
            line=dict(color='#e67e22', width=2),
            fillcolor='rgba(230, 126, 34, 0.15)',
            name='Taux positivité',
            hovertemplate='%{x|%d/%m/%Y}<br>TP: %{y:.1f}%<extra></extra>'
        ), row=2, col=1)
        
        fig_dep.add_hline(y=5, line_dash="dash", line_color="red",
                          annotation_text="Seuil 5%", row=2, col=1)
        
        fig_dep.update_layout(
            height=550, template='plotly_white',
            hovermode='x unified',
            showlegend=False
        )
        st.plotly_chart(fig_dep, use_container_width=True)
        
    else:
        st.warning(f"Aucune donnée pour le département {dep_selectionne} sur cette période.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#95a5a6; font-size:0.85rem'>"
    "EpiSight v1.0 — Données : Santé Publique France / data.gouv.fr — "
    "| Abderemane Attoumani | <a href='https://github.com/abderemaneattoumani' "
    "style='color:#3498db'>GitHub</a></div>",
    unsafe_allow_html=True
)