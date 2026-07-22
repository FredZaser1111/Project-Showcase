# Connect live accounts (Etsy first — no Shopify)

There is no separate “account sync” dashboard yet. **Syncing = putting official API credentials into** `projects/listing-orchestrator/.env` so the Python adapters call *your* shop instead of mock mode.

Skip all `SHOPIFY_*` vars for now.

---

## What you need for Etsy

| Credential | Where it comes from | Env var |
| --- | --- | --- |
| **App API keystring** | Etsy Developer Portal → Your Apps | `ETSY_API_KEY` |
| **Shared secret** | Same page → See API Key Details (required in `x-api-key`) | `ETSY_SHARED_SECRET` |
| **OAuth access token** | After you approve the app in browser (1 hour life) | `ETSY_ACCESS_TOKEN` |
| **OAuth refresh token** | Same token response (≈90 days) | `ETSY_REFRESH_TOKEN` |
| **Shop ID** (numeric) | Returned by `/application/users/me` after OAuth | `ETSY_SHOP_ID` |
| **Taxonomy ID** | Clothing category ID (hats/tops/etc.) | `ETSY_TAXONOMY_ID` |

Official auth docs: https://developer.etsy.com/documentation/essentials/authentication

### Scopes to request

```
listings_r listings_w shops_r shops_w transactions_r
```

(`transactions_r` is for sold-order sync. Buyer email may need extra Etsy approval.)

---

## Step-by-step (Etsy → backend)

### 1. Create a Personal / Seller app

1. Go to https://www.etsy.com/developers/your-apps  
2. Create an app for **Cozy Connoisseur** listing automation  
3. Copy the **keystring** → that is `ETSY_API_KEY`  
4. Add a callback URL for local OAuth, e.g. `http://localhost:8765/callback`
5. Put the keystring in `.env` as `ETSY_API_KEY=...` (copy from `.env.example` if needed)

### 2. Run the OAuth helper (writes tokens into `.env`)

```powershell
cd c:\Users\desmo\Projects\Project-Showcase\projects\listing-orchestrator
.\.venv\Scripts\activate
copy .env.example .env   # if you do not have .env yet
# put ETSY_API_KEY=your_keystring into .env
python etsy_oauth.py
```

This opens a browser, you log into your Cozy Etsy seller account, approve the app, then the script:

- exchanges the code for **access + refresh tokens**
- fetches **shop id**
- appends/updates values in `.env`

### 3. Verify the backend sees your shop

```powershell
python verify_accounts.py --channels etsy
```

You want: `etsy: LIVE` plus your shop name/id.

### 4. Publish without Shopify (draft + carousel images + ledger)

```powershell
python publish.py --seed "c:\Users\desmo\Projects\cozy-connoisseur-co\data\seed-inventory" --channels etsy
python sync_orders.py --channels etsy
```

Live publish now:
1. Creates an Etsy **draft** listing (text)
2. Uploads images in **carousel order** (hero graphic rank 1, then authenticity photos)
3. Appends a row to `outputs/inventory_ledger.csv` (UUID + SKU + Etsy listing id)

Keep listings as drafts until you set `ETSY_ACTIVATE_LISTINGS=true` (also needs shipping profile / shop readiness on Etsy’s side).

If `ETSY_*` is missing, that channel stays **mock** automatically — ledger still records mock publishes for pipeline demos.

### 5. Set a real taxonomy (required for good listings)

```env
ETSY_TAXONOMY_ID=1234
```

Find IDs via Etsy’s seller taxonomy / API (`getSellerTaxonomyNodes`). Start with a clothing category that matches hats/tops/bottoms. Until this is set, the adapter uses a placeholder and Etsy may reject or miscategorize the listing.

---

## Inventory ledger → DBMS

Every successful (or mock) publish appends to:

`outputs/inventory_ledger.csv`

Columns match the future Postgres tables in `schema/inventory.sql` (`items` + `channel_listings`). Phase 2: `docker compose up -d` then swap `append_ledger` to Postgres.

Studio upload now supports:
- **Hero graphic** → `hero_01.*` role `hero_graphic` (carousel first)
- **Authenticity photos** → `photo_NN.*` role `product`
- Stable `item_id` UUID in `meta.json`

---

## eBay (do after Etsy works)

| Credential | Env var |
| --- | --- |
| OAuth user access token | `EBAY_ACCESS_TOKEN` |
| `sandbox` or `production` | `EBAY_ENVIRONMENT` |

1. https://developer.ebay.com/ → create app  
2. Generate a user token with Sell Inventory / Fulfillment scopes  
3. Put token in `.env`, run `python verify_accounts.py --channels ebay`  
4. Publish: `--channels ebay,etsy`  

Full “appears for sale on eBay” still needs offer + publish (next build step after Etsy is live).

---

## Security

- Never commit `.env`  
- Access tokens expire (~1h on Etsy); `verify_accounts.py` / publish will refresh when `ETSY_REFRESH_TOKEN` is present  
- Revoke apps anytime: https://www.etsy.com/your/account/apps  
