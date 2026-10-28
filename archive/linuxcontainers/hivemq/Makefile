# HiveMQ CE on the hivemq LXC — deploy, operate, and sanity-check the broker.
#
# Layout (profile.yaml bind-mounts /config, /data and /extensions from the host's
# /ssd/appdata/hivemq/*, so they survive reinstalls):
#   /opt/hivemq-ce/<version>/        release unpacked from the community-edition zip
#   /opt/hivemq                   -> symlink to the active release (fixed unit path)
#   /config/config.xml                from config/config.xml
#   /etc/systemd/system/hivemq.service from config/hivemq.service
#
#   make deploy                       install the release + config + unit, restart, check
#   make status | logs | logs-f | errors
#   make check                        unit, ports, extensions, recent errors
#   make smoke                        publish/subscribe round trip inside the instance
#   make VERSION=2026.5 deploy        upgrade;  make rollback TO=2025.5  to go back
#   make ext NAME=hivemq-allow-all-extension
#
# Run where the `lxc` CLI is configured for the `core:` remote.
# Extension builds need a local JDK 17+ (gradlew fetches its own Gradle).

LXC      := core:hivemq
LXC_BIN  ?= lxc

VERSION  ?= 2026.5
ZIP      := hivemq-ce-$(VERSION).zip
URL      := https://github.com/hivemq/hivemq-community-edition/releases/download/$(VERSION)/$(ZIP)
CACHE    ?= /tmp/$(ZIP)

RELEASE     := /opt/hivemq-ce/$(VERSION)
# HIVE_DIR is the active-release symlink; bin/run.sh derives hivemq.home from its path.
HIVE_DIR    ?= /opt/hivemq
RUN_USER    ?= hivemq
UNIT        ?= hivemq.service
CONFIG_DIR  ?= /config
DATA_DIR    ?= /data
EXT_DIR     ?= /extensions
MQTT_PORT   ?= 1883
WS_PORT     ?= 8000
JAVA_PKG    ?= openjdk-17-jre-headless

EXT_SRC   := extensions
NAME      ?= hivemq-allow-all-extension
FROM      ?=
N         ?= 200
TO        ?= $(VERSION)

.PHONY: help prereqs dirs perms install activate adopt config unit deploy \
        start stop restart status logs logs-f errors check smoke client version \
        diff ext ext-builtin ext-all rollback uninstall

help: ## list the targets
	@echo "HiveMQ CE on $(LXC) — target version $(VERSION)"
	@grep -hE '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) \
	  | awk -F':.*## ' '{printf "  \033[36m%-11s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- provisioning

prereqs: ## install the JRE and unzip inside the instance
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  need=""; \
	  command -v java  >/dev/null || need="$$need $(JAVA_PKG)"; \
	  command -v unzip >/dev/null || need="$$need unzip"; \
	  if [ -n "$$need" ]; then \
	    apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq $$need; \
	  fi; \
	  java -version 2>&1 | head -n 1'

dirs: ## create the hivemq service user and the mounted folders
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  id -u $(RUN_USER) >/dev/null 2>&1 || \
	    useradd --system --home-dir $(HIVE_DIR) --shell /usr/sbin/nologin $(RUN_USER); \
	  install -d -o $(RUN_USER) -g $(RUN_USER) $(CONFIG_DIR) $(DATA_DIR) $(EXT_DIR); \
	  ls -ld $(CONFIG_DIR) $(DATA_DIR) $(EXT_DIR)'

