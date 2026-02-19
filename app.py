import streamlit as st
import requests
import json
from datetime import datetime

# RECUPERO L'URL DALLA CASSAFORTE DI STREAMLIT
WEBHOOK_URL = st.secrets["google_bridge_url"]

st.set_page_config(page_title="SIE - Magazzino", page_icon="???")

# Stile scuro e rosso come richiesto
st.markdown("<style>.main { background-color: #000000; color: #FF0000; }</style>", unsafe_allow_html=True)

st.title("??? INGRESSO MERCE SIE")

with st.form("form_ingresso", clear_on_submit=True):
    progetto = st.text_input("Progetto/Modello (es. 11A)")
    codice = st.text_input("ITEM_CODE (Scansiona)")
    qty = st.number_input("Quantità", min_value=1)
    nota = st.text_area("Note")
    submit = st.form_submit_button("REGISTRA")

if submit:
    payload = {"values": [progetto, codice, "", qty, "", datetime.now().strftime("%d/%m/%Y"), "DA ELABORARE", "", "", "", nota]}
    r = requests.post(WEBHOOK_URL, data=json.dumps(payload))
    if r.status_code == 200:
        st.success("Registrato con successo!")
        st.balloons()