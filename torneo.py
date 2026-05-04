import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN Y PERSISTENCIA ---
st.set_page_config(page_title="#NAMLEAGUE2026", layout="wide")

DB_FILE = "torneo_data.json"

def img_to_base64(image):
    if image is None: return None
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except: return None

def save_to_disk():
    data_to_save = {
        "partidos": st.session_state.partidos,
        "equipos": {},
        "fase_final": st.session_state.fase_final,
        "goleadores": st.session_state.goleadores,
        "logo_torneo": img_to_base64(st.session_state.logo_torneo),
        "logo_final": img_to_base64(st.session_state.logo_final)
    }
    for id_eq, info in st.session_state.equipos.items():
        data_to_save["equipos"][id_eq] = {
            "nombre": info["nombre"], "grupo": info["grupo"],
            "logo": img_to_base64(info["logo"])
        }
    with open(DB_FILE, "w") as f:
        json.dump(data_to_save, f)

def inicializar_fase_final():
    return {
        "cuartos": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(4)],
        "semis": [{"L": "", "V": "", "gl": None, "gv": None} for _ in range(2)],
        "final": {"L": "", "V": "", "gl": None, "gv": None}
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
    
    [data-testid="stSidebar"] { background-color: #f0f2f6; }
    
    .main-card {
        background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #FFD70033; color: white; backdrop-filter: blur(10px);
    }
    .grid-posiciones { display: grid; grid-template-columns: 2fr repeat(8, 45px); align-items: center; min-width: 650px; padding: 10px 15px; }
    .grid-goleadores { display: grid; grid-template-columns: 2fr 1.5fr 1fr; align-items: center; min-width: 500px; padding: 10px 15px; }
    .header-grid { background: linear-gradient(90deg, #00124d 0%, #ff3b3b33 100%); border-bottom: 3px solid #FFD700; font-weight: 900; }
    .stat-cell { text-align: center; font-weight: bold; }

    /* Estructura Bracket */
    .bracket-scroll { overflow-x: auto; width: 100%; padding: 20px 0; }
    .bracket-wrapper { display: flex; justify-content: space-around; align-items: center; min-width: 1100px; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 500px; width: 220px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 8px; border: 1px solid #FFD70044; padding: 10px; margin: 10px 0; width: 100%; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 30px; text-align: center; border-radius: 3px; display: inline-block; }
    .final-center { width: 300px; text-align: center; display: flex; flex-direction: column; align-items: center; }
    
    .date-divider { background: #FFD700; color: black; padding: 5px 20px; font-weight: 900; border-radius: 4px; margin: 20px 0 10px 0; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE NEGOCIO ---
def get_team_info(name):
    for info in st.session_state.equipos.values():
        if info['nombre'] == name: return info
    return {"nombre": name or "TBD", "logo": None}

def render_match(match):
    t1 = get_team_info(match["L"])
    t2 = get_team_info(match["V"])
    gl = match["gl"] if match["gl"] is not None else "-"
    gv = match["gv"] if match["gv"] is not None else "-"
    
    img1 = f"data:image/png;base64,{img_to_base64(t1['logo'])}" if t1['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    img2 = f"data:image/png;base64,{img_to_base64(t2['logo'])}" if t2['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    
    return f'''
    <div class="match-box-ko">
        <div style="display:flex; align-items:center; justify-content: space-between; margin-bottom:8px;">
            <div style="display:flex; align-items:center; overflow:hidden;">
                <img src="{img1}" style="width:20px; height:20px; margin-right:8px; flex-shrink:0;">
                <span style="font-size:0.75em; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{t1["nombre"]}</span>
            </div>
            <span class="ko-score">{gl}</span>
        </div>
        <div style="display:flex; align-items:center; justify-content: space-between;">
            <div style="display:flex; align-items:center; overflow:hidden;">
                <img src="{img2}" style="width:20px; height:20px; margin-right:8px; flex-shrink:0;">
                <span style="font-size:0.75em; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{t2["nombre"]}</span>
            </div>
            <span class="ko-score">{gv}</span>
        </div>
    </div>
    '''

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
            if gl > gv: stats[l]["G"] += 1; stats[l]["PTS"] += 3; stats[v]["P"] += 1
            elif gv > gl: stats[v]["G"] += 1; stats[v]["PTS"] += 3; stats[l]["P"] += 1
            else: stats[l]["E"] += 1; stats[l]["PTS"] += 1; stats[v]["E"] += 1; stats[v]["PTS"] += 1
    return stats

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    st.session_state.logo_torneo = st.session_state.logo_final = None
    if not load_from_disk():
        st.session_state.equipos = {f"ID_{i}": {"nombre": f"EQUIPO {i}", "grupo": chr(64 + ((i-1) // 4) + 1), "logo": None} for i in range(1, 21)}
        st.session_state.partidos, st.session_state.goleadores = [], []
        st.session_state.fase_final = inicializar_fase_final()

# --- 5. INTERFAZ PÚBLICA ---
st.markdown('<h1 class="nam-title">#<span class="txt-celeste">N</span><span class="txt-red">A</span>MLEAGUE2026</h1>', unsafe_allow_html=True)

if not st.session_state.get('logged_in', False):
    t_pos, t_ff, t_res, t_gol = st.tabs(["📊 POSICIONES", "🏆 FASE FINAL", "⚽ RESULTADOS", "👟 GOLEADORES"])
    
    with t_pos:
        stats_data = calcular_tablas()
        for g in sorted(list(set(i['grupo'] for i in st.session_state.equipos.values()))):
            eq_g = sorted([s for s in stats_data.values() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG'], x['GF']), reverse=True)
            html = f'<div class="main-card"><div class="grid-posiciones header-grid"><span>GRUPO {g}</span><span class="stat-cell">PJ</span><span class="stat-cell">G</span><span class="stat-cell">E</span><span class="stat-cell">P</span><span class="stat-cell">GF</span><span class="stat-cell">GC</span><span class="stat-cell">DG</span><span class="stat-cell">PTS</span></div>'
            for eq in eq_g:
                img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html += f'<div class="grid-posiciones" style="border-bottom:1px solid #ffffff10;"><div style="display:flex;align-items:center;"><img src="{img}" style="width:24px;margin-right:12px;">{eq["nombre"]}</div><span class="stat-cell">{eq["PJ"]}</span><span class="stat-cell">{eq["G"]}</span><span class="stat-cell">{eq["E"]}</span><span class="stat-cell">{eq["P"]}</span><span class="stat-cell">{eq["GF"]}</span><span class="stat-cell">{eq["GC"]}</span><span class="stat-cell">{eq["DG"]}</span><span class="stat-cell" style="color:#FFD700">{eq["PTS"]}</span></div>'
            st.markdown(html + '</div>', unsafe_allow_html=True)

    with t_ff:
        ff = st.session_state.fase_final
        logo_f_base64 = img_to_base64(st.session_state.logo_final)
        logo_html = f'<img src="data:image/png;base64,{logo_f_base64}" width="160" style="filter:drop-shadow(0 0 15px #FFD700)">' if logo_f_base64 else '<h2>FINAL</h2>'
        
        html_bracket = f'''
        <div class="bracket-scroll">
            <div class="bracket-wrapper">
                <div class="bracket-column">
                    <h4>CUARTOS</h4>
                    {render_match(ff["cuartos"][0])}
                    {render_match(ff["cuartos"][1])}
                </div>
                <div class="bracket-column">
                    <h4>SEMIFINAL</h4>
                    {render_match(ff["semis"][0])}
                </div>
                <div class="final-center">
                    {logo_html}
                    <h1 style="color:white !important;margin:15px 0;">GRAN FINAL</h1>
                    {render_match(ff["final"])}
                </div>
                <div class="bracket-column">
                    <h4>SEMIFINAL</h4>
                    {render_match(ff["semis"][1])}
                </div>
                <div class="bracket-column">
                    <h4>CUARTOS</h4>
                    {render_match(ff["cuartos"][2])}
                    {render_match(ff["cuartos"][3])}
                </div>
            </div>
        </div>
        '''
        st.markdown(html_bracket, unsafe_allow_html=True)

    with t_res:
        if st.session_state.partidos:
            df = pd.DataFrame(st.session_state.partidos).sort_values(by="fecha", ascending=False)
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for f in df['fecha'].unique():
                st.markdown(f'<div class="date-divider">{f}</div>', unsafe_allow_html=True)
                html_res = '<div class="main-card">'
                for _, p in df[df['fecha'] == f].iterrows():
                    s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html_res += f'<div style="display:flex;align-items:center;justify-content:center;padding:15px;border-bottom:1px solid #ffffff11;"><div style="flex:1;text-align:right;">{p["local"]} <img src="{s_l}" width="24"></div><div style="width:110px;text-align:center;color:#FFD700;font-weight:900;font-size:1.5em;">{p["goles_l"]}-{p["goles_v"]}</div><div style="flex:1;text-align:left;"><img src="{s_v}" width="24"> {p["visitante"]}</div></div>'
                st.markdown(html_res + '</div>', unsafe_allow_html=True)

    with t_gol:
        if st.session_state.goleadores:
            html_gol = '<div class="main-card"><div class="grid-goleadores header-grid"><span>JUGADOR</span><span class="stat-cell">EQUIPO</span><span class="stat-cell">GOLES</span></div>'
            for g in sorted(st.session_state.goleadores, key=lambda x: x['goles'], reverse=True):
                html_gol += f'<div class="grid-goleadores" style="border-bottom:1px solid #ffffff10;"><span style="font-weight:700;">{g["nombre"]}</span><span class="stat-cell" style="color:#FFD700;">{g["equipo"]}</span><span class="stat-cell">{g["goles"]}</span></div>'
            st.markdown(html_gol + '</div>', unsafe_allow_html=True)

# --- 6. PANEL ADMINISTRADOR ---
with st.sidebar:
    st.header("🔐 Admin")
    if not st.session_state.get('logged_in', False):
        if st.text_input("Clave", type="password") == "admin123":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        adm_t = st.tabs(["LOGOS", "EQ", "GR", "ELIM", "GOL", "💾"])
        
        with adm_t[0]:
            lt, lf = st.file_uploader("Logo Torneo"), st.file_uploader("Logo Final")
            if st.button("Cargar Logos"):
                if lt: st.session_state.logo_torneo = Image.open(lt)
                if lf: st.session_state.logo_final = Image.open(lf)
                save_to_disk(); st.rerun()
        
        with adm_t[1]:
            for id_e, inf in st.session_state.equipos.items():
                with st.expander(f"Editar {inf['nombre']}"):
                    n = st.text_input("Nombre", inf['nombre'], key=f"n{id_e}")
                    l = st.file_uploader("Logo", key=f"l{id_e}")
                    if st.button("OK", key=f"b{id_e}"):
                        st.session_state.equipos[id_e]['nombre'] = n.upper()
                        if l: st.session_state.equipos[id_e]['logo'] = Image.open(l)
                        save_to_disk(); st.rerun()

        with adm_t[2]:
            eqs = sorted([i['nombre'] for i in st.session_state.equipos.values()])
            fecha = st.date_input("Fecha")
            l, v = st.selectbox("Local", eqs), st.selectbox("Visitante", eqs)
            gl, gv = st.number_input("GL", 0), st.number_input("GV", 0)
            if st.button("Guardar Partido"):
                st.session_state.partidos.append({"fecha": str(fecha), "local": l, "visitante": v, "goles_l": gl, "goles_v": gv})
                save_to_disk(); st.rerun()

        with adm_t[3]:
            eqs_ko = [""] + eqs
            for f in ["cuartos", "semis", "final"]:
                with st.expander(f.upper()):
                    matches = st.session_state.fase_final[f]
                    if isinstance(matches, dict): matches = [matches]
                    for i, m in enumerate(matches):
                        m["L"] = st.selectbox(f"Local {f} {i}", eqs_ko, index=eqs_ko.index(m["L"]) if m["L"] in eqs_ko else 0, key=f"l{f}{i}")
                        m["V"] = st.selectbox(f"Visita {f} {i}", eqs_ko, index=eqs_ko.index(m["V"]) if m["V"] in eqs_ko else 0, key=f"v{f}{i}")
                        is_played = st.checkbox("Jugado", value=(m["gl"] is not None), key=f"p{f}{i}")
                        if is_played:
                            m["gl"] = st.number_input("GL", value=m["gl"] or 0, key=f"gl{f}{i}")
                            m["gv"] = st.number_input("GV", value=m["gv"] or 0, key=f"gv{f}{i}")
                        else:
                            m["gl"] = m["gv"] = None
            if st.button("Actualizar Eliminatorias"): save_to_disk(); st.rerun()

        with adm_t[4]:
            n_g = st.text_input("Goleador")
            e_g = st.selectbox("Equipo", eqs, key="egol")
            c_g = st.number_input("Goles", 0)
            if st.button("Añadir Goleador"):
                st.session_state.goleadores.append({"nombre": n_g.upper(), "equipo": e_g, "goles": c_g})
                save_to_disk(); st.rerun()
            for i, gol in enumerate(st.session_state.goleadores):
                st.write(f"{gol['nombre']} ({gol['goles']})")
                if st.button("Eliminar", key=f"dg{i}"):
                    st.session_state.goleadores.pop(i); save_to_disk(); st.rerun()

        with adm_t[5]:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f:
                    st.download_button("Descargar Backup", f.read(), "data.json")
