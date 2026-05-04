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
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    except: return None

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
            "logo": img_to_base64(info["logo"]) if info.get("logo") else None
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
                    logo_pil = None
                    if info.get("logo"):
                        logo_pil = Image.open(io.BytesIO(base64.b64decode(info["logo"])))
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
    .txt-gold { color: #FFD700 !important; }
    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: white !important; font-weight: 900; }
    .nam-title { font-size: clamp(2.5em, 8vw, 4.5em); text-align: center; font-weight: 900; letter-spacing: -2px; line-height: 1; color: white; margin-bottom: 20px; }
    .main-card { background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px; border: 1px solid #FFD70033; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px); overflow-x: auto; }
    .grid-posiciones { display: grid; grid-template-columns: 2fr repeat(8, 45px); align-items: center; min-width: 650px; padding: 10px 15px; }
    .header-grid { background: linear-gradient(90deg, #00124d 0%, #ff3b3b33 100%); border-bottom: 3px solid #FFD700; font-weight: 900; }
    .stat-cell { text-align: center; font-weight: bold; color: white !important; }
    .grid-goleadores { display: grid; grid-template-columns: 2fr 1.5fr 1fr; align-items: center; min-width: 500px; padding: 10px 15px; }
    .bracket-scroll { overflow-x: auto; width: 100%; padding: 20px 0; }
    .bracket-wrapper { display: flex; justify-content: space-between; align-items: center; min-width: 1050px; padding: 20px 0; }
    .bracket-column { display: flex; flex-direction: column; justify-content: space-around; min-height: 550px; width: 240px; }
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
    return f'<div class="match-box-ko"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;"><div style="display:flex;align-items:center;"><img src="{img1}" style="width:22px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;">{t1["nombre"] or "---"}</span></div><span class="ko-score">{match["gl"]}</span></div><div style="display:flex;align-items:center;justify-content:space-between;"><div style="display:flex;align-items:center;"><img src="{img2}" style="width:22px;margin-right:8px;"><span style="font-size:0.8em;font-weight:700;">{t2["nombre"] or "---"}</span></div><span class="ko-score">{match["gv"]}</span></div></div>'

def calcular_tablas():
    stats = {info['nombre']: {"nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']} for info in st.session_state.equipos.values()}
    for p in st.session_state.partidos:
        l, v = p['local'], p['visitante']
        try:
            gl = int(p.get('goles_l', 0))
            gv = int(p.get('goles_v', 0))
        except: gl, gv = 0, 0
            
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
        grupos = sorted(list(set(i['grupo'] for i in st.session_state.equipos.values())))
        for g in grupos:
            eq_g = sorted([s for s in stats_data.values() if s['grupo'] == g], key=lambda x: (x['PTS'], x['DG'], x['GF']), reverse=True)
            html = f'<div class="main-card"><div class="grid-posiciones header-grid"><span>GRUPO {g}</span><span class="stat-cell">PJ</span><span class="stat-cell">G</span><span class="stat-cell">E</span><span class="stat-cell">P</span><span class="stat-cell">GF</span><span class="stat-cell">GC</span><span class="stat-cell">DG</span><span class="stat-cell">PTS</span></div>'
            for eq in eq_g:
                img = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html += f'<div class="grid-posiciones" style="border-bottom:1px solid #ffffff10;"><div style="display:flex;align-items:center;"><img src="{img}" style="width:24px;margin-right:12px;">{eq["nombre"]}</div><span class="stat-cell">{eq["PJ"]}</span><span class="stat-cell">{eq["G"]}</span><span class="stat-cell">{eq["E"]}</span><span class="stat-cell">{eq["P"]}</span><span class="stat-cell">{eq["GF"]}</span><span class="stat-cell">{eq["GC"]}</span><span class="stat-cell">{eq["DG"]}</span><span class="stat-cell" style="color:#FFD700 !important">{eq["PTS"]}</span></div>'
            st.markdown(html + '</div>', unsafe_allow_html=True)

    with t_ff:
        ff = st.session_state.fase_final
        logo_f = f"data:image/png;base64,{img_to_base64(st.session_state.logo_final)}" if st.session_state.logo_final else None
        st.markdown(f'''<div class="bracket-scroll"><div class="bracket-wrapper"><div class="bracket-column"><h4>CUARTOS</h4>{render_match(ff["cuartos"][0])}{render_match(ff["cuartos"][1])}</div><div class="bracket-column"><h4>SEMIFINAL</h4>{render_match(ff["semis"][0])}</div><div class="final-center">{"<img src='"+logo_f+"' width=160>" if logo_f else "<h2>FINAL</h2>"}<h1 style="color:white !important;margin:15px 0;">GRAN FINAL</h1>{render_match(ff["final"])}</div><div class="bracket-column"><h4>SEMIFINAL</h4>{render_match(ff["semis"][1])}</div><div class="bracket-column"><h4>CUARTOS</h4>{render_match(ff["cuartos"][2])}{render_match(ff["cuartos"][3])}</div></div></div>''', unsafe_allow_html=True)

    with t_res:
        if st.session_state.partidos:
            df = pd.DataFrame(st.session_state.partidos)
            df['fecha'] = df.get('fecha', 'S/D')
            l_map = {i['nombre']: i['logo'] for i in st.session_state.equipos.values()}
            for f in df['fecha'].unique():
                st.markdown(f'<div class="date-divider">{f}</div>', unsafe_allow_html=True)
                html_res = '<div class="main-card">'
                for _, p in df[df['fecha'] == f].iterrows():
                    s_l = f"data:image/png;base64,{img_to_base64(l_map.get(p['local']))}" if l_map.get(p['local']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    s_v = f"data:image/png;base64,{img_to_base64(l_map.get(p['visitante']))}" if l_map.get(p['visitante']) else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html_res += f'<div style="display:flex;align-items:center;justify-content:center;padding:15px;border-bottom:1px solid #ffffff11;"><div style="flex:1;text-align:right;">{p["local"]} <img src="{s_l}" width="24"></div><div style="width:100px;text-align:center;color:#FFD700;font-weight:900;font-size:1.3em;">{p["goles_l"]}-{p["goles_v"]}</div><div style="flex:1;text-align:left;"><img src="{s_v}" width="24"> {p["visitante"]}</div></div>'
                st.markdown(html_res + '</div>', unsafe_allow_html=True)

    with t_gol:
        if st.session_state.goleadores:
            gols = sorted(st.session_state.goleadores, key=lambda x: int(x.get('goles', 0)), reverse=True)
            html_gol = '<div class="main-card"><div class="grid-goleadores header-grid"><span>JUGADOR</span><span>EQUIPO</span><span class="stat-cell">GOLES</span></div>'
            for g in gols:
                html_gol += f'<div class="grid-goleadores" style="border-bottom:1px solid #ffffff10;"><span>{g["nombre"]}</span><span style="color:#FFD700;">{g["equipo"]}</span><span class="stat-cell">{g["goles"]}</span></div>'
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
            lt, lf = st.file_uploader("Logo Torneo"), st.file_uploader("Logo Final")
            if st.button("Guardar Logos"):
                if lt: st.session_state.logo_torneo = Image.open(lt)
                if lf: st.session_state.logo_final = Image.open(lf)
                save_to_disk(); st.rerun()
        
        with adm_t[1]:
            for id_e, inf in st.session_state.equipos.items():
                with st.expander(f"Editar {inf['nombre']}"):
                    nn = st.text_input("Nombre", inf['nombre'], key=f"n{id_e}").upper()
                    nl = st.file_uploader("Logo", key=f"l{id_e}")
                    if st.button("Guardar", key=f"b{id_e}"):
                        st.session_state.equipos[id_e]['nombre'] = nn
                        if nl: st.session_state.equipos[id_e]['logo'] = Image.open(nl)
                        save_to_disk(); st.rerun()

        with adm_t[2]:
            st.subheader("Añadir Partido")
            eqs = sorted([i['nombre'] for i in st.session_state.equipos.values()])
            f_p = st.date_input("Fecha")
            l, v = st.selectbox("Local", eqs), st.selectbox("Visitante", eqs)
            gl, gv = st.number_input("GL", 0, step=1), st.number_input("GV", 0, step=1)
            if st.button("Registrar"):
                st.session_state.partidos.append({"fecha": str(f_p), "local": l, "visitante": v, "goles_l": int(gl), "goles_v": int(gv)})
                save_to_disk(); st.rerun()
            st.divider()
            for i, p in enumerate(st.session_state.partidos):
                if st.button(f"🗑️ {p['local']} vs {p['visitante']}", key=f"delp{i}"):
                    st.session_state.partidos.pop(i); save_to_disk(); st.rerun()

        with adm_t[3]:
            eqs_ko = [""] + eqs
            for f in ["cuartos", "semis", "final"]:
                with st.expander(f.upper()):
                    matches = st.session_state.fase_final[f]
                    if isinstance(matches, list):
                        for i, m in enumerate(matches):
                            m["L"] = st.selectbox(f"L{f}{i}", eqs_ko, index=eqs_ko.index(m["L"]) if m["L"] in eqs_ko else 0)
                            m["V"] = st.selectbox(f"V{f}{i}", eqs_ko, index=eqs_ko.index(m["V"]) if m["V"] in eqs_ko else 0)
                            m["gl"], m["gv"] = st.number_input(f"gl{f}{i}", m["gl"]), st.number_input(f"gv{f}{i}", m["gv"])
                    else: # Final
                        matches["L"] = st.selectbox("L Final", eqs_ko, index=eqs_ko.index(matches["L"]) if matches["L"] in eqs_ko else 0)
                        matches["V"] = st.selectbox("V Final", eqs_ko, index=eqs_ko.index(matches["V"]) if matches["V"] in eqs_ko else 0)
                        matches["gl"], matches["gv"] = st.number_input("gl final", matches["gl"]), st.number_input("gv final", matches["gv"])
            if st.button("Guardar Eliminatorias"): save_to_disk(); st.rerun()

        with adm_t[4]:
            nj, ej = st.text_input("Jugador").upper(), st.selectbox("Equipo", eqs, key="gol_eq")
            gj = st.number_input("Goles", 0, step=1)
            if st.button("Añadir Goleador"):
                st.session_state.goleadores.append({"nombre": nj, "equipo": ej, "goles": int(gj)})
                save_to_disk(); st.rerun()

        with adm_t[5]:
            st.subheader("Mantenimiento")
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f: st.download_button("📥 Backup JSON", f.read(), "torneo.json")
            
            st.divider()
            sub = st.file_uploader("Restaurar")
            if sub and st.button("🔴 RESTAURAR ARCHIVO"):
                with open(DB_FILE, "wb") as f: f.write(sub.getbuffer())
                st.rerun()

            st.divider()
            st.error("Zona de Peligro")
            confirmar = st.checkbox("Confirmo borrar todo")
            if st.button("🔥 RESET TOTAL") and confirmar:
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.session_state.equipos = {f"ID_{i}": {"nombre": f"EQUIPO {i}", "grupo": chr(64 + ((i-1) // 4) + 1), "logo": None} for i in range(1, 21)}
                st.session_state.partidos, st.session_state.goleadores = [], []
                st.session_state.fase_final = inicializar_fase_final()
                st.session_state.logo_torneo = st.session_state.logo_final = None
                st.rerun()
