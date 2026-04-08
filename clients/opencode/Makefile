.PHONY: install symlink extension status all

all: install symlink extension

install:
	@echo "Installing OpenCode CLI..."
	@if command -v opencode >/dev/null 2>&1; then \
		echo "OpenCode already installed: $$(opencode --version)"; \
	else \
		curl -fsSL https://opencode.ai/install | bash; \
		echo "Installed: $$(opencode --version)"; \
	fi

symlink:
	@echo "Creating /usr/local/bin/opencode symlink (for VSCode extension host)..."
	@OPENCODE_BIN=$$(command -v opencode 2>/dev/null || echo "$$HOME/.local/bin/opencode"); \
	if [ ! -f "$$OPENCODE_BIN" ]; then \
		echo "ERROR: opencode binary not found. Run 'make install' first."; \
		exit 1; \
	fi; \
	sudo ln -sf "$$OPENCODE_BIN" /usr/local/bin/opencode; \
	echo "Symlinked $$OPENCODE_BIN -> /usr/local/bin/opencode"

extension:
	@echo "Installing VSCode extension..."
	@code --install-extension tanishqkancharla.opencode-vscode
	@echo "Done. Reload VSCode to activate."

status:
	@echo "=== OpenCode Status ==="
	@echo -n "CLI: "; command -v opencode && opencode --version || echo "not found"
	@echo -n "Symlink: "; ls -la /usr/local/bin/opencode 2>/dev/null || echo "not found"
	@echo -n "Extension: "; code --list-extensions 2>/dev/null | grep -i opencode || echo "not installed"
	@echo -n "Config: "; test -f ../../opencode.json && echo "../../opencode.json found" || echo "not found"
