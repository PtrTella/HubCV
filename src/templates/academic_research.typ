#import "/src/utils.typ": parse-color, parse-length, section-title-academic, format-markup

#let render(data) = [
  #let lang = data.config.at("lang", default: "it")
  #let content = data.at(lang)
  #let personal = data.personal
  #let colors = data.config.at("colors", default: (:))

  #let primary-color = parse-color(colors.at("primary", default: "#1E293B"))
  #let accent-color = parse-color(colors.at("accent", default: "#334155"))
  #let line-color = parse-color(colors.at("line_color", default: "#94A3B8"))
  #let font-family = data.config.at("font_family", default: "New Computer Modern")
  #let font-size = parse-length(data.config.at("font_size", default: 9.2pt), default: 9.2pt)
  #let line-spacing = parse-length(data.config.at("line_spacing", default: 0.52em), default: 0.52em)
  #let section-spacing = parse-length(data.config.at("section_spacing", default: 5pt), default: 5pt)
  #let margin-y = parse-length(data.config.at("margin_y", default: 1.2cm), default: 1.2cm)
  #let margin-x = parse-length(data.config.at("margin_x", default: 1.4cm), default: 1.4cm)

  #let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  #let base-size = font-size
  #let size-name = base-size * 2.2
  #let size-headline = base-size * 1.15
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

  #set text(font: font-family, size: base-size, fill: primary-color, lang: lang)
  #set par(justify: true, leading: line-spacing)

  // ==================== ACADEMIC HEADER ====================
  #align(center)[
    #set text(hyphenate: false)
    #text(size: size-name, weight: "bold", tracking: 0.6pt)[#upper(personal.name)]\
    #v(2pt)
    #let hl = if type(personal.headline) == dictionary { personal.headline.at(lang, default: "AI Engineer & Generative AI Researcher") } else { str(personal.headline) }
    #text(size: size-headline, style: "italic", fill: accent-color)[#hl]\
    #v(3pt)
    #text(size: size-small, fill: accent-color)[
      #personal.location #h(8pt) | #h(8pt)
      #link("mailto:" + personal.email)[#personal.email] #h(8pt) | #h(8pt)
      #link("tel:" + personal.phone)[#personal.phone] #h(8pt) | #h(8pt)
      #link("https://" + personal.github)[#personal.github]
    ]
    #v(3pt)
    #line(length: 100%, stroke: 0.8pt + line-color)
  ]
  #v(2pt)

  // ==================== RESEARCH STATEMENT / PROFILE ====================
  #if "profile" in content and content.profile != "" [
    #section-title-academic(content.headings.profile, accent-color: primary-color, size: size-section, spacing: section-spacing)
    #text(size: size-small)[#content.profile]
    #v(section-spacing)
  ]

  // ==================== EDUCATION & RESEARCH INTERNSHIPS ====================
  #if "education" in content and content.education.len() > 0 [
    #section-title-academic(content.headings.education, accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for edu in content.education [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold")[#edu.institution]\
            #text(size: size-small, style: "italic")[#edu.degree]
          ],
          [
            #text(size: size-small, fill: accent-color)[#edu.period]
          ]
        )
        #if "details" in edu and edu.details != "" [
          #v(0.5pt)
          #text(size: size-small, fill: accent-color)[#edu.details]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== RESEARCH & PROFESSIONAL EXPERIENCE ====================
  #if "experience" in content and content.experience.len() > 0 [
    #section-title-academic(content.headings.experience, accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for exp in content.experience [
      #block(width: 100%, inset: (bottom: section-spacing * 0.7))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-role, weight: "bold")[#exp.role]
            #text(size: size-sub, weight: "medium", fill: accent-color)[ — #exp.company]
          ],
          [
            #text(size: size-small, fill: accent-color)[#exp.period]
          ]
        )
        #v(1pt)
        #if "bullets" in exp and exp.bullets.len() > 0 [
          #for b in exp.bullets [
            #grid(
              columns: (8pt, 1fr),
              gutter: 0pt,
              [•],
              [#text(size: size-small)[#format-markup(b)]]
            )
            #v(0.6pt)
          ]
        ] else [
          #text(size: size-small)[#exp.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== SELECTED PROJECTS ====================
  #if "projects" in content and content.projects.len() > 0 [
    #section-title-academic(content.headings.at("projects", default: "PROGETTI"), accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for proj in content.projects [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold")[#proj.name]
            #if "tech" in proj [#text(size: size-small, style: "italic", fill: accent-color)[ — #proj.tech]]
          ],
          [
            #if "link" in proj [#text(size: size-small)[#link("https://" + proj.link)[#proj.link]]]
          ]
        )
        #if "description" in proj [
          #text(size: size-small)[#proj.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // ==================== TECHNICAL EXPERTISE ====================
  #if "skills" in content and content.skills.len() > 0 [
    #section-title-academic(content.headings.skills, accent-color: primary-color, size: size-section, spacing: section-spacing)
    #for sk in content.skills [
      #grid(
        columns: (160pt, 1fr),
        gutter: 8pt,
        [#text(size: size-sub, weight: "bold")[#sk.category:]],
        [#text(size: size-small)[#sk.items]]
      )
      #v(section-spacing * 0.4)
    ]
    #v(section-spacing)
  ]

  // ==================== LANGUAGES & COMMUNITY ====================
  #grid(
    columns: (1fr, 1.3fr),
    gutter: 14pt,
    [
      #if "languages" in content and content.languages.len() > 0 [
        #section-title-academic(content.headings.languages, accent-color: primary-color, size: size-section, spacing: section-spacing)
        #for l in content.languages [
          #text(size: size-small)[*#l.lang*: #l.level]\
        ]
      ]
    ],
    [
      #if "volunteer" in content and content.volunteer != "" [
        #section-title-academic(content.headings.volunteer, accent-color: primary-color, size: size-section, spacing: section-spacing)
        #text(size: size-small)[#content.volunteer]
      ]
    ]
  )

  // ==================== GDPR FOOTER ====================
  #if show-gdpr and "footer" in content and content.footer != "" [
    #v(1fr)
    #align(center)[
      #text(size: size-tiny, fill: accent-color)[#content.footer]
    ]
  ]
]
