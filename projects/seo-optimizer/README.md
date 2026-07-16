# SEO Optimizer — Engineering Content Generator

LLM-powered **content ingestion, Q&A generation, and publishing workflow** for a Herndon, VA engineering firm — useful portfolio signal for **business technology solutions** and applied AI automation roles.

Windows desktop build: articles, scraping, AI-assisted posts. Shipped here as launcher scripts plus this README; the runnable `.exe` and `_internal/` bundle stay **local** (see repo root `.gitignore`).

## Quick start (local machine)

1. Keep this folder **fully extracted** (not inside a zip).
2. Run **`EngineeringContentGenerator.exe`** (generated build — present on your PC only).
3. Wait for startup, then open **http://localhost:5001**
4. Sign in with the credentials from your project setup (defaults were distributed with your build).

## Optional

- **Start Menu:** run `create_installer.bat` or `create_installer.ps1`
- **Diagnostics:** `diagnostics.bat`
- **Launch:** `launch_app.bat`

## Features

- Upload articles (PDF, Word, HTML, Markdown, text, RTF)
- Scrape from URLs
- Generate Q&A-style posts via AI (OpenAI or Groq)
- Manage and export content

## Runtime notes

- App URL: **http://localhost:5001**
- Database: `app.db` (next to the executable)
- Uploads: `uploads/` next to the app

## System requirements

- Windows 10+
- No system Python required for the frozen `.exe` build
