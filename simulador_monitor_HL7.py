import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="Simulador HL7 - Escuela de Interoperabilidad", layout="wide")

st.title("🏥 Simulador de Interoperabilidad: Monitor → EMR")
st.write("Bienvenido Ernesto. Este es el Nivel 1: Envío de Signos Vitales.")

# --- SECCIÓN DE ENTRADA DE DATOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Monitor de Signos")
    hospital = st.text_input("Nombre del Hospital", "Hospital General León")
    area = st.selectbox("Área / Unidad", ["Urgencias", "UCI", "Quirófano", "Piso 3"])
    
    st.divider()
    
    nombre = st.text_input("Paciente", "Juan Perez")
    edad = st.number_input("Edad del Paciente", min_value=0, max_value=120, value=35)
    bpm = st.slider("Frecuencia Cardíaca (BPM)", 40, 180, 75)
    
    enviar = st.button("🚀 ENVIAR MENSAJE")

# --- PROCESAMIENTO Y VISUALIZACIÓN ---
if enviar:
    # Calculamos fecha de nacimiento ficticia basada en la edad
    anio_nac = datetime.now().year - edad
    fecha_nac = f"{anio_nac}0101" # Formato AAAAMMDD
    
    with col2:
        st.subheader("2. Gateway (Mensaje HL7)")
        with st.spinner('Codificando trama...'):
            time.sleep(1)
            fecha_actual = datetime.now().strftime("%Y%m%d%H%M")
            
            # MSH: El hospital va en el campo 4 (Sending Facility)
            trama = f"MSH|^~\\&|MONITOR_LEON|{hospital.upper()}|||{fecha_actual}||ORU^R01|101|P|2.5\n"
            
            # PID: La fecha de nacimiento (edad) va en el campo 7
            trama += f"PID|1||1001||{nombre.upper()}||{fecha_nac}|M\n"
            
            # PV1: El área (Patient Visit) va en el campo 3
            trama += f"PV1|1|I|{area.upper()}^^||||||||||||||||"
            
            # OBX: Los signos vitales
            trama += f"\nOBX|1|NM|BPM^Frecuencia||{bpm}|bpm|||F"
            
            st.code(trama, language="hl7")
            st.success(f"¡Mensaje enviado desde {area}!")

    with col3:
        st.subheader("3. Expediente Digital (EMR)")
        time.sleep(2)
        st.info(f"Hospital: **{hospital}**")
        st.info(f"Paciente: **{nombre}** ({edad} años)")
        st.info(f"Ubicación: **{area}**")
        
        st.metric(label="Pulso recibido", value=f"{bpm} BPM")
        st.success("✅ Registro almacenado exitosamente")