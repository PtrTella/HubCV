.PHONY: setup run build build-it build-en clean

setup:
	uv venv
	uv pip install -r requirements.txt

run:
	uv run streamlit run app.py

build:
	uv run python3 -c "import typst; typst.compile('src/cv.typ', output='cv.pdf', root='.')"

build-it:
	uv run python3 -c "import yaml, typst; d=yaml.safe_load(open('data/cv.yml')); d['config']['lang']='it'; yaml.dump(d, open('data/cv.yml','w'), allow_unicode=True); typst.compile('src/cv.typ', output='cv_it.pdf', root='.')"

build-en:
	uv run python3 -c "import yaml, typst; d=yaml.safe_load(open('data/cv.yml')); d['config']['lang']='en'; yaml.dump(d, open('data/cv.yml','w'), allow_unicode=True); typst.compile('src/cv.typ', output='cv_en.pdf', root='.')"

clean:
	rm -f cv.pdf cv_it.pdf cv_en.pdf
