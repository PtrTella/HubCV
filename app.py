import streamlit as st
import yaml
import os
import re
import uuid
import base64

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

# ==================== MULTI-SESSION SETUP ====================
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:10]

if "data_version" not in st.session_state:
    st.session_state.data_version = 0

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

# Helper: Empty profile structure
def get_empty_profile():
    return {
        "config": {
            "template": "split_header",
            "palette": "vibrant_duo",
            "lang": "it",
            "font_family": "Helvetica",
            "font_size": "8.5pt",
            "line_spacing": "0.46em",
            "section_spacing": "4.0pt",
            "margin_x": "1.2cm",
            "margin_y": "0.8cm",
            "margin_bottom": "0.8cm",
            "show_photo": False,
            "show_gdpr": True,
            "colors": {}
        },
        "personal": {
            "name": "",
            "headline": {"it": "", "en": ""},
            "email": "",
            "phone": "",
            "github": "",
            "location": ""
        },
        "it": {
            "headings": {
                "profile": "PROFILO",
                "experience": "ESPERIENZE LAVORATIVE",
                "education": "ISTRUZIONE",
                "skills": "COMPETENZE TECNICHE",
                "projects": "PROGETTI SELEZIONATI",
                "languages": "LINGUE",
                "volunteer": "ASSOCIAZIONI E VOLONTARIATO"
            },
            "profile": "",
            "experience": [],
            "education": [],
            "skills": [],
            "projects": [],
            "languages": [],
            "volunteer": "",
            "footer": "Autorizzo il trattamento dei miei dati personali ai sensi del Regolamento UE 2016/679 (GDPR)."
        },
        "en": {
            "headings": {
                "profile": "PROFESSIONAL SUMMARY",
                "experience": "WORK EXPERIENCE",
                "education": "EDUCATION",
                "skills": "TECHNICAL SKILLS",
                "projects": "SELECTED PROJECTS",
                "languages": "LANGUAGES",
                "volunteer": "LEADERSHIP & VOLUNTEERING"
            },
            "profile": "",
            "experience": [],
            "education": [],
            "skills": [],
            "projects": [],
            "languages": [],
            "volunteer": "",
            "footer": "I hereby authorize the processing of my personal data pursuant to EU Regulation 2016/679 (GDPR)."
        }
    }

# Initialize Session Data from Master cv.yml or blank
if "cv_data" not in st.session_state:
    if os.path.exists(session_yaml_abs):
        st.session_state.cv_data = load_yaml_file(session_yaml_abs)
    elif os.path.exists("data/cv.yml"):
        st.session_state.cv_data = load_yaml_file("data/cv.yml")
    else:
        st.session_state.cv_data = get_empty_profile()

cv_data = st.session_state.cv_data
ver = st.session_state.data_version

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
cfg.setdefault("show_photo", False)
cfg.setdefault("show_gdpr", True)
cfg.setdefault("colors", {})

# In-memory compiler
def compile_session_pdf(data_dict, lang=None):
    if not HAS_TYPST:
        return None, "Compilatore Typst non trovato."
    
    active_dict = dict(data_dict)
    if lang:
        active_dict["config"] = dict(data_dict.get("config", {}))
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

# ==================== TOP BAR ====================
top_col1, top_col2, top_col3 = st.columns([2.3, 1.2, 1.5], vertical_alignment="center")

with top_col1:
    st.markdown("### :material/badge: HubCV Studio")
    st.caption("Crea, compila e scarica il tuo CV professionale bilingue in Typst.")

with top_col2:
    active_lang = st.segmented_control(
        "Lingua anteprima",
        options=["it", "en"],
        format_func=lambda x: "Italiano 🇮🇹" if x == "it" else "English 🇬🇧",
        default=cfg.get("lang", "it"),
        label_visibility="collapsed",
        key=f"lang_sel_v{ver}"
    ) or cfg.get("lang", "it")
    cfg["lang"] = active_lang

