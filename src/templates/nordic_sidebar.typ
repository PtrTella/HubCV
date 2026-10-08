#import "/src/utils.typ": parse-color, parse-length, mini-icon, skill-chip, section-title-modern, format-markup

#let render(data) = [
  #let lang = data.config.at("lang", default: "it")
  #let content = data.at(lang)
  #let personal = data.personal
  #let colors = data.config.at("colors", default: (:))

  #let sidebar-bg = parse-color(colors.at("sidebar_bg", default: "#0F172A"))
  #let sidebar-text = parse-color(colors.at("sidebar_text", default: "#F8FAFC"))
  #let sidebar-muted = parse-color(colors.at("sidebar_muted", default: "#94A3B8"))
  #let sidebar-accent = parse-color(colors.at("sidebar_accent", default: "#38BDF8"))
  
  #let main-primary = parse-color(colors.at("primary", default: "#0F172A"))
  #let main-accent = parse-color(colors.at("accent", default: "#0284C7"))
  #let main-text = parse-color(colors.at("text_main", default: "#1E293B"))
  #let main-muted = parse-color(colors.at("text_muted", default: "#64748B"))
  #let line-color = parse-color(colors.at("line_color", default: "#E2E8F0"))

  #let font-family = data.config.at("font_family", default: "Helvetica")
  #let font-size = parse-length(data.config.at("font_size", default: 8.5pt), default: 8.5pt)
  #let line-spacing = parse-length(data.config.at("line_spacing", default: 0.46em), default: 0.46em)
  #let section-spacing = parse-length(data.config.at("section_spacing", default: 4pt), default: 4pt)
  #let margin-x = parse-length(data.config.at("margin_x", default: 1.2cm), default: 1.2cm)
  #let margin-y = parse-length(data.config.at("margin_y", default: 1.0cm), default: 1.0cm)

  #let show-photo = data.config.at("show_photo", default: true)
  #let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  #let base-size = font-size
  #let size-name = base-size * 1.55
  #let size-section = base-size * 1.22
  #let size-role = base-size * 1.05
  #let size-sub = base-size * 0.96
  #let size-small = base-size * 0.88
  #let size-tiny = base-size * 0.80

  #let sidebar-width = 6.2cm

  #set page(
    paper: "a4",
    margin: (left: sidebar-width + 0.6cm, right: margin-x, top: margin-y, bottom: margin-y),
    background: place(top + left, rect(width: sidebar-width, height: 100%, fill: sidebar-bg)),
    fill: white
  )

  #set text(font: font-family, size: base-size, fill: main-text, lang: lang)
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
            width: 2.8cm,
            height: 2.8cm,
            radius: 50%,
            stroke: 2pt + sidebar-accent,
            clip: true,
            image(photo-path, width: 100%, height: 100%, fit: "cover")
          )
        ]
        #v(4pt)
      ]

      // Name & Headline
      #align(center)[
        #set text(hyphenate: false)
        #text(size: size-name, weight: "bold", fill: sidebar-text)[
          #let parts = personal.name.split(" ")
          #if parts.len() >= 2 [
            #parts.at(0)\
            #parts.slice(1).join(" ")
          ] else [
            #personal.name
          ]
        ]\
        #v(2pt)
        #let hl = if type(personal.headline) == dictionary { personal.headline.at(lang, default: "AI Engineer") } else { str(personal.headline) }
        #text(size: size-sub, weight: "medium", fill: sidebar-accent)[#hl]
      ]
      
      #v(6pt)
      #line(length: 100%, stroke: 0.5pt + sidebar-muted)
      #v(5pt)

      // Contacts
      #text(size: size-sub, weight: "bold", fill: sidebar-accent)[CONTATTI]\
      #v(3pt)
      #grid(
        columns: (12pt, 1fr),
        gutter: 4pt,
        align: (center + horizon, left + horizon),
        [✉], [#link("mailto:" + personal.email)[#text(size: size-small, fill: sidebar-text)[#personal.email]]],
        [☎], [#link("tel:" + personal.phone)[#text(size: size-small, fill: sidebar-text)[#personal.phone]]],
        [⌥], [#link("https://" + personal.github)[#text(size: size-small, fill: sidebar-text)[#personal.github]]],
        [⌖], [#text(size: size-small, fill: sidebar-text)[#personal.location]]
      )
      
      #v(8pt)

      // Technical Skills
      #if "skills" in content and content.skills.len() > 0 [
        #text(size: size-sub, weight: "bold", fill: sidebar-accent)[#upper(content.headings.skills)]\
        #v(3pt)
        #for sk in content.skills [
          #text(size: size-small, weight: "bold", fill: sidebar-accent)[#sk.category]\
          #v(1.5pt)
          #let items = if type(sk.items) == str { sk.items.split(",") } else { sk.items }
          #for item in items [
            #let trimmed = item.trim()
            #if trimmed != "" [
              #skill-chip(trimmed, bg: rgb(255, 255, 255, 12%), stroke: rgb(255, 255, 255, 25%), text-color: rgb("FFFFFF"), font-size: size-tiny)
              #h(1.5pt)
            ]
          ]
          #v(3pt)
        ]
        #v(5pt)
      ]

      // Languages
      #if "languages" in content and content.languages.len() > 0 [
        #text(size: size-sub, weight: "bold", fill: sidebar-accent)[#upper(content.headings.languages)]\
        #v(3pt)
        #for l in content.languages [
          #text(size: size-small, weight: "semibold", fill: sidebar-text)[• #l.lang:]
          #text(size: size-tiny, fill: sidebar-muted)[ #l.level]\
        ]
      ]
    ]
  ]

  // ==================== MAIN COLUMN BODY (NATURAL DOCUMENT FLOW) ====================
  // Professional Summary
  #if "profile" in content and content.profile != "" [
    #section-title-modern(content.headings.profile, accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #text(size: size-small)[#content.profile]
    #v(section-spacing)
  ]

  // Work Experience
  #if "experience" in content and content.experience.len() > 0 [
    #section-title-modern(content.headings.experience, accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #for exp in content.experience [
      #block(width: 100%, inset: (bottom: section-spacing * 0.7))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-role, weight: "bold", fill: main-primary)[#exp.role]
            #text(size: size-sub, weight: "medium", fill: main-accent)[ — #exp.company]
          ],
          [
            #text(size: size-small, fill: main-muted)[#exp.period]
          ]
        )
        #v(1pt)
        #if "bullets" in exp and exp.bullets.len() > 0 [
          #for b in exp.bullets [
            #grid(
              columns: (7pt, 1fr),
              gutter: 0pt,
              [#text(fill: main-accent, size: size-small)[•]],
              [#text(size: size-small, fill: main-text)[#format-markup(b)]]
            )
            #v(0.6pt)
          ]
        ] else [
          #text(size: size-small, fill: main-text)[#exp.description]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // Selected Projects
  #if "projects" in content and content.projects.len() > 0 [
    #section-title-modern(content.headings.at("projects", default: "PROGETTI"), accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #for proj in content.projects [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #text(size: size-sub, weight: "bold", fill: main-primary)[#proj.name]
        #if "tech" in proj [#text(size: size-small, fill: main-accent)[ — #proj.tech]]\
        #text(size: size-small, fill: main-text)[#proj.description]
      ]
    ]
    #v(section-spacing)
  ]

  // Education
  #if "education" in content and content.education.len() > 0 [
    #section-title-modern(content.headings.education, accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #for edu in content.education [
      #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
        #grid(
          columns: (1fr, auto),
          [
            #text(size: size-sub, weight: "bold", fill: main-primary)[#edu.degree]
            #text(size: size-small, fill: main-accent)[ — #edu.institution]
          ],
          [
            #text(size: size-small, fill: main-muted)[#edu.period]
          ]
        )
        #if "details" in edu and edu.details != "" [
          #text(size: size-small, fill: main-muted, style: "italic")[#edu.details]
        ]
      ]
    ]
    #v(section-spacing)
  ]

  // Volunteering
  #if "volunteer" in content and content.volunteer != "" [
    #section-title-modern(content.headings.volunteer, accent-color: main-primary, line-color: line-color, size: size-section, spacing: section-spacing)
    #text(size: size-small, fill: main-text)[#content.volunteer]
  ]

  // GDPR Footer
  #if show-gdpr and "footer" in content and content.footer != "" [
    #v(1fr)
    #align(center)[
      #text(size: size-tiny, fill: main-muted)[#content.footer]
    ]
  ]
]
