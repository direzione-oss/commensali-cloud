from fpdf import FPDF
import os


class MenuPDF(FPDF):
    def __init__(self, title="Menu dell'Evento"):
        super().__init__()
        self.doc_title = title

    def header(self):
        image_path = "image.png"
        if os.path.exists(image_path):
            try:
                self.image(image_path, x=5, y=100, w=40)
            except Exception as e:
                print(f"Errore nel caricare l'immagine: {e}")
        self.set_font('Times', 'B', 20)
        self.cell(0, 10, self.doc_title, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def create_menu_pdf(evento, ricette, commensali, foto_paths, output_path, doc_title="Menu dell'Evento", vini_text=""):
    pdf = MenuPDF(title=doc_title)
    pdf.add_page()

    pdf.set_font("Times", "BI", 24)
    pdf.cell(0, 15, evento['descrizione'], ln=1, align='C')

    pdf.set_font("Helvetica", "I", 14)
    if evento.get('luogo'):
        pdf.cell(0, 10, f"{evento['luogo']} - {evento['data']}", ln=1, align='C')
    else:
        pdf.cell(0, 10, f"{evento['data']}", ln=1, align='C')
    pdf.ln(10)

    if commensali:
        pdf.set_font("Times", "I", 12)
        guests_str = ", ".join(commensali)
        pdf.multi_cell(0, 6, f"Con la partecipazione di:\n{guests_str}", align='C')
        pdf.ln(10)

    has_custom_sections = any('manually_assigned_section' in r for r in ricette)

    if has_custom_sections:
        sections_map = {}
        for r in ricette:
            sec = r.get('manually_assigned_section', 'Altro')
            if sec not in sections_map:
                sections_map[sec] = []
            sections_map[sec].append(r)

        for sec_name, items in sections_map.items():
            pdf.set_font("Times", "BI", 16)
            pdf.cell(0, 10, sec_name, ln=1, align='C')
            for item in items:
                pdf.set_font("Times", "I", 14)
                pdf.cell(0, 8, item['titolo'], ln=1, align='C')
                if item.get('menu_note'):
                    pdf.set_font("Times", "I", 10)
                    pdf.multi_cell(0, 5, item['menu_note'], align='C')
                    pdf.ln(1)
            pdf.ln(5)
    else:
        course_order = ["Antipasti", "Primi", "Zuppe", "Secondi Carne", "Secondi Pesce", "Contorni", "Dolci", "Lievitati"]
        grouped = {k: [] for k in course_order}
        others = []

        for r in ricette:
            portate = [p.strip() for p in r['portata'].split(',')] if r['portata'] else []
            found = False
            for p in portate:
                for k in grouped:
                    if k.lower() == p.lower():
                        grouped[k].append(r)
                        found = True
                        break
                if found:
                    break
            if not found:
                others.append(r)

        for course in course_order:
            items = grouped[course]
            if items:
                pdf.set_font("Times", "BI", 16)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 10, course.upper(), ln=1, align='C')
                pdf.ln(2)
                pdf.set_text_color(0, 0, 0)
                for item in items:
                    pdf.set_font("Times", "BI", 14)
                    pdf.cell(0, 8, item['titolo'], ln=1, align='C')
                    pdf.set_font("Times", "I", 10)
                    ingr = item['ingredienti'] or ''
                    pdf.multi_cell(0, 5, ingr[:100] + "..." if len(ingr) > 100 else ingr, align='C')
                    pdf.ln(3)
                pdf.ln(5)

        if others:
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "ALTRO", ln=1, align='C')
            for item in others:
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 8, item['titolo'], ln=1, align='C')
                pdf.ln(5)
                pdf.set_font("Helvetica", "", 10)
                ingr = item['ingredienti'] or ''
                pdf.multi_cell(0, 5, ingr[:100] + "..." if len(ingr) > 100 else ingr, align='C')
                pdf.ln(3)
            pdf.ln(5)

    if vini_text:
        pdf.ln(5)
        pdf.set_font("Times", "BI", 18)
        pdf.cell(0, 10, "LA CANTINA", ln=1, align='C')
        pdf.set_font("Times", "I", 14)
        pdf.multi_cell(0, 8, vini_text, align='C')
        pdf.ln(10)

    if foto_paths:
        pdf.add_page()
        pdf.set_font("Times", "BI", 20)
        pdf.cell(0, 10, "Ricordi dell'Evento", ln=1, align='C')
        pdf.ln(10)
        for photo_path in foto_paths:
            if os.path.exists(photo_path):
                try:
                    pdf.image(photo_path, x=30, w=150)
                    pdf.ln(10)
                except Exception as e:
                    print(f"Error adding image {photo_path}: {e}")

    pdf.output(output_path)
    return output_path


