import streamlit as st
import time
import os
import pandas as pd  # <--- IMPORTANTE: Faltaba esta línea para la gráfica
from datetime import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Academia de Interoperabilidad | Nivel 1", layout="wide")

# --- 1. INICIALIZACIÓN DE ESTADOS (Session State) ---
# Esto debe ir al principio para evitar errores de "variable not defined"
if 'historial_bpm' not in st.session_state:
    st.session_state.historial_bpm = []

# --- FUNCIÓN PARA ENVIAR CORREO VÍA BREVO ---
def enviar_bienvenida_brevo(email_alumno, nombre_paciente, hospital):
    configuration = sib_api_v3_sdk.Configuration()
    api_key = os.getenv('BREVO_API_KEY')
    configuration.api_key['api-key'] = api_key
    
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    contenido_html = f"""
    <html>
    <body>
        <h2 style='color: #2e7d32;'>¡Bienvenido a la Academia de Interoperabilidad! 🏥</h2>
        <p>Hola, es un gusto saludarte. Soy <b>Ernesto Ortiz</b>.</p>
        <p>Has completado con éxito el <b>Nivel 1</b> usando nuestro simulador HL7.</p>
        <hr>
        <p><b>Resumen de tu ejercicio técnico:</b></p>
        <ul>
            <li><b>Paciente:</b> {nombre_paciente}</li>
            <li><b>Hospital:</b> {hospital}</li>
        </ul>
        <br>
        <p>Saludos,<br><b>Ing. Ernesto Ortiz</b></p>
    </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email_alumno}],
        sender={"name": "Ernesto Ortiz | Academia HL7", "email": "ernestobiomedico21@gmail.com"},
        subject="🚀 ¡Iniciaste tu camino en Interoperabilidad!",
        html_content=contenido_html
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException:
        return False

# --- INTERFAZ DE USUARIO ---
st.title("🏥 Academia de Interoperabilidad Sanitaria")
st.subheader("Nivel 1: De la Cama del Paciente al Expediente Digital")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1. Monitor de Signos")
    hospital = st.text_input("Nombre del Hospital", "Hospital General León")
    area = st.selectbox("Área / Unidad", ["Urgencias", "UCI", "Quirófano", "Piso 3"])
    st.divider()
    nombre = st.text_input("Paciente", "Juan Perez")
    edad = st.number_input("Edad del Paciente", min_value=0, max_value=120, value=35)
    bpm = st.slider("Frecuencia Cardíaca (BPM)", 40, 180, 75)
    enviar_manual = st.button("🚀 ENVIAR MENSAJE")

with col2:
    st.subheader("2. Gateway (Mensaje HL7)")
    
    # Configuración dentro del bloque Gateway
    with st.expander("⚙️ Configuración del Flujo", expanded=True):
        auto_mode = st.toggle("Modo Automático (Telemetría)", value=False, key="auto_toggle")
        timer_segundos = st.select_slider(
            "Intervalo de actualización (seg)",
            options=[5, 10, 15, 20, 25, 30],
            value=10,
            disabled=not auto_mode
        )

    # Lógica de procesamiento
    anio_nac = datetime.now().year - edad
    fecha_nac = f"{anio_nac}0101"
    fecha_actual = datetime.now().strftime("%Y%m%d%H%M")
    
    trama = f"MSH|^~\\&|MONITOR_LEON|{hospital.upper()}|||{fecha_actual}||ORU^R01|101|P|2.5\n"
    trama += f"PID|1||1001||{nombre.upper()}||{fecha_nac}|M\n"
    trama += f"PV1|1|I|{area.upper()}^^||||||||||||||||\n"
    trama += f"OBX|1|NM|BPM^Frecuencia||{bpm}|bpm|||F"

    with st.spinner('Codificando trama...'):
        st.code(trama, language="hl7")
        # Guardar en historial para la gráfica si hay actividad
        if enviar_manual or auto_mode:
            st.session_state.historial_bpm.append({"Hora": datetime.now().strftime("%H:%M:%S"), "BPM": bpm})
            if len(st.session_state.historial_bpm) > 15: st.session_state.historial_bpm.pop(0)

with col3:
    st.subheader("3. Historial Clínico (HIS)")
    st.info(f"Paciente: **{nombre}**")
    st.metric(label="Pulso recibido", value=f"{bpm} BPM")
    
    # --- GRÁFICA DE TENDENCIA ---
    st.write("**📈 Tendencia de Telemetría**")
    if st.session_state.historial_bpm:
        df_bpm = pd.DataFrame(st.session_state.historial_bpm)
        st.line_chart(df_bpm.set_index("Hora"))
    
    st.divider()
    
    st.download_button(
        label="📥 Descargar Trama HL7",
        data=trama,
        file_name=f"mensaje_{nombre.replace(' ', '_')}.hl7"
    )

    # Formulario de Captura
    with st.form("academia_form", clear_on_submit=True):
        email = st.text_input("Tu mejor correo:")
        submitted = st.form_submit_button("¡Sí quiero!")
        if submitted and "@" in email:
            if enviar_bienvenida_brevo(email, nombre, hospital):
                st.balloons()
                st.success("¡Revisa tu correo!")

# --- LÓGICA DE AUTO-REFRESCO ---
if auto_mode:
    time.sleep(timer_segundos)
    st.rerun()