# Settings Guide

All settings are configured via environment variables (`.env` file) or the Settings panel in the UI.

## Essential Settings

| Setting | What It Does | Default |
|---------|-------------|---------|
| **LLM Backend** | Which AI provider to use | `anthropic` |
| **API Key** | Your Anthropic API key (or use OAuth) | — |
| **Model** | Which model for reasoning | `claude-sonnet-4-6` |
| **Gate Mode** | Whether to ask for approval at key decision points | `auto` |
| **Output Format** | What files to produce | `all` (md + tex + pdf) |

## LLM Backend Options

### Anthropic (default)
Set your `ANTHROPIC_API_KEY` in the Settings panel or `.env` file.

### Claude Pro/Max (OAuth)
If you have a Claude Pro or Max subscription, you can use it without an API key:
1. Set **Auth Mode** to `oauth` in Settings
2. The app will use `ccproxy` to authenticate via your Claude subscription

### OpenRouter
Use any model via OpenRouter:
1. Set **LLM Backend** to `openrouter`
2. Enter your OpenRouter API key

### Local Models
Run with a local model (vLLM, Ollama, LM Studio):
1. Set **LLM Backend** to `local`
2. It defaults to `http://localhost:8000/v1`

## Paper Output

| Setting | Options | What It Means |
|---------|---------|--------------|
| **Output Format** | `all` | Produces .md, .tex, and .pdf (needs pdflatex for PDF) |
| | `latex` | Produces .tex and .pdf only |
| | `markdown` | Produces .md only |

## Gate Mode

Gates are decision points where the system pauses for review:

| Mode | Behavior |
|------|----------|
| **none** | Runs fully autonomously — no pauses |
| **auto** | Pauses only when confidence is low or something looks wrong |
| **human** | Pauses at every gate for your approval |

**Recommended:** Start with `auto`. Switch to `human` if you want more control over the research direction.

## PDF Extraction

When the system finds papers, it tries to extract full text from PDFs:

| Setting | Default | What It Does |
|---------|---------|-------------|
| **PDF Backend** | `pdfplumber` | Lightweight, fast, works for most papers |
| **PDF Backend** | `docling` | ML-powered, better for complex layouts (requires extra install) |
| **Use PDF** | `true` | Enable/disable PDF extraction |
| **PDF Papers** | `3` | Max papers to extract full text from |

## Zotero Integration

Connect your Zotero library for bidirectional paper management:

1. Get your API key at [zotero.org/settings/keys](https://www.zotero.org/settings/keys)
2. Set `ZOTERO_API_KEY` and `ZOTERO_LIBRARY_ID` in Settings
3. Use `from-zotero` to import collections
4. Use `push-to-zotero` to sync discoveries back

## Institutional Library Access

If you have institutional access to academic papers:

1. Run `eurekalab library-auth` to set up
2. Configure your proxy: `eurekalab library-set-proxy <url>`
3. Import browser cookies: `eurekalab library-import-cookies`
4. Test access: `eurekalab library-test <doi>`

This lets EurekaLab download full-text papers through your institution's subscriptions.
