import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Champions League Style Tracker", layout="wide")

# --- ESTILOS CSS (Estilo Champions) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .group-card {
        background: linear-gradient(180deg, #0d1a44 0%, #060b26 100%);
        border-radius: 5px;
        padding: 0px;
        margin-bottom: 20px;
        border: 1px solid #1e2a5a;
        color: white;
    }
    
    .group-header {
        background-color: #0d1a44;
        padding: 10px 15px;
        border-bottom: 2px solid #0052cc;
        font-weight: bold;
        font-size: 1.1em;
        display: flex;
        justify-content: space-between;
    }
    
    .team-row {
        display: flex;
        align-items: center;
        padding: 8px 15px;
        border-bottom: 1px solid #ffffff10;
        font-size: 0.9em;
    }
    
    .team-logo {
        width: 24px;
        height: 24px;
        margin-right: 15px;
        object-fit: contain;
    }
    
    .team-name { flex-grow: 1; text-transform: uppercase; font-weight: 400; }
    .stat-val { width: 35px; text-align: center; font-weight: bold; }
    .header-labels { display: flex; color: #5c78ff; font-size: 0.8em; }
    
    /* Input styling */
    .stTextInput>div>div>input { background-color: #0d1a44; color: white; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE UTILIDAD ---
def img_to_base64(image):
    if image is None: return ""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- INICIALIZACIÓN DE DATOS ---
if 'equipos' not in st.session_state:
    # Generar 20 equipos por defecto
    equipos_iniciales = {}
    for i in range(1, 21):
        # Asignar grupos equitativamente de A a E
        grupo = chr(64 + ((i-1) // 4) + 1) # 4 equipos por grupo
        equipos_iniciales[f"ID_{i}"] = {
            "nombre": f"EQUIPO {i}",
            "grupo": grupo if i <= 20 else "A",
            "logo": None
        }
    st.session_state.equipos = equipos_iniciales

if 'partidos' not in st.session_state:
    st.session_state.partidos = []

PASSWORD_ADMIN = "admin123"

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    password = st.text_input("Contraseña Admin", type="password")
    es_admin = password == PASSWORD_ADMIN
    
    if es_admin:
        st.success("Acceso concedido")
    else:
        st.info("Modo lectura pública")

# --- LÓGICA DE CÁLCULO DE TABLAS ---
def calcular_tablas():
    stats_global = {}
    for id_eq, info in st.session_state.equipos.items():
        stats_global[info['nombre']] = {
            "PJ": 0, "GD": 0, "PTS": 0, "grupo": info['grupo'], "logo": info['logo']
        }
    
    for p in st.session_state.partidos:
        l, v = p['local'], p['visitante']
        gl, gv = p['goles_l'], p['goles_v']
        
        if l in stats_global and v in stats_global:
            stats_global[l]["PJ"] += 1
            stats_global[v]["PJ"] += 1
            stats_global[l]["GD"] += (gl - gv)
            stats_global[v]["GD"] += (gv - gl)
            
            if gl > gv: stats_global[l]["PTS"] += 3
            elif gv > gl: stats_global[v]["PTS"] += 3
            else:
                stats_global[l]["PTS"] += 1
                stats_global[v]["PTS"] += 1
                
    return stats_global

# --- VISTA PÚBLICA / PRINCIPAL ---
if not es_admin:
    st.title("🏆 UEFA CHAMPIONS LEAGUE")
    stats = calcular_tablas()
    grupos = sorted(list(set(info['grupo'] for info in st.session_state.equipos.values())))
    
    # Grid de 2 columnas para las tablas
    cols = st.columns(2)
    for idx, g in enumerate(grupos):
        with cols[idx % 2]:
            # Filtrar y ordenar equipos del grupo
            equipos_g = [info for name, info in stats.items() if info['grupo'] == g]
            equipos_g = sorted(equipos_g, key=lambda x: (x['PTS'], x['GD']), reverse=True)
            
            # Renderizado HTML estilo Champions
            html_tabla = f"""
            <div class="group-card">
                <div class="group-header">
                    <span>GROUP {g}</span>
                    <div class="header-labels">
                        <span class="stat-val">P</span>
                        <span class="stat-val">GD</span>
                        <span class="stat-val">PTS</span>
                    </div>
                </div>
            """
            for eq in equipos_g:
                logo_src = f"data:image/png;base64,{img_to_base64(eq['logo'])}" if eq['logo'] else "https://cdn-icons-png.flaticon.com/512/53/53283.png"
                html_tabla += f"""
                <div class="team-row">
                    <img src="{logo_src}" class="team-logo">
                    <span class="team-name">{eq['nombre']}</span>
                    <span class="stat-val">{eq['PJ']}</span>
                    <span class="stat-val">{eq['GD']}</span>
                    <span class="stat-val">{eq['PTS']}</span>
                </div>
                """
            html_tabla += "</div>"
            st.markdown(html_tabla, unsafe_allow_html=True)

# --- VISTA ADMINISTRADOR ---
else:
    tab_mng, tab_match = st.tabs(["⚙️ Gestionar Equipos", "⚽ Registrar Resultados"])
    
    with tab_mng:
        st.header("Base de Datos de Equipos")
        # Mostrar los 20 equipos en una lista editable
        for id_eq, info in st.session_state.equipos.items():
            with st.expander(f"Editar {info['nombre']} (Grupo {info['grupo']})"):
                c1, c2, c3 = st.columns([2, 1, 2])
                new_name = c1.text_input("Nombre", value=info['nombre'], key=f"name_{id_eq}")
                new_group = c2.selectbox("Grupo", ["A", "B", "C", "D", "E"], index=["A", "B", "C", "D", "E"].index(info['grupo']), key=f"grp_{id_eq}")
                new_logo = c3.file_uploader("Subir Logo", type=["png", "jpg"], key=f"logo_{id_eq}")
                
                if st.button("Guardar Cambios", key=f"btn_{id_eq}"):
                    st.session_state.equipos[id_eq]['nombre'] = new_name.upper()
                    st.session_state.equipos[id_eq]['grupo'] = new_group
                    if new_logo:
                        img = Image.open(new_logo)
                        st.session_state.equipos[id_eq]['logo'] = img
                    st.rerun()
                    
    with tab_match:
        st.header("Nuevo Partido")
        grupo_sel = st.selectbox("Seleccionar Grupo", ["A", "B", "C", "D", "E"])
        eq_grupo = [info['nombre'] for info in st.session_state.equipos.values() if info['grupo'] == grupo_sel]
        
        col1, col2, col3 = st.columns([2, 1, 2])
        l = col1.selectbox("Local", eq_grupo)
        v = col3.selectbox("Visitante", eq_grupo)
        gl = col1.number_input("Goles Local", min_value=0, step=1)
        gv = col3.number_input("Goles Visitante", min_value=0, step=1)
        
        if st.button("Registrar Resultado"):
            if l == v: st.error("No pueden ser el mismo equipo")
            else:
                st.session_state.partidos.append({
                    "grupo": grupo_sel, "local": l, "visitante": v, "goles_l": gl, "goles_v": gv
                })
                st.success("¡Partido Guardado!")
