#import "/src/utils.typ": parse-color, parse-length, mini-icon, skill-chip, section-title-modern, format-markup

#let render(data) = [
  #let lang = data.config.at("lang", default: "it")
  #let content = data.at(lang, default: (:))
  #let personal = data.at("personal", default: (:))
  #let colors = data.config.at("colors", default: (:))
  #let headings = content.at("headings", default: (:))

  #let sidebar-bg = parse-color(colors.at("sidebar_bg", default: "#0F172A"))
  #let sidebar-text = parse-color(colors.at("sidebar_text", default: "#F8FAFC"))
  #let sidebar-muted = parse-color(colors.at("sidebar_muted", default: "#94A3B8"))
  #let sidebar-accent = parse-color(colors.at("sidebar_accent", default: "#38BDF8"))
  
  #let main-primary = parse-color(colors.at("primary", default: "#0F172A"))
  #let main-accent = parse-color(colors.at("accent", default: "#0284C7"))
  #let main-text = parse-color(colors.at("text_main", default: "#1E293B"))
  #let main-muted = parse-color(colors.at("text_muted", default: "#64748B"))
  #let line-color = parse-color(colors.at("line_color", default: "#E2E8F0"))

  #let pref-font = data.config.at("font_family", default: "Helvetica")
  #let font-family = (pref-font, "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans", "sans-serif")

  #let font-size = parse-length(data.config.at("font_size", default: 8.5pt), default: 8.5pt)
  #let line-spacing = parse-length(data.config.at("line_spacing", default: 0.46em), default: 0.46em)
  #let section-spacing = parse-length(data.config.at("section_spacing", default: 4pt), default: 4pt)
  #let margin-x = parse-length(data.config.at("margin_x", default: 1.2cm), default: 1.2cm)
  #let margin-y = parse-length(data.config.at("margin_y", default: 1.0cm), default: 1.0cm)

  #let show-photo = data.config.at("show_photo", default: true)
  #let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  #let base-size = font-size
  #let size-name = base-size * 1.50
  #let size-section = base-size * 1.20
  #let size-role = base-size * 1.05
  #let size-sub = base-size * 0.95
  #let size-small = base-size * 0.88
  #let size-tiny = base-size * 0.80

  #let sidebar-width = 6.2cm

  #set page(
    paper: "a4",
    margin: (left: sidebar-width + 0.6cm, right: margin-x, top: margin-y, bottom: margin-y),
    background: place(top + left, rect(width: sidebar-width, height: 100%, fill: sidebar-bg)),
    fill: white
  )

  #set text(font: font-family, size: base-size, fill: main-text, lang: lang, hyphenate: false)
  #set par(justify: true, leading: line-spacing)

  // ==================== SIDEBAR CONTENT (PLACED ON FIRST PAGE) ====================
  #place(top + left, dx: -(sidebar-width + 0.6cm) + 0.5cm, dy: 0cm)[
    #box(width: sidebar-width - 1.0cm)[
      #set text(fill: sidebar-text)

      // Avatar
      #if show-photo [
        #let photo-path = data.config.at("photo_path", default: "/assets/profile.png")
        #align(center)[
          #box(
            width: 2.7cm,
            height: 2.7cm,
            radius: 50%,
            stroke: 2.5pt + sidebar-accent,
            clip: true,
            image(photo-path, width: 100%, height: 100%, fit: "cover")
          )
        ]
        #v(3pt)
      ]

      // Name & Headline
      #align(center)[
        #set text(hyphenate: false)
        #let raw-name = personal.at("name", default: "")
        #let parts = if raw-name != "" { raw-name.split(" ") } else { () }
        #text(size: size-name, weight: "bold", fill: sidebar-text)[
          #if parts.len() >= 2 [
            #parts.at(0)\
            #parts.slice(1).join(" ")
          ] else if parts.len() == 1 [
            #parts.at(0)
          ] else [
            CV Studio
          ]
        ]\
        #v(1.5pt)
        #let raw-hl = personal.at("headline", default: "")
        #let hl = if type(raw-hl) == dictionary { raw-hl.at(lang, default: "") } else { str(raw-hl) }
        #if hl != "" [
          #text(size: size-sub, weight: "medium", fill: sidebar-accent)[#hl]
        ]
      ]
      
      #v(5pt)
      #line(length: 100%, stroke: 0.5pt + sidebar-muted)
      #v(4pt)

      // Contacts
      #let contact-rows = ()
      #if personal.at("email", default: "") != "" {
        contact-rows.push([#box(baseline: 15%, width: 8.5pt, height: 8.5pt, image("/assets/icons/mail.svg"))])
        contact-rows.push([#link("mailto:" + personal.email)[#text(size: size-small, fill: sidebar-text)[#personal.email]]])
      }
      #if personal.at("phone", default: "") != "" {
        contact-rows.push([#box(baseline: 15%, width: 8.5pt, height: 8.5pt, image("/assets/icons/phone.svg"))])
        contact-rows.push([#link("tel:" + personal.phone)[#text(size: size-small, fill: sidebar-text)[#personal.phone]]])
      }
      #if personal.at("github", default: "") != "" {
        contact-rows.push([#box(baseline: 15%, width: 8.5pt, height: 8.5pt, image("/assets/icons/github.svg"))])
        contact-rows.push([#link("https://" + personal.github.replace("https://", ""))[#text(size: size-small, fill: sidebar-text)[#personal.github]]])
      }
      #if personal.at("location", default: "") != "" {
        contact-rows.push([#box(baseline: 15%, width: 8.5pt, height: 8.5pt, image("/assets/icons/location.svg"))])
        contact-rows.push([#text(size: size-small, fill: sidebar-text)[#personal.location]])
      }

      #if contact-rows.len() > 0 [
        #text(size: size-sub, weight: "bold", fill: sidebar-accent)[#upper(headings.at("contacts", default: "CONTATTI"))]\
        #v(2.5pt)
        #grid(
          columns: (12pt, 1fr),
          gutter: 3.5pt,
          align: (center + horizon, left + horizon),
          ..contact-rows
        )
        #v(6pt)
      ]

      // Technical Skills
      #let skill-list = content.at("skills", default: ())
      #if skill-list.len() > 0 [
        #text(size: size-sub, weight: "bold", fill: sidebar-accent)[#upper(headings.at("skills", default: "COMPETENZE"))]\
        #v(2.5pt)
        #for sk in skill-list [
          #text(size: size-small, weight: "bold", fill: sidebar-accent)[#sk.at("category", default: "")]\
          #v(1.5pt)
          #let raw-items = sk.at("items", default: "")
          #let items = if type(raw-items) == str { raw-items.split(",") } else { raw-items }
          #for item in items [
            #let trimmed = str(item).trim()
            #if trimmed != "" [
              #skill-chip(trimmed, bg: rgb(255, 255, 255, 14%), stroke: rgb(255, 255, 255, 25%), text-color: sidebar-text, font-size: size-tiny)
              #h(1.5pt)
            ]
          ]
          #v(2.5pt)
        ]
        #v(4pt)
      ]

      // Languages
      #let lang-list = content.at("languages", default: ())
      #if lang-list.len() > 0 [
        #text(size: size-sub, weight: "bold", fill: sidebar-accent)[#upper(headings.at("languages", default: "LINGUE"))]\
        #v(2.5pt)
        #for l in lang-list [
          #text(size: size-small, weight: "semibold", fill: sidebar-text)[• #l.at("lang", default: ""):]
          #text(size: size-tiny, fill: sidebar-muted)[ #l.at("level", default: "")]\
        ]
      ]
    ]
  ]

  // ==================== MAIN COLUMN BODY ====================
  // Professional Summary
  #let profile-text = content.at("profile", default: "")
  #if profile-text != "" [
    #section-title-modern(headings.at("profile", default: "PROFILO"), accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #text(size: size-small)[#profile-text]
    #v(section-spacing)
  ]

  // Work Experience
  #let exp-list = content.at("experience", default: ())
  #if exp-list.len() > 0 [
    #section-title-modern(headings.at("experience", default: "ESPERIENZE"), accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #for exp in exp-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          gutter: 6pt,
          [#text(size: size-role, weight: "bold", fill: main-primary)[#exp.at("role", default: "")]],
          [#text(size: size-small, fill: main-muted)[#exp.at("period", default: "")]]
        )
        #text(size: size-sub, weight: "semibold", fill: main-accent)[#exp.at("company", default: "")]\
        #v(1pt)
        #let bullets = exp.at("bullets", default: ())
        #if bullets.len() > 0 [
          #for b in bullets [
            #grid(
              columns: (7pt, 1fr),
              gutter: 0pt,
              [#text(fill: main-accent, size: size-small)[•]],
              [#text(size: size-small, fill: main-text)[#format-markup(b)]]
            )
            #v(0.6pt)
          ]
        ] else if exp.at("description", default: "") != "" [
          #text(size: size-small, fill: main-text)[#exp.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // Selected Projects
  #let proj-list = content.at("projects", default: ())
  #if proj-list.len() > 0 [
    #section-title-modern(headings.at("projects", default: "PROGETTI"), accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #for proj in proj-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          gutter: 6pt,
          [
            #text(size: size-sub, weight: "bold", fill: main-primary)[#proj.at("name", default: "")]
            #if proj.at("tech", default: "") != "" [#text(size: size-small, fill: main-accent)[ — #proj.tech]]
          ],
          [
            #if proj.at("link", default: "") != "" [
              #text(size: size-tiny, fill: main-muted)[#proj.link]
            ]
          ]
        )
        #if proj.at("description", default: "") != "" [
          #v(0.5pt)
          #text(size: size-small, fill: main-text)[#proj.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // Education
  #let edu-list = content.at("education", default: ())
  #if edu-list.len() > 0 [
    #section-title-modern(headings.at("education", default: "ISTRUZIONE"), accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #for edu in edu-list [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          gutter: 6pt,
          [#text(size: size-sub, weight: "bold", fill: main-primary)[#edu.at("degree", default: "")]],
          [#text(size: size-small, fill: main-muted)[#edu.at("period", default: "")]]
        )
        #text(size: size-small, fill: main-accent)[#edu.at("institution", default: "")]\
        #if edu.at("details", default: "") != "" [
          #text(size: size-small, fill: main-muted, style: "italic")[#edu.details]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // Volunteering
  #let vol-text = content.at("volunteer", default: "")
  #if vol-text != "" [
    #section-title-modern(headings.at("volunteer", default: "VOLONTARIATO"), accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #text(size: size-small, fill: main-text)[#vol-text]
  ]

  // GDPR Footer
  #let footer-text = content.at("footer", default: "")
  #if show-gdpr and footer-text != "" [
    #v(section-spacing * 1.5)
    #align(center)[
      #text(size: size-tiny, fill: main-muted)[#footer-text]
    ]
  ]
]
