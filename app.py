import streamlit as st
from openai import OpenAI
from gpt import get_diagnosis
from gsheets import authenticate_google_sheets, save_to_google_sheet

API_KEY = st.secrets["api_key"]
ASSISTANT_ID = st.secrets["assistant_id"]
EXCEL_NAME = st.secrets["excel_name"]
CREDS = st.secrets["gcp_service_account"]
client = OpenAI(api_key=API_KEY)


def trim_text(text):
    """
    Trims the input text by removing leading/trailing whitespace, extra spaces,
    and unnecessary line breaks, and condensing the content for cleaner storage.
    """
    # Remove leading and trailing whitespace
    trimmed_text = text.strip()

    # Replace multiple spaces with a single space
    trimmed_text = " ".join(trimmed_text.split())

    # Optionally, remove excessive line breaks (you can customize this)
    trimmed_text = trimmed_text.replace("\n", " ").replace("\r", "")

    # Further trimming for specific formats, if needed
    # (e.g., remove unwanted punctuation, extra tabs, etc.)

    return trimmed_text


# Configuração da interface do Streamlit
st.title("Diagnóstico Assistido por IA")
st.subheader("Insira as informações do paciente para obter uma análise clínica")

# Inputs do usuário
data_nascimento = st.text_input("Data de Nascimento", "05/09/1974")
genero = st.selectbox("Gênero", ["Feminino", "Masculino"])
problemas = st.text_area(
    "Problemas Relatados",
    "Fadiga constante, ganho de peso sem mudanças na dieta, pele seca, queda de cabelo, intolerância ao frio, dores musculares e articulares frequentes, e constipação.",
)
alergias = st.text_input("Alergias", "Não")
medicacoes = st.text_input(
    "Medicações em Uso", "Nenhuma medicação regular além de suplementos vitamínicos."
)
historico_familiar = st.text_input(
    "Histórico Familiar", "Mãe tem hipotireoidismo, pai tem diabetes tipo 2."
)
habitos = st.text_area(
    "Hábitos",
    "Sedentária, trabalha em um escritório e passa a maior parte do dia sentada.",
)

# Dados formatados para o envio
patient_data = f"""
             Data de Nascimento: {data_nascimento}
             Gênero: {genero}
             Problemas relatados: {problemas}
             Alergias: {alergias}
             Medicações em Uso: {medicacoes}
             Histórico Familiar: {historico_familiar}
             Hábitos: {habitos}
         """

if st.button("Obter Diagnóstico"):
    # Enviar dados para a API e mostrar o resultado
    st.write("Consultando o diagnóstico...")
    api_response = get_diagnosis(client, patient_data, ASSISTANT_ID)
    st.write(api_response)
    sheet = authenticate_google_sheets(CREDS, EXCEL_NAME)
    save_to_google_sheet(sheet, trim_text(patient_data), trim_text(api_response))
