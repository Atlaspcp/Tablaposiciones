import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os
import shutil
from datetime import datetime

# --- 1. CONFIGURACIÓN Y PERSISTENCIA ---
st.set_page_config(page_title="#NAMLEAGUE2026", layout="wide")

DB_FILE = "torneo_data.json"

def img_to_base64(image):
    if image is None: return None
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def save_to_disk():
    data_to_save = {
        "partidos": st.session_state.partidos,
        "equipos": {},
        "fase_final": st.session_state.fase_final,
        "goleadores": st.session_state.goleadores,
        "logo_torneo": img_to_base64(st.session_state.logo_torneo) if st.session_state.logo_torneo else None,
        "logo_final": img_to_base64(st.session_state.logo_final) if st.session_state.logo_final else None
    }
    for id_eq, info in st.session_state.equipos.items():
        data_to_save["equipos"][id_eq] = {
            "nombre": info["nombre"], "grupo": info["grupo"],
            "logo": img_to_base64(info["logo"]) if info["logo"] else None
        }
    with open(DB_FILE, "w") as f:
        json.dump(data_to_save, f)

def inicializar_fase_final():
    return {
        "cuartos": [{"L": "", "V": "", "gl": 0, "gv": 0} for _ in range(4)],
        "semis": [{"L": "", "V": "", "gl": 0, "gv": 0} for _ in range(2)],
        "final": {"L": "", "V": "", "gl": 0, "gv": 0}
    }

def load_from_disk():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                st.session_state.partidos = data.get("partidos", [])
                st.session_state.fase_final = data.get("fase_final", inicializar_fase_final())
                st.session_state.goleadores = data.get("goleadores", [])
                if data.get("logo_torneo"):
                    st.session_state.logo_torneo = Image.open(io.BytesIO(base64.b64decode(data["logo_torneo"])))
                if data.get("logo_final"):
                    st.session_state.logo_final = Image.open(io.BytesIO(base64.b64decode(data["logo_final"])))
                eq_cargados = {}
                for id_eq, info in data.get("equipos", {}).items():
                    logo_pil = Image.open(io.BytesIO(base64.b64decode(info["logo"]))) if info["logo"] else None
                    eq_cargados[id_eq] = {"nombre": info["nombre"], "grupo": info["grupo"], "logo": logo_pil}
                st.session_state.equipos = eq_cargados
                return True
        except: return False
    return False

