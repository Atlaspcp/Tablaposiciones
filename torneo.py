import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os

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
            "nombre": info["nombre"],
            "grupo": info["grupo"],
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
                equipos_cargados = {}
                for id_eq, info in data.get("equipos", {}).items():
                    logo_pil = None
                    if info["logo"]:
                        logo_pil = Image.open(io.BytesIO(base64.b64decode(info["logo"])))
                    equipos_cargados[id_eq] = {"nombre": info["nombre"], "grupo": info["grupo"], "logo": logo_pil}
                st.session_state.equipos = equipos_cargados
                return True
        except: return False
    return False

# --- 2. ESTILOS CSS (MÓVIL ADAPTATIVO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top, #00124d 0%, #000422 100%) !important; }
    
    .txt-celeste { color: #7db1ff !important; }
    .txt-red { color: #ff3b3b !important; }
    .txt-white { color: #ffffff !important; }

    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: white !important; font-weight: 900; }
    
    /* Título Adaptativo */
    .nam-title { font-size: clamp(2em, 8vw, 4.5em); text-align: center; font-weight: 900; margin-bottom: 10px; letter-spacing: -2px; color: white; }

    /* Sidebar Negro */
    [data-testid="stSidebar"] h2 { color: #000000 !important; }

    .main-card {
        background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #FFD70033; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px);
        overflow-x: auto; /* Permitir scroll si la tabla es muy ancha */
    }
    
    .group-header {
        background: linear-gradient(90deg, #00124d 0%, #ff3b3b33 100%);
        padding: 12px 10px; border-bottom: 3px solid #FFD700; font-weight: 900;
        display: flex; align-items: center; min-width: 450px; /* Asegura que las letras no se pisen */
    }
    .group-title { flex-grow: 1; font-size: 1em; color: white; }
    
    .team-row { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #ffffff10; font-size: 0.85em; min-width: 450px; }
    .team-logo { width: 22px; height: 22px; margin-right: 8px; object-fit: contain; }
    .team-name { flex-grow: 1; text-transform: uppercase; font-weight: 700; color: #ffffff; }
    
    /* Columnas fijas */
    .stat-col { width: 35px; text-align: center; font-weight: bold; flex-shrink: 0; color: white !important; }
    .header-labels { display: flex; color: white !important; font-size: 0.8em; }

    /* Fase Final con Scroll para celular */
    .bracket-scroll-container { overflow-x: auto; width: 100%; padding-bottom: 20px; }
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; min-width: 900px; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 500px; width: 200px; }
    .bracket-column h4 { color: white !important; text-align: center; font-size: 0.9em; margin-bottom: 5px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 6px; border: 1px solid #FFD70044; padding: 6px; margin: 10px 0; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 22px; text-align: center; border-radius: 2px; }
    .final-center { width: 250px; display: flex; flex-direction: column; align-items: center; text-align: center; }

    /* Goleadores */
    .gol-header { display: flex; align-items: center; padding: 12px 15px; background: rgba(0,0,0,0.2); border-bottom: 2px solid #FFD700; font-weight: 900; min-width: 400px; }
    .gol-row { display: flex; align-items: center; padding: 10px 15px; border-bottom: 1px solid #ffffff10; min-width: 400px; }
    .gol-name { flex-grow: 1; font-weight: 700; text-transform: uppercase; font-size: 0.9em; }
    .gol-team { width: 150px; text-align: center; color: #FFD700; font-size: 0.8em; }
    .gol-stat { width: 50px; text-align: center; font-weight: 900; color: white !important; }
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
    n1, n2 = (t1['nombre'] or "---"), (t2['nombre'] or "---")
    return f'<div class="match-box-ko"><div class="team-row" style="border:none; padding:2px; min-width:0;"><img src="{img1}" class="team-logo"><span class="team-name" style="font-size:0.7em">{n1}</span><span class="ko-score">{match["gl"]}</span></div><div class="team-row" style="border:none; padding:2px; min-width:0;"><img src="{img2}" class="team-logo"><span class="team-name" style="font-size:0.7em">{n2}</span><span class="ko-score">{match["gv"]}</span></div></div>'

def calcular_tablas():
    stats = {info['nombre']: {"nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']} for info in st.session_state.equipos.values()}
    for p in st.session_state.partidos:
        l, v, gl, gv = p['local'], p['visitante'], p['goles_l'], p['goles_v']
        if l in stats and v in stats:
            stats[l]["PJ"] += 1; stats[v]["PJ"] += 1
            stats[l]["GF"] += gl; stats[l]["GC"] += gv
            stats[v]["GF"] += gv; stats[v]["GC"] += gl
            stats[l]["DG"] = stats[l]["GF"] - stats[l]["GC"]
            stats[v]["DG"] = stats[v]["GF"] - stats[v]["GC"]
            if gl > gv:
                stats[l]["G"] += 1; stats[l]["PTS"] += 3
                stats[v]["P"] += 1
            elif gv > gl:
                stats[v]["G"] += 1; stats[v]["PTS"] += 3
                stats[l]["P"] += 1
            else:
                stats[l]["E"] += 1; stats[l]["PTS"] += 1
                stats[v]["E"] += 1; stats[v]["PTS"] += 1
    return stats

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    st.session_state.logo_torneo = None
    st.session_state.logo_final = None
    if not load_from_disk():
        st.session_state.equipos = {f"ID_{i}": {"nombre": f"EQUIPO {i}", "grupo": chr(64 + ((i-1) // 4) + 1), "logo": None} for i in range(1, 21)}
        st.session_state.partidos, st.session_state.goleadores = [], []
        st.session_state.fase_final = inicializar_fase_final()

# --- 5. INTERFAZ ---
st.markdown('<h1 class="nam-title">#<span class="txt-celeste">N</span><span class="txt-red">A</span>MLEAGUE2026</h1>', unsafe_allow_html=True)

if not st.session_state.get('logged_in', False):
    t_pos, t_ff, t_res, t_gol = st.tabs(["📊 POSICIONES", "🏆 FASE FINAL", "⚽ RESULTADOS", "👟 GOLEADORES"])
    
    with t_pos:
        stats_data = calcular_tablas()
        grupos = sorted(list(set(i['grupo'] for i in st.session_state.equipos.values())))
        for g in grupos:
            eq_g = sorted([s for s in stats_data.values() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG'], x['GF']), reverse=True)
            html = f'''
            <div class="main-card">
                <div class="group-header">
                    <span class="group-title">GRUPO {g}</span>
                    <div class="header-labels">
                        <span class="stat-col">PJ</span><span class="stat-col">G</span><span class="stat-col">E</span><span class="stat-col">P</span>
                        <span class="stat-col">GF</span><span class="stat-col">GC</span><span class="stat-col">DG</span><span class="stat-col">PTS</span>
                    </div>
                </div>'''
            for eq in eq_g:
                img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html += f'''
                <div class="team-row">
                    <img src="{img}" class="team-logo">
                    <span class="team-name">{eq["nombre"]}</span>
                    <span class="stat-col">{eq["PJ"]}</span><span class="stat-col">{eq["G"]}</span><span class="stat-col">{eq["E"]}</span><span class="stat-col">{eq["P"]}</span>
                    <span class="stat-col">{eq["GF"]}</span><span class="stat-col">{eq["GC"]}</span><span class="stat-col">{eq["DG"]}</span><span class="stat-col" style="color:white !important">{eq["PTS"]}</span>
                </div>'''
            st.markdown(html + '</div>', unsafe_allow_html=True)

    with t_ff:
        ff = st.session_state.fase_final
        st.info("💡 Desliza hacia los lados para ver el cuadro completo en el móvil.")
        html_ff = f'''
        <div class="bracket-scroll-container">
            <div class="bracket-wrapper">
                <div class="bracket-column">
                    <h4>CUARTOS</h4>
                    {render_match(ff["cuartos"][0])} {render_match(ff["cuartos"][1])}
                </div>
                <div class="bracket-column">
                    <h4>SEMIFINAL</h4>
                    {render_match(ff["semis"][0])}
                </div>
                <div class="final-center">
                    {"<img src='data:image/png;base64," + img_to_base64(st.session_state.logo_final) + "' style='width:120px; filter:drop-shadow(0 0 10px #FFD700);'>" if st.session_state.logo_final else "<h2>FINAL</h2>"}
                    <h1 style="color:white !important; font-size:1.5em; margin:10px 0;">GRAN FINAL</h1>
                    {render_match(ff["final"])}
                </div>
                <div class="bracket-column">
                    <h4>SEMIFINAL</h4>
                    {render_match(ff["semis"][1])}
                </div>
                <div class="bracket-column">
                    <h4>CUARTOS</h4>
                    {render_match(ff["cuartos"][2])} {render_match(ff["cuartos"][3])}
                </div>
            </div>
        </div>'''
        st.markdown(html_ff, unsafe_allow_html=True)

    with t_res:
        if st.session_state.partidos:
            html_res = '<div class="main-card">'
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for p in reversed(st.session_state.partidos):
                s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html_res += f'<div class="match-row" style="display:flex; align-items:center; justify-content:center; padding:15px; border-bottom:1px solid #ffffff11; min-width:400px;"><div style="flex:1; text-align:right;">{p["local"]} <img src="{s_l}" width="20"></div><div style="width:80px; text-align:center; color:#FFD700; font-weight:900;">{p["goles_l"]}-{p["goles_v"]}</div><div style="flex:1; text-align:left;"><img src="{s_v}" width="20"> {p["visitante"]}</div></div>'
            st.markdown(html_res + '</div>', unsafe_allow_html=True)

    with t_gol:
        if st.session_state.goleadores:
            html_gol = f'''
            <div class="main-card">
                <div class="gol-header">
                    <span style="flex-grow:1">JUGADOR</span><span style="width:150px; text-align:center">EQUIPO</span><span style="width:50px; text-align:center">GOLES</span>
                </div>'''
            for g in st.session_state.goleadores:
                html_gol += f'''
                <div class="gol-row">
                    <span class="gol-name">{g["nombre"]}</span><span class="gol-team">{g["equipo"]}</span><span class="gol-stat">{g["goles"]}</span>
                </div>'''
            st.markdown(html_gol + '</div>', unsafe_allow_html=True)

# --- 6. PANEL ADMINISTRADOR ---
with st.sidebar:
    st.header("🔐 Configuración NAM") 
    if not st.session_state.get('logged_in', False):
        if st.text_input("Clave", type="password") == "admin123":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        adm_tabs = st.tabs(["LOGOS", "EQ", "GR", "ELIM", "GOL"])
        # ... (El resto de la lógica de administración se mantiene igual)
