import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN Y SEGURIDAD ---
st.set_page_config(page_title="Torneo de Fútbol - Resultados", layout="wide")

# Define aquí tu contraseña de administrador
PASSWORD_ADMIN = "futbol2024" 

# Inicializar estados
if 'equipos' not in st.session_state:
    st.session_state.equipos = {}  # {nombre: grupo}
if 'partidos' not in st.session_state:
    st.session_state.partidos = []

# --- BARRA LATERAL (LOGIN) ---
with st.sidebar:
    st.title("🔐 Acceso")
    password_input = st.text_input("Contraseña de Administrador", type="password")
    
    # Verificación de identidad
    es_admin = password_input == PASSWORD_ADMIN
    
    if es_admin:
        st.success("Modo Edición: ACTIVADO")
        st.divider()
        st.header("Configuración de Equipos")
        
        # Formulario para añadir equipos (Solo visible para admin)
        with st.form("form_equipos"):
            nuevo_equipo = st.text_input("Nombre del equipo").strip()
            grupo_asignado = st.selectbox("Asignar a Grupo", ["A", "B", "C", "D", "E"])
            submit_equipo = st.form_submit_button("Añadir Equipo")
            
            if submit_equipo:
                if len(st.session_state.equipos) >= 20:
                    st.error("Límite de 20 equipos alcanzado.")
                elif nuevo_equipo == "" or nuevo_equipo in st.session_state.equipos:
                    st.warning("Nombre inválido o duplicado.")
                else:
                    st.session_state.equipos[nuevo_equipo] = grupo_asignado
                    st.success(f"{nuevo_equipo} añadido.")

        if st.button("🗑️ Resetear Torneo"):
            st.session_state.equipos = {}
            st.session_state.partidos = []
            st.rerun()
    else:
        if password_input != "":
            st.error("Contraseña incorrecta")
        st.info("Visualizando en modo: SOLO LECTURA")

# --- CUERPO PRINCIPAL ---
st.title("🏆 Resultados Torneo de Fútbol")

# Definir pestañas según el nivel de acceso
if es_admin:
    tab1, tab2, tab3 = st.tabs(["📊 Posiciones", "⚽ Registrar Partido", "📜 Historial"])
else:
    tab1, tab2 = st.tabs(["📊 Posiciones", "📜 Historial"])

# --- TAB 1: POSICIONES (Público) ---
with tab1:
    if not st.session_state.equipos:
        st.info("Esperando que el administrador configure los equipos...")
    else:
        grupos_existentes = sorted(list(set(st.session_state.equipos.values())))
        for g in grupos_existentes:
            st.subheader(f"Grupo {g}")
            equipos_en_g = [e for e, grupo in st.session_state.equipos.items() if grupo == g]
            stats = {e: {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "DG": 0, "Pts": 0} for e in equipos_en_g}
            
            for p in st.session_state.partidos:
                if p['grupo'] == g:
                    l, v, gl, gv = p['local'], p['visitante'], p['goles_l'], p['goles_v']
                    stats[l]["PJ"] += 1; stats[v]["PJ"] += 1
                    stats[l]["GF"] += gl; stats[l]["GC"] += gv
                    stats[v]["GF"] += gv; stats[v]["GC"] += gl
                    if gl > gv:
                        stats[l]["G"] += 1; stats[l]["Pts"] += 3; stats[v]["P"] += 1
                    elif gl < gv:
                        stats[v]["G"] += 1; stats[v]["Pts"] += 3; stats[l]["P"] += 1
                    else:
                        stats[l]["E"] += 1; stats[l]["Pts"] += 1
                        stats[v]["E"] += 1; stats[v]["Pts"] += 1

            for e in stats: stats[e]["DG"] = stats[e]["GF"] - stats[e]["GC"]
            df = pd.DataFrame.from_dict(stats, orient='index')
            df = df.sort_values(by=["Pts", "DG", "GF"], ascending=False)
            st.table(df)

# --- TAB: REGISTRAR PARTIDO (Solo Admin) ---
if es_admin:
    with tab2:
        st.header("Registrar Nuevo Resultado")
        if len(st.session_state.equipos) < 2:
            st.warning("Se necesitan al menos 2 equipos.")
        else:
            grupo_act = st.selectbox("Grupo", sorted(list(set(st.session_state.equipos.values()))))
            equipos_grupo = [e for e, g in st.session_state.equipos.items() if g == grupo_act]
            
            c1, c_vs, c2 = st.columns([2, 1, 2])
            local = c1.selectbox("Local", equipos_grupo)
            c_vs.markdown("<h3 style='text-align: center;'>VS</h3>", unsafe_allow_html=True)
            visitante = c2.selectbox("Visitante", equipos_grupo)
            
            g1, g2 = st.columns(2)
            gl = g1.number_input(f"Goles {local}", min_value=0, step=1)
            gv = g2.number_input(f"Goles {visitante}", min_value=0, step=1)
            
            if st.button("Guardar Resultado"):
                if local == visitante:
                    st.error("Error: Mismo equipo.")
                else:
                    st.session_state.partidos.append({
                        "grupo": grupo_act, "local": local, "visitante": visitante,
                        "goles_l": gl, "goles_v": gv
                    })
                    st.success("Resultado actualizado.")
                    st.rerun()

# --- TAB: HISTORIAL (Público) ---
historial_tab = tab3 if es_admin else tab2
with historial_tab:
    st.header("Partidos Jugados")
    if not st.session_state.partidos:
        st.write("Aún no hay partidos registrados.")
    else:
        df_partidos = pd.DataFrame(st.session_state.partidos)
        # Formatear la visualización
        df_partidos["Resultado"] = df_partidos.apply(lambda x: f"{x['local']} {x['goles_l']} - {x['goles_v']} {x['visitante']}", axis=1)
        st.dataframe(df_partidos[["grupo", "Resultado"]], use_container_width=True)
