all: lukkari.py

lukkari.py: lukkari/*.py
	zip --quiet lukkari lukkari/*.py
	zip --quiet --junk-paths lukkari lukkari/__main__.py
	echo '#!/usr/bin/env python3' > lukkari.py
	cat lukkari.zip >> lukkari.py
	rm lukkari.zip
	chmod +x lukkari.py

.PHONY: all clean

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm lukkari.zip lukkari.py || true
