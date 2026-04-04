"""pages/nuovo_evento.py"""
import streamlit as st
from utils.db import (
    get_ricette, get_commensali, insert_evento,
    add_ricetta_to_evento, add_commensale_to_evento
)
import datetime

SEZIONI = ["Antipasti", "Primi", "Zuppe", "Secondi Carne", "Secondi Pesce", "Contorni", "Dolci", "Lievitati"]
ACCENT  = "#f0a500"


def show():
    uid = st.session_state["user_id"]
    st.markdown(f"<h2 style='color:#f0f4f8;border-left:4px solid {ACCENT};padding-left:12px;'>📅 Nuovo Evento</h2>", unsafe_allow_html=True)

    ricette     = get_ricette(uid)
    commensali  = get_commensali(uid)

    if not ricette:
        st.warning("Aggiungi prima almeno una ricetta nel Ricettario.")
        return

    with st.form("nuovo_evento_form"):
        c1, c2 = st.columns(2)
        with c1:
            data        = st.date_input("📅 Data", value=datetime.date.today())
            descrizione = st.text_input("📝 Descrizione", placeholder="es. Cena domenicale")
        with c2:
            luogo = st.text_input("📍 Luogo", placeholder="es. Casa mia")
            vini  = st.text_area("🍷 Vini", height=80, placeholder="Note sui vini")

        st.divider()
        st.markdown("**Menu — scegli le ricette per sezione:**")

        menu_selezionato = {}
        for sezione in SEZIONI:
            ricette_sez = st.multiselect(
                sezione,
                options=[r["titolo"] for r in ricette],
                key=f"sez_{sezione}"
            )
            if ricette_sez:
                menu_selezionato[sezione] = ricette_sez

        st.divider()
        if commensali:
            sel_commensali = st.multiselect(
                "👥 Commensali presenti",
                options=[c["nome"] for c in commensali],
                key="sel_commensali"
            )
        else:
            sel_commensali = []
            st.info("Nessun commensale ancora, l'evento verrà salvato senza.")

        submit = st.form_submit_button("💾 Salva Evento", use_container_width=True)

    if submit:
        if not descrizione:
            st.error("Inserisci una descrizione per l'evento.")
            return

        evento = insert_evento(uid, {
            "data": str(data),
            "descrizione": descrizione,
            "luogo": luogo,
            "vini": vini,
        })
        ev_id = evento["id"]

        # Aggiungi ricette
        ordine = 0
        titolo_map = {r["titolo"]: r["id"] for r in ricette}
        for sezione, titoli in menu_selezionato.items():
            for titolo in titoli:
                rid = titolo_map.get(titolo)
                if rid:
                    add_ricetta_to_evento(ev_id, rid, sezione=sezione, ordine=ordine)
                    ordine += 1

        # Aggiungi commensali
        nome_map = {c["nome"]: c["id"] for c in commensali}
        for nome in sel_commensali:
            cid = nome_map.get(nome)
            if cid:
                add_commensale_to_evento(ev_id, cid)

        st.success(f"✅ Evento '{descrizione}' salvato con {ordine} piatti!")
        st.balloons()
