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

def inicializar_fase_final():
    return {
        "octavos": [{"L": "", "V": "", "gl": 0, "gv": 0} for _ in range(8)],
        "cuartos": [{"L": "", "V": "", "gl": 0, "gv": 0} for _ in range(4)],
        "semis": [{"L": "", "V": "", "gl": 0, "gv": 0} for _ in range(2)],
        "final": {"L": "", "V": "", "gl": 0, "gv": 0}
    }

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

    /* Estilos del Bracket de Fase Final */
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; height: 800px; width: 18%; }
    
    .match-box-knockout {
        background: rgba(0, 20, 80, 0.8); border: 1px solid #00d4ff55;
        border-radius: 4px; padding: 5px; margin: 10px 0; font-size: 0.8em;
    }
    .team-row-ko { display: flex; align-items: center; justify-content: space-between; padding: 4px; border-bottom: 1px solid #ffffff11; }
    .team-row-ko:last-child { border-bottom: none; }
    .ko-logo { width: 20px; height: 20px; object-fit: contain; margin-right: 8px; }
    .ko-name { flex-grow: 1; text-transform: uppercase; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ko-score { background: #00d4ff; color: #000; font-weight: 900; width: 25px; text-align: center; border-radius: 2px; }

    .final-center { width: 24%; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .trophy-img { width: 120px; margin-bottom: 20px; filter: drop-shadow(0 0 15px #00d4ff); }

    .match-team.home { justify-content: flex-end; text-align: right; }
    .match-team.away { justify-content: flex-start; text-align: left; }
    .match-score { color: #00d4ff; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA ---
def get_team_info(name):
    for info in st.session_state.equipos.values():
        if info['nombre'] == name: return info
    return {"nombre": name, "logo": None}

def render_match(match):
    t1 = get_team_info(match["L"])
    t2 = get_team_info(match["V"])
    logo1 = f"data:image/png;base64,{img_to_base64(t1['logo'])}" if t1['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    logo2 = f"data:image/png;base64,{img_to_base64(t2['logo'])}" if t2['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
    
    return f'''
    <div class="match-box-knockout">
        <div class="team-row-ko">
            <img src="{logo1}" class="ko-logo">
            <span class="ko-name">{t1["nombre"] if t1["nombre"] else "---"}</span>
            <span class="ko-score">{match["gl"]}</span>
        </div>
        <div class="team-row-ko">
            <img src="{logo2}" class="ko-logo">
            <span class="ko-name">{t2["nombre"] if t2["nombre"] else "---"}</span>
            <span class="ko-score">{match["gv"]}</span>
        </div>
    </div>
    '''

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
            elif gv > gl: stats_global[v]["G"] += 1; stats[v]["PTS"] += 3; stats[l]["P"] += 1
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
        if st.text_input("Contraseña", type="password") == "admin123":
            if st.button("Acceder"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("❌ Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        if st.button("⚠️ Limpiar Todo"): 
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.clear(); st.rerun()

# --- 6. INTERFAZ PRINCIPAL ---
st.title("🏆 COPA NAM")

if not st.session_state.logged_in:
    t_fnal, t_pos, t_res = st.tabs(["🏆 FASE FINAL", "📊 POSICIONES", "⚽ RESULTADOS"])
    
    with t_fnal:
        ff = st.session_state.fase_final
        st.markdown('<h2 style="text-align:center; color:#00d4ff !important;">ROAD TO MUNICH</h2>', unsafe_allow_html=True)
        
        # BRACKET VISUAL
        col_left, col_mid, col_right = st.columns([2, 1, 2])
        
        # Estructura del bracket en HTML
        bracket_html = f'''
        <div class="bracket-wrapper">
            <!-- IZQUIERDA -->
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
                <h4 style="text-align:center">SEMI</h4>
                {render_match(ff["semis"][0])}
            </div>
            
            <!-- CENTRO -->
            <div class="final-center">
                <img src="https://logodownload.org/wp-content/uploads/2016/03/champions-league-logo-0.png" class="trophy-img">
                <h2 style="color:#00d4ff !important">FINAL</h2>
                {render_match(ff["final"])}
                <p style="font-size:0.8em; margin-top:10px">31 MAYO 2026<br>MUNICH ARENA</p>
            </div>

            <!-- DERECHA -->
            <div class="bracket-column">
                <h4 style="text-align:center">SEMI</h4>
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
        st.markdown(bracket_html, unsafe_allow_html=True)

    with t_pos:
        stats = calcular_tablas()
        grupos = sorted(list(set(i['grupo'] for i in st.session_state.equipos.values())))
        c_cols = st.columns(2)
        for idx, g in enumerate(grupos):
            with c_cols[idx % 2]:
                eq_g = sorted([s for k, s in stats.items() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG']), reverse=True)
                html = f'<div class="main-card"><div class="group-header"><span>GROUP {g}</span><div class="header-labels"><span class="stat-val">PJ</span><span class="stat-val">DG</span><span class="stat-val">PTS</span></div></div>'
                for eq in eq_g:
                    l_src = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html += f'<div class="team-row"><img src="{l_src}" class="team-logo"><span class="team-name">{eq["nombre"]}</span><span class="stat-val">{eq["PJ"]}</span><span class="stat-val">{eq["DG"]}</span><span class="stat-val">{eq["PTS"]}</span></div>'
                st.markdown(html + '</div>', unsafe_allow_html=True)

    with t_res:
        if st.session_state.partidos:
            st.markdown('<h1 class="results-title">RESULTADOS GRUPOS</h1>', unsafe_allow_html=True)
            html_res = '<div class="main-card">'
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for p in reversed(st.session_state.partidos):
                s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html_res += f'<div class="match-row"><div class="match-team home"><span>{p["local"]}</span><img src="{s_l}" class="match-logo"></div><div class="match-score">{p["goles_l"]}-{p["goles_v"]}</div><div class="match-team away"><img src="{s_v}" class="match-logo"><span>{p["visitante"]}</span></div></div>'
            st.markdown(html_res + '</div>', unsafe_allow_html=True)

else:
    # VISTA ADMIN
    adm_tab1, adm_tab2, adm_tab3 = st.tabs(["⚙️ EQUIPOS", "⚽ PARTIDO GRUPO", "🏆 GESTIÓN FASE FINAL"])
    
    with adm_tab1:
        for id_e, inf in st.session_state.equipos.items():
            with st.expander(f"Editar {inf['nombre']}"):
                c1, c2 = st.columns(2)
                nn = c1.text_input("Nombre", inf['nombre'], key=f"nn{id_e}")
                nl = c2.file_uploader("Logo", type=["png", "jpg"], key=f"nl{id_e}")
                if st.button("Guardar", key=f"bt{id_e}"):
                    st.session_state.equipos[id_e].update({"nombre": nn.upper()})
                    if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                    save_to_disk(); st.rerun()

    with adm_tab2:
        eqs_all = [i['nombre'] for i in st.session_state.equipos.values()]
        c1, c2 = st.columns(2)
        lo, vi = c1.selectbox("Local", eqs_all), c2.selectbox("Visitante", eqs_all)
        gl, gv = c1.number_input("Goles L", 0), c2.number_input("Goles V", 0)
        if st.button("Registrar Resultado Grupo"):
            st.session_state.partidos.append({"local": lo, "visitante": vi, "goles_l": gl, "goles_v": gv})
            save_to_disk(); st.rerun()

    with adm_tab3:
        st.subheader("Cargar Equipos y Resultados de Eliminatorias")
        eqs_list = [""] + [i['nombre'] for i in st.session_state.equipos.values()]
        
        fases = ["octavos", "cuartos", "semis", "final"]
        for fase in fases:
            with st.expander(f"Gestionar {fase.upper()}"):
                if fase == "final":
                    c1, c2, c3, c4 = st.columns(4)
                    st.session_state.fase_final[fase]["L"] = c1.selectbox("Equipo A", eqs_list, index=eqs_list.index(st.session_state.fase_final[fase]["L"]) if st.session_state.fase_final[fase]["L"] in eqs_list else 0)
                    st.session_state.fase_final[fase]["V"] = c2.selectbox("Equipo B", eqs_list, index=eqs_list.index(st.session_state.fase_final[fase]["V"]) if st.session_state.fase_final[fase]["V"] in eqs_list else 0)
                    st.session_state.fase_final[fase]["gl"] = c3.number_input("Goles A", value=st.session_state.fase_final[fase]["gl"])
                    st.session_state.fase_final[fase]["gv"] = c4.number_input("Goles B", value=st.session_state.fase_final[fase]["gv"])
                else:
                    for i in range(len(st.session_state.fase_final[fase])):
                        st.write(f"Partido {i+1}")
                        c1, c2, c3, c4 = st.columns(4)
                        st.session_state.fase_final[fase][i]["L"] = c1.selectbox(f"Local P{i+1}", eqs_list, index=eqs_list.index(st.session_state.fase_final[fase][i]["L"]) if st.session_state.fase_final[fase][i]["L"] in eqs_list else 0, key=f"{fase}l{i}")
                        st.session_state.fase_final[fase][i]["V"] = c2.selectbox(f"Vis. P{i+1}", eqs_list, index=eqs_list.index(st.session_state.fase_final[fase][i]["V"]) if st.session_state.fase_final[fase][i]["V"] in eqs_list else 0, key=f"{fase}v{i}")
                        st.session_state.fase_final[fase][i]["gl"] = c3.number_input(f"G {i+1}L", value=st.session_state.fase_final[fase][i]["gl"], key=f"{fase}gl{i}")
                        st.session_state.fase_final[fase][i]["gv"] = c4.number_input(f"G {i+1}V", value=st.session_state.fase_final[fase][i]["gv"], key=f"{fase}gv{i}")
        
        if st.button("💾 Guardar Fase Final"):
            save_to_disk(); st.success("Bracket actualizado!"); st.rerun()
