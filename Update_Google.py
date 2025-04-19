#aula base
#https://www.youtube.com/watch?v=l7pL_Y3fw-o&t=1812s

#Docs
#ctrl+/ = comenta e descomenta
#https://developers.google.com/sheets/api/guides/values?hl=pt-br
#https://awari.com.br/python-como-deletar-um-arquivo/?utm_source=blog&utm_campaign=projeto+blog&utm_medium=Python:%20Como%20Deletar%20um%20Arquivo - remover itens com python

#1° google cloud developer
#2° Novo Projeto
#3° pesquisar google drive api / pesquisar google sheets api - ativar ambas Apis
#4° gerar token de autenticação
#5° menu navegação, apis e serviços e apis e servicos ativados
#6 tela de permissão oAuth
#7 interno ou externo
#8 nome do app (sheets_integrado) e afins
#9 escopo = nivel de acesso (somente ler? somente editar? ambos?)
#10 credenciais (gerar credencial)
#11 id de cliente Oauth - create credencial - id do cliente
#12 marcar tipo de app (app para computador) / nomear e criar
#13 guardar as credenciais assim como o json (baixar na seta de download)
#14 mudar nome do arquivo baixado para credentials.json (ou o que quiser)
#15 colocar ele no mesmo local onde vou rodar o codigo em python
#16 https://developers.google.com/sheets/api/quickstart/python?hl=pt-br


#plan
"https://docs.google.com/spreadsheets/d/1nMDOfJ5vd6fhAqT-vxlAIKMqmbypOhEs6RS2qjduqyE/edit?gid=0#gid=0"
# -------------------- Imports --------------------
import streamlit as st
import time
import pandas as pd
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import plotly.express as px
import matplotlib.pyplot as plt
import json

# -------------------- Parâmetros --------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1nMDOfJ5vd6fhAqT-vxlAIKMqmbypOhEs6RS2qjduqyE"
RANGE_NAME = "Vendas!A:B"

#listas pra df
df_apuracao = []
df_desc = []
ajuste_valor = []
ajuste_desc = []

#setando parametros
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

refresh_interval = 10
# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1nMDOfJ5vd6fhAqT-vxlAIKMqmbypOhEs6RS2qjduqyE"
SAMPLE_RANGE_NAME = f"Vendas!A:B"

@st.cache_resource
def get_credentials():
    creds = None
    # Usa o conteúdo do secrets
    google_creds = json.loads(st.secrets["GOOGLE_CREDS"])

    # Salva temporariamente como um arquivo
    with open("credentials_temp.json", "w") as f:
        json.dump(google_creds, f)

    flow = InstalledAppFlow.from_client_secrets_file("credentials_temp.json", SCOPES)
    creds = flow.run_local_server(port=0)

    return creds

def read_google_sheets():
    try:
        creds = get_credentials()
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=SAMPLE_RANGE_NAME
        ).execute()

        values = result.get("values", [])
        if not values:
            return pd.DataFrame()

        df = pd.DataFrame(values[1:], columns=values[0])
        df["Data"] = pd.to_datetime(df["Data"])
        df["Vendas"] = pd.to_numeric(df["Vendas"], errors="coerce")
        return df

    except HttpError as err:
        st.error(f"Erro ao acessar Google Sheets: {err}")
        return pd.DataFrame()

def teste():
    read_google_sheets()
    time.sleep(3)
    df_venda = pd.read_excel('apurado.xlsx')
    df_venda.info()
    # Obtendo a data de hoje sem horário
    hoje = pd.Timestamp.today().normalize()
    df_venda['Data'] = pd.to_datetime(df_venda['Data'])
    df_venda.info()
    df_hoje = df_venda[df_venda['Data'] == hoje]
    print(df_hoje)
    #print(f"O total de vendas até o momento é: {df_hoje['Vendas'].sum():.2f}")

def streaming():
    read_google_sheets()
    time.sleep(3)
    df_venda = pd.read_excel('apurado.xlsx')
    # Obtendo a data de hoje sem horário
    hoje = pd.Timestamp.today().normalize()
    df_venda['Data'] = pd.to_datetime(df_venda['Data'])
    df_hoje = df_venda[df_venda['Data'] == hoje]
    st.title("Atualização Automática da Página")

    # Exemplo de conteúdo dinâmico
    st.write("A página será atualizada automaticamente a cada 10 segundos.")
    st.write(f"A hora atual é: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.write(f"O total de vendas até o momento é: {df_hoje['Vendas'].sum():.2f}")

    df_agrupado = df_venda.groupby("Data", as_index=False)["Vendas"].sum()


    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(df_agrupado["Data"].dt.strftime('%d/%m/%Y'), df_agrupado["Vendas"], color='skyblue')
    ax.set_title("Vendas Diárias", fontsize=16)
    ax.set_xlabel("Data")
    ax.set_ylabel("Vendas")

    for bar in bars:
        yval = bar.get_height()  # Obtém o valor da barra (altura)
        ax.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:,.0f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold', color='black')

    plt.xticks(rotation=45)

    # Exibir no Streamlit
    st.pyplot(fig)

    countdown = st.empty()
    for i in range(refresh_interval, 0, -1):
        countdown.info(f"🔄 Atualizando em {i} segundos...")
        time.sleep(1)

    # Espera pelo intervalo de atualização
    time.sleep(refresh_interval)

    # Inicializa session_state
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = time.time()

    # Força a atualização após o tempo definido
    if time.time() - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = time.time()
        st.experimental_rerun()


streaming()

