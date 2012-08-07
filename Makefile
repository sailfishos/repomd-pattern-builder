VERSION = $(shell git tag -l | tail -n1)

all:

install:
	mkdir -p $(DESTDIR)/usr/bin/
	cp repomd-pattern-builder.py $(DESTDIR)/usr/bin/

release:
	git archive --format=tar --prefix=repomd-pattern-builder-${VERSION}/ ${VERSION} | xz -z > repomd-pattern-builder-${VERSION}.tar.xz

clean:
	rm -f *.xz
