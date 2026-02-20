import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Magazzino SIE", page_icon="📦")

# --- CONNESSIONE ---
conn = st.connection("gsheets", type=GSheetsConnection)

# Funzione per caricare i dati e i nomi dei fogli
def load_all_data():
    # Carica l'anagrafica
    df_codes = conn.read(worksheet="DATABASE", ttl="1m")
    # Carica i preposti e magazzinieri
    df_config = conn.read(worksheet="CONFIG", ttl="1m")
    
    # Prende l'URL del foglio dai Secrets per recuperare i nomi dei fogli
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    
    # Questa riga recupera i nomi di tutti i fogli presenti nel file
    # Esclude DATABASE e CONFIG per mostrare solo i moduli (11A, 11B, ecc.)
    all_sheets = conn.client.open_by_url(url).worksheets()
    nami_fogli = [s.title for s in all_sheets if s.title not in ["DATABASE", "CONFIG", "Z_BACKUP_EXCEL"]]
    
    return df_codes, df_config, nami_fogli

df_codes, df_config, lista_moduli = load_all_data()

# --- LOGICA DI ACCESSO (PIN) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Accesso Magazzino SIE")
    pin_input = st.text_input("Inserisci il tuo PIN", type="password")
    
    if pin_input:
        df_config['PIN'] = df_config['PIN'].astype(str)
        user_row = df_config[df_config['PIN'] == pin_input]
        
        if not user_row.empty:
            st.session_state.authenticated = True
            st.session_state.user = user_row['MAGAZZINIERI'].values[0]
            st.rerun()
        else:
            st.error("PIN non riconosciuto.")
    st.stop()

# --- INTERFACCIA OPERATIVA ---
st.title(f"📦 Movimentazione")
st.write(f"Operatore: **{st.session_state.user}**")

with st.form("form_movimento", clear_on_submit=True):
    # QUI L'APP TI MOSTRA IN AUTOMATICO I FOGLI CHE TROVA
    modulo = st.selectbox("Destinazione / Modulo", lista_moduli)
    
    # Prende i preposti dalla Colonna C del foglio CONFIG
    lista_preposti = df_config['PREPOSTI'].dropna().tolist()
    preposto = st.selectbox("Richiesto da (Preposto)", lista_preposti)
    
    st.divider()
    
    barcode = st.text_input("Scansiona o digita Codice (Item/Matricola)")
    
    descrizione_display = ""
    if barcode:
        match = df_codes[df_codes['ITEM_CODE'].astype(str) == barcode]
        if not match.empty:
            descrizione_display = match['ITEM_DESC'].values[0]
            st.info(f"Articolo: **{descrizione_display}**")
        else:
            st.warning("⚠️ Codice non trovato. Inserisci descrizione manuale.")
            descrizione_display = st.text_input("Descrizione manuale")

    quantita = st.number_input("Quantità", min_value=1, step=1)
    note = st.text_input("Note")
    
    invio = st.form_submit_button("REGISTRA MOVIMENTO")

if invio:
    if descrizione_display == "":
        st.error("Manca la descrizione.")
    else:
        # Qui aggiungeremo il codice per scrivere nel foglio "INSERIMENTO TOT"
        st.success(f"Registrato con successo!")
        st.balloons()
