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
    
    .nam-title { font-size: clamp(2.5em, 8vw, 4.5em); text-align: center; font-weight: 900; color: white; margin-bottom: 20px; }
    .txt-celeste { color: #7db1ff !important; }
    .txt-red { color: #ff3b3b !important; }

    .main-card {
        background: rgba(0, 10, 60, 0.6); border-radius: 12px; margin-bottom: 25px;
        border: 1px solid #FFD70033; color: white; backdrop-filter: blur(10px);
        overflow: hidden;
    }

    /* GRID DE POSICIONES */
    .grid-posiciones { display: grid; grid-template-columns: 2fr repeat(8, 45px); align-items: center; min-width: 650px; padding: 10px 15px; }
    
    /* GRID DE GOLEADORES CORREGIDA */
    .grid-goleadores { 
        display: grid; 
        grid-template-columns: 2fr 1.5fr 1fr; 
        align-items: center; 
        width: 100%; 
        padding: 12px 15px; 
        border-bottom: 1px solid #ffffff10;
    }
    
    .header-grid { background: linear-gradient(90deg, #00124d 0%, #ff3b3b33 100%); border-bottom: 3px solid #FFD700; font-weight: 900; }
    .stat-cell { text-align: center; font-weight: bold; }

    /* Estructura Bracket */
    .bracket-scroll { overflow-x: auto; width: 100%; padding: 20px 0; }
    .bracket-wrapper { display: flex; justify-content: space-around; align-items: center; min-width: 1100px; }
    .bracket-column { display: flex; flex-direction: column; justify-content: center; gap: 40px; width: 240px; }
    .match-box-ko { background: rgba(0, 20, 80, 0.8); border-radius: 8px; border: 1px solid #FFD70044; padding: 10px; width: 100%; }
    .ko-score { background: #FFD700; color: #000; font-weight: 900; width: 32px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 3px; }
    .final-center { width: 320px; text-align: center; display: flex; flex-direction: column; align-items: center; }
    
    .date-divider { background: #FFD700; color: black; padding: 5px 20px; font-weight: 900; border-radius: 4px; margin: 20px 0 10px 0; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA ---
def get_team_info(name):
    for info in st.session_state.equipos.values():
        if info['nombre'] == name: return info
    return {"nombre": name or "TBD", "logo": None}

def calcular_tablas():
    stats = {info['nombre']: {"nombre": info['nombre'], "PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']} for info in st.session_state.equipos.values()}
    for p in st.session_state.partidos:
        l, v = p['local'], p['visitante']
        gl, gv = p.get('goles_l'), p.get('goles_v')
        if gl is not None and gv is not None and l in stats and v in stats:
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

with t_gol:
    if st.session_state.goleadores:
        # Contenedor principal de la tabla
        html_gol = '<div class="main-card">'
        # Cabecera
        html_gol += '<div class="grid-goleadores header-grid"><span>JUGADOR</span><span class="stat-cell">EQUIPO</span><span class="stat-cell">GOLES</span></div>'
        # Filas de datos (ordenadas por goles)
        for g in sorted(st.session_state.goleadores, key=lambda x: x['goles'], reverse=True):
            html_gol += f'''
            <div class="grid-goleadores">
                <span style="font-weight:900; text-transform:uppercase;">{g["nombre"]}</span>
                <span class="stat-cell" style="color:#FFD700; font-size:0.9em;">{g["equipo"]}</span>
                <span class="stat-cell" style="font-size:1.2em;">{g["goles"]}</span>
            </div>
            '''
        html_gol += '</div>'
        st.markdown(html_gol, unsafe_allow_html=True)
    else:
        st.info("Aún no hay goleadores registrados.")

# --- 6. PANEL ADMINISTRADOR ---
with st.sidebar:
    st.header("🔐 Admin")
    if not st.session_state.get('logged_in', False):
        if st.text_input("Clave", type="password") == "admin123":
            if st.button("Entrar"): st.session_state.logged_in = True; st.rerun()
    else:
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()
        adm_t = st.tabs(["LOGOS", "EQ", "GR", "ELIM", "GOL", "💾"])
        
        with adm_t[4]:
            st.subheader("⚽ Registrar Goleador")
            eqs_nombres = sorted([i['nombre'] for i in st.session_state.equipos.values()])
            
            with st.form("nuevo_goleador", clear_on_submit=True):
                col1, col2, col3 = st.columns([2, 2, 1])
                nuevo_nombre = col1.text_input("Nombre del Jugador")
                nuevo_equipo = col2.selectbox("Equipo", eqs_nombres)
                nuevos_goles = col3.number_input("Goles", min_value=0, step=1)
                
                if st.form_submit_button("Añadir Jugador"):
                    if nuevo_nombre:
                        st.session_state.goleadores.append({
                            "nombre": nuevo_nombre.upper(),
                            "equipo": nuevo_equipo,
                            "goles": nuevos_goles
                        })
                        save_to_disk()
                        st.success(f"{nuevo_nombre} añadido.")
                        st.rerun()

            st.divider()
            st.subheader("📝 Gestionar Goleadores")
            
            for i, gol in enumerate(st.session_state.goleadores):
                with st.expander(f"{gol['nombre']} ({gol['equipo']}) - {gol['goles']} Goles"):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    nuevo_valor = c1.number_input("Editar Goles", value=gol['goles'], key=f"edit_g_{i}")
                    if c2.button("💾 Guardar", key=f"save_g_{i}"):
                        st.session_state.goleadores[i]['goles'] = nuevo_valor
                        save_to_disk()
                        st.rerun()
                    if c3.button("🗑️ Borrar", key=f"del_g_{i}"):
                        st.session_state.goleadores.pop(i)
                        save_to_disk()
                        st.rerun()

        with adm_t[5]:
            if os.path.exists(DB_FILE):
                with open(DB_FILE, "r") as f:
                    st.download_button("Descargar Backup JSON", f.read(), "data_torneo.json")
