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
    data_to_save = {
        "partidos": st.session_state.partidos,
        "equipos": {},
        "fase_final": st.session_state.fase_final
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
        "octavos": [{"L": "", "V": "", "gl": 0, "gv": 0} for _ in range(8)],
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

# --- 2. ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top, #00124d 0%, #000422 100%) !important; }
    h1, h2, h3, [data-testid="stHeader"] h1, .results-title { color: #ffffff !important; opacity: 1 !important; }
    .stTabs [data-baseweb="tab"] p { color: white !important; font-weight: 700; font-size: 1.1em; }
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; color: white !important; }

    .main-card {
        background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #00d4ff33; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px);
    }
    .group-header {
        background: linear-gradient(90deg, #00124d 0%, #0027a3 100%);
        padding: 12px; border-bottom: 3px solid #00d4ff; font-weight: 900; font-size: 0.85em;
        display: flex; justify-content: space-between; border-radius: 12px 12px 0 0;
    }
    .team-row { display: flex; align-items: center; padding: 10px 15px; border-bottom: 1px solid #ffffff10; font-size: 0.8em; }
    .team-logo { width: 22px; height: 22px; margin-right: 10px; object-fit: contain; }
    .team-name { flex-grow: 1; text-transform: uppercase; font-weight: 700; }
    .stat-val { width: 30px; text-align: center; font-weight: bold; flex-shrink: 0; }
    .header-labels { display: flex; color: #00d4ff; font-size: 0.9em; }

    /* Bracket Estilos */
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; min-width: 1000px; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 700px; width: 18%; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border: 1px solid #00d4ff55; border-radius: 4px; padding: 5px; margin: 10px 0; }
    .team-row-ko { display: flex; align-items: center; justify-content: space-between; padding: 4px; border-bottom: 1px solid #ffffff11; font-size: 0.75em; }
    .ko-logo { width: 18px; height: 18px; object-fit: contain; margin-right: 5px; }
    .ko-name { flex-grow: 1; text-transform: uppercase; font-weight: 600; overflow: hidden; text-overflow: ellipsis; }
    .ko-score { background: #00d4ff; color: #000; font-weight: 900; width: 22px; text-align: center; border-radius: 2px; }
    .final-center { width: 24%; display: flex; flex-direction: column; align-items: center; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE NEGOCIO ---
def get_team_info(name):
    for info in st.session_state.equipos.values():
        if info['nombre'] == name: return info
    return {"nombre": name, "logo": None}

def render_match(match):
    t1 = get_team_info(match["L"])
    t2 = get_team_info(match["V"])
    l1 = f"data:image/png;base64,{img_to_base64(t1['logo'])}" if t1['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    l2 = f"data:image/png;base64,{img_to_base64(t2['logo'])}" if t2['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    n1 = t1['nombre'] if t1['nombre'] else "---"
    n2 = t2['nombre'] if t2['nombre'] else "---"
    return f'<div class="match-box-ko"><div class="team-row-ko"><img src="{l1}" class="ko-logo"><span class="ko-name">{n1}</span><span class="ko-score">{match["gl"]}</span></div><div class="team-row-ko"><img src="{l2}" class="ko-logo"><span class="ko-name">{n2}</span><span class="ko-score">{match["gv"]}</span></div></div>'

def calcular_tablas():
    stats = {}
    for info in st.session_state.equipos.values():
        stats[info['nombre']] = {"nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']}
    for p in st.session_state.partidos:
        l, v, gl, gv = p['local'], p['visitante'], p['goles_l'], p['goles_v']
        if l in stats and v in stats:
            stats[l]["PJ"] += 1; stats[v]["PJ"] += 1
            stats[l]["GF"] += gl; stats[l]["GC"] += gv
            stats[v]["GF"] += gv; stats[v]["GC"] += gl
            if gl > gv: stats[l]["G"] += 1; stats[l]["PTS"] += 3; stats[v]["P"] += 1
            elif gv > gl: stats[v]["G"] += 1; stats[v]["PTS"] += 3; stats[l]["P"] += 1
            else: stats[l]["E"] += 1; stats[l]["PTS"] += 1; stats[v]["E"] += 1; stats[v]["PTS"] += 1
    for e in stats: stats[e]["DG"] = stats[e]["GF"] - stats[e]["GC"]
    return stats

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    if not load_from_disk():
        st.session_state.equipos = {f"ID_{i}": {"nombre": f"EQUIPO {i}", "grupo": chr(64 + ((i-1) // 4) + 1), "logo": None} for i in range(1, 21)}
        st.session_state.partidos = []
        st.session_state.fase_final = inicializar_fase_final()

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.title("🛡️ Panel COPA NAM")
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not st.session_state.logged_in:
        if st.text_input("Clave", type="password") == "admin123":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("❌ Salir"): st.session_state.logged_in = False; st.rerun()
        if st.button("🗑️ Reset"): 
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.clear(); st.rerun()

# --- 6. INTERFAZ PRINCIPAL ---
st.title("🏆 COPA NAM")

if not st.session_state.logged_in:
    # EL ORDEN AQUÍ DEFINE QUE "POSICIONES" SEA LA PRIMERA PESTAÑA POR DEFECTO
    t_pos, t_fnal, t_res = st.tabs(["📊 POSICIONES", "🏆 FASE FINAL", "⚽ RESULTADOS"])
    
    with t_pos:
        stats_data = calcular_tablas()
        grupos = sorted(list(set(i['grupo'] for i in st.session_state.equipos.values())))
        cols_g = st.columns(2)
        for idx, g in enumerate(grupos):
            with cols_g[idx % 2]:
                eq_g = sorted([s for k, s in stats_data.items() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG'], x['GF']), reverse=True)
                html_g = f'<div class="main-card"><div class="group-header"><span>GRUPO {g}</span><div class="header-labels"><span class="stat-val">PJ</span><span class="stat-val">G</span><span class="stat-val">E</span><span class="stat-val">P</span><span class="stat-val">DG</span><span class="stat-val">PTS</span></div></div>'
                for eq in eq_g:
                    img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html_g += f'<div class="team-row"><img src="{img}" class="team-logo"><span class="team-name">{eq["nombre"]}</span><span class="stat-val">{eq["PJ"]}</span><span class="stat-val">{eq["G"]}</span><span class="stat-val">{eq["E"]}</span><span class="stat-val">{eq["P"]}</span><span class="stat-val">{eq["DG"]}</span><span class="stat-val">{eq["PTS"]}</span></div>'
                st.markdown(html_g + '</div>', unsafe_allow_html=True)

    with t_fnal:
        ff = st.session_state.fase_final
        st.markdown('<h2 style="text-align:center; color:#00d4ff !important;">CUADRO DE ELIMINATORIAS</h2>', unsafe_allow_html=True)
        html_bracket = f'''
        <div class="bracket-wrapper">
            <div class="bracket-column">
                <h4 style="text-align:center">OCTAVOS</h4>
                {render_match(ff["octavos"][0])} {render_match(ff["octavos"][1])}
                {render_match(ff["octavos"][2])} {render_match(ff["octavos"][3])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center">CUARTOS</h4>
                {render_match(ff["cuartos"][0])} {render_match(ff["cuartos"][1])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center">SEMIS</h4>
                {render_match(ff["semis"][0])}
            </div>
            <div class="final-center">
                <img src="https://logodownload.org/wp-content/uploads/2016/03/champions-league-logo-0.png" style="width:100px; filter:drop-shadow(0 0 10px #00d4ff);">
                <h2 style="color:#00d4ff !important; margin:10px 0;">FINAL</h2>
                {render_match(ff["final"])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center">SEMIS</h4>
                {render_match(ff["semis"][1])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center">CUARTOS</h4>
                {render_match(ff["cuartos"][2])} {render_match(ff["cuartos"][3])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center">OCTAVOS</h4>
                {render_match(ff["octavos"][4])} {render_match(ff["octavos"][5])}
                {render_match(ff["octavos"][6])} {render_match(ff["octavos"][7])}
            </div>
        </div>
        '''
        st.markdown(html_bracket, unsafe_allow_html=True)

    with t_res:
        if st.session_state.partidos:
            st.markdown('<h1 class="results-title">RESULTADOS RECIENTES</h1>', unsafe_allow_html=True)
            html_res = '<div class="main-card">'
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for p in reversed(st.session_state.partidos):
                s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html_res += f'<div class="match-row"><div class="match-team home"><span>{p["local"]}</span><img src="{s_l}" class="match-logo"></div><div class="match-score">{p["goles_l"]}-{p["goles_v"]}</div><div class="match-team away"><img src="{s_v}" class="match-logo"><span>{p["visitante"]}</span></div></div>'
            st.markdown(html_res + '</div>', unsafe_allow_html=True)

else:
    adm_t1, adm_t2, adm_t3 = st.tabs(["⚙️ EQUIPOS", "⚽ GRUPOS", "🏆 FASE FINAL"])
    with adm_t1:
        for id_e, inf in st.session_state.equipos.items():
            with st.expander(f"Editar {inf['nombre']}"):
                c1, c2 = st.columns(2)
                nn = c1.text_input("Nombre", inf['nombre'], key=f"nn{id_e}")
                nl = c2.file_uploader("Logo", type=["png", "jpg"], key=f"nl{id_e}")
                if st.button("Guardar", key=f"bt{id_e}"):
                    st.session_state.equipos[id_e].update({"nombre": nn.upper()})
                    if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                    save_to_disk(); st.rerun()
    with adm_t2:
        eqs_all = [i['nombre'] for i in st.session_state.equipos.values()]
        c1, c2 = st.columns(2)
        lo, vi = c1.selectbox("Local", eqs_all), c2.selectbox("Visitante", eqs_all)
        gl, gv = c1.number_input("Goles L", 0, key="gl_adm"), c2.number_input("Goles V", 0, key="gv_adm")
        if st.button("Registrar Grupo"):
            st.session_state.partidos.append({"local": lo, "visitante": vi, "goles_l": gl, "goles_v": gv})
            save_to_disk(); st.rerun()
    with adm_t3:
        st.subheader("Cargar Fase Final")
        eqs_ko = [""] + [i['nombre'] for i in st.session_state.equipos.values()]
        for fase in ["octavos", "cuartos", "semis", "final"]:
            with st.expander(f"GESTIONAR {fase.upper()}"):
                if fase == "final":
                    c1, c2, c3, c4 = st.columns(4)
                    st.session_state.fase_final[fase]["L"] = c1.selectbox("Finalista 1", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase]["L"]) if st.session_state.fase_final[fase]["L"] in eqs_ko else 0, key="fin1")
                    st.session_state.fase_final[fase]["V"] = c2.selectbox("Finalista 2", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase]["V"]) if st.session_state.fase_final[fase]["V"] in eqs_ko else 0, key="fin2")
                    st.session_state.fase_final[fase]["gl"] = c3.number_input("Goles F1", value=st.session_state.fase_final[fase]["gl"], key="fgl")
                    st.session_state.fase_final[fase]["gv"] = c4.number_input("Goles F2", value=st.session_state.fase_final[fase]["gv"], key="fgv")
                else:
                    for i in range(len(st.session_state.fase_final[fase])):
                        st.write(f"Partido {i+1}")
                        c1, c2, c3, c4 = st.columns(4)
                        st.session_state.fase_final[fase][i]["L"] = c1.selectbox(f"Local {fase}{i}", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase][i]["L"]) if st.session_state.fase_final[fase][i]["L"] in eqs_ko else 0, key=f"l{fase}{i}")
                        st.session_state.fase_final[fase][i]["V"] = c2.selectbox(f"Vis. {fase}{i}", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase][i]["V"]) if st.session_state.fase_final[fase][i]["V"] in eqs_ko else 0, key=f"v{fase}{i}")
                        st.session_state.fase_final[fase][i]["gl"] = c3.number_input(f"GL {fase}{i}", value=st.session_state.fase_final[fase][i]["gl"], key=f"gl{fase}{i}")
                        st.session_state.fase_final[fase][i]["gv"] = c4.number_input(f"GV {fase}{i}", value=st.session_state.fase_final[fase][i]["gv"], key=f"gv{fase}{i}")
        if st.button("💾 GUARDAR FASE FINAL"):
            save_to_disk(); st.success("Guardado!"); st.rerun()
