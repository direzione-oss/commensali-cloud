"""pages/storico.py"""
import streamlit as st
from utils.db import get_eventi, get_evento_ricette, get_evento_commensali, delete_evento
import datetime

ACCENT = "#f0a500"


def show():
    uid = st.session_state["user_id"]
    st.markdown(f"<h2 style='color:#f0f4f8;border-left:4px solid {ACCENT};padding-left:12px;'>📖 Storico Eventi</h2>", unsafe_allow_html=True)

    eventi = get_eventi(uid)
    if not eventi:
        st.info("Nessun evento registrato ancora.")
        return

    st.markdown(f"**{len(eventi)} eventi registrati**")

    for ev in eventi:
        data_str   = ev.get("data", "")
        descr      = ev.get("descrizione", "Evento")
        luogo      = ev.get("luogo", "")
        try:
            data_fmt = datetime.date.fromisoformat(data_str).strftime("%d/%m/%Y")
        except Exception:
            data_fmt = data_str

        header = f"📅 {data_fmt} — {descr}"
        if luogo:
            header += f"  📍 {luogo}"

        with st.expander(header):
            # Ricette
            ricette = get_evento_ricette(ev["id"])
            if ricette:
                sezioni = {}
                for r in ricette:
                    sez = r.get("titolo_sezione") or "Altro"
                    sezioni.setdefault(sez, []).append(r)
                for sez, items in sezioni.items():
                    st.markdown(f"**{sez}**")
                    for item in items:
                        nome_ric = (item.get("comm_ricette") or {}).get("titolo", "—")
                        nota = item.get("nota", "")
                        riga = f"- {nome_ric}"
                        if nota:
                            riga += f" *(nota: {nota})*"
                        st.markdown(riga)

            # Commensali
            commensali = get_evento_commensali(ev["id"])
            if commensali:
                nomi = [c["comm_commensali"]["nome"] for c in commensali if c.get("comm_commensali")]
                st.markdown(f"👥 **Commensali:** {', '.join(nomi)}")

            # Vini
            if ev.get("vini"):
                st.markdown(f"🍷 **Vini:** {ev['vini']}")

            # Elimina
            if st.button("🗑️ Elimina evento", key=f"del_ev_{ev['id']}"):
                delete_evento(ev["id"])
                st.rerun()
