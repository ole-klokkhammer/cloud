# cline

## Setup - Web Browsing Configuration

Cline's MCP servers are configured in your VS Code user settings:

**File:** `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

### What Was Added

The following MCP servers have been added to Cline:

| Server | Purpose |
|--------|---------|
| `browser` | Visit websites and extract content using a headless browser |
| `duckduckgo-search` | Search the web via DuckDuckGo |

### Configuration File

Your Cline MCP settings now include:
```json
{
  "mcpServers": {
    "duckduckgo-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-duckduckgo"]
    },
    "browser": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-browser"]
    }
  }
}
```

### How to Use

1. **Restart Cline** in VS Code (or reload the window)
2. Ask questions like:
   - "Visit https://example.com and extract all text"
   - "Find information about [topic] on the web"
   - "Search for latest news about technology"

### Requirements

Make sure you have Node.js installed (for npx to work):
```bash
node --version
npm --version
```

---

**Note:** OpenCode uses a different config file (`opencode.json` in project root). Both tools can coexist with their own MCP configurations.