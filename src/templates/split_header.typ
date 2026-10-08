#import "/src/utils.typ": parse-color, parse-length, skill-chip, section-title-bar, format-markup

#let render(data) = {
  let lang = data.config.at("lang", default: "it")
  let content = data.at(lang, default: (:))
  let personal = data.at("personal", default: (:))
  let colors = data.config.at("colors", default: (:))
  let headings = content.at("headings", default: (:))

  // Color customization
  let left-bg = parse-color(colors.at("left_bg", default: "#6FE3FF"))
  let right-bg = parse-color(colors.at("right_bg", default: "#A380FF"))
  let primary-text = parse-color(colors.at("primary_text", default: colors.at("primary", default: "#0F172A")))
  let secondary-text = parse-color(colors.at("secondary_text", default: colors.at("text_main", default: "#334155")))
  let accent-text = parse-color(colors.at("accent", default: "#64748B"))
  let bar-left = parse-color(colors.at("bar_left", default: left-bg))
  let bar-right = parse-color(colors.at("bar_right", default: right-bg))

  let pref-font = data.config.at("font_family", default: "Helvetica")
  let font-family = (pref-font, "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans", "sans-serif")

  let font-size = parse-length(data.config.at("font_size", default: 8.5pt), default: 8.5pt)
  let line-spacing = parse-length(data.config.at("line_spacing", default: 0.46em), default: 0.46em)
  let section-spacing = parse-length(data.config.at("section_spacing", default: 4pt), default: 4pt)
  let margin-x = parse-length(data.config.at("margin_x", default: 1.2cm), default: 1.2cm)
  let margin-bottom = parse-length(data.config.at("margin_bottom", default: 0.8cm), default: 0.8cm)

  let show-photo = data.config.at("show_photo", default: true)
  let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  let base-size = font-size
  let size-name = base-size * 2.0
  let size-headline = base-size * 0.95
  let size-section = base-size * 1.22
  let size-role = base-size * 1.05
  let size-sub = base-size * 0.96
  let size-small = base-size * 0.88
  let size-tiny = base-size * 0.80

  set page(
    paper: "a4",
    margin: (x: 0cm, top: 0cm, bottom: margin-bottom),
    fill: white
  )

  set text(font: font-family, size: base-size, fill: secondary-text, lang: lang)
  set par(justify: true, leading: line-spacing)

  // ==================== TWO-TONE HEADER ====================
  box(height: 3.2cm, width: 100%)[
    #grid(
      columns: (46%, 54%),
      rows: (100%),
      [
        #rect(width: 100%, height: 100%, fill: left-bg)[
          #pad(left: margin-x, right: if show-photo { 1.8cm } else { 0.4cm }, top: 0.55cm)[
            #set text(hyphenate: false)
            #let raw-name = personal.at("name", default: "")
            #let parts = if raw-name != "" { raw-name.split(" ") } else { () }
            #text(size: size-name, weight: "black", fill: primary-text, tracking: 0.3pt)[
              #if parts.len() >= 2 [
                #parts.at(0)\
                #parts.slice(1).join(" ")
              ] else if parts.len() == 1 [
                #parts.at(0)
              ] else [
                CV Studio
              ]
            ]
            #let raw-hl = personal.at("headline", default: "")
            #let hl = if type(raw-hl) == dictionary { raw-hl.at(lang, default: "") } else { str(raw-hl) }
            #if hl != "" [
              #v(2pt)
              #let hl-formatted = if show-photo and hl.contains(" & ") {
                let parts = hl.split(" & ")
                [#parts.at(0)\ #text(size: size-headline * 0.95)[& #parts.slice(1).join(" & ")]]
              } else {
                [#hl]
              }
              #text(size: size-headline, weight: "semibold", fill: primary-text.lighten(15%))[#hl-formatted]
            ]
          ]
        ]
      ],
      [
        #rect(width: 100%, height: 100%, fill: right-bg)[
          #pad(left: if show-photo { 1.8cm } else { 0.4cm }, right: margin-x, top: 0.65cm)[
            #align(right + horizon)[
              #set text(size: size-small, weight: "medium", fill: primary-text)
              #let contact-rows = ()
              #if personal.at("phone", default: "") != "" {
                contact-rows.push(align(right)[📞])
                contact-rows.push(align(left)[#personal.phone])
              }
              #if personal.at("email", default: "") != "" {
                contact-rows.push(align(right)[✉️])
                contact-rows.push(align(left)[#personal.email])
              }
              #if personal.at("github", default: "") != "" {
                contact-rows.push(align(right)[🌐])
                contact-rows.push(align(left)[#personal.github])
              }
              #if personal.at("location", default: "") != "" {
                contact-rows.push(align(right)[📍])
                contact-rows.push(align(left)[#personal.location])
              }
              #if contact-rows.len() > 0 [
                #grid(
                  columns: (auto, auto),
                  column-gutter: 6pt,
                  row-gutter: 2.5pt,
                  ..contact-rows
                )
              ]
            ]
          ]
        ]
      ]
    )
  ]

  // ==================== FLOATING CIRCULAR AVATAR ====================
  if show-photo [
    #let photo-path = data.config.at("photo_path", default: "/assets/profile.png")
    #place(top + center, dx: -2.3cm, dy: 1.45cm)[
      #box(
        width: 3.2cm,
        height: 3.2cm,
        radius: 50%,
        stroke: 3.5pt + white,
        clip: true,
        image(photo-path, width: 100%, height: 100%, fit: "cover")
      )
    ]
  ]

  // ==================== MAIN DUAL-COLUMN BODY ====================
  let pad-top = if show-photo { 1.3cm } else { 0.4cm }
  pad(x: margin-x, top: pad-top, bottom: 0.2cm)[
    #grid(
      columns: (45%, 5%, 50%),
      [
        // ---------- LEFT COLUMN ----------
        // Profile
        #let profile-text = content.at("profile", default: "")
        #if profile-text != "" [
          #section-title-bar(headings.at("profile", default: "PROFILO"), bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
          #text(size: size-small)[#profile-text]
          #v(section-spacing)
        ]

        // Education
        #let edu-list = content.at("education", default: ())
        #if edu-list.len() > 0 [
          #section-title-bar(headings.at("education", default: "ISTRUZIONE"), bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
          #for edu in edu-list [
            #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
              #grid(
                columns: (1fr, auto),
                [#text(size: size-sub, weight: "bold", fill: primary-text)[#edu.at("institution", default: "")]],
                [#text(size: size-small, fill: accent-text)[#edu.at("period", default: "")]]
              )
              #text(size: size-sub, weight: "medium", fill: secondary-text)[#edu.at("degree", default: "")]\
              #if edu.at("details", default: "") != "" [
                #text(size: size-small, fill: accent-text, style: "italic")[#edu.details]\
              ]
            ]
          ]
          #v(section-spacing)
        ]

        // Skills
        #let skill-list = content.at("skills", default: ())
        #if skill-list.len() > 0 [
          #section-title-bar(headings.at("skills", default: "COMPETENZE"), bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
          #for sk in skill-list [
            #block(width: 100%, inset: (bottom: section-spacing * 0.5))[
              #text(size: size-sub, weight: "bold", fill: primary-text)[#sk.at("category", default: ""):]\
              #v(1.5pt)
              #let raw-items = sk.at("items", default: "")
              #let items = if type(raw-items) == str { raw-items.split(",") } else { raw-items }
              #for item in items [
                #let trimmed = str(item).trim()
                #if trimmed != "" [
                  #skill-chip(trimmed, bg: rgb("F1F5F9"), stroke: rgb("CBD5E1"), text-color: primary-text, font-size: size-tiny)
                  #h(2pt)
                ]
              ]
            ]
          ]
          #v(section-spacing)
        ]

        // Languages
        #let lang-list = content.at("languages", default: ())
        #if lang-list.len() > 0 [
          #section-title-bar(headings.at("languages", default: "LINGUE"), bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
          #grid(
            columns: (1fr, 1fr),
            row-gutter: 3pt,
            ..lang-list.map(l => [
              #text(size: size-sub, weight: "bold", fill: primary-text)[#l.at("lang", default: "")]
              #text(size: size-small, fill: accent-text)[ - #l.at("level", default: "")]
            ])
          )
        ]
      ],
      [], // Column spacer
      [
        // ---------- RIGHT COLUMN ----------
        // Experience
        #let exp-list = content.at("experience", default: ())
        #if exp-list.len() > 0 [
          #section-title-bar(headings.at("experience", default: "ESPERIENZE"), bar-color: bar-right, text-color: primary-text, size: size-section, spacing: section-spacing)
          #for exp in exp-list [
            #block(width: 100%, inset: (bottom: section-spacing * 0.7))[
              #grid(
                columns: (1fr, auto),
                [
                  #text(size: size-role, weight: "bold", fill: primary-text)[#exp.at("role", default: "")]
                ],
                [
                  #text(size: size-small, fill: accent-text)[#exp.at("period", default: "")]
                ]
              )
              #text(size: size-sub, weight: "semibold", fill: accent-text)[#exp.at("company", default: "")]\
              #v(1pt)
              #let bullets = exp.at("bullets", default: ())
              #if bullets.len() > 0 [
                #for b in bullets [
                  #grid(
                    columns: (7pt, 1fr),
                    gutter: 0pt,
                    [#text(fill: bar-right, size: size-small)[•]],
                    [#text(size: size-small, fill: secondary-text)[#format-markup(b)]]
                  )
                  #v(0.8pt)
                ]
              ] else if exp.at("description", default: "") != "" [
                #text(size: size-small, fill: secondary-text)[#exp.description]
              ]
            ]
          ]
          #v(section-spacing)
        ]

        // Selected Projects
        #let proj-list = content.at("projects", default: ())
        #if proj-list.len() > 0 [
          #section-title-bar(headings.at("projects", default: "PROGETTI"), bar-color: bar-right, text-color: primary-text, size: size-section, spacing: section-spacing)
          #for proj in proj-list [
            #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
              #text(size: size-sub, weight: "bold", fill: primary-text)[#proj.at("name", default: "")]
              #if proj.at("tech", default: "") != "" [#text(size: size-small, fill: accent-text)[ (#proj.tech)]]\
              #if proj.at("description", default: "") != "" [
                #text(size: size-small, fill: secondary-text)[#proj.description]
              ]
            ]
          ]
          #v(section-spacing)
        ]

        // Volunteering
        #let vol-text = content.at("volunteer", default: "")
        #if vol-text != "" [
          #section-title-bar(headings.at("volunteer", default: "VOLONTARIATO"), bar-color: bar-right, text-color: primary-text, size: size-section, spacing: section-spacing)
          #text(size: size-small, fill: secondary-text)[#vol-text]
        ]
      ]
    )
  ]

  // ==================== GDPR FOOTER ====================
  let footer-text = content.at("footer", default: "")
  if show-gdpr and footer-text != "" [
    #v(section-spacing * 1.5)
    #align(center)[
      #text(size: size-tiny, fill: accent-text)[#footer-text]
    ]
  ]
}
