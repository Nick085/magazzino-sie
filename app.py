import streamlit as st
import requests
import json
from datetime import datetime

# RECUPERO L'URL DALLA CASSAFORTE DI STREAMLIT
WEBHOOK_URL = st.secrets["google_bridge_url"]

# Configurazione Pagina
st.set_page_config(page_title="SIE - Magazzino", page_icon="🏗️")

# Stile: Sfondo Nero, Testo Rosso
st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1, h2, h3, p, label { color: #FF0000 !important; }
    .stButton>button { background-color: #FF0000; color: white; border: none; }
    .stTextInput>div>div>input { background-color: #1a1a1a; color: white; border: 1px solid #FF0000; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ INGRESSO MERCE SIE")
st.subheader("Modulo di Registrazione Rapida")

with st.form("form_ingresso", clear_on_submit=True):
    progetto = st.text_input("Progetto / Modulo (es. 11A, 0506175)")
    codice = st.text_input("ITEM_CODE (Scansiona Barcode)")
    mo = st.text_input("Numero MO / DDT")
    qty = st.number_input("Quantità Ricevuta", min_value=1, step=1)
    nota = st.text_area("Note (es. Collo danneggiato)")
    
    submit = st.form_submit_button("CONFERMA E REGISTRA")

if submit:
    if progetto and codice:
        # Prepariamo i dati per il foglio INSERIMENTO_DATI
        payload = {
            "values": [
                progetto,           # Colonna A
                codice,             # Colonna B
                mo,                 # Colonna C
                qty,                # Colonna D
                "",                 # Colonna E (Data emissione)
                datetime.now().strftime("%d/%m/%Y"), # Colonna F (Data handoff)
                "DA ELABORARE",     # Colonna G (Esito)
                "", "", "",         # Colonne H, I, J
                nota                # Colonna K (Note)
            ]
        }
        
        try:
            r = requests.post(WEBHOOK_URL, data=json.dumps(payload))
            if r.status_code == 200:
                st.success(f"✅ REGISTRATO: {qty} pezzi di {codice}")
                st.balloons()
            else:
                st.error("Errore di connessione col server Google.")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
    else:
        st.warning("⚠️ Inserisci almeno Progetto e Codice Articolo!")
