#import "/src/utils.typ": parse-color, parse-length, mini-icon, skill-chip, section-title-modern, format-markup

#let render(data) = [
  #let lang = data.config.at("lang", default: "it")
  #let content = data.at(lang, default: (:))
  #let personal = data.at("personal", default: (:))
  #let colors = data.config.at("colors", default: (:))
  #let headings = content.at("headings", default: (:))
  
  // Color palette defaults
  #let primary-color = parse-color(colors.at("primary", default: "#0F172A"))
  #let accent-color = parse-color(colors.at("accent", default: "#0284C7"))
  #let text-main = parse-color(colors.at("text_main", default: "#1E293B"))
  #let text-muted = parse-color(colors.at("text_muted", default: "#64748B"))
  #let line-color = parse-color(colors.at("line_color", default: "#E2E8F0"))
  #let chip-bg = parse-color(colors.at("chip_bg", default: "#F8FAFC"))
  #let chip-border = parse-color(colors.at("chip_border", default: "#CBD5E1"))
  
  #let pref-font = data.config.at("font_family", default: "Helvetica")
  #let font-family = (pref-font, "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans", "sans-serif")

  #let font-size = parse-length(data.config.at("font_size", default: 8.5pt), default: 8.5pt)
  #let line-spacing = parse-length(data.config.at("line_spacing", default: 0.46em), default: 0.46em)
  #let section-spacing = parse-length(data.config.at("section_spacing", default: 4pt), default: 4pt)
  #let margin-y = parse-length(data.config.at("margin_y", default: 0.9cm), default: 0.9cm)
  #let margin-x = parse-length(data.config.at("margin_x", default: 1.2cm), default: 1.2cm)

  #let show-photo = data.config.at("show_photo", default: false)
  #let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  #let base-size = font-size
  #let size-name = base-size * 2.1
  #let size-headline = base-size * 1.10
  #let size-section = base-size * 1.22
  #let size-role = base-size * 1.05
  #let size-sub = base-size * 0.96
  #let size-small = base-size * 0.88
  #let size-tiny = base-size * 0.80
  
  #set page(
    paper: "a4",
    margin: (x: margin-x, top: margin-y, bottom: margin-y),
    fill: white
  )
  
  #set text(font: font-family, size: base-size, fill: text-main, lang: lang, hyphenate: false)
  #set par(justify: true, leading: line-spacing)

  // ==================== HEADER ====================
  #block(width: 100%, inset: (bottom: 2pt))[
    #grid(
      columns: if show-photo { (1fr, auto) } else { (1fr) },
      gutter: 12pt,
      align: (left + horizon, right + horizon),
      [
        // Name & Title
        #let raw-name = personal.at("name", default: "")
        #text(size: size-name, weight: "bold", fill: primary-color, tracking: -0.2pt)[
          #if raw-name != "" { raw-name } else { [CV Studio] }
        ]
        #v(-4pt)
        #let raw-hl = personal.at("headline", default: "")
        #let hl = if type(raw-hl) == dictionary { raw-hl.at(lang, default: "") } else { str(raw-hl) }
        #if hl != "" [
          #text(size: size-headline, weight: "medium", fill: accent-color)[#hl]
          #v(3pt)
        ]
        
        // Contact details strip
        #let contact-items = ()
        #if personal.at("email", default: "") != "" {
          contact-items.push([#mini-icon("mail", fill: accent-color) #link("mailto:" + personal.email)[#personal.email]])
        }
        #if personal.at("phone", default: "") != "" {
          contact-items.push([#mini-icon("phone", fill: accent-color) #link("tel:" + personal.phone)[#personal.phone]])
        }
        #if personal.at("github", default: "") != "" {
          contact-items.push([#mini-icon("github", fill: accent-color) #link("https://" + personal.github.replace("https://", ""))[#personal.github]])
        }
        #if personal.at("location", default: "") != "" {
          contact-items.push([#mini-icon("location", fill: accent-color) #personal.location])
        }

        #if contact-items.len() > 0 [
          #box[
            #set text(size: size-small, fill: text-muted)
            #grid(
              columns: (auto,) * contact-items.len(),
              gutter: 10pt,
              ..contact-items
            )
          ]
        ]
      ],
      if show-photo [
        #let photo-path = data.config.at("photo_path", default: "/assets/profile.png")
        #box(
          width: 2.2cm,
          height: 2.2cm,
          radius: 50%,
          stroke: 1.5pt + line-color,
          clip: true,
          image(photo-path, width: 100%, height: 100%, fit: "cover")
        )
      ]
    )
  ]
  
  #v(1pt)
  #line(length: 100%, stroke: 1.2pt + primary-color)
  #v(2pt)

  // ==================== PROFILE SUMMARY ====================
  #let profile-text = content.at("profile", default: "")
  #if profile-text != "" [
    #section-title-modern(headings.at("profile", default: "PROFILO"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #text(size: size-small, fill: text-main)[#profile-text]
    #v(section-spacing)
  ]

  // ==================== TECHNICAL SKILLS (CHIPS) ====================
  #let skill-list = content.at("skills", default: ())
  #if skill-list.len() > 0 [
    #section-title-modern(headings.at("skills", default: "COMPETENZE"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #grid(
      columns: (1fr, 1fr),
      column-gutter: 10pt,
      row-gutter: section-spacing * 0.6,
      ..skill-list.map(sk => [
        #block(width: 100%)[
          #text(size: size-sub, weight: "bold", fill: primary-color)[#sk.at("category", default: "")]\
          #v(1.5pt)
          #let raw-items = sk.at("items", default: "")
          #let items = if type(raw-items) == str { raw-items.split(",") } else { raw-items }
          #for item in items [
            #let trimmed = str(item).trim()
            #if trimmed != "" [
              #skill-chip(trimmed, bg: chip-bg, stroke: chip-border, text-color: text-main, font-size: size-tiny)
              #h(2pt)
            ]
          ]
        ]
      ])
    )
    #v(section-spacing)
  ]

  // ==================== WORK EXPERIENCE ====================
  #let exp-list = content.at("experience", default: ())
  #if exp-list.len() > 0 [
    #section-title-modern(headings.at("experience", default: "ESPERIENZE"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #for exp in exp-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.7))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-role, weight: "bold", fill: primary-color)[#exp.at("role", default: "")]
            #text(size: size-sub, weight: "medium", fill: accent-color)[ — #exp.at("company", default: "")]
          ],
          [
            #text(size: size-small, fill: text-muted)[#exp.at("period", default: "")]
          ]
        )
        #v(1pt)
        #let bullets = exp.at("bullets", default: ())
        #if bullets.len() > 0 [
          #for b in bullets [
            #grid(
              columns: (7pt, 1fr),
              gutter: 0pt,
              [#text(fill: accent-color, size: size-small)[•]],
              [#text(size: size-small, fill: text-main)[#format-markup(b)]]
            )
            #v(0.6pt)
          ]
        ] else if exp.at("description", default: "") != "" [
          #text(size: size-small, fill: text-main)[#exp.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== SELECTED PROJECTS ====================
  #let proj-list = content.at("projects", default: ())
  #if proj-list.len() > 0 [
    #section-title-modern(headings.at("projects", default: "PROGETTI"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #for proj in proj-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold", fill: primary-color)[#proj.at("name", default: "")]
            #if proj.at("tech", default: "") != "" [#text(size: size-small, fill: accent-color)[ — #proj.tech]]
          ],
          [
            #if proj.at("link", default: "") != "" [
              #text(size: size-tiny, fill: text-muted)[#mini-icon("link", fill: text-muted) #proj.link]
            ]
          ]
        )
        #if proj.at("description", default: "") != "" [
          #v(0.5pt)
          #text(size: size-small, fill: text-main)[#proj.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== EDUCATION ====================
  #let edu-list = content.at("education", default: ())
  #if edu-list.len() > 0 [
    #section-title-modern(headings.at("education", default: "ISTRUZIONE"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #for edu in edu-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold", fill: primary-color)[#edu.at("degree", default: "")]
            #text(size: size-small, fill: accent-color)[ — #edu.at("institution", default: "")]
          ],
          [
            #text(size: size-small, fill: text-muted)[#edu.at("period", default: "")]
          ]
        )
        #if edu.at("details", default: "") != "" [
          #v(0.5pt)
          #text(size: size-small, fill: text-muted, style: "italic")[#edu.details]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== LANGUAGES & VOLUNTEERING (TWO COLUMN BOTTOM) ====================
  #let lang-list = content.at("languages", default: ())
  #let vol-text = content.at("volunteer", default: "")
  #if lang-list.len() > 0 or vol-text != "" [
    #grid(
      columns: if lang-list.len() > 0 and vol-text != "" { (40%, 60%) } else { (100%) },
      gutter: 14pt,
      [
        #if lang-list.len() > 0 [
          #section-title-modern(headings.at("languages", default: "LINGUE"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
          #for l in lang-list [
            #text(size: size-sub, weight: "bold", fill: primary-color)[#l.at("lang", default: "")]
            #text(size: size-small, fill: text-muted)[ - #l.at("level", default: "")]\
          ]
        ]
      ],
      [
        #if vol-text != "" [
          #section-title-modern(headings.at("volunteer", default: "VOLONTARIATO"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
          #text(size: size-small, fill: text-main)[#vol-text]
        ]
      ]
    )
  ]

  // ==================== GDPR FOOTER ====================
  #let footer-text = content.at("footer", default: "")
  #if show-gdpr and footer-text != "" [
    #v(section-spacing * 1.5)
    #align(center)[
      #text(size: size-tiny, fill: text-muted)[#footer-text]
    ]
  ]
]
