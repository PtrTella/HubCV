#import "/src/utils.typ": parse-color, parse-length, mini-icon, skill-chip, section-title-modern, format-markup

#let render(data) = [
  #let lang = data.config.at("lang", default: "it")
  #let content = data.at(lang)
  #let personal = data.personal
  #let colors = data.config.at("colors", default: (:))
  
  // Color palette defaults
  #let primary-color = parse-color(colors.at("primary", default: "#0F172A"))
  #let accent-color = parse-color(colors.at("accent", default: "#0284C7"))
  #let text-main = parse-color(colors.at("text_main", default: "#1E293B"))
  #let text-muted = parse-color(colors.at("text_muted", default: "#64748B"))
  #let line-color = parse-color(colors.at("line_color", default: "#E2E8F0"))
  #let chip-bg = parse-color(colors.at("chip_bg", default: "#F8FAFC"))
  #let chip-border = parse-color(colors.at("chip_border", default: "#CBD5E1"))
  
  #let font-family = data.config.at("font_family", default: "Helvetica")
  #let font-size = parse-length(data.config.at("font_size", default: 9.0pt), default: 9.0pt)
  #let line-spacing = parse-length(data.config.at("line_spacing", default: 0.50em), default: 0.50em)
  #let section-spacing = parse-length(data.config.at("section_spacing", default: 5pt), default: 5pt)
  #let margin-y = parse-length(data.config.at("margin_y", default: 1.0cm), default: 1.0cm)
  #let margin-x = parse-length(data.config.at("margin_x", default: 1.3cm), default: 1.3cm)

  #let show-photo = data.config.at("show_photo", default: false)
  #let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  #let base-size = font-size
  #let size-name = base-size * 2.2
  #let size-headline = base-size * 1.15
  #let size-section = base-size * 1.25
  #let size-role = base-size * 1.05
  #let size-sub = base-size * 0.98
  #let size-small = base-size * 0.88
  #let size-tiny = base-size * 0.80
  
  #set page(
    paper: "a4",
    margin: (x: margin-x, top: margin-y, bottom: margin-y),
    fill: white
  )
  
  #set text(font: font-family, size: base-size, fill: text-main, lang: lang)
  #set par(justify: true, leading: line-spacing)

  // ==================== HEADER ====================
  #block(width: 100%, inset: (bottom: 2pt))[
    #grid(
      columns: if show-photo { (1fr, auto) } else { (1fr) },
      gutter: 12pt,
      align: (left + horizon, right + horizon),
      [
        // Name & Title
        #text(size: size-name, weight: "bold", fill: primary-color, tracking: -0.2pt)[#personal.name]
        #v(-4pt)
        #let hl = if type(personal.headline) == dictionary { personal.headline.at(lang, default: "AI Engineer & Generative AI Researcher") } else { str(personal.headline) }
        #text(size: size-headline, weight: "medium", fill: accent-color)[#hl]
        #v(3pt)
        
        // Contact details strip
        #box[
          #set text(size: size-small, fill: text-muted)
          #grid(
            columns: (auto, auto, auto, auto),
            gutter: 10pt,
            [#mini-icon("mail", fill: accent-color) #link("mailto:" + personal.email)[#personal.email]],
            [#mini-icon("phone", fill: accent-color) #link("tel:" + personal.phone)[#personal.phone]],
            [#mini-icon("github", fill: accent-color) #link("https://" + personal.github)[#personal.github]],
            [#mini-icon("location", fill: accent-color) #personal.location]
          )
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
  #if "profile" in content and content.profile != "" [
    #section-title-modern(content.headings.profile, accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #text(size: size-small, fill: text-main)[#content.profile]
    #v(section-spacing)
  ]

  // ==================== TECHNICAL SKILLS (CHIPS) ====================
  #if "skills" in content and content.skills.len() > 0 [
    #section-title-modern(content.headings.skills, accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #grid(
      columns: (1fr, 1fr),
      column-gutter: 10pt,
      row-gutter: section-spacing * 0.6,
      ..content.skills.map(sk => [
        #block(width: 100%)[
          #text(size: size-sub, weight: "bold", fill: primary-color)[#sk.category]\
          #v(1.5pt)
          #let items = if type(sk.items) == str { sk.items.split(",") } else { sk.items }
          #for item in items [
            #let trimmed = item.trim()
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
  #if "experience" in content and content.experience.len() > 0 [
    #section-title-modern(content.headings.experience, accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #for exp in content.experience [
      #block(width: 100%, inset: (bottom: section-spacing * 0.7))[
        #grid(
          columns: (1fr, auto),
          align: (left, right),
          [#text(size: size-role, weight: "bold", fill: primary-color)[#exp.role]],
          [#text(size: size-small, weight: "medium", fill: text-muted)[#exp.period]]
        )
        #text(size: size-sub, weight: "medium", fill: accent-color)[#exp.company]\
        #v(1pt)
        #if "bullets" in exp and exp.bullets.len() > 0 [
          #for b in exp.bullets [
            #grid(
              columns: (8pt, 1fr),
              gutter: 0pt,
              [#text(fill: accent-color, size: size-small)[•]],
              [#text(size: size-small, fill: text-main)[#format-markup(b)]]
            )
            #v(0.6pt)
          ]
        ] else [
          #text(size: size-small, fill: text-main)[#exp.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== SELECTED PROJECTS ====================
  #if "projects" in content and content.projects.len() > 0 [
    #section-title-modern(content.headings.at("projects", default: "PROGETTI"), accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #for proj in content.projects [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold", fill: primary-color)[#proj.name]
            #if "tech" in proj [#text(size: size-small, fill: accent-color)[ — #proj.tech]]
          ],
          [
            #if "link" in proj [#text(size: size-small)[#link("https://" + proj.link)[#proj.link]]]
          ]
        )
        #if "description" in proj [
          #v(0.5pt)
          #text(size: size-small, fill: text-main)[#format-markup(proj.description)]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== EDUCATION ====================
  #if "education" in content and content.education.len() > 0 [
    #section-title-modern(content.headings.education, accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
    #for edu in content.education [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          align: (left, right),
          [#text(size: size-sub, weight: "bold", fill: primary-color)[#edu.degree]],
          [#text(size: size-small, weight: "medium", fill: text-muted)[#edu.period]]
        )
        #text(size: size-small, fill: accent-color)[#edu.institution]\
        #if "details" in edu and edu.details != "" [
          #v(0.5pt)
          #text(size: size-small, fill: text-muted, style: "italic")[#edu.details]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== LANGUAGES & VOLUNTEERING ====================
  #grid(
    columns: (1fr, 1.2fr),
    gutter: 14pt,
    [
      #if "languages" in content and content.languages.len() > 0 [
        #section-title-modern(content.headings.languages, accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
        #for l in content.languages [
          #text(size: size-sub, weight: "medium", fill: primary-color)[#l.lang]
          #text(size: size-small, fill: text-muted)[ — #l.level]\
        ]
      ]
    ],
    [
      #if "volunteer" in content and content.volunteer != "" [
        #section-title-modern(content.headings.volunteer, accent-color: primary-color, line-color: line-color, size: size-section, spacing: section-spacing)
        #text(size: size-small, fill: text-main)[#content.volunteer]
      ]
    ]
  )

  // ==================== GDPR FOOTER ====================
  #if show-gdpr and "footer" in content and content.footer != "" [
    #v(1fr)
    #align(center)[
      #text(size: size-tiny, fill: text-muted)[#content.footer]
    ]
  ]
]
