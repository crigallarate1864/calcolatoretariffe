import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="Calcolatore Tariffe CRI", layout="centered")

# Funzione per caricare i dati dall'Excel
@st.cache_data
def load_data():
    df = pd.read_excel("tariffario.xlsx")
    return df

try:
    df_tariffe = load_data()
except:
    st.error("Errore: Assicurati che il file 'tariffario.xlsx' sia presente.")
    st.stop()

st.title("🚑 Calcolatore Trasporti Secondari")
st.write("Inserisci i dati per generare il preventivo basato su D.G.R. XII / 437")

# --- INPUT UTENTE ---
with st.sidebar:
    st.header("Configurazione")
    mezzo = st.selectbox("Seleziona Mezzo", ["Ambulanza 2 Operatori", "Pulmino 2 Operatori", "Auto 1 operatore"])
    tipo_area = st.radio("Ambito", ["Grande Città (>150k ab.)", "Piccolo Comune (<150k ab.)"])
    servizio = st.radio("Servizio", ["Solo Andata", "Andata e Ritorno"])
    secondo_paziente = st.checkbox("2° Paziente (+16.66€)")
    attesa_minuti = st.number_input("Minuti di attesa totali", min_value=0, step=15)

# --- GESTIONE DESTINAZIONI MULTIPLE ---
st.subheader("Tragitto")
if 'tappe' not in st.session_state:
    st.session_state.tappe = [{"addr": "", "km": 0.0}]

def aggiungi_tappa():
    st.session_state.tappe.append({"addr": "", "km": 0.0})

def rimuovi_tappa():
    if len(st.session_state.tappe) > 1:
        st.session_state.tappe.pop()

for i, tappa in enumerate(st.session_state.tappe):
    c1, c2 = st.columns([3, 1])
    with c1:
        st.session_state.tappe[i]['addr'] = st.text_input(f"Indirizzo tappa {i+1}", value=tappa['addr'], key=f"a{i}")
    with c2:
        st.session_state.tappe[i]['km'] = st.number_input(f"KM parziali", value=tappa['km'], key=f"k{i}", min_value=0.0)

col_btns = st.columns(2)
with col_btns[0]:
    st.button("➕ Aggiungi tappa", on_click=aggiungi_tappa)
with col_btns[1]:
    st.button("🗑️ Rimuovi ultima", on_click=rimuovi_tappa)

# --- CALCOLO LOGICA ---
tot_km = sum(t['km'] for t in st.session_state.tappe)

# Estrazione tariffe dal DataFrame (Logica semplificata basata sul tuo file)
# Qui definiamo i valori base per l'esempio (che corrispondono al tuo Excel)
if mezzo == "Ambulanza 2 Operatori":
    fissa = 58.31 if tipo_area == "Grande Città (>150k ab.)" else 54.74
    km_rate = 1.13
    attesa_rate = 41.65
elif mezzo == "Pulmino 2 Operatori":
    fissa = 49.98
    km_rate = 0.95
    attesa_rate = 41.65
else: # Auto
    fissa = 28.56
    km_rate = 0.60
    attesa_rate = 20.23

# Calcolo supplemento attesa (1h inclusa per singola, 1.5h per A/R)
soglia = 90 if servizio == "Andata e Ritorno" else 60
minuti_extra = max(0, attesa_minuti - soglia)
ore_extra = -(-minuti_extra // 60) # Arrotondamento per eccesso

costo_base = fissa * (2 if servizio == "Andata e Ritorno" and tot_km == 0 else 1) # Logica semplificata
totale = fissa + (tot_km * km_rate) + (ore_extra * attesa_rate)
if secondo_paziente: totale += 16.66

st.divider()
st.metric("TOTALE PREVENTIVO", f"€ {totale:.2f}")
st.caption(f"Dettaglio: {tot_km} km totali | {ore_extra} ore attesa extra")