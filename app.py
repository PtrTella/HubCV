import streamlit as st
import yaml
import os
import re
import uuid
import base64
import copy
import io
import zipfile

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

# Custom CSS for polished, orderly modern UI
st.markdown("""
<style>
    /* Remove excess top padding in Streamlit */
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }
    /* Sleek card styling */
    div[data-testid="stExpander"] {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 0.6rem;
    }
    /* Make segmented controls clean */
    div[data-testid="stSegmentedControl"] {
        margin-bottom: 0.2rem;
    }
    /* Compact buttons in item headers */
    .stButton button {
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

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

# ==================== LANGUAGE DEFINITIONS & HEADINGS ====================
LANG_META = {
    "it": {"name": "Italiano", "flag": "🇮🇹"},
    "en": {"name": "English", "flag": "🇬🇧"},
    "fr": {"name": "Français", "flag": "🇫🇷"},
    "de": {"name": "Deutsch", "flag": "🇩🇪"},
    "es": {"name": "Español", "flag": "🇪🇸"},
    "pt": {"name": "Português", "flag": "🇵🇹"},
}

def get_lang_label(code):
    meta = LANG_META.get(code)
    if meta:
        return f"{meta['flag']} {meta['name']} ({code.upper()})"
    return f"🌐 {code.upper()}"

def get_default_headings(lang_code):
    headings_map = {
        "it": {
            "profile": "PROFILO",
            "experience": "ESPERIENZE LAVORATIVE",
            "education": "ISTRUZIONE",
            "skills": "COMPETENZE TECNICHE",
            "projects": "PROGETTI SELEZIONATI",
            "languages": "COMPETENZE LINGUISTICHE",
            "volunteer": "ASSOCIAZIONI E VOLONTARIATO"
        },
        "en": {
            "profile": "PROFESSIONAL SUMMARY",
            "experience": "WORK EXPERIENCE",
            "education": "EDUCATION",
            "skills": "TECHNICAL SKILLS",
            "projects": "SELECTED PROJECTS",
            "languages": "LANGUAGES",
            "volunteer": "LEADERSHIP & VOLUNTEERING"
        },
        "fr": {
            "profile": "PROFIL PROFESSIONNEL",
            "experience": "EXPÉRIENCE PROFESSIONNELLE",
            "education": "FORMATION & DIPLÔMES",
            "skills": "COMPÉTENCES TECHNIQUES",
            "projects": "PROJETS RÉALISÉS",
            "languages": "LANGUES",
            "volunteer": "ENGAGEMENT & BÉNÉVOLAT"
        },
        "de": {
            "profile": "KURZPROFIL",
            "experience": "BERUFSERFAHRUNG",
            "education": "AUSBILDUNG & STUDIUM",
            "skills": "FACHKENNTNISSE",
            "projects": "PROJEKTE",
            "languages": "SPRACHKENNTNISSE",
            "volunteer": "ENGAGEMENT"
        },
        "es": {
            "profile": "PERFIL PROFESIONAL",
            "experience": "EXPERIENCIA LABORAL",
            "education": "EDUCACIÓN Y FORMACIÓN",
            "skills": "COMPETENCIAS TÉCNICAS",
            "projects": "PROYECTOS DESTACADOS",
            "languages": "IDIOMAS",
            "volunteer": "VOLUNTARIADO Y LIDERAZGO"
        }
    }
    return headings_map.get(lang_code, headings_map["en"])

def get_default_footer(lang_code):
    footer_map = {
        "it": "Autorizzo il trattamento dei miei dati personali ai sensi del Regolamento UE 2016/679 (GDPR).",
        "en": "I hereby authorize the processing of my personal data pursuant to EU Regulation 2016/679 (GDPR).",
        "fr": "J'autorise le traitement de mes données personnelles conformément au RGPD (Règlement UE 2016/679).",
        "de": "Ich willige in die Verarbeitung meiner personenbezogenen Daten gemäß DSGVO ein.",
        "es": "Autorizo el tratamiento de mis datos personales de conformidad con el RGPD (Reglamento UE 2016/679)."
    }
    return footer_map.get(lang_code, footer_map["en"])

def create_empty_language_block(lang_code):
    return {
        "headings": get_default_headings(lang_code),
        "profile": "",
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "languages": [],
        "volunteer": "",
        "footer": get_default_footer(lang_code)
    }

def get_available_languages(data):
    langs = [k for k, v in data.items() if isinstance(v, dict) and k not in ("config", "personal")]
    return langs if langs else ["it"]

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
            "margin_y": "0.9cm",
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
        "it": create_empty_language_block("it"),
        "en": create_empty_language_block("en")
    }

def sanitize_config(cfg):
    """Normalize config parameters from imported YAML to prevent cramped or tiny rendering."""
    if not isinstance(cfg, dict):
        cfg = {}
    
    # Sanitize font size: if font size is ant-sized (< 7.8pt), gently boost to readable default
    font_size_str = cfg.get("font_size", "8.5pt")
    try:
        val = float(str(font_size_str).replace("pt", "").strip())
        if val < 7.8:
            cfg["font_size"] = "8.4pt"
    except Exception:
        cfg["font_size"] = "8.5pt"

    # Sanitize section spacing: avoid crushed headings
    spacing_str = cfg.get("section_spacing", "4.0pt")
    try:
        val = float(str(spacing_str).replace("pt", "").strip())
        if val < 3.0:
            cfg["section_spacing"] = "3.8pt"
    except Exception:
        cfg["section_spacing"] = "4.0pt"

    # Margins
    cfg.setdefault("template", "split_header")
    cfg.setdefault("palette", "vibrant_duo")
    cfg.setdefault("line_spacing", "0.46em")
    cfg.setdefault("margin_y", "0.9cm")
    cfg.setdefault("margin_bottom", "0.8cm")
    cfg.setdefault("margin_x", "1.2cm")
    cfg.setdefault("show_photo", False)
    cfg.setdefault("show_gdpr", True)
    cfg.setdefault("font_family", "Helvetica")
    cfg.setdefault("colors", {})
    return cfg

def load_yaml_file(path, default=None):
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or (default or {})
    except Exception:
        return default or {}

def save_yaml_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

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

# Sanitize config
cfg = sanitize_config(cv_data.setdefault("config", {}))

EMOJI_REGEX = re.compile(
    '['
    '\U00010000-\U0010ffff'
    '\u2600-\u27bf'
    '\u2300-\u23ff'
    '\u2b50'
    ']+',
    flags=re.UNICODE
)

def strip_emojis(data):
    if isinstance(data, str):
        return EMOJI_REGEX.sub('', data).strip()
    elif isinstance(data, list):
        return [strip_emojis(x) for x in data]
    elif isinstance(data, dict):
        return {k: strip_emojis(v) for k, v in data.items()}
    return data

# In-memory compiler
def compile_session_pdf(data_dict, lang=None):
    if not HAS_TYPST:
        return None, "Compilatore Typst non trovato."
    
    active_dict = copy.deepcopy(data_dict)
    active_cfg = active_dict.setdefault("config", {})
    if lang:
        active_cfg["lang"] = lang
    
    # Clean emojis to eliminate Type 3 bitmap fonts and ensure 100% vector ATS parseability
    ats_clean_dict = strip_emojis(active_dict)
    save_yaml_file(session_yaml_abs, ats_clean_dict)
    try:
        pdf_bytes = typst.compile(
            "src/cv.typ",
            root=".",
            sys_inputs={"data_path": session_yaml_rel},
            pdf_standards=["1.7"]
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

# Available languages list
avail_langs = get_available_languages(cv_data)
active_preview_lang = cfg.get("lang", avail_langs[0])
if active_preview_lang not in avail_langs:
    active_preview_lang = avail_langs[0]
    cfg["lang"] = active_preview_lang

# ==================== TOP NAVIGATION BAR ====================
top_col_brand, top_col_actions = st.columns([1.6, 1.4], vertical_alignment="center")

with top_col_brand:
    t_row1, t_row2 = st.columns([auto, auto] if False else [1, 10], vertical_alignment="center")
    st.markdown("### 📄 HubCV Studio")
    st.caption("Crea, compila e scarica il tuo CV professionale bilingue e multilingua con Typst.")

with top_col_actions:
    act1, act2, act3 = st.columns(3, gap="small", vertical_alignment="center")
    
    with act1:
        with st.popover("Carica YAML", icon=":material/upload_file:", use_container_width=True):
            st.markdown("##### 📥 Importa Profilo")
            st.caption("Trascina qui il tuo file `.yml` esportato in precedenza per compilare all'istante tutte le lingue.")
            up_yaml = st.file_uploader("Seleziona YAML", type=["yml", "yaml"], label_visibility="collapsed", key=f"up_yaml_{ver}")
            if up_yaml is not None:
                try:
                    raw_bytes = up_yaml.read()
                    parsed = yaml.safe_load(raw_bytes.decode("utf-8"))
                    if isinstance(parsed, dict) and any(k for k in parsed if k not in ("config", "personal")):
                        # Sanitize incoming config to prevent tiny font/bad spacing bugs
                        if "config" in parsed:
                            parsed["config"] = sanitize_config(parsed["config"])
                        st.session_state.cv_data = parsed
                        st.session_state.data_version += 1
                        save_yaml_file(session_yaml_abs, parsed)
                        st.toast("Profilo caricato con successo!", icon=":material/check_circle:")
                        st.rerun()
                    else:
                        st.error("Il file caricato non sembra contenere un profilo CV valido.")
                except Exception as e:
                    st.error(f"Errore lettura file: {e}")

    with act2:
        name_clean = cv_data.get("personal", {}).get("name", "").strip().lower().replace(" ", "_") or "curriculum"
        yaml_payload = yaml.dump(cv_data, allow_unicode=True, sort_keys=False)
        st.download_button(
            "Salva YAML",
            data=yaml_payload,
            file_name=f"cv_{name_clean}.yml",
            mime="text/yaml",
            icon=":material/save:",
            use_container_width=True
        )

    with act3:
        with st.popover("Nuovo / Reset", icon=":material/refresh:", use_container_width=True):
            st.markdown("##### ⚠️ Svuotare tutti i campi?")
            st.caption("Reimposta il CV a un modello pulito e vuoto. Tutti i dati correnti non salvati andranno persi.")
            if st.button("Sì, svuota tutto", type="primary", use_container_width=True, key=f"confirm_reset_{ver}"):
                st.session_state.cv_data = get_empty_profile()
                st.session_state.data_version += 1
                save_yaml_file(session_yaml_abs, st.session_state.cv_data)
                st.toast("CV reimpostato a modello vuoto!", icon=":material/refresh:")
                st.rerun()

st.space("small")

# ==================== MAIN WORKSPACE ====================
left_panel, right_panel = st.columns([1.18, 0.82], gap="large")

with left_panel:
    tab_content, tab_style, tab_audit = st.tabs([
        "📝 Profilo & Contenuti",
        "🎨 Stile & Layout",
        "📊 Audit ATS & Scansionabilità"
    ])

    # -------------------------------------------------------------
    # TAB 1: PROFILO & CONTENUTI (MULTILINGUA DINAMICO)
    # -------------------------------------------------------------
    with tab_content:
        # Multilingual toolbar
        lang_bar1, lang_bar2 = st.columns([3.2, 1.3], vertical_alignment="center")
        
        with lang_bar1:
            edit_lang = st.segmented_control(
                "Lingua in Modifica",
                options=avail_langs,
                format_func=get_lang_label,
                default=active_preview_lang if active_preview_lang in avail_langs else avail_langs[0],
                label_visibility="collapsed",
                key=f"edit_lang_sel_{ver}"
            ) or avail_langs[0]

        with lang_bar2:
            with st.popover("+ Aggiungi Lingua", icon=":material/language:"):
                st.markdown("##### 🌐 Nuova Lingua")
                new_lang_choice = st.selectbox(
                    "Seleziona Lingua",
                    options=["fr", "de", "es", "pt", "custom"],
                    format_func=lambda x: f"{LANG_META.get(x, {}).get('flag', '🌐')} {LANG_META.get(x, {}).get('name', 'Personalizzata')} ({x.upper()})" if x != "custom" else "Altra lingua (codice ISO)"
                )
                if new_lang_choice == "custom":
                    custom_code = st.text_input("Codice ISO (es. nl, pl, ro)", max_chars=3).lower().strip()
                    target_code = custom_code
                else:
                    target_code = new_lang_choice

                clone_source = st.selectbox(
                    "Copia contenuti da:",
                    options=["Modello vuoto"] + avail_langs,
                    index=1 if avail_langs else 0
                )

                if st.button("Aggiungi al Profilo", type="primary", use_container_width=True):
                    if target_code and target_code not in cv_data:
                        if clone_source != "Modello vuoto":
                            cv_data[target_code] = copy.deepcopy(cv_data[clone_source])
                            cv_data[target_code]["headings"] = get_default_headings(target_code)
                            cv_data[target_code]["footer"] = get_default_footer(target_code)
                        else:
                            cv_data[target_code] = create_empty_language_block(target_code)
                        st.session_state.cv_data = cv_data
                        st.session_state.data_version += 1
                        st.toast(f"Lingua {target_code.upper()} aggiunta!", icon=":material/check_circle:")
                        st.rerun()
                    elif target_code in cv_data:
                        st.warning("Questa lingua è già presente nel profilo.")

        # Ensure active edit language dictionary exists
        lang_data = cv_data.setdefault(edit_lang, create_empty_language_block(edit_lang))
        lang_headings = lang_data.setdefault("headings", get_default_headings(edit_lang))

        # Optional: remove language if more than 1
        if len(avail_langs) > 1:
            with st.expander(f"⚙️ Opzioni Lingua: {edit_lang.upper()}", expanded=False):
                del_c1, del_c2 = st.columns([3, 1])
                with del_c1:
                    st.caption(f"Elimina la lingua **{get_lang_label(edit_lang)}** e tutti i suoi testi.")
                with del_c2:
                    if st.button("Rimuovi Lingua", icon=":material/delete:", key=f"del_lang_{edit_lang}_{ver}"):
                        del cv_data[edit_lang]
                        st.session_state.data_version += 1
                        st.toast(f"Lingua {edit_lang.upper()} rimossa.", icon=":material/delete:")
                        st.rerun()

        # 1. Informazioni Personali & Contatti (Shared across languages)
        with st.expander("👤 Informazioni Personali & Foto", expanded=True):
            p = cv_data.setdefault("personal", {})
            p1, p2 = st.columns(2)
            with p1:
                p["name"] = st.text_input("Nome e Cognome", value=p.get("name", ""), placeholder="Es. Mario Rossi", key=f"p_name_{ver}")
                p["email"] = st.text_input("Email", value=p.get("email", ""), placeholder="es. mario.rossi@email.com", key=f"p_mail_{ver}")
                p["phone"] = st.text_input("Telefono", value=p.get("phone", ""), placeholder="es. +39 340 1234567", key=f"p_tel_{ver}")
            with p2:
                # Localized headline per language
                cur_hl = p.get("headline", {})
                if isinstance(cur_hl, dict):
                    hl_val = cur_hl.get(edit_lang, "")
                    hl_input = st.text_input(f"Titolo Professionale ({edit_lang.upper()})", value=hl_val, placeholder="es. AI Engineer & GenAI Researcher", key=f"p_hl_{ver}")
                    cur_hl[edit_lang] = hl_input
                    p["headline"] = cur_hl
                else:
                    hl_input = st.text_input(f"Titolo Professionale ({edit_lang.upper()})", value=str(cur_hl), placeholder="es. AI Engineer", key=f"p_hl_{ver}")
                    p["headline"] = {edit_lang: hl_input}
                
                p["github"] = st.text_input("GitHub / Portfolio (senza https://)", value=p.get("github", ""), placeholder="github.com/tuo-username", key=f"p_gh_{ver}")
                p["location"] = st.text_input("Località (Città, Paese)", value=p.get("location", ""), placeholder="Bologna, Italy", key=f"p_loc_{ver}")

            # Foto Profilo
            ph_c1, ph_c2 = st.columns([3, 1], vertical_alignment="center")
            with ph_c1:
                photo_file = st.file_uploader("Carica Foto Profilo (PNG / JPG)", type=["png", "jpg", "jpeg"], key=f"photo_up_{ver}")
                if photo_file is not None:
                    custom_photo_path = os.path.join(session_dir, "photo.png")
                    with open(custom_photo_path, "wb") as f_img:
                        f_img.write(photo_file.read())
                    cfg["photo_path"] = f"/data/sessions/{session_id}/photo.png"
                    cfg["show_photo"] = True
                    st.toast("Foto profilo caricata!", icon=":material/image:")
            with ph_c2:
                if cfg.get("photo_path") and os.path.exists(os.path.join(session_dir, "photo.png")):
                    st.image(os.path.join(session_dir, "photo.png"), width=60)
                    if st.button("Rimuovi Foto", key=f"rm_photo_{ver}"):
                        cfg["photo_path"] = None
                        cfg["show_photo"] = False
                        st.session_state.data_version += 1
                        st.rerun()

        # 2. Profilo Professionale & Bio
        with st.expander(f"📝 Profilo Professionale & Bio ({edit_lang.upper()})", expanded=True):
            lang_headings["profile"] = st.text_input("Titolo Sezione", value=lang_headings.get("profile", "PROFILO"), key=f"h_prof_{edit_lang}_{ver}")
            lang_data["profile"] = st.text_area("Testo del Profilo", value=lang_data.get("profile", ""), height=100, placeholder="Sintesi del tuo background, competenze chiave e valore che puoi portare...", key=f"txt_prof_{edit_lang}_{ver}")

        # 3. Esperienze Lavorative
        with st.expander(f"💼 Esperienze Lavorative ({edit_lang.upper()})", expanded=False):
            lang_headings["experience"] = st.text_input("Titolo Sezione", value=lang_headings.get("experience", "ESPERIENZE LAVORATIVE"), key=f"h_exp_{edit_lang}_{ver}")
            exps = lang_data.setdefault("experience", [])

            for i, exp in enumerate(exps):
                with st.container(border=True):
                    exp_top1, exp_top2 = st.columns([4, 1])
                    with exp_top1:
                        st.markdown(f"**Esperienza #{i+1}: {exp.get('role', 'Nuovo Ruolo')}**")
                    with exp_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_exp_{edit_lang}_{i}_{ver}"):
                            exps.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()

                    c_r1, c_r2 = st.columns([2, 1])
                    with c_r1:
                        exp["role"] = st.text_input("Ruolo", value=exp.get("role", ""), placeholder="es. Generative AI Engineer", key=f"exp_r_{edit_lang}_{i}_{ver}")
                        exp["company"] = st.text_input("Azienda / Ente", value=exp.get("company", ""), placeholder="es. INRIA Research Lab", key=f"exp_c_{edit_lang}_{i}_{ver}")
                    with c_r2:
                        exp["period"] = st.text_input("Periodo", value=exp.get("period", ""), placeholder="es. Mar - Ago 2025", key=f"exp_p_{edit_lang}_{i}_{ver}")

                    bullets = exp.get("bullets", [])
                    bullets_text = "\n".join(bullets) if isinstance(bullets, list) and bullets else exp.get("description", "")
                    new_bullets_text = st.text_area(
                        "Bullet points (uno per riga. Usa il **grassetto** per mettere in risalto numeri e tool)",
                        value=bullets_text,
                        height=90,
                        placeholder="• Implementate strategie di **similarity caching** riducendo la latenza del **35%**.",
                        key=f"exp_b_{edit_lang}_{i}_{ver}"
                    )
                    exp["bullets"] = [b.strip() for b in new_bullets_text.split("\n") if b.strip()]
                    exp["description"] = " ".join(exp["bullets"])

            if st.button("+ Aggiungi Nuova Esperienza", icon=":material/add:", key=f"add_exp_btn_{edit_lang}_{ver}"):
                exps.append({
                    "role": "Nuovo Ruolo",
                    "company": "Azienda / Ente",
                    "period": "2025 - Presente",
                    "description": "",
                    "bullets": ["Descrivi l'obiettivo raggiunto, il metodo usato e l'impatto numerico."]
                })
                st.session_state.data_version += 1
                st.rerun()

        # 4. Istruzione & Titoli Accademici
        with st.expander(f"🎓 Istruzione & Titoli Accademici ({edit_lang.upper()})", expanded=False):
            lang_headings["education"] = st.text_input("Titolo Sezione", value=lang_headings.get("education", "ISTRUZIONE"), key=f"h_edu_{edit_lang}_{ver}")
            edus = lang_data.setdefault("education", [])
            for i, edu in enumerate(edus):
                with st.container(border=True):
                    ed_top1, ed_top2 = st.columns([4, 1])
                    with ed_top1:
                        st.markdown(f"**Titolo #{i+1}: {edu.get('degree', '')}**")
                    with ed_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_edu_{edit_lang}_{i}_{ver}"):
                            edus.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()

                    ed_c1, ed_c2 = st.columns([2, 1])
                    with ed_c1:
                        edu["degree"] = st.text_input("Titolo di Studio", value=edu.get("degree", ""), placeholder="es. Laurea Magistrale in AI", key=f"ed_d_{edit_lang}_{i}_{ver}")
                        edu["institution"] = st.text_input("Università / Ente", value=edu.get("institution", ""), placeholder="es. Università di Bologna", key=f"ed_inst_{edit_lang}_{i}_{ver}")
                    with ed_c2:
                        edu["period"] = st.text_input("Periodo", value=edu.get("period", ""), placeholder="es. 2023 - Presente", key=f"ed_p_{edit_lang}_{i}_{ver}")
                    edu["details"] = st.text_input("Dettagli / Tesi", value=edu.get("details", ""), placeholder="es. Focus su Deep Learning e Computer Vision", key=f"ed_det_{edit_lang}_{i}_{ver}")

            if st.button("+ Aggiungi Titolo di Studio", icon=":material/add:", key=f"add_edu_btn_{edit_lang}_{ver}"):
                edus.append({
                    "degree": "Nuovo Titolo",
                    "institution": "Università",
                    "period": "2025",
                    "details": ""
                })
                st.session_state.data_version += 1
                st.rerun()

        # 5. Competenze Tecniche
        with st.expander(f"💻 Competenze Tecniche ({edit_lang.upper()})", expanded=False):
            lang_headings["skills"] = st.text_input("Titolo Sezione", value=lang_headings.get("skills", "COMPETENZE TECNICHE"), key=f"h_sk_{edit_lang}_{ver}")
            sks = lang_data.setdefault("skills", [])
            for i, sk in enumerate(sks):
                with st.container(border=True):
                    sk_top1, sk_top2 = st.columns([4, 1])
                    with sk_top1:
                        st.markdown(f"**Categoria #{i+1}: {sk.get('category', '')}**")
                    with sk_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_sk_{edit_lang}_{i}_{ver}"):
                            sks.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()
                    sc1, sc2 = st.columns([1, 2])
                    with sc1:
                        sk["category"] = st.text_input("Categoria", value=sk.get("category", ""), placeholder="es. AI & Machine Learning", key=f"sk_c_{edit_lang}_{i}_{ver}")
                    with sc2:
                        raw_items = sk.get("items", "")
                        items_str = ", ".join(raw_items) if isinstance(raw_items, list) else str(raw_items)
                        sk["items"] = st.text_input("Tecnologie (separate da virgola)", value=items_str, placeholder="PyTorch, Python, Docker, Git", key=f"sk_it_{edit_lang}_{i}_{ver}")

            if st.button("+ Aggiungi Categoria Competenze", icon=":material/add:", key=f"add_sk_btn_{edit_lang}_{ver}"):
                sks.append({"category": "Nuova Categoria", "items": "Tool 1, Tool 2, Tool 3"})
                st.session_state.data_version += 1
                st.rerun()

        # 6. Progetti Selezionati
        with st.expander(f"🚀 Progetti Selezionati ({edit_lang.upper()})", expanded=False):
            lang_headings["projects"] = st.text_input("Titolo Sezione", value=lang_headings.get("projects", "PROGETTI SELEZIONATI"), key=f"h_pr_{edit_lang}_{ver}")
            projs = lang_data.setdefault("projects", [])
            for i, proj in enumerate(projs):
                with st.container(border=True):
                    p_top1, p_top2 = st.columns([4, 1])
                    with p_top1:
                        st.markdown(f"**Progetto #{i+1}: {proj.get('name', '')}**")
                    with p_top2:
                        if st.button("Elimina", icon=":material/delete:", key=f"del_pr_{edit_lang}_{i}_{ver}"):
                            projs.pop(i)
                            st.session_state.data_version += 1
                            st.rerun()
                    pr1, pr2 = st.columns([2, 1])
                    with pr1:
                        proj["name"] = st.text_input("Nome Progetto", value=proj.get("name", ""), placeholder="es. Similarity Caching for Diffusion", key=f"pr_n_{edit_lang}_{i}_{ver}")
                        proj["tech"] = st.text_input("Tecnologie usate", value=proj.get("tech", ""), placeholder="PyTorch, Stable Diffusion", key=f"pr_t_{edit_lang}_{i}_{ver}")
                    with pr2:
                        proj["link"] = st.text_input("Link (GitHub / Demo)", value=proj.get("link", ""), placeholder="github.com/...", key=f"pr_l_{edit_lang}_{i}_{ver}")
                    proj["description"] = st.text_area("Descrizione sintetica", value=proj.get("description", ""), height=55, placeholder="Framework di benchmark per...", key=f"pr_d_{edit_lang}_{i}_{ver}")

            if st.button("+ Aggiungi Progetto", icon=":material/add:", key=f"add_pr_btn_{edit_lang}_{ver}"):
                projs.append({
                    "name": "Nuovo Progetto",
                    "tech": "Python, Docker",
                    "link": "github.com",
                    "description": "Breve descrizione del risultato ottenuto."
                })
                st.session_state.data_version += 1
                st.rerun()

        # 7. Lingue Parlate & Volontariato
        with st.expander(f"🌐 Lingue Parlate & Volontariato ({edit_lang.upper()})", expanded=False):
            lang_headings["languages"] = st.text_input("Titolo Lingue", value=lang_headings.get("languages", "COMPETENZE LINGUISTICHE"), key=f"h_lang_{edit_lang}_{ver}")
            lang_list = lang_data.setdefault("languages", [])
            for i, l in enumerate(lang_list):
                lc1, lc2, lc3 = st.columns([2, 2, 1])
                with lc1:
                    l["lang"] = st.text_input(f"Lingua #{i+1}", value=l.get("lang", ""), placeholder="Italiano", key=f"l_n_{edit_lang}_{i}_{ver}")
                with lc2:
                    l["level"] = st.text_input(f"Livello #{i+1}", value=l.get("level", ""), placeholder="Madrelingua / C1", key=f"l_v_{edit_lang}_{i}_{ver}")
                with lc3:
                    if st.button("Rimuovi", key=f"del_l_{edit_lang}_{i}_{ver}"):
                        lang_list.pop(i)
                        st.session_state.data_version += 1
                        st.rerun()

            if st.button("+ Aggiungi Lingua", icon=":material/add:", key=f"add_lang_btn_{edit_lang}_{ver}"):
                lang_list.append({"lang": "Inglese", "level": "B2 / Fluente"})
                st.session_state.data_version += 1
                st.rerun()

            st.space("small")
            lang_headings["volunteer"] = st.text_input("Titolo Volontariato", value=lang_headings.get("volunteer", "ASSOCIAZIONI E VOLONTARIATO"), key=f"h_vol_{edit_lang}_{ver}")
            lang_data["volunteer"] = st.text_area("Attività extra / Volontariato", value=lang_data.get("volunteer", ""), height=65, placeholder="Educatore scout, volontario...", key=f"txt_vol_{edit_lang}_{ver}")

            st.space("small")
            lang_data["footer"] = st.text_area("Clausola Privacy (GDPR)", value=lang_data.get("footer", get_default_footer(edit_lang)), height=50, key=f"txt_gdpr_{edit_lang}_{ver}")

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
            key=f"tpl_sel_{ver}"
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
            key=f"pal_sel_{ver}"
        ) or current_pal
        cfg["palette"] = selected_pal

        if selected_pal in palettes and selected_pal != "personalizzata":
            cfg["colors"].update(palettes[selected_pal]["colors"])

        with st.expander("Personalizza i singoli colori", icon=":material/colorize:"):
            c_cols = cfg["colors"]
            col1, col2, col3 = st.columns(3)
            with col1:
                c_cols["primary"] = st.color_picker("Titoli Principali", c_cols.get("primary", "#0F172A"), key=f"c_p_{ver}")
                c_cols["accent"] = st.color_picker("Sottotitoli / Accento", c_cols.get("accent", "#7C3AED"), key=f"c_a_{ver}")
                c_cols["left_bg"] = st.color_picker("Header Sinistra", c_cols.get("left_bg", "#6FE3FF"), key=f"c_lb_{ver}")
            with col2:
                c_cols["right_bg"] = st.color_picker("Header Destra", c_cols.get("right_bg", "#A380FF"), key=f"c_rb_{ver}")
                c_cols["text_main"] = st.color_picker("Testo", c_cols.get("text_main", "#1E293B"), key=f"c_tm_{ver}")
                c_cols["text_muted"] = st.color_picker("Testo Muted", c_cols.get("text_muted", "#475569"), key=f"c_mu_{ver}")
            with col3:
                c_cols["line_color"] = st.color_picker("Divisori", c_cols.get("line_color", "#CBD5E1"), key=f"c_ln_{ver}")
                c_cols["sidebar_bg"] = st.color_picker("Sfondo Sidebar", c_cols.get("sidebar_bg", "#0F172A"), key=f"c_sb_{ver}")
                c_cols["sidebar_accent"] = st.color_picker("Accento Sidebar", c_cols.get("sidebar_accent", "#38BDF8"), key=f"c_sa_{ver}")
            
            c_cols["primary_text"] = c_cols["primary"]
            c_cols["secondary_text"] = c_cols["text_main"]

        st.space("small")
        st.subheader("3. Budget Pagine & Densità (Anti-Overflow)")
        
        # 1-click density presets
        preset_c1, preset_c2 = st.columns(2)
        with preset_c1:
            if st.button("⚡ Adatta a 1 Pagina Perfetta", use_container_width=True, icon=":material/auto_fix_high:"):
                cfg["font_size"] = "8.4pt"
                cfg["section_spacing"] = "4.0pt"
                cfg["line_spacing"] = "0.45em"
                cfg["margin_y"] = "0.9cm"
                cfg["margin_bottom"] = "0.8cm"
                st.session_state.data_version += 1
                st.rerun()
        with preset_c2:
            if st.button("📖 Layout Disteso (2 Pagine)", use_container_width=True, icon=":material/format_line_spacing:"):
                cfg["font_size"] = "9.2pt"
                cfg["section_spacing"] = "6.5pt"
                cfg["line_spacing"] = "0.50em"
                cfg["margin_y"] = "1.2cm"
                cfg["margin_bottom"] = "1.1cm"
                st.session_state.data_version += 1
                st.rerun()

        sl_col1, sl_col2 = st.columns(2)
        with sl_col1:
            raw_font_size = float(cfg.get("font_size", "8.5pt").replace("pt", ""))
            new_font_size = st.slider("Dimensione Testo Base (pt)", min_value=7.5, max_value=11.0, value=raw_font_size, step=0.1, key=f"sl_fs_{ver}")
            cfg["font_size"] = f"{new_font_size}pt"

            raw_spacing = float(cfg.get("section_spacing", "4.0pt").replace("pt", ""))
            new_spacing = st.slider("Spaziatura tra Sezioni (pt)", min_value=2.0, max_value=12.0, value=raw_spacing, step=0.5, key=f"sl_ss_{ver}")
            cfg["section_spacing"] = f"{new_spacing}pt"

        with sl_col2:
            raw_leading = float(cfg.get("line_spacing", "0.46em").replace("em", ""))
            new_leading = st.slider("Interlinea / Leading (em)", min_value=0.38, max_value=0.62, value=raw_leading, step=0.01, key=f"sl_ls_{ver}")
            cfg["line_spacing"] = f"{new_leading}em"

            raw_margin_y = float(cfg.get("margin_y", "0.9cm").replace("cm", ""))
            new_margin_y = st.slider("Margini Verticali (cm)", min_value=0.6, max_value=1.8, value=raw_margin_y, step=0.05, key=f"sl_my_{ver}")
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
                key=f"sel_ff_{ver}"
            )
        with t_col2:
            cfg["show_photo"] = st.toggle("Mostra Foto", value=cfg.get("show_photo", False), key=f"tog_ph_{ver}")
        with t_col3:
            cfg["show_gdpr"] = st.toggle("Mostra GDPR", value=cfg.get("show_gdpr", True), key=f"tog_gdpr_{ver}")

    # -------------------------------------------------------------
    # TAB 3: AUDIT ATS & SCANSIONABILITÀ
    # -------------------------------------------------------------
    with tab_audit:
        st.subheader("📊 Audit di Scansionabilità ATS")
        st.caption("Verifica la presenza di metriche d'impatto, verbi d'azione e parole chiave conformi agli standard internazionali.")

        active_content = cv_data.get(active_preview_lang, {})
        full_text = " ".join([
            active_content.get("profile", ""),
            " ".join([exp.get("description", "") + " ".join(exp.get("bullets", [])) for exp in active_content.get("experience", [])]),
            " ".join([str(sk.get("items", "")) for sk in active_content.get("skills", [])]),
        ])

        metrics_found = re.findall(r'\b\d+(?:[\.,]\d+)?%?|\b\d+\b', full_text)
        
        # Action verbs (Multilingual)
        if active_preview_lang == "it":
            action_verbs = [
                "implementate", "sviluppato", "ottimizzato", "progettato", "ridotto",
                "condotta", "erogati", "gestito", "analizzato", "coordinato", "creato",
                "ingegnerizzato", "automatizzato", "integrato", "supervisionato"
            ]
        else:
            action_verbs = [
                "engineered", "implemented", "optimized", "benchmarked", "developed", 
                "designed", "accelerated", "slashed", "integrated", "architected",
                "spearheaded", "authored", "orchestrated", "automated", "delivered"
            ]
        found_verbs = [v for v in action_verbs if re.search(r'\b' + v + r'\b', full_text, re.IGNORECASE)]

        core_tech_keywords = [
            "pytorch", "diffusion", "latent", "caching", "inference", "latency",
            "cuda", "generative ai", "computer vision", "docker", "python",
            "hugging face", "scikit-learn", "agile", "deep learning", "linux", "ci/cd"
        ]
        found_keywords = [kw for kw in core_tech_keywords if re.search(r'\b' + kw + r'\b', full_text, re.IGNORECASE)]

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Metriche Numeriche", f"{len(metrics_found)}", help="Percentuali, tempi o volumi d'impatto.")
        with m2:
            st.metric("Verbi d'Azione", f"{len(found_verbs)}/{len(action_verbs)}")
        with m3:
            st.metric("Keyword Stack Rilevate", f"{len(found_keywords)}/{len(core_tech_keywords)}")

        st.space("small")
        st.markdown("##### 🎯 Riscontro Tecnologico")
        kw_cols = st.columns(4)
        for i, kw in enumerate(core_tech_keywords):
            with kw_cols[i % 4]:
                if kw in found_keywords:
                    st.badge(kw.title(), icon=":material/check:", color="green")
                else:
                    st.badge(kw.title(), icon=":material/close:", color="gray")

# ==================== RIGHT PANEL: AUTO-COMPILE & LIVE PREVIEW ====================
with right_panel:
    # Check if profile has content
    has_content = bool(cv_data.get("personal", {}).get("name") or cv_data.get(active_preview_lang, {}).get("experience"))

    # Active language switcher for preview
    p_head1, p_head2 = st.columns([1.5, 1], vertical_alignment="center")
    with p_head1:
        st.subheader("👁️ Anteprima Live")
    with p_head2:
        new_prev_lang = st.selectbox(
            "Lingua Anteprima",
            options=avail_langs,
            format_func=get_lang_label,
            index=avail_langs.index(active_preview_lang) if active_preview_lang in avail_langs else 0,
            label_visibility="collapsed",
            key=f"prev_lang_sel_{ver}"
        )
        if new_prev_lang != active_preview_lang:
            cfg["lang"] = new_prev_lang
            active_preview_lang = new_prev_lang

    pdf_bytes, compile_err = compile_session_pdf(cv_data, lang=active_preview_lang)
    page_count = count_pdf_pages(pdf_bytes)

    # Status badge
    if not has_content:
        st.badge("Profilo Vuoto", icon=":material/edit:", color="gray")
    elif page_count == 1:
        st.badge("1 Pagina Perfetta (ATS Recommended)", icon=":material/check_circle:", color="green")
    elif page_count == 2:
        st.badge("Layout su 2 Pagine", icon=":material/description:", color="blue")
    elif page_count > 2:
        st.badge(f"{page_count} Pagine (Attenzione Overflow)", icon=":material/warning:", color="red")

    if compile_err:
        st.error(f"Errore di compilazione Typst: {compile_err}")

    if pdf_bytes:
        name_slug = cv_data.get("personal", {}).get("name", "").strip().replace(" ", "_") or "Curriculum"
        
        # Primary Action Bar
        dl_col1, dl_col2 = st.columns([1.4, 1])
        with dl_col1:
            st.download_button(
                label=f"Scarica PDF ({active_preview_lang.upper()})",
                data=pdf_bytes,
                file_name=f"CV_{name_slug}_{active_preview_lang.upper()}.pdf",
                mime="application/pdf",
                type="primary",
                icon=":material/download:",
                use_container_width=True
            )
        with dl_col2:
            # Bundle all languages in ZIP
            with st.popover("Tutte le Lingue", icon=":material/folder_zip:", use_container_width=True):
                st.markdown("##### 📦 Esporta Bundle Multilingua")
                st.caption("Genera e scarica un archivio ZIP con i PDF di tutte le lingue del profilo.")
                if st.button("Crea Archivio ZIP", type="primary", use_container_width=True):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for l_code in avail_langs:
                            l_pdf, l_err = compile_session_pdf(cv_data, lang=l_code)
                            if l_pdf:
                                zf.writestr(f"CV_{name_slug}_{l_code.upper()}.pdf", l_pdf)
                    zip_buffer.seek(0)
                    st.download_button(
                        label="Scarica ZIP Completo",
                        data=zip_buffer.getvalue(),
                        file_name=f"CV_{name_slug}_multilingual.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

        if not has_content:
            st.info("💡 Il profilo è attualmente vuoto. Carica il tuo file YAML in alto oppure inizia a compilare i campi a sinistra per visualizzare il CV!")

        # Embedded iframe
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
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
