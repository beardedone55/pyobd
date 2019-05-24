###########################################################
#
# GNUmakefile
#
# Copyright (C) 2019 Brian LePage (github.com/beardedone55)
#
# This make file builds and packages pyobd
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to:
#
#     Free Software Foundation, Inc.
#     51 Franklin Street, Fifth Floor
#     Boston, MA  02110-1301, USA.
#
###########################################################

PACKAGE_NAME := pyobd_beardedone55
WHL_VERSION := $(shell ./setup.py -V)
DEB_VERSION := $(shell head -1 debian/changelog | sed 's/^.*(\(.*\)).*$$/\1/')

PYOBD_WHL := dist/$(PACKAGE_NAME)-$(WHL_VERSION)-py3-none-any.whl
DEB_PACKAGE_NAME := python3-$(subst _,-,$(PACKAGE_NAME))
PYOBD_DEB := ../$(DEB_PACKAGE_NAME)_$(DEB_VERSION)_all.deb

default: build ;

PYOBD_DEPS := pyobd_beardedone55/__init__.py
PYOBD_DEPS += pyobd_beardedone55/obd2_codes.py
PYOBD_DEPS += pyobd_beardedone55/obd_io.py
PYOBD_DEPS += pyobd_beardedone55/obd_sensors.py
PYOBD_DEPS += pyobd_beardedone55/pyobdGUI.py
PYOBD_DEPS += pyobd_beardedone55/icons_free/check-icon2.png
PYOBD_DEPS += pyobd_beardedone55/icons_free/delete-icon.png
PYOBD_DEPS += pyobd_beardedone55/icons_free/COPYING
PYOBD_DEPS += pyobd_beardedone55/icons_pubdomain/COPYING
PYOBD_DEPS += pyobd_beardedone55/icons_pubdomain/check-engine-off.png
PYOBD_DEPS += pyobd_beardedone55/icons_pubdomain/check-engine.png
PYOBD_DEPS += pyobd_beardedone55/icons_pubdomain/Motorkontrollleuchte.svg
PYOBD_DEPS += pyobd_beardedone55/icons_gpl/Checkbox-Empty-icon.png
PYOBD_DEPS += pyobd_beardedone55/icons_gpl/Checkbox-Full-icon.png
PYOBD_DEPS += pyobd_beardedone55/icons_gpl/COPYING
PYOBD_DEPS += pyobd_beardedone55/icons_gpl/gpl-3.0.txt
PYOBD_DEPS += README.md
PYOBD_DEPS += setup.py
PYOBD_DEPS += MANIFEST.in
PYOBD_DEPS += COPYING
PYOBD_DEPS += pyobd

build: $(PYOBD_DEPS)
	python3 setup.py build -e "/usr/bin/env python3"

wheel: $(PYOBD_WHL) ;

$(PYOBD_WHL): $(PYOBD_DEPS)
	python3 setup.py bdist_wheel

deb: $(PYOBD_DEB) ;

check_version:
	@[ "$(WHL_VERSION)" = "$(DEB_VERSION)" ] || { echo "***Version Mismatch Between changelog and setup.py***"; exit 1; }

$(PYOBD_DEB): $(PYOBD_DEPS) | check_version
	debuild -us -uc --lintian-opts --profile debian

install:
	python3 setup.py install --root $(DESTDIR)/ $(INSTALL_OPTS)

uninstall:
	pip3 uninstall $(PACKAGE_NAME)

clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf pyobd_beardedone55.egg-info
	-rm -rf __pycache__
	-rm -rf pyobd_beardedone55/__pycache__
	-[ ! -f $(PYOBD_DEB) ] || rm ../$(DEB_PACKAGE_NAME)*
