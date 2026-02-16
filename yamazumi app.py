import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Yazaki Yamazumi", layout="wide", page_icon="⏱️")

# Ajouter l'image de fond avec CSS et thème Yazaki TRÈS CLAIR
import base64

# Fonction pour convertir l'image en base64
@st.cache_data
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Charger l'image de fond
bg_image = get_base64_image("yazaki_background.webp")

if bg_image:
    # Appliquer le style CSS pour l'arrière-plan avec thème Yazaki TRÈS CLAIR
    st.markdown(
        f"""
        <style>
        /* Image de fond */
        .stApp {{
            background-image: url("data:image/webp;base64,{bg_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Overlay blanc presque opaque pour thème TRÈS clair */
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.97);
            z-index: -1;
        }}
        
        /* Couleurs Yazaki - Rouge principal */
        h1, h2, h3 {{
            color: #E31E24 !important;
            font-weight: bold !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }}
        
        /* Texte normal en noir pour lisibilité maximale */
        .stMarkdown, p, label, span, div {{
            color: #1a1a1a !important;
        }}
        
        /* Boutons avec couleurs Yazaki */
        .stButton button {{
            background-color: #E31E24 !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            box-shadow: 0 2px 6px rgba(227, 30, 36, 0.2) !important;
            transition: all 0.2s ease !important;
        }}
        
        .stButton button:hover {{
            background-color: #C71820 !important;
            box-shadow: 0 4px 12px rgba(227, 30, 36, 0.35) !important;
            transform: translateY(-2px);
        }}
        
        /* Boutons secondaires - fond blanc */
        .stButton button[kind="secondary"] {{
            background-color: white !important;
            color: #E31E24 !important;
            border: 2px solid #E31E24 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08) !important;
        }}
        
        .stButton button[kind="secondary"]:hover {{
            background-color: #FFF5F5 !important;
        }}
        
        /* Containers avec fond blanc pur */
        .element-container {{
            background-color: rgba(255, 255, 255, 0.96);
            border-radius: 12px;
            padding: 14px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
            margin: 5px 0;
        }}
        
        /* Selectbox Yazaki style */
        .stSelectbox > div > div {{
            background-color: white !important;
            border: 2px solid #E31E24 !important;
            border-radius: 8px !important;
        }}
        
        /* Success messages en vert très clair */
        .stSuccess {{
            background-color: rgba(76, 175, 80, 0.12) !important;
            color: #2E7D32 !important;
            border-left: 4px solid #4CAF50 !important;
            border-radius: 8px !important;
        }}
        
        /* Info messages avec accent Yazaki ultra léger */
        .stInfo {{
            background-color: rgba(227, 30, 36, 0.06) !important;
            color: #E31E24 !important;
            border-left: 4px solid #E31E24 !important;
            border-radius: 8px !important;
        }}
        
        /* Error messages */
        .stError {{
            background-color: rgba(244, 67, 54, 0.08) !important;
            color: #C62828 !important;
            border-left: 4px solid #F44336 !important;
            border-radius: 8px !important;
        }}
        
        /* Divider en rouge Yazaki */
        hr {{
            border-color: #E31E24 !important;
            border-width: 2px !important;
            margin: 25px 0 !important;
            opacity: 0.3;
        }}
        
        /* Dataframe styling - fond blanc pur */
        .dataframe {{
            background-color: white !important;
            border: 1px solid #e0e0e0 !important;
        }}
        
        /* Checkbox */
        .stCheckbox label {{
            color: #1a1a1a !important;
        }}
        
        /* Header */
        [data-testid="stHeader"] {{
            background-color: rgba(255, 255, 255, 0.98) !important;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.99) !important;
        }}
        
        /* Vertical blocks blancs */
        [data-testid="stVerticalBlock"] {{
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 10px;
            padding: 15px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Ajouter le logo et le titre
col_logo, col_title = st.columns([1, 5])

with col_logo:
    # Essayer de charger le logo
    try:
        st.image("yazaki_logo.webp", width=150)
    except:
        st.markdown("### YAZAKI")

with col_title:
    st.title("⏱️ Yamazumi Chart - YAZAKI Morocco")

# Option pour contrôler le lag
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

# ===============================
# Configuration
# ===============================

# Liste des étapes organisées par catégorie
STEPS_VA = ["SET", "TAPE", "LOCK", "PUSH BUTTON", "TEST", "INSERT", "PACKING", "CUT"]

STEPS_NW = ["PICK UP", "PUT", "REMOVE", "ROUTING"]

STEPS_AW = ["SCAN", "LEAVE", "COIL UP", "OPEN", "PULL UP", "PUSH DOWN"]

STEPS_MUDA = [
    "WALK", "WAIT", "HANDLING", "SEARCHING", "FIXING",
    "RUBBER FIXING", "RUBBER TAKING", "REACHING", 
    "OPENNING RUBBER", "CHECKING", "SCRAPPING"
]

# Toutes les étapes combinées
STEPS = STEPS_VA + STEPS_NW + STEPS_AW + STEPS_MUDA

# Classification pour chaque étape
CLASSIFICATION = {
    # VA - Value Added (Green)
    "SET": "VA", "TAPE": "VA", "LOCK": "VA", "PUSH BUTTON": "VA",
    "TEST": "VA", "INSERT": "VA", "PACKING": "VA", "CUT": "VA",
    
    # NW - Necessary Works (Yellow)
    "PICK UP": "NW", "PUT": "NW", "REMOVE": "NW", "ROUTING": "NW",
    
    # AW - Avoidable Works (Orange)
    "SCAN": "AW", "LEAVE": "AW", "COIL UP": "AW", "OPEN": "AW",
    "PULL UP": "AW", "PUSH DOWN": "AW",
    
    # MUDA - Waste (Red)
    "WALK": "MUDA", "WAIT": "MUDA", "HANDLING": "MUDA", "SEARCHING": "MUDA",
    "FIXING": "MUDA", "RUBBER FIXING": "MUDA", "RUBBER TAKING": "MUDA",
    "REACHING": "MUDA", "OPENNING RUBBER": "MUDA", "CHECKING": "MUDA", "SCRAPPING": "MUDA"
}

# Liste des workstations (colonnes du tableau)
WORKSTATIONS = [
    "COILING 1", "COILING 2", "WELDING 1", "WELDING 2",
    "WS1", "WS2", "WS3", "WS4", "WS5", "WS6",
    "WS7", "WS8", "WS9", "WS10", "WS11", "WS12"
]

# Cycle Time
CYCLE_TIME = 180.0

# ===============================
# Initialisation Session State
# ===============================
if "data_matrix" not in st.session_state:
    st.session_state.data_matrix = {}

if "chrono_active" not in st.session_state:
    st.session_state.chrono_active = {}

# ===============================
# Sélection SPS
# ===============================
st.subheader("📋 Configuration")

col1, col2 = st.columns(2)

with col1:
    sps = st.selectbox("Select SPS", ["SPS1", "SPS2", "SPS3", "SPS4", "SPS5"])

with col2:
    auto_refresh = st.checkbox("🔄 Auto-refresh chrono (décocher si lag)", value=True)
    st.session_state.auto_refresh = auto_refresh

st.divider()

# ===============================
# Boutons de navigation entre sections
# ===============================
st.subheader("⏱️ Tableau de Chronométrage")

# Initialiser la section active si pas encore définie
if "active_section" not in st.session_state:
    st.session_state.active_section = "VA"

# Créer les boutons de navigation
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🟢 VA - Value Added", use_container_width=True, 
                 type="primary" if st.session_state.active_section == "VA" else "secondary"):
        st.session_state.active_section = "VA"
        st.rerun()

with col2:
    if st.button("🟡 NW - Necessary Works", use_container_width=True,
                 type="primary" if st.session_state.active_section == "NW" else "secondary"):
        st.session_state.active_section = "NW"
        st.rerun()

with col3:
    if st.button("🟠 AW - Avoidable Works", use_container_width=True,
                 type="primary" if st.session_state.active_section == "AW" else "secondary"):
        st.session_state.active_section = "AW"
        st.rerun()

with col4:
    if st.button("🔴 MUDA - Waste", use_container_width=True,
                 type="primary" if st.session_state.active_section == "MUDA" else "secondary"):
        st.session_state.active_section = "MUDA"
        st.rerun()

st.divider()

# ===============================
# Tableau de chronométrage avec sections
# ===============================

# Fonction pour créer une section de tableau
def create_section(title, steps_list, emoji, color):
    st.markdown(f"### {emoji} {title}")
    
    # En-têtes de colonnes
    header_cols = st.columns([2] + [1] * len(WORKSTATIONS))
    with header_cols[0]:
        st.markdown("**ÉTAPE**")
    for idx, ws in enumerate(WORKSTATIONS):
        with header_cols[idx + 1]:
            st.markdown(f"**{ws}**")
    
    # Lignes pour chaque étape
    for step in steps_list:
        classification = CLASSIFICATION[step]
        
        cols = st.columns([2] + [1] * len(WORKSTATIONS))
        
        # Première colonne : nom de l'étape
        with cols[0]:
            st.markdown(f"**{step}**")
        
        # Colonnes suivantes : une pour chaque workstation
        for idx, ws in enumerate(WORKSTATIONS):
            with cols[idx + 1]:
                key = (step, ws)
                
                # Afficher le temps si déjà enregistré
                if key in st.session_state.data_matrix:
                    temps = st.session_state.data_matrix[key]
                    st.success(f"✅ {temps:.2f}s")
                    
                    # Bouton pour réinitialiser
                    if st.button("🔄", key=f"reset_{step}_{ws}", help="Réinitialiser"):
                        del st.session_state.data_matrix[key]
                        if key in st.session_state.chrono_active:
                            del st.session_state.chrono_active[key]
                        st.rerun()
                
                # Chrono actif
                elif key in st.session_state.chrono_active:
                    start_time = st.session_state.chrono_active[key]
                    elapsed = time.time() - start_time
                    st.info(f"⏱️ {elapsed:.1f}s")
                    
                    # Bouton Stop
                    if st.button("⏹️ Stop", key=f"stop_{step}_{ws}"):
                        final_time = time.time() - start_time
                        st.session_state.data_matrix[key] = final_time
                        del st.session_state.chrono_active[key]
                        st.rerun()
                
                # Chrono non démarré
                else:
                    if st.button("▶️ Start", key=f"start_{step}_{ws}"):
                        st.session_state.chrono_active[key] = time.time()
                        st.rerun()
    
    st.divider()

# Afficher seulement la section active
if st.session_state.active_section == "VA":
    create_section("VA - Value Added", STEPS_VA, "🟢", "green")
elif st.session_state.active_section == "NW":
    create_section("NW - Necessary Works", STEPS_NW, "🟡", "yellow")
elif st.session_state.active_section == "AW":
    create_section("AW - Avoidable Works", STEPS_AW, "🟠", "orange")
elif st.session_state.active_section == "MUDA":
    create_section("MUDA - Waste", STEPS_MUDA, "🔴", "red")

# Auto-refresh pour les chronos actifs (réduit le lag)
if st.session_state.chrono_active and st.session_state.auto_refresh:
    time.sleep(0.5)
    st.rerun()

st.divider()

# ===============================
# Analyse et Yamazumi Chart
# ===============================
if st.session_state.data_matrix:
    st.subheader("📈 Analyse")
    
    # Convertir en DataFrame
    data_list = []
    for (step, ws), temps in st.session_state.data_matrix.items():
        data_list.append({
            "SPS": sps,
            "Step": step,
            "WS": ws,
            "Classification": CLASSIFICATION[step],
            "Temps": temps
        })
    
    df = pd.DataFrame(data_list)
    
    # Afficher les données
    st.dataframe(df, use_container_width=True)
    
    # Export CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name=f'chronometrage_{sps}.csv',
        mime='text/csv',
    )
    
    st.divider()
    
    # Calculer les totaux par WS
    cycle_times = df.groupby("WS")["Temps"].sum().sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⏰ Cycle Time par WS")
        st.dataframe(cycle_times, use_container_width=True)
    
    with col2:
        # VA %
        va_time = df[df["Classification"] == "VA"].groupby("WS")["Temps"].sum()
        total_time = df.groupby("WS")["Temps"].sum()
        va_percent = (va_time / total_time * 100).fillna(0).round(2)
        
        st.subheader("✅ VA % par WS")
        st.dataframe(va_percent, use_container_width=True)
    
    # Goulot
    if len(cycle_times) > 0:
        goulot = cycle_times.idxmax()
        goulot_time = cycle_times.max()
        st.error(f"🔴 **Goulot d'étranglement:** {goulot} ({goulot_time:.2f} sec)")
    
    st.divider()
    
    # ===============================
    # Yamazumi Chart
    # ===============================
    st.subheader("📊 Yamazumi Chart")
    
    # Créer le pivot
    pivot = df.pivot_table(
        index="WS",
        columns="Classification",
        values="Temps",
        aggfunc="sum",
        fill_value=0
    )
    
    # S'assurer que toutes les classifications sont présentes
    for cls in ['VA', 'NW', 'AW', 'MUDA']:
        if cls not in pivot.columns:
            pivot[cls] = 0
    
    # Réorganiser les colonnes
    pivot = pivot[['VA', 'NW', 'AW', 'MUDA']]
    
    # Calculer les totaux
    totals = pivot.sum(axis=1)
    
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(16, 6))
    
    # Couleurs de base
    colors_base = {
        'VA': '#00FF00',      # Vert vif
        'NW': '#FFFF00',      # Jaune
        'AW': '#FFA500',      # Orange
        'MUDA': '#FF0000'     # Rouge
    }
    
    # Position des barres
    x_pos = range(len(pivot.index))
    width = 0.6
    
    # Créer les barres empilées
    bottom_values = [0] * len(pivot.index)
    bars_containers = []
    
    for classification in ['VA', 'NW', 'AW', 'MUDA']:
        values = pivot[classification].values
        
        bars = ax.bar(
            x_pos,
            values,
            width=width,
            bottom=bottom_values,
            label=classification,
            color=colors_base[classification],
            edgecolor='black',
            linewidth=0.5
        )
        
        bars_containers.append(bars)
        bottom_values = [b + v for b, v in zip(bottom_values, values)]
    
    # Changer SEULEMENT la bordure selon le cycle time
    for i, (ws, total) in enumerate(totals.items()):
        if total > CYCLE_TIME:
            # OVERTIME - Bordure rouge épaisse
            for container in bars_containers:
                container[i].set_edgecolor('#8B0000')
                container[i].set_linewidth(4)
        else:
            # OK - Bordure bleue épaisse
            for container in bars_containers:
                container[i].set_edgecolor('#0000FF')
                container[i].set_linewidth(4)
    
    # Ligne de Cycle Time
    ax.axhline(y=CYCLE_TIME, color='black', linestyle='-', linewidth=2, 
              label=f'TT (Takt Time = {CYCLE_TIME}s)', zorder=5)
    
    # Configuration
    ax.set_ylabel("Time (sec)", fontsize=12, fontweight='bold')
    ax.set_xlabel("", fontsize=12)
    ax.set_title(f"Yamazumi Chart - {sps} - YAZAKI Morocco", fontsize=14, fontweight='bold')
    
    # Grille
    ax.grid(axis='y', alpha=0.5, linestyle='-', linewidth=0.5, color='gray')
    ax.set_axisbelow(True)
    
    # Légende
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), 
             ncol=5, frameon=True, fontsize=10)
    
    # Labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(pivot.index, rotation=90, ha='center', fontsize=8)
    
    # Limites Y
    max_total = totals.max() if len(totals) > 0 and not pd.isna(totals.max()) else 0
    max_val = max(max_total, CYCLE_TIME)
    if max_val > 0:
        ax.set_ylim(0, max_val * 1.15)
    else:
        ax.set_ylim(0, 200)
    
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close(fig)
    
    st.divider()
    
    # Reset button
    if st.button("🗑️ Reset All Data", type="primary"):
        st.session_state.data_matrix = {}
        st.session_state.chrono_active = {}
        st.rerun()
else:
    st.info("ℹ️ Aucune donnée enregistrée. Commencez par chronométrer des étapes en cliquant sur ▶️ Start.")
