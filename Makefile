VERSION = $(shell git tag -l | tail -n1)

all: release

release:
	git archive --format=tar --prefix=repomd-pattern-builder-${VERSION}/ ${VERSION} | xz -z > repomd-pattern-builder-${VERSION}.tar.xz

clean:
	rm -f *.xz
