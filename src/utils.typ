// Utility helpers and components for Typst CV templates

// --- COLOR CONVERTERS & HELPERS ---
#let parse-color(c, default: rgb("1E293B")) = {
  if type(c) == color {
    c
  } else if type(c) == str {
    if c.starts-with("#") {
      rgb(c)
    } else {
      rgb("#" + c)
    }
  } else {
    default
  }
}

// --- LENGTH & DIMENSION PARSER ---
#let parse-length(val, default: 9pt) = {
  if type(val) == length {
    val
  } else if type(val) == float or type(val) == int {
    val * 1pt
  } else if type(val) == str {
    let s = val.trim()
    if s.ends-with("pt") {
      float(s.slice(0, -2)) * 1pt
    } else if s.ends-with("cm") {
      float(s.slice(0, -2)) * 1cm
    } else if s.ends-with("mm") {
      float(s.slice(0, -2)) * 1mm
    } else if s.ends-with("em") {
      float(s.slice(0, -2)) * 1em
    } else {
      default
    }
  } else {
    default
  }
}

// --- ICONS (Clean Typst-native representations) ---
#let icon-phone = [#box(baseline: 10%, text(size: 8.5pt)[📞])]
#let icon-mail = [#box(baseline: 10%, text(size: 8.5pt)[✉])]
#let icon-github = [#box(baseline: 10%, text(size: 8.5pt)[⌥])]
#let icon-location = [#box(baseline: 10%, text(size: 8.5pt)[📍])]
#let icon-calendar = [#box(baseline: 10%, text(size: 8.5pt)[🗓])]
#let icon-link = [#box(baseline: 10%, text(size: 8.5pt)[🔗])]
#let icon-bullet = [•]

// Minimal vector-styled glyphs for modern tech template
#let mini-icon(name, fill: rgb("475569")) = {
  box(baseline: 15%, width: 11pt, height: 11pt)[
    #if name == "mail" [
      #align(center + horizon)[#text(size: 8.5pt, fill: fill)[✉]]
    ] else if name == "phone" [
      #align(center + horizon)[#text(size: 8.5pt, fill: fill)[☎]]
    ] else if name == "github" [
      #align(center + horizon)[#text(size: 8pt, fill: fill, weight: "bold")[GH]]
    ] else if name == "location" [
      #align(center + horizon)[#text(size: 8.5pt, fill: fill)[⌖]]
    ] else if name == "calendar" [
      #align(center + horizon)[#text(size: 8.5pt, fill: fill)[◷]]
    ] else if name == "link" [
      #align(center + horizon)[#text(size: 8.5pt, fill: fill)[↗]]
    ] else [
      #align(center + horizon)[#text(size: 8.5pt, fill: fill)[•]]
    ]
  ]
}

// --- BADGE / SKILL CHIP ---
#let skill-chip(label, bg: rgb("F1F5F9"), stroke: rgb("CBD5E1"), text-color: rgb("1E293B"), font-size: 8pt) = {
  box(
    radius: 3pt,
    fill: bg,
    stroke: 0.5pt + stroke,
    inset: (x: 4.5pt, y: 2pt),
    outset: 0pt,
    baseline: 0%,
    [#text(size: font-size, weight: "medium", fill: text-color)[#label]]
  )
}

// --- SECTION HEADER STYLES ---
#let section-title-modern(title, accent-color: rgb("0F172A"), line-color: rgb("E2E8F0"), size: 11pt, spacing: 4pt) = {
  v(spacing)
  block(width: 100%)[
    #grid(
      columns: (auto, 1fr),
      align: (left + horizon, horizon),
      gutter: 8pt,
      [#text(size: size, weight: "bold", fill: accent-color, tracking: 0.5pt)[#upper(title)]],
      [#line(length: 100%, stroke: 0.8pt + line-color)]
    )
  ]
  v(spacing * 0.4)
}

#let section-title-bar(title, bar-color: rgb("0284C7"), text-color: rgb("0F172A"), size: 11pt, spacing: 4pt) = {
  v(spacing)
  block(width: 100%)[
    #text(size: size, weight: "bold", fill: text-color, tracking: 0.6pt)[#upper(title)]
    #v(-4pt)
    #line(length: 100%, stroke: 1.5pt + bar-color)
  ]
  v(spacing * 0.4)
}


#let section-title-academic(title, accent-color: rgb("1E293B"), size: 11pt, spacing: 4pt) = {
  v(spacing)
  block(width: 100%)[
    #align(left)[
      #text(size: size, weight: "bold", fill: accent-color, font: ("New Computer Modern", "Times New Roman", "Georgia"))[#smallcaps(title)]
      #v(-3pt)
      #line(length: 100%, stroke: 0.5pt + rgb("94A3B8"))
    ]
  ]
  v(spacing * 0.4)
}

// --- BULLET POINT WITH BOLD KEYWORD ---
#let impact-bullet(lead-in, body, bullet-color: rgb("64748B"), text-color: rgb("334155"), font-size: 8.5pt) = {
  grid(
    columns: (10pt, 1fr),
    gutter: 0pt,
    [#align(left)[#text(fill: bullet-color)[•]]],
    [
      #text(fill: text-color, size: font-size)[
        #if lead-in != "" [*#lead-in:* ]#body
      ]
    ]
  )
}

// --- SAFE MARKUP FORMATTER ---
// Converts Markdown double-asterisks (**) to bold without using eval()
// Immune to apostrophes, parentheses, slashes, and special characters
#let format-text(t) = {
  if type(t) != str { return t }
  let clean = t.replace("**", "*")
  let parts = clean.split("*")
  let is-bold = false
  let items = ()
  for p in parts {
    if p != "" {
      if is-bold {
        items.push(strong(p))
      } else {
        items.push(p)
      }
    }
    is-bold = not is-bold
  }
  items.join()
}

#let format-markup = format-text
