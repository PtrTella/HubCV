# 🚀 HubCV — Typst Studio 2026

Piattaforma modulare, professionale e ad alto impatto per creare, personalizzare ed esportare Curriculum Vitae moderni per ruoli Tech, AI Engineering e Ricerca con compilazione istantanea in **Typst**.

---

## 🌟 Caratteristiche Principali

- 📄 **4 Template Professionali Modulari**:
  - `split_header`: Layout distintivo con header bicolore, avatar centrale e corpo bilanciato a 2 colonne.
  - `modern_tech`: Layout lineare pulito, ad altissimo impatto visivo e massima scansionabilità ATS. Ideale per startup, scale-up e ruoli internazionali.
  - `academic_research`: Tipografia accademica in stile LaTeX Computer Modern, ideale per laboratori di ricerca (INRIA, Max Planck), PhD e borse di studio.
  - `nordic_sidebar`: Formato executive con sidebar scura ad alto contrasto per anagrafica, contatti, skill e lingue, affiancata da un'ampia colonna principale per le esperienze.
- 🌐 **Gestione Dati Unificata Bilingue (IT / EN)**:
  - Tutti i contenuti risiedono in `data/cv.yml`.
  - Passaggio istantaneo tra Italiano e Inglese con terminologia tecnica allineata ai requisiti di AI Engineering.
- 🎨 **Palette Colori & Design System**:
  - Palette preimpostate: *Vibrant Duo (Cyan & Violet)*, *Nordic Slate (Tech & AI)*, *Electric Indigo (GenAI)*, *Deep Emerald (Biotech)*, *Pure Monochrome (ATS)*.
  - Color picker per calibrare ogni elemento (primario, accento, sfondi, divisori).
  - Gestione flessibile della foto profilo (attivabile o disattivabile in un click).
- ⚡ **Streamlit Studio Interattivo**:
  - Compilazione live istantanea ad ogni modifica.
  - Regolazione proporzionale di dimensione font, leading, margini e spaziature tra sezioni per un controllo millimetrico del budget pagina (1 pagina vs 2 pagine anti-overflow).
  - **Audit ATS & Keyword Scanner**: Analisi trasparente di metriche numeriche, verbi d'azione e keyword tecnologiche.

---

## 📂 Struttura del Progetto

```
.
├── app.py                     # Streamlit Studio (GUI completa con live preview e auto-compilazione)
├── Makefile                   # Comandi rapidi di automazione (uv + venv)
├── requirements.txt           # Dipendenze Python (streamlit, typst, pyyaml, watchdog)
├── data/
│   ├── cv.yml                 # Dati anagrafici, testi bilingue e configurazione attiva
│   └── presets.yml            # Palette colori e metadati dei template
├── src/
│   ├── cv.typ                 # Router principale del compilatore Typst
│   ├── utils.typ              # Componenti riutilizzabili (chip competenze, icone, titoli sezioni)
│   └── templates/
│       ├── split_header.typ       # Template Split Header Bicolore
│       ├── modern_tech.typ        # Template Modern Tech
│       ├── academic_research.typ  # Template Ricerca Accademica
│       └── nordic_sidebar.typ     # Template Nordic Sidebar
└── assets/
    └── profile.png            # Foto profilo (ritagliata automaticamente a cerchio)
```

---

## 🛠️ Come Avviare il Progetto

Il progetto utilizza **`uv`** e un virtual environment isolato:

### 1. Installazione Dipendenze
```bash
make setup
```

### 2. Avvia lo Studio Grafico
```bash
make run
```
Si aprirà automaticamente il browser su `http://localhost:8501`.

### 3. Compilazione Rapida da Terminale (CLI)
```bash
make build
```

---

## 🎯 Guida Strategica per Candidature AI Engineer

| Tipo di Candidatura | Template Consigliato | Foto | Lingua |
| :--- | :--- | :--- | :--- |
| **Startup AI & Scale-up Internazionali** | `modern_tech` | Opzionale | `en` |
| **Aziende Big Tech / US / UK (ATS rigido)** | `modern_tech` o `monochrome_ats` | Disattivata | `en` |
| **Laboratori di Ricerca / PhD (INRIA, università)** | `academic_research` | Disattivata | `en` / `it` |
| **Aziende Italiane & Scaleup europee** | `split_header` o `nordic_sidebar` | Attiva | `it` |

---

## 📸 Personalizzazione Foto
Sostituisci il file `assets/profile.png` con la tua foto profilo. Il compilatore Typst provvederà automaticamente al ritaglio e al bordo circolare.
