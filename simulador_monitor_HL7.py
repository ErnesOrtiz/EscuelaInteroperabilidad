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
    # Render leerá automáticamente la variable BREVO_API_KEY que configuraste
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
        <p>Estás iniciando un camino que muy pocos deciden emprender hacia lo último en tecnología médica. 
        Pronto tendrás más noticias mías con el material para el <b>Nivel 2 (Conectividad Real con Python)</b>.</p>
        <br>
        <p>Saludos,<br><b>Ing. Ernesto Ortiz</b><br>Especialista en Biomédica e Interoperabilidad</p>
    </body>
    </html>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email_alumno}],
        # IMPORTANTE: Cambia este correo por el que validaste en Brevo como "Sender"
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

if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False
if 'timer_segundos' not in st.session_state:
    st.session_state.timer_segundos = 10

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



# --- LÓGICA DE DISPARO (TRIGGER) ---
# Se activa si presionas el botón O si el modo automático está encendido 
if enviar_manual or auto_mode:
    
    # Si es automático, agregamos una pequeña pausa visual para el loop
    if auto_mode and not enviar_manual:
        time.sleep(timer_segundos)
        # Forzamos el refresco para que los bloques 2 y 3 se actualicen
        st.rerun() 

    # --- PROCESAMIENTO (Este bloque se ejecuta solo al dispararse) ---
    anio_nac = datetime.now().year - edad
    fecha_nac = f"{anio_nac}0101"
    
with col2:
    st.subheader("2. Gateway (Mensaje HL7)")

    # --- Nueva sección de configuración dentro del Gateway ---
    with st.expander("⚙️ Configuración del Flujo", expanded=False):
        auto_mode = st.toggle("Modo Automático (Telemetría)", value=False)
        timer_segundos = st.select_slider(
            "Intervalo de actualización (seg)",
            options=[5, 10, 15, 20, 25, 30],
            value=10,
            disabled=not auto_mode
        )
        if auto_mode:
            st.info(f"🔄 Transmitiendo cada {timer_segundos}s")
    
    # --- Generación de la Trama ---
    with st.spinner('Codificando trama...'):
        time.sleep(1)
        fecha_actual = datetime.now().strftime("%Y%m%d%H%M")
        
        trama = f"MSH|^~\\&|MONITOR_LEON|{hospital.upper()}|||{fecha_actual}||ORU^R01|101|P|2.5\n"
        trama += f"PID|1||1001||{nombre.upper()}||{fecha_nac}|M\n"
        trama += f"PV1|1|I|{area.upper()}^^||||||||||||||||\n"
        trama += f"OBX|1|NM|BPM^Frecuencia||{bpm}|bpm|||F"
        
        st.code(trama, language="hl7")
        st.success(f"¡Mensaje enviado desde {area}!")

    # Lógica de autorefresh (opcional, requiere streamlit-autorefresh)
    # if auto_mode:
    #    st_autorefresh(interval=timer_segundos * 1000, key="gateway_refresh")

    with col3:
        st.subheader("3. Historial Clínico (HIS)")
        time.sleep(1.5)
        st.info(f"Paciente: **{nombre}** ({edad} años)")
        st.info(f"Ubicación: **{area}**")
        st.metric(label="Pulso recibido", value=f"{bpm} BPM")
        st.success("✅ Registro almacenado exitosamente")

        st.divider()
        
        # Botón de Descarga
        st.download_button(
            label="📥 Descargar Trama HL7 (.hl7)",
            data=trama,
            file_name=f"mensaje_{nombre.replace(' ', '_')}.hl7",
            mime="text/plain"
        )

        # Formulario de Captura
        st.write("---")
        st.write("**📩 ¿Quieres seguir aprendiendo?**")
        with st.form("academia_form", clear_on_submit=True):
            email = st.text_input("Tu mejor correo:")
            submitted = st.form_submit_button("Si quiero!")
            
            if submitted:
                if "@" in email:
                    with st.spinner('Registrándote...'):
                        exito = enviar_bienvenida_brevo(email, nombre, hospital)
                    
                    if exito:
                        st.balloons()
                        st.markdown(f"### 🚀 ¡Bienvenido, **{email.split('@')[0]}**!")
                        st.write("Te esperan un emocionante camino hacia lo último en tecnología médica. Revisa tu correo.")
                    else:
                        st.warning("Te hemos registrado, pero hubo un detalle al enviar el correo automático. Pronto te contactaré.")
                else:
                    st.error("Por favor, introduce un correo válido.")