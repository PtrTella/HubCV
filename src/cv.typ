// Entry point router for Typst Curriculum Vitae
// Automatically routes to the selected template configured in data/cv.yml

#import "/src/templates/modern_tech.typ" as modern_tech
#import "/src/templates/split_header.typ" as split_header
#import "/src/templates/academic_research.typ" as academic_research
#import "/src/templates/nordic_sidebar.typ" as nordic_sidebar

#let data-path = sys.inputs.at("data_path", default: "/data/cv.yml")
#let raw-data = yaml(data-path)

// Ensure data is a valid dictionary
#let data = if type(raw-data) == dictionary { raw-data } else { (:) }
#let cfg = data.at("config", default: (:))
#let template-name = cfg.at("template", default: "split_header")
#let req-lang = cfg.at("lang", default: "it")

// Find available languages in data (excluding config and personal)
#let available-langs = data.keys().filter(k => k != "config" and k != "personal")
#let active-lang = if req-lang in available-langs {
  req-lang
} else if available-langs.len() > 0 {
  available-langs.at(0)
} else {
  "it"
}

// Ensure active-lang content dictionary exists
#let active-content = data.at(active-lang, default: (:))
#let sanitized-config = cfg + (lang: active-lang)
#let sanitized-data = data + (config: sanitized-config) + ((active-lang): active-content)

#if template-name == "split_header" {
  split_header.render(sanitized-data)
} else if template-name == "modern_tech" {
  modern_tech.render(sanitized-data)
} else if template-name == "academic_research" {
  academic_research.render(sanitized-data)
} else if template-name == "nordic_sidebar" {
  nordic_sidebar.render(sanitized-data)
} else {
  split_header.render(sanitized-data)
}

