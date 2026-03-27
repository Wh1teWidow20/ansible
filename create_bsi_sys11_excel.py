#!/usr/bin/env python3
"""Erstellt eine Arbeits-Excel-Tabelle für den BSI IT-Grundschutz Baustein SYS.1.1 Allgemeiner Server."""

import openpyxl
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

# Farben
COLOR_HEADER_DARK = "1F3864"      # Dunkelblau (Titelzeile)
COLOR_HEADER_BLUE = "2E75B6"      # Mittelblau (Abschnittsköpfe)
COLOR_BASIS = "D9E1F2"            # Hellblau (Basisanforderungen)
COLOR_STANDARD = "E2EFDA"         # Hellgrün (Standardanforderungen)
COLOR_ERHOEHTER = "FFF2CC"        # Hellgelb (Erhöhter Schutzbedarf)
COLOR_ROW_ALT_BASIS = "EEF2FA"
COLOR_ROW_ALT_STANDARD = "F0F7EB"
COLOR_ROW_ALT_ERHOEHTER = "FFFAE6"
COLOR_WHITE = "FFFFFF"
COLOR_LIGHT_GRAY = "F2F2F2"

# Anforderungen SYS.1.1 - Allgemeiner Server
requirements = [
    # (ID, Titel, Beschreibung, Verantwortliche, Kategorie)
    # BASISANFORDERUNGEN
    ("SYS.1.1.A1", "Zugangsbeschränkung und Nutzung",
     "Physischer Zugang zu Servern muss auf autorisierte Personen beschränkt sein. "
     "Server dürfen nicht als Arbeitsplatzrechner genutzt werden. "
     "Nicht benötigte Schnittstellen und Dienste müssen deaktiviert werden.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A2", "Benutzerauthentisierung",
     "Alle Benutzenden und Dienste müssen sich vor Zugriff auf ein IT-System authentisieren. "
     "Standardpasswörter müssen geändert werden. Sichere Authentisierungsmechanismen sind einzusetzen.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A3", "Restriktive Rechtevergabe",
     "Zugriffsrechte auf Dateien und Verzeichnisse müssen restriktiv vergeben werden. "
     "Das Prinzip der minimalen Rechtevergabe ist einzuhalten. "
     "Administrative Tätigkeiten sind mit gesonderten Konten durchzuführen.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A4", "Rollentrennung",
     "Für die Administration und Nutzung des Servers müssen unterschiedliche Rollen eingerichtet werden. "
     "Administrative Konten dürfen nicht für die tägliche Arbeit genutzt werden.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A5", "Schutz von Schnittstellen",
     "Alle nicht benötigten Schnittstellen müssen deaktiviert werden. "
     "Physische Schnittstellen (USB, Firewire etc.) sind zu sichern.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A6", "Deaktivierung nicht benötigter Dienste",
     "Nicht benötigte Dienste und Komponenten müssen deaktiviert oder deinstalliert werden. "
     "Installierte Softwarekomponenten sind regelmäßig zu überprüfen.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A7", "Updates und Patches",
     "Betriebssystem und installierte Software müssen regelmäßig aktualisiert werden. "
     "Sicherheitsrelevante Patches sind zeitnah einzuspielen. "
     "Ein Patch-Management-Prozess muss etabliert sein.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A8", "Regelmäßige Datensicherung",
     "Regelmäßige Backups der Daten müssen durchgeführt werden. "
     "Sicherungskopien sind gesichert aufzubewahren. "
     "Wiederherstellungstests müssen regelmäßig durchgeführt werden.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A9", "Einsatz von Virenschutzprogrammen",
     "Auf Servern müssen Virenschutzprogramme eingesetzt werden, sofern keine anderen Schutzmaßnahmen "
     "gleichwertigen Schutz bieten. Virensignaturen müssen aktuell gehalten werden.",
     "IT-Betrieb", "Basis"),
    ("SYS.1.1.A10", "Protokollierung",
     "Sicherheitsrelevante Ereignisse müssen protokolliert werden. "
     "Protokolldaten sind regelmäßig auszuwerten. "
     "Protokolldaten müssen vor unberechtigtem Zugriff und Manipulationen geschützt werden.",
     "IT-Betrieb", "Basis"),

    # STANDARDANFORDERUNGEN
    ("SYS.1.1.A11", "Festlegung einer Sicherheitsrichtlinie für Server",
     "Es muss eine Sicherheitsrichtlinie für Server erstellt und regelmäßig aktualisiert werden. "
     "Die Richtlinie muss alle sicherheitsrelevanten Aspekte der Serverbetriebsumgebung abdecken.",
     "ISB, IT-Betrieb", "Standard"),
    ("SYS.1.1.A12", "Planung des Server-Einsatzes",
     "Jeder Server muss vor seiner Beschaffung und Installation geplant werden. "
     "Anforderungen an Hardware, Betriebssystem und Anwendungen sind zu dokumentieren.",
     "IT-Betrieb, Fachverantwortliche", "Standard"),
    ("SYS.1.1.A13", "Beschaffung von Servern",
     "Bei der Beschaffung von Servern müssen Sicherheitsaspekte berücksichtigt werden. "
     "Hardware und Software müssen von vertrauenswürdigen Lieferanten bezogen werden.",
     "Beschaffung, IT-Betrieb", "Standard"),
    ("SYS.1.1.A14", "Erstellung und Pflege eines Betriebshandbuchs",
     "Für jeden Server muss ein Betriebshandbuch erstellt und gepflegt werden. "
     "Es muss alle betriebsrelevanten Informationen enthalten.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A15", "Unterbrechungsfreie und stabile Stromversorgung",
     "Server müssen an eine unterbrechungsfreie Stromversorgung (USV) angeschlossen werden. "
     "Die USV muss regelmäßig gewartet und getestet werden.",
     "IT-Betrieb, Haustechnik", "Standard"),
    ("SYS.1.1.A16", "Sichere Installation und Grundkonfiguration",
     "Server müssen nach dem Prinzip der minimalen Installation installiert werden. "
     "Sichere Grundkonfigurationen sind zu dokumentieren und einzuhalten.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A17", "Einsatz von Sicherheitsrichtlinien für das Betriebssystem",
     "Sicherheitsrichtlinien (z. B. Group Policies) müssen für das Betriebssystem definiert "
     "und umgesetzt werden.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A18", "Verschlüsselung der Kommunikation",
     "Die Kommunikation zwischen Servern und Clients muss verschlüsselt erfolgen. "
     "Unsichere Protokolle müssen durch sichere Alternativen ersetzt werden.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A19", "Einrichtung lokaler Paketfilter",
     "Auf Servern müssen lokale Paketfilter eingerichtet werden, um den Netzwerkzugriff zu beschränken. "
     "Regeln müssen dokumentiert und regelmäßig überprüft werden.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A20", "Beschränkung des Zugangs über Netze",
     "Der Zugang zu Servern über Netze muss beschränkt werden. "
     "Nur autorisierte Systeme und Benutzer dürfen Zugriff erhalten.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A21", "Betrieb und Administration in getrennten Netzen",
     "Server sollen über ein separates Administrationsnetz administriert werden. "
     "Produktions- und Administrationsnetz müssen voneinander getrennt sein.",
     "IT-Betrieb, Netzadministration", "Standard"),
    ("SYS.1.1.A22", "Zentrale Protokollierung und Auswertung von Protokolldaten",
     "Protokolldaten aller Server sollen zentral gesammelt und ausgewertet werden. "
     "Ein SIEM oder vergleichbares System soll eingesetzt werden.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A23", "Systemüberwachung und Monitoring",
     "Server müssen in ein System zur Systemüberwachung eingebunden werden. "
     "Kritische Parameter wie Verfügbarkeit, Auslastung und Fehler müssen überwacht werden.",
     "IT-Betrieb", "Standard"),
    ("SYS.1.1.A24", "Sicherheitsprüfungen",
     "Regelmäßige Sicherheitsprüfungen (z. B. Vulnerability Scans) müssen durchgeführt werden. "
     "Gefundene Schwachstellen müssen zeitnah behoben werden.",
     "IT-Betrieb, ISB", "Standard"),
    ("SYS.1.1.A25", "Geregelte Außerbetriebnahme von Servern",
     "Bei der Außerbetriebnahme von Servern müssen alle sensitiven Daten sicher gelöscht werden. "
     "Hardware muss gemäß Datenschutzanforderungen entsorgt werden.",
     "IT-Betrieb", "Standard"),

    # ANFORDERUNGEN BEI ERHÖHTEM SCHUTZBEDARF
    ("SYS.1.1.A26", "Schutz vor Denial-of-Service-Angriffen",
     "Gegen Denial-of-Service-Angriffe müssen geeignete Schutzmaßnahmen implementiert werden. "
     "Rate Limiting und Traffic-Filterung sind einzusetzen.",
     "IT-Betrieb, Netzadministration", "Erhöht"),
    ("SYS.1.1.A27", "Hostbasiertes Angriffserkennungssystem",
     "Ein hostbasiertes Angriffserkennungssystem (HIDS) muss eingesetzt werden. "
     "Meldungen des HIDS müssen überwacht und ausgewertet werden.",
     "IT-Betrieb", "Erhöht"),
    ("SYS.1.1.A28", "Redundanz",
     "Für hochverfügbare Server müssen Redundanzmaßnahmen implementiert werden. "
     "Single Points of Failure sind zu vermeiden.",
     "IT-Betrieb, Architektur", "Erhöht"),
    ("SYS.1.1.A29", "Einrichtung einer Testumgebung",
     "Für kritische Server muss eine Testumgebung eingerichtet werden. "
     "Änderungen müssen vor dem Produktiveinsatz in der Testumgebung validiert werden.",
     "IT-Betrieb", "Erhöht"),
    ("SYS.1.1.A30", "Verschlüsselung der Massenspeicher",
     "Die Massenspeicher von Servern mit erhöhtem Schutzbedarf müssen verschlüsselt werden. "
     "Schlüsselverwaltung muss sicher gestaltet sein.",
     "IT-Betrieb", "Erhöht"),
    ("SYS.1.1.A31", "Fernwartung",
     "Fernwartungszugriffe müssen abgesichert werden. "
     "Alle Fernwartungssitzungen müssen protokolliert werden. "
     "Zugriff ist auf das notwendige Minimum zu beschränken.",
     "IT-Betrieb", "Erhöht"),
]

