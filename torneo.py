import streamlit as st
import pandas as pd
from PIL import Image
import io
import base64

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Champions League Style Tracker", layout="wide")

# --- 2. ESTILOS CSS (Personalización de la Tabla) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .group-card {
        background: linear-gradient(180deg, #0d1a44 0%, #060b26 100%);
        border-radius: 8px;
        padding: 0px;
        margin-bottom: 25px;
        border: 1px solid #1e2a5a;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .group-header {
        background-color: #0d1a44;
        padding: 12px 15px;
        border-bottom: 2px solid #0052cc;
        font-weight: bold;
        font-size: 1.1em;
        display: flex;
        justify-content: space-between;
        border-radius: 8px 8px 0 0;
    }
    
    .team-row {
        display: flex;
        align-items: center;
        padding: 10px 15px;
        border-bottom: 1px solid #ffffff10;
        font-size: 0.95em;
    }
    
    .team-row:last-child { border-bottom: none; }
    
    .team-logo {
        width: 28px;
        height: 28px;
        margin-right: 15px;
        object-fit: contain;
    }
    
    .team-name { flex-grow: 1; text-transform: uppercase; font-weight: 500; letter-spacing: 0.5px; }
    .stat-val { width: 40px; text-align: center; font-weight: bold; }
    .header-labels { display: flex; color: #5c78ff; font-size: 0.85em; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE APOYO ---
def img_to_base64(image):
    """Convierte objeto PIL Image a string base64 para mostrar en HTML"""
    if image is None: return ""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def calcular_tablas():
    """Procesa los partidos y genera las estadísticas por equipo"""
    stats_global = {}
    
    # Inicializar estadísticas para cada equipo
    for id_eq, info in st.session_state.equipos.items():
        stats_global[info['nombre']] = {
            "nombre": info['nombre'],  # Corregido: Clave necesaria para el renderizado
            "PJ": 0, 
            "GD": 0, 
            "PTS": 0, 
            "grupo": info['grupo'], 
            "logo": info['logo']
        }
    
    # Procesar resultados registrados
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

# --- 4. INICIALIZACIÓN DE DATOS (20 Equipos) ---
if 'equipos' not in st.session_state:
    equipos_iniciales = {}
    for i in range(1, 21):
        # Distribución automática: 4 equipos por grupo (A, B, C, D, E)
        grupo = chr(64 + ((i-1) // 4) + 1) 
        equipos_iniciales[f"ID_{i}"] = {
            "nombre": f"EQUIPO {i}",
            "grupo": grupo,
            "logo": None
        }
    st.session_state.equipos = equipos_iniciales

if 'partidos' not in st.session_state:
    st.session_state.partidos = []

PASSWORD_ADMIN = "admin123"

# --- 5. BARRA LATERAL (Admin) ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    password = st.text_input("Contraseña de Acceso", type="password")
    es_admin = password == PASSWORD_ADMIN
    
    if es_admin:
        st.success("Modo Edición: ON")
        st.divider()
        if st.button("🗑️ Resetear Todos los Partidos"):
            st.session_state.partidos = []
            st.rerun()
    else:
        st.info("Visualizando como Espectador")

# --- 6. INTERFAZ PRINCIPAL ---
st.title("🏆 UEFA CHAMPIONS LEAGUE")

if not es_admin:
    # --- VISTA PÚBLICA (TABLAS Y RESULTADOS) ---
    tab_pos, tab_res = st.tabs(["📊 TABLA DE POSICIONES", "⚽ ÚLTIMOS RESULTADOS"])
    
    with tab_pos:
        stats = calcular_tablas()
        grupos = sorted(list(set(info['grupo'] for info in st.session_state.equipos.values())))
        
        # Grid de 2 columnas para un look más compacto
        cols = st.columns(2)
        for idx, g in enumerate(grupos):
            with cols[idx % 2]:
                # Filtrar y ordenar equipos por Puntos > Diferencia de Goles
                equipos_g = [info for name, info in stats.items() if info['grupo'] == g]
                equipos_g = sorted(equipos_g, key=lambda x: (x['PTS'], x['GD']), reverse=True)
                
                # HTML Personalizado para la tabla
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
                    # Si no hay logo, usar uno por defecto
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
    
    with tab_res:
        if not st.session_state.partidos:
            st.info("No hay partidos jugados todavía.")
        else:
            for p in reversed(st.session_state.partidos):
                st.markdown(f"**Grupo {p['grupo']}**: {p['local']} **{p['goles_l']} - {p['goles_v']}** {p['visitante']}")

else:
    # --- VISTA ADMINISTRADOR (EDICIÓN Y CARGA) ---
    tab_mng, tab_match = st.tabs(["⚙️ GESTIONAR EQUIPOS / LOGOS", "⚽ REGISTRAR PARTIDO"])
    
    with tab_mng:
        st.subheader("Configuración de los 20 Equipos")
        for id_eq, info in st.session_state.equipos.items():
            with st.expander(f"📝 Editar: {info['nombre']} (Grupo {info['grupo']})"):
                c1, c2 = st.columns([2, 2])
                new_name = c1.text_input("Nombre del Equipo", value=info['nombre'], key=f"n_{id_eq}")
                new_group = c1.selectbox("Grupo", ["A", "B", "C", "D", "E"], index=["A", "B", "C", "D", "E"].index(info['grupo']), key=f"g_{id_eq}")
                new_logo = c2.file_uploader("Cargar Logo (PNG/JPG)", type=["png", "jpg"], key=f"l_{id_eq}")
                
                if st.button("Actualizar Equipo", key=f"b_{id_eq}"):
                    st.session_state.equipos[id_eq]['nombre'] = new_name.upper()
                    st.session_state.equipos[id_eq]['grupo'] = new_group
                    if new_logo:
                        st.session_state.equipos[id_eq]['logo'] = Image.open(new_logo)
                    st.success("Cambios guardados.")
                    st.rerun()

    with tab_match:
        st.subheader("Ingresar Resultado")
        grupo_sel = st.selectbox("Seleccionar Grupo", ["A", "B", "C", "D", "E"], key="sel_g")
        eq_grupo = [info['nombre'] for info in st.session_state.equipos.values() if info['grupo'] == grupo_sel]
        
        if len(eq_grupo) < 2:
            st.warning("Necesitas al menos 2 equipos en este grupo.")
        else:
            col1, col_vs, col2 = st.columns([2, 1, 2])
            l = col1.selectbox("Local", eq_grupo, key="sel_l")
            v = col2.selectbox("Visitante", eq_grupo, key="sel_v")
            gl = col1.number_input(f"Goles {l}", min_value=0, step=1, key="gl")
            gv = col2.number_input(f"Goles {v}", min_value=0, step=1, key="gv")
            
            if st.button("✅ Guardar Resultado"):
                if l == v:
                    st.error("Un equipo no puede jugar contra sí mismo.")
                else:
                    st.session_state.partidos.append({
                        "grupo": grupo_sel, "local": l, "visitante": v, "goles_l": gl, "goles_v": gv
                    })
                    st.success("¡Resultado registrado con éxito!")
                    st.rerun()
