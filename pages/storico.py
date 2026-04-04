"""pages/storico.py"""
import streamlit as st
from utils.db import get_eventi, get_evento_ricette, get_evento_commensali, delete_evento
import datetime
import tempfile, os, io
import requests
from PIL import Image

ACCENT = "#f0a500"


def _build_pdf(ev, ev_id):
    """Genera il PDF del menu e restituisce i bytes."""
    from pdf_generator import create_menu_pdf

    # Ricette con dettagli
    ev_ricette = get_evento_ricette(ev_id)
    ricette_list = []
    for er in ev_ricette:
        info = er.get("comm_ricette") or {}
        ricette_list.append({
            "titolo":     info.get("titolo", "—"),
            "portata":    info.get("portata", ""),
            "ingredienti": info.get("ingredienti", ""),
            "manually_assigned_section": er.get("titolo_sezione", ""),
            "menu_note":  er.get("nota", ""),
        })

    # Commensali
    ev_comm = get_evento_commensali(ev_id)
    nomi_commensali = [
        c["comm_commensali"]["nome"]
        for c in ev_comm
        if c.get("comm_commensali")
    ]

    # Foto evento (nessuna nel cloud per ora, lista vuota)
    foto_paths = []

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    create_menu_pdf(
        evento=ev,
        ricette=ricette_list,
        commensali=nomi_commensali,
        foto_paths=foto_paths,
        output_path=tmp_path,
        doc_title=ev.get("descrizione", "Menu"),
        vini_text=ev.get("vini", ""),
    )

    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()
    os.unlink(tmp_path)
    return pdf_bytes


def show():
    uid = st.session_state["user_id"]
    st.markdown(
        f"<h2 style='color:#f0f4f8;border-left:4px solid {ACCENT};padding-left:12px;'>📖 Storico Eventi</h2>",
        unsafe_allow_html=True,
    )

    eventi = get_eventi(uid)
    if not eventi:
        st.info("Nessun evento registrato ancora.")
        return

    st.markdown(f"**{len(eventi)} eventi registrati**")

    for ev in eventi:
        data_str = ev.get("data", "")
        descr    = ev.get("descrizione", "Evento")
        luogo    = ev.get("luogo", "")
        try:
            data_fmt = datetime.date.fromisoformat(data_str).strftime("%d/%m/%Y")
        except Exception:
            data_fmt = data_str

        header = f"📅 {data_fmt} — {descr}"
        if luogo:
            header += f"  📍 {luogo}"

        with st.expander(header):
            # ── Ricette per sezione ─────────────────────────────
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

            # ── Commensali ──────────────────────────────────────
            commensali = get_evento_commensali(ev["id"])
            if commensali:
                nomi = [
                    c["comm_commensali"]["nome"]
                    for c in commensali
                    if c.get("comm_commensali")
                ]
                st.markdown(f"👥 **Commensali:** {', '.join(nomi)}")

            # ── Vini ────────────────────────────────────────────
            if ev.get("vini"):
                st.markdown(f"🍷 **Vini:** {ev['vini']}")

            st.divider()

            # ── Pulsanti ────────────────────────────────────────
            col_pdf, col_del = st.columns([3, 1])

            with col_pdf:
                if st.button("📄 Genera PDF Menu", key=f"pdf_ev_{ev['id']}", use_container_width=True):
                    with st.spinner("Generazione PDF..."):
                        try:
                            pdf_bytes = _build_pdf(ev, ev["id"])
                            fname = f"menu_{descr.replace(' ', '_')[:30]}.pdf"
                            st.download_button(
                                label="⬇️ Scarica PDF",
                                data=pdf_bytes,
                                file_name=fname,
                                mime="application/pdf",
                                key=f"dl_pdf_{ev['id']}",
                                use_container_width=True,
                            )
                        except Exception as e:
                            st.error(f"Errore generazione PDF: {e}")

            with col_del:
                if st.button("🗑️ Elimina", key=f"del_ev_{ev['id']}", use_container_width=True):
                    delete_evento(ev["id"])
                    st.rerun()
