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

def crear_backup():
    if os.path.exists(DB_FILE):
        if not os.path.exists("backups"): os.makedirs("backups")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(DB_FILE, f"backups/backup_{ts}.json")

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
    crear_backup()

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

# --- 2. ESTILOS CSS (MÓVIL + ALINEACIÓN GRID) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at top, #00124d 0%, #000422 100%) !important; }
    
    .txt-celeste { color: #7db1ff !important; }
    .txt-red { color: #ff3b3b !important; }
    .txt-white { color: #ffffff !important; }
    .txt-gold { color: #FFD700 !important; }

    /* Sidebar: Título Negro */
    [data-testid="stSidebar"] h2 { color: #000000 !important; font-weight: 900; }

    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: white !important; font-weight: 900; }
    .nam-title { font-size: clamp(2.5em, 8vw, 4.5em); text-align: center; font-weight: 900; letter-spacing: -2px; line-height: 1; color: white; margin-bottom: 20px; }

    /* Cartas Principales */
    .main-card {
        background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #FFD70033; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px);
        overflow-x: auto;
    }

    /* SISTEMA GRID PARA POSICIONES */
    .grid-posiciones {
        display: grid;
        grid-template-columns: 1fr 40px 40px 40px 40px 40px 40px 40px 45px;
        align-items: center;
        min-width: 600px;
    }
    
    .group-header-grid {
        background: linear-gradient(90deg, #00124d 0%, #ff3b3b33 100%);
        padding: 12px 15px; border-bottom: 3px solid #FFD700; font-weight: 900;
    }
    
    .row-grid { padding: 10px 15px; border-bottom: 1px solid #ffffff10; font-size: 0.85em; }
    .team-cell { display: flex; align-items: center; font-weight: 700; text-transform: uppercase; }
    .stat-cell { text-align: center; font-weight: bold; color: white !important; }

    /* SISTEMA GRID PARA GOLEADORES */
    .grid-goleadores {
        display: grid;
        grid-template-columns: 1fr 180px 80px;
        align-items: center;
        min-width: 500px;
    }
    .gol-header-grid { padding: 12px 15px; border-bottom: 2px solid #FFD700; font-weight: 900; background: rgba(0,0,0,0.2); }
    .gol-row-grid { padding: 10px 15px; border-bottom: 1px solid #ffffff10; }

    /* FASE FINAL */
    .bracket-scroll { overflow-x: auto; width: 100%; padding: 20px 0; }
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; min-width: 1050px; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 550px; width: 240px; }
    .bracket-column h4 { color: white !important; text-align: center; font-weight: 900; margin-bottom: 10px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 8px; border: 1px solid #FFD70044; padding: 10px; margin: 15px 0; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 28px; text-align: center; border-radius: 3px; }

    .date-divider { background: #FFD700; color: black; padding: 5px 20px; font-weight: 900; border-radius: 4px; margin: 25px 0 10px 0; display: inline-block; }
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
    return f'''
    <div class="match-box-ko">
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;">
            <div style="display:flex; align-items:center;"><img src="{img1}" style="width:22px; margin-right:8px;"><span style="font-size:0.8em; font-weight:700;">{t1["nombre"] or "---"}</span></div>
            <span class="ko-score">{match["gl"]}</span>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between;">
            <div style="display:flex; align-items:center;"><img src="{img2}" style="width:22px; margin-right:8px;"><span style="font-size:0.8em; font-weight:700;">{t2["nombre"] or "---"}</span></div>
            <span class="ko-score">{match["gv"]}</span>
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
                <div class="grid-posiciones group-header-grid">
                    <span>GRUPO {g}</span>
                    <span class="stat-cell">PJ</span><span class="stat-cell">G</span><span class="stat-cell">E</span><span class="stat-cell">P</span>
                    <span class="stat-cell">GF</span><span class="stat-cell">GC</span><span class="stat-cell">DG</span><span class="stat-cell">PTS</span>
                </div>'''
            for eq in eq_g:
                img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html += f'''
                <div class="grid-posiciones row-grid">
                    <div class="team-cell"><img src="{img}" style="width:24px; margin-right:12px;">{eq["nombre"]}</div>
                    <span class="stat-cell">{eq["PJ"]}</span><span class="stat-cell">{eq["G"]}</span><span class="stat-cell">{eq["E"]}</span><span class="stat-cell">{eq["P"]}</span>
                    <span class="stat-cell">{eq["GF"]}</span><span class="stat-cell">{eq["GC"]}</span><span class="stat-cell">{eq["DG"]}</span><span class="stat-cell" style="color:#FFD700 !important">{eq["PTS"]}</span>
                </div>'''
            st.markdown(html + '</div>', unsafe_allow_html=True)

    with t_ff:
        ff = st.session_state.fase_final
        st.markdown('<div class="bracket-scroll"><div class="bracket-wrapper">', unsafe_allow_html=True)
        col1 = f'<div class="bracket-column"><h4>CUARTOS</h4>{render_match(ff["cuartos"][0])}{render_match(ff["cuartos"][1])}</div>'
        col2 = f'<div class="bracket-column"><h4>SEMIFINAL</h4>{render_match(ff["semis"][0])}</div>'
        
        logo_f = f"data:image/png;base64,{img_to_base64(st.session_state.logo_final)}" if st.session_state.logo_final else None
        center = f'<div class="final-center">{"<img src="+logo_f+" width=160 style=\"filter:drop-shadow(0 0 15px #FFD700)\">" if logo_f else "<h2>FINAL</h2>"}<h1 style="color:white !important; margin:15px 0;">GRAN FINAL</h1>{render_match(ff["final"])}</div>'
        
        col4 = f'<div class="bracket-column"><h4>SEMIFINAL</h4>{render_match(ff["semis"][1])}</div>'
        col5 = f'<div class="bracket-column"><h4>CUARTOS</h4>{render_match(ff["cuartos"][2])}{render_match(ff["cuartos"][3])}</div>'
        st.markdown(col1 + col2 + center + col4 + col5 + '</div></div>', unsafe_allow_html=True)

    with t_res:
        if st.session_state.partidos:
            df = pd.DataFrame(st.session_state.partidos)
            if "fecha" not in df.columns: df["fecha"] = "S/D"
            df = df.fillna("S/D").sort_values(by="fecha", ascending=False)
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for f in df['fecha'].unique():
                st.markdown(f'<div class="date-divider">{f}</div>', unsafe_allow_html=True)
                html_res = '<div class="main-card">'
                for _, p in df[df['fecha'] == f].iterrows():
                    s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html_res += f'<div style="display:flex; align-items:center; justify-content:center; padding:15px; border-bottom:1px solid #ffffff11; min-width:500px;"><div style="flex:1; text-align:right;">{p["local"]} <img src="{s_l}" width="24"></div><div style="width:110px; text-align:center; color:#FFD700; font-weight:900; font-size:1.5em;">{p["goles_l"]}-{p["goles_v"]}</div><div style="flex:1; text-align:left;"><img src="{s_v}" width="24"> {p["visitante"]}</div></div>'
                st.markdown(html_res + '</div>', unsafe_allow_html=True)

    with t_gol:
        if st.session_state.goleadores:
            html_gol = f'''
            <div class="main-card">
                <div class="grid-goleadores gol-header-grid">
                    <span>JUGADOR</span><span style="text-align:center">EQUIPO</span><span style="text-align:center">GOLES</span>
                </div>'''
            for g in st.session_state.goleadores:
                html_gol += f'''
                <div class="grid-goleadores gol-row-grid">
                    <span style="font-weight:700; text-transform:uppercase;">{g["nombre"]}</span>
                    <span class="gol-team-txt">{g["equipo"]}</span>
                    <span class="gol-score-txt">{g["goles"]}</span>
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
        adm_t = st.tabs(["LOGOS", "EQ", "GR", "ELIM", "GOL", "💾"])
        with adm_t[0]:
            lt, lf = st.file_uploader("Logo Principal"), st.file_uploader("Logo Final")
            if st.button("Guardar Logos"):
                if lt: st.session_state.logo_torneo = Image.open(lt)
                if lf: st.session_state.logo_final = Image.open(lf)
                save_to_disk(); st.rerun()
        with adm_t[1]:
            for id_e, inf in st.session_state.equipos.items():
                with st.expander(f"Editar {inf['nombre']}"):
                    nn = st.text_input("Nombre", inf['nombre'], key=f"n{id_e}")
                    nl = st.file_uploader("Logo", key=f"l{id_e}")
                    if st.button("Guardar", key=f"b{id_e}"):
                        st.session_state.equipos[id_e]['nombre'] = nn.upper()
                        if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                        save_to_disk(); st.rerun()
        with adm_t[2]:
            eqs = sorted([i['nombre'] for i in st.session_state.equipos.values()])
            fecha_p = st.date_input("Fecha", datetime.now())
            l, v = st.selectbox("Local", eqs), st.selectbox("Visitante", eqs)
            gl, gv = st.number_input("GL", 0), st.number_input("GV", 0)
            if st.button("Registrar Partido"):
                st.session_state.partidos.append({"fecha": str(fecha_p), "local": l, "visitante": v, "goles_l": gl, "goles_v": gv})
                save_to_disk(); st.rerun()
        with adm_t[3]:
            eqs_ko = [""] + eqs
            for f in ["cuartos", "semis", "final"]:
                with st.expander(f.upper()):
                    if f == "final":
                        st.session_state.fase_final[f]["L"] = st.selectbox("F1", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[f]["L"]) if st.session_state.fase_final[f]["L"] in eqs_ko else 0)
                        st.session_state.fase_final[f]["V"] = st.selectbox("F2", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[f]["V"]) if st.session_state.fase_final[f]["V"] in eqs_ko else 0)
                        st.session_state.fase_final[f]["gl"] = st.number_input("G1", value=st.session_state.fase_final[f]["gl"])
                        st.session_state.fase_final[f]["gv"] = st.number_input("G2", value=st.session_state.fase_final[f]["gv"])
                    else:
                        for i in range(len(st.session_state.fase_final[f])):
                            st.session_state.fase_final[f][i]["L"] = st.selectbox(f"L{i}", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[f][i]["L"]) if st.session_state.fase_final[f][i]["L"] in eqs_ko else 0, key=f"l{f}{i}")
                            st.session_state.fase_final[f][i]["V"] = st.selectbox(f"V{i}", eqs_ko, index=eqs_ko.index(st.session_state.fase_final[f][i]["V"]) if st.session_state.fase_final[f][i]["V"] in eqs_ko else 0, key=f"v{f}{i}")
                            st.session_state.fase_final[f][i]["gl"] = st.number_input(f"GL{i}", value=st.session_state.fase_final[f][i]["gl"], key=f"gl{f}{i}")
                            st.session_state.fase_final[f][i]["gv"] = st.number_input(f"GV{i}", value=st.session_state.fase_final[f][i]["gv"], key=f"gv{f}{i}")
            if st.button("Guardar Eliminatoria"): save_to_disk(); st.rerun()
        with adm_t[4]:
            n = st.text_input("Jugador").upper()
            e = st.selectbox("Equipo", eqs)
            g = st.number_input("Goles", 0)
            if st.button("Añadir"):
                st.session_state.goleadores.append({"nombre": n, "equipo": e, "goles": g})
                save_to_disk(); st.rerun()
            for i, gol in enumerate(st.session_state.goleadores):
                c1, c2, c3, c4 = st.columns([2,1,1,1])
                c1.write(gol['nombre'])
                if c2.button("🔼", key=f"u{i}") and i > 0:
                    st.session_state.goleadores[i], st.session_state.goleadores[i-1] = st.session_state.goleadores[i-1], st.session_state.goleadores[i]
                    save_to_disk(); st.rerun()
                if c4.button("🗑️", key=f"d{i}"):
                    st.session_state.goleadores.pop(i)
                    save_to_disk(); st.rerun()
        with adm_t[5]:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f:
                    st.download_button("📥 Descargar JSON", f.read(), f"BACKUP_{datetime.now().strftime('%d_%m')}.json")
            subido = st.file_uploader("Restaurar JSON")
            if subido and st.button("🔴 RESTAURAR"):
                with open(DB_FILE, "wb") as f: f.write(subido.getbuffer())
                st.rerun()
