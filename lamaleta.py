import streamlit as st
import openai
import requests
from dotenv import dotenv_values
from textwrap import dedent
from datetime import date

# Leer claves directamente desde el archivo .env
config = dotenv_values("llaves.env")
OPENAI_API_KEY = config["OPENAI_API_KEY"]
WEATHER_API_KEY = config["WEATHER_API_KEY"]

# Configura cliente de OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Interfaz de la app
st.title("🎒 La maleta de Aleja")
st.caption("Empaca con estilo según destino, clima y actividades ✨")

# Inputs del usuario
destination = st.text_input("📍 ¿A qué ciudad viajas?")
start_date = st.date_input("📅 ¿Cuándo comienza tu viaje?", value=date.today())
num_days = st.number_input("🕒 ¿Cuántos días vas a estar?", min_value=1, max_value=90, value=5)
luggage_type = st.selectbox("🧳 ¿Qué tipo de maleta llevas?", ["Equipaje de mano (10kg)", "Mediana (23kg)", "Grande (32kg)"])
activities = st.multiselect("🎯 ¿Qué actividades planeas?", ["Trabajo", "Turismo", "Caminatas", "Playa / Piscina", "Cena elegante", "Salir con amigos"])

# Función para obtener el clima
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=es"
    try:
        res = requests.get(url)
        data = res.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"{description}, {round(temp)}°C"
    except:
        return "No se pudo obtener el clima."

# Botón para generar la checklist
if st.button("👚 ¿Qué empaco?") and destination:
    with st.spinner("🧠 Analizando destino, clima y estilo..."):

        weather = get_weather(destination)
        activity_str = ", ".join(activities) if activities else "actividades generales"

        prompt = dedent(f"""
        Eres una asesora de imagen profesional para viajeros.

        El usuario va a viajar a {destination} durante {num_days} días, a partir del {start_date.strftime('%d de %B de %Y')}.
        Lleva una maleta tipo: {luggage_type}.
        Clima actual en el destino: {weather}.
        Actividades previstas: {activity_str}.

        Tu tarea:
        - Sugiere una checklist de ropa, calzado y accesorios adecuados al clima, la duración y el tipo de maleta.
        - Asegúrate de incluir ropa combinable para evitar llevar de más.
        - Incluye elementos de cuidado personal (como bloqueador, shampoo, cargador, etc.)
        - Muestra el resultado en formato lista con viñetas y en español.
        - Agrega un consejo de estilo y organización al final.
        """)

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres una asesora de imagen experta, cálida y práctica."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.85
            )

            plan = response.choices[0].message.content
            st.markdown(plan)

        except Exception as e:
            st.error(f"❌ Error: {e}")