def create_recipe_pdf(ricetta, output_path):
    """Genera un PDF moderno per una singola ricetta."""
    from PIL import Image as PILImage

    SLATE     = (44,  62,  80)
    ORANGE    = (230, 126,  34)
    YELLOW_BG = (255, 248, 225)
    YELLOW_TX = (120,  90,   0)
    WHITE     = (255, 255, 255)
    DARK_TX   = (30,  30,  30)

    pdf = FPDF()
    pdf.set_margins(0, 0, 0)
    pdf.add_page()

    PW = pdf.w   # 210mm
    PH = pdf.h   # 297mm
    M  = 18      # margine laterale
    CW = PW - 2 * M  # 174mm

    # ── Header band ───────────────────────────────────────────────
    pdf.set_fill_color(*SLATE)
    pdf.rect(0, 0, PW, 38, 'F')

    pdf.set_xy(M, 8)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Times", "B", 26)
    pdf.cell(CW, 14, ricetta['titolo'], align='C')

    if ricetta.get('portata'):
        pdf.set_xy(M, 24)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(189, 195, 199)
        pdf.cell(CW, 8, ricetta['portata'], align='C')

    # Striscia accent arancione
    pdf.set_fill_color(*ORANGE)
    pdf.rect(0, 38, PW, 4, 'F')

    # ── Foto ─────────────────────────────────────────────────────
    current_y = 50
    if ricetta.get('foto_path') and os.path.exists(ricetta['foto_path']):
        try:
            img_w = 120
            img_x = (PW - img_w) / 2
            with PILImage.open(ricetta['foto_path']) as im:
                iw, ih = im.size
                img_h = img_w * (ih / iw)
            pdf.image(ricetta['foto_path'], x=img_x, y=current_y, w=img_w)
            current_y += img_h + 10
        except Exception as e:
            print(f"Errore foto: {e}")

    pdf.set_y(current_y)

    # ── Helper: titolo sezione con accent bar ─────────────────────
    def section_header(label):
        y = pdf.get_y() + 4
        pdf.set_fill_color(*ORANGE)
        pdf.rect(M, y, 4, 10, 'F')
        pdf.set_xy(M + 8, y)
        pdf.set_text_color(*SLATE)
        pdf.set_font("Times", "B", 15)
        pdf.cell(CW - 8, 10, label)
        pdf.ln(13)

    # ── Ingredienti ───────────────────────────────────────────────
    section_header("Ingredienti")
    ingredienti = ricetta.get('ingredienti') or ''
    for riga in [r.strip() for r in ingredienti.split('\n') if r.strip()]:
        by = pdf.get_y() + 2.5
        pdf.set_fill_color(*ORANGE)
        pdf.rect(M, by, 3, 3, 'F')
        pdf.set_x(M + 8)
        pdf.set_text_color(*DARK_TX)
        pdf.set_font("Times", "", 12)
        pdf.multi_cell(CW - 8, 6.5, riga)
    pdf.ln(5)

    # ── Procedimento ───────────────────────────────────────────────
    section_header("Procedimento")
    procedimento = ricetta.get('procedimento') or ''
    for i, passo in enumerate([r.strip() for r in procedimento.split('\n') if r.strip()], 1):
        sy = pdf.get_y()
        pdf.set_fill_color(*ORANGE)
        pdf.rect(M, sy, 8, 8, 'F')
        pdf.set_xy(M, sy)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(8, 8, str(i), align='C')
        pdf.set_xy(M + 12, sy)
        pdf.set_text_color(*DARK_TX)
        pdf.set_font("Times", "", 12)
        pdf.multi_cell(CW - 12, 7, passo)
        pdf.ln(2)
    pdf.ln(4)

    # ── Note ───────────────────────────────────────────────────────
    if ricetta.get('note'):
        ny = pdf.get_y()
        pdf.set_fill_color(*YELLOW_BG)
        pdf.rect(M, ny, CW, 7, 'F')
        pdf.set_xy(M + 4, ny)
        pdf.set_text_color(*YELLOW_TX)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(CW - 4, 7, ">> Note e Trucchetti")
        pdf.ln(8)
        pdf.set_x(M + 4)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_fill_color(*YELLOW_BG)
        pdf.multi_cell(CW - 8, 6, ricetta['note'], fill=True)
        pdf.ln(4)

    # ── Footer band ────────────────────────────────────────────────
    pdf.set_y(PH - 12)
    pdf.set_fill_color(*SLATE)
    pdf.rect(0, PH - 12, PW, 12, 'F')
    pdf.set_xy(0, PH - 10)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(PW, 8, "Commensali - Gestore Menu Anti-Ripetizione", align='C')

    pdf.output(output_path)
    return output_path
