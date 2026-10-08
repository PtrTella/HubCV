// Entry point router for Typst Curriculum Vitae
// Automatically routes to the selected template configured in data/cv.yml

#import "/src/templates/modern_tech.typ" as modern_tech
#import "/src/templates/split_header.typ" as split_header
#import "/src/templates/academic_research.typ" as academic_research
#import "/src/templates/nordic_sidebar.typ" as nordic_sidebar

#let data-path = sys.inputs.at("data_path", default: "/data/cv.yml")
#let data = yaml(data-path)
#let template-name = data.config.at("template", default: "split_header")

#if template-name == "split_header" {
  split_header.render(data)
} else if template-name == "modern_tech" {
  modern_tech.render(data)
} else if template-name == "academic_research" {
  academic_research.render(data)
} else if template-name == "nordic_sidebar" {
  nordic_sidebar.render(data)
} else {
  split_header.render(data)
}
