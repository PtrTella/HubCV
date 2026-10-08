#import "/src/utils.typ": parse-color, parse-length, skill-chip, section-title-bar, format-markup

#let render(data) = {
  let lang = data.config.at("lang", default: "it")
  let content = data.at(lang)
  let personal = data.personal
  let colors = data.config.at("colors", default: (:))

  // Color customization
  let left-bg = parse-color(colors.at("left_bg", default: "#6FE3FF"))
  let right-bg = parse-color(colors.at("right_bg", default: "#A380FF"))
  let primary-text = parse-color(colors.at("primary_text", default: "#0F172A"))
  let secondary-text = parse-color(colors.at("secondary_text", default: "#334155"))
  let accent-text = parse-color(colors.at("accent", default: "#64748B"))
  let bar-left = parse-color(colors.at("bar_left", default: left-bg))
  let bar-right = parse-color(colors.at("bar_right", default: right-bg))

  let font-family = data.config.at("font_family", default: "Helvetica")
  let font-size = parse-length(data.config.at("font_size", default: 8.5pt), default: 8.5pt)
  let line-spacing = parse-length(data.config.at("line_spacing", default: 0.46em), default: 0.46em)
  let section-spacing = parse-length(data.config.at("section_spacing", default: 4pt), default: 4pt)
  let margin-x = parse-length(data.config.at("margin_x", default: 1.2cm), default: 1.2cm)
  let margin-bottom = parse-length(data.config.at("margin_bottom", default: 0.8cm), default: 0.8cm)

  let show-photo = data.config.at("show_photo", default: true)
  let show-gdpr = data.config.at("show_gdpr", default: true)

  // Relative typography scale derived from font_size slider
  let base-size = font-size
  let size-name = base-size * 2.3
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
          #pad(left: margin-x, top: 0.8cm)[
            #set text(hyphenate: false)
            #text(size: size-name, weight: "black", fill: primary-text, tracking: 0.4pt)[
              #let parts = personal.name.split(" ")
              #if parts.len() >= 2 [
                #parts.at(0)\
                #parts.slice(1).join(" ")
              ] else [
                #personal.name
              ]
            ]
          ]
        ]
      ],
      [
        #rect(width: 100%, height: 100%, fill: right-bg)[
          #pad(right: margin-x, top: 0.65cm)[
            #align(right + horizon)[
              #set text(size: size-small, weight: "medium", fill: primary-text)
              #grid(
                columns: (auto, auto),
                column-gutter: 6pt,
                row-gutter: 3pt,
                align(right)[📞], align(left)[#personal.phone],
                align(right)[✉️], align(left)[#personal.email],
                align(right)[🌐], align(left)[#personal.github],
                align(right)[📍], align(left)[#personal.location]
              )
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
        #section-title-bar(content.headings.profile, bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
        #text(size: size-small)[#content.profile]
        #v(section-spacing)

        #section-title-bar(content.headings.education, bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
        #for edu in content.education [
          #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
            #grid(
              columns: (1fr, auto),
              [#text(size: size-sub, weight: "bold", fill: primary-text)[#edu.institution]],
              [#text(size: size-small, fill: accent-text)[#edu.period]]
            )
            #text(size: size-sub, weight: "medium", fill: secondary-text)[#edu.degree]\
            #if "details" in edu and edu.details != "" [
              #text(size: size-small, fill: accent-text, style: "italic")[#edu.details]\
            ]
          ]
        ]
        #v(section-spacing)

        #section-title-bar(content.headings.skills, bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
        #for sk in content.skills [
          #block(width: 100%, inset: (bottom: section-spacing * 0.5))[
            #text(size: size-sub, weight: "bold", fill: primary-text)[#sk.category:]\
            #v(1.5pt)
            #let items = if type(sk.items) == str { sk.items.split(",") } else { sk.items }
            #for item in items [
              #let trimmed = item.trim()
              #if trimmed != "" [
                #skill-chip(trimmed, bg: rgb("F1F5F9"), stroke: rgb("E2E8F0"), text-color: primary-text, font-size: size-tiny)
                #h(2pt)
              ]
            ]
          ]
        ]
        #v(section-spacing)

        #section-title-bar(content.headings.languages, bar-color: bar-left, text-color: primary-text, size: size-section, spacing: section-spacing)
        #grid(
          columns: (1fr, 1fr),
          row-gutter: 3pt,
          ..content.languages.map(l => [
            #text(size: size-sub, weight: "bold", fill: primary-text)[#l.lang]
            #text(size: size-small, fill: accent-text)[ - #l.level]
          ])
        )
      ],
      [], // Column spacer
      [
        // ---------- RIGHT COLUMN ----------
        #section-title-bar(content.headings.experience, bar-color: bar-right, text-color: primary-text, size: size-section, spacing: section-spacing)
        #for exp in content.experience [
          #block(width: 100%, inset: (bottom: section-spacing * 0.7))[
            #grid(
              columns: (1fr, auto),
              [
                #text(size: size-role, weight: "bold", fill: primary-text)[#exp.role]
              ],
              [
                #text(size: size-small, fill: accent-text)[#exp.period]
              ]
            )
            #text(size: size-sub, weight: "semibold", fill: accent-text)[#exp.company]\
            #v(1pt)
            #if "bullets" in exp and exp.bullets.len() > 0 [
              #for b in exp.bullets [
                #grid(
                  columns: (7pt, 1fr),
                  gutter: 0pt,
                  [#text(fill: bar-right, size: size-small)[•]],
                  [#text(size: size-small, fill: secondary-text)[#format-markup(b)]]
                )
                #v(0.8pt)
              ]
            ] else [
              #text(size: size-small, fill: secondary-text)[#exp.description]
            ]
          ]
        ]
        #v(section-spacing)

        // Selected Projects
        #if "projects" in content and content.projects.len() > 0 [
          #section-title-bar(content.headings.at("projects", default: "PROGETTI"), bar-color: bar-right, text-color: primary-text, size: size-section, spacing: section-spacing)
          #for proj in content.projects [
            #block(width: 100%, inset: (bottom: section-spacing * 0.6))[
              #text(size: size-sub, weight: "bold", fill: primary-text)[#proj.name]
              #if "tech" in proj [#text(size: size-small, fill: accent-text)[ (#proj.tech)]]\
              #text(size: size-small, fill: secondary-text)[#proj.description]
            ]
          ]
          #v(section-spacing)
        ]

        #section-title-bar(content.headings.volunteer, bar-color: bar-right, text-color: primary-text, size: size-section, spacing: section-spacing)
        #text(size: size-small, fill: secondary-text)[#content.volunteer]
      ]
    )
  ]

  // ==================== GDPR FOOTER ====================
  if show-gdpr and "footer" in content and content.footer != "" [
    #v(1fr)
    #align(center)[
      #text(size: size-tiny, fill: accent-text)[#content.footer]
    ]
  ]
}