perms: ## hand the mounted folders back to the service user (fixes EACCES on /data/data.lock)
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  set -e; \
	  id -u $(RUN_USER) >/dev/null 2>&1 || { echo "no $(RUN_USER) user - run make dirs first" >&2; exit 1; }; \
	  if ! systemctl is-active --quiet $(UNIT); then \
	    stray=$$(pgrep -f hivemq.jar || true); \
	    if [ -n "$$stray" ]; then \
	      echo "a HiveMQ process is running outside systemd (pid $$stray) - it holds the data lock and creates root-owned files:" >&2; \
	      echo "  lxc exec $(LXC) -- kill $$stray" >&2; exit 1; \
	    fi; \
	  fi; \
	  chown -R $(RUN_USER):$(RUN_USER) $(CONFIG_DIR) $(DATA_DIR) $(EXT_DIR) || true; \
	  bad=$$(find $(CONFIG_DIR) $(DATA_DIR) $(EXT_DIR) ! -user $(RUN_USER) 2>/dev/null | head -n 5); \
	  if [ -n "$$bad" ]; then \
	    echo "still not owned by $(RUN_USER):" >&2; echo "$$bad" | sed "s/^/  /" >&2; \
	    echo "these need a chown on the LXD host under /ssd/appdata/hivemq (see the Uid map in: lxc info $(LXC))" >&2; exit 1; \
	  fi; \
	  echo "$(CONFIG_DIR) $(DATA_DIR) $(EXT_DIR) all owned by $(RUN_USER)"; \
	  ls -ln $(DATA_DIR) | head -n 5'