# Umsetzungsstatus-Optionen
status_options = ["Nicht umgesetzt", "In Umsetzung", "Umgesetzt", "Entbehrlich", "Nicht anwendbar"]

def create_border(style='thin'):
    side = Side(style=style)
    return Border(left=side, right=side, top=side, bottom=side)

def create_header_border():
    return Border(
        left=Side(style='medium'),
        right=Side(style='medium'),
        top=Side(style='medium'),
        bottom=Side(style='medium')
    )

def set_column_widths(ws):
    widths = {
        'A': 14,   # Anforderungs-ID
        'B': 38,   # Titel
        'C': 65,   # Beschreibung / Maßnahme
        'D': 22,   # Verantwortliche
        'E': 14,   # Kategorie
        'F': 20,   # Umsetzungsstatus
        'G': 12,   # Priorität
        'H': 18,   # Fälligkeitsdatum
        'I': 22,   # Zuständige Person
        'J': 55,   # Bemerkungen / Nachweise
    }
    for col, width in widths.items():
        ws.column_dimensions[col].width = width

def add_data_validation(ws, start_row, end_row):
    from openpyxl.worksheet.datavalidation import DataValidation
    status_dv = DataValidation(
        type="list",
        formula1='"Nicht umgesetzt,In Umsetzung,Umgesetzt,Entbehrlich,Nicht anwendbar"',
        allow_blank=True,
        showDropDown=False
    )
    status_dv.sqref = f"F{start_row}:F{end_row}"
    ws.add_data_validation(status_dv)

    prio_dv = DataValidation(
        type="list",
        formula1='"Hoch,Mittel,Niedrig"',
        allow_blank=True,
        showDropDown=False
    )
    prio_dv.sqref = f"G{start_row}:G{end_row}"
    ws.add_data_validation(prio_dv)

