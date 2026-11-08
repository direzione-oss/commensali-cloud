"""
utils/db.py — Persistenza SQLite Locale + Immagini per Commensali (VPS)
"""
import os
import uuid
import sqlite3
import datetime
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "storage"))
IMAGES_DIR = os.path.join(DATA_DIR, "images")
DB_PATH = os.path.join(DATA_DIR, "commensali.db")
STATIC_DIR = os.path.join(BASE_DIR, "static")

ADMIN_USER_ID = "admin-serrastudio-0001"
ADMIN_EMAIL = "direzione@serrastudio.it"


def _ensure_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(IMAGES_DIR, "ricette"), exist_ok=True)
    if not os.path.exists(STATIC_DIR):
        try:
            os.symlink(IMAGES_DIR, STATIC_DIR, target_is_directory=True)
        except Exception:
            pass


def _get_conn() -> sqlite3.Connection:
    _ensure_storage()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


INITIAL_RICETTE = [
    (2, "Verdure pastellate", "", "Antipasti", "", "", ""),
    (3, "Degustazione di salumi e formaggi della tradizione", "", "Antipasti", "", "", ""),
    (4, "Focaccia artigianale al rosmarino", "", "Antipasti", "", "", ""),
    (7, "Torta rustica ricotta e spinaci", "", "Antipasti", "", "", ""),
    (10, "Verdure dell'orto grigliate", "", "Antipasti", "", "", ""),
    (11, "Lasagne alla Bolognese", "", "Primi", "", "", ""),
    (12, "Punta di petto di manzo al bbq (Brisket)", "", "Secondi Carne", "", "", ""),
    (13, "Patate novelle al forno con erbe aromatiche", "", "Contorni", "", "", ""),
    (14, "Insalata fresca d'inverno con finocchi e arance", "", "Contorni", "", "", ""),
    (15, "Crostata casereccia alla frutta", "", "Dolci", "", "", ""),
    (16, "Crostata casereccia alla frutta (variante)", "", "Dolci", "", "", ""),
    (17, "Gelato alla crema di vaniglia", "", "Dolci", "", "", ""),
    (18, "Caffè e liquori", "", "Dolci", "", "", ""),
    (
        21,
        "Pizza istantanea",
        "/app/static/ricette/pizza_istantanea.jpg",
        "Lievitati",
        "400 gr farina 00\n140 ml acqua\n10 gr zucchero\n5 gr sale\n3 cucchiai di olio evo\n1 busta di lievito istantaneo PaneAngeli\npassata di pomodoro\nmozzarella\norigano",
        "tutto in un contenitore\nmescola \nstendi in una teglia con carta da forno\n200 gr in forno per 20 minuti",
        "FOCACCIA DOLCE: al posto dell'olio il burro\nsale un pizzico\n100 gr di zucchero (spolverato anche sopra)",
    ),
]

INITIAL_COMMENSALI = [
    (1, "Nicola Mazzocato"),
    (2, "Tommaso Mazzocato"),
    (3, "Giulia Mazzocato"),
    (4, "Elisa Viviani"),
    (5, "Raffaella Viviani"),
    (6, "Gian Carlo Serra"),
    (7, "Liliana Famoso"),
    (8, "Willy Serra"),
    (9, "Ita Beltrame"),
    (10, "Ger Beltrame"),
    (11, "Italo Viviani"),
    (12, "Anna Serra"),
    (13, "Fabio Orlando"),
    (14, "Enrico Bona"),
    (15, "Edoardo Bona"),
]

INITIAL_EVENTI_RICETTE = [
    (4, 3, "IL BENVENUTO", "", 0),
    (4, 4, "IL BENVENUTO", "", 1),
    (4, 7, "IL BENVENUTO", "", 2),
    (4, 10, "IL BENVENUTO", "", 3),
    (4, 11, "LA TRADIZIONE", "", 4),
    (4, 12, "DAL FUOCO LENTO", "", 5),
    (4, 13, "DAL FUOCO LENTO", "", 6),
    (4, 14, "DAL FUOCO LENTO", "", 7),
    (4, 16, "IL GRAN FINALE", "", 8),
    (4, 17, "IL GRAN FINALE", "", 9),
    (4, 18, "I SALUTI", "", 10),
]


