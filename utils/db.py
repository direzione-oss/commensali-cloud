"""
utils/db.py — Client Supabase per Commensali Cloud
"""
import streamlit as st
from supabase import create_client, Client

_SB_URL  = "https://ygaoxoohlfhxbjrcfbjf.supabase.co"
_SB_ANON = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
             ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnYW94b29obGZoeGJqcmNmYmpmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUyNjI3MTAsImV4cCI6MjA5MDgzODcxMH0"
             ".JB8y7XDTysGBYbXQISApkw3NA2lju5ZtF83SbX2w1UY")

BUCKET = "immagini di commensali"


@st.cache_resource
def get_supabase() -> Client:
    try:
        url = st.secrets.get("SUPABASE_URL", _SB_URL) or _SB_URL
        key = st.secrets.get("SUPABASE_KEY", _SB_ANON) or _SB_ANON
    except Exception:
        url, key = _SB_URL, _SB_ANON
    return create_client(url, key)


# ── Storage ───────────────────────────────────────────────────────────────────

def upload_image(file_bytes: bytes, filename: str, folder: str = "ricette") -> str:
    sb = get_supabase()
    path = f"{folder}/{filename}"
    try:
        sb.storage.from_(BUCKET).remove([path])
    except Exception:
        pass
    sb.storage.from_(BUCKET).upload(
        path, file_bytes, file_options={"content-type": "image/jpeg", "upsert": "true"}
    )
    return sb.storage.from_(BUCKET).get_public_url(path)


# ── Ricette ───────────────────────────────────────────────────────────────────

def get_ricette(user_id: str) -> list[dict]:
    sb = get_supabase()
    return sb.table("comm_ricette").select("*").eq("user_id", user_id).order("titolo").execute().data or []


def get_ricetta(ricetta_id: int) -> dict:
    sb = get_supabase()
    r = sb.table("comm_ricette").select("*").eq("id", ricetta_id).execute()
    return r.data[0] if r.data else {}


def insert_ricetta(user_id: str, data: dict) -> dict:
    sb = get_supabase()
    data["user_id"] = user_id
    r = sb.table("comm_ricette").insert(data).execute()
    return r.data[0] if r.data else {}


def update_ricetta(ricetta_id: int, data: dict) -> dict:
    sb = get_supabase()
    r = sb.table("comm_ricette").update(data).eq("id", ricetta_id).execute()
    return r.data[0] if r.data else {}


def delete_ricetta(ricetta_id: int):
    sb = get_supabase()
    sb.table("comm_ricette").delete().eq("id", ricetta_id).execute()


# ── Commensali ────────────────────────────────────────────────────────────────

def get_commensali(user_id: str) -> list[dict]:
    sb = get_supabase()
    return sb.table("comm_commensali").select("*").eq("user_id", user_id).order("nome").execute().data or []


def insert_commensale(user_id: str, nome: str) -> dict:
    sb = get_supabase()
    r = sb.table("comm_commensali").insert({"user_id": user_id, "nome": nome}).execute()
    return r.data[0] if r.data else {}


def delete_commensale(commensale_id: int):
    sb = get_supabase()
    sb.table("comm_commensali").delete().eq("id", commensale_id).execute()


# ── Eventi ────────────────────────────────────────────────────────────────────

def get_eventi(user_id: str) -> list[dict]:
    sb = get_supabase()
    return sb.table("comm_eventi").select("*").eq("user_id", user_id).order("data", desc=True).execute().data or []


def get_evento(evento_id: int) -> dict:
    sb = get_supabase()
    r = sb.table("comm_eventi").select("*").eq("id", evento_id).execute()
    return r.data[0] if r.data else {}


def insert_evento(user_id: str, data: dict) -> dict:
    sb = get_supabase()
    data["user_id"] = user_id
    r = sb.table("comm_eventi").insert(data).execute()
    return r.data[0] if r.data else {}


def update_evento(evento_id: int, data: dict) -> dict:
    sb = get_supabase()
    r = sb.table("comm_eventi").update(data).eq("id", evento_id).execute()
    return r.data[0] if r.data else {}


def delete_evento(evento_id: int):
    sb = get_supabase()
    sb.table("comm_eventi_ricette").delete().eq("evento_id", evento_id).execute()
    sb.table("comm_eventi_commensali").delete().eq("evento_id", evento_id).execute()
    sb.table("comm_eventi_foto").delete().eq("evento_id", evento_id).execute()
    sb.table("comm_eventi").delete().eq("id", evento_id).execute()


def get_evento_ricette(evento_id: int) -> list[dict]:
    sb = get_supabase()
    return sb.table("comm_eventi_ricette").select("*, comm_ricette(titolo, portata)").eq("evento_id", evento_id).order("ordine").execute().data or []


def get_evento_commensali(evento_id: int) -> list[dict]:
    sb = get_supabase()
    return sb.table("comm_eventi_commensali").select("*, comm_commensali(nome)").eq("evento_id", evento_id).execute().data or []


def add_ricetta_to_evento(evento_id: int, ricetta_id: int, sezione: str = "", nota: str = "", ordine: int = 0):
    sb = get_supabase()
    sb.table("comm_eventi_ricette").insert({
        "evento_id": evento_id,
        "ricetta_id": ricetta_id,
        "titolo_sezione": sezione,
        "nota": nota,
        "ordine": ordine,
    }).execute()


def add_commensale_to_evento(evento_id: int, commensale_id: int):
    sb = get_supabase()
    try:
        sb.table("comm_eventi_commensali").insert({
            "evento_id": evento_id,
            "commensale_id": commensale_id,
        }).execute()
    except Exception:
        pass  # già presente


def get_ricetta_last_dates(user_id: str, ricetta_id: int) -> list[dict]:
    """Ultime date in cui la ricetta è stata servita."""
    sb = get_supabase()
    rows = (sb.table("comm_eventi_ricette")
              .select("evento_id, comm_eventi(data, descrizione)")
              .eq("ricetta_id", ricetta_id)
              .execute().data or [])
    risultati = []
    for r in rows:
        ev = r.get("comm_eventi") or {}
        if ev.get("data"):
            risultati.append({
                "data": ev["data"],
                "descrizione": ev.get("descrizione", ""),
            })
    risultati.sort(key=lambda x: x["data"], reverse=True)
    return risultati[:5]


# ── Admin ─────────────────────────────────────────────────────────────────────

def get_all_users() -> list[dict]:
    sb = get_supabase()
    return sb.table("comm_utenti").select("id, nome, email, ruolo, created_at").order("created_at", desc=True).execute().data or []


def set_user_role(user_id: str, ruolo: str):
    sb = get_supabase()
    sb.table("comm_utenti").update({"ruolo": ruolo}).eq("id", user_id).execute()


def delete_user(user_id: str):
    sb = get_supabase()
    sb.table("comm_utenti").delete().eq("id", user_id).execute()
