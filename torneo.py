import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os

# --- 1. CONFIGURACIÓN Y PERSISTENCIA ---
st.set_page_config(page_title="NAM 2026", layout="wide")

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
                
                # Cargar Logos de Torneo
                if data.get("logo_torneo"):
                    st.session_state.logo_torneo = Image.open(io.BytesIO(base64.b64decode(data["logo_torneo"])))
                if data.get("logo_final"):
                    st.session_state.logo_final = Image.open(io.BytesIO(base64.b64decode(data["logo_final"])))
                
                # Cargar Equipos
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

# --- 2. ESTILOS CSS (DORADO + NAM STYLE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top, #00124d 0%, #000422 100%) !important; }
    
    .txt-gold { color: #FFD700 !important; }
    .txt-red { color: #ff3b3b !important; }
    .txt-white { color: #ffffff !important; }

    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: white !important; font-weight: 900; }
    
    .nam-title { font-size: 4.5em; text-align: center; font-weight: 900; margin-bottom: 0px; letter-spacing: -2px; line-height: 1; }

    .main-card {
        background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #FFD70033; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px);
    }
    
    .group-header {
        background: linear-gradient(90deg, #00124d 0%, #ff3b3b33 100%);
        padding: 12px; border-bottom: 3px solid #FFD700; font-weight: 900;
        display: flex; justify-content: space-between; border-radius: 12px 12px 0 0;
    }

    .team-row { display: flex; align-items: center; padding: 10px 15px; border-bottom: 1px solid #ffffff10; font-size: 0.9em; }
    .team-logo { width: 26px; height: 26px; margin-right: 12px; object-fit: contain; }
    .team-name { flex-grow: 1; text-transform: uppercase; font-weight: 700; color: #ffffff; }
    .stat-val { width: 35px; text-align: center; font-weight: bold; color: #FFD700; }

    /* Fase Final */
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 500px; width: 25%; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 6px; border: 1px solid #FFD70044; padding: 8px; margin: 15px 0; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 26px; text-align: center; border-radius: 2px; }
    .final-center { width: 35%; display: flex; flex-direction: column; align-items: center; text-align: center; }
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
    return f'<div class="match-box-ko"><div class="team-row"><img src="{img1}" class="team-logo"><span class="team-name" style="font-size:0.8em">{n1}</span><span class="ko-score">{match["gl"]}</span></div><div class="team-row"><img src="{img2}" class="team-logo"><span class="team-name" style="font-size:0.8em">{n2}</span><span class="ko-score">{match["gv"]}</span></div></div>'

def calcular_tablas():
    stats = {info['nombre']: {"nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']} for info in st.session_state.equipos.values()}
    for p in st.session_state.partidos:
        l, v, gl, gv = p['local'], p['visitante'], p['goles_l'], p['goles_v']
        if l in stats and v in stats:
            stats[l]["PJ"] += 1; stats[v]["PJ"] += 1
            stats[l]["DG"] += (gl-gv); stats[v]["DG"] += (gv-gl)
            if gl > gv: stats[l]["G"] += 1; stats[l]["PTS"] += 3; stats[v]["P"] += 1
            elif gv > gl: stats[v]["G"] += 1; stats[v]["PTS"] += 3; stats[l]["P"] += 1
            else: stats[l]["E"] += 1; stats[l]["PTS"] += 1; stats[v]["E"] += 1; stats[v]["PTS"] += 1
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
# Header con Logo Dinámico
c_logo1, c_title, c_logo2 = st.columns([1, 4, 1])
with c_title:
    st.markdown('<h1 class="nam-title"><span class="txt-gold">N</span><span class="txt-red">A</span><span class="txt-white">M 2026</span></h1>', unsafe_allow_html=True)
if st.session_state.logo_torneo:
    with c_logo1: st.image(st.session_state.logo_torneo, width=120)
    with c_logo2: st.image(st.session_state.logo_torneo, width=120)

if not st.session_state.get('logged_in', False):
    t_pos, t_ff, t_res, t_gol = st.tabs(["📊 POSICIONES", "🏆 FASE FINAL", "⚽ RESULTADOS", "👟 GOLEADORES"])
    
    with t_pos:
        stats_data = calcular_tablas()
        grupos = sorted(list(set(i['grupo'] for i in st.session_state.equipos.values())))
        cols = st.columns(2)
        for idx, g in enumerate(grupos):
            with cols[idx % 2]:
                eq_g = sorted([s for s in stats_data.values() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG']), reverse=True)
                html = f'<div class="main-card"><div class="group-header"><span>GRUPO {g}</span><div class="header-labels"><span class="stat-val">PJ</span><span class="stat-val">DG</span><span class="stat-val">PTS</span></div></div>'
                for eq in eq_g:
                    img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html += f'<div class="team-row"><img src="{img}" class="team-logo"><span class="team-name">{eq["nombre"]}</span><span class="stat-val">{eq["PJ"]}</span><span class="stat-val">{eq["DG"]}</span><span class="stat-val">{eq["PTS"]}</span></div>'
                st.markdown(html + '</div>', unsafe_allow_html=True)

    with t_ff:
        ff = st.session_state.fase_final
        html_ff = f'''
        <div class="bracket-wrapper">
            <div class="bracket-column">
                <h4 style="text-align:center; color:#FFD700">CUARTOS</h4>
                {render_match(ff["cuartos"][0])} {render_match(ff["cuartos"][1])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center; color:#ff3b3b">SEMIFINAL</h4>
                {render_match(ff["semis"][0])}
            </div>
            <div class="final-center">
                {"<img src='data:image/png;base64," + img_to_base64(st.session_state.logo_final) + "' class='final-center' style='width:180px; filter:drop-shadow(0 0 15px #FFD700);'>" if st.session_state.logo_final else "<h2>FINAL</h2>"}
                <h1 style="color:white !important; margin:15px 0;">GRAN FINAL</h1>
                {render_match(ff["final"])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center; color:#ff3b3b">SEMIFINAL</h4>
                {render_match(ff["semis"][1])}
            </div>
            <div class="bracket-column">
                <h4 style="text-align:center; color:#FFD700">CUARTOS</h4>
                {render_match(ff["cuartos"][2])} {render_match(ff["cuartos"][3])}
            </div>
        </div>
        '''
        st.markdown(html_ff, unsafe_allow_html=True)

    with t_res:
        if st.session_state.partidos:
            html_res = '<div class="main-card">'
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for p in reversed(st.session_state.partidos):
                s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html_res += f'<div class="match-row" style="display:flex; align-items:center; justify-content:center; padding:15px; border-bottom:1px solid #ffffff11;"><div class="match-team home" style="flex:1; display:flex; align-items:center; justify-content:flex-end;"><span>{p["local"]}</span><img src="{s_l}" style="width:30px; margin-left:15px;"></div><div class="match-score" style="width:120px; text-align:center; color:#FFD700; font-size:1.8em; font-weight:900;">{p["goles_l"]}-{p["goles_v"]}</div><div class="match-team away" style="flex:1; display:flex; align-items:center; justify-content:flex-start;"><img src="{s_v}" style="width:30px; margin-right:15px;"><span>{p["visitante"]}</span></div></div>'
            st.markdown(html_res + '</div>', unsafe_allow_html=True)

    with t_gol:
        if st.session_state.goleadores:
            html_gol = '<div class="main-card"><div class="group-header"><span>JUGADOR</span><div class="header-labels"><span style="width:120px; text-align:center">EQUIPO</span><span class="stat-val">GOLES</span></div></div>'
            for g in st.session_state.goleadores:
                html_gol += f'<div class="team-row"><span class="team-name">{g["nombre"]}</span><span style="width:120px; text-align:center; font-size:0.8em; color:#FFD700">{g["equipo"]}</span><span class="stat-val">{g["goles"]}</span></div>'
            st.markdown(html_gol + '</div>', unsafe_allow_html=True)

# --- 6. PANEL ADMINISTRADOR (SIDEBAR) ---
with st.sidebar:
    st.header("🔐 Configuración NAM")
    if not st.session_state.get('logged_in', False):
        if st.text_input("Clave", type="password") == "admin123":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        
        adm_t1, adm_t2, adm_t3, adm_t4, adm_t5 = st.tabs(["LOGOS", "EQUIPOS", "GRUPOS", "ELIMIN.", "GOL."])
        
        with adm_t1:
            st.subheader("Logos del Torneo")
            lt = st.file_uploader("Logo Principal (NAM)", type=["png", "jpg"])
            lf = st.file_uploader("Logo de la Final", type=["png", "jpg"])
            if st.button("Guardar Logos"):
                if lt: st.session_state.logo_torneo = Image.open(lt)
                if lf: st.session_state.logo_final = Image.open(lf)
                save_to_disk(); st.success("Logos actualizados"); st.rerun()

        with adm_t2:
            for id_e, inf in st.session_state.equipos.items():
                with st.expander(f"Editar {inf['nombre']}"):
                    nn = st.text_input("Nombre", inf['nombre'], key=f"nn{id_e}")
                    nl = st.file_uploader("Logo", key=f"nl{id_e}")
                    if st.button("Guardar", key=f"bt{id_e}"):
                        st.session_state.equipos[id_e]['nombre'] = nn.upper()
                        if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                        save_to_disk(); st.rerun()
        
        with adm_t3:
            eqs = [i['nombre'] for i in st.session_state.equipos.values()]
            l, v = st.selectbox("Local", eqs), st.selectbox("Visitante", eqs)
            gl, gv = st.number_input("GL", 0), st.number_input("GV", 0)
            if st.button("Guardar Resultado Grupo"):
                st.session_state.partidos.append({"local": l, "visitante": v, "goles_l": gl, "goles_v": gv})
                save_to_disk(); st.rerun()
        
        with adm_t4:
            st.write("Fase Final (Cuartos en adelante)")
            eqs_ko = [""] + [i['nombre'] for i in st.session_state.equipos.values()]
            for fase in ["cuartos", "semis", "final"]:
                with st.expander(f"GESTIONAR {fase.upper()}"):
                    if fase == "final":
                        st.session_state.fase_final[fase]["L"] = st.selectbox("F1", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase]["L"]) if st.session_state.fase_final[fase]["L"] in eqs_ko else 0)
                        st.session_state.fase_final[fase]["V"] = st.selectbox("F2", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase]["V"]) if st.session_state.fase_final[fase]["V"] in eqs_ko else 0)
                        st.session_state.fase_final[fase]["gl"] = st.number_input("G1", value=st.session_state.fase_final[fase]["gl"])
                        st.session_state.fase_final[fase]["gv"] = st.number_input("G2", value=st.session_state.fase_final[fase]["gv"])
                    else:
                        for i in range(len(st.session_state.fase_final[fase])):
                            st.session_state.fase_final[fase][i]["L"] = st.selectbox(f"{fase} L{i}", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase][i]["L"]) if st.session_state.fase_final[fase][i]["L"] in eqs_ko else 0)
                            st.session_state.fase_final[fase][i]["V"] = st.selectbox(f"{fase} V{i}", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[fase][i]["V"]) if st.session_state.fase_final[fase][i]["V"] in eqs_ko else 0)
                            st.session_state.fase_final[fase][i]["gl"] = st.number_input(f"GL {fase}{i}", value=st.session_state.fase_final[fase][i]["gl"])
                            st.session_state.fase_final[fase][i]["gv"] = st.number_input(f"GV {fase}{i}", value=st.session_state.fase_final[fase][i]["gv"])
            if st.button("Guardar Eliminatoria"): save_to_disk(); st.success("Guardado!"); st.rerun()

        with adm_t5:
            n = st.text_input("Jugador")
            e = st.selectbox("Equipo", [i['nombre'] for i in st.session_state.equipos.values()])
            g = st.number_input("Goles", 0)
            if st.button("Añadir Goleador"):
                st.session_state.goleadores.append({"nombre": n.upper(), "equipo": e, "goles": g})
                save_to_disk(); st.rerun()
            for i, gol in enumerate(st.session_state.goleadores):
                c1, c2, c3 = st.columns([3,1,1])
                c1.write(f"{gol['nombre']}")
                if c2.button("🔼", key=f"u{i}") and i > 0:
                    st.session_state.goleadores[i], st.session_state.goleadores[i-1] = st.session_state.goleadores[i-1], st.session_state.goleadores[i]
                    save_to_disk(); st.rerun()
                if c3.button("🔽", key=f"d{i}") and i < len(st.session_state.goleadores)-1:
                    st.session_state.goleadores[i], st.session_state.goleadores[i+1] = st.session_state.goleadores[i+1], st.session_state.goleadores[i]
                    save_to_disk(); st.rerun()
