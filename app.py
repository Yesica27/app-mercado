import streamlit as st
import json
from google import genai
from pydantic import BaseModel, Field

st.set_page_config(
    page_title="Planificador de Menú y Mercado",
    page_icon="🍲",
    layout="wide"
)

class IngredienteMercado(BaseModel):
    categoria: str = Field(description="Categoría del supermercado")
    item: str = Field(description="Nombre del producto")
    cantidad_aproximada: str = Field(description="Cantidad estimada")

class DiaMenu(BaseModel):
    dia: int
    almuerzo: str
    cena: str

class PlanQuincenal(BaseModel):
    menu_dias: list[DiaMenu]
    lista_mercado: list[IngredienteMercado]

st.title("🍲 Planificador Inteligente de Menú y Mercado Quincenal")
st.markdown("Organiza las comidas de tu hogar para 14 días y genera tu lista de compras automáticamente.")

st.sidebar.header("⚙️ Configuración del Hogar")

personas = st.sidebar.number_input("Número de personas:", min_value=1, max_value=10, value=3)
presupuesto = st.sidebar.selectbox("Presupuesto estimado:", ["Económico / Ahorro", "Moderado", "Alto / Gourmet"])
gustos = st.sidebar.text_area("Gustos, alergias o restricciones:", value="Comida casera variada, sin picante.")
despensa = st.sidebar.text_area("Ingredientes que ya tienes en casa:", value="Arroz, aceite, sal, azúcar, fríjoles.")

if st.sidebar.button("🚀 Generar Plan Quincenal", type="primary"):
    with st.spinner("La IA está calculando el menú óptimo y la lista de compras..."):
        try:
            client = genai.Client()

            prompt = f"""
            Eres un experto en nutrición y economía del hogar.
            Crea un plan de comidas completo para 14 días (almuerzo y cena) y una lista de mercado quincenal eficiente.

            Datos del hogar:
            - Personas: {personas}
            - Nivel de Presupuesto: {presupuesto}
            - Gustos o Restricciones: {gustos}
            - Ingredientes disponibles en despensa: {despensa}

            Reglas:
            1. Planifica 14 días con almuerzo y cena equilibrados.
            2. Reutiliza ingredientes inteligentemente para reducir costos.
            3. Organiza la lista de mercado por categorías del supermercado.
            """

            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': PlanQuincenal,
                },
            )

            st.session_state["plan"] = json.loads(response.text)
            st.success("¡Plan generado con éxito!")

        except Exception as e:
            st.error(f"Ocurrió un error al conectar con Gemini: {str(e)}")

if "plan" in st.session_state:
    plan = st.session_state["plan"]

    tab1, tab2 = st.tabs(["📅 Menú para 14 Días", "🛒 Lista de Mercado Quincenal"])

    with tab1:
        st.subheader("Planificación de Comidas")
        col1, col2 = st.columns(2)
        
        for idx, dia in enumerate(plan["menu_dias"]):
            col = col1 if idx < 7 else col2
            with col:
                st.info(f"**Día {dia['dia']}**\n\n* **Almuerzo:** {dia['almuerzo']}\n* **Cena:** {dia['cena']}")

    with tab2:
        st.subheader("Lista de Compras Organizada")
        
        categorias = {}
        for item in plan["lista_mercado"]:
            cat = item["categoria"]
            if cat not in categorias:
                categorias[cat] = []
            categorias[cat].append(item)

        for cat, items in categorias.items():
            st.write(f"### {cat}")
            for prod in items:
                st.checkbox(f"{prod['item']} — *({prod['cantidad_aproximada']})*", key=f"{cat}_{prod['item']}")