def create_excel():
    wb = openpyxl.Workbook()

    # ── Tabellenblatt 1: Anforderungen ──────────────────────────────────────
    ws = wb.active
    ws.title = "SYS.1.1 Anforderungen"
    ws.sheet_view.showGridLines = True
    ws.freeze_panes = "A4"

    set_column_widths(ws)

    # Titelzeile
    ws.merge_cells("A1:J1")
    title_cell = ws["A1"]
    title_cell.value = "BSI IT-Grundschutz – Baustein SYS.1.1: Allgemeiner Server"
    title_cell.font = Font(name="Calibri", bold=True, size=16, color=COLOR_WHITE)
    title_cell.fill = PatternFill("solid", fgColor=COLOR_HEADER_DARK)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    title_cell.border = create_header_border()
    ws.row_dimensions[1].height = 32

    # Untertitel / Meta
    ws.merge_cells("A2:J2")
    meta_cell = ws["A2"]
    meta_cell.value = (
        "Erstellungsdatum: 2026-03-27  |  Stand: BSI IT-Grundschutz-Kompendium Edition 2023  |  "
        "Verantwortlich: ___________________________"
    )
    meta_cell.font = Font(name="Calibri", italic=True, size=10, color="4F4F4F")
    meta_cell.fill = PatternFill("solid", fgColor=COLOR_LIGHT_GRAY)
    meta_cell.alignment = Alignment(horizontal="center", vertical="center")
    meta_cell.border = create_border()
    ws.row_dimensions[2].height = 18

    # Spaltenköpfe
    headers = [
        "Anforderungs-ID", "Titel", "Beschreibung / Maßnahme",
        "Verantwortliche", "Kategorie", "Umsetzungsstatus",
        "Priorität", "Fälligkeitsdatum", "Zuständige Person", "Bemerkungen / Nachweise"
    ]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col_idx, value=header)
        cell.font = Font(name="Calibri", bold=True, size=11, color=COLOR_WHITE)
        cell.fill = PatternFill("solid", fgColor=COLOR_HEADER_BLUE)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = create_header_border()
    ws.row_dimensions[3].height = 28

    # Datenzeilen
    row = 4
    category_colors = {
        "Basis": (COLOR_BASIS, COLOR_ROW_ALT_BASIS),
        "Standard": (COLOR_STANDARD, COLOR_ROW_ALT_STANDARD),
        "Erhöht": (COLOR_ERHOEHTER, COLOR_ROW_ALT_ERHOEHTER),
    }
    category_labels = {
        "Basis": "Basisanforderung",
        "Standard": "Standardanforderung",
        "Erhöht": "Erhöhter Schutzbedarf",
    }

    section_headers = {
        "Basis": ("BASISANFORDERUNGEN (MUSS)", "1F3864"),
        "Standard": ("STANDARDANFORDERUNGEN (SOLL)", "375623"),
        "Erhöht": ("ANFORDERUNGEN BEI ERHÖHTEM SCHUTZBEDARF", "7B4F00"),
    }

    last_category = None
    data_start_row = row

    for req_id, title, desc, responsible, category in requirements:
        # Abschnittsüberschrift bei Kategorienwechsel
        if category != last_category:
            label, color = section_headers[category]
            ws.merge_cells(f"A{row}:J{row}")
            sec_cell = ws[f"A{row}"]
            sec_cell.value = label
            sec_cell.font = Font(name="Calibri", bold=True, size=11, color=COLOR_WHITE)
            sec_cell.fill = PatternFill("solid", fgColor=color)
            sec_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            sec_cell.border = create_header_border()
            ws.row_dimensions[row].height = 22
            row += 1
            last_category = category

        colors = category_colors[category]
        # Alternierende Zeilen innerhalb Kategorie
        fill_color = colors[0] if (row % 2 == 0) else colors[1]

        values = [
            req_id, title, desc, responsible,
            category_labels[category],
            "",   # Umsetzungsstatus – per Dropdown
            "",   # Priorität – per Dropdown
            "",   # Fälligkeitsdatum
            "",   # Zuständige Person
            "",   # Bemerkungen
        ]
        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=row, column=col_idx, value=value)
            cell.font = Font(name="Calibri", size=10)
            cell.fill = PatternFill("solid", fgColor=fill_color)
            cell.border = create_border()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if col_idx == 1:
                cell.font = Font(name="Calibri", size=10, bold=True)
                cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
            elif col_idx == 5:
                cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)
        ws.row_dimensions[row].height = 60
        row += 1

    data_end_row = row - 1
    add_data_validation(ws, data_start_row, data_end_row)

    # ── Tabellenblatt 2: Zusammenfassung ────────────────────────────────────
    ws2 = wb.create_sheet("Zusammenfassung")
    ws2.column_dimensions['A'].width = 32
    ws2.column_dimensions['B'].width = 16
    ws2.column_dimensions['C'].width = 16
    ws2.column_dimensions['D'].width = 16
    ws2.column_dimensions['E'].width = 18

    ws2.merge_cells("A1:E1")
    t = ws2["A1"]
    t.value = "Zusammenfassung – SYS.1.1 Umsetzungsstand"
    t.font = Font(name="Calibri", bold=True, size=14, color=COLOR_WHITE)
    t.fill = PatternFill("solid", fgColor=COLOR_HEADER_DARK)
    t.alignment = Alignment(horizontal="center", vertical="center")
    t.border = create_header_border()
    ws2.row_dimensions[1].height = 28

    h2_headers = ["Kategorie", "Gesamt", "Umgesetzt", "In Umsetzung", "Nicht umgesetzt"]
    for ci, hdr in enumerate(h2_headers, 1):
        c = ws2.cell(row=2, column=ci, value=hdr)
        c.font = Font(name="Calibri", bold=True, size=11, color=COLOR_WHITE)
        c.fill = PatternFill("solid", fgColor=COLOR_HEADER_BLUE)
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = create_header_border()
    ws2.row_dimensions[2].height = 22

    summary_data = [
        ("Basisanforderungen", 10, "", "", ""),
        ("Standardanforderungen", 15, "", "", ""),
        ("Erhöhter Schutzbedarf", 6, "", "", ""),
        ("Gesamt", 31, "", "", ""),
    ]
    fill_colors_s = [COLOR_BASIS, COLOR_STANDARD, COLOR_ERHOEHTER, COLOR_LIGHT_GRAY]
    for ri, (row_data, fill) in enumerate(zip(summary_data, fill_colors_s), 3):
        for ci, val in enumerate(row_data, 1):
            c = ws2.cell(row=ri, column=ci, value=val)
            c.font = Font(name="Calibri", size=11, bold=(ri == 6))
            c.fill = PatternFill("solid", fgColor=fill)
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = create_border()
        ws2.row_dimensions[ri].height = 20

    # Hinweis
    ws2.merge_cells("A8:E8")
    note = ws2["A8"]
    note.value = (
        "Hinweis: Bitte Umsetzungsstatus im Tabellenblatt 'SYS.1.1 Anforderungen' pflegen. "
        "Diese Tabelle dient als manuelle Auswertungsübersicht."
    )
    note.font = Font(name="Calibri", italic=True, size=9, color="666666")
    note.alignment = Alignment(wrap_text=True, horizontal="left")
    ws2.row_dimensions[8].height = 32

    # ── Tabellenblatt 3: Legende ─────────────────────────────────────────────
    ws3 = wb.create_sheet("Legende")
    ws3.column_dimensions['A'].width = 24
    ws3.column_dimensions['B'].width = 60

    ws3.merge_cells("A1:B1")
    lt = ws3["A1"]
    lt.value = "Legende & Hinweise"
    lt.font = Font(name="Calibri", bold=True, size=14, color=COLOR_WHITE)
    lt.fill = PatternFill("solid", fgColor=COLOR_HEADER_DARK)
    lt.alignment = Alignment(horizontal="center", vertical="center")
    lt.border = create_header_border()
    ws3.row_dimensions[1].height = 28

    legend_entries = [
        ("Umsetzungsstatus", ""),
        ("Nicht umgesetzt", "Anforderung ist noch nicht adressiert worden."),
        ("In Umsetzung", "Maßnahmen zur Umsetzung wurden begonnen."),
        ("Umgesetzt", "Anforderung ist vollständig erfüllt und nachgewiesen."),
        ("Entbehrlich", "Anforderung wurde risikobasiert als entbehrlich eingestuft (mit Begründung)."),
        ("Nicht anwendbar", "Anforderung ist für die vorliegende Systemumgebung nicht relevant."),
        ("", ""),
        ("Priorität", ""),
        ("Hoch", "Sofortiger Handlungsbedarf; kritische Sicherheitslücke."),
        ("Mittel", "Umsetzung im nächsten Planungszyklus."),
        ("Niedrig", "Langfristige Verbesserungsmaßnahme."),
        ("", ""),
        ("Anforderungskategorien", ""),
        ("Basisanforderung", "Pflichtanforderungen gemäß IT-Grundschutz (MUSS)."),
        ("Standardanforderung", "Empfohlene Anforderungen (SOLL), normaler Schutzbedarf."),
        ("Erhöhter Schutzbedarf", "Zusätzliche Maßnahmen bei hohem/sehr hohem Schutzbedarf."),
    ]
    for ri, (term, desc) in enumerate(legend_entries, 2):
        c_term = ws3.cell(row=ri, column=1, value=term)
        c_desc = ws3.cell(row=ri, column=2, value=desc)
        is_section = term in ("Umsetzungsstatus", "Priorität", "Anforderungskategorien")
        if is_section:
            for c in (c_term, c_desc):
                c.font = Font(name="Calibri", bold=True, size=11, color=COLOR_WHITE)
                c.fill = PatternFill("solid", fgColor=COLOR_HEADER_BLUE)
                c.border = create_header_border()
                c.alignment = Alignment(vertical="center")
        elif term:
            for c in (c_term, c_desc):
                c.font = Font(name="Calibri", size=10)
                c.fill = PatternFill("solid", fgColor=COLOR_LIGHT_GRAY if ri % 2 == 0 else COLOR_WHITE)
                c.border = create_border()
                c.alignment = Alignment(vertical="center", wrap_text=True)
        ws3.row_dimensions[ri].height = 18

    output_path = "/home/user/ansible/BSI_SYS1.1_Arbeitsmappe.xlsx"
    wb.save(output_path)
    print(f"Excel-Datei erstellt: {output_path}")

if __name__ == "__main__":
    create_excel()
