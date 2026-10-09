#import "/src/utils.typ": parse-color, parse-length, section-title-academic, format-markup

#let render(data) = [
  #let lang = data.config.at("lang", default: "it")
  #let content = data.at(lang, default: (:))
  #let personal = data.at("personal", default: (:))
  #let colors = data.config.at("colors", default: (:))
  #let headings = content.at("headings", default: (:))

  #let primary-color = parse-color(colors.at("primary", default: "#1E293B"))
  #let accent-color = parse-color(colors.at("accent", default: "#334155"))
  #let line-color = parse-color(colors.at("line_color", default: "#94A3B8"))

  #let pref-font = data.config.at("font_family", default: "New Computer Modern")
  #let font-family = (pref-font, "New Computer Modern", "DejaVu Serif", "Liberation Serif", "Times New Roman", "serif")

  #let font-size = parse-length(data.config.at("font_size", default: 9.0pt), default: 9.0pt)
  #let line-spacing = parse-length(data.config.at("line_spacing", default: 0.50em), default: 0.50em)
  #let section-spacing = parse-length(data.config.at("section_spacing", default: 4.5pt), default: 4.5pt)
  #let margin-y = parse-length(data.config.at("margin_y", default: 1.1cm), default: 1.1cm)
  #let margin-x = parse-length(data.config.at("margin_x", default: 1.3cm), default: 1.3cm)

  #let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  #let base-size = font-size
  #let size-name = base-size * 2.1
  #let size-headline = base-size * 1.12
  #let size-section = base-size * 1.22
  #let size-role = base-size * 1.05
  #let size-sub = base-size * 0.98
  #let size-small = base-size * 0.88
  #let size-tiny = base-size * 0.80

  #set page(
    paper: "a4",
    margin: (x: margin-x, top: margin-y, bottom: margin-y),
    fill: white
  )

  #set text(font: font-family, size: base-size, fill: primary-color, lang: lang, hyphenate: false)
  #set par(justify: true, leading: line-spacing)

  // ==================== ACADEMIC HEADER ====================
  #align(center)[
    #set text(hyphenate: false)
    #let raw-name = personal.at("name", default: "")
    #text(size: size-name, weight: "bold", tracking: 0.6pt)[
      #if raw-name != "" { upper(raw-name) } else { [CURRICULUM VITAE] }
    ]\
    #v(2pt)
    #let raw-hl = personal.at("headline", default: "")
    #let hl = if type(raw-hl) == dictionary { raw-hl.at(lang, default: "") } else { str(raw-hl) }
    #if hl != "" [
      #text(size: size-headline, style: "italic", fill: accent-color)[#hl]\
      #v(3pt)
    ]

    #let contact-items = ()
    #if personal.at("location", default: "") != "" { contact-items.push(personal.location) }
    #if personal.at("email", default: "") != "" { contact-items.push(link("mailto:" + personal.email)[#personal.email]) }
    #if personal.at("phone", default: "") != "" { contact-items.push(link("tel:" + personal.phone)[#personal.phone]) }
    #if personal.at("github", default: "") != "" { contact-items.push(link("https://" + personal.github.replace("https://", ""))[#personal.github]) }

    #if contact-items.len() > 0 [
      #text(size: size-small, fill: accent-color)[
        #contact-items.join([ #h(6pt) | #h(6pt) ])
      ]
      #v(3pt)
    ]
    #line(length: 100%, stroke: 0.8pt + line-color)
  ]
  #v(2pt)

  // ==================== RESEARCH STATEMENT / PROFILE ====================
  #let profile-text = content.at("profile", default: "")
  #if profile-text != "" [
    #section-title-academic(headings.at("profile", default: "PROFILO"), accent-color: primary-color, size: size-section, spacing: section-spacing)
    #text(size: size-small)[#profile-text]
    #v(section-spacing)
  ]

  // ==================== EDUCATION & RESEARCH INTERNSHIPS ====================
  #let edu-list = content.at("education", default: ())
  #if edu-list.len() > 0 [
    #section-title-academic(headings.at("education", default: "ISTRUZIONE"), accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for edu in edu-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold")[#edu.at("institution", default: "")]\
            #text(size: size-small, style: "italic")[#edu.at("degree", default: "")]
          ],
          [
            #text(size: size-small, fill: accent-color)[#edu.at("period", default: "")]
          ]
        )
        #if edu.at("details", default: "") != "" [
          #v(0.5pt)
          #text(size: size-small, fill: accent-color)[#edu.details]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== RESEARCH & PROFESSIONAL EXPERIENCE ====================
  #let exp-list = content.at("experience", default: ())
  #if exp-list.len() > 0 [
    #section-title-academic(headings.at("experience", default: "ESPERIENZE"), accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for exp in exp-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.7))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-role, weight: "bold")[#exp.at("role", default: "")]
            #text(size: size-sub, weight: "medium", fill: accent-color)[ — #exp.at("company", default: "")]
          ],
          [
            #text(size: size-small, fill: accent-color)[#exp.at("period", default: "")]
          ]
        )
        #v(1pt)
        #let bullets = exp.at("bullets", default: ())
        #if bullets.len() > 0 [
          #for b in bullets [
            #grid(
              columns: (8pt, 1fr),
              gutter: 0pt,
              [#text(fill: accent-color, size: size-small)[•]],
              [#text(size: size-small)[#format-markup(b)]]
            )
            #v(0.6pt)
          ]
        ] else if exp.at("description", default: "") != "" [
          #text(size: size-small)[#exp.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== SELECTED PROJECTS ====================
  #let proj-list = content.at("projects", default: ())
  #if proj-list.len() > 0 [
    #section-title-academic(headings.at("projects", default: "PROGETTI"), accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for proj in proj-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold")[#proj.at("name", default: "")]
            #if proj.at("tech", default: "") != "" [#text(size: size-small, style: "italic")[ (#proj.tech)]]
          ],
          [
            #if proj.at("link", default: "") != "" [#text(size: size-small, fill: accent-color)[#proj.link]]
          ]
        )
        #if proj.at("description", default: "") != "" [
          #text(size: size-small)[#proj.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== TECHNICAL SKILLS & LANGUAGES ====================
  #let skill-list = content.at("skills", default: ())
  #if skill-list.len() > 0 [
    #section-title-academic(headings.at("skills", default: "COMPETENZE"), accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for sk in skill-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.4))[
        #text(size: size-sub, weight: "bold")[#sk.at("category", default: ""): ]
        #let raw-items = sk.at("items", default: "")
        #let item-str = if type(raw-items) == list { raw-items.join(", ") } else { str(raw-items) }
        #text(size: size-small)[#item-str]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== LANGUAGES & VOLUNTEERING ====================
  #let lang-list = content.at("languages", default: ())
  #let vol-text = content.at("volunteer", default: "")
  #if lang-list.len() > 0 or vol-text != "" [
    #grid(
      columns: if lang-list.len() > 0 and vol-text != "" { (40%, 60%) } else { (100%) },
      gutter: 14pt,
      [
        #if lang-list.len() > 0 [
          #section-title-academic(headings.at("languages", default: "LINGUE"), accent-color: primary-color, size: size-section, spacing: section-spacing)
          #for l in lang-list [
            #text(size: size-sub, weight: "bold")[#l.at("lang", default: "")]
            #text(size: size-small, fill: accent-color)[ - #l.at("level", default: "")]\
          ]
        ]
      ],
      [
        #if vol-text != "" [
          #section-title-academic(headings.at("volunteer", default: "VOLONTARIATO"), accent-color: primary-color, size: size-section, spacing: section-spacing)
          #text(size: size-small)[#vol-text]
        ]
      ]
    )
  ]

  // ==================== GDPR FOOTER ====================
  #let footer-text = content.at("footer", default: "")
  if show-gdpr and footer-text != "" [
    #v(section-spacing * 1.5)
    #align(center)[
      #text(size: size-tiny, fill: accent-color)[#footer-text]
    ]
  ]
]
