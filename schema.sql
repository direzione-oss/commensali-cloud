-- ═══════════════════════════════════════════════════════════
-- Commensali Cloud — Schema Supabase
-- Esegui questo script nell'SQL Editor del progetto Supabase
-- ═══════════════════════════════════════════════════════════

-- ── Utenti ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comm_utenti (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    nome text,
    email text UNIQUE NOT NULL,
    password_hash text NOT NULL,
    ruolo text DEFAULT 'utente',
    created_at timestamptz DEFAULT now()
);

-- ── Ricette ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comm_ricette (
    id bigserial PRIMARY KEY,
    user_id uuid REFERENCES comm_utenti(id) ON DELETE CASCADE,
    titolo text NOT NULL,
    foto_url text,
    portata text,
    ingredienti text,
    procedimento text,
    note text,
    created_at timestamptz DEFAULT now()
);

-- ── Commensali ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comm_commensali (
    id bigserial PRIMARY KEY,
    user_id uuid REFERENCES comm_utenti(id) ON DELETE CASCADE,
    nome text NOT NULL
);

-- ── Eventi ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comm_eventi (
    id bigserial PRIMARY KEY,
    user_id uuid REFERENCES comm_utenti(id) ON DELETE CASCADE,
    data date NOT NULL,
    descrizione text,
    luogo text,
    vini text,
    created_at timestamptz DEFAULT now()
);

-- ── Ricette per evento ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS comm_eventi_ricette (
    id bigserial PRIMARY KEY,
    evento_id bigint REFERENCES comm_eventi(id) ON DELETE CASCADE,
    ricetta_id bigint REFERENCES comm_ricette(id) ON DELETE SET NULL,
    titolo_sezione text,
    nota text,
    ordine int DEFAULT 0
);

-- ── Commensali per evento ──────────────────────────────────
CREATE TABLE IF NOT EXISTS comm_eventi_commensali (
    evento_id bigint REFERENCES comm_eventi(id) ON DELETE CASCADE,
    commensale_id bigint REFERENCES comm_commensali(id) ON DELETE CASCADE,
    PRIMARY KEY (evento_id, commensale_id)
);

-- ── Foto eventi ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS comm_eventi_foto (
    id bigserial PRIMARY KEY,
    evento_id bigint REFERENCES comm_eventi(id) ON DELETE CASCADE,
    user_id uuid REFERENCES comm_utenti(id) ON DELETE CASCADE,
    foto_url text NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- ── RLS: disabilita per ora (usiamo filtri user_id nel codice)
ALTER TABLE comm_utenti DISABLE ROW LEVEL SECURITY;
ALTER TABLE comm_ricette DISABLE ROW LEVEL SECURITY;
ALTER TABLE comm_commensali DISABLE ROW LEVEL SECURITY;
ALTER TABLE comm_eventi DISABLE ROW LEVEL SECURITY;
ALTER TABLE comm_eventi_ricette DISABLE ROW LEVEL SECURITY;
ALTER TABLE comm_eventi_commensali DISABLE ROW LEVEL SECURITY;
ALTER TABLE comm_eventi_foto DISABLE ROW LEVEL SECURITY;

-- ── Storage bucket ─────────────────────────────────────────
-- Crea manualmente il bucket "commensali-images" in Storage > New Bucket
-- con accesso Public abilitato.
