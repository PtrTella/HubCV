import streamlit as st
import yaml
import os
import re
import uuid
import base64
import shutil

# Typst compiler check
try:
    import typst
    HAS_TYPST = True
except ImportError:
    HAS_TYPST = False

st.set_page_config(
    page_title="HubCV | Typst Resume Studio",
    page_icon=":material/badge:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== MULTI-SESSION ISOLATION SETUP ====================
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:10]

session_id = st.session_state.session_id
session_dir = os.path.join("data", "sessions", session_id)
os.makedirs(session_dir, exist_ok=True)
session_yaml_rel = f"/data/sessions/{session_id}/cv.yml"
session_yaml_abs = os.path.join(session_dir, "cv.yml")

def load_yaml_file(path, default=None):
    if not os.path.exists(path):
        return default or {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or (default or {})

def save_yaml_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

# Initialize Session Data from Master cv.yml or existing session file
if "cv_data" not in st.session_state:
    if os.path.exists(session_yaml_abs):
        st.session_state.cv_data = load_yaml_file(session_yaml_abs)
    else:
        master_data = load_yaml_file("data/cv.yml")
        st.session_state.cv_data = master_data
        save_yaml_file(session_yaml_abs, master_data)

cv_data = st.session_state.cv_data
presets_data = load_yaml_file("data/presets.yml", {"palettes": {}, "templates_meta": {}})
palettes = presets_data.get("palettes", {})
templates_meta = presets_data.get("templates_meta", {})

# Configuration sanity defaults
cfg = cv_data.setdefault("config", {})
cfg.setdefault("template", "split_header")
cfg.setdefault("palette", "vibrant_duo")
cfg.setdefault("lang", "it")
cfg.setdefault("font_family", "Helvetica")
cfg.setdefault("font_size", "8.5pt")
cfg.setdefault("line_spacing", "0.46em")
cfg.setdefault("section_spacing", "4.0pt")
cfg.setdefault("margin_y", "1.0cm")
cfg.setdefault("margin_bottom", "0.8cm")
cfg.setdefault("margin_x", "1.2cm")
cfg.setdefault("show_photo", True)
cfg.setdefault("show_gdpr", True)
cfg.setdefault("colors", {})

# ==================== IN-MEMORY COMPILER ====================
def compile_session_pdf(data_dict, lang=None):
    if not HAS_TYPST:
        return None, "Compilatore Typst non trovato. Esegui 'make setup' o 'pip install typst'."
    
    # Clone and set language if specified
    active_dict = dict(data_dict)
    if lang:
        active_dict["config"] = dict(data_dict["config"])
        active_dict["config"]["lang"] = lang
        
    save_yaml_file(session_yaml_abs, active_dict)
    try:
        pdf_bytes = typst.compile(
            "src/cv.typ",
            root=".",
            sys_inputs={"data_path": session_yaml_rel}
        )
        return pdf_bytes, None
    except Exception as e:
        return None, str(e)

def count_pdf_pages(pdf_bytes):
    if not pdf_bytes:
        return 0
    try:
        matches = re.findall(rb'/Type\s*/Page\b', pdf_bytes)
        return len(matches) if matches else 1
    except Exception:
        return 1

# ==================== TOP CONTROL BAR ====================
top_col1, top_col2, top_col3 = st.columns([2.2, 1.2, 1.6], vertical_alignment="center")

with top_col1:
    st.markdown("### :material/badge: HubCV Studio")
    st.caption("Crea, compila e scarica il tuo CV professionale bilingue in Typst.")

with top_col2:
    active_lang = st.segmented_control(
        "Lingua anteprima",
        options=["it", "en"],
        format_func=lambda x: "Italiano 🇮🇹" if x == "it" else "English 🇬🇧",
        default=cfg.get("lang", "it"),
        label_visibility="collapsed"
    ) or cfg.get("lang", "it")
    cfg["lang"] = active_lang

with top_col3:
    action_c1, action_c2 = st.columns([1.1, 1.1])
    with action_c1:
        # Import YAML popover
        with st.popover("Carica YAML", icon=":material/upload:"):
            st.markdown("**Carica il tuo profilo salvato**")
            st.caption("Importa un file YAML precedente per non dover reinserire le tue informazioni.")
            uploaded_yaml = st.file_uploader("Seleziona file .yml", type=["yml", "yaml"], label_visibility="collapsed")
            if uploaded_yaml is not None:
                try:
                    loaded_content = yaml.safe_load(uploaded_yaml.read().decode("utf-8"))
                    if isinstance(loaded_content, dict) and ("it" in loaded_content or "en" in loaded_content):
                        st.session_state.cv_data = loaded_content
                        save_yaml_file(session_yaml_abs, loaded_content)
                        st.toast("Profilo caricato con successo!", icon=":material/check_circle:")
                        st.rerun()
                    else:
                        st.error("Formato YAML non valido. Il file deve contenere le sezioni del CV.")
                except Exception as err:
                    st.error(f"Errore lettura file: {err}")
    with action_c2:
        # Export IT + EN bundle
        if st.button("Esporta IT+EN", icon=":material/folder_zip:"):
            pdf_it, _ = compile_session_pdf(cv_data, lang="it")
            pdf_en, _ = compile_session_pdf(cv_data, lang="en")
            if pdf_it and pdf_en:
                st.download_button(
                    "Scarica CV Italiano 🇮🇹",
                    data=pdf_it,
                    file_name="CV_Italiano.pdf",
                    mime="application/pdf",
                    key="dl_it_btn"
                )
                st.download_button(
                    "Scarica CV English 🇬🇧",
                    data=pdf_en,
                    file_name="CV_English.pdf",
                    mime="application/pdf",
                    key="dl_en_btn"
                )
                st.toast("Entrambi i PDF pronti per il download!", icon=":material/done_all:")

st.space("small")

# ==================== MAIN WORKSPACE ====================
left_panel, right_panel = st.columns([1.15, 0.85], gap="large")

with left_panel:
    tab_content, tab_style, tab_audit = st.tabs([
        ":material/person: I Miei Dati & Esperienze",
        ":material/palette: Stile, Template & Layout",
        ":material/fact_check: Audit ATS & Scansionabilità"
    ])

    # -------------------------------------------------------------
    # TAB 1: I MIEI DATI & ESPERIENZE (CORE CONTENT)
    # -------------------------------------------------------------
    with tab_content:
        edit_lang = st.segmented_control(
            "Lingua in modifica",
            options=["it", "en"],
            format_func=lambda x: "Modifica Italiano 🇮🇹" if x == "it" else "Edit English 🇬🇧",
            default=active_lang,
            label_visibility="collapsed"
        ) or active_lang

        lang_data = cv_data.setdefault(edit_lang, {})
        lang_data.setdefault("headings", {})

        # Dati Personali
        with st.expander("👤 Informazioni Personali & Contatti", expanded=True):
            p = cv_data.setdefault("personal", {})
            p1, p2 = st.columns(2)
            with p1:
                p["name"] = st.text_input("Nome e Cognome", p.get("name", ""))
                p["email"] = st.text_input("Email", p.get("email", ""))
                p["phone"] = st.text_input("Telefono", p.get("phone", ""))
            with p2:
                if isinstance(p.get("headline"), dict):
                    p["headline"][edit_lang] = st.text_input("Titolo Professionale (es. AI Engineer)", p["headline"].get(edit_lang, "AI Engineer"))
                else:
                    p["headline"] = {edit_lang: st.text_input("Titolo Professionale", str(p.get("headline", "AI Engineer")))}
                p["github"] = st.text_input("GitHub / Portfolio", p.get("github", ""))
                p["location"] = st.text_input("Località (Città, Paese)", p.get("location", ""))

            # Upload Foto Profilo Personale
            st.space("small")
            photo_file = st.file_uploader("Carica una tua Foto Profilo (PNG / JPG)", type=["png", "jpg", "jpeg"])
            if photo_file is not None:
                custom_photo_path = os.path.join(session_dir, "photo.png")
                with open(custom_photo_path, "wb") as f_img:
                    f_img.write(photo_file.read())
                cfg["photo_path"] = f"/data/sessions/{session_id}/photo.png"
                st.toast("Foto profilo aggiornata!", icon=":material/image:")

        # Profilo Professionale
        with st.expander(f"📝 Profilo & Bio ({edit_lang.upper()})", expanded=True):
            lang_data["headings"]["profile"] = st.text_input("Titolo Sezione", lang_data["headings"].get("profile", "PROFILO"))
            lang_data["profile"] = st.text_area("Testo del Profilo", lang_data.get("profile", ""), height=105)

        # Esperienze Lavorative
        with st.expander(f"💼 Esperienze Lavorative ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["experience"] = st.text_input("Titolo Sezione Esperienze", lang_data["headings"].get("experience", "ESPERIENZE"))
            exps = lang_data.setdefault("experience", [])

            for i, exp in enumerate(exps):
                with st.container(border=True):
                    exp_top1, exp_top2 = st.columns([4, 1])
                    with exp_top1:
                        st.markdown(f"**Esperienza #{i+1}: {exp.get('role', 'Nuovo Ruolo')}**")
                    with exp_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_exp_{edit_lang}_{i}"):
                            exps.pop(i)
                            st.rerun()

                    c_r1, c_r2 = st.columns([2, 1])
                    with c_r1:
                        exp["role"] = st.text_input("Ruolo", exp.get("role", ""), key=f"exp_r_{edit_lang}_{i}")
                        exp["company"] = st.text_input("Azienda / Ente", exp.get("company", ""), key=f"exp_c_{edit_lang}_{i}")
                    with c_r2:
                        exp["period"] = st.text_input("Periodo (es. 2024 - Presente)", exp.get("period", ""), key=f"exp_p_{edit_lang}_{i}")

                    bullets = exp.get("bullets", [])
                    bullets_text = "\n".join(bullets) if isinstance(bullets, list) and bullets else exp.get("description", "")
                    new_bullets_text = st.text_area(
                        "Bullet points (uno per riga. Usa il **grassetto** per mettere in risalto numeri, percentuali e tool)",
                        value=bullets_text,
                        height=95,
                        key=f"exp_b_{edit_lang}_{i}"
                    )
                    exp["bullets"] = [b.strip() for b in new_bullets_text.split("\n") if b.strip()]
                    exp["description"] = " ".join(exp["bullets"])

            if st.button("+ Aggiungi Nuova Esperienza", icon=":material/add:", key=f"add_exp_{edit_lang}"):
                exps.append({
                    "role": "Nuovo Ruolo",
                    "company": "Nome Azienda",
                    "period": "2025 - Presente",
                    "description": "",
                    "bullets": ["Descrivi l'obiettivo raggiunto, il metodo usato e l'impatto numerico."]
                })
                st.rerun()

        # Istruzione
        with st.expander(f"🎓 Istruzione & Percorsi Accademici ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["education"] = st.text_input("Titolo Sezione Istruzione", lang_data["headings"].get("education", "ISTRUZIONE"))
            edus = lang_data.setdefault("education", [])
            for i, edu in enumerate(edus):
                with st.container(border=True):
                    ed_top1, ed_top2 = st.columns([4, 1])
                    with ed_top1:
                        st.markdown(f"**Titolo #{i+1}: {edu.get('degree', '')}**")
                    with ed_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_edu_{edit_lang}_{i}"):
                            edus.pop(i)
                            st.rerun()

                    ed_c1, ed_c2 = st.columns([2, 1])
                    with ed_c1:
                        edu["degree"] = st.text_input("Titolo di Studio", edu.get("degree", ""), key=f"ed_d_{edit_lang}_{i}")
                        edu["institution"] = st.text_input("Università / Ente", edu.get("institution", ""), key=f"ed_inst_{edit_lang}_{i}")
                    with ed_c2:
                        edu["period"] = st.text_input("Periodo (es. 2020 - 2023)", edu.get("period", ""), key=f"ed_p_{edit_lang}_{i}")
                    edu["details"] = st.text_input("Dettagli / Tesi", edu.get("details", ""), key=f"ed_det_{edit_lang}_{i}")

            if st.button("+ Aggiungi Titolo di Studio", icon=":material/add:", key=f"add_edu_{edit_lang}"):
                edus.append({
                    "degree": "Nuovo Titolo",
                    "institution": "Università",
                    "period": "2025",
                    "details": ""
                })
                st.rerun()

        # Competenze Tecniche
        with st.expander(f"💻 Competenze Tecniche ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["skills"] = st.text_input("Titolo Sezione Competenze", lang_data["headings"].get("skills", "SKILLS"))
            sks = lang_data.setdefault("skills", [])
            for i, sk in enumerate(sks):
                with st.container(border=True):
                    sk_top1, sk_top2 = st.columns([4, 1])
                    with sk_top1:
                        st.markdown(f"**Categoria #{i+1}: {sk.get('category', '')}**")
                    with sk_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_sk_{edit_lang}_{i}"):
                            sks.pop(i)
                            st.rerun()
                    sc1, sc2 = st.columns([1, 2])
                    with sc1:
                        sk["category"] = st.text_input("Categoria", sk.get("category", ""), key=f"sk_c_{edit_lang}_{i}")
                    with sc2:
                        sk["items"] = st.text_input("Tecnologie (separate da virgola)", sk.get("items", ""), key=f"sk_it_{edit_lang}_{i}")

            if st.button("+ Aggiungi Categoria Competenze", icon=":material/add:", key=f"add_sk_{edit_lang}"):
                sks.append({"category": "Nuova Categoria", "items": "Tool 1, Tool 2, Tool 3"})
                st.rerun()

        # Progetti Selezionati
        with st.expander(f"🚀 Progetti Selezionati ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["projects"] = st.text_input("Titolo Sezione Progetti", lang_data["headings"].get("projects", "PROGETTI SELEZIONATI"))
            projs = lang_data.setdefault("projects", [])
            for i, proj in enumerate(projs):
                with st.container(border=True):
                    p_top1, p_top2 = st.columns([4, 1])
                    with p_top1:
                        st.markdown(f"**Progetto #{i+1}: {proj.get('name', '')}**")
                    with p_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_pr_{edit_lang}_{i}"):
                            projs.pop(i)
                            st.rerun()
                    pr1, pr2 = st.columns([2, 1])
                    with pr1:
                        proj["name"] = st.text_input("Nome Progetto", proj.get("name", ""), key=f"pr_n_{edit_lang}_{i}")
                        proj["tech"] = st.text_input("Tecnologie usate", proj.get("tech", ""), key=f"pr_t_{edit_lang}_{i}")
                    with pr2:
                        proj["link"] = st.text_input("Link (GitHub / Demo)", proj.get("link", ""), key=f"pr_l_{edit_lang}_{i}")
                    proj["description"] = st.text_area("Descrizione sintetica", proj.get("description", ""), height=55, key=f"pr_d_{edit_lang}_{i}")

            if st.button("+ Aggiungi Progetto", icon=":material/add:", key=f"add_pr_{edit_lang}"):
                projs.append({
                    "name": "Nuovo Progetto",
                    "tech": "Python, Docker",
                    "link": "github.com",
                    "description": "Breve descrizione del risultato ottenuto."
                })
                st.rerun()

        # Lingue, Volontariato & GDPR
        with st.expander(f"🌐 Lingue, Volontariato & Privacy ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["languages"] = st.text_input("Titolo Lingue", lang_data["headings"].get("languages", "LINGUE"))
            for i, l in enumerate(lang_data.setdefault("languages", [])):
                lc1, lc2 = st.columns(2)
                with lc1:
                    l["lang"] = st.text_input(f"Lingua #{i+1}", l.get("lang", ""), key=f"l_n_{edit_lang}_{i}")
                with lc2:
                    l["level"] = st.text_input(f"Livello #{i+1}", l.get("level", ""), key=f"l_v_{edit_lang}_{i}")

            st.space("small")
            lang_data["headings"]["volunteer"] = st.text_input("Titolo Volontariato", lang_data["headings"].get("volunteer", "VOLONTARIATO"))
            lang_data["volunteer"] = st.text_area("Attività extra / Volontariato", lang_data.get("volunteer", ""), height=65)

            st.space("small")
            lang_data["footer"] = st.text_area("Clausola GDPR / Privacy (in calce al CV)", lang_data.get("footer", ""), height=50)

    # -------------------------------------------------------------
    # TAB 2: STILE, TEMPLATE & LAYOUT
    # -------------------------------------------------------------
    with tab_style:
        st.subheader("1. Scelta del Template Grafico")
        tpl_keys = ["split_header", "modern_tech", "academic_research", "nordic_sidebar"]
        current_tpl = cfg.get("template", "split_header")
        if current_tpl not in tpl_keys:
            current_tpl = "split_header"

        selected_tpl = st.segmented_control(
            "Scegli Template",
            options=tpl_keys,
            format_func=lambda k: templates_meta.get(k, {}).get("name", k),
            default=current_tpl,
            label_visibility="collapsed"
        ) or current_tpl
        cfg["template"] = selected_tpl

        t_meta = templates_meta.get(selected_tpl, {})
        with st.container(border=True):
            st.markdown(f"**{t_meta.get('name', selected_tpl)}**")
            st.caption(t_meta.get('description', ''))

        st.space("small")
        st.subheader("2. Palette Colori")
        palette_keys = list(palettes.keys()) + ["personalizzata"]
        current_pal = cfg.get("palette", "vibrant_duo")
        if current_pal not in palette_keys:
            current_pal = "personalizzata"

        selected_pal = st.segmented_control(
            "Palette",
            options=palette_keys,
            format_func=lambda p: palettes.get(p, {}).get("name", "Personalizzata 🖌️"),
            default=current_pal,
            label_visibility="collapsed"
        ) or current_pal
        cfg["palette"] = selected_pal

        if selected_pal in palettes and selected_pal != "personalizzata":
            cfg["colors"].update(palettes[selected_pal]["colors"])

        with st.expander("Personalizza i singoli colori", icon=":material/colorize:"):
            c_cols = cfg["colors"]
            col1, col2, col3 = st.columns(3)
            with col1:
                c_cols["primary"] = st.color_picker("Titoli Principali", c_cols.get("primary", "#0F172A"))
                c_cols["accent"] = st.color_picker("Sottotitoli / Accento", c_cols.get("accent", "#7C3AED"))
                c_cols["left_bg"] = st.color_picker("Header Sinistra", c_cols.get("left_bg", "#6FE3FF"))
            with col2:
                c_cols["right_bg"] = st.color_picker("Header Destra", c_cols.get("right_bg", "#A380FF"))
                c_cols["text_main"] = st.color_picker("Testo", c_cols.get("text_main", "#1E293B"))
                c_cols["text_muted"] = st.color_picker("Testo Muted", c_cols.get("text_muted", "#475569"))
            with col3:
                c_cols["line_color"] = st.color_picker("Divisori", c_cols.get("line_color", "#CBD5E1"))
                c_cols["sidebar_bg"] = st.color_picker("Sfondo Sidebar", c_cols.get("sidebar_bg", "#0F172A"))
                c_cols["sidebar_accent"] = st.color_picker("Accento Sidebar", c_cols.get("sidebar_accent", "#38BDF8"))
            
            c_cols["primary_text"] = c_cols["primary"]
            c_cols["secondary_text"] = c_cols["text_main"]

        st.space("small")
        st.subheader("3. Budget Pagine & Densità (Anti-Overflow)")
        st.caption("Muovi questi slider per adattare il CV a 1 pagina esatta o espanderlo a 2.")

        sl_col1, sl_col2 = st.columns(2)
        with sl_col1:
            raw_font_size = float(cfg.get("font_size", "8.5pt").replace("pt", ""))
            new_font_size = st.slider("Dimensione Testo Base (pt)", min_value=7.0, max_value=10.5, value=raw_font_size, step=0.1)
            cfg["font_size"] = f"{new_font_size}pt"

            raw_spacing = float(cfg.get("section_spacing", "4.0pt").replace("pt", ""))
            new_spacing = st.slider("Spaziatura tra Sezioni (pt)", min_value=1.5, max_value=12.0, value=raw_spacing, step=0.5)
            cfg["section_spacing"] = f"{new_spacing}pt"

        with sl_col2:
            raw_leading = float(cfg.get("line_spacing", "0.46em").replace("em", ""))
            new_leading = st.slider("Interlinea / Leading (em)", min_value=0.38, max_value=0.62, value=raw_leading, step=0.01)
            cfg["line_spacing"] = f"{new_leading}em"

            raw_margin_y = float(cfg.get("margin_y", "1.0cm").replace("cm", ""))
            new_margin_y = st.slider("Margini Verticali (cm)", min_value=0.5, max_value=1.8, value=raw_margin_y, step=0.05)
            cfg["margin_y"] = f"{new_margin_y}cm"
            cfg["margin_bottom"] = f"{new_margin_y}cm"

        st.space("small")
        st.subheader("4. Opzioni Visive")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            cfg["font_family"] = st.selectbox(
                "Famiglia Font",
                ["Helvetica", "Arial", "Inter", "Roboto", "New Computer Modern"],
                index=["Helvetica", "Arial", "Inter", "Roboto", "New Computer Modern"].index(cfg.get("font_family", "Helvetica")) if cfg.get("font_family") in ["Helvetica", "Arial", "Inter", "Roboto", "New Computer Modern"] else 0
            )
        with t_col2:
            cfg["show_photo"] = st.toggle("Mostra Foto", value=cfg.get("show_photo", True))
        with t_col3:
            cfg["show_gdpr"] = st.toggle("Mostra GDPR", value=cfg.get("show_gdpr", True))

    # -------------------------------------------------------------
    # TAB 3: AUDIT ATS
    # -------------------------------------------------------------
    with tab_audit:
        st.subheader(":material/fact_check: Audit di Scansionabilità ATS")
        st.caption("Verifica la leggibilità del testo e la presenza dei segnali chiave ricercati dagli recruiter tech.")

        active_content = cv_data.get(active_lang, {})
        full_text = " ".join([
            active_content.get("profile", ""),
            " ".join([exp.get("description", "") + " ".join(exp.get("bullets", [])) for exp in active_content.get("experience", [])]),
            " ".join([sk.get("items", "") for sk in active_content.get("skills", [])]),
        ])

        metrics_found = re.findall(r'\b\d+(?:[\.,]\d+)?%?|\b\d+\b', full_text)
        
        ai_action_verbs = [
            "engineered", "implemented", "optimized", "benchmarked", "developed", 
            "designed", "accelerated", "slashed", "integrated", "architected",
            "implementate", "sviluppato", "ottimizzato", "progettato", "ridotto",
            "condotta", "erogati", "gestito"
        ]
        found_verbs = [v for v in ai_action_verbs if re.search(r'\b' + v + r'\b', full_text, re.IGNORECASE)]

        core_ai_keywords = [
            "pytorch", "diffusion", "latent", "caching", "inference", "latency",
            "cuda", "generative ai", "computer vision", "docker", "python",
            "hugging face", "scikit-learn", "agile", "deep learning"
        ]
        found_keywords = [kw for kw in core_ai_keywords if re.search(r'\b' + kw + r'\b', full_text, re.IGNORECASE)]

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Metriche Numeriche", f"{len(metrics_found)}", help="Percentuali, velocità o volumi misurati.")
        with m2:
            st.metric("Verbi d'Azione", f"{len(found_verbs)}/{len(ai_action_verbs)}")
        with m3:
            st.metric("Keyword Stack Presenti", f"{len(found_keywords)}/{len(core_ai_keywords)}")

        st.space("small")
        st.markdown("#### :material/stars: Keyword Tecniche Rilevate")
        kw_cols = st.columns(4)
        for i, kw in enumerate(core_ai_keywords):
            with kw_cols[i % 4]:
                if kw in found_keywords:
                    st.badge(kw.title(), icon=":material/check:", color="green")
                else:
                    st.badge(kw.title(), icon=":material/close:", color="gray")

        st.space("small")
        with st.container(border=True):
            st.markdown("#### :material/tips_and_updates: Consigli per Massimizzare le Interviste")
            st.write("1. **Formula STAR / XYZ**: Per ogni esperienza, descrivi *cosa hai realizzato [X]*, *come è stato misurato [Y]*, usando *quale tecnologia o approccio [Z]*.")
            st.write("2. **Evidenzia in Grassetto**: Metti in **grassetto** solo percentuali e tool critici per guidare l'occhio dell'HR nei primi 6 secondi di scansione.")
            st.write("3. **1 Pagina per < 5 anni di esperienza**: Regola lo slider della spaziatura per far stare tutto in una sola pagina densa e accattivante.")

# ==================== RIGHT PANEL: AUTO-COMPILE & LIVE PREVIEW ====================
with right_panel:
    # Auto-compile in-memory
    pdf_bytes, compile_err = compile_session_pdf(cv_data, lang=active_lang)
    page_count = count_pdf_pages(pdf_bytes)

    st.subheader(":material/visibility: Anteprima Live")

    badge_c1, badge_c2 = st.columns([2, 1], vertical_alignment="center")
    with badge_c1:
        if page_count == 1:
            st.badge("1 Pagina Perfetta", icon=":material/check_circle:", color="green")
        elif page_count == 2:
            st.badge("Layout su 2 Pagine", icon=":material/description:", color="blue")
        elif page_count > 2:
            st.badge(f"{page_count} Pagine (Attenzione Overflow)", icon=":material/warning:", color="red")
    with badge_c2:
        st.caption(f"Lingua: **{active_lang.upper()}**")

    if compile_err:
        st.error(f"Errore di compilazione Typst: {compile_err}")

    if pdf_bytes:
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        dl1, dl2 = st.columns([1.2, 1])
        with dl1:
            st.download_button(
                label=f"Scarica PDF ({active_lang.upper()})",
                data=pdf_bytes,
                file_name=f"CV_{cv_data.get('personal', {}).get('name', 'Curriculum').replace(' ', '_')}_{active_lang.upper()}.pdf",
                mime="application/pdf",
                type="primary",
                icon=":material/download:"
            )
        with dl2:
            st.download_button(
                label="Salva Dati (YAML)",
                data=yaml.dump(cv_data, allow_unicode=True, sort_keys=False),
                file_name=f"cv_{cv_data.get('personal', {}).get('name', 'profilo').replace(' ', '_').lower()}.yml",
                mime="text/yaml",
                icon=":material/save:"
            )

        pdf_html = f'''
        <iframe 
            src="data:application/pdf;base64,{b64_pdf}#toolbar=0&navpanes=0&scrollbar=1" 
            width="100%" 
            height="860px" 
            type="application/pdf"
            style="border: 1px solid #E2E8F0; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
        </iframe>
        '''
        st.markdown(pdf_html, unsafe_allow_html=True)
    else:
        st.info("Generazione anteprima in corso...")
