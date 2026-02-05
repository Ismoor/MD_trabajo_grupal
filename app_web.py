# app_web.py
"""
Interfaz web simple para el bot de viajes usando Streamlit.
Ejecutar con: streamlit run app_web.py
"""
import streamlit as st
import json
from nlp_parser import parse_user_message
from iata_service import build_final_json

# Configuración de la página
st.set_page_config(
    page_title="Bot de Búsqueda de Vuelos",
    page_icon="✈️",
    layout="centered"
)

# Título
st.title("Bot de Búsqueda de Vuelos")
st.markdown("---")

# Información inicial
with st.expander("Cómo usar"):
    st.markdown("""
    **Escribe tu solicitud de vuelo en lenguaje natural:**
    
    Ejemplos:
    - `Billete de Quito a Madrid con Iberia para el 15 de agosto`
    - `2 billetes a Roma en septiembre con Lufthansa`
    - `Tres pasajes de Barcelona a París con Air France el 10 de marzo`
    
    El sistema extraerá automáticamente:
    - 📍 Origen y Destino
    - 📅 Fecha
    - 👥 Cantidad de pasajeros
    - ✈️ Aerolínea
    - 🏷️ Códigos IATA de aeropuertos
    """)

# Input del usuario
st.markdown("### Tu solicitud:")
mensaje = st.text_input(
    "",
    placeholder="Ej: Billete de Quito a Madrid con Iberia para el 15 de agosto",
    label_visibility="collapsed"
)

# Botón de búsqueda
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    buscar = st.button("Buscar Vuelo", use_container_width=True)

# Procesar cuando se hace clic en buscar
if buscar and mensaje:
    with st.spinner("Procesando tu solicitud..."):
        
        # Paso 1: Parsear el mensaje
        st.markdown("---")
        st.markdown("### 🔄 Procesamiento")
        
        parsed = parse_user_message(mensaje)
        
        # Validar datos faltantes
        faltantes = []
        if not parsed.get("origen"):
            faltantes.append("origen")
        if not parsed.get("destino"):
            faltantes.append("destino")
        if not parsed.get("fecha"):
            faltantes.append("fecha")
        if not parsed.get("aerolínea"):
            faltantes.append("aerolínea")
        
        if faltantes:
            st.error(f"Faltan datos: {', '.join(faltantes)}")
            st.info("Intenta incluir todos los detalles: origen, destino, fecha y aerolínea")
        else:
            # Paso 2: Generar JSON final con IATA
            try:
                final = build_final_json(parsed)
                
                st.success("¡Búsqueda exitosa!")
                
                # Mostrar resultado de forma visual
                st.markdown("---")
                st.markdown("### Resultado de la Búsqueda")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Origen", final["Ciudad Origen"])
                    st.caption(f"Código IATA: {final['IATA From'] or 'N/A'}")
                    
                with col2:
                    st.metric("Destino", final["Ciudad Destino"])
                    st.caption(f"Código IATA: {final['IATA To'] or 'N/A'}")
                
                col3, col4, col5 = st.columns(3)
                
                with col3:
                    st.metric("Fecha", final["Fecha"] or "No especificada")
                
                with col4:
                    st.metric("Pasajeros", final["Pax"])
                
                with col5:
                    st.metric("Aerolínea", final["Aerolínea"] or "N/A")
                
                # JSON final completo
                st.markdown("---")
                st.markdown("### JSON Final (para sistema de reservas)")
                st.json(final)
                
                # Botón para copiar
                st.code(json.dumps(final, indent=2, ensure_ascii=False), language="json")
                
            except Exception as e:
                st.error(f"Error al procesar: {e}")

elif buscar and not mensaje:
    st.warning("Por favor, escribe tu solicitud de vuelo")

# Pie de página
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>
        🎓 Universidad Politécnica Salesiana - Minería de Datos<br>
        Grupo N°1: Milton Peralta | Mishelle Menéndez | Anthony Vega
        </small>
    </div>
    """,
    unsafe_allow_html=True
)
