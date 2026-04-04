"""
setup_admin.py — Crea l'account admin su Supabase
Eseguire una sola volta: python setup_admin.py
"""
import hashlib
from supabase import create_client

SB_URL  = "https://ygaoxoohlfhxbjrcfbjf.supabase.co"
SB_KEY  = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnYW94b29obGZoeGJqcmNmYmpmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUyNjI3MTAsImV4cCI6MjA5MDgzODcxMH0"
            ".JB8y7XDTysGBYbXQISApkw3NA2lju5ZtF83SbX2w1UY")

ADMIN_EMAIL = "direzione@serrastudio.it"
ADMIN_NOME  = "Serra Admin"
ADMIN_PW    = input("Inserisci la password admin: ")

sb = create_client(SB_URL, SB_KEY)

pw_hash = hashlib.sha256(ADMIN_PW.encode()).hexdigest()

existing = sb.table("comm_utenti").select("id").eq("email", ADMIN_EMAIL).execute()

if existing.data:
    sb.table("comm_utenti").update({
        "password_hash": pw_hash,
        "ruolo": "admin",
        "nome": ADMIN_NOME,
    }).eq("email", ADMIN_EMAIL).execute()
    print(f"✅ Admin aggiornato: {ADMIN_EMAIL}")
else:
    sb.table("comm_utenti").insert({
        "nome": ADMIN_NOME,
        "email": ADMIN_EMAIL,
        "password_hash": pw_hash,
        "ruolo": "admin",
    }).execute()
    print(f"✅ Admin creato: {ADMIN_EMAIL}")
