# Project Showcase (monorepo)

One GitHub repository for the landing page, shipped projects, and McCombs capstone work. Push from this folder only.

**Repository:** [github.com/FredZaser1111/Project-Showcase](https://github.com/FredZaser1111/Project-Showcase)

**Resume-friendly site (after GitHub Pages is enabled):** [fredzaser1111.github.io/Project-Showcase](https://fredzaser1111.github.io/Project-Showcase/)

---

## Layout

| Path | Contents |
| --- | --- |
| `index.html` | Landing page for GitHub Pages |
| `projects/seo-optimizer/` | SEO Optimizer (Engineering Content Generator — scripts + docs; frozen `.exe` stays local) |
| `projects/nba-z-lock/` | NBA Z Lock (Python app; see its `README.md`) |
| `projects/automated-workflows/` | XGBoost + LangGraph agents (maintenance, loan underwriting, churn) |
| `projects/listing-orchestrator/` | AI listing workflow → Shopify / eBay / Etsy (Cozy Connoisseur production path) |
| `projects/capstones/` | UT Austin McCombs AI/ML capstone projects (in progress) |

Update and push from the repo root:

```bash
git add .
git commit -m "Add project sources"
git push
```

---

## SEO Optimizer

| | Link |
| --- | --- |
| Code in this repo | [projects/seo-optimizer](projects/seo-optimizer) |
| Browse on GitHub | [tree/main/projects/seo-optimizer](https://github.com/FredZaser1111/Project-Showcase/tree/main/projects/seo-optimizer) |
| Live demo | Add your URL here when you have one |

**Highlights:** Article ingest, URL scrape, AI Q&A generation, export — content and SEO-oriented workflow (Engineering Content Generator v1.1).

---

## NBA Z Lock

| | Link |
| --- | --- |
| Code in this repo | [projects/nba-z-lock](projects/nba-z-lock) |
| Browse on GitHub | [tree/main/projects/nba-z-lock](https://github.com/FredZaser1111/Project-Showcase/tree/main/projects/nba-z-lock) |
| Live demo | Add your URL here when you have one |

**Highlights:** NBA game data, predictions, injuries, Flask web UI — see `projects/nba-z-lock/README.md` and `QUICKSTART.md`.

---

## Listing Orchestrator

Shipped AI commerce workflow used by **Cozy Connoisseur Co.**: seed photos → vision → listing copy → publish to **Shopify / eBay / Etsy** → sold notify → consent-aware buyer contact log.

| | Link |
| --- | --- |
| Code in this repo | [projects/listing-orchestrator](projects/listing-orchestrator) |
| Workflow mockup (Pages) | [listing-orchestrator/demo](https://fredzaser1111.github.io/Project-Showcase/projects/listing-orchestrator/demo/) |
| Browse on GitHub | [tree/main/projects/listing-orchestrator](https://github.com/FredZaser1111/Project-Showcase/tree/main/projects/listing-orchestrator) |

**Highlights:** Official marketplace APIs only (low ToS risk); mock mode for recruiters; production seed packs from the private Cozy `/studio` UI.

---

## Automated Workflows

Predictive score → autonomous investigation → workflow action (HITL when needed). Appian-style case management and hyperautomation demos.

| Project | Folder | Focus |
| --- | --- | --- |
| Predictive Maintenance & Procurement | [projects/automated-workflows/predictive-maintenance-agent](projects/automated-workflows/predictive-maintenance-agent) | XGBoost days-to-failure → inventory / PO / approval agent |
| Loan Underwriting & Risk | [projects/automated-workflows/loan-underwriting-agent](projects/automated-workflows/loan-underwriting-agent) | Default risk → triager / compliance / HITL webhook |
| Churn Savior | [projects/automated-workflows/churn-savior-agent](projects/automated-workflows/churn-savior-agent) | Churn probability → CRM / ticket analysis / retention offer |

| | Link |
| --- | --- |
| Section index | [projects/automated-workflows](projects/automated-workflows) |
| Browse on GitHub | [tree/main/projects/automated-workflows](https://github.com/FredZaser1111/Project-Showcase/tree/main/projects/automated-workflows) |

**Highlights:** Mock LLM by default (optional OpenAI/Anthropic keys); shared thresholds and JSON case packets; continues ReneWind / EasyVisa themes into agentic workflows.

---

## McCombs Capstones

Coursework from the **UT Austin McCombs Post Graduate Program in AI & Machine Learning** (Great Learning), graduating August 2026.

| Project | Folder | Focus |
| --- | --- | --- |
| Clinical AI Assistant | [projects/capstones/clinical-ai-assistant](projects/capstones/clinical-ai-assistant) | RAG / NLP over Merck Manuals |
| EasyVisa | [projects/capstones/easyvisa](projects/capstones/easyvisa) | Classification — visa outcomes |
| ReneWind | [projects/capstones/renewind](projects/capstones/renewind) | Neural nets — turbine failure |

| | Link |
| --- | --- |
| Capstone index | [projects/capstones](projects/capstones) |
| Browse on GitHub | [tree/main/projects/capstones](https://github.com/FredZaser1111/Project-Showcase/tree/main/projects/capstones) |

---

## Adding more projects

Create `projects/<short-name>/`, add a README, and add a card to `index.html` plus a section here.

---

## License

**Proprietary — All Rights Reserved.** See [`LICENSE`](LICENSE).

You may view this portfolio on GitHub for evaluation (e.g. recruiting). Copying,
reusing, or redistributing the code or materials requires prior express written
consent from the copyright holder (Zed Fraser / FredZaser1111).
