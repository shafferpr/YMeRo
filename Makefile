PIP ?= python3 -m pip
CMAKE_FLAGS ?= "-DCMAKE_CXX_COMPILER=/usr/bin/g++ -DCMAKE_C_COMPILER=/usr/bin/gcc"

build:
	mkdir -p build/
	(cd build/;	cmake ${CMAKE_FLAGS} ../)
	make -C build/ -j
	cd ..

install: build
	$(PIP) install . --user --upgrade

uninstall:
	$(PIP) uninstall ymero

docs:
	make -C docs/

test: install
	(cd tests; ymr.make test)

clean:; rm -rf build

.PHONY: install uninstall build test clean docs
