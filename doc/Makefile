# Minimal makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = pyggi
SOURCEDIR     = .
BUILDDIR      = ../../pyggi-docs

html: Makefile
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

buildandcommithtml: html
	cd $(BUILDDIR)/html; git add . ; git commit -m "rebuilt docs"; git push origin gh-pages