install: prereqs dirs ## download + unpack the release into /opt/hivemq-ce/<version>
	@test -f $(CACHE) || curl -fsSLo $(CACHE) $(URL)
	@echo "local zip: $$(wc -c < $(CACHE)) bytes (expect ~100M)"
	$(LXC_BIN) file push $(CACHE) $(LXC)/tmp/$(ZIP)
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  set -e; \
	  if [ ! -s $(RELEASE)/bin/hivemq.jar ]; then \
	    rm -rf $(RELEASE); \
	    install -d -m 0755 /opt/hivemq-ce; \
	    unzip -tq /tmp/$(ZIP) >/dev/null || { echo "the zip is corrupt or truncated - delete $(CACHE) and re-run make install" >&2; rm -f /tmp/$(ZIP); exit 1; }; \
	    unzip -q /tmp/$(ZIP) -d /opt/hivemq-ce; \
	    mv /opt/hivemq-ce/hivemq-ce-$(VERSION) $(RELEASE); \
	    test -s $(RELEASE)/bin/hivemq.jar || { echo "$(RELEASE)/bin/hivemq.jar missing - bad zip, delete $(CACHE) and re-run" >&2; rm -rf $(RELEASE); exit 1; }; \
	  fi; \
	  rm -f /tmp/$(ZIP); \
	  chown -R $(RUN_USER):$(RUN_USER) /opt/hivemq-ce; \
	  chmod 0755 $(RELEASE)/bin/*.sh; \
	  du -sh $(RELEASE)'
	@$(MAKE) --no-print-directory activate VERSION=$(VERSION)

activate: ## point /opt/hivemq at VERSION (used by install and rollback)
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  set -e; \
	  test -x $(RELEASE)/bin/run.sh || { echo "$(RELEASE) not installed - run: make install VERSION=$(VERSION)" >&2; exit 1; }; \
	  if [ -e $(HIVE_DIR) ] && [ ! -L $(HIVE_DIR) ]; then \
	    echo "$(HIVE_DIR) is a real directory, not a symlink. Move it aside first:" >&2; \
	    echo "  lxc exec $(LXC) -- mv $(HIVE_DIR) /opt/hivemq-ce/<its-version> && make activate VERSION=<its-version>" >&2; \
	    exit 1; \
	  fi; \
	  ln -sfn $(RELEASE) $(HIVE_DIR); \
	  echo "$(HIVE_DIR) -> $$(readlink -f $(HIVE_DIR))"'

adopt: ## migrate an existing flat /opt/hivemq install into /opt/hivemq-ce/<version> + symlink
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  set -e; \
	  if [ -L $(HIVE_DIR) ]; then echo "$(HIVE_DIR) already points at $$(readlink $(HIVE_DIR)) - nothing to adopt"; exit 0; fi; \
	  test -d $(HIVE_DIR) || { echo "no $(HIVE_DIR) directory to adopt" >&2; exit 1; }; \
	  src=$(HIVE_DIR); v="$(FROM)"; \
	  if [ ! -x $$src/bin/run.sh ]; then \
	    sub=$$(ls -1 $$src | head -n 1); \
	    if [ -z "$$sub" ] || [ ! -x $$src/$$sub/bin/run.sh ]; then \
	      echo "no bin/run.sh under $(HIVE_DIR) - move it into /opt/hivemq-ce by hand" >&2; exit 1; \
	    fi; \
	    src=$$src/$$sub; \
	    if [ -z "$$v" ]; then v=$$sub; fi; \
	  fi; \
	  if [ -z "$$v" ]; then \
	    v=$$(journalctl -u $(UNIT) --no-pager 2>/dev/null | sed -n "s/.*HiveMQ version: //p" | tail -n 1); \
	  fi; \
	  test -n "$$v" || { echo "cannot tell which version is installed - run: make adopt FROM=<version>" >&2; exit 1; }; \
	  test ! -e /opt/hivemq-ce/$$v || { echo "/opt/hivemq-ce/$$v already exists - sort that out by hand" >&2; exit 1; }; \
	  systemctl stop $(UNIT) || true; \
	  install -d -m 0755 /opt/hivemq-ce; \
	  mv $$src /opt/hivemq-ce/$$v; \
	  if [ -d $(HIVE_DIR) ]; then mv $(HIVE_DIR) $(HIVE_DIR).old; echo "kept leftovers in $(HIVE_DIR).old - check them, then delete"; fi; \
	  chown -R $(RUN_USER):$(RUN_USER) /opt/hivemq-ce; \
	  ln -sfn /opt/hivemq-ce/$$v $(HIVE_DIR); \
	  echo "adopted /opt/hivemq-ce/$$v and pointed $(HIVE_DIR) at it"; \
	  systemctl start $(UNIT); \
	  systemctl is-active $(UNIT) || true'

rollback: ## re-point /opt/hivemq at TO=<version> and restart
	@$(MAKE) --no-print-directory activate VERSION=$(TO)
	$(LXC_BIN) exec $(LXC) -- systemctl restart $(UNIT)

config: ## push config/config.xml -> /config/config.xml
	$(LXC_BIN) file push config/config.xml $(LXC)$(CONFIG_DIR)/config.xml
	@$(LXC_BIN) exec $(LXC) -- chown $(RUN_USER):$(RUN_USER) $(CONFIG_DIR)/config.xml
	@$(LXC_BIN) exec $(LXC) -- sh -c 'test -f $(CONFIG_DIR)/logback.xml || install -m 0644 -o $(RUN_USER) -g $(RUN_USER) $(HIVE_DIR)/conf/logback.xml $(CONFIG_DIR)/logback.xml'
	@echo "config pushed — 'make restart' to apply (HiveMQ reads config.xml at boot only)"

unit: ## push config/hivemq.service -> /etc/systemd/system, reload + enable
	$(LXC_BIN) file push config/hivemq.service $(LXC)/etc/systemd/system/$(UNIT)
	@$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	@$(LXC_BIN) exec $(LXC) -- systemctl enable $(UNIT)

deploy: install config unit ## install the release, push config + unit, restart, check
	@$(LXC_BIN) exec $(LXC) -- systemctl restart $(UNIT)
	@$(MAKE) --no-print-directory check

# -------------------------------------------------------------- life management

start: ## systemctl start
	@$(LXC_BIN) exec $(LXC) -- systemctl start $(UNIT)

stop: ## systemctl stop
	@$(LXC_BIN) exec $(LXC) -- systemctl stop $(UNIT)

restart: ## systemctl restart (needed after any config.xml or extension change)
	@$(LXC_BIN) exec $(LXC) -- systemctl restart $(UNIT)
	@$(MAKE) --no-print-directory check

status: ## unit state, active release, listening MQTT/WebSocket ports
	@$(LXC_BIN) exec $(LXC) -- systemctl status $(UNIT) --no-pager
	@$(LXC_BIN) exec $(LXC) -- systemctl show $(UNIT) \
	  -p ActiveState -p SubState -p MainPID -p ExecMainStartTimestamp

logs: ## last N journal lines (make logs N=1000)
	@$(LXC_BIN) exec $(LXC) -- journalctl -u $(UNIT) -n $(N) --no-pager

logs-f: ## follow the journal (Ctrl-C to stop)
	$(LXC_BIN) exec $(LXC) -- journalctl -u $(UNIT) -f

errors: ## recent warning/error lines only
	@$(LXC_BIN) exec $(LXC) -- journalctl -u $(UNIT) -p warning -n $(N) --no-pager

# -------------------------------------------------------------------- checking

check: ## is the broker serving? unit, ports, extensions, recent errors
	@$(LXC_BIN) exec $(LXC) -- bash -c '\
	  printf "%-12s %s\n" unit     "$$(systemctl is-active $(UNIT))"; \
	  printf "%-12s %s\n" pid      "$$(systemctl show $(UNIT) -p MainPID --value)"; \
	  h=$$(readlink $(HIVE_DIR) 2>/dev/null); \
	  [ -n "$$h" ] || h="MISSING - run make activate"; \
	  printf "%-12s %s\n" home     "$$h"; \
	  printf "%-12s %s\n" java     "$$(java -version 2>&1 | head -n 1)"; \
	  d=$$(test -w $(DATA_DIR) && echo writable || echo "NOT writable - run make perms"); \
	  printf "%-12s %s\n" data     "$$d"; \
	  for p in $(MQTT_PORT) $(WS_PORT); do \
	    if ss -lnt | grep -q ":$$p "; then echo "port         $$p listening"; \
	    else echo "port         $$p NOT LISTENING"; fi; \
	  done; \
	  printf "%-12s %s\n" extensions "$$(ls -1 $(EXT_DIR) 2>/dev/null | tr "\n" " ")"; \
	  if [ -z "$$(ls -A $(EXT_DIR) 2>/dev/null)" ]; then \
	    echo "WARN         $(EXT_DIR) is empty — no auth extension, clients will be rejected"; \
	  fi; \
	  echo "recent warnings/errors:"; \
	  journalctl -u $(UNIT) -p warning -n 15 --no-pager | sed "s/^/  /"'

smoke: ## publish/subscribe round trip inside the instance (needs mosquitto-clients)
	@$(LXC_BIN) exec $(LXC) -- bash -c '\
	  command -v mosquitto_pub >/dev/null || { echo "mosquitto-clients missing — run: make client"; exit 1; }; \
	  t=hivemq-make/ping; \
	  out=$$( { timeout 10 mosquitto_sub -h 127.0.0.1 -p $(MQTT_PORT) -t "$$t" -C 1 -v & \
	           sleep 1; \
	           mosquitto_pub -h 127.0.0.1 -p $(MQTT_PORT) -t "$$t" -m pong; \
	           wait; } 2>&1 ); \
	  case "$$out" in \
	    *pong*) echo "  OK   $$out" ;; \
	    *)      echo "  FAIL nothing came back: $$out"; exit 1 ;; \
	  esac'

client: ## install mosquitto-clients in the instance (used by 'make smoke')
	@$(LXC_BIN) exec $(LXC) -- sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y -qq mosquitto-clients'

version: ## active vs installed vs target release
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  echo "target     $(VERSION)"; \
	  echo "active     $$(readlink $(HIVE_DIR) 2>/dev/null || echo none)"; \
	  echo "installed  $$(ls -1 /opt/hivemq-ce 2>/dev/null | tr "\n" " ")"'

diff: ## diff local config/config.xml against the running one
	@if ! $(LXC_BIN) file pull $(LXC)$(CONFIG_DIR)/config.xml /tmp/hivemq.running.xml 2>/dev/null; then \
	  echo "no $(CONFIG_DIR)/config.xml on $(LXC) — 'make config' to push the repo copy"; exit 1; \
	fi
	@diff -u config/config.xml /tmp/hivemq.running.xml \
	  && echo "config in sync" \
	  || echo "^ drift — 'make config' pushes the repo copy"

# ------------------------------------------------------------------ extensions

ext: ## build extensions/NAME and drop it into /extensions (gradlew, needs a local JDK)
	@test -f $(EXT_SRC)/$(NAME)/build.gradle.kts || { echo "no build file at $(EXT_SRC)/$(NAME) - try: make ext-builtin" >&2; exit 1; }
	@command -v java >/dev/null 2>&1 || test -n "$$JAVA_HOME" || { \
	  echo "no java on this machine - gradlew builds the extension locally." >&2; \
	  echo "either install a JDK 17 (sudo apt install openjdk-17-jdk-headless) or, for the" >&2; \
	  echo "bundled allow-all extension, run: make ext-builtin" >&2; exit 1; }
	cd $(EXT_SRC)/$(NAME) && ./gradlew --no-daemon clean hivemqExtensionZip
	@zip=$$(ls -1t $(EXT_SRC)/$(NAME)/build/hivemq-extension/*.zip | head -n 1); \
	base=$$(basename $$zip); \
	echo "pushing $$base"; \
	$(LXC_BIN) file push $$zip $(LXC)/tmp/$$base; \
	$(LXC_BIN) exec $(LXC) -- sh -c "set -e; \
	  rm -rf $(EXT_DIR)/$(NAME)-*; \
	  unzip -qo /tmp/$$base -d $(EXT_DIR); \
	  rm -f /tmp/$$base; \
	  chown -R $(RUN_USER):$(RUN_USER) $(EXT_DIR); \
	  ls -1 $(EXT_DIR)"; \
	echo "extension pushed — 'make restart' to load it"

ext-builtin: ## copy the extension bundled in the active release into /extensions (no local JDK)
	@$(LXC_BIN) exec $(LXC) -- sh -c '\
	  set -e; \
	  src=$(HIVE_DIR)/extensions/$(NAME); \
	  test -d $$src || { echo "no bundled extension at $$src - run make install first" >&2; exit 1; }; \
	  install -d -o $(RUN_USER) -g $(RUN_USER) $(EXT_DIR); \
	  rm -rf $(EXT_DIR)/$(NAME) $(EXT_DIR)/$(NAME)-*; \
	  cp -a $$src $(EXT_DIR)/$(NAME); \
	  chown -R $(RUN_USER):$(RUN_USER) $(EXT_DIR); \
	  ls -1 $(EXT_DIR); \
	  echo "copied $(NAME) into $(EXT_DIR) - restart to load: make restart"'

ext-all: ## build + push every extension under extensions/
	@for b in $(wildcard $(EXT_SRC)/*/build.gradle.kts); do \
	  d=$$(basename $$(dirname $$b)); \
	  echo "=== $$d"; \
	  $(MAKE) --no-print-directory ext NAME=$$d || exit 1; \
	done

# ------------------------------------------------------------------- teardown

uninstall: ## stop + disable + drop the unit (keeps releases, config, data, extensions)
	@$(LXC_BIN) exec $(LXC) -- systemctl disable --now $(UNIT) || true
	@$(LXC_BIN) exec $(LXC) -- rm -f /etc/systemd/system/$(UNIT)
	@$(LXC_BIN) exec $(LXC) -- systemctl daemon-reload
	@echo "unit removed. $(HIVE_DIR), $(CONFIG_DIR), $(DATA_DIR), $(EXT_DIR) untouched."
