import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64
import json
import os

# --- 1. CONFIGURACIÓN Y PERSISTENCIA ---
st.set_page_config(page_title="Champions League Admin", layout="wide")

DB_FILE = "torneo_data.json"

def img_to_base64(image):
    if image is None: return None
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def save_to_disk():
    data_to_save = {
        "partidos": st.session_state.partidos,
        "equipos": {}
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
                equipos_cargados = {}
                for id_eq, info in data.get("equipos", {}).items():
                    logo_pil = None
                    if info["logo"]:
                        logo_data = base64.b64decode(info["logo"])
                        logo_pil = Image.open(io.BytesIO(logo_data))
                    equipos_cargados[id_eq] = {
                        "nombre": info["nombre"],
                        "grupo": info["grupo"],
                        "logo": logo_pil
                    }
                st.session_state.equipos = equipos_cargados
                return True
        except:
            return False
    return False

# --- 2. ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .group-card {
        background: linear-gradient(180deg, #0d1a44 0%, #060b26 100%);
        border-radius: 8px; padding: 0px; margin-bottom: 25px;
        border: 1px solid #1e2a5a; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .group-header {
        background-color: #0d1a44; padding: 12px 15px; border-bottom: 2px solid #0052cc;
        font-weight: bold; font-size: 1.1em; display: flex; justify-content: space-between; border-radius: 8px 8px 0 0;
    }
    .team-row { display: flex; align-items: center; padding: 10px 15px; border-bottom: 1px solid #ffffff10; font-size: 0.95em; }
    .team-logo { width: 28px; height: 28px; margin-right: 15px; object-fit: contain; }
    .team-name { flex-grow: 1; text-transform: uppercase; font-weight: 500; }
    .stat-val { width: 40px; text-align: center; font-weight: bold; }
    .header-labels { display: flex; color: #5c78ff; font-size: 0.85em; }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE NEGOCIO ---
def calcular_tablas():
    stats_global = {}
    for id_eq, info in st.session_state.equipos.items():
        stats_global[info['nombre']] = {
            "nombre": info['nombre'], "PJ": 0, "GD": 0, "PTS": 0, 
            "grupo": info['grupo'], "logo": info['logo']
        }
    for p in st.session_state.partidos:
        l, v, gl, gv = p['local'], p['visitante'], p['goles_l'], p['goles_v']
        if l in stats_global and v in stats_global:
            stats_global[l]["PJ"] += 1; stats_global[v]["PJ"] += 1
            stats_global[l]["GD"] += (gl - gv); stats_global[v]["GD"] += (gv - gl)
            if gl > gv: stats_global[l]["PTS"] += 3
            elif gv > gl: stats_global[v]["PTS"] += 3
            else: stats_global[l]["PTS"] += 1; stats_global[v]["PTS"] += 1
    return stats_global

# --- 4. INICIALIZACIÓN ---
if 'equipos' not in st.session_state:
    if not load_from_disk():
        equipos_iniciales = {}
        for i in range(1, 21):
            grupo = chr(64 + ((i-1) // 4) + 1) 
            equipos_iniciales[f"ID_{i}"] = {"nombre": f"EQUIPO {i}", "grupo": grupo, "logo": None}
        st.session_state.equipos = equipos_iniciales
        st.session_state.partidos = []

PASSWORD_ADMIN = "admin123"

# --- 5. BARRA LATERAL (LOGIN/LOGOUT) ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        pass_input = st.text_input("Contraseña de Admin", type="password", key="login_pass")
        if st.button("Ingresar", key="login_btn"):
            if pass_input == PASSWORD_ADMIN:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrecta")
    else:
        st.success("Modo Edición Activo")
        if st.button("❌ Salir de Modo Admin", key="logout_btn"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        if st.button("🗑️ Resetear Todo", key="reset_btn"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.clear()
            st.rerun()

# --- 6. INTERFAZ PRINCIPAL ---
st.title("🏆 UEFA CHAMPIONS LEAGUE")

if not st.session_state.logged_in:
    # --- VISTA PÚBLICA ---
    tab_pos, tab_res = st.tabs(["📊 POSICIONES", "⚽ RESULTADOS"])
    stats = calcular_tablas()
    
    with tab_pos:
        grupos = sorted(list(set(info['grupo'] for info in st.session_state.equipos.values())))
        cols = st.columns(2)
        for idx, g in enumerate(grupos):
            with cols[idx % 2]:
                equipos_g = sorted([info for name, info in stats.items() if info['grupo'] == g], 
                                   key=lambda x: (x['PTS'], x['GD']), reverse=True)
                html = f'<div class="group-card"><div class="group-header"><span>GROUP {g}</span><div class="header-labels"><span class="stat-val">P</span><span class="stat-val">GD</span><span class="stat-val">PTS</span></div></div>'
                for eq in equipos_g:
                    logo_src = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                    html += f'<div class="team-row"><img src="{logo_src}" class="team-logo"><span class="team-name">{eq["nombre"]}</span><span class="stat-val">{eq["PJ"]}</span><span class="stat-val">{eq["GD"]}</span><span class="stat-val">{eq["PTS"]}</span></div>'
                st.markdown(html + '</div>', unsafe_allow_html=True)
    
    with tab_res:
        if not st.session_state.partidos:
            st.info("Aún no se han registrado partidos.")
        else:
            for p in reversed(st.session_state.partidos):
                st.write(f"**Grupo {p['grupo']}**: {p['local']} {p['goles_l']} - {p['goles_v']} {p['visitante']}")

else:
    # --- VISTA ADMINISTRADOR ---
    tab_mng, tab_match = st.tabs(["⚙️ GESTIONAR EQUIPOS", "⚽ REGISTRAR RESULTADO"])
    
    with tab_mng:
        st.info("Haz clic en '💾 Guardar Cambios' después de editar cada equipo.")
        for id_eq, info in st.session_state.equipos.items():
            with st.expander(f"Editar {info['nombre']} (ID: {id_eq})"):
                col1, col2 = st.columns(2)
                n_name = col1.text_input("Nombre", value=info['nombre'], key=f"input_n_{id_eq}")
                n_grp = col1.selectbox("Grupo", ["A", "B", "C", "D", "E"], index=ord(info['grupo'])-65, key=f"input_g_{id_eq}")
                n_logo = col2.file_uploader("Logo", type=["png", "jpg"], key=f"input_l_{id_eq}")
                
                if st.button("💾 Guardar Cambios Equipo", key=f"save_btn_{id_eq}"):
                    st.session_state.equipos[id_eq]['nombre'] = n_name.upper()
                    st.session_state.equipos[id_eq]['grupo'] = n_grp
                    if n_logo: st.session_state.equipos[id_eq]['logo'] = Image.open(n_logo)
                    save_to_disk()
                    st.success("Guardado correctamente.")
                    st.rerun()

    with tab_match:
        st.subheader("Registrar Nuevo Resultado")
        g_sel = st.selectbox("Seleccionar Grupo", ["A", "B", "C", "D", "E"], key="admin_grupo_sel")
        eq_grupo = [info['nombre'] for info in st.session_state.equipos.values() if info['grupo'] == g_sel]
        
        if len(eq_grupo) < 2:
            st.warning("Se necesitan al menos 2 equipos en este grupo.")
        else:
            c1, c2 = st.columns(2)
            local_eq = c1.selectbox("Local", eq_grupo, key="admin_local_sel")
            visit_eq = c2.selectbox("Visitante", eq_grupo, key="admin_visit_sel")
            
            # Aquí es donde estaba el error: añadimos keys únicas 'admin_gl' y 'admin_gv'
            goles_l = c1.number_input(f"Goles {local_eq}", min_value=0, step=1, key="admin_gl")
            goles_v = c2.number_input(f"Goles {visit_eq}", min_value=0, step=1, key="admin_gv")
            
            if st.button("💾 Guardar Resultado de Partido", key="admin_save_match"):
                if local_eq == visit_eq:
                    st.error("No puedes registrar un partido contra el mismo equipo.")
                else:
                    st.session_state.partidos.append({
                        "grupo": g_sel, "local": local_eq, "visitante": visit_eq, 
                        "goles_l": goles_l, "goles_v": goles_v
                    })
                    save_to_disk()
                    st.success("¡Partido guardado!")
                    st.rerun()