with top_col3:
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("Svuota Dati", icon=":material/clear_all:"):
            st.session_state.cv_data = get_empty_profile()
            st.session_state.data_version += 1
            st.toast("Tutti i campi sono stati svuotati!", icon=":material/refresh:")
            st.rerun()
    with c_btn2:
        if st.button("Esporta IT+EN", icon=":material/folder_zip:"):
            pdf_it, _ = compile_session_pdf(cv_data, lang="it")
            pdf_en, _ = compile_session_pdf(cv_data, lang="en")
            if pdf_it and pdf_en:
                st.download_button("Scarica IT 🇮🇹", data=pdf_it, file_name="CV_Italiano.pdf", mime="application/pdf", key="dl_it")
                st.download_button("Scarica EN 🇬🇧", data=pdf_en, file_name="CV_English.pdf", mime="application/pdf", key="dl_en")
                st.toast("PDF IT ed EN generati!", icon=":material/done_all:")

st.space("small")

# ==================== MAIN WORKSPACE ====================
left_panel, right_panel = st.columns([1.18, 0.82], gap="large")

with left_panel:
    # Prominent YAML Drag & Drop Uploader Box
    with st.container(border=True):
        u_col1, u_col2 = st.columns([3, 1], vertical_alignment="center")
        with u_col1:
            st.markdown("**:material/upload_file: Carica il tuo Profilo YAML**")
            st.caption("Trascina qui il tuo file `.yml` salvato in precedenza per compilare tutti i dati all'istante.")
        with u_col2:
            st.badge("Auto-Fill Istantaneo", color="blue")

        uploaded_yaml = st.file_uploader(
            "Carica file .yml",
            type=["yml", "yaml"],
            label_visibility="collapsed",
            key=f"yaml_drop_{ver}"
        )
        if uploaded_yaml is not None:
            try:
                raw_bytes = uploaded_yaml.read()
                parsed = yaml.safe_load(raw_bytes.decode("utf-8"))
                if isinstance(parsed, dict) and ("it" in parsed or "en" in parsed or "personal" in parsed):
                    st.session_state.cv_data = parsed
                    # Increment data_version to force Streamlit to recreate all widgets with the new data
                    st.session_state.data_version += 1
                    save_yaml_file(session_yaml_abs, parsed)
                    st.toast("Profilo caricato con successo! Tutti i campi aggiornati.", icon=":material/check_circle:")
                    st.rerun()
                else:
                    st.error("Il file caricato non sembra contenere la struttura valida di un profilo CV.")
            except Exception as e:
                st.error(f"Errore lettura file: {e}")

    tab_content, tab_style, tab_audit = st.tabs([
        ":material/person: I Miei Dati & Esperienze",
        ":material/palette: Stile, Template & Layout",
        ":material/fact_check: Audit ATS & Scansionabilità"
    ])

    # -------------------------------------------------------------
    # TAB 1: I MIEI DATI & ESPERIENZE
    # -------------------------------------------------------------
    with tab_content:
        edit_lang = st.segmented_control(
            "Lingua in modifica",
            options=["it", "en"],
            format_func=lambda x: "Modifica Italiano 🇮🇹" if x == "it" else "Edit English 🇬🇧",
            default=active_lang,
            label_visibility="collapsed",
            key=f"edit_lang_sel_v{ver}"
        ) or active_lang

        lang_data = cv_data.setdefault(edit_lang, {})
        lang_data.setdefault("headings", {})

        # Dati Personali
        with st.expander("👤 Informazioni Personali & Contatti", expanded=True):
            p = cv_data.setdefault("personal", {})
            p1, p2 = st.columns(2)
            with p1:
                p["name"] = st.text_input("Nome e Cognome", value=p.get("name", ""), key=f"p_name_v{ver}")
                p["email"] = st.text_input("Email", value=p.get("email", ""), key=f"p_mail_v{ver}")
                p["phone"] = st.text_input("Telefono", value=p.get("phone", ""), key=f"p_tel_v{ver}")
            with p2:
                cur_hl = p.get("headline", {})
                if isinstance(cur_hl, dict):
                    hl_val = cur_hl.get(edit_lang, "")
                    hl_input = st.text_input("Titolo Professionale (es. AI Engineer)", value=hl_val, key=f"p_hl_v{ver}")
                    cur_hl[edit_lang] = hl_input
                    p["headline"] = cur_hl
                else:
                    hl_input = st.text_input("Titolo Professionale", value=str(cur_hl), key=f"p_hl_v{ver}")
                    p["headline"] = {edit_lang: hl_input}
                p["github"] = st.text_input("GitHub / Portfolio (senza https://)", value=p.get("github", ""), key=f"p_gh_v{ver}")
                p["location"] = st.text_input("Località (Città, Paese)", value=p.get("location", ""), key=f"p_loc_v{ver}")

            # Foto Profilo Personale
            st.space("small")
            photo_file = st.file_uploader("Carica la tua Foto Profilo (PNG / JPG)", type=["png", "jpg", "jpeg"], key=f"photo_up_v{ver}")
            if photo_file is not None:
                custom_photo_path = os.path.join(session_dir, "photo.png")
                with open(custom_photo_path, "wb") as f_img:
                    f_img.write(photo_file.read())
                cfg["photo_path"] = f"/data/sessions/{session_id}/photo.png"
                cfg["show_photo"] = True
                st.toast("Foto profilo caricata e attivata!", icon=":material/image:")

        # Profilo Professionale
        with st.expander(f"📝 Profilo Professionale & Bio ({edit_lang.upper()})", expanded=True):
            lang_data["headings"]["profile"] = st.text_input("Titolo Sezione", value=lang_data["headings"].get("profile", "PROFILO"), key=f"h_prof_v{ver}")
            lang_data["profile"] = st.text_area("Testo del Profilo", value=lang_data.get("profile", ""), height=100, key=f"txt_prof_v{ver}")

        # Esperienze Lavorative
        with st.expander(f"💼 Esperienze Lavorative ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["experience"] = st.text_input("Titolo Sezione", value=lang_data["headings"].get("experience", "ESPERIENZE LAVORATIVE"), key=f"h_exp_v{ver}")
            exps = lang_data.setdefault("experience", [])

            for i, exp in enumerate(exps):
                with st.container(border=True):
                    exp_top1, exp_top2 = st.columns([4, 1])
                    with exp_top1:
                        st.markdown(f"**Esperienza #{i+1}: {exp.get('role', 'Ruolo')}**")
                    with exp_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_exp_{edit_lang}_{i}_v{ver}"):
                            exps.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()

                    c_r1, c_r2 = st.columns([2, 1])
                    with c_r1:
                        exp["role"] = st.text_input("Ruolo", value=exp.get("role", ""), key=f"exp_r_{edit_lang}_{i}_v{ver}")
                        exp["company"] = st.text_input("Azienda / Ente", value=exp.get("company", ""), key=f"exp_c_{edit_lang}_{i}_v{ver}")
                    with c_r2:
                        exp["period"] = st.text_input("Periodo (es. 2024 - Presente)", value=exp.get("period", ""), key=f"exp_p_{edit_lang}_{i}_v{ver}")

                    bullets = exp.get("bullets", [])
                    bullets_text = "\n".join(bullets) if isinstance(bullets, list) and bullets else exp.get("description", "")
                    new_bullets_text = st.text_area(
                        "Bullet points (uno per riga. Usa il **grassetto** per mettere in risalto numeri e tool)",
                        value=bullets_text,
                        height=90,
                        key=f"exp_b_{edit_lang}_{i}_v{ver}"
                    )
                    exp["bullets"] = [b.strip() for b in new_bullets_text.split("\n") if b.strip()]
                    exp["description"] = " ".join(exp["bullets"])

            if st.button("+ Aggiungi Nuova Esperienza", icon=":material/add:", key=f"add_exp_btn_v{ver}"):
                exps.append({
                    "role": "Nuovo Ruolo",
                    "company": "Azienda / Startup",
                    "period": "2025 - Presente",
                    "description": "",
                    "bullets": ["Descrivi l'obiettivo raggiunto, il metodo usato e l'impatto numerico."]
                })
                st.session_state.data_version += 1
                st.rerun()

        # Istruzione
        with st.expander(f"🎓 Istruzione & Titoli Accademici ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["education"] = st.text_input("Titolo Sezione", value=lang_data["headings"].get("education", "ISTRUZIONE"), key=f"h_edu_v{ver}")
            edus = lang_data.setdefault("education", [])
            for i, edu in enumerate(edus):
                with st.container(border=True):
                    ed_top1, ed_top2 = st.columns([4, 1])
                    with ed_top1:
                        st.markdown(f"**Titolo #{i+1}: {edu.get('degree', '')}**")
                    with ed_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_edu_{edit_lang}_{i}_v{ver}"):
                            edus.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()

                    ed_c1, ed_c2 = st.columns([2, 1])
                    with ed_c1:
                        edu["degree"] = st.text_input("Titolo di Studio", value=edu.get("degree", ""), key=f"ed_d_{edit_lang}_{i}_v{ver}")
                        edu["institution"] = st.text_input("Università / Ente", value=edu.get("institution", ""), key=f"ed_inst_{edit_lang}_{i}_v{ver}")
                    with ed_c2:
                        edu["period"] = st.text_input("Periodo (es. 2020 - 2023)", value=edu.get("period", ""), key=f"ed_p_{edit_lang}_{i}_v{ver}")
                    edu["details"] = st.text_input("Dettagli / Tesi", value=edu.get("details", ""), key=f"ed_det_{edit_lang}_{i}_v{ver}")

            if st.button("+ Aggiungi Titolo di Studio", icon=":material/add:", key=f"add_edu_btn_v{ver}"):
                edus.append({
                    "degree": "Nuovo Titolo",
                    "institution": "Università",
                    "period": "2025",
                    "details": ""
                })
                st.session_state.data_version += 1
                st.rerun()

        # Competenze Tecniche
        with st.expander(f"💻 Competenze Tecniche ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["skills"] = st.text_input("Titolo Sezione", value=lang_data["headings"].get("skills", "COMPETENZE TECNICHE"), key=f"h_sk_v{ver}")
            sks = lang_data.setdefault("skills", [])
            for i, sk in enumerate(sks):
                with st.container(border=True):
                    sk_top1, sk_top2 = st.columns([4, 1])
                    with sk_top1:
                        st.markdown(f"**Categoria #{i+1}: {sk.get('category', '')}**")
                    with sk_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_sk_{edit_lang}_{i}_v{ver}"):
                            sks.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()
                    sc1, sc2 = st.columns([1, 2])
                    with sc1:
                        sk["category"] = st.text_input("Nome Categoria", value=sk.get("category", ""), key=f"sk_c_{edit_lang}_{i}_v{ver}")
                    with sc2:
                        sk["items"] = st.text_input("Tecnologie (separate da virgola)", value=sk.get("items", ""), key=f"sk_it_{edit_lang}_{i}_v{ver}")

            if st.button("+ Aggiungi Categoria Competenze", icon=":material/add:", key=f"add_sk_btn_v{ver}"):
                sks.append({"category": "Nuova Categoria", "items": "Tool 1, Tool 2, Tool 3"})
                st.session_state.data_version += 1
                st.rerun()

        # Progetti Selezionati
        with st.expander(f"🚀 Progetti Selezionati ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["projects"] = st.text_input("Titolo Sezione", value=lang_data["headings"].get("projects", "PROGETTI SELEZIONATI"), key=f"h_pr_v{ver}")
            projs = lang_data.setdefault("projects", [])
            for i, proj in enumerate(projs):
                with st.container(border=True):
                    p_top1, p_top2 = st.columns([4, 1])
                    with p_top1:
                        st.markdown(f"**Progetto #{i+1}: {proj.get('name', '')}**")
                    with p_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_pr_{edit_lang}_{i}_v{ver}"):
                            projs.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()
                    pr1, pr2 = st.columns([2, 1])
                    with pr1:
                        proj["name"] = st.text_input("Nome Progetto", value=proj.get("name", ""), key=f"pr_n_{edit_lang}_{i}_v{ver}")
                        proj["tech"] = st.text_input("Tecnologie usate", value=proj.get("tech", ""), key=f"pr_t_{edit_lang}_{i}_v{ver}")
                    with pr2:
                        proj["link"] = st.text_input("Link (GitHub / Demo)", value=proj.get("link", ""), key=f"pr_l_{edit_lang}_{i}_v{ver}")
                    proj["description"] = st.text_area("Descrizione sintetica", value=proj.get("description", ""), height=55, key=f"pr_d_{edit_lang}_{i}_v{ver}")

            if st.button("+ Aggiungi Progetto", icon=":material/add:", key=f"add_pr_btn_v{ver}"):
                projs.append({
                    "name": "Nuovo Progetto",
                    "tech": "Python, Docker",
                    "link": "github.com",
                    "description": "Breve descrizione del risultato ottenuto."
                })
                st.session_state.data_version += 1
                st.rerun()

        # Lingue & Volontariato
        with st.expander(f"🌐 Lingue, Volontariato & Privacy ({edit_lang.upper()})", expanded=False):
            lang_data["headings"]["languages"] = st.text_input("Titolo Lingue", value=lang_data["headings"].get("languages", "LINGUE"), key=f"h_lang_v{ver}")
            for i, l in enumerate(lang_data.setdefault("languages", [])):
                lc1, lc2 = st.columns(2)
                with lc1:
                    l["lang"] = st.text_input(f"Lingua #{i+1}", value=l.get("lang", ""), key=f"l_n_{edit_lang}_{i}_v{ver}")
                with lc2:
                    l["level"] = st.text_input(f"Livello #{i+1}", value=l.get("level", ""), key=f"l_v_{edit_lang}_{i}_v{ver}")

            st.space("small")
            lang_data["headings"]["volunteer"] = st.text_input("Titolo Volontariato", value=lang_data["headings"].get("volunteer", "ASSOCIAZIONI E VOLONTARIATO"), key=f"h_vol_v{ver}")
            lang_data["volunteer"] = st.text_area("Attività extra / Volontariato", value=lang_data.get("volunteer", ""), height=65, key=f"txt_vol_v{ver}")

            st.space("small")
            lang_data["footer"] = st.text_area("Clausola GDPR / Privacy", value=lang_data.get("footer", ""), height=50, key=f"txt_gdpr_v{ver}")

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
            label_visibility="collapsed",
            key=f"tpl_sel_v{ver}"
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
            label_visibility="collapsed",
            key=f"pal_sel_v{ver}"
        ) or current_pal
        cfg["palette"] = selected_pal

        if selected_pal in palettes and selected_pal != "personalizzata":
            cfg["colors"].update(palettes[selected_pal]["colors"])

        with st.expander("Personalizza i singoli colori", icon=":material/colorize:"):
            c_cols = cfg["colors"]
            col1, col2, col3 = st.columns(3)
            with col1:
                c_cols["primary"] = st.color_picker("Titoli Principali", c_cols.get("primary", "#0F172A"), key=f"c_p_v{ver}")
                c_cols["accent"] = st.color_picker("Sottotitoli / Accento", c_cols.get("accent", "#7C3AED"), key=f"c_a_v{ver}")
                c_cols["left_bg"] = st.color_picker("Header Sinistra", c_cols.get("left_bg", "#6FE3FF"), key=f"c_lb_v{ver}")
            with col2:
                c_cols["right_bg"] = st.color_picker("Header Destra", c_cols.get("right_bg", "#A380FF"), key=f"c_rb_v{ver}")
                c_cols["text_main"] = st.color_picker("Testo", c_cols.get("text_main", "#1E293B"), key=f"c_tm_v{ver}")
                c_cols["text_muted"] = st.color_picker("Testo Muted", c_cols.get("text_muted", "#475569"), key=f"c_mu_v{ver}")
            with col3:
                c_cols["line_color"] = st.color_picker("Divisori", c_cols.get("line_color", "#CBD5E1"), key=f"c_ln_v{ver}")
                c_cols["sidebar_bg"] = st.color_picker("Sfondo Sidebar", c_cols.get("sidebar_bg", "#0F172A"), key=f"c_sb_v{ver}")
                c_cols["sidebar_accent"] = st.color_picker("Accento Sidebar", c_cols.get("sidebar_accent", "#38BDF8"), key=f"c_sa_v{ver}")
            
            c_cols["primary_text"] = c_cols["primary"]
            c_cols["secondary_text"] = c_cols["text_main"]

        st.space("small")
        st.subheader("3. Budget Pagine & Densità (Anti-Overflow)")
        st.caption("Muovi questi slider per adattare il CV a 1 pagina esatta o espanderlo a 2.")

        sl_col1, sl_col2 = st.columns(2)
        with sl_col1:
            raw_font_size = float(cfg.get("font_size", "8.5pt").replace("pt", ""))
            new_font_size = st.slider("Dimensione Testo Base (pt)", min_value=7.0, max_value=10.5, value=raw_font_size, step=0.1, key=f"sl_fs_v{ver}")
            cfg["font_size"] = f"{new_font_size}pt"

            raw_spacing = float(cfg.get("section_spacing", "4.0pt").replace("pt", ""))
            new_spacing = st.slider("Spaziatura tra Sezioni (pt)", min_value=1.5, max_value=12.0, value=raw_spacing, step=0.5, key=f"sl_ss_v{ver}")
            cfg["section_spacing"] = f"{new_spacing}pt"

        with sl_col2:
            raw_leading = float(cfg.get("line_spacing", "0.46em").replace("em", ""))
            new_leading = st.slider("Interlinea / Leading (em)", min_value=0.38, max_value=0.62, value=raw_leading, step=0.01, key=f"sl_ls_v{ver}")
            cfg["line_spacing"] = f"{new_leading}em"

            raw_margin_y = float(cfg.get("margin_y", "1.0cm").replace("cm", ""))
            new_margin_y = st.slider("Margini Verticali (cm)", min_value=0.5, max_value=1.8, value=raw_margin_y, step=0.05, key=f"sl_my_v{ver}")
            cfg["margin_y"] = f"{new_margin_y}cm"
            cfg["margin_bottom"] = f"{new_margin_y}cm"

        st.space("small")
        st.subheader("4. Opzioni Visive")
        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            cfg["font_family"] = st.selectbox(
                "Famiglia Font",
                ["Helvetica", "Arial", "Inter", "Roboto", "New Computer Modern"],
                index=["Helvetica", "Arial", "Inter", "Roboto", "New Computer Modern"].index(cfg.get("font_family", "Helvetica")) if cfg.get("font_family") in ["Helvetica", "Arial", "Inter", "Roboto", "New Computer Modern"] else 0,
                key=f"sel_ff_v{ver}"
            )
        with t_col2:
            cfg["show_photo"] = st.toggle("Mostra Foto", value=cfg.get("show_photo", False), key=f"tog_ph_v{ver}")
        with t_col3:
            cfg["show_gdpr"] = st.toggle("Mostra GDPR", value=cfg.get("show_gdpr", True), key=f"tog_gdpr_v{ver}")

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

# ==================== RIGHT PANEL: AUTO-COMPILE & LIVE PREVIEW ====================
with right_panel:
    # Check if profile has minimal content
    has_content = bool(cv_data.get("personal", {}).get("name") or cv_data.get(active_lang, {}).get("experience"))

    pdf_bytes, compile_err = compile_session_pdf(cv_data, lang=active_lang)
    page_count = count_pdf_pages(pdf_bytes)

    st.subheader(":material/visibility: Anteprima Live")

    badge_c1, badge_c2 = st.columns([2, 1], vertical_alignment="center")
    with badge_c1:
        if not has_content:
            st.badge("Profilo Vuoto", icon=":material/edit:", color="gray")
        elif page_count == 1:
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

        name_slug = cv_data.get("personal", {}).get("name", "").strip().replace(" ", "_") or "Curriculum"
        dl1, dl2 = st.columns([1.2, 1])
        with dl1:
            st.download_button(
                label=f"Scarica PDF ({active_lang.upper()})",
                data=pdf_bytes,
                file_name=f"CV_{name_slug}_{active_lang.upper()}.pdf",
                mime="application/pdf",
                type="primary",
                icon=":material/download:"
            )
        with dl2:
            st.download_button(
                label="Salva Dati (YAML)",
                data=yaml.dump(cv_data, allow_unicode=True, sort_keys=False),
                file_name=f"cv_{name_slug.lower()}.yml",
                mime="text/yaml",
                icon=":material/save:"
            )

        if not has_content:
            st.info("💡 Il profilo è attualmente vuoto. Trascina il tuo file YAML a sinistra oppure inizia a inserire i tuoi dati per vedere il CV popolato!")

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
