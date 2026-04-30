import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Gestor de Torneo de Fútbol", layout="wide")

# Inicializar el estado de la aplicación
if 'equipos' not in st.session_state:
    st.session_state.equipos = {}  # {nombre: grupo}
if 'partidos' not in st.session_state:
    st.session_state.partidos = [] # Listado de dicts con resultados

st.title("🏆 Gestor de Torneo Pro")

# --- BARRA LATERAL: CONFIGURACIÓN ---
with st.sidebar:
    st.header("Configuración de Equipos")
    
    # Formulario para añadir equipos
    with st.form("form_equipos"):
        nuevo_equipo = st.text_input("Nombre del equipo").strip()
        grupo_asignado = st.selectbox("Asignar a Grupo", ["A", "B", "C", "D", "E"])
        submit_equipo = st.form_submit_button("Añadir Equipo")
        
        if submit_equipo:
            if len(st.session_state.equipos) >= 20:
                st.error("Límite de 20 equipos alcanzado.")
            elif nuevo_equipo == "":
                st.warning("El nombre no puede estar vacío.")
            elif nuevo_equipo in st.session_state.equipos:
                st.warning("Ese equipo ya existe.")
            else:
                st.session_state.equipos[nuevo_equipo] = grupo_asignado
                st.success(f"{nuevo_equipo} añadido al Grupo {grupo_asignado}")

    if st.button("Resetear Torneo"):
        st.session_state.equipos = {}
        st.session_state.partidos = []
        st.rerun()

# --- CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["⚽ Registrar Partido", "📊 Tabla de Posiciones"])

with tab1:
    st.header("Resultados de la Jornada")
    if len(st.session_state.equipos) < 2:
        st.info("Añade al menos 2 equipos en la barra lateral para empezar.")
    else:
        # Filtrar por grupo para registrar partido
        grupo_act = st.selectbox("Seleccionar Grupo para el partido", sorted(list(set(st.session_state.equipos.values()))))
        equipos_grupo = [e for e, g in st.session_state.equipos.items() if g == grupo_act]
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            local = st.selectbox("Local", equipos_grupo, key="local")
        with col2:
            st.markdown("<h3 style='text-align: center;'>VS</h3>", unsafe_allow_html=True)
        with col3:
            visitante = st.selectbox("Visitante", equipos_grupo, key="visitante")
            
        c1, c2 = st.columns(2)
        goles_l = c1.number_input(f"Goles {local}", min_value=0, step=1)
        goles_v = c2.number_input(f"Goles {visitante}", min_value=0, step=1)
        
        if st.button("Guardar Resultado"):
            if local == visitante:
                st.error("Un equipo no puede jugar contra sí mismo.")
            else:
                st.session_state.partidos.append({
                    "grupo": grupo_act,
                    "local": local,
                    "visitante": visitante,
                    "goles_l": goles_l,
                    "goles_v": goles_v
                })
                st.success("¡Resultado guardado!")

with tab2:
    st.header("Tablas de Posiciones")
    
    if not st.session_state.equipos:
        st.info("No hay equipos registrados.")
    else:
        grupos_existentes = sorted(list(set(st.session_state.equipos.values())))
        
        for g in grupos_existentes:
            st.subheader(f"Grupo {g}")
            
            # Crear base de la tabla para el grupo
            equipos_en_g = [e for e, grupo in st.session_state.equipos.items() if grupo == g]
            stats = {e: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "Pts": 0} for e in equipos_en_g}
            
            # Procesar partidos del grupo
            for p in st.session_state.partidos:
                if p['grupo'] == g:
                    l, v = p['local'], p['visitante']
                    gl, gv = p['goles_l'], p['goles_v']
                    
                    # Actualizar goles
                    stats[l]["GF"] += gl
                    stats[l]["GC"] += gv
                    stats[v]["GF"] += gv
                    stats[v]["GC"] += gl
                    stats[l]["PJ"] += 1
                    stats[v]["PJ"] += 1
                    
                    # Calcular Puntos
                    if gl > gv:
                        stats[l]["G"] += 1; stats[l]["Pts"] += 3
                        stats[v]["P"] += 1
                    elif gl < gv:
                        stats[v]["G"] += 1; stats[v]["Pts"] += 3
                        stats[l]["P"] += 1
                    else:
                        stats[l]["E"] += 1; stats[l]["Pts"] += 1
                        stats[v]["E"] += 1; stats[v]["Pts"] += 1
            
            # Calcular Diferencia de Goles y preparar DataFrame
            for e in stats:
                stats[e]["DG"] = stats[e]["GF"] - stats[e]["GC"]
            
            df = pd.DataFrame.from_dict(stats, orient='index')
            # Ordenar por Puntos, luego Diferencia de Goles, luego Goles a Favor
            df = df.sort_values(by=["Pts", "DG", "GF"], ascending=False)
            
            st.table(df)
