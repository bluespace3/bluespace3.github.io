# Blog Preview Skill

Start local development server to preview blog changes before deployment.

## Description

Launches Hugo development server with live reload. Changes to content are reflected immediately in the browser.

## Usage

```bash
# Linux/macOS
./preview.sh

# Windows
preview.bat
```

## What It Does

- Starts Hugo development server on http://localhost:1313
- Enables live reload (auto-refresh on file changes)
- Includes draft posts by default (`-D` flag)

## Requirements

- Hugo (Extended) installed
- No dependencies on Python or other tools

## Manual Preview

```bash
# Start server (with drafts)
hugo server -D

# Start server (without drafts)
hugo server

# Custom port
hugo server -p 8080

# Bind to all interfaces (for network access)
hugo server --bind 0.0.0.0 --baseURL http://your-ip:1313
```

## Example

```bash
./preview.sh

# Output:
# Start building sites …
# hugo v0.140.2...
#                   | EN
# -------------------+-----
#   Pages            |  44
#   Paginator pages  |   0
# ...
# Watching for changes in /var/www/bluespace3.github.io/{archetypes,content,data,layouts,static,themes}
# Watching for config changes in /var/www/bluespace3.github.io/config.toml, /var/www/bluespace3.github.io/hugo.toml
# Serving pages from memory
# Running in Fast Render Mode. For full rebuilds on change: hugo server --disableFastRender
# Web Server is available at http://localhost:1313/ (bind address 127.0.0.1)
# Press Ctrl+C to stop
```

## Access

Open browser and navigate to: http://localhost:1313

## Notes

- Encryption is NOT applied during preview (only during deployment)
- Draft posts are visible with `-D` flag
- Press `Ctrl+C` to stop the server
- Changes are automatically reflected

## Related Skills

- `deploy.md` - Deploy changes after preview
