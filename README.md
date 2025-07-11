# Jirato 🍨

AI-Powered JIRA Ticket Creator with Ollama integration and a delightful gelato theme.

## Features

- 🎫 **AI-Generated JIRA Tickets** with preview & edit workflow
- 🤖 **Ollama Integration** for intelligent content generation
- 🍨 **Gelato Theme** - beautiful, minimalist design
- 📋 **Multiple Project Support** - HI, HB, HSF, HSH, HSI, HSS, HSW
- 📝 **User Story Templates** - Connextra format support
- ⚙️ **Softpack Admin** - special handling for HI project tickets

## Quick Start

### Setup
```bash
# Full setup (recommended)
make full-setup

# Or step by step:
make install      # Install dependencies
make setup        # Create .env file
```

### Usage
1. **Edit .env** and add your `JIRA_TOKEN`
2. **Run the app**: `make run` (port 80, production) or `make dev` (port 8000, development)
3. **Enter your JIRA username**
4. **Select project** from dropdown (HI, HB, HSF, etc.)
5. **Describe your request** (Slack conversations, brain dumps, etc.)
6. **Optional**: Check "Softpack Admin" (HI only) or "User Story" format
7. **Generate Preview** → Review & Edit → **Create Ticket**

## Project Support

| Project | ID | Description |
|---------|----|-------------|
| HI | 14101 | HGI Informatics |
| HB | 14800 | HGI Bioinformatics |
| HSF | 14300 | HGI Software Farmers |
| HSH | 14301 | HGI Software HailQC |
| HSI | 14200 | HGI Software iBackup |
| HSS | 14202 | HGI Software Softpack |
| HSW | 14201 | HGI Software wrstat |

## Special Features

### 🎯 User Story Template
When enabled, generates tickets using the Connextra format:
> "As a [user], I want [feature] so that [benefit]"

### ⚙️ Softpack Admin
- **Available only for HI project**
- Sets `customfield_10110` to `None` instead of `"HI-229"`
- Automatically disabled for other projects

## API Endpoints

- `GET /` - Web interface
- `POST /preview-ticket` - Generate AI preview
- `POST /create-ticket` - Create JIRA ticket
- `GET /health` - Health check

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JIRA_TOKEN` | JIRA API token | Required |
| `OLLAMA_REMOTE_HOST` | Ollama server URL | `http://ollama.hgi.sanger.ac.uk:11434` |

## Development

```bash
# Install dependencies and setup
make full-setup

# Run with auto-reload
make dev

# Check environment
make check-env

# Clean up
make clean
```

Visit http://localhost:8000 to start creating tickets! 🍨✨