# --- 2. ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top, #00124d 0%, #000422 100%) !important; }
    .txt-celeste { color: #7db1ff !important; }
    .txt-red { color: #ff3b3b !important; }
    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: white !important; font-weight: 900; }
    .nam-title { font-size: clamp(2.5em, 8vw, 4.5em); text-align: center; font-weight: 900; letter-spacing: -2px; color: white; margin-bottom: 20px; }
    
    [data-testid="stSidebar"] h2 { color: #000000 !important; font-weight: 900; }

    .main-card {
        background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #FFD70033; color: white; backdrop-filter: blur(10px);
        overflow-x: auto;
    }

    /* GRID PARA POSICIONES Y GOLEADORES */
    .grid-posiciones { display: grid; grid-template-columns: 2fr repeat(8, 45px); align-items: center; min-width: 650px; padding: 10px 15px; }
    .grid-goleadores { display: grid; grid-template-columns: 2fr 1.5fr 1fr; align-items: center; min-width: 500px; padding: 10px 15px; }
    
    .header-grid { background: linear-gradient(90deg, #00124d 0%, #ff3b3b33 100%); border-bottom: 3px solid #FFD700; font-weight: 900; }
    .stat-cell { text-align: center; font-weight: bold; color: white !important; }

    /* FASE FINAL - Layout Izquierda, Centro, Derecha */
    .bracket-scroll { overflow-x: auto; width: 100%; }
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; min-width: 1050px; padding: 20px 0; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 550px; width: 240px; }
    .bracket-column h4 { color: white !important; text-align: center; margin-bottom: 10px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 8px; border: 1px solid #FFD70044; padding: 10px; margin: 15px 0; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 28px; text-align: center; border-radius: 3px; }
    .final-center { width: 300px; display: flex; flex-direction: column; align-items: center; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA ---
def get_team_info(name):
    for info in st.session_state.equipos.values():
        if info['nombre'] == name: return info
    return {"nombre": name, "logo": None}

def render_match(match):
    t1, t2 = get_team_info(match["L"]), get_team_info(match["V"])
    img1 = f"data:image/png;base64,{img_to_base64(t1['logo'])}" if t1['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    img2 = f"data:image/png;base64,{img_to_base64(t2['logo'])}" if t2['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    # El HTML se devuelve sin sangría excesiva para evitar que Markdown lo tome como código
    return f'<div class="match-box-ko"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;"><div style="display:flex;align-items:center;"><img src="{img1}" style="width:22px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;">{t1["nombre"] or "---"}</span></div><span class="ko-score">{match["gl"]}</span></div><div style="display:flex;align-items:center;justify-content:space-between;"><div style="display:flex;align-items:center;"><img src="{img2}" style="width:22px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;">{t2["nombre"] or "---"}</span></div><span class="ko-score">{match["gv"]}</span></div></div>'

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    st.session_state.logo_torneo = st.session_state.logo_final = None
    if not load_from_disk():
        st.session_state.equipos = {f"ID_{i}": {"nombre": f"EQUIPO {i}", "grupo": chr(64 + ((i-1) // 4) + 1), "logo": None} for i in range(1, 21)}
        st.session_state.partidos, st.session_state.goleadores = [], []
        st.session_state.fase_final = inicializar_fase_final()

# --- 5. INTERFAZ ---
st.markdown('<h1 class="nam-title">#<span class="txt-celeste">N</span><span class="txt-red">A</span>MLEAGUE2026</h1>', unsafe_allow_html=True)

t_pos, t_ff, t_gol = st.tabs(["📊 POSICIONES", "🏆 FASE FINAL", "👟 GOLEADORES"])

with t_ff:
    ff = st.session_state.fase_final
    logo_f = f"data:image/png;base64,{img_to_base64(st.session_state.logo_final)}" if st.session_state.logo_final else None
    
    # Construcción de las columnas: Izquierda (Cuartos/Semis), Centro (Final), Derecha (Semis/Cuartos)
    html_bracket = f'''
<div class="bracket-scroll">
<div class="bracket-wrapper">
<div class="bracket-column">
<h4>CUARTOS</h4>{render_match(ff["cuartos"][0])}{render_match(ff["cuartos"][1])}
</div>
<div class="bracket-column">
<h4>SEMIFINAL</h4>{render_match(ff["semis"][0])}
</div>
<div class="final-center">
{"<img src='"+logo_f+"' width=160 style='filter:drop-shadow(0 0 15px #FFD700)'>" if logo_f else "<h2>FINAL</h2>"}
<h1 style="color:white !important;margin:15px 0;">GRAN FINAL</h1>
{render_match(ff["final"])}
</div>
<div class="bracket-column">
<h4>SEMIFINAL</h4>{render_match(ff["semis"][1])}
</div>
<div class="bracket-column">
<h4>CUARTOS</h4>{render_match(ff["cuartos"][2])}{render_match(ff["cuartos"][3])}
</div>
</div>
</div>'''
    st.markdown(html_bracket, unsafe_allow_html=True)

with t_gol:
    if st.session_state.goleadores:
        html_gol = '<div class="main-card"><div class="grid-goleadores header-grid"><span>JUGADOR</span><span class="stat-cell">EQUIPO</span><span class="stat-cell">GOLES</span></div>'
        for g in st.session_state.goleadores:
            html_gol += f'<div class="grid-goleadores" style="border-bottom:1px solid #ffffff10;"><span style="font-weight:700;text-transform:uppercase;">{g["nombre"]}</span><span class="stat-cell" style="color:#FFD700;font-size:0.85em;">{g["equipo"]}</span><span class="stat-cell">{g["goles"]}</span></div>'
        st.markdown(html_gol + '</div>', unsafe_allow_html=True)
