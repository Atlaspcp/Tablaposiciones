import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os

# --- 1. CONFIGURACIÓN Y PERSISTENCIA ---
st.set_page_config(page_title="COPA NAM", layout="wide")

DB_FILE = "torneo_data.json"

def img_to_base64(image):
    if image is None: return None
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def save_to_disk():
    data_to_save = {"partidos": st.session_state.partidos, "equipos": {}}
    for id_eq, info in st.session_state.equipos.items():
        data_to_save["equipos"][id_eq] = {
            "nombre": info["nombre"],
            "grupo": info["grupo"],
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
                equipos_cargados = {}
                for id_eq, info in data.get("equipos", {}).items():
                    logo_pil = None
                    if info["logo"]:
                        logo_data = base64.b64decode(info["logo"])
                        logo_pil = Image.open(io.BytesIO(logo_data))
                    equipos_cargados[id_eq] = {"nombre": info["nombre"], "grupo": info["grupo"], "logo": logo_pil}
                st.session_state.equipos = equipos_cargados
                return True
        except: return False
    return False

# --- 2. ESTILOS CSS (FIJANDO COLOR BLANCO EN TÍTULOS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    
    /* Fondo General */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top, #00124d 0%, #000422 100%) !important;
    }

    /* FORZAR BLANCO EN TÍTULOS (COPA NAM y otros h1/h2) */
    h1, h2, h3, [data-testid="stHeader"] h1, .results-title {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    /* Forzar blanco en las letras de las pestañas (Tabs) */
    .stTabs [data-baseweb="tab"] p {
        color: white !important;
        font-weight: 700;
        font-size: 1.1em;
    }

    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; color: white !important; }

    /* Tarjetas de grupos */
    .main-card {
        background: rgba(0, 10, 60, 0.6);
        border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #00d4ff33; color: white; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
    }

    .group-header {
        background: linear-gradient(90deg, #00124d 0%, #0027a3 100%);
        padding: 15px; border-bottom: 3px solid #00d4ff;
        font-weight: 900; font-size: 0.9em; display: flex; 
        justify-content: space-between; border-radius: 12px 12px 0 0;
    }
    
    .team-row { display: flex; align-items: center; padding: 12px 15px; border-bottom: 1px solid #ffffff08; font-size: 0.85em; }
    .team-logo { width: 26px; height: 26px; margin-right: 12px; object-fit: contain; }
    .team-name { flex-grow: 1; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; color: white !important; }
    .stat-val { width: 32px; text-align: center; font-weight: bold; flex-shrink: 0; color: white !important; }
    .header-labels { display: flex; color: #00d4ff; font-size: 0.9em; }

    /* Estilo de los Resultados */
    .results-title { 
        text-align: center; color: #ffffff !important; text-transform: uppercase; 
        letter-spacing: 4px; margin-top: 30px; font-weight: 900; font-size: 2.5em; 
    }
    .match-row { display: flex; align-items: center; justify-content: center; padding: 20px; border-bottom: 1px solid #ffffff08; }
    .match-team { flex: 1; display: flex; align-items: center; font-weight: 700; text-transform: uppercase; font-size: 1em; color: white !important; }
    .match-team.home { justify-content: flex-end; text-align: right; }
    .match-team.away { justify-content: flex-start; text-align: left; }
    .match-score { 
        width: 140px; text-align: center; font-size: 2em; font-weight: 900; 
        color: #00d4ff; letter-spacing: 5px; text-shadow: 0 0 15px rgba(0,212,255,0.4);
    }
    .match-logo { width: 40px; height: 40px; object-fit: contain; }
    
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff 0%, #0055ff 100%);
        color: white !important; border: none; font-weight: bold; border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE NEGOCIO ---
def calcular_tablas():
    stats_global = {}
    for id_eq, info in st.session_state.equipos.items():
        stats_global[info['nombre']] = {
            "nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, 
            "GF": 0, "GC": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']
        }
    for p in st.session_state.partidos:
        l, v, gl, gv = p['local'], p['visitante'], p['goles_l'], p['goles_v']
        if l in stats_global and v in stats_global:
            stats_global[l]["PJ"] += 1; stats_global[v]["PJ"] += 1
            stats_global[l]["GF"] += gl; stats_global[l]["GC"] += gv
            stats_global[v]["GF"] += gv; stats_global[v]["GC"] += gl
            if gl > gv: stats_global[l]["G"] += 1; stats_global[l]["PTS"] += 3; stats_global[v]["P"] += 1
            elif gv > gl: stats_global[v]["G"] += 1; stats_global[v]["PTS"] += 3; stats_global[l]["P"] += 1
            else: stats_global[l]["E"] += 1; stats_global[l]["PTS"] += 1; stats_global[v]["E"] += 1; stats_global[v]["PTS"] += 1
    for e in stats_global: stats_global[e]["DG"] = stats_global[e]["GF"] - stats_global[e]["GC"]
    return stats_global

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    if not load_from_disk():
        equipos_iniciales = {}
        for i in range(1, 21):
            grupo = chr(64 + ((i-1) // 4) + 1) 
            equipos_iniciales[f"ID_{i}"] = {"nombre": f"EQUIPO {i}", "grupo": grupo, "logo": None}
        st.session_state.equipos, st.session_state.partidos = equipos_iniciales, []

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.title("🛡️ Panel COPA NAM")
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        p_in = st.text_input("Contraseña", type="password")
        if st.button("Acceder"):
            if p_in == "admin123": st.session_state.logged_in = True; st.rerun()
    else:
        st.success("Modo Edición")
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        if st.button("Limpiar Datos"): 
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.clear(); st.rerun()

# --- 6. INTERFAZ PRINCIPAL ---
# Título principal del torneo
st.title("🏆 COPA NAM")

if not st.session_state.logged_in:
    t1, t2 = st.tabs(["📊 POSICIONES", "⚽ RESULTADOS"])
    with t1:
        stats = calcular_tablas()
        grupos = sorted(list(set(i['grupo'] for i in st.session_state.equipos.values())))
        c_cols = st.columns(2)
        for idx, g in enumerate(grupos):
            with c_cols[idx % 2]:
                eq_g = sorted([s for k, s in stats.items() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG'], x['GF']), reverse=True)
                html = f'<div class="main-card"><div class="group-header"><span>GROUP {g}</span><div class="header-labels"><span class="stat-val">PJ</span><span class="stat-val">G</span><span class="stat-val">E</span><span class="stat-val">P</span><span class="stat-val">GF</span><span class="stat-val">GC</span><span class="stat-val">DG</span><span class="stat-val">PTS</span></div></div>'
                for eq in eq_g:
                    l_src = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html += f'<div class="team-row"><img src="{l_src}" class="team-logo"><span class="team-name">{eq["nombre"]}</span><span class="stat-val">{eq["PJ"]}</span><span class="stat-val">{eq["G"]}</span><span class="stat-val">{eq["E"]}</span><span class="stat-val">{eq["P"]}</span><span class="stat-val">{eq["GF"]}</span><span class="stat-val">{eq["GC"]}</span><span class="stat-val">{eq["DG"]}</span><span class="stat-val">{eq["PTS"]}</span></div>'
                st.markdown(html + '</div>', unsafe_allow_html=True)
    with t2:
        if not st.session_state.partidos: st.info("Sin resultados registrados.")
        else:
            # Aquí aplicamos la clase results-title que forzamos en el CSS
            st.markdown('<h1 class="results-title">RESULTADOS</h1>', unsafe_allow_html=True)
            html_res = '<div class="main-card">'
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for p in reversed(st.session_state.partidos):
                s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html_res += f'<div class="match-row"><div class="match-team home"><span>{p["local"]}</span><img src="{s_l}" class="match-logo"></div><div class="match-score">{p["goles_l"]}-{p["goles_v"]}</div><div class="match-team away"><img src="{s_v}" class="match-logo"><span>{p["visitante"]}</span></div></div>'
            st.markdown(html_res + '</div>', unsafe_allow_html=True)
else:
    # VISTA ADMIN
    tm, tr = st.tabs(["⚙️ EQUIPOS", "⚽ PARTIDO"])
    with tm:
        for id_e, inf in st.session_state.equipos.items():
            with st.expander(f"Editar {inf['nombre']}"):
                c1, c2 = st.columns(2)
                nn = c1.text_input("Nombre", inf['nombre'], key=f"nn{id_e}")
                ng = c1.selectbox("Grupo", ["A", "B", "C", "D", "E"], index=ord(inf['grupo'])-65, key=f"ng{id_e}")
                nl = c2.file_uploader("Logo", type=["png", "jpg"], key=f"nl{id_e}")
                if st.button("Guardar", key=f"bt{id_e}"):
                    st.session_state.equipos[id_e].update({"nombre": nn.upper(), "grupo": ng})
                    if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                    save_to_disk(); st.rerun()
    with tr:
        gs = st.selectbox("Grupo", ["A", "B", "C", "D", "E"], key="gs")
        eqs = [i['nombre'] for i in st.session_state.equipos.values() if i['grupo'] == gs]
        c1, c2 = st.columns(2)
        lo, vi = c1.selectbox("Local", eqs), c2.selectbox("Visitante", eqs)
        gl, gv = c1.number_input(f"Goles {lo}", 0, key="gl"), c2.number_input(f"Goles {vi}", 0, key="gv")
        if st.button("Registrar"):
            if lo != vi:
                st.session_state.partidos.append({"grupo": gs, "local": lo, "visitante": vi, "goles_l": gl, "goles_v": gv})
                save_to_disk(); st.rerun()
