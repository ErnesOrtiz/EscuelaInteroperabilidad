import streamlit as st
import time
import os
from datetime import datetime
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Academia de Interoperabilidad | Nivel 1", layout="wide")

# --- FUNCIÓN PARA ENVIAR CORREO VÍA BREVO ---
def enviar_bienvenida_brevo(email_alumno, nombre_paciente, hospital):
configuration = sib_api_v3_sdk.Configuration()
api_key = os.getenv('BREVO_API_KEY')

# Limpiamos cualquier espacio y forzamos que sea String
if api_key:
    configuration.api_key['api-key'] = str(api_key).strip()
else:
    print("ERROR: No se encontró la variable BREVO_API_KEY")
    
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
        <p>Estás iniciando un camino que muy pocos deciden emprender hacia lo último en tecnología médica. 
        Pronto tendrás más noticias mías con el material para el <b>Nivel 2 (Conectividad Real con Python)</b>.</p>
        <br>
        <p>Saludos,<br><b>Ing. Ernesto Ortiz</b><br>Especialista en Biomédica e Interoperabilidad</p>
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
    except ApiException as e:
        print(f"Error en Brevo: {e}")
        return False

# --- INTERFAZ DE USUARIO ---
st.title("🏥 Academia de Interoperabilidad Sanitaria")
st.subheader("Nivel 1: De la Cama del Paciente al Expediente Digital")

st.markdown("""
### ¡Bienvenido al Futuro de la Ingeniería Clínica!
Basado en estándares reales de la industria (**HL7 v2.5**), este ejercicio te muestra el viaje de los datos:
1. **Captura** en el monitor. 2. **Codificación** en el Gateway. 3. **Almacenamiento** en el EMR.
""")

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

# --- PROCESAMIENTO ---
if enviar:
    # Guardamos en session_state para que el formulario de abajo los pueda usar
    st.session_state['nombre_paciente'] = nombre
    st.session_state['hospital_paciente'] = hospital
    
    anio_nac = datetime.now().year - edad
    fecha_nac = f"{anio_nac}0101"
    
    with col2:
        st.subheader("2. Gateway (Mensaje HL7)")
        with st.spinner('Codificando trama...'):
            time.sleep(1)
            fecha_actual = datetime.now().strftime("%Y%m%d%H%M")
            trama = f"MSH|^~\\&|MONITOR_LEON|{hospital.upper()}|||{fecha_actual}||ORU^R01|101|P|2.5\n"
            trama += f"PID|1||1001||{nombre.upper()}||{fecha_nac}|M\n"
            trama += f"PV1|1|I|{area.upper()}^^||||||||||||||||\n"
            trama += f"OBX|1|NM|BPM^Frecuencia||{bpm}|bpm|||F"
            st.code(trama, language="hl7")
            st.success(f"¡Mensaje enviado desde {area}!")

    with col3:
        st.subheader("3. Expediente Digital (EMR)")
        time.sleep(1.5)
        st.info(f"Paciente: **{nombre}** ({edad} años)")
        st.info(f"Ubicación: **{area}**")
        st.metric(label="Pulso recibido", value=f"{bpm} BPM")
        st.success("✅ Registro almacenado exitosamente")
        st.divider()
        st.download_button(
            label="📥 Descargar Trama HL7 (.hl7)",
            data=trama,
            file_name=f"mensaje_{nombre.replace(' ', '_')}.hl7",
            mime="text/plain"
        )

# --- FORMULARIO DE REGISTRO (FUERA DEL IF PRINCIPAL) ---
st.write("---")
st.write("**📩 ¿Quieres recibir el material del Nivel 2?**")

# Recuperamos datos de la sesión o usamos valores por defecto si no han enviado nada arriba
nombre_final = st.session_state.get('nombre_paciente', 'Estudiante')
hospital_final = st.session_state.get('hospital_paciente', 'Hospital General')

with st.form("academia_form", clear_on_submit=True):
    email = st.text_input("Tu mejor correo para enviarte el Nivel 2:")
    submitted = st.form_submit_button("¡Si, enviame el material!")
    
    if submitted:
        if "@" in email:
            with st.spinner('Procesando registro...'):
                exito = enviar_bienvenida_brevo(email, nombre_final, hospital_final)
            if exito:
                st.balloons()
                st.success(f"¡Perfecto! Revisa tu correo **{email}**. ¡Nos vemos en el Nivel 2!")
            else:
                st.error("Hubo un detalle con la conexión a Brevo. Revisa los Logs en Render.")
        else:
            st.error("Por favor, introduce un correo válido.")