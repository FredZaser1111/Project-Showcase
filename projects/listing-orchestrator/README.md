# Listing Orchestrator

Shipped AI commerce workflow: **seed photos → vision attributes → listing copy → publish to Shopify / eBay / Etsy → sold notify → buyer contact log**.

**Production use case:** Cozy Connoisseur Co. streetwear reseller (private storefront `/studio` feeds seed packs into this engine).

**Channels (official APIs only):** Shopify, eBay, Etsy — chosen for feasibility and low ToS/ban risk. No Depop/Facebook Marketplace scrapers.

## Recruiter demo (mock results)

| | Link |
| --- | --- |
| Visual workflow mockup | [demo/index.html](demo/index.html) · [GitHub Pages](https://fredzaser1111.github.io/Project-Showcase/projects/listing-orchestrator/demo/) |
| Sample JSON artifacts | [showcase/samples/](showcase/samples/) |

No API keys required. Figures on the demo page match committed samples from `python run_demo.py`.

## Pipeline

```
Seed folder (photos + optional meta.json)
  → Vision enrichment (mock or OpenAI vision)
  → LLM listing copy (Cozy brand voice)
  → Canonical SKU JSON
  → Channel adapters (live if credentials set, else mock)
  → outputs/listings + outputs/publish_log.json
Order sync
  → seller notification stub
  → contacts.jsonl (marketing-ready, consent-flagged)
```

## Quick start (demo — no API keys)

```bash
cd projects/listing-orchestrator
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_demo.py
```

Writes enriched listings and mock publish receipts under `outputs/`.

## Cozy Connoisseur seed packs

1. Run the storefront: `npm run dev` → open **http://localhost:3000/studio**
2. Upload photos + metadata (saved under `cozy-connoisseur-co/data/seed-inventory/<sku>/`)
3. Publish from this folder:

```bash
python publish.py --seed "../../../cozy-connoisseur-co/data/seed-inventory" --channels shopify,ebay,etsy
python sync_orders.py
```

## Live credentials

Copy `.env.example` → `.env` (never commit). Adapters no-op into mock mode when keys are missing so the portfolio demo always runs.

## Order sync / CRM

```bash
python sync_orders.py
```

Pulls mock (or live) recent sales, appends buyer email rows to `outputs/contacts.jsonl` with `marketing_consent` when provided by the channel.
