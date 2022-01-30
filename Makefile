PYTHON := python3
SUDO := sudo

OWNER := thombashi
REPO := elasticsearch-faker

BUILD_WORK_DIR := _work
PKG_BUILD_DIR := $(BUILD_WORK_DIR)/$(REPO)


.PHONY: build-remote
build-remote: clean
	@mkdir -p $(BUILD_WORK_DIR)
	@cd $(BUILD_WORK_DIR) && \
		git clone https://github.com/$(OWNER)/$(REPO).git --depth 1 && \
		cd $(REPO) && \
		$(PYTHON) -m tox -e build
	ls -lh $(PKG_BUILD_DIR)/dist/*

.PHONY: build
build: clean
	@$(PYTHON) -m tox -e build
	ls -lh dist/*

.PHONY: check
check:
	@$(PYTHON) -m tox -e lint

.PHONY: clean
clean:
	@rm -rf $(BUILD_WORK_DIR)
	@$(PYTHON) -m tox -e clean

.PHONY: fmt
fmt:
	@$(PYTHON) -m tox -e fmt

.PHONY: release
release:
	@cd $(PKG_BUILD_DIR) && $(PYTHON) setup.py release --sign --search-dir elasticsearch_faker
	@make clean

.PHONY: setup-deb-build
setup-deb-build:
	@$(SUDO) apt -qq update
	@$(SUDO) apt install -qq -y --no-install-recommends git fakeroot rename

.PHONY: setup-ci
setup-ci:
	@$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade tox

.PHONY: setup
setup: setup-ci
	@$(PYTHON) -m pip install -q --disable-pip-version-check --upgrade -e .[test] releasecmd
	@$(PYTHON) -m pip check
