import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os
import shutil
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="#NAMLEAGUE2026", layout="wide")
DB_FILE = "torneo_data.json"

def img_to_base64(image):
    if image is None: return None
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.decodebytes(base64.b64encode(buffered.getvalue())).decode() if isinstance(image, str) else base64.b64encode(buffered.getvalue()).decode()

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

def load_from_disk():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                st.session_state.partidos = data.get("partidos", [])
                st.session_state.fase_final = data.get("fase_final", {
                    "cuartos": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(4)],
                    "semis": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(2)],
                    "final": {"L": "", "V": "", "gl": None, "gv": None}
                })
                st.session_state.goleadores = data.get("goleadores", [])
                if data.get("logo_torneo"): st.session_state.logo_torneo = Image.open(io.BytesIO(base64.b64decode(data["logo_torneo"])))
                if data.get("logo_final"): st.session_state.logo_final = Image.open(io.BytesIO(base64.b64decode(data["logo_final"])))
                eq_cargados = {}
                for id_eq, info in data.get("equipos", {}).items():
                    logo_pil = Image.open(io.BytesIO(base64.b64decode(info["logo"]))) if info["logo"] else None
                    eq_cargados[id_eq] = {"nombre": info["nombre"], "grupo": info["grupo"], "logo": logo_pil}
                st.session_state.equipos = eq_cargados
                return True
        except: return False
    return False

# --- 2. ESTILOS CORREGIDOS ---
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #000422 !important; }
    .nam-title { font-size: 4em; text-align: center; font-weight: 900; color: white; margin-bottom: 20px; }
    
    /* Caja de partido corregida para alineación total */
    .match-box-ko { 
        background: rgba(0, 20, 80, 0.8); 
        border-radius: 8px; 
        border: 1px solid #FFD70044; 
        padding: 12px; 
        margin: 10px 0;
        width: 100%;
    }
    .team-row {
        display: flex;
        align-items: center;
        justify-content: space-between; /* Empuja el score al final */
        width: 100%;
        margin: 4px 0;
    }
    .team-info {
        display: flex;
        align-items: center;
        gap: 10px;
        overflow: hidden;
    }
    .ko-score { 
        background: #FFD700; 
        color: #000; 
        font-weight: 900; 
        width: 30px; 
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px; 
        flex-shrink: 0;
    }
    
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; min-width: 1000px; }
    .bracket-column { width: 220px; display: flex; flex-direction: column; justify-content: space-around; min-height: 500px; }
    .final-center { width: 280px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE RENDERIZADO ---
def render_match(match):
    # Función para obtener nombre y logo
    def get_info(name):
        for info in st.session_state.equipos.values():
            if info['nombre'] == name: return info
        return {"nombre": name if name else "---", "logo": None}

    t1, t2 = get_info(match["L"]), get_info(match["V"])
    gl = match["gl"] if match["gl"] is not None else "-"
    gv = match["gv"] if match["gv"] is not None else "-"
    
    # Placeholder de logo si no hay uno
    def get_img(logo):
        if logo: return f"data:image/png;base64,{img_to_base64(logo)}"
        return "https://cdn-icons-png.flaticon.com/512/53/53283.png"

    return f'''
    <div class="match-box-ko">
        <div class="team-row">
            <div class="team-info">
                <img src="{get_img(t1['logo'])}" width="22">
                <span style="color:white; font-weight:700; font-size:0.9em;">{t1['nombre']}</span>
            </div>
            <div class="ko-score">{gl}</div>
        </div>
        <div class="team-row" style="margin-top:8px;">
            <div class="team-info">
                <img src="{get_img(t2['logo'])}" width="22">
                <span style="color:white; font-weight:700; font-size:0.9em;">{t2['nombre']}</span>
            </div>
            <div class="ko-score">{gv}</div>
        </div>
    </div>
    '''

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    st.session_state.logo_torneo = st.session_state.logo_final = None
    if not load_from_disk():
        st.session_state.equipos = {f"ID_{i}": {"nombre": f"EQUIPO {i}", "grupo": "A", "logo": None} for i in range(1, 21)}
        st.session_state.partidos, st.session_state.goleadores = [], []
        st.session_state.fase_final = {
            "cuartos": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(4)],
            "semis": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(2)],
            "final": {"L": "", "V": "", "gl": None, "gv": None}
        }

# --- 5. VISTA DE ADMINISTRADOR (GR CON GUIONES) ---
with st.sidebar:
    st.header("🔐 Panel NAM")
    if st.session_state.get('logged_in'):
        adm_tabs = st.tabs(["EQ", "GR", "ELIM", "GOL"])
        
        with adm_tabs[1]: # Pestaña GR (Resultados de Grupo)
            st.subheader("Registrar / Pre-cargar Partido")
            eqs = sorted([i['nombre'] for i in st.session_state.equipos.values()])
            l = st.selectbox("Local", eqs)
            v = st.selectbox("Visitante", eqs)
            
            # NUEVO: Checkbox para decidir si poner resultado o dejarlo pendiente
            jugado = st.checkbox("¿Partido ya jugado?", value=False)
            if jugado:
                gl, gv = st.number_input("Goles Local", 0), st.number_input("Goles Visitante", 0)
            else:
                gl, gv = None, None
            
            if st.button("Guardar Partido"):
                st.session_state.partidos.append({
                    "fecha": str(datetime.now().date()), 
                    "local": l, "visitante": v, 
                    "goles_l": gl, "goles_v": gv
                })
                save_to_disk(); st.rerun()

# --- 6. VISTA PÚBLICA (FASE FINAL) ---
st.markdown('<h1 class="nam-title">#NAMLEAGUE2026</h1>', unsafe_allow_html=True)
t1, t2, t3, t4 = st.tabs(["POSICIONES", "FASE FINAL", "RESULTADOS", "GOLEADORES"])

with t2:
    ff = st.session_state.fase_final
    st.markdown(f'''
    <div class="bracket-wrapper">
        <div class="bracket-column">
            <h4 style="text-align:center; color:white;">CUARTOS</h4>
            {render_match(ff['cuartos'][0])}
            {render_match(ff['cuartos'][1])}
        </div>
        <div class="bracket-column">
            <h4 style="text-align:center; color:white;">SEMIFINAL</h4>
            {render_match(ff['semis'][0])}
        </div>
        <div class="final-center">
            <h2 style="color:#FFD700; margin-bottom:0;">GRAN FINAL</h2>
            <div style="padding: 10px 0;">{render_match(ff['final'])}</div>
        </div>
        <div class="bracket-column">
            <h4 style="text-align:center; color:white;">SEMIFINAL</h4>
            {render_match(ff['semis'][1])}
        </div>
        <div class="bracket-column">
            <h4 style="text-align:center; color:white;">CUARTOS</h4>
            {render_match(ff['cuartos'][2])}
            {render_match(ff['cuartos'][3])}
        </div>
    </div>
    ''', unsafe_allow_html=True)