def _init_db():
    with _get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS comm_utenti (
            id TEXT PRIMARY KEY,
            nome TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            ruolo TEXT DEFAULT 'utente',
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS comm_ricette (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            titolo TEXT NOT NULL,
            foto_url TEXT DEFAULT '',
            portata TEXT DEFAULT '',
            ingredienti TEXT DEFAULT '',
            procedimento TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS comm_commensali (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS comm_eventi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            data TEXT NOT NULL,
            descrizione TEXT DEFAULT '',
            luogo TEXT DEFAULT '',
            vini TEXT DEFAULT '',
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS comm_eventi_ricette (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento_id INTEGER NOT NULL,
            ricetta_id INTEGER,
            titolo_sezione TEXT DEFAULT '',
            nota TEXT DEFAULT '',
            ordine INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS comm_eventi_commensali (
            evento_id INTEGER NOT NULL,
            commensale_id INTEGER NOT NULL,
            PRIMARY KEY (evento_id, commensale_id)
        );

        CREATE TABLE IF NOT EXISTS comm_eventi_foto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            foto_url TEXT NOT NULL,
            created_at TEXT
        );
        """)

        cur = conn.execute("SELECT COUNT(*) FROM comm_utenti")
        if cur.fetchone()[0] == 0:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            # Default admin hash (supporta sia la password di SpiceMaster/CantinaPro sia eventuale cambio)
            conn.execute("""
                INSERT INTO comm_utenti (id, nome, email, password_hash, ruolo, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ADMIN_USER_ID,
                "Gian Carlo Serra",
                ADMIN_EMAIL,
                "$2b$12$vs6G2NNZtNIyMOS1LaZWn.cVg0DnJF78bEgvqvJ7GH9oskSZ1iJYm",
                "admin",
                now,
            ))

            for rid, titolo, foto_url, portata, ing, proc, note in INITIAL_RICETTE:
                conn.execute("""
                    INSERT OR IGNORE INTO comm_ricette (id, user_id, titolo, foto_url, portata, ingredienti, procedimento, note, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (rid, ADMIN_USER_ID, titolo, foto_url, portata, ing, proc, note, now))

            for cid, nome in INITIAL_COMMENSALI:
                conn.execute("""
                    INSERT OR IGNORE INTO comm_commensali (id, user_id, nome)
                    VALUES (?, ?, ?)
                """, (cid, ADMIN_USER_ID, nome))

            conn.execute("""
                INSERT OR IGNORE INTO comm_eventi (id, user_id, data, descrizione, luogo, vini, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                4,
                ADMIN_USER_ID,
                "2026-03-01",
                "90esimo di Zio Italo",
                "Montebelluna (TV), casa di Nicola ed Elisa",
                "Prosecco\nValpolicella Ripasso\nMoscato",
                now,
            ))

            for ev_id, ric_id, sez, nota, ordine in INITIAL_EVENTI_RICETTE:
                conn.execute("""
                    INSERT INTO comm_eventi_ricette (evento_id, ricetta_id, titolo_sezione, nota, ordine)
                    VALUES (?, ?, ?, ?, ?)
                """, (ev_id, ric_id, sez, nota, ordine))

            for cid, _ in INITIAL_COMMENSALI:
                conn.execute("""
                    INSERT OR IGNORE INTO comm_eventi_commensali (evento_id, commensale_id)
                    VALUES (4, ?)
                """, (cid,))

            conn.commit()


_init_db()


# ── Query Builder compatibile per get_supabase().table(...) ──────────────────

class _ExecResult:
    def __init__(self, data, count=None):
        self.data = data
        self.count = count if count is not None else len(data)


class _SqliteQueryBuilder:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._op = "select"
        self._cols = "*"
        self._count = None
        self._filters = []
        self._order = None
        self._payload = None

    def select(self, cols="*", count=None):
        self._op = "select"
        self._cols = cols
        self._count = count
        return self

    def insert(self, payload: dict):
        self._op = "insert"
        self._payload = dict(payload)
        return self

    def update(self, payload: dict):
        self._op = "update"
        self._payload = dict(payload)
        return self

    def delete(self):
        self._op = "delete"
        return self

    def eq(self, col: str, val):
        self._filters.append((col, val))
        return self

    def order(self, col: str, desc: bool = False):
        self._order = (col, desc)
        return self

    def execute(self) -> _ExecResult:
        where_sql = ""
        params = []
        if self._filters:
            where_sql = " WHERE " + " AND ".join(f"{c} = ?" for c, _ in self._filters)
            params = [v for _, v in self._filters]

        with _get_conn() as conn:
            if self._op == "select":
                order_sql = ""
                if self._order:
                    order_sql = f" ORDER BY {self._order[0]} {'DESC' if self._order[1] else 'ASC'}"
                rows = conn.execute(f"SELECT * FROM {self.table_name}{where_sql}{order_sql}", params).fetchall()
                data = [dict(r) for r in rows]
                return _ExecResult(data, len(data))

            if self._op == "insert":
                p = dict(self._payload)
                if self.table_name == "comm_utenti":
                    p.setdefault("id", str(uuid.uuid4()))
                    p.setdefault("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
                cols = ", ".join(p.keys())
                placeholders = ", ".join("?" for _ in p)
                cur = conn.execute(f"INSERT INTO {self.table_name} ({cols}) VALUES ({placeholders})", list(p.values()))
                conn.commit()
                if "id" in p:
                    row = conn.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (p["id"],)).fetchone()
                else:
                    row = conn.execute(f"SELECT * FROM {self.table_name} WHERE rowid = ?", (cur.lastrowid,)).fetchone()
                return _ExecResult([dict(row)] if row else [p])

            if self._op == "update":
                p = dict(self._payload)
                set_sql = ", ".join(f"{k} = ?" for k in p.keys())
                conn.execute(f"UPDATE {self.table_name} SET {set_sql}{where_sql}", list(p.values()) + params)
                conn.commit()
                rows = conn.execute(f"SELECT * FROM {self.table_name}{where_sql}", params).fetchall()
                return _ExecResult([dict(r) for r in rows])

            if self._op == "delete":
                conn.execute(f"DELETE FROM {self.table_name}{where_sql}", params)
                conn.commit()
                return _ExecResult([])


class _LocalSupabaseMock:
    def table(self, name: str) -> _SqliteQueryBuilder:
        return _SqliteQueryBuilder(name)


def get_supabase() -> _LocalSupabaseMock:
    return _LocalSupabaseMock()


# ── Storage ───────────────────────────────────────────────────────────────────

def upload_image(file_bytes: bytes, filename: str, folder: str = "ricette") -> str:
    _ensure_storage()
    target_dir = os.path.join(IMAGES_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return f"/app/static/{folder}/{filename}"


# ── Ricette ───────────────────────────────────────────────────────────────────

def get_ricette(user_id: str) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM comm_ricette WHERE user_id = ? ORDER BY titolo",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_ricetta(ricetta_id: int) -> dict:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM comm_ricette WHERE id = ?", (ricetta_id,)).fetchone()
        return dict(row) if row else {}


def insert_ricetta(user_id: str, data: dict) -> dict:
    payload = dict(data)
    payload["user_id"] = user_id
    payload.setdefault("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
    cols = ", ".join(payload.keys())
    placeholders = ", ".join("?" for _ in payload)
    with _get_conn() as conn:
        cur = conn.execute(f"INSERT INTO comm_ricette ({cols}) VALUES ({placeholders})", list(payload.values()))
        conn.commit()
        return get_ricetta(cur.lastrowid)


def update_ricetta(ricetta_id: int, data: dict) -> dict:
    payload = dict(data)
    if not payload:
        return get_ricetta(ricetta_id)
    set_sql = ", ".join(f"{k} = ?" for k in payload.keys())
    with _get_conn() as conn:
        conn.execute(f"UPDATE comm_ricette SET {set_sql} WHERE id = ?", list(payload.values()) + [ricetta_id])
        conn.commit()
        return get_ricetta(ricetta_id)


def delete_ricetta(ricetta_id: int):
    with _get_conn() as conn:
        conn.execute("DELETE FROM comm_ricette WHERE id = ?", (ricetta_id,))
        conn.commit()


# ── Commensali ────────────────────────────────────────────────────────────────

def get_commensali(user_id: str) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM comm_commensali WHERE user_id = ? ORDER BY nome",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def insert_commensale(user_id: str, nome: str) -> dict:
    with _get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO comm_commensali (user_id, nome) VALUES (?, ?)",
            (user_id, nome)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM comm_commensali WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row) if row else {}


def delete_commensale(commensale_id: int):
    with _get_conn() as conn:
        conn.execute("DELETE FROM comm_commensali WHERE id = ?", (commensale_id,))
        conn.commit()


# ── Eventi ────────────────────────────────────────────────────────────────────

def get_eventi(user_id: str) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM comm_eventi WHERE user_id = ? ORDER BY data DESC",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_evento(evento_id: int) -> dict:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM comm_eventi WHERE id = ?", (evento_id,)).fetchone()
        return dict(row) if row else {}


def insert_evento(user_id: str, data: dict) -> dict:
    payload = dict(data)
    payload["user_id"] = user_id
    payload.setdefault("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
    cols = ", ".join(payload.keys())
    placeholders = ", ".join("?" for _ in payload)
    with _get_conn() as conn:
        cur = conn.execute(f"INSERT INTO comm_eventi ({cols}) VALUES ({placeholders})", list(payload.values()))
        conn.commit()
        return get_evento(cur.lastrowid)


def update_evento(evento_id: int, data: dict) -> dict:
    payload = dict(data)
    if not payload:
        return get_evento(evento_id)
    set_sql = ", ".join(f"{k} = ?" for k in payload.keys())
    with _get_conn() as conn:
        conn.execute(f"UPDATE comm_eventi SET {set_sql} WHERE id = ?", list(payload.values()) + [evento_id])
        conn.commit()
        return get_evento(evento_id)


def delete_evento(evento_id: int):
    with _get_conn() as conn:
        conn.execute("DELETE FROM comm_eventi_ricette WHERE evento_id = ?", (evento_id,))
        conn.execute("DELETE FROM comm_eventi_commensali WHERE evento_id = ?", (evento_id,))
        conn.execute("DELETE FROM comm_eventi_foto WHERE evento_id = ?", (evento_id,))
        conn.execute("DELETE FROM comm_eventi WHERE id = ?", (evento_id,))
        conn.commit()


def get_evento_ricette(evento_id: int) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT er.*, r.titolo AS r_titolo, r.portata AS r_portata, r.ingredienti AS r_ingredienti
            FROM comm_eventi_ricette er
            LEFT JOIN comm_ricette r ON er.ricetta_id = r.id
            WHERE er.evento_id = ?
            ORDER BY er.ordine
        """, (evento_id,)).fetchall()
        res = []
        for row in rows:
            d = dict(row)
            d["comm_ricette"] = {
                "titolo": d.pop("r_titolo", None) or "—",
                "portata": d.pop("r_portata", None) or "",
                "ingredienti": d.pop("r_ingredienti", None) or "",
            }
            res.append(d)
        return res


def get_evento_commensali(evento_id: int) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT ec.*, c.nome AS c_nome
            FROM comm_eventi_commensali ec
            LEFT JOIN comm_commensali c ON ec.commensale_id = c.id
            WHERE ec.evento_id = ?
        """, (evento_id,)).fetchall()
        res = []
        for row in rows:
            d = dict(row)
            nome = d.pop("c_nome", None)
            d["comm_commensali"] = {"nome": nome} if nome else None
            res.append(d)
        return res


def add_ricetta_to_evento(evento_id: int, ricetta_id: int, sezione: str = "", nota: str = "", ordine: int = 0):
    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO comm_eventi_ricette (evento_id, ricetta_id, titolo_sezione, nota, ordine)
            VALUES (?, ?, ?, ?, ?)
        """, (evento_id, ricetta_id, sezione, nota, ordine))
        conn.commit()


def add_commensale_to_evento(evento_id: int, commensale_id: int):
    with _get_conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO comm_eventi_commensali (evento_id, commensale_id)
            VALUES (?, ?)
        """, (evento_id, commensale_id))
        conn.commit()


def get_ricetta_last_dates(user_id: str, ricetta_id: int) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute("""
            SELECT e.data, e.descrizione
            FROM comm_eventi_ricette er
            JOIN comm_eventi e ON er.evento_id = e.id
            WHERE er.ricetta_id = ? AND e.user_id = ?
            ORDER BY e.data DESC
            LIMIT 5
        """, (ricetta_id, user_id)).fetchall()
        return [dict(r) for r in rows]


# ── Admin ─────────────────────────────────────────────────────────────────────

def get_all_users() -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, nome, email, ruolo, created_at FROM comm_utenti ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def set_user_role(user_id: str, ruolo: str):
    with _get_conn() as conn:
        conn.execute("UPDATE comm_utenti SET ruolo = ? WHERE id = ?", (ruolo, user_id))
        conn.commit()


def delete_user(user_id: str):
    with _get_conn() as conn:
        conn.execute("DELETE FROM comm_utenti WHERE id = ?", (user_id,))
        conn.commit()
