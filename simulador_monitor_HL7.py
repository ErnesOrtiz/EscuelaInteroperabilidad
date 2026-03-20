import streamlit as st
import time

st.set_page_config(page_title="Simulador HL7 - Escuela de Interoperabilidad", layout="wide")

st.title("🏥 Simulador de Interoperabilidad: Monitor → EMR")
st.write("Bienvenido Ernesto. Este es el Nivel 1: Envío de Signos Vitales.")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Monitor de Signos")
    nombre = st.text_input("Paciente", "Juan Perez")
    bpm = st.slider("Frecuencia Cardíaca (BPM)", 40, 180, 75)
    enviar = st.button("🚀 ENVIAR MENSAJE")

if enviar:
    with col2:
        st.subheader("2. Gateway (Mensaje HL7)")
        with st.spinner('Codificando trama...'):
            time.sleep(1)
            fecha = time.strftime("%Y%m%d%H%M")
            trama = f"MSH|^~\\&|MONITOR_LEON|HOSPITAL_GTO|||{fecha}||ORU^R01|101|P|2.5\n"
            trama += f"PID|1||1001||{nombre.upper()}||19850101|M\n"
            trama += f"OBX|1|NM|BPM^Frecuencia||{bpm}|bpm|||F"
            st.code(trama, language="hl7")
            st.success("¡Mensaje enviado por MLLP!")

    with col3:
        st.subheader("3. Expediente Digital (EMR)")
        time.sleep(2)
        st.info(f"Registro actualizado para: **{nombre}**")
        st.metric(label="Pulso recibido", value=f"{bpm} BPM")
        st.success("✅ Datos guardados en la BD del Hospital")