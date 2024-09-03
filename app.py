import streamlit as st
from openai import OpenAI
import json
from gpt import get_diagnosis
from datetime import datetime
from gsheets import authenticate_google_sheets, save_to_google_sheet

API_KEY = st.secrets["api_key"]
ASSISTANT_ID = st.secrets["assistant_id"]
EXCEL_NAME = st.secrets["excel_name"]
CREDS = st.secrets["gcp_service_account"]
client = OpenAI(api_key=API_KEY)

# Set the sidebar to be collapsed by default
st.set_page_config(
    page_title="Diagnóstico Assistido por IA",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="auto",
)

footer = """<style>
a:link, a:visited {
    color: white;
    background-color: transparent;
    text-decoration: underline;
}
a:hover, a:active {
    color: red;
    background-color: transparent;
    text-decoration: underline;
}
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: transparent;
    color: white;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 5px; /* Adds a small space between text and link */
}
</style>

<div class="footer">
    <p style="margin: 0;">Desenvolvido por</p>
    <a href="https://www.linkedin.com/in/thiago-bellotto/" target="_blank">Thiago Bellotto Rosa</a>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)

st.markdown(
    "<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>",
    unsafe_allow_html=True,
)

if "use_default" not in st.session_state:
    st.session_state.use_default = False

if "show_soap" not in st.session_state:
    st.session_state.show_soap = False


## Function to toggle default values
def toggle_defaults():
    st.session_state.use_default = not st.session_state.use_default


## Function to toggle SOAP fields visibility
def toggle_soap():
    st.session_state.show_soap = not st.session_state.show_soap


## Configuração da interface do Streamlit
st.title("Diagnóstico Assistido por IA")
st.checkbox("Inserir Texto Padrão?", on_change=toggle_defaults)

## Add the "About the App" section to the sidebar
with st.sidebar:
    st.header("Sobre o App")
    st.sidebar.info(
        """
        Este aplicativo é uma ferramenta experimental desenvolvida para auxiliar profissionais de saúde na análise de informações clínicas e na sugestão de diagnósticos potenciais com o apoio de inteligência artificial.

        O objetivo do app é fornecer insights diagnósticos **preliminares**, baseados nas informações inseridas e nas notas SOAP (Subjetivo, Objetivo, Avaliação, e Plano).

        Importante: Este aplicativo é experimental e deve ser usado como um suporte complementar.

        Desenvolvido por [Thiago Bellotto Rosa](https://www.linkedin.com/in/thiago-bellotto/)
        """
    )

## Define default values based on session state
default_data_nascimento = (
    datetime(year=1974, month=9, day=5)
    if st.session_state.use_default
    else datetime.today()
)
default_genero = "Feminino" if st.session_state.use_default else ""
default_problemas = (
    "Fadiga constante, ganho de peso sem mudanças na dieta, pele seca, queda de cabelo, intolerância ao frio, dores musculares e articulares frequentes, e constipação."
    if st.session_state.use_default
    else ""
)
default_alergias = "Não" if st.session_state.use_default else ""
default_medicacoes = (
    "Nenhuma medicação regular além de suplementos vitamínicos."
    if st.session_state.use_default
    else ""
)
default_historico_familiar = (
    "Mãe tem hipotireoidismo, pai tem diabetes tipo 2."
    if st.session_state.use_default
    else ""
)
default_habitos = (
    "Sedentária, trabalha em um escritório e passa a maior parte do dia sentada."
    if st.session_state.use_default
    else ""
)

## User Inputs
data_nascimento = st.date_input(
    "Data de Nascimento",
    value=default_data_nascimento,
    format="DD/MM/YYYY",
    max_value=datetime.today(),
)
genero = st.selectbox(
    "Gênero", ["Feminino", "Masculino"], index=0 if default_genero == "Feminino" else 1
)
problemas = st.text_area("Problemas Relatados", value=default_problemas, max_chars=300)
alergias = st.text_input("Alergias", value=default_alergias, max_chars=300)
medicacoes = st.text_input("Medicações em Uso", value=default_medicacoes, max_chars=300)
historico_familiar = st.text_input(
    "Histórico Familiar", value=default_historico_familiar, max_chars=300
)
habitos = st.text_area("Hábitos", value=default_habitos, max_chars=300)

## Button to toggle SOAP fields
st.checkbox("Mostrar Campos SOAP?", on_change=toggle_soap)

## Optional SOAP Fields
if st.session_state.show_soap:
    st.subheader("Informações SOAP (Opcional)")
    subjective = st.text_area(
        "Subjetivo (S) - Descrição dos sintomas relatados pelo paciente:",
        help="Inclua sintomas relatados pelo paciente, como dores, desconfortos, cansaço, e outras queixas subjetivas. Ex: Paciente relata dor de cabeça frequente e cansaço ao subir escadas.",
        max_chars=500,
    )
    objective = st.text_area(
        "Objetivo (O) - Observações clínicas e exames físicos realizados na consulta:",
        help="Registre sinais clínicos e achados observados pelo profissional de saúde, como febre, pressão arterial, resultados de exames físicos. Ex: Paciente apresenta palidez e pressão arterial levemente elevada.",
        max_chars=400,
    )
    assessment = st.text_area(
        "Avaliação (A) - Diagnóstico preliminar ou hipóteses diagnósticas:",
        help="Informe as hipóteses diagnósticas baseadas nos sintomas e sinais observados. Ex: Suspeita de hipertensão arterial devido aos sintomas relatados e observações clínicas.",
        max_chars=300,
    )
    plan = st.text_area(
        "Plano (P) - Tratamentos propostos, exames adicionais ou encaminhamentos:",
        help="Descreva os próximos passos, incluindo exames adicionais, tratamento inicial, ou recomendações para especialistas. Ex: Solicitar exame de sangue completo e iniciar tratamento com antihipertensivo.",
        max_chars=400,
    )
else:
    ## Set SOAP fields to empty if not used
    subjective = ""
    objective = ""
    assessment = ""
    plan = ""

## Create a dictionary with all the patient data
patient_data_dict = {
    "data_nascimento": str(data_nascimento),
    "genero": genero,
    "problemas": problemas,
    "alergias": alergias,
    "medicacoes": medicacoes,
    "historico_familiar": historico_familiar,
    "habitos": habitos,
    "subjective": subjective,
    "objective": objective,
    "assessment": assessment,
    "plan": plan,
}

## Convert the dictionary to a JSON string for storage
patient_data_json = json.dumps(patient_data_dict, ensure_ascii=False, indent=4)

if st.button("Obter Diagnóstico"):
    st.divider()
    with st.spinner("Consultando o diagnóstico..."):
        gpt_dict = get_diagnosis(client, patient_data_json, ASSISTANT_ID)
        st.write(gpt_dict["gpt_message"])
        sheet = authenticate_google_sheets(CREDS, EXCEL_NAME)
        save_to_google_sheet(sheet, gpt_dict)
